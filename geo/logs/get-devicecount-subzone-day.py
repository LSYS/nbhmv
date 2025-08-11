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
from tqdm.notebook import tqdm

from utilities import get_date, walk_through_files, get_subzone_name_from_dir

pd.set_option("display.max_rows", 500)

RECORDS_PATH = "input/sg_subzones_devices"
SAVEPATH = "out/devicecount-subzone-day.csv"

# %%
ix = 0
dict_placeholder = {}


for filepath in tqdm(walk_through_files(RECORDS_PATH, "csv.gz", fullpath=True)):

    # parse file name to get date and loc
    try:
        subzone = get_subzone_name_from_dir(filepath)
        date = get_date(filepath)
    except ValueError:
        print(filepath)

    # read into df
    _df = pd.read_csv(
        filepath,
        compression="gzip",
        names=["id", "os"],
        dtype={"id": "object", "os": "int8"},
    )

    android_count = len(_df[_df["os"] == 0])
    ios_count = len(_df[_df["os"] == 1])

    # init list and add to dict
    dict_placeholder[ix] = [subzone, date, android_count, ios_count]

    ix += 1

# %%
df = (
    pd.DataFrame.from_dict(
        dict_placeholder,
        orient="index",
        columns=["subzone", "date", "android_count", "ios_count"],
    )
    .astype(
        {
            "subzone": "object",
            "date": "datetime64[ns]",
            "android_count": "int",
            "ios_count": "int",
        }
    )
    .drop_duplicates(["subzone", "date"], ignore_index=True)
    .sort_values(["date", "subzone"], ignore_index=True)
)

df.head(10)

# %%
(
    df.groupby("subzone")[["android_count", "ios_count"]]
    .sum()
    .assign(ios_android_ratio=lambda df_: df_["ios_count"] / df_["android_count"])
    .sort_values(["ios_android_ratio"], ascending=False)
)

# %%
df.to_csv(SAVEPATH, index=False)

# %%
