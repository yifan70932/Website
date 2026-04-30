# Catchment Population Workflow

This directory contains the scripts that compute **drive-time catchment population**
for each US ski resort. For every resort, three demographic indicators are derived
within the resort's 60-minute drive-time isochrone:

1. **Total population** — total persons within 60 min drive
2. **Working-age population** — persons aged 15–64
3. **Median household income** — population-weighted median across the catchment

These indicators populate the popup of `../map.html` and provide a meaningful
"local market" measure for each resort, complementing the geographic isochrone
overlay.

## Why catchment population

A 60-minute isochrone polygon, by itself, only shows *spatial extent*. But two
isochrones of the same shape can serve markedly different markets:

- **Mountain Creek (NJ)** — 60 min from a polygon that contains ~15 million people
  (NYC metro)
- **Whiteface (NY)** — 60 min from a polygon that contains ~250 thousand people
  (Plattsburgh + rural Adirondacks; underestimate due to nearby Quebec)

Showing the *population* inside each isochrone makes this 60× difference visible
in a way that the polygon shape alone cannot.

## Methodology

**Areal interpolation.** For each resort isochrone polygon P:

```
For each US census tract T whose polygon intersects P:
   ratio = area(P ∩ T) / area(T)
   pop_contribution(T) = tract_population(T) × ratio
catchment_pop = sum over T of pop_contribution(T)
```

This assumes uniform population density within each tract, which is reasonable
at the tract scale (typically 1,200–8,000 people per tract, smaller in dense
urban cores).

The intersect computation is done in the **US Albers Equal Area projection
(EPSG:5070)**, which preserves area, so the `area(P ∩ T) / area(T)` ratio is
geometrically faithful.

**Median income** is computed as a population-weighted median across all
contributing tracts (weighted by `pop_contribution`).

## Data source

- **Tract polygons**: US Census Bureau TIGER/Line cartographic boundary files,
  vintage 2023, 1:500,000 generalization. Free public download from
  `www2.census.gov/geo/tiger/GENZ2023/shp/`.

- **Demographic estimates**: American Community Survey (ACS) 2023 5-year
  estimates (data covers 2019–2023). Variables fetched:
  - `B01003_001E` — Total population
  - `B01001_006E`–`019E`, `030E`–`043E` — Sex by age cells covering ages 15–64
  - `B19013_001E` — Median household income (12-month, inflation-adjusted)

  Free public API at `api.census.gov`. Sign up for an API key (no rate limit
  if used responsibly):
  https://api.census.gov/data/key_signup.html

## Workflow

### Step 1: Download Census data (one-time, ~10 min)

```powershell
# Windows PowerShell
$env:CENSUS_API_KEY = "your-key-here"
python fetch_census_data.py
```

```bash
# Linux/Mac
export CENSUS_API_KEY='your-key-here'
python3 fetch_census_data.py
```

This downloads all 50 state shapefiles + DC, fetches ACS estimates for all
~84,000 census tracts, and writes:

- `../research-data/us_tracts.geojson` (~30–50 MB, simplified polygons)
- `../research-data/us_tract_demographics.csv` (~5–8 MB)

To test with a subset first:

```bash
python fetch_census_data.py --states CO UT
```

### Step 2: Compute catchments (~5 min)

```bash
python compute_catchments.py
```

This reads the isochrones + tract polygons + demographic CSV, runs spatial
intersection, and writes the catchment fields back into
`../research-data/us_ski_resorts.json`.

### Step 3: Refresh the deployed wiki

The newly enriched `us_ski_resorts.json` is what `map.html` reads at page load.
Just commit and redeploy the file — no map.html changes needed; it picks up
the new fields automatically and renders them in the resort popup.

## Output schema

After running `compute_catchments.py`, each resort in `us_ski_resorts.json`
gains four new fields:

```json
{
  "name": "Vail",
  "state": "CO",
  ...
  "catchment_total_pop": 387000,
  "catchment_working_age_pop": 247000,
  "catchment_median_income": 76500,
  "catchment_border_note": false
}
```

Resorts whose isochrone failed to generate (Eaglecrest, Teton Pass MT) have
`null` values for the population fields.

## Canadian border caveat

US Census tracts do not cover Canada. Resorts whose 60-minute isochrone extends
across the US-Canada border have **underestimated** catchment populations,
because the Canadian portion contributes zero. This affects northern resorts
including Holiday Valley NY, Whiteface NY, Jay Peak VT, Burke VT, Whitefish
MT, Schweitzer ID, Lookout Pass ID/MT, Mt. Baker WA, 49 Degrees North WA, and
Lutsen Mountains MN.

`compute_catchments.py` flags any isochrone whose bounding box reaches above
**47.5°N** (a conservative threshold for proximity to the border) by setting
`catchment_border_note: true`. The map UI displays an italicized note in
those resorts' popups: "*US population only. The 60-min drive area may extend
into Canada; Canadian portion not counted.*"

To compute true binational catchments, one would need to add Statistics Canada
census subdivision data and merge the two national datasets — out of scope
here, but a natural extension.

## Reproducibility

Both the tract polygon vintage (TIGER 2023) and the ACS estimate vintage
(2019–2023 5-year) are stable. A re-run of these scripts in 6 months should
produce essentially identical results, with the exception of any Census Bureau
post-publication corrections (rare).

For frozen reference, commit the generated files (`us_tracts.geojson`,
`us_tract_demographics.csv`, the updated `us_ski_resorts.json`) to git.

## Citation

If using catchment data generated by these scripts in academic work:

> US Census Bureau. 2023 American Community Survey 5-Year Estimates.
> Tables B01001, B01003, B19013. Retrieved via Census API at api.census.gov.

> US Census Bureau. 2023 TIGER/Line Cartographic Boundary Files, Census Tracts.
> https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
