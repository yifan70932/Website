#!/usr/bin/env python3
"""
fetch_census_data.py
=====================

Download US Census tract polygons + ACS 2023 5-year demographic estimates,
producing two files used by compute_catchments.py:

    research-data/us_tracts.geojson           ~ 30-50 MB simplified polygons
    research-data/us_tract_demographics.csv   ~ 5-8 MB tract-level estimates

The script downloads from two Census endpoints:

  1. TIGER/Line cartographic boundary shapefile (tract level, 1:500k version)
     — one shapefile per state, covering 50 states + DC + PR. We skip PR.
     URL pattern: https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_{ST}_tract_500k.zip

  2. ACS 5-year API (vintage 2023, 2019-2023 estimate window) for three groups
     of variables per tract:
       B01003_001E             Total population
       B01001_006E..019E       Male 15-17 through 62-64 (working-age portion)
       B01001_030E..043E       Female 15-17 through 62-64
       B19013_001E             Median household income (12-month, infl-adj)

DEPENDENCIES (install once):
    pip install requests pandas geopandas shapely

CENSUS API KEY:
    Free, no rate limit if used responsibly. Sign up:
    https://api.census.gov/data/key_signup.html
    Then either set an env var or pass --api-key:
        $env:CENSUS_API_KEY = "your-key-here"          # PowerShell
        export CENSUS_API_KEY='your-key-here'          # bash/zsh

USAGE:
    python fetch_census_data.py
    python fetch_census_data.py --api-key XXXX --skip-tracts    # only ACS
    python fetch_census_data.py --skip-acs                       # only polygons
    python fetch_census_data.py --states CO UT WY                # subset (testing)

WALL CLOCK:
    Full run: ~10-15 minutes (50 shapefile downloads, ~1.5 GB total raw data;
    51 ACS API calls; one big polygon simplification pass).
    Output footprint: ~40 MB (compact GeoJSON + CSV).
"""
import argparse
import csv
import io
import json
import os
import sys
import time
import zipfile
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR.parent / 'research-data'

# All 50 states + DC, with FIPS codes. Skip PR (no relevant ski catchment data).
STATE_FIPS = {
    'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08',
    'CT': '09', 'DE': '10', 'DC': '11', 'FL': '12', 'GA': '13', 'HI': '15',
    'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19', 'KS': '20', 'KY': '21',
    'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27',
    'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33',
    'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
    'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46',
    'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53',
    'WV': '54', 'WI': '55', 'WY': '56',
}

# ACS 2023 5-year vintage variables we need
TOTAL_POP_VAR = 'B01003_001E'

# Working-age 15-64 cells (28 variables total)
WORKING_AGE_VARS = (
    [f'B01001_{i:03d}E' for i in range(6, 20)]    # Male:   _006..._019
    + [f'B01001_{i:03d}E' for i in range(30, 44)] # Female: _030..._043
)
MEDIAN_INCOME_VAR = 'B19013_001E'

ALL_VARS = [TOTAL_POP_VAR] + WORKING_AGE_VARS + [MEDIAN_INCOME_VAR]
# ACS API caps each request at 50 variables, so we are fine in one call (30 vars)

ACS_BASE = 'https://api.census.gov/data/2023/acs/acs5'
TIGER_BASE = 'https://www2.census.gov/geo/tiger/GENZ2023/shp'

# Polygon simplification tolerance in degrees
# 0.001 deg ≈ 100 m at mid-latitudes — fine enough for our use, ~10x size reduction
SIMPLIFY_TOLERANCE_DEG = 0.001


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.split('USAGE')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--api-key', default=os.environ.get('CENSUS_API_KEY'),
                   help='Census API key (or set CENSUS_API_KEY env var)')
    p.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR,
                   help=f'Where to write output files (default: {DEFAULT_OUTPUT_DIR})')
    p.add_argument('--states', nargs='+', default=None,
                   help='Subset of state codes to process (default: all 50 + DC)')
    p.add_argument('--skip-tracts', action='store_true',
                   help='Skip TIGER polygon download (only fetch ACS data)')
    p.add_argument('--skip-acs', action='store_true',
                   help='Skip ACS API call (only fetch polygons)')
    p.add_argument('--no-simplify', action='store_true',
                   help='Do not simplify polygons (file will be ~5x larger)')
    return p.parse_args()


def fetch_acs_data(api_key, state_codes, output_csv):
    """Fetch tract-level ACS data for all requested states. Writes one combined CSV."""
    sys.stderr.write(f'\n=== ACS demographic data ===\n')
    sys.stderr.write(f'Requesting {len(ALL_VARS)} variables for tracts in {len(state_codes)} states\n')

    rows = []
    cols = None
    for i, st in enumerate(state_codes):
        fips = STATE_FIPS[st]
        # API URL — get all variables for all tracts in this state
        # Use comma-separated variable list; geography hierarchy: tract within state
        params = {
            'get': ','.join(ALL_VARS),
            'for': 'tract:*',
            'in': f'state:{fips}',
        }
        if api_key:
            params['key'] = api_key

        sys.stderr.write(f'  [{i+1}/{len(state_codes)}] {st} (FIPS {fips}) ... ')
        sys.stderr.flush()
        try:
            r = requests.get(ACS_BASE, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            sys.stderr.write(f'FAILED: {e}\n')
            continue

        # First row of response is headers; rest is data
        if cols is None:
            cols = data[0]
            # Add a synthesized GEOID column = state + county + tract
            cols_out = ['GEOID'] + cols
            with open(output_csv, 'w', newline='') as f:
                csv.writer(f).writerow(cols_out)

        with open(output_csv, 'a', newline='') as f:
            w = csv.writer(f)
            for row in data[1:]:
                row_dict = dict(zip(cols, row))
                geoid = row_dict.get('state', '') + row_dict.get('county', '') + row_dict.get('tract', '')
                w.writerow([geoid] + row)

        sys.stderr.write(f'ok ({len(data)-1} tracts)\n')
        time.sleep(0.5)  # be nice to Census servers

    sys.stderr.write(f'\nACS data saved to: {output_csv}\n')
    sys.stderr.write(f'File size: {output_csv.stat().st_size / 1024:.0f} KB\n')


def fetch_tracts(state_codes, output_geojson, simplify):
    """Download TIGER tract shapefiles, merge into one GeoJSON. Requires geopandas."""
    sys.stderr.write(f'\n=== TIGER tract polygons ===\n')

    try:
        import geopandas as gpd
        from shapely.geometry import shape
    except ImportError:
        sys.stderr.write('ERROR: geopandas + shapely required for polygon download.\n')
        sys.stderr.write('       Install with: pip install geopandas shapely\n')
        sys.exit(1)

    sys.stderr.write(f'Downloading {len(state_codes)} state shapefiles from TIGER/Line\n')
    sys.stderr.write(f'(cb_2023_*_tract_500k — cartographic boundary, 1:500k generalization)\n')
    if simplify:
        sys.stderr.write(f'Polygons will be simplified at {SIMPLIFY_TOLERANCE_DEG}° tolerance\n')

    all_gdfs = []
    total_bytes = 0
    for i, st in enumerate(state_codes):
        fips = STATE_FIPS[st]
        url = f'{TIGER_BASE}/cb_2023_{fips}_tract_500k.zip'

        sys.stderr.write(f'  [{i+1}/{len(state_codes)}] {st} (FIPS {fips}) ... ')
        sys.stderr.flush()
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            total_bytes += len(r.content)
        except Exception as e:
            sys.stderr.write(f'FAILED: {e}\n')
            continue

        # Read shapefile from in-memory zip
        try:
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                # Extract to temp dir then read with geopandas
                tmpdir = SCRIPT_DIR / '_tmp_shp' / st
                tmpdir.mkdir(parents=True, exist_ok=True)
                z.extractall(tmpdir)
                shp = next(tmpdir.glob('*.shp'))
                gdf = gpd.read_file(shp)
                # Keep only fields we need
                gdf = gdf[['GEOID', 'geometry']]
                if simplify:
                    gdf['geometry'] = gdf['geometry'].simplify(SIMPLIFY_TOLERANCE_DEG, preserve_topology=True)
                all_gdfs.append(gdf)
        except Exception as e:
            sys.stderr.write(f'extract FAILED: {e}\n')
            continue

        sys.stderr.write(f'ok ({len(gdf)} tracts)\n')

    sys.stderr.write(f'\nTotal raw download: {total_bytes / 1024 / 1024:.1f} MB\n')

    # Merge and write
    merged = gpd.pd.concat(all_gdfs, ignore_index=True)
    merged = gpd.GeoDataFrame(merged, geometry='geometry', crs=all_gdfs[0].crs)
    sys.stderr.write(f'Merged: {len(merged)} tracts. Writing GeoJSON...\n')
    # Write as compact GeoJSON. We don't specify engine — geopandas will
    # auto-select pyogrio (preferred) if installed, falling back to fiona.
    # On Python 3.14 + Windows, pyogrio is the only option that installs cleanly
    # (fiona requires external GDAL).
    merged.to_file(output_geojson, driver='GeoJSON')
    sys.stderr.write(f'Saved: {output_geojson}\n')
    sys.stderr.write(f'File size: {output_geojson.stat().st_size / 1024 / 1024:.1f} MB\n')

    # Cleanup temp dir
    import shutil
    shutil.rmtree(SCRIPT_DIR / '_tmp_shp', ignore_errors=True)


def main():
    args = parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    state_codes = args.states or sorted(STATE_FIPS.keys())
    for st in state_codes:
        if st not in STATE_FIPS:
            sys.stderr.write(f'ERROR: Unknown state code {st!r}\n')
            sys.exit(1)

    if not args.skip_acs:
        if not args.api_key:
            sys.stderr.write('WARNING: No CENSUS_API_KEY set. ACS API will likely rate-limit you.\n')
            sys.stderr.write('         Get a free key: https://api.census.gov/data/key_signup.html\n\n')
        fetch_acs_data(args.api_key, state_codes, output_dir / 'us_tract_demographics.csv')

    if not args.skip_tracts:
        fetch_tracts(state_codes, output_dir / 'us_tracts.geojson', simplify=not args.no_simplify)

    sys.stderr.write(f'\n=== Done ===\n')
    sys.stderr.write(f'Outputs in {output_dir}:\n')
    for f in sorted(output_dir.glob('us_tract*')):
        sys.stderr.write(f'  {f.name}: {f.stat().st_size / 1024 / 1024:.1f} MB\n')
    sys.stderr.write(f'\nNext: run compute_catchments.py to compute per-resort catchment populations.\n')


if __name__ == '__main__':
    main()
