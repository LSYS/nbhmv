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
from tqdm.notebook import tqdm
import time
import janitor 
from utilities import get_date, get_subzone_name, walk_through_files

import warnings

warnings.filterwarnings("ignore")
# -

RECORDS_PATH = os.path.join("raw-data", "sg_subzones_devices", "sg_subzones_devices")
SAVEPATH = os.path.join("intermediate-output", "device-area-maxcount.csv.gz")
SUBZONE_PATH = os.path.join("intermediate-output", "citydata-subzones.csv")
ALTERNATE_DUMP_PATH = os.path.join("raw-data", "datadump")
DEVICE_ID_DICT_PATH = os.path.join(
    "intermediate-output", "deviceID-list", "deviceID-list-chunk*.csv.gz"
)

# #### Replicate datadump with (integer) IDs

if False:

    # Get device ID dict DEVICE_ID_DICT_PATH
    devices = (dd.read_csv(DEVICE_ID_DICT_PATH, compression="gzip")).compute()
    devices = dict(zip(devices["hashid"], devices["xid"]))

    # Get area ID dict
    subzones = pd.read_csv(SUBZONE_PATH)
    subzones = dict(zip(subzones["subzone"].str.lower(), subzones["areaid"]))

    file_lists = tuple(walk_through_files(RECORDS_PATH, "csv.gz", returnboth=True))

    # Create alternate datadump
    for filepath, filename in tqdm(file_lists):
        # open file
        _date = get_date(filename)
        # https://stackoverflow.com/questions/19801727/convert-datetime-to-unix-timestamp-and-convert-it-back-in-python
        _date = time.mktime(_date.timetuple())
        _subzone = get_subzone_name(filename)

        df = (
            pd.read_csv(
                os.path.join(filepath, filename),
                compression="gzip",
                names=["device", "ios"],
            )
            .assign(date=_date)
            .assign(area_id=subzones[_subzone])
            #           .assign(device=lambda x: [devices[device] for device in x['device']])
            .assign(device=lambda x: [devices[device] for device in x["device"]])
            .rename(columns={"device": "device_xid"})
            .astype(
                {"area_id": "int", "device_xid": "int", "ios": "int", "date": "int"}
            )
        ).to_csv(
            os.path.join(ALTERNATE_DUMP_PATH, filename), index=False, compression="gzip"
        )

# #### Get max count

file_lists = tuple(walk_through_files(ALTERNATE_DUMP_PATH, "csv.gz", fullpath=True))
len(file_lists)

# +
df = (pd.concat([pd.read_csv(f, compression='gzip', usecols=['device_xid', 'area_id']) 
                 for f in file_lists])
      .groupby(['device_xid', 'area_id']).size()
      .reset_index()
      .rename_column(0, 'count')
      .loc[lambda x: x.groupby('device_xid')['count'].transform('max') == x['count']]
#       .sort_values(["device_xid", "area_id", "count"], ascending=(False, False, True), ignore_index=True)
     )

df
# -

df.to_csv(SAVEPATH, index=False, compression="gzip")

# #### Testing output using dummyfiles/datadump.csv
#
# * contains only 3 devices, 3 areas, over 3 dates
#
# * device 1's home is area 1 (appears in area 1 three times, and area 3 once)
# * device 2's home is a tie between area 1 and 2 (appears in area 1 and 2 twice)
# * device 3 is one of those that only appears once in the sample, still, output should return "home" as that one area 3 it appeared in.

DUMMY_PATH = os.path.join("tests", "datadump.csv")
dummy = pd.read_csv(DUMMY_PATH)
dummy

# +
dummyhome = (
    dummy.groupby(["device_xid", "area_id"])
    .size()
    .reset_index()
    .rename(columns={0: "count"})
    .astype({"count": "int", "area_id": "int", "device_xid": "int"})
    .loc[lambda x: x.groupby("device_xid")["count"].transform(max) == x["count"]]
    .rename(columns={"area_id": "home"})
)

dummyhome
# -

dummyhome.to_csv(os.path.join("tests", "dummy-home.csv"), index=False)
