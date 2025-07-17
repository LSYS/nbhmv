# 📦 Neighborhood Mismatch and Visits

This study combines GPS traces with census and housing microtransactions to examine how socioeconomic mismatches shape daily movements in Singapore.
We measure mismatch as a difference in income levels or ethnic composition, which naturally decomposes into the directional components of mismatch.
We find stark asymmetries.
Income-based segregation is driven by a lack of visits from richer to poorer neighborhoods, while ethnic-based segregation is driven by a lack of visits from majority- to minority-ethnic neighborhoods.
We take our estimates to a counterfactual analysis of an extant ethnic residential integration policy. The findings show that the policy’s effect on fostering cross-neighborhood flows would have been three times smaller without accounting for directional asymmetries in ethnic mismatch.

## 📂 Notable Files and Structure

```bash
.
├── analysis
├── assets
│  └── requirements.txt
├── build
│  ├── raw-data
│  ├── 0a-get-devicecount-subzone-day.ipynb
│  ├── 0b-get-subzones-from-records.ipynb
│  ├── 1-get-device-appearances-count.ipynb
│  ├── 2-get-IDs.ipynb
│  ├── 3-get-devicehome.ipynb
│  ├── 4-postal_to_2014subzonename.ipynb
│  ├── 5a-clean-housetype.ipynb
│  ├── 5b-compile-POI-count.ipynb
│  ├── 5c-map-weather.ipynb
│  ├── 5d-get-movementcount.ipynb
│  ├── 6-merge.ipynb
│  ├── readme.md
│  └── utilities.py
├── .gitignore
├── LICENSE
├── Makefile
└── README.md
```