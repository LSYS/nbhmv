`do` files for results using different percentile cutoffs will take hourrs (~24hrs for `./code/cutoffs/cutoffs_pxor_wpsm.do`).

## Structure
```
.
├── code
│  ├── ado
│  ├── cutoffs
│  ├── init
│  ├── mismatch
│  └── policy
├── logs
├── cd-panel.csv
├── main.do
└── readme.md
```


## Runtime Warnings ⚠️
- `do` files for results using different percentile cutoffs will take hours to complete
- E.g., `./code/cutoffs/cutoffs_pxor_wpsm.do` takes approximately **24 hours** to run

## Setup Requirements
`ssc` dependencies are listed in a [requirements-stata.txt](https://github.com/LSYS/nbhmv/blob/main/assets/requirements-stata.txt) and custom dependencies are in [`./analysis/code/ado`](https://github.com/LSYS/nbhmv/tree/main/analysis/code/ado).
