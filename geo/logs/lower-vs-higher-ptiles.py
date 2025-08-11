# ---
# jupyter:
#   jupytext:
#     formats: ipynb,logs//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python (venv_nbhmv)
#     language: python
#     name: venv_nbhmv
# ---

# %%
import pandas as pd
import janitor

janitor

import geopandas as gpd

import warnings

warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import make_axes
import seaborn as sns

sns.set_theme(context="notebook", style="white", font_scale=1.2, palette="bright")
# from palettable import *
from palettable import colorbrewer

from utilities import add_north_arrow, add_scalebar, save_mpl_fig

FP_SUBZONE_SHP2014 = "input/master-plan-2014-subzone-boundary-no-sea/master-plan-2014-subzone-boundary-no-sea-shp.zip"
FP_PANEL = "input/cd-panel-labels.csv"

# %%
gdf_subzones = (
    gpd.read_file(FP_SUBZONE_SHP2014)
    .to_crs("EPSG:4326")
    .clean_names()
    .assign(subzone=lambda df_: df_["subzone_n"].str.lower())
    .filter(["subzone", "geometry", "pln_area_n", "region_c"])
)
gdf_subzones

# %%
gdf_subzones = (
    gpd.read_file(FP_SUBZONE_SHP2014)
    .to_crs("EPSG:4326")
    .clean_names()
    .assign(subzone=lambda df_: df_["subzone_n"].str.lower())
    .filter(["subzone", "geometry", "pln_area_n", "region_c"])
)
gdf_subzones

# %%
df = (
    pd.read_csv(FP_PANEL, low_memory=False)
    .rename_column("home", "subzone")
    .drop_duplicates(["subzone"], ignore_index=True)
    # ==============
    .assign(
        wpsm_ptile=lambda df_: df_["wpsm_home"].rank(method="max", pct=True).mul(100),
        wpsm_qtile=lambda df_: (
            (df_["wpsm_ptile"] // 25).clip(0, 3).add(1).astype("Int8")
        ),
    )
)

df.head()

# %%
gdf = gdf_subzones.merge(df, on="subzone", how="right", validate="1:1")
gdf.head()

# %% code_folding=[0]
# plot
_, ax = plt.subplots(figsize=(6, 4))
gdf.query("resident_count_home>0").plot(
    column="wpsm_qtile",
    categorical=True,
    cmap="RdBu",
    linewidth=0.3,
    edgecolor="white",
    legend=True,
    ax=ax,
)
plt.tight_layout()

# %% code_folding=[]
# plot
# Create custom cmap
# base_cmap = plt.cm.get_cmap("RdBu")
# base_cmap = cmocean.diverging.Curl_20.get_mpl_colormap()
base_cmap = colorbrewer.diverging.RdGy_11_r.get_mpl_colormap()
# base_cmap = lightbartlein.diverging.BlueGray_8_r.get_mpl_colormap()
# base_cmap = lightbartlein.diverging.GreenMagenta_16.get_mpl_colormap()
# base_cmap = lightbartlein.diverging.BlueDarkOrange18_18_r.get_mpl_colormap()
# base_cmap = colorbrewer.diverging.PRGn_11_r.get_mpl_colormap()
# base_cmap = scientific.diverging.Lisbon_20.get_mpl_colormap()
# base_cmap = cmocean.diverging.Delta_20_r.get_mpl_colormap()
split = 25  # where the hue switch should be
asym_cmap = LinearSegmentedColormap.from_list(
    "custom_asym",
    [(0.0, base_cmap(0.00)), (split / 100.0, base_cmap(0.50)), (1.0, base_cmap(1.00))],
    N=100,
)
norm = mcolors.Normalize(vmin=0, vmax=100)

# Init plot
fig, ax = plt.subplots(figsize=(12, 8))
gdf.query("resident_count_home>0").plot(
    column="wpsm_ptile",
    cmap=asym_cmap,
    norm=norm,
    edgecolor="none",
    linewidth=0.3,
    alpha=0.99,
    legend=False,
    ax=ax,
    missing_kwds={"color": "lightgrey", "label": "No data"},
)

# Compose Color bar
sm = ScalarMappable(norm=norm, cmap=asym_cmap)
sm.set_array([])
axins, kw = make_axes(
    ax,
    location="bottom",
    fraction=0.9,
    shrink=0.40,
    aspect=8,
    pad=0.12,
    anchor=(1.05, 0),
)
cbar = fig.colorbar(sm, cax=axins, **kw)
cbar.set_ticks([0, split, 50, 75, 100])
cbar.set_ticklabels([0, 25, 50, 75, 100])
cbar.ax.tick_params(labelsize=12)
cbar.ax.set_title(
    "Neighborhood house price percentile",
    fontsize=12,
    pad=6,
    loc="center",
    color=".3",
    fontweight="bold",
)

# Add simple text annotations below the colorbar using figure coordinates
# Get colorbar position in figure coordinates
cbar_pos = cbar.ax.get_position()
left_x = cbar_pos.x0
right_x = cbar_pos.x1
width = cbar_pos.width
bottom_y = cbar_pos.y0

# Calculate positions for the two labels
left_center = left_x + (split / 100) * width * 0.5  # Center of 0-25% range
right_center = left_x + (split / 100 + 1) * width * 0.5  # Center of 25-100% range

# Add bracket annotations using figure.add_artist
from matplotlib.lines import Line2D

TO_START_Y_POS = -0.05
TO_BOTTOM_Y_POS = -0.065
# Left bracket (0-25%) - shape: |_____|
# Left vertical line (down from colorbar)
line1 = Line2D(
    [left_x, left_x],
    [bottom_y + TO_START_Y_POS, bottom_y + TO_BOTTOM_Y_POS],
    color=".4",
    linewidth=1.5,
    transform=fig.transFigure,
)
fig.add_artist(line1)

# Bottom horizontal line
line2 = Line2D(
    [left_x, left_x + (split / 100) * width],
    [bottom_y + TO_BOTTOM_Y_POS, bottom_y + TO_BOTTOM_Y_POS],
    color=".4",
    linewidth=1.5,
    transform=fig.transFigure,
)
fig.add_artist(line2)

# Right vertical line for left bracket
line3 = Line2D(
    [left_x + (split / 100) * width, left_x + (split / 100) * width],
    [bottom_y + TO_START_Y_POS, bottom_y + TO_BOTTOM_Y_POS],
    color=".4",
    linewidth=1.5,
    transform=fig.transFigure,
)
fig.add_artist(line3)

# Right bracket (25-100%) - shape: |___________________|
# Left vertical line for right bracket
line4 = Line2D(
    [
        (left_x * 1.005) + (split / 100) * width,
        (left_x * 1.005) + (split / 100) * width,
    ],
    [bottom_y + TO_START_Y_POS, bottom_y + TO_BOTTOM_Y_POS],
    color=".4",
    linewidth=1.5,
    transform=fig.transFigure,
)
fig.add_artist(line4)

# Bottom horizontal line
line5 = Line2D(
    [(left_x * 1.005) + (split / 100) * width, right_x],
    [bottom_y + TO_BOTTOM_Y_POS, bottom_y + TO_BOTTOM_Y_POS],
    color=".4",
    linewidth=1.5,
    transform=fig.transFigure,
    linestyle="--",
)
fig.add_artist(line5)

# Right vertical line
line6 = Line2D(
    [right_x, right_x],
    [bottom_y + TO_START_Y_POS, bottom_y + TO_BOTTOM_Y_POS],
    color=".4",
    linewidth=1.5,
    transform=fig.transFigure,
)
fig.add_artist(line6)

# Add text labels
fig.text(
    left_center,
    bottom_y + (TO_BOTTOM_Y_POS * 1.1),
    "Bottom 25%",
    ha="center",
    va="top",
    fontsize=10,
    color=".3",
    fontweight="bold",
)

fig.text(
    right_center,
    bottom_y + (TO_BOTTOM_Y_POS * 1.1),
    "Top 75%",
    ha="center",
    va="top",
    fontsize=10,
    color=".3",
    fontweight="bold",
)

# axis settings
ax.set_xlim(103.683, 103.992)
ax.set_ylim(1.255, 1.460)
add_north_arrow(ax=ax, x=103.98, y=1.445, fontsize=25)
add_scalebar(ax=ax, location="lower left", fontsize=25)
plt.tight_layout()
ax.set_axis_off()
save_mpl_fig("../results/figures/supplementary/lower-vs-higher-ptiles")

# %%
