#!/usr/bin/env python3
"""
compute_catchments.py
=====================

Compute the population, working-age population, and population-weighted median
household income within each ski resort's 60-minute drive-time isochrone.

INPUTS:
    research-data/resort_isochrones.geojson   (from compute_isochrones.py)
    research-data/us_tracts.geojson           (from fetch_census_data.py)
    research-data/us_tract_demographics.csv   (from fetch_census_data.py)
    research-data/us_ski_resorts.json         (from build_resort_dataset.py)

OUTPUT:
    research-data/us_ski_resorts.json   (rewritten in place with new fields per resort)

NEW FIELDS WRITTEN INTO us_ski_resorts.json:
    catchment_total_pop          int   — total persons in 60-min drive area
    catchment_working_age_pop    int   — persons aged 15-64 in 60-min drive area
    catchment_median_income      int   — population-weighted median household income (USD)
    catchment_border_note        bool  — true if the isochrone might extend across
                                          the US-Canada border (rough check; see below)

METHODOLOGY:
    Areal interpolation. For each resort isochrone polygon P:
       For each US census tract T whose polygon intersects P:
          ratio = area(P ∩ T) / area(T)
          pop_contribution = tract_pop(T) × ratio
          working_age_contribution = tract_working_age_pop(T) × ratio
       catchment_total_pop = sum(pop_contribution)
       catchment_working_age_pop = sum(working_age_contribution)
       catchment_median_income = population-weighted median of tract_median_income(T)
                                  weighted by pop_contribution

    Areal interpolation assumes uniform population density within each tract.
    This is a standard simplifying assumption in spatial accessibility analysis
    and is reasonable at the tract scale (typically 1,200-8,000 people per tract
    in suburban areas, smaller in dense urban cores).

CANADIAN BORDER NOTE:
    US Census tracts do not cover Canada, so the catchment population for
    resorts whose 60-min isochrone extends across the border (Whiteface,
    Jay Peak, Holiday Valley, Mt. Baker, Schweitzer, Lookout Pass, etc.)
    will be UNDERESTIMATED. We flag any isochrone whose bounding box reaches
    above 47°N (the rough latitude where US-Canada border becomes relevant)
    as `catchment_border_note: true` so the map UI can display a caveat.

DEPENDENCIES:
    pip install geopandas pandas shapely

USAGE:
    python compute_catchments.py
    python compute_catchments.py --equal-area-crs EPSG:5070   # alt projection
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = SCRIPT_DIR.parent / 'research-data'

# Variable codes — must match those fetched by fetch_census_data.py
TOTAL_POP_VAR = 'B01003_001E'
WORKING_AGE_VARS = (
    [f'B01001_{i:03d}E' for i in range(6, 20)]    # Male:   _006..._019
    + [f'B01001_{i:03d}E' for i in range(30, 44)] # Female: _030..._043
)
MEDIAN_INCOME_VAR = 'B19013_001E'

# US Albers Equal Area projection — preserves area, ideal for ratio computations
EQUAL_AREA_CRS = 'EPSG:5070'

# ACS missing-value sentinels
ACS_NULL_SENTINELS = {-666666666, -888888888, -999999999, None}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.split('USAGE')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--data-dir', type=Path, default=DEFAULT_DATA_DIR,
                   help=f'Directory containing input files (default: {DEFAULT_DATA_DIR})')
    p.add_argument('--equal-area-crs', default=EQUAL_AREA_CRS,
                   help=f'Projected CRS for area-preserving intersect (default: {EQUAL_AREA_CRS})')
    p.add_argument('--limit', type=int, default=None,
                   help='Process only the first N isochrones (for testing)')
    return p.parse_args()


def safe_int(x):
    """Parse ACS API string return as int, mapping nulls to None."""
    if x is None or x == '' or x == 'null':
        return None
    try:
        v = int(float(x))
        if v in ACS_NULL_SENTINELS:
            return None
        return v
    except (ValueError, TypeError):
        return None


def load_demographics(csv_path):
    """Load tract-level ACS data, compute working-age sum per tract. Return dict GEOID -> {pop, wa, inc}."""
    sys.stderr.write(f'Loading demographics from {csv_path}...\n')
    out = {}
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            geoid = row.get('GEOID', '').strip()
            if not geoid:
                continue
            pop = safe_int(row.get(TOTAL_POP_VAR))
            wa_cells = [safe_int(row.get(c)) for c in WORKING_AGE_VARS]
            wa = sum(c for c in wa_cells if c is not None) if any(c is not None for c in wa_cells) else None
            inc = safe_int(row.get(MEDIAN_INCOME_VAR))
            out[geoid] = {'pop': pop, 'wa': wa, 'inc': inc}
    sys.stderr.write(f'  Loaded {len(out):,} tract demographic records\n')
    n_pop = sum(1 for v in out.values() if v['pop'] is not None)
    n_inc = sum(1 for v in out.values() if v['inc'] is not None)
    sys.stderr.write(f'  Tracts with population data:    {n_pop:,}\n')
    sys.stderr.write(f'  Tracts with median income data: {n_inc:,} (NA for very small tracts)\n')
    return out


def load_tract_polygons(geojson_path, equal_area_crs):
    """Load tract polygons, project to equal-area CRS for accurate area math."""
    sys.stderr.write(f'\nLoading tract polygons from {geojson_path}...\n')
    gdf = gpd.read_file(geojson_path)
    gdf = gdf[['GEOID', 'geometry']].copy()
    sys.stderr.write(f'  Loaded {len(gdf):,} tract polygons (CRS: {gdf.crs})\n')
    sys.stderr.write(f'  Projecting to {equal_area_crs} for area-preserving intersect...\n')
    gdf = gdf.to_crs(equal_area_crs)
    gdf['tract_area'] = gdf.geometry.area  # m²
    return gdf


def load_isochrones(geojson_path, equal_area_crs, limit=None):
    """Load resort isochrone polygons, project to equal-area CRS."""
    sys.stderr.write(f'\nLoading isochrones from {geojson_path}...\n')
    with open(geojson_path) as f:
        data = json.load(f)
    feats = data['features']
    if limit:
        feats = feats[:limit]
    sys.stderr.write(f'  {len(feats)} isochrone polygons\n')

    gdf = gpd.GeoDataFrame.from_features(feats, crs='EPSG:4326')
    sys.stderr.write(f'  Projecting to {equal_area_crs}...\n')
    gdf = gdf.to_crs(equal_area_crs)
    return gdf


def weighted_median(values, weights):
    """Compute weighted median of (value, weight) pairs. Used for income aggregation."""
    pairs = [(v, w) for v, w in zip(values, weights) if v is not None and w is not None and w > 0]
    if not pairs:
        return None
    pairs.sort(key=lambda x: x[0])
    total_weight = sum(w for _, w in pairs)
    cumulative = 0
    for v, w in pairs:
        cumulative += w
        if cumulative >= total_weight / 2:
            return int(v)
    return int(pairs[-1][0])


def near_canada_border(geom_4326):
    """Rough heuristic: does this isochrone's bounding box reach above the Canada border?
    The US-Canada border runs ~49°N for most of the west, drops to ~45°N for VT/NH/ME,
    crosses Lake Erie/Ontario at ~42-44°N for NY/MI. We use 47.5°N as a single conservative
    threshold — anything above that is potentially border-spanning."""
    try:
        bounds = geom_4326.bounds  # (minx, miny, maxx, maxy)
        max_lat = bounds[3]
        return max_lat > 47.5
    except Exception:
        return False


def main():
    args = parse_args()
    data_dir = args.data_dir

    iso_path = data_dir / 'resort_isochrones.geojson'
    tracts_path = data_dir / 'us_tracts.geojson'
    demog_path = data_dir / 'us_tract_demographics.csv'
    resorts_path = data_dir / 'us_ski_resorts.json'

    for p, name in [(iso_path, 'isochrones'), (tracts_path, 'tract polygons'),
                    (demog_path, 'demographics'), (resorts_path, 'resorts JSON')]:
        if not p.exists():
            sys.stderr.write(f'ERROR: {name} file not found at {p}\n')
            sys.stderr.write(f'       Run fetch_census_data.py and compute_isochrones.py first.\n')
            sys.exit(1)

    # 1. Load demographics
    demog = load_demographics(demog_path)

    # 2. Load tract polygons in equal-area CRS
    tracts_gdf = load_tract_polygons(tracts_path, args.equal_area_crs)

    # Build spatial index for fast tract lookup
    sys.stderr.write('\nBuilding spatial index on tracts...\n')
    tracts_sindex = tracts_gdf.sindex

    # 3. Load isochrones in same CRS, plus keep WGS84 copy for border check
    iso_gdf = load_isochrones(iso_path, args.equal_area_crs, limit=args.limit)
    # We need the original WGS84 coords for the Canada border bounding-box check
    iso_4326 = iso_gdf.to_crs('EPSG:4326')

    # 4. For each isochrone, intersect with tracts, compute weighted sums
    sys.stderr.write(f'\n=== Computing catchment for {len(iso_gdf)} resort isochrones ===\n')
    catchments = {}  # resort_name -> dict of metrics

    for idx, row in iso_gdf.iterrows():
        resort = row['resort_name']
        iso_geom = row.geometry
        iso_geom_4326 = iso_4326.iloc[idx].geometry

        # Find candidate tracts using spatial index
        candidates_idx = list(tracts_sindex.intersection(iso_geom.bounds))
        candidates = tracts_gdf.iloc[candidates_idx]

        # Compute exact intersections
        total_pop_contrib = 0.0
        total_wa_contrib = 0.0
        income_pairs = []  # list of (median_inc, pop_contrib) for weighted median

        for _, tract in candidates.iterrows():
            geoid = tract['GEOID']
            tract_geom = tract.geometry
            tract_area = tract['tract_area']
            if tract_area <= 0:
                continue

            d = demog.get(geoid)
            if d is None:
                continue

            try:
                isect = iso_geom.intersection(tract_geom)
            except Exception:
                continue
            if isect.is_empty:
                continue
            isect_area = isect.area
            ratio = isect_area / tract_area
            if ratio <= 0:
                continue

            if d['pop'] is not None:
                total_pop_contrib += d['pop'] * ratio
            if d['wa'] is not None:
                total_wa_contrib += d['wa'] * ratio
            if d['inc'] is not None and d['pop'] is not None and d['pop'] > 0:
                income_pairs.append((d['inc'], d['pop'] * ratio))

        wmedian_inc = weighted_median(
            [p[0] for p in income_pairs],
            [p[1] for p in income_pairs]
        )

        border_note = near_canada_border(iso_geom_4326)

        catchments[resort] = {
            'catchment_total_pop': int(round(total_pop_contrib)),
            'catchment_working_age_pop': int(round(total_wa_contrib)),
            'catchment_median_income': wmedian_inc,
            'catchment_border_note': border_note,
        }

        if (idx + 1) % 25 == 0 or idx + 1 == len(iso_gdf):
            sys.stderr.write(f'  [{idx+1}/{len(iso_gdf)}] {resort}: '
                             f'pop={catchments[resort]["catchment_total_pop"]:,} '
                             f'wa={catchments[resort]["catchment_working_age_pop"]:,} '
                             f'inc={wmedian_inc} '
                             f'{"(border)" if border_note else ""}\n')

    # 5. Merge into us_ski_resorts.json
    sys.stderr.write(f'\nMerging into {resorts_path}...\n')
    with open(resorts_path) as f:
        resorts_doc = json.load(f)

    n_updated = 0
    n_missing = 0
    for r in resorts_doc['resorts']:
        c = catchments.get(r['name'])
        if c is None:
            r['catchment_total_pop'] = None
            r['catchment_working_age_pop'] = None
            r['catchment_median_income'] = None
            r['catchment_border_note'] = False
            n_missing += 1
        else:
            r.update(c)
            n_updated += 1

    # Update meta
    resorts_doc['meta']['catchment_method'] = (
        'Areal interpolation against ACS 2023 5-year tract estimates within '
        '60-minute drive-time isochrone (OpenRouteService). Working-age = 15-64. '
        'Median income is population-weighted across tracts. '
        'Resorts with border_note=true may be underestimates (Canadian portion not counted).'
    )

    with open(resorts_path, 'w') as f:
        json.dump(resorts_doc, f, indent=2, ensure_ascii=False)

    sys.stderr.write(f'\n=== Done ===\n')
    sys.stderr.write(f'Resorts updated with catchment data: {n_updated}\n')
    sys.stderr.write(f'Resorts missing isochrone (no data):  {n_missing}\n')
    sys.stderr.write(f'Output: {resorts_path}\n')


if __name__ == '__main__':
    main()
