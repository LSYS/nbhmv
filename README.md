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
│  ├── code
│  ├── logs
│  ├── cd-panel.csv
│  ├── main-spare.do
│  └── main.do
├── assets
│  ├── build-pipeline.mmd
│  ├── build-pipeline.png
│  ├── build-pipeline.svg
│  ├── requirements-stata.txt
│  └── requirements.txt
├── build
│  ├── aux-notebooks
│  ├── cache
│  ├── intermediate-output
│  ├── logs
│  ├── preprocessed-data
│  ├── raw-data
│  ├── tests
│  ├── 0-get-subzones-from-records.ipynb
│  ├── 1-get-IDs.ipynb
│  ├── 2-get-devicehome.ipynb
│  ├── 3-get-movementcount.ipynb
│  ├── 4-postal_to_2014subzonename.ipynb
│  ├── 5-compile-POI-count-Copy1.ipynb
│  ├── 5-compile-POI-count.ipynb
│  ├── 6a-clean-housetype.ipynb
│  ├── 6b-map-weather.ipynb
│  ├── 7-merge.ipynb
│  ├── cd-panel.csv
│  ├── Makefile
│  ├── readme.md
│  └── utilities.py
├── results
│  ├── figures
│  ├── logs
│  ├── tables
│  └── README.md
├── venv_nbhmv
├── .gitignore
├── LICENSE
├── Makefile
└── README.md
```

## 🔧 Build

To build the complete dataset, use

```bash
make data
```
See [https://github.com/LSYS/nbhmv/blob/main/build/Makefile](https://github.com/LSYS/nbhmv/blob/main/build/Makefile), which uses [runpynb](https://pypi.org/project/runpynb/) to execute relevant notebooks in sequence in a `venv` (see dependencies in [requirements.txt](https://github.com/LSYS/nbhmv/blob/main/assets/requirements.txt)):

![Build dependency graph](./assets/build-pipeline.png)

## 📊 Analysis

`ssc` dependencies are listed in [requirements-stata.txt](https://github.com/LSYS/nbhmv/blob/main/assets/requirements-stata.txt) and custom dependencies are in [`./analysis/code/ado`](https://github.com/LSYS/nbhmv/tree/main/analysis/code/ado)