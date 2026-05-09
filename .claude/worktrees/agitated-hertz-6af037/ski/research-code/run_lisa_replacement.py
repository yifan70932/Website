"""Replace fig17 with LISA cluster maps for selected years."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Patch
import matplotlib as mpl
from pathlib import Path

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
    'axes.titleweight': 'bold',
})

FIG_DIR = Path('/home/claude/research/figures')
df = pd.read_csv('/home/claude/research/data/master_dataset.csv').sort_values('year').reset_index(drop=True)

# 6 NSAA regions, hex layout (US-style stylized)
hex_layout = {
    'pacific_northwest': (1, 4.5),
    'pacific_southwest': (1, 3),
    'rocky_mountain':   (2.5, 3.5),
    'midwest':          (4, 4),
    'northeast':        (5.5, 4.5),
    'southeast':        (5, 2.5),
}
short_names = {
    'pacific_northwest': 'PNW',
    'pacific_southwest': 'PSW',
    'rocky_mountain': 'RM',
    'midwest': 'MW',
    'northeast': 'NE',
    'southeast': 'SE',
}
adj = {
    'northeast': ['midwest', 'southeast'],
    'southeast': ['northeast', 'midwest'],
    'midwest': ['northeast', 'southeast', 'rocky_mountain'],
    'rocky_mountain': ['midwest', 'pacific_southwest', 'pacific_northwest'],
    'pacific_southwest': ['rocky_mountain', 'pacific_northwest'],
    'pacific_northwest': ['rocky_mountain', 'pacific_southwest'],
}
region_keys = list(hex_layout.keys())

def lisa_classify(row):
    """Classify each region by Anselin's LISA quadrants:
    H-H: high own value, high neighbor mean
    L-L: low, low
    H-L: high, low (outlier-positive)
    L-H: low, high (outlier-negative)
    Use z-scores of the row's region values.
    """
    vals = np.array([row[k] for k in region_keys], dtype=float)
    if np.isnan(vals).any():
        return None
    z = (vals - vals.mean()) / vals.std()
    classes = {}
    for i, k in enumerate(region_keys):
        # neighbor mean z
        nb_indices = [region_keys.index(nb) for nb in adj[k]]
        nb_mean_z = z[nb_indices].mean()
        own_z = z[i]
        if own_z >= 0 and nb_mean_z >= 0:
            classes[k] = 'HH'
        elif own_z < 0 and nb_mean_z < 0:
            classes[k] = 'LL'
        elif own_z >= 0 and nb_mean_z < 0:
            classes[k] = 'HL'
        else:
            classes[k] = 'LH'
    return classes

color_lisa = {
    'HH': RED,        # high-high cluster (hot)
    'LL': NAVY,       # low-low cluster (cold)
    'HL': '#e8a23c',  # high outlier in low neighborhood
    'LH': '#7eaaca',  # low outlier in high neighborhood
}
label_lisa = {
    'HH': 'High–High (hot)',
    'LL': 'Low–Low (cold)',
    'HL': 'High–Low (hot outlier)',
    'LH': 'Low–High (cold outlier)',
}

# Pick 4 representative years
selected_years = [1996, 2008, 2019, 2024]
fig, axes = plt.subplots(1, 4, figsize=(15, 4.2))

for ax, yr in zip(axes, selected_years):
    row = df[df['year'] == yr]
    if row.empty:
        continue
    row = row.iloc[0]
    classes = lisa_classify(row)
    
    for k, (x, y) in hex_layout.items():
        cls = classes.get(k) if classes else None
        color = color_lisa.get(cls, '#cccccc') if cls else '#cccccc'
        poly = RegularPolygon((x, y), numVertices=6, radius=0.78,
                              orientation=0, facecolor=color, alpha=0.85,
                              edgecolor=INK, linewidth=1.0)
        ax.add_patch(poly)
        ax.text(x, y + 0.05, short_names[k], ha='center', va='center',
                fontsize=9, fontweight='600',
                color='white' if cls in ('HH','LL') else INK)
        # Visit value
        val = row[k]
        ax.text(x, y - 0.3, f'{val:.1f}M', ha='center', va='center',
                fontsize=7, color='white' if cls in ('HH','LL') else INK_SOFT)
    
    ax.set_xlim(0, 6.5)
    ax.set_ylim(1.5, 6)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'{int(yr - 1)}–{str(int(yr))[-2:]}', fontsize=12, pad=4)

# Legend
legend_handles = [Patch(facecolor=c, edgecolor=INK, label=label_lisa[k])
                  for k, c in color_lisa.items()]
fig.legend(handles=legend_handles, loc='lower center', ncol=4,
           bbox_to_anchor=(0.5, -0.02), fontsize=9, frameon=False)

fig.suptitle("LISA cluster map: each region's status relative to its neighbors, four representative seasons",
             fontsize=12, y=1.00, x=0.05, ha='left')

plt.tight_layout(rect=[0, 0.04, 1, 0.96])
plt.savefig(FIG_DIR / 'fig17_lisa_clusters.svg', bbox_inches='tight')
plt.savefig(FIG_DIR / 'fig17_lisa_clusters.png', bbox_inches='tight')
plt.close()
print("Fig 17 (LISA) saved")

# Remove old fig17_morans_I_timeseries by renaming it to a backup
import os
old = FIG_DIR / 'fig17_morans_I_timeseries.svg'
if old.exists():
    os.rename(old, FIG_DIR / 'fig17_morans_I_timeseries_OLD.svg')
old_png = FIG_DIR / 'fig17_morans_I_timeseries.png'
if old_png.exists():
    os.rename(old_png, FIG_DIR / 'fig17_morans_I_timeseries_OLD.png')
print("Old Morans I figure renamed to _OLD")
