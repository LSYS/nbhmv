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
import geopandas as gpd
import fiona

fiona.drvsupport.supported_drivers["KML"] = (
    "rw"  # enable KML support which is disabled by default
)
import gc
import janitor 
janitor
pd.set_option("display.max_rows", 500)

from utilities import walk_through_files, auto_reduce_mem, get_html_table_metadata
import osmnx
import warnings
warnings.filterwarnings('ignore')

# %%
FP_SUBZONES_SHP = os.path.join(
    "zip://" "./",
    "raw-data",
    "master-plan-2014-subzone-boundary-no-sea",
    "master-plan-2014-subzone-boundary-no-sea-kml.zip",
)
FP_PARKS = os.path.join("raw-data", "poi", "parks", "parks-geojson.geojson")
FP_LIB = os.path.join("raw-data", "poi", "libraries", "libraries-geojson.geojson")
FP_TRANSIT = os.path.join(
    "raw-data",
    "poi",
    "lta-mrt-station-exit",
    "lta-mrt-station-exit-geojson.geojson",
)
FP_PRESCH = os.path.join(
    "raw-data",
    "poi",
    "pre-schools-location",
    "pre-schools-location-geojson.geojson",
)
FP_SPORT = os.path.join(
    "raw-data",
    "poi",
    "sportsg-sport-facilities",
    "sportsg-sport-facilities-geojson.geojson",
)
FP_MART = os.path.join(
    "raw-data", "poi", "supermarkets", "supermarkets-geojson.geojson"
)
FP_SCHZONE = os.path.join(
    "raw-data", "poi", "lta-school-zone", "lta-school-zone-kml.kml"
)
FP_SILVER = os.path.join(
    "raw-data", "poi", "lta-silver-zone", "lta-silver-zone-kml.kml"
)
FP_TOURIST = os.path.join(
    "zip://",
    "raw-data",
    "poi",
    "tourist-attractions",
    "tourist-attractions-kml.zip",
)
FP_LRT = os.path.join(
    "raw-data", "poi", "singapore-postal-codes-master", "lrt_stations.json"
)
FP_MRT = os.path.join(
    "raw-data", "poi", "singapore-postal-codes-master", "mrt_stations.json"
)
FP_BUILDINGS = os.path.join(
    "raw-data", "poi", "singapore-postal-codes-master", "buildings.json"
)

# FP_REG_BUSINESS = os.path.join(
#     "..", "..", "wgw-lf", "acra-information-on-corporate-entities"
# )
FP_REG_BUSINESS = os.path.join("raw-data", "ACRAInformationonCorporateEntities")
FP_XWALK_ZIP_SUBZONE = os.path.join(
    "intermediate-output", "fixed_postal_subzone_xwalk.csv"
)

FP_HAWKERS = os.path.join("raw-data", "HawkerCentresGEOJSON.geojson")

SAVEPATH = os.path.join("intermediate-output", "subzones-poi-count.csv")

# %%
xwalk = (
    pd.read_csv(FP_XWALK_ZIP_SUBZONE)
    .rename(columns={"POSTAL": "postcode", "subzone_name": "subzone"})
    .assign(postcode=lambda df: df["postcode"].astype("str").str.zfill(6))
)
xwalk.head(3)

# %% [markdown]
# ### Data.gov.sg resources

# %%
subzones = (
    gpd.read_file(FP_SUBZONES_SHP)
    .rename(columns={"Name": "subzone"})
    .drop("Description", axis=1)
)
subzones.head(3)

# %%
# Parks
parks = (
    gpd.read_file(FP_PARKS).rename(columns={"Name": "park"}).drop("Description", axis=1)
)

assert parks.crs == subzones.crs

parks = (
    gpd.sjoin(parks, subzones, how="left", predicate="within")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "parks"})
)
parks.head(3)

# %%
# Libraries
lib = (
    gpd.read_file(FP_LIB)
    .rename(columns={"Name": "libraries"})
    .drop("Description", axis=1)
)

assert lib.crs == subzones.crs

lib = (
    gpd.sjoin(lib, subzones, how="left", predicate="within")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "libraries"})
)
lib.head(3)

# %%
# LRT & MRT stations
transit = (
    gpd.read_file(FP_TRANSIT)
    .rename(columns={"Name": "transit"})
    .drop("Description", axis=1)
)

assert transit.crs == subzones.crs

transit = (
    gpd.sjoin(transit, subzones, how="left", predicate="within")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "transit"})
)
transit.head(3)

# %%
# Preschools
presch = (
    gpd.read_file(FP_PRESCH)
    .rename(columns={"Name": "preschools"})
    .drop("Description", axis=1)
)

assert presch.crs == subzones.crs

presch = (
    gpd.sjoin(presch, subzones, how="left", predicate="within")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "preschools"})
)

# %%
# Sport facilities
sport = (
    gpd.read_file(FP_SPORT)
    .rename(columns={"Name": "sport_facilities"})
    .drop("Description", axis=1)
)

assert sport.crs == subzones.crs

sport = (
    gpd.sjoin(sport, subzones, how="left", predicate="within")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "sport_facilities"})
)

# %%
# Supermarkets
marts = (
    gpd.read_file(FP_MART)
    .rename(columns={"Name": "supermarkets"})
    .drop("Description", axis=1)
)

assert marts.crs == subzones.crs

marts = (
    gpd.sjoin(marts, subzones, how="left", predicate="within")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "supermarkets"})
)

# %%
# LTA school zones
schzone = (
    gpd.read_file(FP_SCHZONE)
    .rename(columns={"Name": "schzone"})
    .drop("Description", axis=1)
)

assert schzone.crs == subzones.crs

schzone = (
    gpd.sjoin(schzone, subzones, how="left", predicate="intersects")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "schzones"})
)

# %%
# LTA silver zones
silver = (
    gpd.read_file(FP_SILVER)
    .rename(columns={"Name": "silverzones"})
    .drop("Description", axis=1)
)

assert silver.crs == subzones.crs

silver = (
    gpd.sjoin(silver, subzones, how="left", predicate="intersects")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "silverzones"})
)

# %%
# Tourist attractions
tour = (
    gpd.read_file(FP_TOURIST)
    .rename(columns={"Name": "tourist_attraction"})
    .drop("Description", axis=1)
)

assert tour.crs == subzones.crs

tour = (
    gpd.sjoin(tour, subzones, how="left", predicate="intersects")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "tour"})
)

# %% [markdown]
# ### Open-source resources

# %% [markdown]
# #### Schools

# %%
poi = (
    pd.read_json(FP_BUILDINGS)
    .rename(columns={"BUILDING": "poi", "POSTAL": "postcode"})
    .filter(["poi", "postcode"])
    .assign(poi=lambda df: df["poi"].str.lower())
)

schools = poi[
    (poi["poi"].str.contains("primary school"))
    | (poi["poi"].str.contains("secondary school"))
]

del poi
gc.collect()

# Merge schools with postcode to subzone crosswalk
schools = (
    schools.merge(xwalk, how="left", on="postcode")
    .drop("postcode", axis=1)
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "schools"})
)

# %% [markdown]
# #### Transit

# %%
lrts = (
    pd.read_json(FP_LRT)
    .rename(columns={"Possible Locations": "geopayload"})
    .explode("geopayload")
    .query("geopayload==geopayload")
    .assign(postcode=lambda df: [js["POSTAL"] for js in df["geopayload"]])
    .drop_duplicates("Station")
    .merge(xwalk, how="left", on="postcode")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "lrts"})
)

# %%
mrts = (
    pd.read_json(FP_MRT)
    .rename(columns={"Possible Locations": "geopayload"})
    .explode("geopayload")
    .query("geopayload==geopayload")
    .assign(postcode=lambda df: [js["POSTAL"] for js in df["geopayload"]])
    .drop_duplicates("Station")
    .merge(xwalk, how="left", on="postcode")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "mrts"})
)

# %% [markdown]
# #### Distribution of industry groups
# Resources on SSIC:
#
# * https://stats.mom.gov.sg/Pages/Employment-Distribution-and-Employment-Level-by-Industry.aspx\
# * https://www.singstat.gov.sg/standards/standards-and-classifications/ssic
# * https://www.singstat.gov.sg/-/media/files/standards_and_classifications/industrial_classification/ssic2020report.pdf
#
# 3 Biggest "Industry groups:
#
# 1. Manufacturing 10
# 2. construction 41
# 3. Services:
# * wholesale 46
# * retail trade 47
# * Transport & storage 49
# * Land transport & Support svcs 49?

# %%
csv_files = list(walk_through_files(FP_REG_BUSINESS, "csv", fullpath=True))
dfs = []
for file in csv_files:
    df = pd.read_csv(file, low_memory=False)
    dfs.append(df)

df = (
    pd.concat(dfs, ignore_index=True)
    .assign(
        entity_status_description=lambda df: df["entity_status_description"].str.lower()
    )
    .assign(
        entity_status_description=lambda df: df[
            "entity_status_description"
        ].str.replace("live company", "live")
    )
    .query('entity_status_description=="live"')
    .query('uen_issue_date <= "2020-01-01"')
    .rename(columns={"primary_ssic_code": "ssic"})
    .pipe(lambda df: df[["postal_code", "ssic"]])
    .astype({"ssic": "str"})
    .assign(ind=lambda df: df["ssic"].str.zfill(5).str.slice(stop=2))
    .groupby(["postal_code", "ind"])
    .size()
    .reset_index()
    .rename(columns={0: "count", "postal_code": "postcode"})
)

manufact = df[df["ind"] == "10"]
construct = df[df["ind"] == "41"]
services = df[(df["ind"] == "46") | (df["ind"] == "47") | (df["ind"] == "49")]

df.head()

# %%
manufact = (
    manufact.merge(xwalk, how="left", on="postcode")
    .groupby("subzone")["count"]
    .sum()
    .reset_index()
    .rename(columns={"count": "manufacturing"})
)


construct = (
    construct.merge(xwalk, how="left", on="postcode")
    .groupby("subzone")["count"]
    .sum()
    .reset_index()
    .rename(columns={"count": "construction"})
)


services = (
    services.merge(xwalk, how="left", on="postcode")
    .groupby("subzone")["count"]
    .sum()
    .reset_index()
    .rename(columns={"count": "services"})
)

# %% [markdown]
# ### New

# %% [markdown]
# #### Hawkers

# %%
gdf_hawkers = (
    gpd.read_file(FP_HAWKERS)
    .pipe(get_html_table_metadata)
    .query("STATUS!='Under Construction'")
    # keep those before 2020
    .assign(
        completion_date=lambda df_: pd.to_datetime(df_["EST_ORIGINAL_COMPLETION_DATE"], errors='coerce'),
        completion_year=lambda df_: np.where(df_["completion_date"].isna(), 
                                             df_["EST_ORIGINAL_COMPLETION_DATE"], 
                                             df_["completion_date"].dt.year),
    )
    .replace("Pre-War", 1990)
    .assign(completion_year=lambda df_: df_["completion_year"].fillna(1900).apply(int))
    .query('completion_year<2020')
    .reset_index()
    .assign(postcode=lambda df_: df_["ADDRESSPOSTALCODE"].astype("str").str.zfill(6))
    .filter(["postcode"])
)
gdf_hawkers.head()

# %%
hawkers = (
    gdf_hawkers
    .merge(xwalk, how="left", on="postcode")
    .drop("postcode", axis=1)
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "hawkers"})
)
hawkers.head()

# %% [markdown]
# #### Shopping malls

# %%
# https://wiki.openstreetmap.org/wiki/Tag:shop%3Dmall
payload = osmnx.features_from_place("Singapore", tags={'shop': 'mall'})

priority_order = {
   'way': 1,      # Building footprints - most accurate for mall boundaries
   'node': 2,     # Point locations - simple but less detailed
   'relation': 3  # Complex structures - often contain duplicate data from member ways
}

gdf_malls = (
    payload
    .clean_names()
    .reset_index()
    .query("addr_housename==addr_housename | name==name")
    .assign(name=lambda df_: np.where(df_["name"].isna(), df_["addr_housename"], df_["name"]))
    # Dedup
    .assign(priority=lambda df_: df_['element'].map(priority_order))
    .sort_values('priority')
    .drop_duplicates(subset=['name'], keep='first', ignore_index=True)
    .remove_columns('priority')
    # get centroid for PIP
    .assign(centroid=lambda df_: df_['geometry'].centroid)
    .remove_columns("geometry")
    .rename_column("centroid", "geometry")
)
gdf_malls

# %%
assert gdf_malls.crs == subzones.crs
shopping_malls = (
    gpd.sjoin(gdf_malls, subzones, how="left", predicate="intersects")
    .groupby("subzone")
    .size()
    .reset_index()
    .rename(columns={0: "shopping_malls"})    
)
shopping_malls.head()

# %% [markdown]
# ### Merge all

# %%
df_list_toappend = [
    lib,
    marts,
    parks,
    presch,
    schzone,
    silver,
    sport,
    transit,
    tour,
    schools,
    mrts,
    lrts,
    manufact,
    construct,
    services,
    hawkers,
    shopping_malls,
]

# Merge
df = subzones[["subzone"]]

for _pddf in df_list_toappend:
    df = df.merge(_pddf, how="outer", on="subzone")

for _pddf in df_list_toappend:
    del _pddf
    gc.collect()

df.fillna(0, inplace=True)

auto_reduce_mem(df, downcast_float="integer")

# %%
df

# %%
df.to_csv(SAVEPATH, index=False)

# %%
