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
import numpy as np
import janitor

janitor

from utilities import cat_to_num

FP_PROPPRICE = "input/propprice-subzone.csv"
FP_HTYPE = "input/htype.csv"
FP_PA_SHP = "input/master-plan-2014-planning-area-boundary-no-sea/master-plan-2014-planning-area-boundary-no-sea-shp.zip"
FP_INC = "input/resident-working-persons-aged-15-years-over-by-planning-area-gross-monthly-income-from-work-2015/resident-working-persons-aged-15-yrs-over-by-pa-gross-monthly-income-from-work.csv"

# %%
# Read in house prices
df_price = pd.read_csv(FP_PROPPRICE).rename(columns={"area": "subzone"})
df_price.head(3)

# %%
# Read in residence data
df_htype = (
    pd.read_csv(FP_HTYPE)
    .rename(columns={"area": "subzone", "pa": "planning_area"})
    .assign(planning_area=lambda df: df["planning_area"].str.lower())
    .query("resident_count!=0")
    # Retrieve region of planning areas
    .merge(
        (
            gpd.read_file(FP_PA_SHP)
            .rename(columns={"REGION_C": "region"})
            .assign(planning_area=lambda gdf: gdf.PLN_AREA_N.str.lower())
            .filter(["planning_area", "region"])
        ),
        how="left",
        on="planning_area",
        validate="m:1",
    )
)
df_htype.head(3)

# %%
# Read and clean income data
df_income = (
    pd.read_csv(FP_INC, usecols=["level_1", "level_3", "value"])
    .rename(columns={"level_1": "income", "level_3": "planning_area", "value": "count"})
    .query('income!= "Total"')
    .assign(planning_area=lambda df: df["planning_area"].str.lower())
)

income_cats = df_income["income"].unique().tolist()

# Convert cat to median values
df_income["income"] = df_income["income"].map(
    cat_to_num(income_cats, **{"Below $1,000": 500})
)

# Get total inc = income * count
df_income["income"] = df_income["income"] * df_income["count"]

# Groupby area and sum
df_income = df_income.groupby(["planning_area"])["income"].sum().reset_index()
df_income.head(3)
df_income = df_income.merge(
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

df_income.head(3)

# %%
# Merge all
df = df_price.merge(df_htype, on="subzone", how="outer", validate="1:1").merge(
    df_income, on="planning_area", how="outer", validate="m:1"
)

df.head(5)

# %%
df["wpsm_private"] = df["private"] / 100 * df["private_psm"]
df["wpsm_public"] = (100 - df["private"]) / 100 * df["public_psm"]
df["wpsm"] = df[["wpsm_private", "wpsm_public"]].sum(
    axis=1, skipna=True
)  # Treat na as 0
# If zero, means both private and public data is missing, replace as missing
df["wpsm"] = np.where(df["wpsm"] == 0, np.nan, df["wpsm"])

df["wprice_private"] = df["private"] / 100 * df["private_price"]
df["wprice_public"] = (100 - df["private"]) / 100 * df["public_price"]
df["wprice"] = df[["wprice_private", "wprice_public"]].sum(
    axis=1, skipna=True
)  # Treat na as 0
# If zero, means both private and public data is missing, replace as missing
df["wprice"] = np.where(df["wprice"] == 0, np.nan, df["wprice"])

# %%
(
    df.remove_columns(["subzone", "htype"])
    .groupby(["planning_area", "region"])
    .mean()
    .reset_index()
    .to_csv("./out/pa-price.csv", index=False)
)

# %%
