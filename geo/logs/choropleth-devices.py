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
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import contextily as cx
from legendgram import legendgram
from mapclassify import Quantiles
import palettable.matplotlib as mplpal
import yaml

import warnings

warnings.filterwarnings("ignore")

FP_SUBZONE_SHP2014 = "input/master-plan-2014-subzone-boundary-no-sea/master-plan-2014-subzone-boundary-no-sea-kml.zip"
FP_DEVICECOUNT = "./out/devicecount-subzone-day.csv"
FP_RESCOUNT = "input/htype.csv"

from utilities import add_north_arrow, add_scalebar, save_mpl_fig

# %%
with open("../api.yml", "r") as file:
    config = yaml.safe_load(file)

api_key = config["maps"]["stadia"]["api_key"]
basemap = f"https://tiles.stadiamaps.com/tiles/stamen_toner_background/{{z}}/{{x}}/{{y}}.png?api_key={api_key}"

# %%
SCHEME = "quantiles"
DPI = 50
CMAP = "viridis_r"
MAINPLOT_ALPHA = 0.85
EDGECOLOR = "white"
LINEWIDTH = 0.5

BASEMAP_ALPHA = 0.60

# %%
subzones2014 = gpd.read_file(FP_SUBZONE_SHP2014)
subzones2014.head(5)

# %% [markdown]
# ## Prep residents

# %%
# Read in res count
gdf_rescount = (
    pd.read_csv(FP_RESCOUNT)
    .assign(area=lambda df: df["area"].str.upper())
    .merge(subzones2014, how="right", left_on="area", right_on="Name")
    .pipe(
        lambda df: gpd.GeoDataFrame(df, crs=subzones2014.crs, geometry=df["geometry"])
    )
    .assign(resident_count=lambda df_: df_["resident_count"].replace(0, np.nan))
)
gdf_rescount.head()

# %%
# Plot pop
_, ax = plt.subplots(figsize=(8, 6))

# Plot devices density
gdf_rescount.query('Name!="SENTOSA"').plot(
    column="resident_count",
    cmap=CMAP,
    alpha=MAINPLOT_ALPHA,
    scheme=SCHEME,
    k=10,
    edgecolor=EDGECOLOR,
    linewidth=LINEWIDTH,
    ax=ax,
)

bins = Quantiles(
    gdf_rescount.query("resident_count==resident_count").resident_count, k=10
).bins
hax = legendgram(
    plt.gcf(),
    ax,
    gdf_rescount.resident_count,
    bins,  # the breaks to induce color differences on
    pal=mplpal.Viridis_10_r,  # the palette to use,
    legend_size=(
        0.35,
        0.2,
    ),  # the size of the subplot, in fractions of the original axis
    loc="lower right",  # the location on the axis
    clip=(100, 80000),  # bounds to clip the view of the histogram
)

# Add basemap
cx.add_basemap(
    crs=gdf_rescount.crs,
    source=basemap,
    attribution="",
    alpha=BASEMAP_ALPHA,
    zoom=12,
    ax=ax,
    zorder=0,
)

plt.tight_layout()
ylim = ax.get_ylim()
xlim = ax.get_xlim()
add_north_arrow(ax=ax, x=103.99, y=1.44, fontsize=30)
add_scalebar(ax=ax, location="lower left", fontsize=20)
plt.axis("off")
ax.axis("off")
save_mpl_fig("../results/figures/supplementary/choropleth-resident-legend")

# %% [markdown]
# ## Prep devices

# %%
# Clean obvious name errors from Citydata (to get perfect match)
clean_cd_subzone = {
    "marina east mp": "marina east (mp)",
    "monks hill": "monk's hill",
    "national university of s pore": "national university of s'pore",
    "peoples park": "people's park",
}

gdf_device = (
    pd.read_csv(FP_DEVICECOUNT)
    .assign(devices=lambda df: df["android_count"] + df["ios_count"])
    .groupby("subzone")["devices"]
    .sum()
    .reset_index()
    .assign(subzone=lambda df: df["subzone"].str.strip().replace(clean_cd_subzone))
    .assign(subzone=lambda df: df["subzone"].str.upper())
    .merge(subzones2014, how="right", left_on="subzone", right_on="Name")
    .pipe(
        lambda df: gpd.GeoDataFrame(df, crs=subzones2014.crs, geometry=df["geometry"])
    )
    #               .assign(centroid=lambda df: df['geometry'].centroid)
    #               .drop('geometry', axis=1)
    .rename(columns={"centroid": "geometry"})
    .query('subzone!="CITY HALL"')
    .query('subzone!="BOAT QUAY"')
    .assign(size=lambda df: np.log(df["devices"]) * 3)
    .query("subzone==subzone")
    # Merge to get residential areas
    .merge(
        gdf_rescount[gdf_rescount["resident_count"] != 0][["area", "resident_count"]],
        how="left",
        left_on="subzone",
        right_on="area",
        validate="1:1",
    )
    .assign(
        devices=lambda df: np.where(
            pd.isna(df["resident_count"]), np.nan, df["devices"]
        )
    )
)
gdf_device.head(3)

# %%
# Plot devices
_, ax = plt.subplots(figsize=(8, 6))

# Plot devices density
gdf_device.plot(
    column="devices",
    cmap=CMAP,
    alpha=MAINPLOT_ALPHA,
    scheme=SCHEME,
    k=10,
    edgecolor=EDGECOLOR,
    linewidth=LINEWIDTH,
    ax=ax,
)


bins = Quantiles(gdf_device.query("devices==devices").devices, k=10).bins
hax = legendgram(
    plt.gcf(),
    ax,
    gdf_device.devices,
    bins,  # the breaks to induce color differences on
    pal=mplpal.Viridis_10_r,  # the palette to use,
    legend_size=(
        0.35,
        0.2,
    ),  # the size of the subplot, in fractions of the original axis
    loc="lower right",  # the location on the axis
    clip=(0, 800000),  # bounds to clip the view of the histogram
)

# Add basemap
cx.add_basemap(
    crs=gdf_device.crs,
    source=basemap,
    attribution="",
    alpha=BASEMAP_ALPHA,
    zoom=12,
    ax=ax,
    zorder=0,
)

# plt.tight_layout()\
ax.set_xlim(xlim)
ax.set_ylim(ylim)
add_north_arrow(ax=ax, x=103.99, y=1.44, fontsize=30)
add_scalebar(ax=ax, location="lower left", fontsize=20)
plt.axis("off")
ax.axis("off")
ylim = ax.get_ylim()
xlim = ax.get_xlim()
save_mpl_fig("../results/figures/supplementary/choropleth-devices-legend")

# %%
