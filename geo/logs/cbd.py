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

df_zone_mapping = pd.read_csv("input/zone_mappings.csv")
df_zone_mapping

# %%
# https://www.ura.gov.sg/Corporate/Guidelines/Urban-Design/Downtown-Core/Downtown-Core-Planning-Area
cbd = [
    "Raffles Place",
    "Cecil",
    "Maxwell",
    "Anson",
    "Tanjong Pagar",
    "Marina Centre",
    "Bayfront Subzone",
    "Clifford Pier",
    "City Hall",
    "Central Subzone",
    "Bugis",
    "Phillip",
]
cbd = [x.lower() for x in cbd]

# %%
df_zone_mapping.query("column=='area'").query("original_name in @cbd").reset_index(
    drop=True
)

# %%
