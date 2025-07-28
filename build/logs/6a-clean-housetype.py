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

# +
import os
import pandas as pd
import gc

FP_DWELLING = os.path.join(
    "raw-data",
    "singapore-residents-by-subzone-and-type-of-dwelling-2011-2019",
    "planning-area-subzone-age-group-sex-and-type-of-dwelling-june-2011-2019.csv",
)
SAVEPATH = os.path.join("intermediate-output", "htype.csv")
# -

# **Data notes**:
# 1. Drop
# * HUDC Flats (excluding those privatised)
# * Others
# * from both numerator and denominator.
# 2. Group
# * Landed Properties
# * Condominiums and Other Apartments
# * as "Private" houses.
# 3. For year=2019 only

# + code_folding=[]
# Read in
area_rm12 = (
    pd.read_csv(
        FP_DWELLING, usecols=["subzone", "type_of_dwelling", "resident_count", "year"]
    )
    .query("year==2019")
    .drop("year", axis=1)
    .rename(
        columns={"type_of_dwelling": "htype", "planning_area": "pa", "subzone": "area"}
    )
    .query('htype!="HUDC Flats (excluding those privatised)"')
    .query('htype!="Others"')
    .assign(area=lambda df: df["area"].str.lower().str.strip())
    .assign(htype=lambda df: df["htype"].replace({"Landed Properties": "private"}))
    .assign(
        htype=lambda df: df["htype"].replace(
            {"Condominiums and Other Apartments": "private"}
        )
    )
    .groupby(["area", "htype"])
    .sum()
    .reset_index()
    .query('htype=="HDB 1- and 2-Room Flats"')
    .drop("htype", axis=1)
    .rename(columns={"resident_count": "rm12"})
)
area_rm3 = (
    pd.read_csv(
        FP_DWELLING, usecols=["subzone", "type_of_dwelling", "resident_count", "year"]
    )
    .query("year==2019")
    .drop("year", axis=1)
    .rename(
        columns={"type_of_dwelling": "htype", "planning_area": "pa", "subzone": "area"}
    )
    .query('htype!="HUDC Flats (excluding those privatised)"')
    .query('htype!="Others"')
    .assign(area=lambda df: df["area"].str.lower().str.strip())
    .assign(htype=lambda df: df["htype"].replace({"Landed Properties": "private"}))
    .assign(
        htype=lambda df: df["htype"].replace(
            {"Condominiums and Other Apartments": "private"}
        )
    )
    .groupby(["area", "htype"])
    .sum()
    .reset_index()
    .query('htype=="HDB 3-Room Flats"')
    .drop("htype", axis=1)
    .rename(columns={"resident_count": "rm3"})
)
area_rm4 = (
    pd.read_csv(
        FP_DWELLING, usecols=["subzone", "type_of_dwelling", "resident_count", "year"]
    )
    .query("year==2019")
    .drop("year", axis=1)
    .rename(
        columns={"type_of_dwelling": "htype", "planning_area": "pa", "subzone": "area"}
    )
    .query('htype!="HUDC Flats (excluding those privatised)"')
    .query('htype!="Others"')
    .assign(area=lambda df: df["area"].str.lower().str.strip())
    .assign(htype=lambda df: df["htype"].replace({"Landed Properties": "private"}))
    .assign(
        htype=lambda df: df["htype"].replace(
            {"Condominiums and Other Apartments": "private"}
        )
    )
    .groupby(["area", "htype"])
    .sum()
    .reset_index()
    .query('htype=="HDB 4-Room Flats"')
    .drop("htype", axis=1)
    .rename(columns={"resident_count": "rm4"})
)
area_rm5 = (
    pd.read_csv(
        FP_DWELLING, usecols=["subzone", "type_of_dwelling", "resident_count", "year"]
    )
    .query("year==2019")
    .drop("year", axis=1)
    .rename(
        columns={"type_of_dwelling": "htype", "planning_area": "pa", "subzone": "area"}
    )
    .query('htype!="HUDC Flats (excluding those privatised)"')
    .query('htype!="Others"')
    .assign(area=lambda df: df["area"].str.lower().str.strip())
    .assign(htype=lambda df: df["htype"].replace({"Landed Properties": "private"}))
    .assign(
        htype=lambda df: df["htype"].replace(
            {"Condominiums and Other Apartments": "private"}
        )
    )
    .groupby(["area", "htype"])
    .sum()
    .reset_index()
    .query('htype=="HDB 5-Room and Executive Flats"')
    .drop("htype", axis=1)
    .rename(columns={"resident_count": "rm5"})
)
area_private = (
    pd.read_csv(
        FP_DWELLING, usecols=["subzone", "type_of_dwelling", "resident_count", "year"]
    )
    .query("year==2019")
    .drop("year", axis=1)
    .rename(
        columns={"type_of_dwelling": "htype", "planning_area": "pa", "subzone": "area"}
    )
    .query('htype!="HUDC Flats (excluding those privatised)"')
    .query('htype!="Others"')
    .assign(area=lambda df: df["area"].str.lower().str.strip())
    .assign(htype=lambda df: df["htype"].replace({"Landed Properties": "private"}))
    .assign(
        htype=lambda df: df["htype"].replace(
            {"Condominiums and Other Apartments": "private"}
        )
    )
    .groupby(["area", "htype"])
    .sum()
    .reset_index()
    .query('htype=="private"')
    .drop("htype", axis=1)
    .rename(columns={"resident_count": "private"})
)
area_tt = (
    pd.read_csv(
        FP_DWELLING,
        usecols=[
            "planning_area",
            "subzone",
            "type_of_dwelling",
            "resident_count",
            "year",
        ],
    )
    .query("year==2019")
    .drop("year", axis=1)
    .rename(
        columns={"type_of_dwelling": "htype", "planning_area": "pa", "subzone": "area"}
    )
    .query('htype!="HUDC Flats (excluding those privatised)"')
    .query('htype!="Others"')
    .assign(area=lambda df: df["area"].str.lower().str.strip())
    .assign(htype=lambda df: df["htype"].replace({"Landed Properties": "private"}))
    .assign(
        htype=lambda df: df["htype"].replace(
            {"Condominiums and Other Apartments": "private"}
        )
    )
    .groupby(["pa", "area"])
    .sum()
    .reset_index()
)
htype = (
    area_tt.merge(area_private, how="left", on="area", validate="1:1")
    .merge(area_rm12, how="left", on="area", validate="1:1")
    .merge(area_rm3, how="left", on="area", validate="1:1")
    .merge(area_rm4, how="left", on="area", validate="1:1")
    .merge(area_rm5, how="left", on="area", validate="1:1")
)
del area_tt, area_private, area_rm12, area_rm3, area_rm4, area_rm5
gc.collect()

# + code_folding=[]
for x in ["private", "rm12", "rm3", "rm4", "rm5"]:
    htype[x] = 100 * (htype[x] / htype["resident_count"])
# -

htype

htype.to_csv(SAVEPATH, index=False)


