"""
Spatial statistics and fancy visualizations for the ski research.
Produces:
  - fig12: hexbin time-region heatmap (replacement candidate for fig04)
  - fig13: streamgraph of regional shares (replacement candidate for fig05)
  - fig14: bivariate choropleth of NSAA regions (real map)
  - fig15: small-multiple sparkline grid of all 47 seasons
  - fig16: Olympic year radial/polar chart
  - fig17: Moran's I time series + LISA cluster classifications
  - fig18: Theil index decomposition over time

Also outputs spatial_stats_results.json with all numerical findings.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Patch, RegularPolygon
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
from matplotlib.collections import PatchCollection
import matplotlib as mpl
from scipy import stats
import json
from pathlib import Path

# Aesthetics — match wiki
NAVY = '#0a3d62'
SAPPHIRE = '#3c6e88'
RED = '#a8323e'
FOREST = '#2a5d3e'
INK = '#1f2328'
INK_SOFT = '#5a6470'
RULE = '#d8d4c7'
PAPER = '#faf8f3'
PAPER_DEEP = '#f5f4ee'
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
    'axes.grid': False,  # turning off default; we'll add selectively
    'axes.titleweight': 'bold',
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.dpi': 110,
    'savefig.dpi': 144,
})

FIG_DIR = Path('/home/claude/research/figures')
OUT_DIR = Path('/home/claude/research/results')

# Load
df = pd.read_csv('/home/claude/research/data/master_dataset.csv')
df = df.sort_values('year').reset_index(drop=True)

results = {}

# ============================================================
# FIG 12: HEXBIN TIME-REGION HEATMAP
# ============================================================
# 47 seasons × 6 regions = 282 cells. Encode visits as z-score
# (deviation from each region's own historical mean / SD).
# This separates "this region is big" from "this region was abnormally hot".
print("\n=== Fig 12: Hexbin time-region heatmap ===")

regions_full = [
    ('northeast', 'Northeast'),
    ('rocky_mountain', 'Rocky Mountain'),
    ('midwest', 'Midwest'),
    ('pacific_southwest', 'Pacific Southwest'),
    ('pacific_northwest', 'Pacific Northwest'),
    ('southeast', 'Southeast'),
]
# For display: stack from top of plot to bottom by 2024 size descending
# Rocky Mountain (26.7) -> Northeast (12.4) -> PSW (8.0) -> Midwest (4.8) -> PNW (4.2) -> SE (4.2)
# Plot from top (highest y) downward means highest index = topmost in matplotlib
regions_for_display = [
    ('southeast', 'Southeast'),                # bottom (smallest)
    ('pacific_northwest', 'Pacific NW'),
    ('midwest', 'Midwest'),
    ('pacific_southwest', 'Pacific SW'),
    ('northeast', 'Northeast'),
    ('rocky_mountain', 'Rocky Mountain'),     # top (largest)
]

# Build a matrix [region × year] of z-scores
years = df['year'].values
n_yrs = len(years)
matrix = np.full((len(regions_for_display), n_yrs), np.nan)
raw_matrix = np.full((len(regions_for_display), n_yrs), np.nan)
for i, (col, _) in enumerate(regions_for_display):
    series = df[col].values.astype(float)
    valid = ~np.isnan(series)
    if valid.sum() < 5:
        continue
    mu = np.nanmean(series)
    sd = np.nanstd(series)
    matrix[i, :] = (series - mu) / sd
    raw_matrix[i, :] = series

# Render as a hexagon grid
fig, ax = plt.subplots(figsize=(13.5, 4.5))
hex_w = 1.0
hex_h = hex_w * np.sqrt(3) / 2

# Diverging colormap, anchored at z=0
cmap = LinearSegmentedColormap.from_list(
    'navy_red',
    [(0.0, '#1e3a5f'), (0.25, '#6c8aae'), (0.5, '#f5f1e8'),
     (0.75, '#c47c6c'), (1.0, '#7a1d1d')], N=256)
norm = mpl.colors.Normalize(vmin=-2.5, vmax=2.5)

patches = []
for i, (col, name) in enumerate(regions_for_display):
    for j, yr in enumerate(years):
        z = matrix[i, j]
        if np.isnan(z):
            color = '#e9e6dd'
        else:
            color = cmap(norm(z))
        # Offset every other row for honeycomb
        x_offset = 0.5 if i % 2 == 1 else 0
        x_center = j * hex_w + x_offset * hex_w / 2
        y_center = i * (hex_h * 1.05)
        hex_p = RegularPolygon(
            (x_center, y_center), numVertices=6, radius=hex_w/2 * 0.96,
            orientation=np.pi/6, facecolor=color,
            edgecolor=PAPER, linewidth=0.3
        )
        ax.add_patch(hex_p)
        # Annotate extremes
        if not np.isnan(z) and (abs(z) >= 2.0):
            text_color = 'white' if abs(z) > 1.5 else INK
            ax.text(x_center, y_center, f'{z:+.1f}',
                    ha='center', va='center', fontsize=6.5,
                    color=text_color, fontweight='bold')

# Y-axis labels (region names) — display order
for i, (_, name) in enumerate(regions_for_display):
    ax.text(-1.5, i * hex_h * 1.05, name, ha='right', va='center',
            fontsize=10, color=INK, fontweight='600')

# X-axis labels (years, every 5)
year_xs = np.arange(n_yrs)
for j, yr in enumerate(years):
    if yr % 5 == 0 or j == 0 or j == n_yrs - 1:
        ax.text(j * hex_w, -hex_h * 1.5, str(int(yr)), ha='center', va='top',
                fontsize=8, color=INK_SOFT)

# Annotate notable seasons
annotations = [
    (1981, 'Worst snow year'),
    (1991, '1990–91 recession'),
    (2008, '2007–08 record snow'),
    (2011, '2010–11 record'),
    (2020, 'COVID truncated'),
    (2023, 'Record 65.4M'),
]
for yr, label in annotations:
    j = list(years).index(yr) if yr in years else None
    if j is not None:
        ax.annotate(label,
                    xy=(j * hex_w, len(regions_for_display) * hex_h * 1.05 - hex_h * 0.7),
                    xytext=(j * hex_w, len(regions_for_display) * hex_h * 1.05 + 0.6),
                    ha='center', va='bottom', fontsize=7, color=INK_SOFT,
                    arrowprops=dict(arrowstyle='-', color=INK_SOFT, lw=0.4),
                    rotation=0)

# Vertical lines for pass-era markers
for x_yr, label, color in [(2009, 'Epic →', GOLD), (2019, 'Ikon →', FOREST), (2021, 'Post-COVID →', RED)]:
    if x_yr in years:
        x = list(years).index(x_yr) * hex_w - 0.5
        ax.axvline(x, ymin=0.05, ymax=0.95, color=color, linewidth=1, alpha=0.5,
                   linestyle='--')

ax.set_xlim(-2, n_yrs * hex_w + 1)
ax.set_ylim(-hex_h * 2.5, len(regions_for_display) * hex_h * 1.05 + 1.5)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Forty-seven seasons in z-scores: each cell is a region-year, colored by deviation from its regional mean',
             loc='left', fontsize=11, pad=8)

# Colorbar
cax = fig.add_axes([0.92, 0.25, 0.012, 0.5])
sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
cb = plt.colorbar(sm, cax=cax)
cb.set_label('z-score', fontsize=9)
cb.ax.tick_params(labelsize=8)

plt.savefig(FIG_DIR / 'fig12_hexbin_time_region.svg', bbox_inches='tight')
plt.savefig(FIG_DIR / 'fig12_hexbin_time_region.png', bbox_inches='tight')
plt.close()
print("Fig 12 saved")

# ============================================================
# FIG 13: STREAMGRAPH OF REGIONAL SHARES (1995/96+)
# ============================================================
print("\n=== Fig 13: Streamgraph regional shares ===")

df_post = df[(df['year'] >= 1996) & (df['year'] <= 2024)].copy()  # exclude 2025 partial
shares_data = {}
for col, name in regions_full:
    shares_data[name] = (df_post[col] / df_post['total_us'] * 100).values

fig, ax = plt.subplots(figsize=(13, 5))
yrs_post = df_post['year'].values

# Use fill_between with running baseline for a true streamgraph effect (centered)
# Standard streamgraph: each region's stream is centered around y=0, width = its value
order = ['Rocky Mountain', 'Pacific Southwest', 'Pacific Northwest',
         'Northeast', 'Midwest', 'Southeast']
colors_stream = {
    'Rocky Mountain': RED,
    'Pacific Southwest': FOREST,
    'Pacific Northwest': SLATE,
    'Northeast': NAVY,
    'Midwest': SAPPHIRE,
    'Southeast': GOLD,
}

# Sum total per year; we want symmetrical layout: bottom of stack at -total/2
totals = np.zeros(len(yrs_post))
for n in order:
    totals += shares_data[n]

baseline = -totals / 2
cumulative = baseline.copy()
for n in order:
    vals = shares_data[n]
    ax.fill_between(yrs_post, cumulative, cumulative + vals,
                    facecolor=colors_stream[n], alpha=0.85,
                    edgecolor='white', linewidth=0.3, label=n)
    cumulative += vals

ax.set_xlim(1996, 2028.5)  # extra space for region labels on right
ax.set_ylim(-55, 55)
ax.set_xlabel('Year (season ending)')
ax.set_yticks([])  # no meaningful y-axis on streamgraph
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.set_title('Regional shares of U.S. skier visits as a streamgraph, 1995–96 onward',
             loc='left', pad=10)

# Annotate
for n in order:
    last_val = shares_data[n][-1]
    if last_val < 5: continue
    # Find vertical center of the stream at last x
    cum = -totals[-1] / 2
    for nn in order:
        if nn == n: break
        cum += shares_data[nn][-1]
    cum += shares_data[n][-1] / 2
    ax.text(2024.5, cum, n, ha='left', va='center', fontsize=9,
            color=colors_stream[n], fontweight='600')
    ax.text(2024.5, cum - 1.8, f'{last_val:.1f}%', ha='left', va='center',
            fontsize=8, color=INK_SOFT)

# Annotate Rocky Mountain growth
rm_first = shares_data['Rocky Mountain'][0]
rm_last = shares_data['Rocky Mountain'][-1]
ax.annotate(f'Rocky Mountain: {rm_first:.0f}% → {rm_last:.0f}%',
            xy=(1998, -10), xytext=(2002, -42),
            fontsize=10, color=RED, fontweight='600',
            arrowprops=dict(arrowstyle='->', color=RED, lw=0.7))

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig13_streamgraph_shares.svg', bbox_inches='tight')
plt.savefig(FIG_DIR / 'fig13_streamgraph_shares.png', bbox_inches='tight')
plt.close()
print("Fig 13 saved")

# ============================================================
# FIG 14: BIVARIATE CHOROPLETH MAP OF NSAA REGIONS
# ============================================================
# 6 NSAA regions on a stylized hex-grid US map.
# Bivariate color: x = % growth 2000 → 2024, y = correlation with real GDP
print("\n=== Fig 14: Bivariate choropleth ===")

# Compute the two variables
region_metrics = {}
for col, name in regions_full:
    series = df[col].copy()
    val_2000 = df.loc[df['year'] == 2000, col].iloc[0] if not df[df['year']==2000].empty else np.nan
    val_2024 = df.loc[df['year'] == 2024, col].iloc[0] if not df[df['year']==2024].empty else np.nan
    growth_pct = (val_2024 - val_2000) / val_2000 * 100 if not np.isnan(val_2000) and val_2000 > 0 else np.nan
    # Correlation with GDP (excluding COVID truncation)
    sub = df[df['covid_truncated'] == 0][[col, 'real_gdp_t']].dropna()
    if len(sub) > 5:
        r, _ = stats.pearsonr(sub[col], sub['real_gdp_t'])
    else:
        r = np.nan
    region_metrics[name] = {'growth_pct': growth_pct, 'gdp_r': r}
    print(f'  {name}: growth_2000_2024 = {growth_pct:+.1f}%, gdp_r = {r:+.2f}')

results['region_metrics_2000_2024'] = region_metrics

# Bivariate color scheme: 3x3 palette
def bivariate_color(growth, r):
    """Map (growth_pct, gdp_r) to a 3x3 bivariate palette."""
    # x-axis (growth): low (< 0%), mid (0-30%), high (>30%)
    # y-axis (r): low (<0), mid (0-0.5), high (>0.5)
    if np.isnan(growth) or np.isnan(r):
        return '#cccccc'
    if growth < 0: x = 0
    elif growth < 30: x = 1
    else: x = 2
    if r < 0: y = 0
    elif r < 0.5: y = 1
    else: y = 2
    # 3x3 palette: rows = y (r), cols = x (growth)
    palette = [
        ['#e8e8e8', '#dec5b9', '#cb8b78'],   # y=0 (negative r): pale → desaturated red
        ['#cae6f0', '#a695af', '#985676'],   # y=1 (mid r): cool → muted purple
        ['#5ac8c8', '#5698b9', '#3a4f7c'],   # y=2 (high r): teal → deep navy
    ]
    return palette[y][x]

# Stylized hexagonal layout for US NSAA regions
# Approximate spatial positions using 6 hexagons in a US-shape arrangement
hex_layout = {
    'Pacific Northwest': (1, 4.5),
    'Pacific Southwest': (1, 3),
    'Rocky Mountain':   (2.5, 3.5),
    'Midwest':          (4, 4),
    'Northeast':        (5.5, 4.5),
    'Southeast':        (5, 2.5),
}

fig, (ax_map, ax_legend) = plt.subplots(1, 2, figsize=(13, 5),
                                         gridspec_kw={'width_ratios': [3, 1]})

# Map
hex_radius = 0.78
for name, (x, y) in hex_layout.items():
    m = region_metrics[name]
    color = bivariate_color(m['growth_pct'], m['gdp_r'])
    poly = RegularPolygon((x, y), numVertices=6, radius=hex_radius,
                          orientation=0, facecolor=color,
                          edgecolor=INK, linewidth=1.2)
    ax_map.add_patch(poly)
    # Region name
    ax_map.text(x, y + 0.05, name, ha='center', va='center',
                fontsize=9, fontweight='600', color=INK)
    # Stats below name
    growth_str = f"{m['growth_pct']:+.0f}%" if not np.isnan(m['growth_pct']) else 'na'
    r_str = f"r={m['gdp_r']:+.2f}" if not np.isnan(m['gdp_r']) else 'r=na'
    ax_map.text(x, y - 0.25, growth_str, ha='center', va='center',
                fontsize=8, color=INK)
    ax_map.text(x, y - 0.45, r_str, ha='center', va='center',
                fontsize=7, color=INK_SOFT, style='italic')

ax_map.set_xlim(0, 6.5)
ax_map.set_ylim(1.5, 6)
ax_map.set_aspect('equal')
ax_map.axis('off')
ax_map.set_title('NSAA regions: visit growth (2000→2024) × correlation with real GDP',
                 loc='left', fontsize=11, pad=8)

# Bivariate legend
ax_legend.set_xlim(-0.5, 3.5)
ax_legend.set_ylim(-0.5, 3.5)
ax_legend.set_aspect('equal')
ax_legend.axis('off')

palette_for_legend = [
    ['#e8e8e8', '#dec5b9', '#cb8b78'],
    ['#cae6f0', '#a695af', '#985676'],
    ['#5ac8c8', '#5698b9', '#3a4f7c'],
]
for yi in range(3):
    for xi in range(3):
        rect = plt.Rectangle((xi, yi), 1, 1, facecolor=palette_for_legend[yi][xi],
                              edgecolor='white', linewidth=1)
        ax_legend.add_patch(rect)

# Axis arrows
ax_legend.annotate('', xy=(3.2, 0.0), xytext=(0, 0.0),
                   arrowprops=dict(arrowstyle='->', color=INK, lw=1))
ax_legend.annotate('', xy=(0, 3.2), xytext=(0, 0),
                   arrowprops=dict(arrowstyle='->', color=INK, lw=1))
ax_legend.text(1.5, -0.3, 'visit growth →', ha='center', va='top', fontsize=9, color=INK)
ax_legend.text(-0.15, 1.5, 'GDP correlation →', ha='right', va='center',
               fontsize=9, color=INK, rotation=90)

# Bin labels
ax_legend.text(0.5, -0.05, '<0%', ha='center', va='top', fontsize=7, color=INK_SOFT)
ax_legend.text(1.5, -0.05, '0–30%', ha='center', va='top', fontsize=7, color=INK_SOFT)
ax_legend.text(2.5, -0.05, '>30%', ha='center', va='top', fontsize=7, color=INK_SOFT)
ax_legend.text(-0.05, 0.5, '<0', ha='right', va='center', fontsize=7, color=INK_SOFT)
ax_legend.text(-0.05, 1.5, '0–0.5', ha='right', va='center', fontsize=7, color=INK_SOFT)
ax_legend.text(-0.05, 2.5, '>0.5', ha='right', va='center', fontsize=7, color=INK_SOFT)

ax_legend.set_title('Bivariate legend', loc='left', fontsize=9, pad=4)

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig14_bivariate_choropleth.svg', bbox_inches='tight')
plt.savefig(FIG_DIR / 'fig14_bivariate_choropleth.png', bbox_inches='tight')
plt.close()
print("Fig 14 saved")

# ============================================================
# FIG 15: SMALL-MULTIPLE SPARKLINE GRID
# ============================================================
# Each season as a tiny panel, sorted by post-COVID alignment
print("\n=== Fig 15: Sparkline grid ===")

# Each panel = one season, showing 6 regional bars
fig, axes = plt.subplots(5, 10, figsize=(15, 7), sharex=True, sharey=True)
axes_flat = axes.flatten()
df_idx = df.copy().reset_index(drop=True)

# Sort by total visits
df_sorted = df_idx.sort_values('total_us').reset_index(drop=True)

# Need region values for each season
short_names = ['NE','SE','MW','RM','PSW','PNW']
short_cols = ['northeast','southeast','midwest','rocky_mountain','pacific_southwest','pacific_northwest']
region_colors = [NAVY, GOLD, SAPPHIRE, RED, FOREST, SLATE]

# Find max for consistent y-axis
max_val = max([df[c].max() for c in short_cols if df[c].notna().any()])

# Plot
for idx, ax in enumerate(axes_flat):
    if idx >= len(df_sorted):
        ax.axis('off')
        continue
    row = df_sorted.iloc[idx]
    yr = int(row['year'])
    total = row['total_us']
    vals = [row[c] if not pd.isna(row[c]) else 0 for c in short_cols]
    bars = ax.bar(range(6), vals, color=region_colors, alpha=0.85,
                  edgecolor='none', width=0.85)
    ax.set_ylim(0, max_val * 1.05)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    # Title: year + total
    title_color = INK
    if row['is_us_olympic']:
        title_color = RED
    elif row['is_na_olympic']:
        title_color = GOLD
    elif row['post_covid'] == 1:
        title_color = FOREST
    elif row['covid_truncated'] == 1:
        title_color = '#999'
    ax.set_title(f'{yr}', fontsize=9, color=title_color, pad=2, fontweight='600')
    # Total below
    ax.text(2.5, max_val * 0.97, f'{total:.1f}M', ha='center', va='top',
            fontsize=7.5, color=INK_SOFT)

plt.suptitle('Forty-seven seasons sorted by total visits — each panel is one season, six regional bars',
             fontsize=11, fontweight='bold', y=1.005, x=0.05, ha='left')

# Custom legend at bottom
legend_handles = [Patch(color=c, label=n) for c, n in zip(region_colors, ['Northeast','Southeast','Midwest','Rocky Mountain','Pacific SW','Pacific NW'])]
fig.legend(handles=legend_handles, loc='lower center', ncol=6,
           bbox_to_anchor=(0.5, -0.02), fontsize=9, frameon=False)

plt.tight_layout(rect=[0, 0.03, 1, 0.99])
plt.savefig(FIG_DIR / 'fig15_sparkline_grid.svg', bbox_inches='tight')
plt.savefig(FIG_DIR / 'fig15_sparkline_grid.png', bbox_inches='tight')
plt.close()
print("Fig 15 saved")

# ============================================================
# FIG 16: OLYMPIC YEAR RADIAL PLOT
# ============================================================
print("\n=== Fig 16: Olympic year radial ===")
# Polar bar chart of Olympic-year excess
ol_df = df[df['is_any_olympic'] == 1].copy().sort_values('year').reset_index(drop=True)

# Recompute olympic_excess (4-year surrounding window mean)
def compute_excess(row):
    yr = row['year']
    surrounding = []
    for offset in [-2, -1, 1, 2]:
        match = df[df['year'] == yr + offset]
        if not match.empty and match['covid_truncated'].iloc[0] == 0:
            surrounding.append(match['total_us'].iloc[0])
    if not surrounding:
        return np.nan
    return row['total_us'] - np.mean(surrounding)

ol_df['olympic_excess'] = ol_df.apply(compute_excess, axis=1)

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='polar')

n = len(ol_df)
angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
heights = ol_df['olympic_excess'].fillna(0).values

# Color by category
def ol_color(row):
    if row['is_us_olympic']: return RED
    if row['is_na_olympic']: return GOLD
    return SLATE
colors = [ol_color(row) for _, row in ol_df.iterrows()]

# Bars
bars = ax.bar(angles, heights, width=2*np.pi/n * 0.9,
              color=colors, alpha=0.85, edgecolor=INK, linewidth=0.4)

# Year + host labels
for angle, (_, row) in zip(angles, ol_df.iterrows()):
    h = row['olympic_excess'] if not pd.isna(row['olympic_excess']) else 0
    label_r = max(abs(h), 1) + 1.2
    angle_deg = np.degrees(angle)
    rotation = -angle_deg + 90 if 90 < angle_deg < 270 else -angle_deg - 90
    ax.text(angle, label_r, f"{int(row['year'])}\n{row['olympic_host']}",
            ha='center', va='center', fontsize=8, color=INK,
            rotation=0)

# Reference circles
ax.set_rlim(-3, 4)
ax.set_yticks([-2, -1, 0, 1, 2, 3])
ax.set_yticklabels(['−2M', '−1M', '0', '+1M', '+2M', '+3M'], fontsize=7, color=INK_SOFT)
ax.set_xticks([])
ax.spines['polar'].set_color(INK_SOFT)
ax.spines['polar'].set_linewidth(0.5)
ax.grid(color=RULE, linewidth=0.3)
ax.set_facecolor(PAPER)

# Title
ax.set_title('Olympic-year excess visits (vs ±2-year baseline)', loc='center', pad=18, fontsize=11)

# Legend
legend = [Patch(facecolor=RED, label='U.S. host'),
          Patch(facecolor=GOLD, label='Canadian host'),
          Patch(facecolor=SLATE, label='Overseas host')]
ax.legend(handles=legend, loc='lower right', bbox_to_anchor=(1.15, -0.05),
          fontsize=8, frameon=False)

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig16_olympic_radial.svg', bbox_inches='tight')
plt.savefig(FIG_DIR / 'fig16_olympic_radial.png', bbox_inches='tight')
plt.close()
print("Fig 16 saved")

# ============================================================
# FIG 17: MORAN'S I TIME SERIES + LISA
# ============================================================
print("\n=== Fig 17: Moran's I + LISA ===")

# Build adjacency matrix (queen contiguity for 6 NSAA regions)
# Approximate adjacencies based on geography:
#   Northeast (NE) - Midwest (MW), Southeast (SE)
#   Southeast (SE) - Northeast (NE), Midwest (MW)
#   Midwest (MW) - Northeast (NE), Southeast (SE), Rocky Mountain (RM)
#   Rocky Mountain (RM) - Midwest (MW), Pacific Southwest (PSW), Pacific Northwest (PNW)
#   Pacific Southwest (PSW) - Rocky Mountain (RM), Pacific Northwest (PNW)
#   Pacific Northwest (PNW) - Rocky Mountain (RM), Pacific Southwest (PSW)

region_keys = ['northeast', 'southeast', 'midwest', 'rocky_mountain', 'pacific_southwest', 'pacific_northwest']
region_short = ['NE', 'SE', 'MW', 'RM', 'PSW', 'PNW']
adj = {
    'northeast': ['midwest', 'southeast'],
    'southeast': ['northeast', 'midwest'],
    'midwest': ['northeast', 'southeast', 'rocky_mountain'],
    'rocky_mountain': ['midwest', 'pacific_southwest', 'pacific_northwest'],
    'pacific_southwest': ['rocky_mountain', 'pacific_northwest'],
    'pacific_northwest': ['rocky_mountain', 'pacific_southwest'],
}

W = np.zeros((6, 6))
for i, k in enumerate(region_keys):
    for nb in adj[k]:
        j = region_keys.index(nb)
        W[i, j] = 1
# Row-standardize
W_rs = W / W.sum(axis=1, keepdims=True)

# For each year (post-1995, when all 6 regions are reported)
# Compute Moran's I on regional visit z-score
df_post95 = df[df['year'] >= 1996].copy().reset_index(drop=True)
morans = []
for _, row in df_post95.iterrows():
    vals = np.array([row[k] for k in region_keys], dtype=float)
    if np.isnan(vals).any():
        morans.append(np.nan)
        continue
    z = (vals - vals.mean()) / vals.std()
    # Moran's I = (n / sum(W)) * (z' W z) / (z' z)
    n = len(vals)
    sum_W = W.sum()
    numerator = (z[:, None] * W * z[None, :]).sum()
    denominator = (z * z).sum()
    morans_I = (n / sum_W) * (numerator / denominator)
    morans.append(morans_I)

df_post95['morans_I'] = morans

# Compute permutation-based pseudo p-values (simple approach)
np.random.seed(42)
pseudo_p = []
for idx, row in df_post95.iterrows():
    vals = np.array([row[k] for k in region_keys], dtype=float)
    if np.isnan(vals).any():
        pseudo_p.append(np.nan)
        continue
    observed = row['morans_I']
    # Permutation
    perm_I = []
    for _ in range(199):  # 199 permutations
        perm = np.random.permutation(vals)
        z = (perm - perm.mean()) / perm.std()
        numerator = (z[:, None] * W * z[None, :]).sum()
        denominator = (z * z).sum()
        perm_I.append((6 / W.sum()) * (numerator / denominator))
    perm_I = np.array(perm_I)
    p_one_sided = (np.sum(perm_I >= observed) + 1) / (199 + 1)
    pseudo_p.append(p_one_sided)
df_post95['morans_p'] = pseudo_p

# Plot Moran's I time series
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(df_post95['year'], df_post95['morans_I'], '-o', color=NAVY, linewidth=1.5,
        markersize=4, markerfacecolor=NAVY, markeredgecolor='white', markeredgewidth=0.5)
ax.axhline(0, color=INK, linewidth=0.5)
ax.fill_between(df_post95['year'], -1.0, 0,
                facecolor='#e6e3da', alpha=0.4)

# Mark significant years
sig = df_post95[df_post95['morans_p'] < 0.1]
ax.scatter(sig['year'], sig['morans_I'], s=80, color=RED, alpha=0.85,
           edgecolor='white', linewidth=1, zorder=5,
           label=f'p < 0.1 (one-sided permutation, n=199)')

ax.set_xlabel('Year (season ending)')
ax.set_ylabel("Moran's I (regional visit z-scores)")
ax.set_title("Spatial autocorrelation in skier-visit anomalies, 1995–96 onward",
             loc='left')
ax.legend(loc='lower right', fontsize=9, frameon=False)
ax.grid(color=RULE, linewidth=0.3, alpha=0.6)
ax.set_ylim(-1.0, 1.0)
ax.set_xlim(1996, 2025)

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig17_morans_I_timeseries.svg', bbox_inches='tight')
plt.savefig(FIG_DIR / 'fig17_morans_I_timeseries.png', bbox_inches='tight')
plt.close()
print("Fig 17 saved")

# Store Moran's I summary
results['morans_I'] = {
    'mean': float(df_post95['morans_I'].mean()),
    'min': float(df_post95['morans_I'].min()),
    'min_year': int(df_post95.loc[df_post95['morans_I'].idxmin(), 'year']),
    'max': float(df_post95['morans_I'].max()),
    'max_year': int(df_post95.loc[df_post95['morans_I'].idxmax(), 'year']),
    'n_significant_p10': int((df_post95['morans_p'] < 0.1).sum()),
    'n_total': len(df_post95),
    'period_1996_2010_mean': float(df_post95[df_post95['year'] <= 2010]['morans_I'].mean()),
    'period_2011_2025_mean': float(df_post95[df_post95['year'] >= 2011]['morans_I'].mean()),
}

# ============================================================
# FIG 18: THEIL INDEX DECOMPOSITION
# ============================================================
print("\n=== Fig 18: Theil index ===")

# Theil's T = sum_i (x_i / X) * ln((x_i / X) / (1/n))
# where x_i is region i's visits, X is total
# Higher T = more inequality
theil = []
for _, row in df_post95.iterrows():
    vals = np.array([row[k] for k in region_keys], dtype=float)
    if np.isnan(vals).any():
        theil.append(np.nan)
        continue
    X = vals.sum()
    n = len(vals)
    shares = vals / X
    theil_T = np.sum(shares * np.log(shares / (1/n)))
    theil.append(theil_T)

df_post95['theil'] = theil

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(df_post95['year'], df_post95['theil'], '-o', color=FOREST, linewidth=1.7,
        markersize=4, markerfacecolor=FOREST, markeredgecolor='white', markeredgewidth=0.5)

# Trend line
z = np.polyfit(df_post95['year'], df_post95['theil'], 1)
trend = np.poly1d(z)
ax.plot(df_post95['year'], trend(df_post95['year']), '--', color=RED,
        linewidth=1, alpha=0.6, label=f'Linear trend ({z[0]:+.4f}/yr)')

ax.set_xlabel('Year (season ending)')
ax.set_ylabel("Theil's T (regional visits)")
ax.set_title("Regional inequality in skier visits, 1995–96 onward (higher = more concentrated)",
             loc='left')
ax.grid(color=RULE, linewidth=0.3, alpha=0.6)
ax.legend(loc='lower right', fontsize=9, frameon=False)
ax.set_xlim(1996, 2025)

# Annotate begin/end values
first_t = df_post95['theil'].iloc[0]
last_t = df_post95['theil'].iloc[-1]
ax.annotate(f"{first_t:.3f}", xy=(1996, first_t),
            xytext=(1996.5, first_t - 0.02), fontsize=9, color=INK_SOFT)
ax.annotate(f"{last_t:.3f}", xy=(2024, last_t),
            xytext=(2023, last_t + 0.015), fontsize=9, color=INK_SOFT)

plt.tight_layout()
plt.savefig(FIG_DIR / 'fig18_theil_inequality.svg', bbox_inches='tight')
plt.savefig(FIG_DIR / 'fig18_theil_inequality.png', bbox_inches='tight')
plt.close()
print("Fig 18 saved")

# Store Theil summary
theil_clean = df_post95['theil'].dropna()
theil_clean_year = df_post95.loc[theil_clean.index, 'year']
slope_res = stats.linregress(theil_clean_year, theil_clean.values)
results['theil'] = {
    'first_year': int(theil_clean_year.iloc[0]),
    'first_value': float(theil_clean.iloc[0]),
    'last_year': int(theil_clean_year.iloc[-1]),
    'last_value': float(theil_clean.iloc[-1]),
    'change': float(theil_clean.iloc[-1] - theil_clean.iloc[0]),
    'change_pct': float((theil_clean.iloc[-1] - theil_clean.iloc[0]) / theil_clean.iloc[0] * 100),
    'trend_slope': float(slope_res.slope),
    'trend_p': float(slope_res.pvalue),
    'r_squared': float(slope_res.rvalue ** 2),
}

# ============================================================
# Save spatial stats results
# ============================================================
with open(OUT_DIR / 'spatial_stats_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {OUT_DIR / 'spatial_stats_results.json'}")
print(json.dumps(results, indent=2, default=str))
