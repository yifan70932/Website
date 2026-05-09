"""
Build the master dataset for the ski research analysis.
Combines NSAA visits + macroeconomic + Olympic + climate (where available)
into a single CSV indexed by ski season.
"""
import pandas as pd
import numpy as np
from io import StringIO

# ---------- 1. NSAA visits ----------
nsaa = pd.read_csv('/home/claude/research/data/nsaa_visits.csv')
nsaa = nsaa.rename(columns={'year_end': 'year'})
print(f"NSAA: {len(nsaa)} seasons, year range {nsaa['year'].min()}-{nsaa['year'].max()}")

# ---------- 2. Real GDP (chained 2012 dollars, trillions) from multpl, Dec 31 of each year ----------
gdp_data = """year,real_gdp_t
1978,7.23
1979,7.32
1980,7.32
1981,7.41
1982,7.30
1983,7.88
1984,8.32
1985,8.67
1986,8.92
1987,9.32
1988,9.67
1989,9.94
1990,10.00
1991,10.12
1992,10.56
1993,10.83
1994,11.28
1995,11.53
1996,12.04
1997,12.58
1998,13.19
1999,13.83
2000,14.23
2001,14.25
2002,14.54
2003,15.16
2004,15.67
2005,16.14
2006,16.56
2007,16.92
2008,16.49
2009,16.50
2010,16.96
2011,17.22
2012,17.49
2013,18.02
2014,18.50
2015,18.89
2016,19.30
2017,19.88
2018,20.30
2019,20.99
2020,20.79
2021,21.99
2022,22.28
2023,23.03
2024,23.59
2025,24.06
"""
gdp = pd.read_csv(StringIO(gdp_data))
gdp['gdp_growth_pct'] = gdp['real_gdp_t'].pct_change() * 100
print(f"GDP: {len(gdp)} years")

# ---------- 3. Real Disposable Personal Income Per Capita (from FRED A229RX0, monthly) ----------
# I'll embed the December values for each year as the "season-anchor" reading
# Values are chained 2017 dollars
rdpi_dec = """year,rdpi_dec
1978,22967
1979,22896
1980,23108
1981,23272
1982,23585
1983,24758
1984,25878
1985,26283
1986,26784
1987,27518
1988,28460
1989,28743
1990,28697
1991,29024
1992,30241
1993,30289
1994,30425
1995,30820
1996,31459
1997,32584
1998,33825
1999,34666
2000,35821
2001,35943
2002,37066
2003,37884
2004,39581
2005,38798
2006,39838
2007,39993
2008,40182
2009,39807
2010,40771
2011,41150
2012,43190
2013,40905
2014,42763
2015,43487
2016,43942
2017,45136
2018,47038
2019,47334
2020,49374
2021,49843
2022,49398
2023,51626
2024,52349
2025,52557
"""
# Note: 2025 is November (last available reading at fetch time)
rdpi = pd.read_csv(StringIO(rdpi_dec))
rdpi['rdpi_growth_pct'] = rdpi['rdpi_dec'].pct_change() * 100
print(f"RDPI: {len(rdpi)} years")

# ---------- 4. Olympic year encoding ----------
# A ski season ending in year X has its peak winter months Dec(X-1), Jan(X), Feb(X)
# Olympic Games typically occur in February of year X
# So we attribute Olympic effects to the season *ending* in year X
olympic_years = {
    1980: ('Lake Placid', 'US'),
    1984: ('Sarajevo', 'overseas'),
    1988: ('Calgary', 'NA'),  # Canada, neighboring/drivable for many US markets
    1992: ('Albertville', 'overseas'),
    1994: ('Lillehammer', 'overseas'),
    1998: ('Nagano', 'overseas'),
    2002: ('Salt Lake City', 'US'),
    2006: ('Torino', 'overseas'),
    2010: ('Vancouver', 'NA'),
    2014: ('Sochi', 'overseas'),
    2018: ('PyeongChang', 'overseas'),
    2022: ('Beijing', 'overseas'),
    2026: ('Milano-Cortina', 'overseas'),
}

def olympic_host(year):
    info = olympic_years.get(year)
    return info[0] if info else ''

def olympic_zone(year):
    info = olympic_years.get(year)
    return info[1] if info else 'none'

def is_us_olympic(year):
    return 1 if olympic_years.get(year, ('',''))[1] == 'US' else 0

def is_na_olympic(year):
    # Includes both US and Canada hosting
    z = olympic_years.get(year, ('',''))[1]
    return 1 if z in ('US', 'NA') else 0

def is_any_olympic(year):
    return 1 if year in olympic_years else 0

# ---------- 5. Pass-era markers ----------
# Epic Pass launched May 2008 (effective for 2008/09 season onward = year_end 2009+)
# Epic Pass major price cut 2017 (effective for 2017/18 = year_end 2018+)
# Ikon Pass launched 2018 (effective for 2018/19 = year_end 2019+)
def post_epic(year):
    return 1 if year >= 2009 else 0

def post_epic_pricecut(year):
    return 1 if year >= 2018 else 0

def post_ikon(year):
    return 1 if year >= 2019 else 0

def post_covid(year):
    # 2019/20 was truncated by COVID (year_end 2020); 2020/21+ are post-COVID
    return 1 if year >= 2021 else 0

def covid_truncated(year):
    return 1 if year == 2020 else 0

# ---------- 6. Recession year indicators (NBER-defined US recessions) ----------
# Recessions affecting US ski seasons (year_end terms):
# 1980 (Jan-Jul 1980), 1981-82 (Jul 81 - Nov 82), 1990-91 (Jul 90 - Mar 91),
# 2001 (Mar - Nov 2001), 2007-09 Great Recession (Dec 07 - Jun 09), 2020 COVID (Feb-Apr 20)
recession_years = {1980, 1981, 1982, 1990, 1991, 2001, 2008, 2009, 2020}
def in_recession(year):
    return 1 if year in recession_years else 0

# ---------- 7. National average snowfall at ski areas (from NSAA reports) ----------
# This series is patchy; NSAA started reporting it consistently only ~2013.
# Earlier values reconstructed from press releases where mentioned; Many are NA.
# Inches of snow, average across U.S. ski areas, per NSAA Kottke Report
snowfall_data = """year,natl_snowfall_in
2007,
2008,
2009,
2010,
2011,
2012,
2013,
2014,
2015,
2016,
2017,
2018,
2019,
2020,
2021,
2022,145
2023,225
2024,158
2025,150
"""
snow = pd.read_csv(StringIO(snowfall_data))

# ---------- 8. Winter (DJF) temperature data ----------
# As state-level NOAA Climate at a Glance data is too tedious to fetch via web search
# for every year, I'll use a National Average DJF temperature anomaly proxy.
# These are CONUS-average DJF anomalies vs 1901-2000 baseline (deg F),
# from NOAA NCEI annual climate reports. Values for years where I have specific
# search-result anchors; gap-filled with NaN otherwise.
# (Will be filled by researcher in deployed CSV if available.)
# I'm noting these are widely reported climate facts:
# Data structure left mostly empty; analysis will note the limitation
winter_temp_data = """year,winter_anom_f
"""
# We will not include this systematically in main analysis but will discuss it
# in the methodology section as a known data gap.

# ---------- 9. Build merged dataset ----------
df = nsaa.copy()
df = df.merge(gdp, on='year', how='left')
df = df.merge(rdpi, on='year', how='left')
df = df.merge(snow, on='year', how='left')

# Add Olympic encoding
df['olympic_host'] = df['year'].apply(olympic_host)
df['olympic_zone'] = df['year'].apply(olympic_zone)
df['is_us_olympic'] = df['year'].apply(is_us_olympic)
df['is_na_olympic'] = df['year'].apply(is_na_olympic)
df['is_any_olympic'] = df['year'].apply(is_any_olympic)

# Pass-era markers
df['post_epic'] = df['year'].apply(post_epic)
df['post_epic_pricecut'] = df['year'].apply(post_epic_pricecut)
df['post_ikon'] = df['year'].apply(post_ikon)
df['post_covid'] = df['year'].apply(post_covid)
df['covid_truncated'] = df['year'].apply(covid_truncated)
df['in_recession'] = df['year'].apply(in_recession)

# Reorder
cols = ['season','year','total_us','northeast','southeast','midwest',
        'rocky_mountain','pacific_southwest','pacific_northwest','pacific_west_total',
        'rank','natl_snowfall_in',
        'real_gdp_t','gdp_growth_pct','rdpi_dec','rdpi_growth_pct',
        'olympic_host','olympic_zone','is_us_olympic','is_na_olympic','is_any_olympic',
        'in_recession','post_epic','post_epic_pricecut','post_ikon','post_covid',
        'covid_truncated']
df = df[cols]

# Save
out_path = '/home/claude/research/data/master_dataset.csv'
df.to_csv(out_path, index=False)
print(f"\nMaster dataset saved: {out_path}")
print(f"Shape: {df.shape}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nLast 5 rows:")
print(df.tail())
print(f"\nOlympic-year US visits:")
print(df[df['is_us_olympic']==1][['season','total_us','olympic_host']])
print(f"\nNA-Olympic-year US visits:")
print(df[df['is_na_olympic']==1][['season','total_us','olympic_host']])
