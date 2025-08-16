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

# %%
import janitor
janitor

import geopandas as gpd

# %%
# Subzones/\nbhs{} (finer)
gdf_sz = gpd.read_file("../build/raw-data/master-plan-2019-subzone-boundary-no-sea/master-plan-2019-subzone-boundary-no-sea-kml.kml")
gdf_sz

# %%
# Census areas, with residential records
df_census = (
    pd.read_csv("../build/raw-data/resident-population-by-planning-area-subzone-age-group-and-sex-2015/resident-population-by-planning-area-age-group-and-sex.csv")
    .rename_column("level_3", "pa")
    .groupby("pa")
    ["value"]
    .sum()
    .reset_index()
    .query("pa!='Total'")
    .reset_index(drop=True)
    .assign(pa=lambda df_: df_["pa"].str.replace("- Total", ""))
)
df_census

# %%
df = (
    pd.read_parquet("input/cd-panel-labels.parquet")
    .dropna(subset=["inflow"])
)
df.head(3)

# %%
#Census areas, with GPS records
df["pa_home"].nunique()

# %%
#Census areas, with GPS records
df["pa_dest"].nunique()

# %%
df["home"].nunique()

# %%
#Subzones/\nbhs{}, with GPS records
df["area"].nunique()

# %%
(
    df
    .drop_duplicates(["home"], ignore_index=True)
    .query("resident_count_home>0")
    ["home"].nunique()
)

# %%
c = 0
for pa in list(df["pa_home"].unique()):
    if pa in df_census["pa"].tolist():
        c+=1
    else:
        print(pa)
print(c)        

# %%
df_census_sz = (
    pd.read_csv("../build/raw-data/resident-population-by-planning-area-subzone-age-group-and-sex-2015/resident-population-by-subzone-age-group-and-sex.csv")
    .rename_column("level_4", "sz")
    .groupby("sz")
    ["value"]
    .sum()
    .reset_index()
    .query('value>0')
    .reset_index(drop=True)
)
df_census_sz

# %%
# Subzones/\nbhs{}, with residential records
df_census_sz["sz"].nunique()

# %%
