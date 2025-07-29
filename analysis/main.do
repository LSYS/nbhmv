cap log close
local myLog "local log ./logs/main"
`myLog'
display "`myLog'"
// log using `log'.smcl


* =========================================================
* Init
* =========================================================
global SCRATCH 0  // if 1, read only 5000 rows (for faster proofing/debugging)
// global READ "yes" // (RE)READ data

// dis "$READ"
// if "$READ" == "yes" {
// 	dis "yrs"
// }

// if ("$READ" == "yes") {
// 	do code/init/set_environment.do
// }
// tictoc tic 1

// do code/init/set_globals.do

// if ("$READ" == "yes") {
// 	do code/init/data_preamble.do
// }
// aa

do code/init/set_environment.do
tictoc tic 1
do code/init/set_globals.do
do code/init/data_preamble.do

// preserve
// keep if _n in 1/5000
*======================================
* Linking scripts to exhibits numbering
*======================================
cap program drop make_fig4a
program define make_fig4a
    do code/mismatch/pxor_wpsm.do
end

cap program drop make_fig4b
program define make_fig4b
    do code/mismatch/pxor_wpsm_r2p_p2r.do
end

cap program drop make_fig6a
program define make_fig6a
	do code/mismatch/pxor_race.do
end

cap program drop make_fig6b
program define make_fig6b
    do code/mismatch/pxor_race_asymmetry.do
end

cap program drop make_fig7
program define make_fig7
	do code/mismatch/pxor_wpsm_ncentral.do
end

cap program drop make_fig8
program define make_fig8
	do code/cutoffs/cutoffs_pxor_wpsm.do
	do code/cutoffs/graph_cutoffs_pxor_wpsm.do
end

cap program drop make_fig9
program define make_fig9
	do code/cutoffs/cutoffs_pxor_wpsm_p2r_r2p.do
	do code/cutoffs/graph_cutoffs_pxor_wpsm_p2r_r2p.do
end

cap program drop make_fig10
program define make_fig10
	do code/policy/visits_increase_by_ethnicmismatch_percentiles.do
	do code/policy/visits_increase_by_ethnicmismatch_c2m_percentiles.do
	do code/policy/graph.do
end

cap program drop make_figD1
program define make_figD1
	do code/cutoffs/cutoffs_pxor_wpsm_ncentral.do
	do code/cutoffs/graph_cutoffs_pxor_wpsm_ncentral.do
end

cap program drop make_tabD1
program define make_tabD1
	do code/additional_specifications/eudist_wpsm.do
end

cap program drop make_tabD5
program define make_tabD5
	do code/additional_specifications/pxor_race_loglog.do
end

cap program drop make_tabD6
program define make_tabD6
	/* Also makes */
	do code/mismatch/pxor_race_ncentral.do
end

cap program drop make_tabD8
program define make_tabD8
	do code/additional_specifications/pxor_wpsm_race.do
end

* =========================================================
* Nbh flows and mismatch
* =========================================================
make_fig4a
make_fig4b

make_fig6a
make_fig6b

make_fig7

// make_fig8

// make_fig9

make_fig10

// make_figD1

make_tabD1
make_tabD5

make_tabD6
make_tabD8


// for preserve before keep if _n < 5000
// restore

* =========================================================
* Nbh flows and mismatch
* =========================================================
tictoc toc 1
beepme 5

// restore
// log close
// `myLog'
// translate `log'.smcl `log'.log linesize(150)
// translate `log'.smcl `log'.pdf
