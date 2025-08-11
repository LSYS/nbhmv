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
# import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.cm as cm

import warnings

warnings.filterwarnings("ignore")
# FP_REALIS = os.path.join(
#     "..", "build", "preprocessed-data", "realis_with_postal_code_complete.csv.gz"
# )
# FP_HDBRESALE = os.path.join(
#     "..", "build", "preprocessed-data", "hdb_saledata_with_geodata.csv.gz"
# )

FP_INC = "input/resident-working-persons-aged-15-years-over-by-planning-area-gross-monthly-income-from-work-2015/resident-working-persons-aged-15-yrs-over-by-pa-gross-monthly-income-from-work.csv"
FP_REALIS = "input/realis_with_postal_code_complete.csv.gz"
FP_HDBRESALE = "input/hdb_saledata_with_geodata.csv.gz"
FP_PA_SHP2014 = "input/master-plan-2014-planning-area-boundary-no-sea/master-plan-2014-planning-area-boundary-no-sea-kml.zip"
from utilities import add_north_arrow, add_scalebar, save_mpl_fig, cat_to_num

# %% [markdown]
# ## Prep files

# %% [markdown]
# ### PA

# %%
# FP_PA_SHP2014 = os.path.join(
#     "zip://",
#     "..",
#     "build",
#     "raw-data",
#     "master-plan-2014-planning-area-boundary-no-sea",
#     "master-plan-2014-planning-area-boundary-no-sea-kml.zip",
# )

gdf_pa = gpd.read_file(FP_PA_SHP2014).assign(
    planning_area=lambda df: df.Name.str.lower()
)

# %% [markdown]
# ### House prices

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
)

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONGITUDE, df.LATITUDE))

gdf.crs = gdf_pa.crs

gdf.head(3)

# %% [markdown]
# ### Income

# %%
df_inc = (
    pd.read_csv(FP_INC, usecols=["level_1", "level_3", "value"])
    .rename(columns={"level_1": "income", "level_3": "planning_area", "value": "count"})
    .query('income!= "Total"')
    .assign(planning_area=lambda df: df["planning_area"].str.lower())
)
df_inc.head(3)

income_cats = df_inc["income"].unique().tolist()

# Convert cat to median values
df_inc["income"] = df_inc["income"].map(
    cat_to_num(income_cats, **{"Below $1,000": 500})
)

# Get total inc = income * count
df_inc["income"] = df_inc["income"] * df_inc["count"]

# Groupby area and sum
df_inc = df_inc.groupby(["planning_area"])["income"].sum().reset_index()
df_inc.head(3)

# Merge to get per working pop. income
df_inc = df_inc.merge(
    (
        pd.read_csv(FP_INC, usecols=["level_1", "level_3", "value"])
        .rename(
            columns={
                "level_1": "income",
                "level_3": "planning_area",
                "value": "workpop",
            }
        )
        .query('income!= "Total"')
        .assign(planning_area=lambda df: df["planning_area"].str.lower())
        .groupby("planning_area")["workpop"]
        .sum()
        .reset_index()
    ),
    how="left",
    on="planning_area",
    validate="1:1",
).assign(income=lambda df: df.income / df.workpop)

df_inc.head(3)

gdf_inc = gdf_pa.merge(df_inc, how="left", on="planning_area", validate="1:1").assign(
    centroid=lambda df: df.geometry.centroid
)
gdf_inc.head(3)

# %% code_folding=[1]
# Retain only planning areas with transaction data
gdf_inc = (
    gpd.sjoin(gdf_inc, gdf, how="left", predicate="contains")
    .drop_duplicates(subset="planning_area", keep="first")
    # Manually drop the Changi area
    .query('planning_area!="changi"')
    .dropna(subset=["psm"])
)
gdf_inc.head(3)

# %%
# GRAPH SETTINGS
LINEWIDTH = 0.7
EDGECOLOR = "white"

REGION_LINEWIDTH = 1.5
REGION_EDGECOLOR = "gray"
REGION_COLOR = "none"

CMAP = "Reds"
DWELL_CMAP = "Blues"
MISS_COLOR = "whitesmoke"
MISS_EDGECOLOR = "darkgray"
HATCHES = "+"

MISSKWDS = {
    "color": "dimgray",
    "edgecolor": "white",
    "hatch": "+",
    "label": "Missing values",
}

ANNOTE_SIZE = 12

# for square markers in legend
plt.rcParams["legend.handlelength"] = 0.4
plt.rcParams["legend.handleheight"] = 1.5

DPI = 150

# %%
gdf_pa["planning_area"] = gdf_pa.Name.str.title()
gdf_pa["centroid"] = gdf_pa["geometry"].centroid

# %% code_folding=[0]
# # Plot (old)
# _, ax = plt.subplots(figsize=(10, 10))
# gdf_inc.plot(column='income', categorical=True, legend=False,
#                linewidth=LINEWIDTH, edgecolor=EDGECOLOR,
#                cmap='Reds',
#                alpha=.9,
#                missing_kwds=MISSKWDS,
#                ax=ax
#               )

# for pa, lat, long in zip(gdf_pa['planning_area'], gdf_pa['centroid'].x, gdf_pa['centroid'].y):
# #     if pa=='Bishan':
# #         plt.annotate(pa, xy=(lat, long), xytext=(lat+.06, long+.1),
# #              arrowprops=dict(arrowstyle= '->', lw=1), size=ANNOTE_SIZE)
# #     if pa=='Serangoon':
# #         plt.annotate(pa, xy=(lat, long), xytext=(lat+.07, long+.07),
# #              arrowprops=dict(arrowstyle= '->', lw=1), size=ANNOTE_SIZE)
# #     if pa=='Outram':
# #         plt.annotate(pa, xy=(lat, long), xytext=(lat+.05, long-.02),
# #              arrowprops=dict(arrowstyle= '->', lw=1), size=ANNOTE_SIZE)
# #     if pa=='Tanglin':
# #         plt.annotate(pa, xy=(lat, long), xytext=(lat+.05, long-.08),
# #              arrowprops=dict(arrowstyle= '->', lw=1), size=ANNOTE_SIZE)
# #     if pa=='Bukit Timah':
# #         plt.annotate(pa, xy=(lat, long), xytext=(lat-.1, long-.1),
# #              arrowprops=dict(arrowstyle= '->', lw=1), size=ANNOTE_SIZE)
#     if pa=='Central Water Catchment':
#         plt.annotate('Central\nWater\nCatchment', xy=(lat, long), xytext=(lat, long), fontweight='bold',
#                      size=ANNOTE_SIZE, horizontalalignment='center', verticalalignment='center')
#     if pa=='Western Water Catchment':
#         plt.annotate('Western\nWater\nCatchment', xy=(lat, long), xytext=(lat+.013, long), fontweight='bold',
#                      size=ANNOTE_SIZE, horizontalalignment='center', verticalalignment='center')
#     if pa=='Paya Lebar':
#         plt.annotate('Paya\nLebar\n Air Base', xy=(lat, long), xytext=(lat+.00, long), fontweight='bold',
#                      size=ANNOTE_SIZE, horizontalalignment='center', verticalalignment='center')
# add_north_arrow(ax=ax, x=103.99, y=1.46, fontsize=30)
# add_scalebar(ax=ax, fontsize=20)
# plt.axis('off')
# plt.tight_layout()
# plt.margins(0,0)

# %%
# plot
_, ax = plt.subplots(figsize=(10, 10))

gdf_inc.plot(
    column="income",
    scheme="quantiles",
    k=5,
    legend=False,
    linewidth=LINEWIDTH,
    edgecolor=EDGECOLOR,
    cmap="Reds",
    alpha=0.9,
    missing_kwds=MISSKWDS,
    ax=ax,
)

# Annotate
for pa, lat, long in zip(
    gdf_pa["planning_area"], gdf_pa["centroid"].x, gdf_pa["centroid"].y
):
    if pa == "Central Water Catchment":
        plt.annotate(
            "Central\nWater\nCatchment",
            xy=(lat, long),
            xytext=(lat, long),
            fontweight="bold",
            size=ANNOTE_SIZE,
            horizontalalignment="center",
            verticalalignment="center",
        )
    if pa == "Western Water Catchment":
        plt.annotate(
            "Western\nWater\nCatchment",
            xy=(lat, long),
            xytext=(lat + 0.013, long),
            fontweight="bold",
            size=ANNOTE_SIZE,
            horizontalalignment="center",
            verticalalignment="center",
        )
    if pa == "Paya Lebar":
        plt.annotate(
            "Paya\nLebar\n Air Base",
            xy=(lat, long),
            xytext=(lat - 0.001, long),
            fontweight="bold",
            size=ANNOTE_SIZE,
            horizontalalignment="center",
            verticalalignment="center",
        )

# Create income bins
income_values = gdf_inc["income"].dropna()
quantiles = [0, 0.25, 0.5, 0.75, 1.0]
breaks = np.quantile(income_values, quantiles)

# Get colors for the ranges
cmap = cm.get_cmap("Reds")
colors = [cmap(i / 4) for i in range(4)]

# Format income ranges


def format_income(value):
    return f"${value/1000:.1f}k"


# Compose legend
legend_elements = []
for i in range(len(breaks) - 1):
    if i == 0:
        label = f"< \${format_income(breaks[i+1])}"
    else:
        label = f"\${format_income(breaks[i])} - \${format_income(breaks[i+1])}"

    # Create rectangular patch for horizontal bar appearance
    legend_elements.append(
        mpatches.Rectangle(
            (0, 0),
            1,
            1,
            facecolor=colors[i],
            edgecolor="black",
            linewidth=0.5,
            label=label,
        )
    )

# Add element for missing data
legend_elements.append(
    mpatches.Rectangle(
        (0, 0),
        1,
        1,
        facecolor="gray",
        hatch="+++",
        edgecolor="white",
        linewidth=0.1,
        label="No data",
    )
)

# Create the legend with horizontal bars
legend = ax.legend(
    handles=legend_elements,
    title="Monthly Income (SGD)",
    title_fontsize=14,
    fontsize=14,
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
    handlelength=2,
    handleheight=1,
    handletextpad=0.5,
    labelspacing=0.3,
)

legend.get_title().set_fontweight("bold")
legend.get_frame().set_linewidth(1.5)
for text in legend.get_texts():
    text.set_color(".3")

add_north_arrow(ax=ax, x=103.99, y=1.46, fontsize=30)
add_scalebar(ax=ax, fontsize=20)
ax.set_ylim(1.235, 1.470774832084755)
plt.axis("off")
plt.tight_layout()
plt.margins(0, 0)
save_mpl_fig("../results/figures/supplementary/choropleth-income")

# %%
