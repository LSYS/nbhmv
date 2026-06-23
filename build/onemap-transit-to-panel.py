"""Convert OneMap subzone-pair travel times to the analysis panel's numeric IDs.

Input : intermediate-output/transit_time_subzone.csv  (keyed by subzone code, from onemap-transit-time.py)
Output: intermediate-output/transit_time_panel.csv    (keyed by panel origin/dest IDs)
"""

import geopandas as gpd
import janitor
import numpy as np
import pandas as pd

SHP_PATH = "raw-data/master-plan-2014-subzone-boundary-no-sea/master-plan-2014-subzone-boundary-no-sea-shp.zip"

# crosswalk for subzone name -> subzone code
gdf_subzones = gpd.read_file(f"zip://{SHP_PATH}")
name_to_code = dict(
    zip(gdf_subzones["SUBZONE_N"].str.lower().str.strip(), gdf_subzones["SUBZONE_C"])
)
name_to_code["peoples park"] = "OTSZ02"
name_to_code["marina east mp"] = "MESZ01"

# crosswalk for subzone code -> panel numeric ID
df_xwalk = pd.read_csv("intermediate-output/citydata-subzones.csv").assign(
    subzone_code=lambda df_: df_["subzone"].str.lower().str.strip().map(name_to_code)
)
code_to_id = dict(zip(df_xwalk["subzone_code"], df_xwalk["areaid"]))

# map the travel times onto panel IDs
df_panel = (
    pd.read_csv("intermediate-output/transit_time_subzone.csv")
    .dropna(subset=["transit_time_sec"])
    .assign(
        origin=lambda df_: df_["Subzone Code_o"].map(code_to_id),
        dest=lambda df_: df_["Subzone Code_d"].map(code_to_id),
    )
    .dropna(subset=["origin", "dest"])
    .astype({"origin": int, "dest": int})
    .assign(ln_transit_time=lambda df_: np.log(df_["transit_time_sec"]))
    .select_columns(["origin", "dest", "transit_time_sec", "ln_transit_time"])
    .sort_values(["origin", "dest"])
    .reset_index(drop=True)
)

df_panel.to_csv("intermediate-output/transit_time_panel.csv", index=False)
print(f"Wrote {len(df_panel):,} OD pairs to intermediate-output/transit_time_panel.csv")
