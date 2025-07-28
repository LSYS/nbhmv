# ---
# jupyter:
#   jupytext:
#     formats: ipynb,logs//py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# ### this file generates the postal code to subzone name/code crosswalk,
# ### postal_to_kmlno_xwalk.csv

# +
import pandas as pd
import geopandas as gpd

import fiona

fiona.drvsupport.supported_drivers["KML"] = "rw"

buildings_df = pd.read_json("./raw-data/buildings.json")
buildings_df = gpd.GeoDataFrame(
    buildings_df,
    geometry=gpd.points_from_xy(buildings_df.LONGTITUDE, buildings_df.LATITUDE),
)


subzones = gpd.read_file(
    "./raw-data/master-plan-2014-subzone-boundary-no-sea/master-plan-2014-subzone-boundary-no-sea-kml.zip"
)


# -

def brute_force_check(point, subzone_df):

    try:
        return subzone_df[
            subzone_df.geometry.map(lambda subzone: subzone.contains(point))
        ].values[0][0]

    except IndexError:
        # not in subzone
        return None


# %%time
buildings_df["subzone_name"] = buildings_df.geometry.apply(
    lambda point: brute_force_check(point, subzones)
)

# + code_folding=[]
if True:
    buildings_df[["POSTAL", "subzone_name"]].to_csv(
        "./intermediate-output/fixed_postal_subzone_xwalk.csv", index=False
    )
# -

buildings_df


