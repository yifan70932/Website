"""
Statistical analyses for "Skiing in the United States: A multi-variable retrospective"
Loads master dataset and produces all numerical results / saves all plots.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import stats
import json
from pathlib import Path

# ---- Aesthetic config: match wiki main page ----
NAVY = '#0a3d62'
SAPPHIRE = '#3c6e88'
RED = '#a8323e'
FOREST = '#2a5d3e'
INK = '#1f2328'
INK_SOFT = '#5a6470'
RULE = '#d8d4c7'
PAPER = '#faf8f3'
GOLD = '#b8860b'
SLATE = '#475569'

mpl.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif', 'serif'],
    'axes.facecolor': PAPER,
    'figure.facecolor': PAPER,
    'savefig.facecolor': PAPER,
    'savefig.edgecolor': 'none',
    'savefig.bbox': 'tight',
    'axes.edgecolor': INK,
    'axes.labelcolor': INK,
    'xtick.color': INK_SOFT,
    'ytick.color': INK_SOFT,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.color': RULE,
    'grid.linewidth': 0.5,
    'grid.alpha': 0.7,
    'axes.titleweight': 'bold',
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.dpi': 110,
    'savefig.dpi': 144,
})

# ---- Output dirs ----
FIG_DIR = Path('/home/claude/research/figures')
FIG_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR = Path('/home/claude/research/results')
OUT_DIR.mkdir(parents=True, exist_ok=True)

results = {}

# ---- Load ----
df = pd.read_csv('/home/claude/research/data/master_dataset.csv')
df = df.sort_values('year').reset_index(drop=True)
print(f"Loaded {len(df)} seasons")
print(f"Variables with non-null counts:")
for c in df.columns:
    n = df[c].notna().sum()
    print(f"  {c}: {n}")

# ---- 1. DESCRIPTIVE: Summary stats ----
print("\n=== Section 1: Descriptive Stats ===")
desc = {
    'visits_min': float(df['total_us'].min()),
    'visits_min_year': int(df.loc[df['total_us'].idxmin(), 'year']),
    'visits_max': float(df['total_us'].max()),
    'visits_max_year': int(df.loc[df['total_us'].idxmax(), 'year']),
    'visits_mean': float(df['total_us'].mean()),
    'visits_std': float(df['total_us'].std()),
    'visits_cv': float(df['total_us'].std() / df['total_us'].mean()),
    # Trend over full period
    'trend_slope_per_yr': float(np.polyfit(df['year'], df['total_us'], 1)[0]),
}
# Period decomposition
periods = {
    'period_1980s': (1979, 1989),
    'period_1990s': (1990, 1999),
    'period_2000s': (2000, 2009),
    'period_2010s': (2010, 2019),
    'period_2020s': (2020, 2025),
}
for name, (start, end) in periods.items():
    sub = df[(df['year'] >= start) & (df['year'] <= end)]
    desc[f'{name}_mean'] = float(sub['total_us'].mean())
    desc[f'{name}_std'] = float(sub['total_us'].std())
    desc[f'{name}_cv'] = float(sub['total_us'].std() / sub['total_us'].mean()) if sub['total_us'].mean() else np.nan

results['descriptive'] = desc
print(json.dumps(desc, indent=2))

# ---- 2. Time series plot with regime annotations ----
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(df['year'], df['total_us'], '-', color=NAVY, linewidth=1.6, marker='o', markersize=3.5)
ax.fill_between(df['year'], df['total_us'], alpha=0.08, color=NAVY)

# Annotate breakpoints
ax.axvline(2009, color=GOLD, linestyle='--', alpha=0.6, linewidth=1)
ax.text(2009, 67.5, 'Epic\n(2008-09)', fontsize=8, ha='center', color=GOLD)
ax.axvline(2019, color=FOREST, linestyle='--', alpha=0.6, linewidth=1)
ax.text(2019, 67.5, 'Ikon\n(2018-19)', fontsize=8, ha='center', color=FOREST)
ax.axvline(2020, color=RED, linestyle=':', alpha=0.7, linewidth=1)
ax.text(2020, 39, 'COVID', fontsize=8, ha='center', color=RED)

# Olympic year markers
for olympic_year in df[df['is_us_olympic']==1]['year']:
    ax.scatter(olympic_year, df.loc[df['year']==olympic_year, 'total_us'].iloc[0],
               s=100, marker='*', color=RED, zorder=5, edgecolor='white', linewidth=0.8)
for olympic_year in df[(df['is_na_olympic']==1) & (df['is_us_olympic']==0)]['year']:
    ax.scatter(olympic_year, df.loc[df['year']==olympic_year, 'total_us'].iloc[0],
               s=70, marker='*', color=GOLD, zorder=5, edgecolor='white', linewidth=0.6)

ax.set_xlabel('Year (season ending)')
ax.set_ylabel('Skier visits, millions')
ax.set_title('U.S. skier visits, 1978–79 through 2024–25', loc='left')
ax.set_xlim(1978, 2026)
ax.set_ylim(35, 70)

# Legend
import matplotlib.lines as mlines
us_star = mlines.Line2D([], [], color=RED, marker='*', linestyle='None', markersize=10, label='U.S. Olympic year')
na_star = mlines.Line2D([], [], color=GOLD, marker='*', linestyle='None', markersize=8, label='Canadian Olympic year')
ax.legend(handles=[us_star, na_star], loc='lower right', fontsize=8, frameon=False)

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig01_visits_timeseries.svg')
plt.savefig(FIG_DIR / 'fig01_visits_timeseries.png')
plt.close()
print("Fig 1 saved")

# ---- 3. CORRELATION ANALYSIS ----
print("\n=== Section 2: Correlations ===")
# Drop COVID year for cleanliness; analysis will note this
df_clean = df[df['covid_truncated']==0].copy()

corrs = {}
for var in ['real_gdp_t','gdp_growth_pct','rdpi_dec','rdpi_growth_pct']:
    sub = df_clean[['total_us', var]].dropna()
    if len(sub) > 5:
        r, p = stats.pearsonr(sub['total_us'], sub[var])
        corrs[var] = {'r': float(r), 'p': float(p), 'n': int(len(sub))}
        # Spearman for robustness
        rs, ps = stats.spearmanr(sub['total_us'], sub[var])
        corrs[var]['spearman_r'] = float(rs)
        corrs[var]['spearman_p'] = float(ps)

# Region-level correlations with macroeconomic
for region in ['northeast','southeast','midwest','rocky_mountain','pacific_southwest','pacific_northwest']:
    for var in ['real_gdp_t','rdpi_dec']:
        sub = df_clean[[region, var]].dropna()
        if len(sub) > 10:
            r, p = stats.pearsonr(sub[region], sub[var])
            corrs[f'{region}_vs_{var}'] = {'r': float(r), 'p': float(p), 'n': int(len(sub))}

results['correlations'] = corrs
print(json.dumps({k: v for k, v in list(corrs.items())[:8]}, indent=2))

# ---- 4. ROLLING CORRELATIONS (visits vs GDP, vs RDPI) ----
# This captures whether the relationship has shifted over time
window = 10
def rolling_corr(x, y, window):
    """Rolling Pearson r with window."""
    rs = []
    for i in range(len(x) - window + 1):
        sub_x = x.iloc[i:i+window]
        sub_y = y.iloc[i:i+window]
        if sub_x.notna().sum() >= window-1 and sub_y.notna().sum() >= window-1:
            rs.append(np.corrcoef(sub_x, sub_y)[0,1])
        else:
            rs.append(np.nan)
    return rs

# Rolling correlations
rc_gdp = rolling_corr(df_clean['total_us'], df_clean['real_gdp_t'], window)
rc_rdpi = rolling_corr(df_clean['total_us'], df_clean['rdpi_dec'], window)
rc_years = df_clean['year'].iloc[window-1:].values

# Plot rolling corrs
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(rc_years, rc_gdp, '-', color=NAVY, linewidth=1.6, label='Visits vs Real GDP')
ax.plot(rc_years, rc_rdpi, '-', color=RED, linewidth=1.6, label='Visits vs Real Disposable Income/Capita')
ax.axhline(0, color=INK, linewidth=0.5)
ax.axhline(0.5, color=RULE, linewidth=0.5, linestyle='--')
ax.axhline(-0.5, color=RULE, linewidth=0.5, linestyle='--')
ax.set_ylim(-1, 1)
ax.set_xlabel('Year (end of 10-year window)')
ax.set_ylabel('Pearson r')
ax.set_title(f'Rolling {window}-year correlations: U.S. skier visits vs macroeconomic indicators', loc='left')
ax.legend(loc='lower left', fontsize=9, frameon=False)
ax.set_xlim(rc_years[0]-1, rc_years[-1]+1)

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig02_rolling_correlations.svg')
plt.savefig(FIG_DIR / 'fig02_rolling_correlations.png')
plt.close()
print("Fig 2 saved")

# ---- 5. SCATTER: Visits vs Real GDP ----
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

# Visits vs real GDP
ax = axes[0]
sub = df_clean[['total_us','real_gdp_t']].dropna()
ax.scatter(sub['real_gdp_t'], sub['total_us'], color=NAVY, alpha=0.7, s=40, edgecolor='white', linewidth=0.5)
slope, intercept, r, p, se = stats.linregress(sub['real_gdp_t'], sub['total_us'])
xx = np.linspace(sub['real_gdp_t'].min(), sub['real_gdp_t'].max(), 50)
ax.plot(xx, slope*xx + intercept, color=RED, linewidth=1.5, alpha=0.7)
ax.set_xlabel('Real GDP (chained 2012$, trillions)')
ax.set_ylabel('Skier visits (millions)')
ax.set_title(f'Visits vs Real GDP\nr = {r:.3f}, p < {0.001 if p<0.001 else p:.3f}, n = {len(sub)}', loc='left', fontsize=10)

# Visits vs RDPI
ax = axes[1]
sub = df_clean[['total_us','rdpi_dec']].dropna()
ax.scatter(sub['rdpi_dec']/1000, sub['total_us'], color=FOREST, alpha=0.7, s=40, edgecolor='white', linewidth=0.5)
slope, intercept, r, p, se = stats.linregress(sub['rdpi_dec']/1000, sub['total_us'])
xx = np.linspace((sub['rdpi_dec']/1000).min(), (sub['rdpi_dec']/1000).max(), 50)
ax.plot(xx, slope*xx + intercept, color=RED, linewidth=1.5, alpha=0.7)
ax.set_xlabel('Real disposable income/capita (chained 2017$, thousands)')
ax.set_ylabel('Skier visits (millions)')
ax.set_title(f'Visits vs Real Disposable Income/Capita\nr = {r:.3f}, p < {0.001 if p<0.001 else p:.3f}, n = {len(sub)}', loc='left', fontsize=10)

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig03_scatter_macro.svg')
plt.savefig(FIG_DIR / 'fig03_scatter_macro.png')
plt.close()
print("Fig 3 saved")

# ---- 6. RECESSION YEAR ANALYSIS ----
print("\n=== Section 3: Recession Year Analysis ===")
recession = df_clean[df_clean['in_recession']==1]
nonrecession = df_clean[df_clean['in_recession']==0]
t_stat, p_val = stats.ttest_ind(recession['total_us'], nonrecession['total_us'], equal_var=False)
recession_analysis = {
    'recession_years': sorted(recession['year'].tolist()),
    'recession_mean_visits': float(recession['total_us'].mean()),
    'nonrecession_mean_visits': float(nonrecession['total_us'].mean()),
    'difference': float(recession['total_us'].mean() - nonrecession['total_us'].mean()),
    't_stat': float(t_stat),
    'p_value': float(p_val),
    'n_recession': len(recession),
    'n_nonrecession': len(nonrecession),
}

# YoY visits change in recession years vs not
df_clean['visits_yoy'] = df_clean['total_us'].pct_change() * 100
recession_yoy = df_clean[df_clean['in_recession']==1]['visits_yoy'].dropna()
nonrecession_yoy = df_clean[df_clean['in_recession']==0]['visits_yoy'].dropna()
t_yoy, p_yoy = stats.ttest_ind(recession_yoy, nonrecession_yoy, equal_var=False)
recession_analysis['yoy_recession_mean_pct'] = float(recession_yoy.mean())
recession_analysis['yoy_nonrecession_mean_pct'] = float(nonrecession_yoy.mean())
recession_analysis['yoy_t'] = float(t_yoy)
recession_analysis['yoy_p'] = float(p_yoy)

results['recession_analysis'] = recession_analysis
print(json.dumps(recession_analysis, indent=2))

# ---- 7. OLYMPIC YEAR ANALYSIS ----
print("\n=== Section 4: Olympic Year Analysis ===")
olympic_analysis = {}

# Compute "expected visits" via 3-year rolling mean of surrounding years
df_clean['visits_lag1'] = df_clean['total_us'].shift(1)
df_clean['visits_lag2'] = df_clean['total_us'].shift(2)
df_clean['visits_lead1'] = df_clean['total_us'].shift(-1)

# For each Olympic year, compare actual to mean of (year-2, year-1, year+1)
def olympic_excess(row):
    surrounding = []
    yr = row['year']
    for offset in [-2, -1, 1, 2]:
        match = df[df['year'] == yr+offset]
        if not match.empty and match['covid_truncated'].iloc[0] == 0:
            surrounding.append(match['total_us'].iloc[0])
    if not surrounding:
        return np.nan
    return row['total_us'] - np.mean(surrounding)

df['olympic_excess'] = df.apply(olympic_excess, axis=1)

us_olympics = df[df['is_us_olympic']==1].copy()
na_olympics = df[(df['is_na_olympic']==1) & (df['is_us_olympic']==0)].copy()
overseas_olympics = df[(df['is_any_olympic']==1) & (df['is_na_olympic']==0)].copy()
nonolympic = df[df['is_any_olympic']==0].copy()

olympic_analysis['us_host_years'] = us_olympics[['season','total_us','olympic_excess']].to_dict(orient='records')
olympic_analysis['na_host_years'] = na_olympics[['season','total_us','olympic_excess']].to_dict(orient='records')
olympic_analysis['overseas_olympic_years'] = overseas_olympics[['season','total_us','olympic_excess']].to_dict(orient='records')

# Mean excess for each category
olympic_analysis['us_host_mean_excess'] = float(us_olympics['olympic_excess'].mean())
olympic_analysis['na_host_mean_excess'] = float(na_olympics['olympic_excess'].mean())
olympic_analysis['overseas_mean_excess'] = float(overseas_olympics['olympic_excess'].mean())

results['olympic_analysis'] = olympic_analysis
print(json.dumps({
    'us_host_mean_excess': olympic_analysis['us_host_mean_excess'],
    'na_host_mean_excess': olympic_analysis['na_host_mean_excess'],
    'overseas_mean_excess': olympic_analysis['overseas_mean_excess'],
}, indent=2))

# ---- 8. CHOW TEST: Pre vs Post-Epic, Pre vs Post-Ikon ----
print("\n=== Section 5: Structural Breakpoint Tests ===")
import statsmodels.api as sm

def chow_test(df, breakpoint, y_col='total_us', x_col='year'):
    """Chow test for structural break in OLS regression of y on x"""
    sub = df[[y_col, x_col]].dropna().copy()
    sub = sub[df.loc[sub.index, 'covid_truncated']==0]
    
    pre = sub[sub[x_col] < breakpoint]
    post = sub[sub[x_col] >= breakpoint]
    if len(pre) < 5 or len(post) < 5:
        return None
    
    # Pooled
    X_pooled = sm.add_constant(sub[x_col])
    pooled = sm.OLS(sub[y_col], X_pooled).fit()
    rss_pooled = (pooled.resid**2).sum()
    
    # Separate
    X_pre = sm.add_constant(pre[x_col])
    pre_fit = sm.OLS(pre[y_col], X_pre).fit()
    rss_pre = (pre_fit.resid**2).sum()
    
    X_post = sm.add_constant(post[x_col])
    post_fit = sm.OLS(post[y_col], X_post).fit()
    rss_post = (post_fit.resid**2).sum()
    
    k = 2  # number of parameters
    n1 = len(pre)
    n2 = len(post)
    chow_F = ((rss_pooled - (rss_pre + rss_post)) / k) / ((rss_pre + rss_post) / (n1 + n2 - 2*k))
    
    from scipy.stats import f as f_dist
    p = 1 - f_dist.cdf(chow_F, k, n1+n2-2*k)
    
    return {
        'chow_F': float(chow_F),
        'p_value': float(p),
        'n_pre': n1,
        'n_post': n2,
        'pre_slope': float(pre_fit.params[x_col]),
        'pre_intercept': float(pre_fit.params['const']),
        'post_slope': float(post_fit.params[x_col]),
        'post_intercept': float(post_fit.params['const']),
        'pooled_slope': float(pooled.params[x_col]),
    }

chow_results = {}
chow_results['epic_2009'] = chow_test(df, 2009)
chow_results['ikon_2019'] = chow_test(df, 2019)
chow_results['covid_2021'] = chow_test(df, 2021)  # using post-COVID (2021+)
results['chow_tests'] = chow_results
print(json.dumps(chow_results, indent=2))

# ---- 9. MULTIVARIATE OLS ----
print("\n=== Section 6: Multivariate OLS ===")
df_ols = df_clean.dropna(subset=['total_us','real_gdp_t','rdpi_dec']).copy()
# Build trend term (years since start)
df_ols['t'] = df_ols['year'] - df_ols['year'].min()

X_specs = {
    'M1: Trend only': ['t'],
    'M2: + Real GDP': ['t','real_gdp_t'],
    'M3: + RDPI/cap': ['t','real_gdp_t','rdpi_dec'],
    'M4: + Olympic flags': ['t','real_gdp_t','rdpi_dec','is_us_olympic','is_na_olympic','is_any_olympic'],
    'M5: + Pass-era flags': ['t','real_gdp_t','rdpi_dec','is_us_olympic','is_na_olympic','is_any_olympic','post_epic','post_ikon','post_covid'],
}

ols_results = {}
for name, vars_ in X_specs.items():
    X = sm.add_constant(df_ols[vars_])
    fit = sm.OLS(df_ols['total_us'], X).fit()
    ols_results[name] = {
        'r2': float(fit.rsquared),
        'r2_adj': float(fit.rsquared_adj),
        'aic': float(fit.aic),
        'bic': float(fit.bic),
        'n': int(fit.nobs),
        'coef': {k: float(v) for k, v in fit.params.items()},
        'pvals': {k: float(v) for k, v in fit.pvalues.items()},
    }
    print(f"\n{name}: R²={fit.rsquared:.3f}, adj-R²={fit.rsquared_adj:.3f}, AIC={fit.aic:.1f}")
    print(fit.summary().as_text()[:600])

results['ols'] = ols_results

# ---- 10. REGIONAL TIME-SERIES PLOT ----
fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
regions_info = [
    ('northeast', 'Northeast', NAVY),
    ('southeast', 'Southeast', GOLD),
    ('midwest', 'Midwest', SAPPHIRE),
    ('rocky_mountain', 'Rocky Mountain', RED),
    ('pacific_southwest', 'Pacific Southwest', FOREST),
    ('pacific_northwest', 'Pacific Northwest', SLATE),
]
for ax, (col, label, color) in zip(axes.flat, regions_info):
    ax.plot(df['year'], df[col], '-', color=color, linewidth=1.5, marker='o', markersize=2.5)
    ax.set_title(label, loc='left', fontsize=11)
    ax.set_ylabel('Visits (M)', fontsize=9)
    ax.set_xlim(1978, 2026)
    if 'pacific' in col.lower():
        ax.text(1990, ax.get_ylim()[1]*0.85, '(reported only\nfrom 1995/96)',
                fontsize=8, color=INK_SOFT, style='italic')

axes[1,0].set_xlabel('Year')
axes[1,1].set_xlabel('Year')
axes[1,2].set_xlabel('Year')
plt.suptitle('Skier visits by NSAA region, 1978–79 through 2024–25',
             fontsize=12, fontweight='bold', y=1.02, ha='left', x=0.05)
plt.tight_layout()
plt.savefig(FIG_DIR / 'fig04_regional_timeseries.svg')
plt.savefig(FIG_DIR / 'fig04_regional_timeseries.png')
plt.close()
print("Fig 4 saved")

# ---- 11. REGIONAL SHARES CHANGE ----
print("\n=== Section 7: Regional Share Trends ===")
df_shares = df.copy()
for col in ['northeast','southeast','midwest','rocky_mountain','pacific_southwest','pacific_northwest','pacific_west_total']:
    df_shares[f'share_{col}'] = df_shares[col] / df_shares['total_us'] * 100

# Change in share, recent decade vs first decade
share_changes = {}
recent = df_shares[(df_shares['year'] >= 2015) & (df_shares['year'] <= 2024) & (df_shares['covid_truncated']==0)]
early_post95 = df_shares[(df_shares['year'] >= 1996) & (df_shares['year'] <= 2005)]  # First decade with PSW/PNW split
for col in ['northeast','southeast','midwest','rocky_mountain','pacific_southwest','pacific_northwest']:
    early_share = early_post95[f'share_{col}'].mean()
    recent_share = recent[f'share_{col}'].mean()
    share_changes[col] = {
        'early_share_pct': float(early_share),
        'recent_share_pct': float(recent_share),
        'change_pct_pts': float(recent_share - early_share)
    }
results['share_changes'] = share_changes
print(json.dumps(share_changes, indent=2))

# Stacked area share plot
fig, ax = plt.subplots(figsize=(10, 4.5))
df_post95 = df[df['year'] >= 1996].copy()
shares = pd.DataFrame({
    'Northeast': df_post95['northeast'] / df_post95['total_us'] * 100,
    'Southeast': df_post95['southeast'] / df_post95['total_us'] * 100,
    'Midwest': df_post95['midwest'] / df_post95['total_us'] * 100,
    'Rocky Mountain': df_post95['rocky_mountain'] / df_post95['total_us'] * 100,
    'Pacific Southwest': df_post95['pacific_southwest'] / df_post95['total_us'] * 100,
    'Pacific Northwest': df_post95['pacific_northwest'] / df_post95['total_us'] * 100,
})
ax.stackplot(df_post95['year'].values,
             [shares['Northeast'].values, shares['Southeast'].values,
              shares['Midwest'].values, shares['Rocky Mountain'].values,
              shares['Pacific Southwest'].values, shares['Pacific Northwest'].values],
             labels=['Northeast','Southeast','Midwest','Rocky Mountain','Pacific SW','Pacific NW'],
             colors=[NAVY, GOLD, SAPPHIRE, RED, FOREST, SLATE], alpha=0.85)
ax.set_ylim(0, 100)
ax.set_xlim(1996, 2025)
ax.set_ylabel('Share of national visits (%)')
ax.set_xlabel('Year')
ax.set_title('Regional share of U.S. skier visits, 1995–96 through 2024–25', loc='left')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=6, fontsize=8, frameon=False)
plt.tight_layout()
plt.savefig(FIG_DIR / 'fig05_regional_shares.svg')
plt.savefig(FIG_DIR / 'fig05_regional_shares.png')
plt.close()
print("Fig 5 saved")

# ---- 12. POST-COVID COMPARISON ----
print("\n=== Section 8: Post-COVID baseline shift ===")
pre_covid = df_clean[(df_clean['year'] >= 2015) & (df_clean['year'] <= 2019)]
post_covid = df_clean[df_clean['year'] >= 2021]
covid_analysis = {
    'pre_covid_2015_2019_mean': float(pre_covid['total_us'].mean()),
    'pre_covid_2015_2019_std': float(pre_covid['total_us'].std()),
    'post_covid_2021_mean': float(post_covid['total_us'].mean()),
    'post_covid_2021_std': float(post_covid['total_us'].std()),
    'shift_M': float(post_covid['total_us'].mean() - pre_covid['total_us'].mean()),
    'shift_pct': float((post_covid['total_us'].mean() - pre_covid['total_us'].mean()) / pre_covid['total_us'].mean() * 100),
}
t_cv, p_cv = stats.ttest_ind(post_covid['total_us'], pre_covid['total_us'], equal_var=False)
covid_analysis['t_stat'] = float(t_cv)
covid_analysis['p_value'] = float(p_cv)
results['covid_baseline'] = covid_analysis
print(json.dumps(covid_analysis, indent=2))

# ---- 13. WEATHER COUPLING (where data exists) ----
# We have national snowfall for 2022-2025 (only 4 points). Real analysis is limited.
# We'll use the *qualitative* observations from NSAA narratives instead.
# But let's check correlation of YOY change in visits across all periods
df_clean['visits_yoy_chg'] = df_clean['total_us'].diff()

# ---- 14. BY DECADE COMPARISON BARCHART ----
fig, ax = plt.subplots(figsize=(10, 4))
decades = ['1980s','1990s','2000s','2010s','2020s']
period_means = [desc['period_1980s_mean'], desc['period_1990s_mean'],
                desc['period_2000s_mean'], desc['period_2010s_mean'], desc['period_2020s_mean']]
period_stds = [desc['period_1980s_std'], desc['period_1990s_std'],
               desc['period_2000s_std'], desc['period_2010s_std'], desc['period_2020s_std']]

bars = ax.bar(decades, period_means, color=NAVY, alpha=0.75, edgecolor=INK, linewidth=0.5)
ax.errorbar(decades, period_means, yerr=period_stds, fmt='none', color=INK, capsize=4, linewidth=1)
for bar, val in zip(bars, period_means):
    ax.text(bar.get_x() + bar.get_width()/2, val + 1, f'{val:.1f}M',
            ha='center', va='bottom', fontsize=9, color=INK)
ax.set_ylabel('Mean skier visits (millions)')
ax.set_title('Decade means and within-decade standard deviation',
             loc='left')
ax.set_ylim(0, 75)
plt.tight_layout()
plt.savefig(FIG_DIR / 'fig06_decade_means.svg')
plt.savefig(FIG_DIR / 'fig06_decade_means.png')
plt.close()
print("Fig 6 saved")

# ---- 15. OLYMPIC EFFECT VISUALIZATION ----
fig, ax = plt.subplots(figsize=(10, 4.5))
# Plot each Olympic year as bar showing excess over local mean
us_olympics = df.dropna(subset=['olympic_excess']).query('is_us_olympic==1')
na_olympics = df.dropna(subset=['olympic_excess']).query('is_na_olympic==1 and is_us_olympic==0')
overseas_olympics = df.dropna(subset=['olympic_excess']).query('is_any_olympic==1 and is_na_olympic==0')

xs = np.arange(len(df[df['is_any_olympic']==1]))
olympic_yrs = df[df['is_any_olympic']==1].sort_values('year')
colors = []
for _, row in olympic_yrs.iterrows():
    if row['is_us_olympic']:
        colors.append(RED)
    elif row['is_na_olympic']:
        colors.append(GOLD)
    else:
        colors.append(SLATE)

ax.bar(xs, olympic_yrs['olympic_excess'].values, color=colors, alpha=0.85, edgecolor=INK, linewidth=0.5)
ax.axhline(0, color=INK, linewidth=0.7)
ax.set_xticks(xs)
ax.set_xticklabels([f"{int(r['year'])}\n{r['olympic_host']}" for _, r in olympic_yrs.iterrows()], fontsize=8, rotation=0)
ax.set_ylabel('Visits anomaly vs local mean (M)\n[year - mean of (yr-2, yr-1, yr+1, yr+2)]')
ax.set_title('Olympic-year skier visits: excess vs surrounding-year baseline', loc='left')

# Legend
from matplotlib.patches import Patch
legend = [Patch(facecolor=RED, label='U.S. host'),
          Patch(facecolor=GOLD, label='Canadian host'),
          Patch(facecolor=SLATE, label='Overseas host')]
ax.legend(handles=legend, loc='lower right', fontsize=8, frameon=False)
plt.tight_layout()
plt.savefig(FIG_DIR / 'fig07_olympic_effect.svg')
plt.savefig(FIG_DIR / 'fig07_olympic_effect.png')
plt.close()
print("Fig 7 saved")

# ---- 16. PRE/POST EPIC, IKON RELATIONSHIPS ----
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

# Pre-Epic vs Post-Epic visits-vs-RDPI relationship
ax = axes[0]
pre = df_clean[df_clean['year'] < 2009]
post = df_clean[df_clean['year'] >= 2009]
ax.scatter(pre['rdpi_dec']/1000, pre['total_us'], color=SAPPHIRE, alpha=0.7, s=40, label=f'Pre-Epic (n={len(pre)})', edgecolor='white', linewidth=0.5)
ax.scatter(post['rdpi_dec']/1000, post['total_us'], color=RED, alpha=0.7, s=40, label=f'Post-Epic (n={len(post)})', edgecolor='white', linewidth=0.5)
# Fit lines
for sub, color in [(pre, SAPPHIRE), (post, RED)]:
    if len(sub) > 3:
        slope, intercept, r, p, se = stats.linregress(sub['rdpi_dec']/1000, sub['total_us'])
        xx = np.linspace((sub['rdpi_dec']/1000).min(), (sub['rdpi_dec']/1000).max(), 30)
        ax.plot(xx, slope*xx + intercept, color=color, linewidth=1.3, alpha=0.6)
ax.set_xlabel('Real disposable income/capita ($K)')
ax.set_ylabel('Skier visits (millions)')
ax.set_title('Pre- vs post-Epic Pass relationships', loc='left', fontsize=10)
ax.legend(loc='lower right', fontsize=9, frameon=False)

# Same for Ikon
ax = axes[1]
pre = df_clean[df_clean['year'] < 2019]
post = df_clean[df_clean['year'] >= 2019]
ax.scatter(pre['rdpi_dec']/1000, pre['total_us'], color=SAPPHIRE, alpha=0.7, s=40, label=f'Pre-Ikon (n={len(pre)})', edgecolor='white', linewidth=0.5)
ax.scatter(post['rdpi_dec']/1000, post['total_us'], color=FOREST, alpha=0.7, s=40, label=f'Post-Ikon (n={len(post)})', edgecolor='white', linewidth=0.5)
for sub, color in [(pre, SAPPHIRE), (post, FOREST)]:
    if len(sub) > 3:
        slope, intercept, r, p, se = stats.linregress(sub['rdpi_dec']/1000, sub['total_us'])
        xx = np.linspace((sub['rdpi_dec']/1000).min(), (sub['rdpi_dec']/1000).max(), 30)
        ax.plot(xx, slope*xx + intercept, color=color, linewidth=1.3, alpha=0.6)
ax.set_xlabel('Real disposable income/capita ($K)')
ax.set_ylabel('Skier visits (millions)')
ax.set_title('Pre- vs post-Ikon Pass relationships', loc='left', fontsize=10)
ax.legend(loc='lower right', fontsize=9, frameon=False)

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig08_pre_post_passes.svg')
plt.savefig(FIG_DIR / 'fig08_pre_post_passes.png')
plt.close()
print("Fig 8 saved")

# ---- 17. CORRELATION HEATMAP ----
print("\n=== Section 9: Correlation Matrix ===")
keyvars = ['total_us','northeast','rocky_mountain','pacific_southwest','real_gdp_t','rdpi_dec']
clean = df_clean[keyvars].dropna()
corr_matrix = clean.corr()

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(corr_matrix.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax.set_xticks(range(len(keyvars)))
ax.set_yticks(range(len(keyvars)))
nice_labels = ['Visits (US)','Visits (NE)','Visits (RM)','Visits (PSW)','Real GDP','RDPI/cap']
ax.set_xticklabels(nice_labels, rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(nice_labels, fontsize=9)
# Add r values
for i in range(len(keyvars)):
    for j in range(len(keyvars)):
        v = corr_matrix.values[i,j]
        ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                color='white' if abs(v) > 0.5 else INK, fontsize=9)
plt.colorbar(im, ax=ax, label='Pearson r', shrink=0.8)
ax.set_title('Correlation matrix: visits vs macroeconomic indicators', loc='left')
plt.tight_layout()
plt.savefig(FIG_DIR / 'fig09_correlation_heatmap.svg')
plt.savefig(FIG_DIR / 'fig09_correlation_heatmap.png')
plt.close()
print("Fig 9 saved")

# ---- 18. ROCKY MOUNTAIN GROWTH FOCUS ----
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(df['year'], df['rocky_mountain'], '-', color=RED, linewidth=2, marker='o', markersize=3.5, label='Rocky Mountain')
ax.plot(df['year'], df['northeast'], '-', color=NAVY, linewidth=1.5, marker='s', markersize=3, label='Northeast', alpha=0.8)
# Polynomial trend (Rocky)
df_rm = df[df['rocky_mountain'].notna()]
z = np.polyfit(df_rm['year'], df_rm['rocky_mountain'], 1)
yy = np.poly1d(z)(df_rm['year'])
ax.plot(df_rm['year'], yy, '--', color=RED, linewidth=1, alpha=0.5, label=f'Rocky Mountain trend ({z[0]:+.2f} M/yr)')
# Northeast trend
df_ne = df[df['northeast'].notna()]
z_ne = np.polyfit(df_ne['year'], df_ne['northeast'], 1)
yy_ne = np.poly1d(z_ne)(df_ne['year'])
ax.plot(df_ne['year'], yy_ne, '--', color=NAVY, linewidth=1, alpha=0.5, label=f'Northeast trend ({z_ne[0]:+.2f} M/yr)')

ax.set_xlabel('Year')
ax.set_ylabel('Skier visits (millions)')
ax.set_title('The geographic divergence: Rocky Mountain vs Northeast, 1978–79 to 2024–25', loc='left')
ax.set_xlim(1978, 2026)
ax.legend(loc='upper left', fontsize=9, frameon=False)
plt.tight_layout()
plt.savefig(FIG_DIR / 'fig10_rocky_vs_NE.svg')
plt.savefig(FIG_DIR / 'fig10_rocky_vs_NE.png')
plt.close()
print("Fig 10 saved")

# ---- 19. POST-COVID FOCUS PLOT ----
fig, ax = plt.subplots(figsize=(10, 4.5))
df_recent = df[df['year'] >= 2010].copy()
colors_pt = []
for _, row in df_recent.iterrows():
    if row['covid_truncated']==1:
        colors_pt.append(RED)
    elif row['post_covid']==1:
        colors_pt.append(FOREST)
    else:
        colors_pt.append(NAVY)

ax.bar(df_recent['year'], df_recent['total_us'], color=colors_pt, alpha=0.85,
       edgecolor=INK, linewidth=0.4)
# Pre-COVID 2015-2019 mean line
pre_mean = covid_analysis['pre_covid_2015_2019_mean']
post_mean = covid_analysis['post_covid_2021_mean']
ax.axhline(pre_mean, color=NAVY, linestyle='--', linewidth=1.2, label=f'2015–19 mean: {pre_mean:.1f}M')
ax.axhline(post_mean, color=FOREST, linestyle='--', linewidth=1.2, label=f'2021–25 mean: {post_mean:.1f}M')
ax.set_xlabel('Year')
ax.set_ylabel('Skier visits (millions)')
ax.set_title(f"Post-COVID baseline shift: +{covid_analysis['shift_M']:.1f}M visits/year (+{covid_analysis['shift_pct']:.1f}%)",
             loc='left')
ax.set_ylim(45, 70)
ax.set_xticks(df_recent['year'])
ax.set_xticklabels(df_recent['year'], rotation=45)
ax.legend(loc='upper left', fontsize=9, frameon=False)
plt.tight_layout()
plt.savefig(FIG_DIR / 'fig11_postcovid_baseline.svg')
plt.savefig(FIG_DIR / 'fig11_postcovid_baseline.png')
plt.close()
print("Fig 11 saved")

# ---- 20. Save results JSON ----
with open(OUT_DIR / 'analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nAll analysis results saved to {OUT_DIR / 'analysis_results.json'}")
print(f"All figures saved to {FIG_DIR}/")
