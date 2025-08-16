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
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import contextily as cx

from utilities import add_north_arrow, add_segmented_scalebar, save_mpl_fig

SAVEPATH = "../results/figures/supplementary/"

import warnings

warnings.filterwarnings("ignore")

FP_REGION_SHP2014 = "input/master-plan-2014-region-boundary-no-sea/master-plan-2014-region-boundary-no-sea-shp.zip"
FP_SUBZONE_SHP2014 = "input/master-plan-2014-subzone-boundary-no-sea/master-plan-2014-subzone-boundary-no-sea-shp.zip"
FP_ZONE_SHP2014 = "input/master-plan-2014-planning-area-boundary-no-sea/master-plan-2014-planning-area-boundary-no-sea-shp.zip"
FP_HTYPE = "input/htype.csv"

# %% [markdown]
# ## Regions

# %%
regions2014 = gpd.read_file(FP_REGION_SHP2014).to_crs("EPSG:4326")
zones = gpd.read_file(FP_ZONE_SHP2014).to_crs("EPSG:4326")
subzones = gpd.read_file(FP_SUBZONE_SHP2014).to_crs("EPSG:4326")

EDGECOLOR = "maroon"
LINEWIDTH = 3
MAPPROVIDER = cx.providers.CartoDB.PositronNoLabels
BASEMAP_OPTS = dict(crs=regions2014.crs, source=MAPPROVIDER, attribution="", zorder=0)

SCALEBAR_OPTS = dict(
    height_fraction=0.012,
    location="lower right",
    segments=[2, 2, 2, 4, 4, 4],
    unit_position="right",
    label_offset=0.005,
    unit_label_spacing=0.005,
    fontsize=14,
    unit_fontsize=15,
)
NORTH_ARROW_OPTS = dict(x=104.08, y=1.46, fontsize=25)

# %%
_, ax = plt.subplots(figsize=(12, 12))

regions2014.plot(
    color="white",
    edgecolor=EDGECOLOR,
    linewidth=LINEWIDTH,
    alpha=0.5,
    rasterized=True,
    ax=ax,
    zorder=1,
)

cx.add_basemap(**BASEMAP_OPTS, ax=ax)
add_north_arrow(ax=ax, **NORTH_ARROW_OPTS)
add_segmented_scalebar(ax, **SCALEBAR_OPTS)
plt.tight_layout()
plt.margins(0, 0)
plt.axis("off")

save_mpl_fig(os.path.join(SAVEPATH, "borders-region"))

# %% [markdown]
# ## Planning areas

# %%
_, ax = plt.subplots(figsize=(12, 12))

zones.plot(
    color="white",
    edgecolor=EDGECOLOR,
    linewidth=LINEWIDTH,
    alpha=0.5,
    rasterized=True,
    ax=ax,
    zorder=1,
)

cx.add_basemap(**BASEMAP_OPTS, ax=ax)
add_north_arrow(ax=ax, **NORTH_ARROW_OPTS)
add_segmented_scalebar(ax, **SCALEBAR_OPTS)
plt.tight_layout()
plt.margins(0, 0)
plt.axis("off")

save_mpl_fig(os.path.join(SAVEPATH, "borders-zones"))

# %% [markdown]
# ## Subzones

# %%
_, ax = plt.subplots(figsize=(12, 12))

subzones.plot(
    color="white",
    edgecolor=EDGECOLOR,
    linewidth=1,
    alpha=0.5,
    rasterized=True,
    ax=ax,
    zorder=1,
)

cx.add_basemap(**BASEMAP_OPTS, ax=ax)
add_north_arrow(ax=ax, **NORTH_ARROW_OPTS)
add_segmented_scalebar(ax, **SCALEBAR_OPTS)
plt.tight_layout()
plt.margins(0, 0)
plt.axis("off")

save_mpl_fig(os.path.join(SAVEPATH, "borders-subzones"))

# %% [markdown]
# ## Neighborhoods

# %%
# Read in URA2014 version
subzones2014 = (
    gpd.read_file(FP_SUBZONE_SHP2014)
    .rename(columns={"SUBZONE_N": "subzone"})
    .assign(subzone=lambda df: df["subzone"].str.lower())
    .assign(centroid=lambda df: df["geometry"].centroid)
    .to_crs("EPSG:4326")
)

htype = (
    pd.read_csv(FP_HTYPE, usecols=["area", "resident_count", "rm12", "private"])
    .rename(columns={"area": "subzone"})
    .assign(resident_count=lambda df: df["resident_count"].replace(0, np.nan))
)

htype = subzones2014[["subzone", "geometry", "PLN_AREA_N", "REGION_C"]].merge(
    htype, how="left", on="subzone", validate="1:1"
)
htype.head()

# %%
_, ax = plt.subplots(figsize=(12, 12))

# Subzones non-residential/missing areas
MISSKWDS = {
    "color": "black",
    "edgecolor": "white",
    "hatch": "+",
    "label": "Missing values",
}

htype[htype["resident_count"].isnull()].plot(
    column="resident_count",
    edgecolor="white",
    missing_kwds=MISSKWDS,
    alpha=0.6,
    ax=ax,
    zorder=2,
)

subzones.plot(
    color="white",
    edgecolor=EDGECOLOR,
    linewidth=1,
    alpha=0.5,
    rasterized=True,
    ax=ax,
    zorder=1,
)

cx.add_basemap(**BASEMAP_OPTS, ax=ax)
add_north_arrow(ax=ax, **NORTH_ARROW_OPTS)
add_segmented_scalebar(ax, **SCALEBAR_OPTS)
plt.tight_layout()
plt.margins(0, 0)
plt.axis("off")

save_mpl_fig(os.path.join(SAVEPATH, "borders-neighbourhoods"))

# %%

# %%
