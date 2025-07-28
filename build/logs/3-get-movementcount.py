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
#     display_name: Python (venv_nbhmv)
#     language: python
#     name: venv_nbhmv
# ---

# +
import os
import pandas as pd
import dask.dataframe as dd

from utilities import walk_through_files, mem_usage

import warnings

warnings.filterwarnings("ignore")

pd.set_option("display.max_rows", 500)

from dask.distributed import LocalCluster, Client

cluster = LocalCluster(n_workers=4)
client = Client(cluster)  # Connect to distributed cluster and override default
client
# -

HOMECOUNT_PATH = os.path.join("intermediate-output", "device-area-maxcount.csv.gz")
ALTERNATE_DUMP_PATH = os.path.join("raw-data", "datadump")
SAVEPATH = os.path.join("intermediate-output", "daily-movecount.csv.gz")

# ### Get daily movement (long format)

# +
# read in device home
home_ddf = (
    dd.read_csv(HOMECOUNT_PATH, compression="gzip")
    .rename(columns={"area_id": "home"})
    .query("count > 30")
)

home_ddf

# +
file_lists = tuple(walk_through_files(ALTERNATE_DUMP_PATH, "csv.gz", fullpath=True))

# Read in records
daily_ddf = dd.read_csv(
    file_lists, compression="gzip", usecols=["device_xid", "date", "area_id"]
)

daily_ddf

# +
# merge
gravity = (
    daily_ddf.merge(home_ddf, how="left", on="device_xid")
    .groupby(["date", "home", "area_id"])
    .size()
    .reset_index()
    .rename(columns={0: "inflow_count"})
    .astype({"home": "int"})
)

gravity
# -

gravity_df = gravity.compute()

gravity_df

mem_usage(gravity_df)

gravity_df.to_csv(SAVEPATH, index=False, compression="gzip")

# How many devices included
df = (
    home_ddf.compute()
    .sort_values("count", ascending=False)
    .drop_duplicates("device_xid")
    .query("count > 30")
)
len(df)

# ### Test output with dummy files

# +
dummy_datadump_ddf = pd.read_csv(os.path.join("tests", "datadump.csv"))
dummy_home_ddf = pd.read_csv(os.path.join("tests", "dummy-home.csv"))

merged_only = dummy_datadump_ddf.merge(dummy_home_ddf, how="left", on="device_xid")

dummy_output = (
    dummy_datadump_ddf.merge(dummy_home_ddf, how="left", on="device_xid")
    .groupby(["date", "home", "area_id"])
    .size()
    .reset_index()
    .rename(columns={0: "inflow_count"})
    .astype({"home": "int"})
)

dummy_output
# -

_usecols = ["home", "area_id"]
merged_only[merged_only["date"] == 1][_usecols]

merged_only[merged_only["date"] == 2][_usecols]

merged_only[merged_only["date"] == 3][_usecols]


