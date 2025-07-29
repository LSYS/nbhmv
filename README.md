# 📦 Neighborhood Mismatch and Visits

This study combines GPS traces with census and housing microtransactions to examine how socioeconomic mismatches shape daily movements in Singapore.
We measure mismatch as a difference in income levels or ethnic composition, which naturally decomposes into the directional components of mismatch.
We find stark asymmetries.
Income-based segregation is driven by a lack of visits from richer to poorer neighborhoods, while ethnic-based segregation is driven by a lack of visits from majority- to minority-ethnic neighborhoods.
We take our estimates to a counterfactual analysis of an extant ethnic residential integration policy. The findings show that the policy’s effect on fostering cross-neighborhood flows would have been three times smaller without accounting for directional asymmetries in ethnic mismatch.

## 📂 Repo Structure and Scripts

```bash
.
├── analysis
│  ├── code
│  ├── logs
│  ├── cd-panel.csv
│  ├── main.do
│  └── readme.md
├── assets
│  ├── build-pipeline.mmd
│  ├── build-pipeline.png
│  ├── build-pipeline.svg
│  ├── requirements-stata.txt
│  └── requirements.txt
├── build
│  ├── aux-notebooks
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
│  ├── 5-compile-POI-count.ipynb
│  ├── 6a-clean-housetype.ipynb
│  ├── 6b-map-weather.ipynb
│  ├── 7-merge.ipynb
│  ├── cd-panel.csv
│  ├── Makefile
│  ├── readme.md
│  └── utilities.py
├── geo
│  ├── logs
│  ├── out
│  ├── bootstrap-r2.ipynb
│  ├── borders.ipynb
│  ├── choropleth-devices.ipynb
│  ├── choropleth-income.ipynb
│  ├── choropleth-price.ipynb
│  ├── get-devicecount-subzone-day.ipynb
│  ├── Makefile
│  ├── pa-price.ipynb
│  ├── ping-variation.ipynb
│  ├── regplot_wpsm_income_pa.do
│  └── utilities.py -> ../build/utilities.py
├── results
│  ├── figures
│  ├── tables
│  └── README.md
├── .gitignore
├── LICENSE
├── Makefile
└── README.md
```

## 🔧 Build


Set up the `venv` using 

```bash
make setup
```

which uses dependencies listed in [`requirements.txt`](https://github.com/LSYS/nbhmv/blob/main/assets/requirements.txt).

To build the complete dataset:

![Build dependency graph](./assets/build-pipeline.png)

```bash
make data
```

using the [`Makefile`](https://github.com/LSYS/nbhmv/blob/main/build/Makefile) and [`runpynb`](https://pypi.org/project/runpynb/) to execute relevant notebooks in sequence in the `venv`.


See [`./build`](https://github.com/LSYS/nbhmv/tree/main/build) for more details.


## 📊 Analysis

`ssc` dependencies are listed in a [requirements-stata.txt](https://github.com/LSYS/nbhmv/blob/main/assets/requirements-stata.txt) and custom dependencies are in [`./analysis/code/ado`](https://github.com/LSYS/nbhmv/tree/main/analysis/code/ado).