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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import geopandas as gpd
import numpy as np
import janitor

janitor

pd.set_option("display.max_columns", 100)
pd.set_option("display.max_rows", 500)
import warnings

warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mapclassify import Quantiles

from utilities import add_segmented_scalebar, add_north_arrow, save_mpl_fig


FP_SUBZONE_SHP2014 = "input/master-plan-2014-subzone-boundary-no-sea/master-plan-2014-subzone-boundary-no-sea-shp.zip"
FP_CITYDATA_SUBZONES = "input/citydata-subzones.csv"
FP_HTYPE = "input/htype.csv"
FP_PRICE = "input/propprice-subzone.csv"
FP_MOVEMENT = "input/daily-movecount.csv.gz"
SAVEPATH = "../results/figures/supplementary/"

# %% [markdown]
# ## Prep tables

# %% [markdown]
# ### Shp

# %% code_folding=[]
# Read in URA2014 version
subzones2014 = (
    gpd.read_file(FP_SUBZONE_SHP2014)
    .rename(columns={"SUBZONE_N": "subzone"})
    .assign(subzone=lambda df: df["subzone"].str.lower())
    .to_crs("EPSG:4326")
    .assign(centroid=lambda df: df["geometry"].centroid)
)

# %% [markdown]
# ### Prices

# %%
df_price = (
    pd.read_csv(FP_PRICE)
    .rename_column("area", "subzone")
    .merge(
        (pd.read_csv(FP_HTYPE).rename_column("area", "subzone")),
        how="outer",
        on="subzone",
        validate="1:1",
    )
    .assign(
        wpsm_public=lambda df_: (100 - df_["private"]) / 100 * df_["public_psm"],
        wpsm_private=lambda df_: (df_["private"] / 100) * df_["private_psm"],
        wpsm=lambda df_: df_[["wpsm_public", "wpsm_private"]].sum(axis=1, skipna=True),
    )
    # 0 to nan
    .assign(
        wpsm=lambda x: x["wpsm"].replace(0, np.nan),
        resident_count=lambda x: x["resident_count"].replace(0, np.nan),
    )
    .assign(
        wpsm=lambda df_: df_["wpsm"].fillna(
            (
                (
                    df_["public_num_transactions"].fillna(0)
                    * df_["public_psm"].fillna(0)
                    + df_["private_num_transactions"].fillna(0) * df_["private_psm"]
                ).fillna(0)
                / (
                    df_["public_num_transactions"].fillna(0)
                    + df_["private_num_transactions"].fillna(0)
                )
            )
        )
    )
)
df_price

# %%
(
    df_price.query("resident_count!=resident_count").query(
        "public_psm==public_psm | private_psm==private_psm"
    )
    #     .query("wpsm!=wpsm")
)

# %%
gdf_price = subzones2014[["subzone", "geometry", "PLN_AREA_N", "REGION_C"]].merge(
    df_price, how="right", on="subzone", validate="1:1"
)

gdf_sz_cr = gdf_price[gdf_price["REGION_C"] == "CR"]
gdf_sz_cr

# %%
# Drop zones/subzones to shrink map
# https://www.citypopulation.de/en/singapore/admin/

subzones_to_drop = [
    "north-eastern islands",
    "sudong",
    "semakau",
    "jurong island and bukom",
    "southern group",
    "tuas bay",
    "tuas north",
    "tuas view",
    "tuas view extension",
    "tuas promenade",
    "changi airport",
    "changi bay",
    "tengeh",
    "western water catchment",
    "lim chu kang",
    "reservoir view",
    "gul circle",
    "pioneer sector",
    "safti",
    "joo koon",
    "gul basin",
    "benoi sector",
    "samulun",
    "senoko north",
    "the wharves",
    "kranji",
    "pang sua",
    "tanjong irau",
    "pulau seletar",
]
gdf_sz_cr = gdf_sz_cr[~gdf_sz_cr["subzone"].isin(subzones_to_drop)]

# zones_to_drop = ['SOUTHERN ISLANDS', 'NORTH-EASTERN ISLANDS', 'WESTERN ISLANDS']
# zones2014 = zones2014[~zones2014['PLN_AREA_N'].isin(zones_to_drop)]

# %% [markdown]
# ### Flows

# %%
# Clean obvious name errors from Citydata (to get perfect match)
clean_cd_subzone = {
    "marina east mp": "marina east (mp)",
    "monks hill": "monk's hill",
    "national university of s pore": "national university of s'pore",
    "peoples park": "people's park",
}

# %%
# Read in citydata subzones
cd_subzones = (
    pd.read_csv(FP_CITYDATA_SUBZONES)
    .assign(subzone=lambda df: df["subzone"].str.lower())
    .assign(subzone=lambda df: df["subzone"].replace(clean_cd_subzone))
)

# Merge with URA shp
cd_subzones = cd_subzones.merge(
    subzones2014[["subzone", "geometry"]], how="left", on="subzone", indicator=True
)

assert len(cd_subzones[cd_subzones["_merge"] == "left_only"]) == 0

subzones_dict = dict(zip(cd_subzones["areaid"], cd_subzones["subzone"]))

cd_subzones.head(3)

# %%
# Read in movement matrix for weekdays and map area xid back to citydata subzone name
move = (
    pd.read_csv(FP_MOVEMENT, compression="gzip")
    .assign(date=lambda df: pd.to_datetime(df["date"]))
    #         .assign(dow=lambda df: [ts.isoweekday() for ts in df['date']])
    #         .query('dow<6')
    #         #         .drop('date', axis=1)
    .groupby(["home", "area_id"])["inflow_count"]
    .sum()
    .reset_index()
    .assign(source=lambda df: df["home"].map(subzones_dict))
    .assign(dest=lambda df: df["area_id"].map(subzones_dict))
    .assign(source=lambda df: df["source"].str.lower())
    .assign(dest=lambda df: df["dest"].str.lower())
    .assign(source=lambda df: df["source"].replace(clean_cd_subzone))
    .assign(dest=lambda df: df["dest"].replace(clean_cd_subzone))
)

# Merge with URA shp
move = (
    move.merge(
        subzones2014[["subzone", "centroid"]],
        how="left",
        left_on="source",
        right_on="subzone",
    )
    .assign(slong=lambda df: [pt.coords[0][0] for pt in df["centroid"]])
    .assign(slat=lambda df: [pt.coords[0][1] for pt in df["centroid"]])
    .drop("centroid", axis=1)
)

move = (
    move.merge(
        subzones2014[["subzone", "centroid"]],
        how="left",
        left_on="dest",
        right_on="subzone",
    )
    .assign(dlong=lambda df: [pt.coords[0][0] for pt in df["centroid"]])
    .assign(dlat=lambda df: [pt.coords[0][1] for pt in df["centroid"]])
)

# Get total home for percentages
move = move.merge(
    move.groupby(["home"])["inflow_count"]
    .sum()
    .reset_index()
    .rename(columns={"inflow_count": "tt"}),
    how="left",
    on=["home"],
    validate="m:1",
)
move["flow"] = move["inflow_count"] / move["tt"] * 100

move.drop(
    ["subzone_x", "subzone_y", "centroid", "home", "area_id"], axis=1, inplace=True
)

move.head(3)

# %% [markdown]
# ## Plot

# %% [markdown]
# ### Preamble

# %%
# Graph settings
FIGSIZE = (10, 10)

AREA_LINEWIDTH = 1.5
EDGE_COLOR = "darkgray"

ZONE_LINEWIDTH = 3
ZONE_EDGECOLOR = "dimgray"

MOVE_COLOR = "black"
MOVE_LINE_ALPHA = 0.99
MOVE_LWIDTH_NORM = 100  # smaller = thicker

FLOW_CUTOFF = 1  # at least 1 percent flow

CM = "Oranges_r"
MISSKWDS = {
    "color": "black",
    "edgecolor": "white",
    "hatch": "///",
    "label": "Missing values",
}
SCALEBAR_OPTS = dict(
    height_fraction=.010,
    location="lower left",
    segments=[1, 1, 2, 2],
    unit_position="right",
    label_offset=0.005,
    unit_label_spacing=0.003,
    fontsize=10,
    unit_fontsize=11,
)

# %% [markdown]
# ### mount pleasant

# %% code_folding=[0]
# # Plot mount pleasant
# SELECTED_AREA = "mount pleasant"
# _, ax = plt.subplots(figsize=FIGSIZE)
# # =====================================================
# # Plot wpsm
# gdf_sz_cr.plot(
#     column="wpsm",
#     cmap="Oranges",
#     scheme="quantiles",
#     edgecolor=EDGE_COLOR,
#     linewidth=AREA_LINEWIDTH,
#     ax=ax,
#     zorder=2,
# )
# # =====================================================
# # Plot non-resid hatching
# gdf_sz_cr.query("resident_count!=resident_count").query("wpsm!=wpsm").plot(
#     column="resident_count",
#     alpha=0.5,
#     edgecolor=EDGE_COLOR,
#     missing_kwds=MISSKWDS,
#     ax=ax,
#     zorder=1,
# )

# # =====================================================
# # Highlight selected area border
# selected_gdf = gdf_sz_cr[gdf_sz_cr["subzone"] == SELECTED_AREA]
# selected_gdf.boundary.plot(ax=ax, color="#000080", linewidth=7, zorder=5, alpha=0.7)

# selected_gdf = gdf_sz_cr[gdf_sz_cr["subzone"] == "toa payoh central"]
# selected_gdf.boundary.plot(ax=ax, color="#008080", linewidth=6, zorder=5, alpha=0.7)

# # =====================================================
# # Plot movement lines
# for slat, dlat, slon, dlon, area, flow, base in zip(
#     move["slat"],
#     move["dlat"],
#     move["slong"],
#     move["dlong"],
#     move["source"],
#     move["flow"],
#     move["inflow_count"],
# ):
#     if area == SELECTED_AREA:
#         #         if (flow>FLOW_CUTOFF) & (base > BASE_FLOW_CUTOFF):
#         if flow > FLOW_CUTOFF:
#             plt.plot(
#                 [slon, dlon],
#                 [slat, dlat],
#                 linewidth=base / MOVE_LWIDTH_NORM,
#                 color="#000080",
#                 alpha=MOVE_LINE_ALPHA,
#                 zorder=4,
#                 linestyle=":",
#                 marker=">",
#             )

# # =====================================================
# # Get quantiles
# classifier = Quantiles(gdf_sz_cr["wpsm"], k=5)
# breaks = classifier.bins
# colors = [plt.cm.Oranges(i / 4) for i in range(5)]


# def format_price(price):
#     if price >= 1000:
#         return f"{price/1000:.1f}k"
#     else:
#         return f"{price:.0f}"


# # =====================================================
# # Compose legend
# legend_elements = []

# # Add quantile legend items
# for i, (color, break_val) in enumerate(zip(colors, breaks)):
#     if i == 0:
#         label = f"< \${format_price(break_val)}"
#     elif i == 4:
#         label = f"> \${format_price(breaks[i-1])}"
#     else:
#         label = f"\${format_price(breaks[i-1])} - \${format_price(break_val)}"
#     legend_elements.append(
#         mpatches.Patch(facecolor=color, edgecolor="black", linewidth=0.5, label=label)
#     )

# # Add non-residential areas to legend
# legend_elements.append(
#     mpatches.Patch(
#         facecolor=MISSKWDS.get("color", "lightgray"),
#         hatch=MISSKWDS.get("hatch", "/////"),
#         alpha=0.5,
#         edgecolor=MISSKWDS.get("facecolor", "lightgray"),
#         linewidth=0.5,
#         label="Non-residential",
#     )
# )

# legend = ax.legend(
#     handles=legend_elements,
#     title="Weighted price per\nsqm (SGD)",
#     title_fontsize=15,
#     fontsize=15,
#     loc="lower right",
#     bbox_to_anchor=(1.0, 0),
#     frameon=False,
#     shadow=False,
#     framealpha=0.95,
#     edgecolor="#333333",
#     facecolor="white",
#     borderpad=0,
#     columnspacing=1,
#     labelspacing=0.4,
#     handletextpad=0.5,
# )
# legend.get_title().set_fontweight("bold")
# legend._legend_box.align = "left"
# for text in legend.get_texts():
#     text.set_color(".2")
# # =====================================================
# # add_scalebar(ax=ax, location="upper right")
# add_north_arrow(ax=ax, x=103.915, y=1.36)
# add_segmented_scalebar(
#     ax,
#     location="lower left",
#     segments=[1, 1, 2, 2],
#     unit_position="right",
#     label_offset=0.005,
#     unit_label_spacing=0.003,
#     fontsize=10,
#     unit_fontsize=11,
# )
# plt.tight_layout()
# plt.margins(0, 0)
# plt.axis("off")
# save_mpl_fig(f"{SAVEPATH}/outflow-{'_'.join(SELECTED_AREA.split(' '))}-wpsm")

# %% [markdown]
# ### Malcolm

# %% code_folding=[]
# Plot mount pleasant
SELECTED_AREA = "malcolm"
_, ax = plt.subplots(figsize=FIGSIZE)
# =====================================================
# Plot wpsm
gdf_sz_cr.plot(
    column="wpsm",
    cmap="Oranges",
    scheme="quantiles",
    edgecolor=EDGE_COLOR,
    linewidth=AREA_LINEWIDTH,
    ax=ax,
    zorder=2,
)
# =====================================================
# Plot non-resid hatching
gdf_sz_cr.query("resident_count!=resident_count").query("wpsm!=wpsm").plot(
    column="resident_count",
    alpha=0.5,
    edgecolor=EDGE_COLOR,
    missing_kwds=MISSKWDS,
    ax=ax,
    zorder=1,
)

# =====================================================
# Highlight selected area border
selected_gdf = gdf_sz_cr[gdf_sz_cr["subzone"] == SELECTED_AREA]
selected_gdf.boundary.plot(ax=ax, color="#000080", linewidth=7, zorder=5, alpha=0.7)

selected_gdf = gdf_sz_cr[gdf_sz_cr["subzone"] == "toa payoh central"]
selected_gdf.boundary.plot(ax=ax, color="#008080", linewidth=6, zorder=5, alpha=0.7)

# =====================================================
# Plot movement lines
for slat, dlat, slon, dlon, area, flow, base in zip(
    move["slat"],
    move["dlat"],
    move["slong"],
    move["dlong"],
    move["source"],
    move["flow"],
    move["inflow_count"],
):
    if area == SELECTED_AREA:
        #         if (flow>FLOW_CUTOFF) & (base > BASE_FLOW_CUTOFF):
        if flow > FLOW_CUTOFF:
            plt.plot(
                [slon, dlon],
                [slat, dlat],
                linewidth=base / MOVE_LWIDTH_NORM,
                color="#000080",
                alpha=MOVE_LINE_ALPHA,
                zorder=4,
                linestyle=":",
                marker=">",
            )

# =====================================================
# add_scalebar(ax=ax, location="upper right")
add_north_arrow(ax=ax, x=103.915, y=1.36)
add_segmented_scalebar(
    ax,
    **SCALEBAR_OPTS,
)
plt.tight_layout()
plt.margins(0, 0)
plt.axis("off")
save_mpl_fig(f"{SAVEPATH}/outflow-{'_'.join(SELECTED_AREA.split(' '))}-wpsm")

# %% [markdown]
# ### toa payoh central

# %%
import matplotlib

# %%
matplotlib.__version__

# %% code_folding=[]
# Plot toa payoh central
SELECTED_AREA = "toa payoh central"

_, ax = plt.subplots(figsize=FIGSIZE)

# =====================================================
# Plot wpsm
gdf_sz_cr.plot(
    column="wpsm",
    cmap="Oranges",
    scheme="quantiles",
    edgecolor=EDGE_COLOR,
    linewidth=AREA_LINEWIDTH,
    ax=ax,
    zorder=2,
)

# =====================================================
# Plot non-resid
gdf_sz_cr.query("resident_count!=resident_count").query("wpsm!=wpsm").plot(
    column="resident_count",
    alpha=0.5,
    edgecolor=EDGE_COLOR,
    missing_kwds=MISSKWDS,
    ax=ax,
    zorder=1,
)

# =====================================================
# Highlight selected area border
selected_gdf = gdf_sz_cr[gdf_sz_cr["subzone"] == "malcolm"]
selected_gdf.boundary.plot(ax=ax, color="#000080", linewidth=7, zorder=5, alpha=0.7)

selected_gdf = gdf_sz_cr[gdf_sz_cr["subzone"] == SELECTED_AREA]
selected_gdf.boundary.plot(ax=ax, color="#008080", linewidth=6, zorder=5, alpha=0.7)

# =====================================================
# Plot movement lines
for slat, dlat, slon, dlon, area, flow, base in zip(
    move["slat"],
    move["dlat"],
    move["slong"],
    move["dlong"],
    move["source"],
    move["flow"],
    move["inflow_count"],
):
    if area == SELECTED_AREA:
        #         if (flow>FLOW_CUTOFF) & (base > BASE_FLOW_CUTOFF):
        if flow > FLOW_CUTOFF:
            plt.plot(
                [slon, dlon],
                [slat, dlat],
                linewidth=base / (MOVE_LWIDTH_NORM * 5),
                color="#008080",
                alpha=MOVE_LINE_ALPHA,
                zorder=4,
                linestyle=":",
                marker=">",
            )

# =====================================================
# Get quantiles
classifier = Quantiles(gdf_sz_cr["wpsm"], k=5)
breaks = classifier.bins
colors = [plt.cm.Oranges(i / 4) for i in range(5)]


def format_price(price):
    if price >= 1000:
        return f"{price/1000:.1f}k"
    else:
        return f"{price:.0f}"


# =====================================================
# Compose legend
legend_elements = []

# Add quantile legend items
for i, (color, break_val) in enumerate(zip(colors, breaks)):
    if i == 0:
        label = f"< \${format_price(break_val)}"
    elif i == 4:
        label = f"> \${format_price(breaks[i-1])}"
    else:
        label = f"\${format_price(breaks[i-1])} - \${format_price(break_val)}"
    legend_elements.append(
        mpatches.Patch(facecolor=color, edgecolor="black", linewidth=0.5, label=label)
    )

# Add non-residential areas to legend
legend_elements.append(
    mpatches.Patch(
        facecolor=MISSKWDS.get("color", "lightgray"),
        hatch="//////",
        alpha=0.5,
        edgecolor=MISSKWDS.get("facecolor", "lightgray"),
        linewidth=0.5,
        label="Non-residential",
    )
)

legend = ax.legend(
    handles=legend_elements,
    title="Weighted price per\nsqm (SGD)",
    title_fontsize=15,
    fontsize=15,
    loc="lower right",
    bbox_to_anchor=(1.0, 0),
    frameon=False,
    shadow=False,
    framealpha=0.95,
    edgecolor="#333333",
    facecolor="white",
    borderpad=0,
    columnspacing=1,
    labelspacing=0.4,
    handletextpad=0.5,
)
legend.get_title().set_fontweight("bold")
legend._legend_box.align = "left"
for text in legend.get_texts():
    text.set_color(".2")
    
# =====================================================
# add_scalebar(ax=ax, location="upper right")
add_north_arrow(ax=ax, x=103.915, y=1.36)
add_segmented_scalebar(
    ax,
    **SCALEBAR_OPTS,
)
plt.tight_layout()
plt.margins(0, 0)
plt.axis("off")
save_mpl_fig(f"{SAVEPATH}/outflow-{'_'.join(SELECTED_AREA.split(' '))}-wpsm")

# %%
