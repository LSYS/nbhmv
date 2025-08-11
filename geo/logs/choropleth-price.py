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
import pandas as pd
import geopandas as gpd
import fiona

fiona.drvsupport.supported_drivers["KML"] = "rw"
import matplotlib.pyplot as plt

# FP_SUBZONE_SHP2014 = os.path.join(
#     "zip://",
#     "..",
#     "build",
#     "raw-data",
#     "master-plan-2014-subzone-boundary-no-sea",
#     "master-plan-2014-subzone-boundary-no-sea-kml.zip",
# )
# FP_PA_SHP2014 = os.path.join(
#     "zip://",
#     "..",
#     "build",
#     "raw-data",
#     "master-plan-2014-planning-area-boundary-no-sea",
#     "master-plan-2014-planning-area-boundary-no-sea-kml.zip",
# )


# FP_REALIS = os.path.join(
#     "..", "build", "preprocessed-data", "realis_with_postal_code_complete.csv.gz"
# )
# FP_HDBRESALE = os.path.join(
#     "..", "build", "preprocessed-data", "hdb_saledata_with_geodata.csv.gz"
# )
FP_PA_SHP2014 = "input/master-plan-2014-planning-area-boundary-no-sea/master-plan-2014-planning-area-boundary-no-sea-kml.zip"
FP_SUBZONE_SHP2014 = "input/master-plan-2014-subzone-boundary-no-sea/master-plan-2014-subzone-boundary-no-sea-kml.zip"
FP_REALIS = "input/realis_with_postal_code_complete.csv.gz"
FP_HDBRESALE = "input/hdb_saledata_with_geodata.csv.gz"
import warnings

warnings.filterwarnings("ignore")
from utilities import custom_cmap, add_north_arrow, add_scalebar, save_mpl_fig

from mapclassify import Quantiles

import matplotlib.patches as mpatches

# %%
# Read in shape files
gdf_subzone = gpd.read_file(FP_SUBZONE_SHP2014)
gdf_pa = gpd.read_file(FP_PA_SHP2014).assign(
    planning_area=lambda df: df.Name.str.lower()
)

assert gdf_subzone.crs == gdf_pa.crs

# %%
YEARS = [2017, 2018, 2019]  # 3 years before sample year of 2020

df = (
    pd.concat(
        [
            (
                pd.read_csv(
                    FP_REALIS,
                    compression="gzip",
                    usecols=["unitpricepsm", "contractdate", "LATITUDE", "LONGITUDE"],
                    low_memory=False,
                )
                .rename(columns={"unitpricepsm": "psm"})
                # retain only transactions in 2017 to 2019
                .assign(
                    year=lambda df: df["contractdate"].str.slice(stop=4).astype(int)
                )
                .query("year in @YEARS")
                .drop(["contractdate", "year"], axis=1)
            ),
            (
                pd.read_csv(
                    FP_HDBRESALE,
                    compression="gzip",
                    usecols=["psm", "month", "LATITUDE", "LONGITUDE"],
                )
                # retain only transactions in 2017 to 2019
                .assign(year=lambda df: df["month"].str.slice(stop=4).astype(int))
                .query("year in @YEARS")
                .drop(["month", "year"], axis=1)
            ),
        ],
        ignore_index=True,
    )
    # Remove comma from valuations (e.g. 17,493)
    .assign(
        psm=lambda df: df["psm"].astype("string").str.replace(",", "").astype("float")
    ).astype({"psm": "float"})
    #       .groupby(['LATITUDE', 'LONGITUDE'])['psm'].mean().reset_index()
)

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONGITUDE, df.LATITUDE))

gdf.crs = gdf_pa.crs

gdf.head(3)

# %%
# Retain only planning areas with transaction data
gdf_pa_subset = (
    gpd.sjoin(gdf_pa, gdf, how="inner", predicate="contains").drop_duplicates(
        subset="planning_area", keep="first"
    )
    # Manually drop the Changi area
    .query('planning_area!="changi"')
)

gdf_subzone_subset = (
    gpd.sjoin(
        gdf_subzone,
        gdf_pa_subset.drop("index_right", axis=1),
        how="inner",
        predicate="intersects",
    ).drop_duplicates(subset="planning_area", keep="first")
    #                       # Manually drop the Changi area
    #                       .query('planning_area!="changi"')
)

# %%
# # Plot house price (OLD VERSION)
# fig, ax = plt.subplots(figsize=(14,14))

# gdf.plot('psm', markersize=.005,
#          cmap='PuRd',  legend=False,
#          scheme='quantiles',
#          zorder=3,
#          ax=ax)

# # Plot planning area borders
# gdf_pa_subset.boundary.plot(edgecolor='black', linewidth=.5,
#                             alpha=.5,
#                             zorder=0,
#                             ax=ax)

# add_north_arrow(ax=ax, x=103.99, y=1.46, fontsize=30)
# add_scalebar(ax=ax, fontsize=20)
# plt.axis('off')
# plt.tight_layout()
# plt.margins(0,0)

# %%
# plot
_, ax = plt.subplots(figsize=(16, 16))
gdf.plot(
    "psm",
    markersize=0.005,
    cmap=custom_cmap,
    legend=False,
    scheme="quantiles",
    k=5,
    zorder=3,
    ax=ax,
)
gdf_pa_subset.boundary.plot(
    edgecolor="black", linewidth=0.5, alpha=0.5, zorder=0, ax=ax
)

# Get quantiles
classifier = Quantiles(gdf["psm"], k=5)
breaks = classifier.bins
colors = [custom_cmap(i / 4) for i in range(5)]


def format_price(price):
    if price >= 1000:
        return f"{price/1000:.1f}k"
    else:
        return f"{price:.0f}"


# Compose legend
legend_elements = []
for i, (color, break_val) in enumerate(zip(colors, breaks)):
    if i == 0:
        label = f"< \${format_price(break_val)}"
    else:
        label = f"\${format_price(breaks[i-1])} - \${format_price(break_val)}"

    legend_elements.append(
        mpatches.Patch(facecolor=color, edgecolor="black", linewidth=0.5, label=label)
    )

legend = ax.legend(
    handles=legend_elements,
    title="Price per sqm (SGD)",
    title_fontsize=19,
    fontsize=19,
    loc="upper left",
    bbox_to_anchor=(0.0, 1),
    frameon=True,
    fancybox=False,
    shadow=False,
    framealpha=0.95,
    edgecolor="#333333",
    facecolor="white",
    borderpad=1,
    columnspacing=1,
    handletextpad=0.5,
)

legend.get_title().set_fontweight("bold")
legend.get_frame().set_linewidth(1.5)
for text in legend.get_texts():
    text.set_color(".3")

ax.set_ylim(1.235, 1.470774832084755)
add_north_arrow(ax=ax, x=103.99, y=1.46, fontsize=30)
add_scalebar(ax=ax, fontsize=20)
plt.tight_layout()
plt.axis("off")
save_mpl_fig("../results/figures/supplementary/choropleth-price")

# %%
