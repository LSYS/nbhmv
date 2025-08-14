# Analyses

`main.do` runs all `do` scripts in [`./code`](https://github.com/LSYS/nbhmv/tree/main/analysis/code).

![Build dependency graph](../assets/analysis.png)

## Code structure
```
.
├── code
│  ├── additional_specifications
│  │  ├── cny_wpsm.do
│  │  ├── eudist_wpsm.do
│  │  ├── pxor_race_loglog.do
│  │  ├── pxor_wpsm_race.do
│  │  ├── pxor_wpsm_race_decomp.do
│  │  └── wpsm.do
│  ├── adjacency_filter
│  │  ├── adjfilter_pxor_race.do
│  │  ├── adjfilter_pxor_race_asymmetry.do
│  │  ├── adjfilter_pxor_race_ncentral.do
│  │  ├── adjfilter_pxor_wpsm.do
│  │  ├── adjfilter_pxor_wpsm_ncentral.do
│  │  └── adjfilter_pxor_wpsm_r2p_p2r.do
│  ├── ado
│  │  ├── assert_macros.ado
│  │  ├── beepme.ado
│  │  ├── corr_pval.ado
│  │  ├── encvar.ado
│  │  ├── get_pval.ado
│  │  ├── hettests.ado
│  │  ├── onesidetest.ado
│  │  ├── README.md
│  │  ├── run_es.ado
│  │  ├── savefig.ado
│  │  ├── setup.ado
│  │  ├── storespecs.ado
│  │  ├── tables2in1.ado
│  │  ├── TestStatSig.ado
│  │  ├── tictoc.ado
│  │  └── txt2macro.ado
│  ├── cutoffs
│  │  ├── out
│  │  ├── cutoffs_pxor_wpsm.do
│  │  ├── cutoffs_pxor_wpsm_ncentral.do
│  │  ├── cutoffs_pxor_wpsm_p2r_r2p.do
│  │  ├── graph_cutoffs_pxor_wpsm.do
│  │  ├── graph_cutoffs_pxor_wpsm_ncentral.do
│  │  ├── graph_cutoffs_pxor_wpsm_p2r_r2p.do
│  │  └── graph_settings.do
│  ├── dow
│  │  ├── dow_pxor_race.do
│  │  ├── dow_pxor_race_asymmetry.do
│  │  ├── dow_pxor_race_ncentral.do
│  │  ├── dow_pxor_wpsm.do
│  │  ├── dow_pxor_wpsm_ncentral.do
│  │  └── dow_pxor_wpsm_r2p_p2r.do
│  ├── exc_majorempcenters
│  │  ├── exc_majorempcenters_pxor_race.do
│  │  ├── exc_majorempcenters_pxor_race_asymmetry.do
│  │  ├── exc_majorempcenters_pxor_race_ncentral.do
│  │  ├── exc_majorempcenters_pxor_wpsm.do
│  │  ├── exc_majorempcenters_pxor_wpsm_ncentral.do
│  │  └── exc_majorempcenters_pxor_wpsm_r2p_p2r.do
│  ├── init
│  │  ├── data_preamble.do
│  │  ├── set_environment.do
│  │  └── set_globals.do
│  ├── mismatch
│  │  ├── pxor_race.do
│  │  ├── pxor_race_asymmetry.do
│  │  ├── pxor_race_ncentral.do
│  │  ├── pxor_wpsm.do
│  │  ├── pxor_wpsm_ncentral.do
│  │  └── pxor_wpsm_r2p_p2r.do
│  ├── mismatch_top25p
│  │  ├── top25p_exc_majorempcenters_pxor_wpsm_ncentral.do
│  │  ├── top25p_pxor_wpsm.do
│  │  ├── top25p_pxor_wpsm_ncentral.do
│  │  └── top25p_pxor_wpsm_r2p_p2r.do
│  └── policy
│     ├── out
│     ├── graph.do
│     ├── visits_increase_by_ethnicmismatch_c2m_percentiles.do
│     └── visits_increase_by_ethnicmismatch_percentiles.do
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
