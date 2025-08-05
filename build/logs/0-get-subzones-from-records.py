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

from utilities import get_subzone_name, walk_through_files

RECORDS_PATH = os.path.join("raw-data", "sg_subzones_devices", "sg_subzones_devices")
SAVEPATH = os.path.join("intermediate-output", "citydata-subzones.csv")

# %%
subzones = set()

for filename in walk_through_files(RECORDS_PATH, "csv.gz"):
    subzone = get_subzone_name(filename)
    subzones.add(subzone)

# %%
df = (
    pd.DataFrame(subzones, columns=["subzone"])
    .sort_values("subzone", ignore_index=True)
    .assign(subzone=lambda x: x["subzone"].str.title())
    .assign(areaid=lambda x: x.index)
)

# %%
df

# %%
df.to_csv(SAVEPATH, index=False)
