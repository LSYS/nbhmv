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
import numpy as np
import warnings

warnings.filterwarnings("ignore")
import janitor

janitor

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(context="notebook", font_scale=1.25, style="white", palette="PRGn")

import scipy.stats
import matplotlib as mpl
import matplotlib.patches as mpl_patches
import ptitprince as pt

FILEPATH = "input/cd-panel.csv"
SAVEPATH = "../results/figures/ping-variation/"

from utilities import save_mpl_fig, walk_through_files

# %%
xlabels = [
    "Bin 1",
    "Bin 2",
    "Bin 3",
    "Bin 4",
    "Bin 5",
    "Bin 6",
    "Bin 7",
    "Bin 8",
    "Bin 9",
    "Bin 10",
]
df = (
    pd.read_csv(FILEPATH)
    # Keep only those that have basics variables
    .query("age_20_o==age_20_o")
    .query("age20_40_o==age20_40_o")
    .query("age65__o==age65__o")
    .query("age_20_d==age_20_d")
    .query("age20_40_d==age20_40_d")
    .query("age65__d==age65__d")
    .query("females_o==females_o")
    .query("females_d==females_d")
    .query("chinese_o==chinese_o")
    .query("indians_o==indians_o")
    .query("malays_o==malays_o")
    .query("others_o==others_o")
    .query("resident_count_dest>0")
    .query("resident_count_home>0")
    .query("wpsm_dest==wpsm_dest")
    .query("wpsm_home==wpsm_home")
    .query("rain_home==rain_home")
    .query("rain_dest==rain_dest")
    .assign(
        # Calculate missing age groups first
        age40_65_o=lambda df: 100 - df.age_20_o - df.age20_40_o - df.age65__o,
        age40_65_d=lambda df: 100 - df.age_20_d - df.age20_40_d - df.age65__d,
        date=lambda df: pd.to_datetime(df.date),
        dow=lambda df: [dt_obj.isoweekday() for dt_obj in df.date],
        woy=lambda df: [dt_obj.weekofyear for dt_obj in df.date],
        mth=lambda df: [dt_obj.month for dt_obj in df.date],
        # popsize
        pop_home_10bin=lambda df: pd.cut(
            df.resident_count_home, bins=10, precision=1, labels=xlabels
        ),
        pop_dest_10bin=lambda df: pd.cut(
            df.resident_count_dest, bins=10, precision=1, labels=xlabels
        ),
        # age
        age_20_o_10bin=lambda df: pd.cut(df.age_20_o, bins=10, labels=xlabels),
        age20_40_o_10bin=lambda df: pd.cut(df.age20_40_o, bins=10, labels=xlabels),
        age40_65_o_10bin=lambda df: pd.cut(df.age40_65_o, bins=10, labels=xlabels),
        age65__o_10bin=lambda df: pd.cut(df.age65__o, bins=10, labels=xlabels),
        age_20_d_10bin=lambda df: pd.cut(df.age_20_d, bins=10, labels=xlabels),
        age20_40_d_10bin=lambda df: pd.cut(df.age20_40_d, bins=10, labels=xlabels),
        age40_65_d_10bin=lambda df: pd.cut(df.age40_65_d, bins=10, labels=xlabels),
        age65__d_10bin=lambda df: pd.cut(df.age65__d, bins=10, labels=xlabels),
        # gemder
        females_o_bin=lambda df: pd.cut(df.females_o, bins=10, labels=xlabels),
        females_d_bin=lambda df: pd.cut(df.females_d, bins=10, labels=xlabels),
        # ethnic
        chinese_o_bin=lambda df: pd.cut(df.chinese_o, bins=10, labels=xlabels),
        malays_o_bin=lambda df: pd.cut(df.malays_o, bins=10, labels=xlabels),
        indians_o_bin=lambda df: pd.cut(df.indians_o, bins=10, labels=xlabels),
        others_o_bin=lambda df: pd.cut(df.others_o, bins=10, labels=xlabels),
        chinese_d_bin=lambda df: pd.cut(df.chinese_o, bins=10, labels=xlabels),
        malays_d_bin=lambda df: pd.cut(df.malays_o, bins=10, labels=xlabels),
        indians_d_bin=lambda df: pd.cut(df.indians_o, bins=10, labels=xlabels),
        others_d_bin=lambda df: pd.cut(df.others_o, bins=10, labels=xlabels),
        # House type
        rm12_home_bin=lambda df: pd.cut(df.rm12_home, bins=10, labels=xlabels),
        rm3_home_bin=lambda df: pd.cut(df.rm3_home, bins=10, labels=xlabels),
        rm4_home_bin=lambda df: pd.cut(df.rm4_home, bins=10, labels=xlabels),
        rm5_home_bin=lambda df: pd.cut(df.rm5_home, bins=10, labels=xlabels),
        private_home_bin=lambda df: pd.cut(df.private_home, bins=10, labels=xlabels),
        rm12_dest_bin=lambda df: pd.cut(df.rm12_dest, bins=10, labels=xlabels),
        rm3_dest_bin=lambda df: pd.cut(df.rm3_dest, bins=10, labels=xlabels),
        rm4_dest_bin=lambda df: pd.cut(df.rm4_dest, bins=10, labels=xlabels),
        rm5_dest_bin=lambda df: pd.cut(df.rm5_dest, bins=10, labels=xlabels),
        private_dest_bin=lambda df: pd.cut(df.private_dest, bins=10, labels=xlabels),
        # Distance
        dist_10bin=lambda df: pd.cut(
            df.centroid_distance_epsg, bins=10, labels=xlabels
        ),
        distedge_10bin=lambda df: pd.cut(
            df.edge_distance_epsg, bins=10, labels=xlabels
        ),
        noncontiguous=lambda df: np.where(df.edge_distance_epsg == 0, 0, 1),
        linflow=lambda df: np.log(df.inflow),
        # House price
        wpsm_home_bin=lambda df: pd.cut(df.wpsm_home, bins=10, labels=xlabels),
        wpsm_dest_bin=lambda df: pd.cut(df.wpsm_dest, bins=10, labels=xlabels),
    )
)

df.head(3)

# %% [markdown]
# ## Variation by population size

# %%
# coefplot-home-pings-population
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="pop_home_10bin",
    y="basecount",
    data=df,
    ci="sd",
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")

LABSIZE = 16
plt.xlabel("Residential population", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-home-pings-population"))

# %%
# coefplot-dest-pings-population
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="pop_dest_10bin",
    y="dest_basecount",
    data=df,
    ci="sd",
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

LABSIZE = 16
plt.xlabel("Residential population", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-population"))

# %% [markdown]
# ## Variation by time

# %%
# coefplot-home-pings-woy
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

x = "woy"
y = "basecount"

sns.pointplot(
    x=x,
    y=y,
    data=df,
    ci="sd",
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    zorder=1,
    ax=ax,
)

# Draw joining lines in different colour
sns.pointplot(
    x=x,
    y=y,
    data=df,
    ci=None,
    capsize=None,
    markers="",
    join=True,
    linestyles="--",
    errwidth=2,  # error bar width
    scale=0.8,
    color="dimgray",
    zorder=0,
    ax=ax,
)

LABSIZE = 16
plt.xlabel("Week of the year", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
plt.locator_params(axis="y", nbins=4)
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-home-pings-woy"))

# %%
# coefplot-dest-pings-woy
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

x = "woy"
y = "dest_basecount"

sns.pointplot(
    x=x,
    y=y,
    data=df,
    ci="sd",
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    zorder=1,
    ax=ax,
)

# Draw joining lines in different colour
sns.pointplot(
    x=x,
    y=y,
    data=df,
    ci=None,
    capsize=None,
    markers="",
    join=True,
    linestyles="--",
    errwidth=2,  # error bar width
    scale=0.8,
    color="dimgray",
    zorder=0,
    ax=ax,
)

LABSIZE = 16
plt.xlabel("Week of the year", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
plt.locator_params(axis="y", nbins=4)
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-woy"))

# %%
# home-pings-dow
_df = df.groupby(["dow", "home"])["basecount"].mean().reset_index()

x = "basecount"
y = "dow"

_, ax = plt.subplots(figsize=(12 * 0.7, 8 * 0.7))

ax = pt.half_violinplot(
    x=x,
    y=y,
    data=_df,
    bw=0.2,
    cut=0,
    width=0.75,
    inner=None,
    color="lightslategray",
    alpha=0.7,
    orient="h",
    ax=ax,
)

ax = sns.stripplot(
    x=x,
    y=y,
    data=_df,
    edgecolor="black",
    size=2.5,
    jitter=1,
    color="dimgray",
    alpha=0.6,
    orient="h",
    zorder=0,
    ax=ax,
)

ax = sns.boxplot(
    x=x,
    y=y,
    data=_df,
    color="lightslategray",
    width=0.15,
    boxprops={"facecolor": "none", "zorder": 10},
    showfliers=False,
    whiskerprops={"linewidth": 2, "zorder": 10},
    zorder=10,
    orient="h",
    ax=ax,
)

ylabels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ax.set_yticklabels(ylabels)

LABSIZE = 13
plt.xlabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Day of the Week", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
sns.despine(left=True, bottom=True)
save_mpl_fig(os.path.join(SAVEPATH, "home-pings-dow"))

# %%
# dest-pings-dow
x = "dest_basecount"
y = "dow"

_df = df.groupby(["dow", "area"])[x].mean().reset_index()


_, ax = plt.subplots(figsize=(12 * 0.7, 8 * 0.7))

ax = pt.half_violinplot(
    x=x,
    y=y,
    data=_df,
    bw=0.2,
    cut=0,
    width=0.7,
    inner=None,
    color="lightslategray",
    alpha=0.7,
    orient="h",
    ax=ax,
)

ax = sns.stripplot(
    x=x,
    y=y,
    data=_df,
    edgecolor="black",
    size=2.5,
    jitter=1,
    color="dimgray",
    alpha=0.6,
    orient="h",
    zorder=0,
    ax=ax,
)

ax = sns.boxplot(
    x=x,
    y=y,
    data=_df,
    color="lightslategray",
    width=0.15,
    boxprops={"facecolor": "none", "zorder": 10},
    showfliers=False,
    whiskerprops={"linewidth": 2, "zorder": 10},
    zorder=10,
    orient="h",
    ax=ax,
)

ylabels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ax.set_yticklabels(ylabels)

LABSIZE = 13
plt.xlabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Day of the Week", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
sns.despine(left=True, bottom=True)
save_mpl_fig(os.path.join(SAVEPATH, "dest-pings-dow"))

# %%
# home-pings-mth
sns.set_theme(context="notebook", font_scale=1.05, style="whitegrid")

x = "mth"
y = "basecount"

_df = df.groupby(["mth", "home"])[y].mean().reset_index()


_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

ax = pt.half_violinplot(
    x=x,
    y=y,
    data=_df,
    bw=0.2,
    cut=0,
    width=1,
    inner=None,
    color="lightslategray",
    alpha=0.7,
    orient="v",
    ax=ax,
)

ax = sns.stripplot(
    x=x,
    y=y,
    data=_df,
    edgecolor="black",
    size=2.5,
    jitter=1,
    color="dimgray",
    alpha=0.6,
    orient="v",
    zorder=0,
    ax=ax,
)

ax = sns.boxplot(
    x=x,
    y=y,
    data=_df,
    color="lightslategray",
    width=0.15,
    boxprops={"facecolor": "none", "zorder": 10},
    showfliers=False,
    whiskerprops={"linewidth": 2, "zorder": 10},
    zorder=10,
    orient="v",
    ax=ax,
)

sns.pointplot(
    x=x,
    y=y,
    data=_df,
    orient="v",
    estimator=np.median,
    color="dimgray",
    linestyles="--",
    ax=ax,
)

ax.set_xticklabels(["Jan", "Feb", "Mar"], fontsize=14)

LABSIZE = 13
plt.xlabel("")
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)

plt.locator_params(axis="y", nbins=5)
plt.tight_layout()
sns.despine(left=True, bottom=True)
save_mpl_fig(os.path.join(SAVEPATH, "home-pings-mth"))

# %%
# dest-pings-mth
x = "mth"
y = "dest_basecount"

_df = df.groupby(["mth", "area"])[y].mean().reset_index()


_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

ax = pt.half_violinplot(
    x=x,
    y=y,
    data=_df,
    bw=0.2,
    cut=0,
    width=1,
    inner=None,
    color="lightslategray",
    alpha=0.7,
    orient="v",
    ax=ax,
)

ax = sns.stripplot(
    x=x,
    y=y,
    data=_df,
    edgecolor="black",
    size=2.5,
    jitter=1,
    color="dimgray",
    alpha=0.6,
    orient="v",
    zorder=0,
    ax=ax,
)

ax = sns.boxplot(
    x=x,
    y=y,
    data=_df,
    color="lightslategray",
    width=0.15,
    boxprops={"facecolor": "none", "zorder": 10},
    showfliers=False,
    whiskerprops={"linewidth": 2, "zorder": 10},
    zorder=10,
    orient="v",
    ax=ax,
)

sns.pointplot(
    x=x,
    y=y,
    data=_df,
    orient="v",
    estimator=np.median,
    color="dimgray",
    linestyles="--",
    ax=ax,
)

ax.set_xticklabels(["Jan", "Feb", "Mar"], fontsize=14)

LABSIZE = 13
plt.xlabel("")
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)

plt.locator_params(axis="y", nbins=5)
plt.tight_layout()
sns.despine(left=True, bottom=True)
save_mpl_fig(os.path.join(SAVEPATH, "dest-pings-mth"))

# %% [markdown]
# ## By Region

# %%
# coefplot-home-pings-region
sns.set_theme(
    context="notebook",
    font_scale=1.05,
    style="white",
)
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="region_o",
    y="basecount",
    data=df,
    ci="sd",
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.locator_params(axis="y", nbins=5)
ax.set_xticklabels(["North", "Central", "West", "East", "North-East"])

LABSIZE = 16
plt.xlabel("Region", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-home-pings-region"))

# %%
# coefplot-dest-pings-region
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="region_d",
    y="dest_basecount",
    data=df,
    ci="sd",
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.locator_params(axis="y", nbins=4)
ax.set_xticklabels(["North", "Central", "West", "East", "North-East"])

LABSIZE = 16
plt.xlabel("Region", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-region"))

# %% [markdown]
# ## By census demo

# %% [markdown]
# ### Age

# %%
# coefplot-origin-pings-age20
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="age_20_o_10bin",
    y="basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel("% Aged below 20", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-origin-pings-age20"))

# %%
# coefplot-origin-pings-age20to40
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="age20_40_o_10bin",
    y="basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel("% Aged 20 to 39", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-origin-pings-age20to40"))

# %%
# coefplot-origin-pings-age40to64
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="age40_65_o_10bin",
    y="basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel("% Aged 40 to 64", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-origin-pings-age40to65"))

# %%
# coefplot-origin-pings-age65
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="age65__o_10bin",
    y="basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel("% Aged 65 and above", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-origin-pings-age65"))

# %%
# coefplot-dest-pings-age20
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="age_20_d_10bin",
    y="dest_basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel("% Aged 20 and below", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-age20"))

# %%
# coefplot-dest-pings-age20to40
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="age20_40_d_10bin",
    y="dest_basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel("% Aged 20 to 40", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-age20to40"))

# %%
# coefplot-origin-dest-age40to64
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="age40_65_d_10bin",
    y="basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel("% Aged 40 to 64", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-age40to65"))

# %%
# coefplot-dest-pings-age65
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="age65__d_10bin",
    y="dest_basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel("% Aged 65 and above", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-age65"))

# %% [markdown]
# ### Gender

# %%
# coefplot-home-pings-female
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="females_o_bin",
    y="basecount",
    data=df,
    ci="sd",
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")

LABSIZE = 16
plt.xlabel("% Females", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-home-pings-female"))

# %%
# coefplot-dest-pings-female
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="females_d_bin",
    y="dest_basecount",
    data=df,
    ci="sd",
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")

LABSIZE = 16
plt.xlabel("% Females", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-female"))

# %% [markdown]
# ### Ethnic

# %%
# coefplot-pings-{race}
for race in ["chinese_o", "malays_o", "indians_o", "others_o"]:
    xvar = f"{race}_bin"
    print(xvar)

    _, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))
    sns.pointplot(
        x=xvar,
        y="basecount",
        data=df,
        ci="sd",
        n_boot=100,
        capsize=None,
        join=False,
        errwidth=2,  # error bar width
        scale=0.8,
        color="black",
        ax=ax,
    )

    plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
    plt.locator_params(axis="y", nbins=4)

    TICKSIZE = 15
    ax.tick_params(axis="both", labelsize=TICKSIZE)

    LABSIZE = 18
    if "chinese" in xvar:
        xlabel = "% Majority ethnic"
    elif "malay" in xvar:
        xlabel = "% Minority ethnic A"
    elif "indian" in xvar:
        xlabel = "% Minority ethnic B"
    elif "other" in xvar:
        xlabel = "% Minority ethnic C"
    plt.xlabel(xlabel, fontweight="bold", loc="center", size=LABSIZE)
    plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
    save_mpl_fig(os.path.join(SAVEPATH, f"coefplot-pings-{race}"))

# %% [markdown]
# ## Distance

# %% [markdown]
# ### Adjacent nbh flows

# %%
# linflow-nbh-adjacency
sns.set_theme(context="notebook", font_scale=1.05, style="whitegrid")

x = "noncontiguous"
y = "linflow"

_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

ax = pt.half_violinplot(
    x=x,
    y=y,
    data=df,
    bw=0.2,
    cut=0,
    width=0.6,
    inner=None,
    color="lightslategray",
    alpha=0.7,
    orient="v",
    ax=ax,
)

ax = sns.boxplot(
    x=x,
    y=y,
    data=df,
    color="lightslategray",
    width=0.15,
    boxprops={"facecolor": "none", "zorder": 10},
    showfliers=False,
    whiskerprops={"linewidth": 2, "zorder": 10},
    zorder=10,
    orient="v",
    ax=ax,
)

sns.pointplot(
    x=x,
    y=y,
    data=df,
    orient="v",
    estimator=np.median,
    color="dimgray",
    linestyles="--",
    ax=ax,
)

ax.set_xticklabels(["Adjacent\nneighbors", "Non-adjacent\nneighbors"], fontsize=14)

LABSIZE = 13
plt.xlabel("")
plt.ylabel("Log inflow", fontweight="bold", loc="center", size=LABSIZE)

plt.locator_params(axis="y", nbins=4)

sns.despine(left=True, bottom=True)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "linflow-nbh-adjacency"))

# %% [markdown]
# ### Continuous distance

# %%
# linflow-nbh-distance
_df = df.query("noncontiguous==1")
sns.set_theme(context="notebook", font_scale=1.05, style="white")

_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.lineplot(
    x="dist_10bin",
    y="linflow",
    data=_df,
    n_boot=10000,
    color="black",
    marker="o",
    ci=95,
    label="Centroid-based distance",
    ax=ax,
)

sns.lineplot(
    x="distedge_10bin",
    y="linflow",
    data=_df,
    n_boot=10000,
    color="gray",
    marker="X",
    ci=95,
    markers=True,
    label="Edge-based distance",
    zorder=0,
    ax=ax,
)

ax.lines[1].set_linestyle("--")

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")

LABSIZE = 16
plt.xlabel(
    "Distance between neighborhoods", fontweight="bold", loc="center", size=LABSIZE
)
plt.ylabel("Log inflow", fontweight="bold", loc="center", size=LABSIZE)

plt.locator_params(axis="y", nbins=4)

plt.legend(frameon=False)

sns.despine()
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "linflow-nbh-distance"))

# %% [markdown]
# ## Precipitation

# %%
# Prep data
# rain origin
df_rainorigin = (
    pd.read_csv(FILEPATH)
    # Keep only those that have basics variables
    .query("age_20_o==age_20_o")
    .query("age20_40_o==age20_40_o")
    .query("age65__o==age65__o")
    .query("age_20_d==age_20_d")
    .query("age20_40_d==age20_40_d")
    .query("age65__d==age65__d")
    .query("females_o==females_o")
    .query("females_d==females_d")
    .query("chinese_o==chinese_o")
    .query("indians_o==indians_o")
    .query("malays_o==malays_o")
    .query("others_o==others_o")
    .query("resident_count_dest>0")
    .query("resident_count_home>0")
    .query("wpsm_dest==wpsm_dest")
    .query("wpsm_home==wpsm_home")
    .query("rain_home==rain_home")
    .query("rain_dest==rain_dest")
    .groupby(["area", "date"])[["inflow", "rain_home"]]
    .mean()
    .reset_index()
    .assign(
        #               rain_home_10bin=lambda df: pd.cut(df.rain_home, bins=10),
        rain_home_10bin=lambda df: pd.cut(df.rain_home, bins=10, labels=xlabels),
        #               rain_dest_10bin=lambda df: pd.cut(df.rain_dest, bins=10, labels=[1,2,3,4,5,6,7,8,9,10]),
        #               rain_home_5bin=lambda df: pd.cut(df.rain_home, bins=5, labels=[1,2,3,4,5]),
        #               rain_dest_5bin=lambda df: pd.cut(df.rain_dest, bins=5, labels=[1,2,3,4,5]),
        linflow=lambda df: np.log(df.inflow),
    )
)

df_rainorigin.head(3)

# rain dest
df_raindest = (
    pd.read_csv(FILEPATH)
    # Keep only those that have basics variables
    .query("age_20_o==age_20_o")
    .query("age20_40_o==age20_40_o")
    .query("age65__o==age65__o")
    .query("age_20_d==age_20_d")
    .query("age20_40_d==age20_40_d")
    .query("age65__d==age65__d")
    .query("females_o==females_o")
    .query("females_d==females_d")
    .query("chinese_o==chinese_o")
    .query("indians_o==indians_o")
    .query("malays_o==malays_o")
    .query("others_o==others_o")
    .query("resident_count_dest>0")
    .query("resident_count_home>0")
    .query("wpsm_dest==wpsm_dest")
    .query("wpsm_home==wpsm_home")
    .query("rain_home==rain_home")
    .query("rain_dest==rain_dest")
    .groupby(["area", "date"])[["inflow", "rain_dest"]]
    .mean()
    .reset_index()
    .assign(
        #               rain_home_10bin=lambda df: pd.cut(df.rain_home, bins=10),
        rain_dest_10bin=lambda df: pd.cut(df.rain_dest, bins=10, labels=xlabels),
        #               rain_dest_10bin=lambda df: pd.cut(df.rain_dest, bins=10, labels=[1,2,3,4,5,6,7,8,9,10]),
        #               rain_home_5bin=lambda df: pd.cut(df.rain_home, bins=5, labels=[1,2,3,4,5]),
        #               rain_dest_5bin=lambda df: pd.cut(df.rain_dest, bins=5, labels=[1,2,3,4,5]),
        linflow=lambda df: np.log(df.inflow),
    )
)

df_raindest.head(3)

# %%
# linflow-nbh-distance
sns.set_theme(context="notebook", font_scale=1.05, style="white")

_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))


sns.lineplot(
    x="rain_dest_10bin",
    y="linflow",
    data=df_raindest,
    n_boot=10000,
    color="black",
    marker="o",
    ci=95,
    label="Precipitation destination neighborhood",
    ax=ax,
)

sns.lineplot(
    x="rain_home_10bin",
    y="linflow",
    data=df_rainorigin,
    n_boot=10000,
    color="gray",
    marker="X",
    ci=95,
    markers=True,
    label="Precipitation origin neighborhood",
    zorder=0,
    ax=ax,
)

ax.lines[1].set_linestyle("--")

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

LABSIZE = 16
plt.xlabel("Precipitation (mm)", fontweight="bold", loc="center", size=LABSIZE)
plt.ylabel("Log inflow", fontweight="bold", loc="center", size=LABSIZE)

plt.legend(frameon=False, loc="best")

sns.despine()
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "linflow-nbh-rainfall"))

# %% [markdown]
# ## House type

# %%
for xvar in [
    "rm12_home_bin",
    "rm3_home_bin",
    "rm4_home_bin",
    "rm5_home_bin",
    "private_home_bin",
]:
    print(xvar)

    _, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))
    sns.pointplot(
        x=xvar,
        y="basecount",
        data=df,
        ci="sd",
        n_boot=100,
        capsize=None,
        join=False,
        errwidth=2,  # error bar width
        scale=0.8,
        color="black",
        ax=ax,
    )

    plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
    plt.locator_params(axis="y", nbins=4)

    TICKSIZE = 15
    ax.tick_params(axis="both", labelsize=TICKSIZE)

    LABSIZE = 18
    if "rm12_home_bin" in xvar:
        xlabel = "% 1 to 2 room public flats"
    elif "rm3_home_bin" in xvar:
        xlabel = "% 3 room public flats"
    elif "rm4_home_bin" in xvar:
        xlabel = "% 4 room public flats"
    elif "rm5_home_bin" in xvar:
        xlabel = "% 5 room public flats"
    elif "private_home_bin" in xvar:
        xlabel = "% Private housing"
    plt.xlabel(xlabel, fontweight="bold", loc="center", size=LABSIZE)
    plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
    plt.tight_layout()
    save_mpl_fig(os.path.join(SAVEPATH, f"coefplot-pings-{xvar}"))

# %%
for xvar in [
    "rm12_dest_bin",
    "rm3_dest_bin",
    "rm4_dest_bin",
    "rm5_dest_bin",
    "private_dest_bin",
]:
    print(xvar)

    _, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))
    sns.pointplot(
        x=xvar,
        y="dest_basecount",
        data=df,
        ci="sd",
        n_boot=100,
        capsize=None,
        join=False,
        errwidth=2,  # error bar width
        scale=0.8,
        color="black",
        ax=ax,
    )

    plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
    plt.locator_params(axis="y", nbins=4)

    TICKSIZE = 15
    ax.tick_params(axis="both", labelsize=TICKSIZE)

    LABSIZE = 18
    if "rm12_dest_bin" in xvar:
        xlabel = "% 1 to 2 room public flats"
    elif "rm3_dest_bin" in xvar:
        xlabel = "% 3 room public flats"
    elif "rm4_dest_bin" in xvar:
        xlabel = "% 4 room public flats"
    elif "rm5_dest_bin" in xvar:
        xlabel = "% 5 room public flats"
    elif "private_dest_bin" in xvar:
        xlabel = "Private housing"
    plt.xlabel(xlabel, fontweight="bold", loc="center", size=LABSIZE)
    plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
    plt.tight_layout()
    save_mpl_fig(os.path.join(SAVEPATH, f"coefplot-pings-{xvar}"))

# %% [markdown]
# ## House price

# %%
# coefplot-origin-pings-houseprice
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="wpsm_home_bin",
    y="basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel(
    "Weighted house price (per square meter)",
    fontweight="bold",
    loc="center",
    size=LABSIZE,
)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-origin-pings-houseprice"))

# %%
# coefplot-dest-pings-houseprice
_, ax = plt.subplots(figsize=(12 * 0.8, 8 * 0.8))

sns.pointplot(
    x="wpsm_dest_bin",
    y="dest_basecount",
    data=df,
    ci="sd",
    n_boot=100,
    capsize=None,
    join=False,
    errwidth=2,  # error bar width
    scale=0.8,
    color="black",
    ax=ax,
)

plt.xticks(rotation=25, ha="right", rotation_mode="anchor")
plt.locator_params(axis="y", nbins=4)

TICKSIZE = 15
ax.tick_params(axis="both", labelsize=TICKSIZE)

LABSIZE = 18
plt.xlabel(
    "Weighted house price (per square meter)",
    fontweight="bold",
    loc="center",
    size=LABSIZE,
)
plt.ylabel("Captured GPS pings", fontweight="bold", loc="center", size=LABSIZE)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "coefplot-dest-pings-houseprice"))


# %% [markdown]
# ## Inferred residence

# %%
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    import matplotlib.colors as colors

    # https://stackoverflow.com/questions/18926031/how-to-extract-a-subset-of-a-colormap-as-a-new-colormap-in-matplotlib
    new_cmap = colors.LinearSegmentedColormap.from_list(
        "trunc({n},{a:.2f},{b:.2f})".format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)),
    )
    return new_cmap


my_gray_r = plt.get_cmap("gray_r")
my_gray_r = truncate_colormap(my_gray_r, minval=0.5)

# %%
df_home_residents = (
    df.groupby(["home", "resident_count_home"])["basecount"].mean().reset_index()
)
df_home_residents = df.drop_duplicates(["home"], ignore_index=True)
df_home_residents.head(3)

# %%
xvar = "resident_count_home"
yvar = "basecount"
data = df_home_residents

fig, ax = plt.subplots(figsize=(12 * 1.2, 8 * 1.2))
sns.regplot(x=xvar, y=yvar, data=data, color="0.3", scatter=False, ax=ax)

sns.scatterplot(
    x=xvar,
    y=yvar,
    data=data,
    marker="$\circ$",
    #     marker="o",
    #     facecolors='none',
    #     edgecolors="navy",
    #     linewidth=10,
    #     edgewidth=10,
    color="blue",
    size=xvar,
    alpha=0.8,
    sizes=(100, 500),
    legend=False,
    #     hue=xvar,
    palette=my_gray_r,
    ax=ax,
)
ax.set_yticks([0, 1000, 2000, 3000, 4000])
ax.set_xticks([0, 25_000, 50_000, 75_000, 100_000, 125_000])
TICKSIZE = 20
ax.tick_params(axis="both", labelsize=TICKSIZE)
ax.set_xlabel("Census resident data", fontweight="bold", loc="center", size=28)
ax.set_ylabel("GPS-inferred resident data", fontweight="bold", loc="center", size=28)
ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))

# Correlate
r, pval = scipy.stats.pearsonr(data[xvar], data[yvar])
r, pval = format(r, ".2f"), format(pval, ".2f")

labels = []
# labels.append(f"r = {r}")
labels.append(r"$\hat{r} = $" + " " + r)
handles = [
    mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white", lw=0, alpha=0)
] * 1
ax.legend(
    handles,
    labels,
    loc="best",
    fontsize=27,
    frameon=False,
    framealpha=0.5,
    handlelength=0,
    handletextpad=0,
)
plt.tight_layout()
save_mpl_fig(os.path.join(SAVEPATH, "residence-inference"))

# %% [markdown]
# ### Random residence (conditional on more than once)

# %%
ALTERNATE_DUMP_PATH = "../build/raw-data/datadump/"
file_lists = tuple(walk_through_files(ALTERNATE_DUMP_PATH, "csv.gz", fullpath=True))
len(file_lists)

# %%
df_raw = (
    pd.concat(
        [
            pd.read_csv(f, compression="gzip", usecols=["device_xid", "area_id"])
            for f in file_lists
        ]
    )
    .groupby(["device_xid", "area_id"])
    .size()
    .reset_index()
    .rename_column(0, "count")
    #     .loc[lambda x: x.groupby("device_xid")["count"].transform("max") == x["count"]]
    #       .sort_values(["device_xid", "area_id", "count"], ascending=(False, False, True), ignore_index=True)
)

df_raw

# %%
df_psuedo = (
    df_raw.query("count > 1")
    .groupby("device_xid")
    .sample(n=1, random_state=0)
    .rename(columns={"area_id": "home"})
    .groupby("home")
    .size()
    .reset_index()
    .rename_column(0, "psuedo_count")
    .merge(df_home_residents, how="left", on="home", validate="1:1")
)
df_psuedo

# %%
# plot pseudo
xvar = "resident_count_home"
yvar = "psuedo_count"
data = df_psuedo.query(f"{xvar}>0")

print(f"NaN values in {xvar}: {data[xvar].isna().sum()}")
print(f"NaN values in {yvar}: {data[yvar].isna().sum()}")
print(f"Total rows: {len(data)}")

# Correlate
r, pval = scipy.stats.pearsonr(data[xvar], data[yvar])
# r, pval = format(r, ".2f"), format(pval, ".2f")
print(f"r = {r}")

# %% [markdown]
# ### Unconditional random

# %%
devices = (
    df_raw.groupby("device_xid")
    .sum()
    .reset_index()
    .query("count>30")["device_xid"]
    .tolist()
)
devices[:5]

# %%
all_areas = df_psuedo["home"].unique()

# %%
np.random.seed(0)
random_area_assignments = pd.DataFrame(
    {
        "device_xid": devices,
        "random_area_id": np.random.choice(all_areas, size=len(devices)),
    }
)

random_area_assignments

# %%
df_with_random_areas = (
    random_area_assignments.merge(
        df_raw,
        left_on=["device_xid", "random_area_id"],
        right_on=["device_xid", "area_id"],
        how="left",
    )
    .assign(
        area_id=lambda x: x["random_area_id"],
    )
    .drop(columns=["random_area_id"])
)
df_with_random_areas

# %%
df_psuedo = (
    df_with_random_areas.rename(columns={"area_id": "home"})
    .groupby("home")
    .size()
    .reset_index()
    .rename(columns={0: "psuedo_count"})
    .merge(df_home_residents, how="left", on="home", validate="1:1")
)
df_psuedo

# %%
# Correlate
xvar = "resident_count_home"
yvar = "psuedo_count"
data = df_psuedo.query(f"{xvar}>0")

print(f"NaN values in {xvar}: {data[xvar].isna().sum()}")
print(f"NaN values in {yvar}: {data[yvar].isna().sum()}")
print(f"Total rows: {len(data)}")

# Correlate
r, pval = scipy.stats.pearsonr(data[xvar], data[yvar])
r, pval = format(r, ".2f"), format(pval, ".2f")
print(f"r = {r}")

# %%
