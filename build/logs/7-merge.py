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
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import gc

from utilities import walk_through_files

import warnings

warnings.filterwarnings("ignore")

pd.set_option("display.max_rows", 250)
pd.set_option("display.max_columns", 150)

FP_CDGRAVITY = os.path.join("intermediate-output", "daily-movecount.csv.gz")

FP_WEATHERSTATION_CROSSWALK = os.path.join(
    "intermediate-output", "subzones2014-weatherstation-crosswalk.csv"
)
FP_WEATHER = os.path.join("raw-data", "SWEAT", "datafiles", "weather")

FP_CD_AREANAMES = os.path.join("intermediate-output", "citydata-subzones.csv")
FP_HTYPE = os.path.join("intermediate-output", "htype.csv")
FP_SUBZONES_SHP = os.path.join(
    "zip:/" "raw-data",
    "master-plan-2014-subzone-boundary-no-sea",
    "master-plan-2014-subzone-boundary-no-sea-shp.zip",
)

FP_REALIS = os.path.join("preprocessed-data", "realis_with_postal_code_complete.csv.gz")
FP_HDBRESALE = os.path.join("preprocessed-data", "hdb_saledata_with_geodata.csv.gz")

FP_AGEGENDER = os.path.join(
    "raw-data",
    "resident-population-by-planning-area-subzone-age-group-and-sex-2015",
    "resident-population-by-subzone-age-group-and-sex.csv",
)
FP_ETHNIC = os.path.join(
    "raw-data",
    "resident-population-by-planning-area-subzone-ethnic-group-and-sex-2015",
    "resident-population-by-subzone-ethnic-group-and-sex.csv",
)
FP_PUB_RENTALS = os.path.join("preprocessed-data", "subzone_rental_portion.csv")
FP_DIST = os.path.join("preprocessed-data", "distance_subzone_2014.csv")
FP_POI = os.path.join("intermediate-output", "subzones-poi-count.csv")

FP_SUBZONES_SHP = os.path.join(
    "zip://",
    "raw-data",
    "master-plan-2014-subzone-boundary-no-sea",
    "master-plan-2014-subzone-boundary-no-sea-shp.zip",
)

SAVEPATH = os.path.join("cd-panel.csv")

# %% [markdown]
# ### Prep Citydata gravity panel

# %% code_folding=[]
# Prep area to xid dict AND dict to clean 4 names
xid_area = (
    pd.read_csv(FP_CD_AREANAMES)
    .rename(columns={"subzone": "area", "areaid": "area_id"})
    .assign(area=lambda df: df["area"].str.lower().str.strip())
)
xid_area = dict(zip(xid_area["area_id"], xid_area["area"]))

# Clean obvious name errors from Citydata (to get perfect match)
clean_cd_subzone = {
    "marina east mp": "marina east (mp)",
    "monks hill": "monk's hill",
    "national university of s pore": "national university of s'pore",
    "peoples park": "people's park",
}
xid_area

# %%
df = pd.read_csv(FP_CDGRAVITY, compression="gzip")

df = (
    pd.read_csv(FP_CDGRAVITY, compression="gzip")
    .merge(
        (
            df.groupby(["home", "date"])["inflow_count"]
            .sum()
            .reset_index()
            .rename(columns={"inflow_count": "basecount"})
        ),
        how="left",
        on=["home", "date"],
    )
    .merge(
        (
            df.groupby(["area_id", "date"])["inflow_count"]
            .sum()
            .reset_index()
            .rename(columns={"inflow_count": "dest_basecount"})
        ),
        how="left",
        on=["area_id", "date"],
    )
    .rename(columns={"inflow_count": "inflow"})
    .assign(inflow=lambda df: df["inflow"] / df["basecount"] * 100)
    .assign(date=lambda df: pd.to_datetime(df["date"]))
    .assign(date=lambda df: [timestamp.date() for timestamp in df["date"]])
    .assign(home=lambda df: df["home"].map(xid_area))
    .assign(area=lambda df: df["area_id"].map(xid_area))
    .drop("area_id", axis=1)
    .assign(home=lambda df: df["home"].replace(clean_cd_subzone))
    .assign(area=lambda df: df["area"].replace(clean_cd_subzone))
    #     .sort_values(["home", "area", "date"], ignore_index=True)
    .sort_values(["home", "date", "area"], ignore_index=True)
)
print(len(df))
df

# %%
print(df["home"].nunique())
print(df["area"].nunique())
print(df["date"].nunique())

# %%
300 * 91

# %%
df[df.duplicated(subset=["home", "area", "date"], keep=False)]

# %% [markdown]
# ### Merge with house types

# %% code_folding=[]
# read in and merge
htype = pd.read_csv(FP_HTYPE).assign(area=lambda df: df["area"].str.lower().str.strip())
# Get home area dwelling type
df = (
    df
    # Convert home column to string to ensure compatibility
    .assign(home=lambda df: df["home"].astype(str)).merge(
        htype.add_suffix("_home")
        .rename(columns={"area_home": "home"})
        .assign(home=lambda df: df["home"].astype(str)),
        how="left",
        on="home",
        validate="m:1",
    )
)

# Get dest area dwelling type
df = (
    df
    # Convert AREA column to string to ensure compatibility (not home!)
    .assign(area=lambda df: df["area"].astype(str)).merge(
        htype.add_suffix("_dest")
        .rename(columns={"area_dest": "area"})
        .assign(area=lambda df: df["area"].astype(str)),
        how="left",
        on="area",  # merging on 'area', not 'home'
        validate="m:1",
    )
)

del htype
gc.collect()
df.head()

# %% [markdown]
# ### Prep Weather

# %% code_folding=[]
# 2014 Area to weather station crosswalk
ws_area_crosswalk = (
    pd.read_csv(FP_WEATHERSTATION_CROSSWALK)
    .rename(columns={"subzone": "area", "weather_station": "wsid"})
    .assign(area=lambda df: df["area"].str.lower().str.strip())
)

ws_area_crosswalk = dict(zip(ws_area_crosswalk["area"], ws_area_crosswalk["wsid"]))

# %% code_folding=[]
# Read in weather data
WEATHER_DATA = list(walk_through_files(FP_WEATHER, "csv", returnboth=True))

weather = pd.DataFrame()

_usecols = ["Year", "Month", "Day", "Daily Rainfall Total (mm)"]
for path, file in WEATHER_DATA:
    for period in ["202001", "202002", "202003"]:
        if period not in file:
            continue

        wsid = file.split("-")[0]

        _df = (
            pd.read_csv(os.path.join(path, file), usecols=_usecols)
            .assign(wsid=wsid)
            .rename(
                columns={
                    "Year": "year",
                    "Month": "month",
                    "Day": "day",
                    "Daily Rainfall Total (mm)": "rainfall",
                }
            )
            .assign(date=lambda df: pd.to_datetime(df[["year", "month", "day"]]))
            .assign(date=lambda df: [timestamp.date() for timestamp in df["date"]])
            .drop(["year", "month", "day"], axis=1)
        )

        weather = pd.concat([weather, _df], ignore_index=True)

# %%
len(weather["wsid"].unique().tolist())

# %%
# weather = (weather.merge(ws_area_crosswalk, how='inner', on='wsid', validate='m:m')
#            .drop('wsid', axis=1)
#           )

# %%
# Fill in missing data
weather = (
    weather.groupby(["wsid"])
    .apply(lambda group: group.interpolate(method="linear"))
    .drop(columns=["wsid"])
    .reset_index()
    .drop(columns=["level_1"])
)
weather

# %%
weather

# %% [markdown]
# ### Merge with weather

# %%
assert type(df.loc[0, "date"]) == type(weather.reset_index().loc[0, "date"])

# %%
df["wsid_home"] = df["home"].map(ws_area_crosswalk)
df["wsid_dest"] = df["area"].map(ws_area_crosswalk)

# %% code_folding=[]
# Home area weather
df = df.merge(
    weather.rename(columns={"wsid": "wsid_home", "rainfall": "rain_home"}),
    how="left",
    on=["date", "wsid_home"],
    validate="m:1",
)

# Dest area weather
df = df.merge(
    weather.rename(columns={"wsid": "wsid_dest", "rainfall": "rain_dest"}),
    how="left",
    on=["date", "wsid_dest"],
    validate="m:1",
)

del weather
gc.collect()

df.drop(["wsid_home", "wsid_dest"], axis=1, inplace=True)
df.head()

# %% [markdown]
# ### Merge area distance and continguity

# %%
_usecols = [
    "Subzone Name_o",
    "Subzone Name_d",
    "centroid_distance",
    "edge_distance",
    "centroid_distance_epsg",
    "edge_distance_epsg",
]

dist = (
    pd.read_csv(FP_DIST, usecols=_usecols)
    .rename(columns={"Subzone Name_o": "home", "Subzone Name_d": "area"})
    .assign(home=lambda df: df["home"].str.lower().str.strip())
    .assign(area=lambda df: df["area"].str.lower().str.strip())
)

df = df.merge(dist, how="left", on=["home", "area"], validate="m:m")

del dist
gc.collect()
df.head()

# %%
# get_diff_stringval_from_2columns(df, 'home', dist, 'home')

# %%
# get_diff_stringval_from_2columns(df, 'area', dist, 'area')

# %% [markdown]
# ### Get area's land area

# %% code_folding=[]
# https://www.singstat.gov.sg/-/media/files/publications/population/population2018-map1.pdf
subzones_area = (
    gpd.read_file(FP_SUBZONES_SHP)
    .rename(columns={"SUBZONE_N": "subzone", "REGION_C": "region"})
    .assign(subzone=lambda gdf: gdf["subzone"].str.lower())
    .assign(area=lambda gdf: gdf["geometry"].area / (10**6))
    .filter(["subzone", "area", "region"])
)
# subzones_area.crs

# %% code_folding=[]
# Merge
df = df.merge(
    subzones_area.rename(
        columns={"subzone": "home", "area": "area_o", "region": "region_o"}
    ),
    how="left",
    on="home",
    validate="m:1",
)

df = df.merge(
    subzones_area.rename(
        columns={"subzone": "area", "area": "area_d", "region": "region_d"}
    ),
    how="left",
    on="area",
    validate="m:1",
)
df.head()

# %% [markdown]
# ### Merge other available subzone census var.

# %% [markdown]
# #### Age and gender

# %% code_folding=[]
# Read in and prep
collapse_age_brackets = {
    "0 - 4": "0-9",
    "5 - 9": "0-9",
    "10 - 14": "10-19",
    "15 - 19": "10-19",
    "20 - 24": "20-39",
    "25 - 29": "20-39",
    "30 - 34": "20-39",
    "35 - 39": "20-39",
    "40 - 44": "40-64",
    "45 - 49": "40-64",
    "50 - 54": "40-64",
    "55 - 59": "40-64",
    "60 - 64": "40-64",
    "65 - 69": ">65",
    "70 - 74": ">65",
    "75 - 79": ">65",
    "80 - 84": ">65",
    "85 & Over": ">65",
}

age_bracket_codes = {"0-9": 1, "10-19": 2, "20-39": 3, "40-64": 4, ">65": 5}

# Agegender
agegender = (
    pd.read_csv(FP_AGEGENDER, usecols=["level_1", "level_2", "level_4", "value"])
    .rename(columns={"level_1": "gender", "level_2": "age", "level_4": "subzone"})
    .query('age!="Total"')
    .query('gender!="Total"')
    .assign(subzone=lambda df: df["subzone"].str.lower())
    .assign(age=lambda df: df["age"].map(collapse_age_brackets))
    .assign(age=lambda df: df["age"].map(age_bracket_codes))
)

ttpop = (
    agegender.groupby("subzone")["value"]
    .sum()
    .reset_index()
    .rename(columns={"value": "tt_pop"})
)

females = (
    agegender.query('gender=="Females"')
    .drop("gender", axis=1)
    .groupby("subzone")["value"]
    .sum()
    .reset_index()
    .rename(columns={"value": "females"})
)


age_20 = (
    agegender.query("age<=2")
    .drop("age", axis=1)
    .groupby(["subzone"])
    .sum()
    .reset_index()
    .rename(columns={"value": "age_20"})
)
age20_40 = (
    agegender.query("age==3")
    .drop("age", axis=1)
    .groupby(["subzone"])
    .sum()
    .reset_index()
    .rename(columns={"value": "age20_40"})
)

age65_ = (
    agegender.query("age==5")
    .drop("age", axis=1)
    .groupby(["subzone"])
    .sum()
    .reset_index()
    .rename(columns={"value": "age65_"})
)

# %% code_folding=[]
# Merge origin
for pd_df in [females, age_20, age20_40, age65_, ttpop]:
    _pd_df = pd_df.add_suffix("_o").rename(columns={"subzone_o": "home"})

    df = df.merge(_pd_df, how="left", on="home", validate="m:1")

# Merge dest
for pd_df in [females, age_20, age20_40, age65_, ttpop]:
    _pd_df = pd_df.add_suffix("_d").rename(columns={"subzone_d": "area"})

    df = df.merge(_pd_df, how="left", on="area", validate="m:1")

del agegender, females, ttpop, age20_40, age_20, age65_

# %% code_folding=[]
# Get proportions and drop total
for x in ["females_o", "age_20_o", "age20_40_o", "age65__o"]:
    df[x] = 100 * (df[x] / df["tt_pop_o"])

for x in ["females_d", "age_20_d", "age20_40_d", "age65__d"]:
    df[x] = 100 * (df[x] / df["tt_pop_d"])

df.drop(["tt_pop_o", "tt_pop_d"], axis=1, inplace=True)
df.head()

# %% [markdown]
# #### Ethnic

# %% code_folding=[]
# Read in and prep
ethnic = (
    pd.read_csv(FP_ETHNIC, usecols=["level_1", "level_2", "level_4", "value"])
    .rename(columns={"level_1": "ethnic", "level_2": "sex", "level_4": "subzone"})
    .query('ethnic!="Total"')
    .query('sex!="Total"')
    .drop("sex", axis=1)
    .assign(subzone=lambda df: df["subzone"].str.lower().str.strip())
)

chinese = (
    ethnic[ethnic["ethnic"] == "Chinese"]
    .drop("ethnic", axis=1)
    .groupby("subzone")
    .sum()
    .reset_index()
    .rename(columns={"value": "chinese"})
)

malay = (
    ethnic[ethnic["ethnic"] == "Malays"]
    .drop("ethnic", axis=1)
    .groupby("subzone")
    .sum()
    .reset_index()
    .rename(columns={"value": "malays"})
)

indian = (
    ethnic[ethnic["ethnic"] == "Indians"]
    .drop("ethnic", axis=1)
    .groupby("subzone")
    .sum()
    .reset_index()
    .rename(columns={"value": "indians"})
)

other = (
    ethnic[ethnic["ethnic"] == "Others"]
    .drop("ethnic", axis=1)
    .groupby("subzone")
    .sum()
    .reset_index()
    .rename(columns={"value": "others"})
)

tt_ethnic = (
    ethnic.drop("ethnic", axis=1)
    .groupby("subzone")
    .sum()
    .reset_index()
    .rename(columns={"value": "tt_ethnic"})
)

# %% code_folding=[]
# Merge origin
for pd_df in [chinese, malay, indian, other, tt_ethnic]:
    _pd_df = pd_df.add_suffix("_o").rename(columns={"subzone_o": "home"})

    df = df.merge(_pd_df, how="left", on="home", validate="m:1")

# Merge dest
for pd_df in [chinese, malay, indian, other, tt_ethnic]:
    _pd_df = pd_df.add_suffix("_d").rename(columns={"subzone_d": "area"})

    df = df.merge(_pd_df, how="left", on="area", validate="m:1")

del chinese, indian, malay, other, tt_ethnic

# %% code_folding=[]
# Get proportions and drop total
for x in ["chinese_o", "malays_o", "indians_o", "others_o"]:
    df[x] = 100 * (df[x] / df["tt_ethnic_o"])

for x in ["chinese_d", "malays_d", "indians_d", "others_d"]:
    df[x] = 100 * (df[x] / df["tt_ethnic_d"])

df.drop(["tt_ethnic_o", "tt_ethnic_d"], axis=1, inplace=True)
df.head()

# %% [markdown]
# ### Merge with POIs count

# %%
poi = (
    pd.read_csv(FP_POI)
    .assign(subzone=lambda df: df["subzone"].str.lower().str.strip())
    .rename(columns={"subzone": "area"})
)

df = df.merge(poi, how="left", on="area", validate="m:1")

del poi
gc.collect()
df.head()

# %% [markdown]
# ### Merge Public Rentals

# %%
_usecols = [
    "area",
    "1room_rental_pct",
    "2room_rental_pct",
    "3room_rental_pct",
    "other_room_rental_pct",
    "total_dwelling_units",
]
pub_rentals = (
    pd.read_csv(FP_PUB_RENTALS, usecols=_usecols)
    .query("total_dwelling_units!=0")
    .assign(rm12_rental_pct=lambda df: df["1room_rental_pct"] + df["2room_rental_pct"])
    .assign(
        rental_pct=lambda df: df["rm12_rental_pct"]
        + df["3room_rental_pct"]
        + df["other_room_rental_pct"]
    )
    .drop(
        [
            "1room_rental_pct",
            "2room_rental_pct",
            "3room_rental_pct",
            "other_room_rental_pct",
        ],
        axis=1,
    )
)

df = df.merge(
    pub_rentals.add_suffix("_home").rename(columns={"area_home": "home"}),
    how="left",
    on="home",
    validate="m:1",
)

df = df.merge(
    pub_rentals.add_suffix("_dest").rename(columns={"area_dest": "area"}),
    how="left",
    on="area",
    validate="m:1",
)

del pub_rentals
gc.collect()
df.head()

# %% [markdown]
# ### Merge resale price

# %% [markdown]
# #### Avg public & private together

# %%
YEARS = [2017, 2018, 2019]  # 3 years before sample year of 2020

df_price = (
    pd.concat(
        [
            (
                pd.read_csv(
                    FP_HDBRESALE,
                    compression="gzip",
                    usecols=["month", "psm", "resale_price", "subzone_name"],
                )
                .rename(columns={"resale_price": "price"})
                .assign(area=lambda df: df["subzone_name"].str.lower())
                # retain only transactions in 2017 to 2019
                .assign(year=lambda df: df["month"].str.slice(stop=4).astype(int))
                .query("year in @YEARS")
                .filter(["area", "psm", "price"])
            ),
            (
                pd.read_csv(
                    FP_REALIS,
                    compression="gzip",
                    usecols=[
                        "contractdate",
                        "unitpricepsm",
                        "transactedprice",
                        "subzone_name",
                    ],
                )
                .rename(columns={"transactedprice": "price", "unitpricepsm": "psm"})
                .assign(area=lambda df: df["subzone_name"].str.lower())
                # retain only transactions in 2017 to 2019
                .assign(
                    year=lambda df: df["contractdate"].str.slice(stop=4).astype(int)
                )
                .query("year in @YEARS")
                .filter(["area", "psm", "price"])
            ),
        ],
        ignore_index=True,
    )
    # Remove comma from valuations (e.g. 17,493)
    .assign(
        psm=lambda df: df["psm"].astype("string").str.replace(",", "").astype("float")
    )
    .assign(
        price=lambda df: df["price"]
        .astype("string")
        .str.replace(",", "")
        .astype("float")
    )
    # Get num of property transactions by subzone
    .pipe(
        lambda df: df.merge(
            df.groupby("area")
            .size()
            .reset_index()
            .rename(columns={0: "num_transactions"}),
            how="left",
            on="area",
            validate="m:1",
        )
    )
    .groupby(["area", "num_transactions"])
    .mean()
    .reset_index()
)

df_price.head()

# %%
df = df.merge(
    df_price.add_suffix("_home").rename(columns={"area_home": "home"}),
    how="left",
    on="home",
    validate="m:1",
)

df = df.merge(
    df_price.add_suffix("_dest").rename(columns={"area_dest": "area"}),
    how="left",
    on="area",
    validate="m:1",
)
df.head()

# %%
df_price.num_transactions.sum()

# %% [markdown]
# #### Keep public & private separate

# %%
df_hdb_price = (
    (
        pd.read_csv(
            FP_HDBRESALE,
            compression="gzip",
            usecols=["month", "psm", "resale_price", "subzone_name"],
        )
        .rename(columns={"resale_price": "price"})
        .assign(area=lambda df: df["subzone_name"].str.lower())
        # retain only transactions in 2017 to 2019
        .assign(year=lambda df: df["month"].str.slice(stop=4).astype(int))
        .query("year in @YEARS")
        .filter(["area", "psm", "price"])
        # Get num of property transactions by subzone
        .pipe(
            lambda df: df.merge(
                df.groupby("area")
                .size()
                .reset_index()
                .rename(columns={0: "public_num_transactions"}),
                how="left",
                on="area",
                validate="m:1",
            )
        )
    )
    # Take avg of psm over areas
    .groupby(["area", "public_num_transactions"])
    .mean()
    .reset_index()
    .rename(columns={"psm": "public_psm", "price": "public_price"})
)

# Add to df_price (subzone level transaction price)
df_price = df_price.merge(df_hdb_price, how="left", on="area", validate="1:1")

df_hdb_price.head(2)

# %%
# Merge with df
df = df.merge(
    df_hdb_price.add_suffix("_home").rename(columns={"area_home": "home"}),
    how="left",
    on="home",
    validate="m:1",
)

df = df.merge(
    df_hdb_price.add_suffix("_dest").rename(columns={"area_dest": "area"}),
    how="left",
    on="area",
    validate="m:1",
)

del df_hdb_price
gc.collect()

# %%
df_private_price = (
    (
        pd.read_csv(
            FP_REALIS,
            compression="gzip",
            usecols=["contractdate", "unitpricepsm", "transactedprice", "subzone_name"],
        )
        .rename(columns={"transactedprice": "price", "unitpricepsm": "psm"})
        .assign(area=lambda df: df["subzone_name"].str.lower())
        # retain only transactions in 2017 to 2019
        .assign(year=lambda df: df["contractdate"].str.slice(stop=4).astype(int))
        .query("year in @YEARS")
        .filter(["area", "psm", "price"])
        # Remove comma from valuations (e.g. 17,493)
        .assign(
            psm=lambda df: df["psm"]
            .astype("string")
            .str.replace(",", "")
            .astype("float")
        )
        .assign(
            price=lambda df: df["price"]
            .astype("string")
            .str.replace(",", "")
            .astype("float")
        )
        .pipe(
            lambda df: df.merge(
                df.groupby("area")
                .size()
                .reset_index()
                .rename(columns={0: "private_num_transactions"}),
                how="left",
                on="area",
                validate="m:1",
            )
        )
    )
    # Take avg of psm over areas
    .groupby(["area", "private_num_transactions"])
    .mean()
    .reset_index()
    .rename(columns={"psm": "private_psm", "price": "private_price"})
)

# Add to df_price (subzone level transaction price)
df_price = df_price.merge(df_private_price, how="left", on="area", validate="1:1")

df_private_price.head(2)

# %%
# Merge with df
df = df.merge(
    df_private_price.add_suffix("_home").rename(columns={"area_home": "home"}),
    how="left",
    on="home",
    validate="m:1",
)

df = df.merge(
    df_private_price.add_suffix("_dest").rename(columns={"area_dest": "area"}),
    how="left",
    on="area",
    validate="m:1",
)

del df_private_price
gc.collect()

# %%
# Save subzone level transaction price
df_price.to_csv(
    os.path.join("intermediate-output", "propprice-subzone.csv"), index=False
)

del df_price
gc.collect()

# %% [markdown]
# #### Compute weighted (by public/private residence share) house price

# %%
# weighted PSM for home
df["wpsm_private_home"] = df["private_home"] / 100 * df["private_psm_home"]
df["wpsm_public_home"] = (100 - df["private_home"]) / 100 * df["public_psm_home"]
df["wpsm_home"] = df[["wpsm_private_home", "wpsm_public_home"]].sum(
    axis=1, skipna=True
)  # Treat na as 0
# If zero, means both private and public data is missing, replace as missing
df["wpsm_home"] = np.where(df["wpsm_home"] == 0, np.nan, df["wpsm_home"])

# weighted PSM for dest
df["wpsm_private_dest"] = df["private_dest"] / 100 * df["private_psm_dest"]
df["wpsm_public_dest"] = (100 - df["private_dest"]) / 100 * df["public_psm_dest"]
df["wpsm_dest"] = df[["wpsm_private_dest", "wpsm_public_dest"]].sum(
    axis=1, skipna=True
)  # Treat na as 0
# If zero, means both private and public data is missing, replace as missing
df["wpsm_dest"] = np.where(df["wpsm_dest"] == 0, np.nan, df["wpsm_dest"])

# # weighted price for home
# df["wprice_private_home"] = df["private_home"] / 100 * df["private_price_home"]
# df["wprice_public_home"] = (100 - df["private_home"]) / 100 * df["public_price_home"]
# df["wprice_home"] = df[["wprice_private_home", "wprice_public_home"]].sum(
#     axis=1, skipna=True
# )  # Treat na as 0
# # If zero, means both private and public data is missing, replace as missing
# df["wprice_home"] = np.where(df["wprice_home"] == 0, np.nan, df["wprice_home"])

# # weighted price for dest
# df["wprice_private_dest"] = df["private_home"] / 100 * df["private_price_dest"]
# df["wprice_public_dest"] = (100 - df["private_home"]) / 100 * df["public_price_dest"]
# df["wprice_dest"] = df[["wprice_private_dest", "wprice_public_dest"]].sum(
#     axis=1, skipna=True
# )  # Treat na as 0
# # If zero, means both private and public data is missing, replace as missing
# df["wprice_dest"] = np.where(df["wprice_dest"] == 0, np.nan, df["wprice_dest"])

# %% [markdown]
# ### Save

# %%
# Dont remember what this is for
_g = ["pa_home", "home", "rm12_home"]
df[_g].drop_duplicates().sort_values("rm12_home", ascending=False).head(10)

# %%
df.to_csv("cd-panel-labels.csv", index=False)

# %%
# Codify area names (remove text names, e.g. Crawford --> 16)
for col in ["home", "area", "pa_home", "pa_dest"]:
    df[col] = df[col].astype("category").cat.codes

# %%
df.head(3)

# %%
df.to_csv(SAVEPATH, index=False)

# %%
