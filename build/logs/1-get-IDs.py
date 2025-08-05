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
import dask.dataframe as dd
import pandas as pd
from utilities import save_df_in_chunks

import warnings

warnings.filterwarnings("ignore")

from dask.distributed import LocalCluster, Client

cluster = LocalCluster(n_workers=6)
client = Client(cluster)  # Connect to distributed cluster and override default
client

# %%
SAVEPATH = os.path.join("intermediate-output", "deviceID-list")
DEVICE_COUNT_PATH = os.path.join(
    "intermediate-output", "tt-appearances-areadate", "*.csv.gz"
)

# %%
# Get device ID dict
devices_ddf = (
    dd.read_csv(DEVICE_COUNT_PATH, compression="gzip", usecols=["deviceID"])
).compute()

devices_ddf.sort_values("deviceID", inplace=True)
devices_ddf.reset_index(drop=True, inplace=True)
devices = dict(zip(devices_ddf["deviceID"], devices_ddf.index))
# https://stackoverflow.com/questions/19201290/how-to-save-a-dictionary-to-a-file/32216025
# np.save(os.path.join('intermediate-files', 'device-xid.npy'), devices)

# %%
devices = (
    pd.DataFrame.from_dict(devices, orient="index")
    .reset_index()
    .rename(columns={"index": "hashid", 0: "xid"})
    .astype({"xid": "int"})
)

# %%
devices

# %%
save_df_in_chunks(
    devices, SAVEPATH, 5, "deviceID-list-chunk", "csv.gz", compression="gzip"
)

# %%
