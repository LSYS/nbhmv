"""Cartesian-expand the analysis panel so every (home, area) pair has a row
for all 91 dates, with inflow=0 on filled rows. Covariates on new rows are
propagated back into the panel.
"""

import janitor  # noqa: F401
import numpy as np
import pandas as pd

PARQUET_IN = "build/cd-panel-labels.parquet"
PARQUET_OUT = "build/cd-panel-ppml.parquet"
DTA_OUT = "build/cd-panel-ppml.dta"

KEY_ORIGIN_DATE = ["basecount", "rain_home"]
KEY_DEST_DATE = ["dest_basecount", "rain_dest"]
INFLOW_LIKE = ["inflow"]

df_panel = pd.read_parquet(PARQUET_IN)

df_pairs = df_panel.select_columns(["home", "area"]).drop_duplicates()
df_dates = pd.DataFrame({"date": np.sort(df_panel["date"].unique())})
df_grid = df_pairs.merge(df_dates, how="cross")

df_expand = (
    df_grid.merge(df_panel, on=["home", "area", "date"], how="left", validate="1:1")
    .assign(
        _zero_filled=lambda d: d["inflow"].isna().astype(np.int8),
        **{col: lambda d, c=col: d[c].fillna(0.0) for col in INFLOW_LIKE},
    )
)

# Broadcast origin-date covariates by (home, date)
df_origin_date = (
    df_panel.select_columns(["home", "date"] + KEY_ORIGIN_DATE)
    .drop_duplicates(subset=["home", "date"])
)
df_expand = (
    df_expand
    .remove_columns(KEY_ORIGIN_DATE)
    .merge(df_origin_date, on=["home", "date"], how="left", validate="m:1")
)

# Broadcast dest-date covariates by (area, date)
df_dest_date = (
    df_panel.select_columns(["area", "date"] + KEY_DEST_DATE)
    .drop_duplicates(subset=["area", "date"])
)
df_expand = (
    df_expand
    .remove_columns(KEY_DEST_DATE)
    .merge(df_dest_date, on=["area", "date"], how="left", validate="m:1")
)

# Remaining cols are time-invariant within each OD pair; fill from existing rows
TIME_VARYING = set(INFLOW_LIKE + KEY_ORIGIN_DATE + KEY_DEST_DATE + ["date"])
_od_invariant = [
    c
    for c in df_expand.columns
    if c not in TIME_VARYING and c not in ("home", "area", "_zero_filled")
]
for _col in _od_invariant:
    df_expand[_col] = (
        df_expand.groupby(["home", "area"])[_col].transform(lambda s: s.ffill().bfill())
    )

nans = df_expand.isna().sum()
nans = nans[nans > 0]
if len(nans):
    print(f"Remaining NaNs ({len(nans)} cols). Largest: {nans.max():,}")
else:
    print("No remaining NaNs.")

df_expand.to_parquet(PARQUET_OUT, index=False)

# save to dta
df_dta = df_expand.assign(date=lambda d: pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d"))

for _col in df_dta.select_dtypes(include="object").columns:
    if df_dta[_col].isna().any():
        df_dta[_col] = df_dta[_col].fillna("")

df_dta.to_stata(DTA_OUT, write_index=False, version=117)
