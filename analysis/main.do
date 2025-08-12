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

// do code/init/set_environment.do
// tictoc tic 1
// do code/init/set_globals.do
// do code/init/data_preamble.do

*======================================
* Linking scripts to exhibits numbering
*======================================
cap program drop make_fig4a
program define make_fig4a
	/* Also makes Tab 2 */
    do code/mismatch/pxor_wpsm.do
end

cap program drop make_fig4b
program define make_fig4b
	/* Also makes Tab C1 */
    do code/mismatch/pxor_wpsm_r2p_p2r.do
end

cap program drop make_fig6a
program define make_fig6a
	/* Also makes Tab 2 */
	do code/mismatch/pxor_race.do
end

cap program drop make_fig6b
program define make_fig6b
	/* Also makes Tab C3 */
    do code/mismatch/pxor_race_asymmetry.do
end

cap program drop make_fig7
program define make_fig7
	/* Also makes Tab C2 */
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


cap program drop make_top25p
program define make_top25p
	make_figD1
	make_figD2
	make_figD3
end

cap program drop make_figD1
program define make_figD1
	/* Also makes Tab D1 */
	do code/mismatch_top25p/top25p_pxor_wpsm.do
end

cap program drop make_figD2
program define make_figD2
	* Also makes Tab D2 */
	do code/mismatch_top25p/top25p_pxor_wpsm_r2p_p2r.do
end

cap program drop make_figD3
program define make_figD3
	* Also makes Tab D3 */
	do code/mismatch_top25p/top25p_pxor_wpsm_ncentral.do
end

cap program drop make_robust
program define make_robust
	make_tabE1
	make_tabE2
	make_tabE3
	make_tabE4
end

cap program drop make_figE1
program define make_figE1
	do code/cutoffs/cutoffs_pxor_wpsm_ncentral.do
	do code/cutoffs/graph_cutoffs_pxor_wpsm_ncentral.do
end

cap program drop make_tabE1
program define make_tabE1
	do code/additional_specifications/eudist_wpsm.do
end

cap program drop make_tabE2
program define make_tabE2
	do code/additional_specifications/pxor_race_loglog.do
end

cap program drop make_tabE3
program define make_tabE3
	/* Also makes Fig E2 */
	do code/mismatch/pxor_race_ncentral.do
end

cap program drop make_tabE4
program define make_tabE4
	do code/additional_specifications/pxor_wpsm_race.do
end

cap program drop make_exc_emp
program define make_exc_emp
	make_tabE5
	make_tabE6
	make_tabE7
	make_tabE8
	make_tabE9
	make_tabE10
end

cap program drop make_tabE5
program define make_tabE5
	do code/exc_majorempcenters/exc_majorempcenters_pxor_wpsm.do
end

cap program drop make_tabE6
program define make_tabE6
	do code/exc_majorempcenters/exc_majorempcenters_pxor_wpsm_r2p_p2r.do
end

cap program drop make_tabE7
program define make_tabE7
	do code/exc_majorempcenters/exc_majorempcenters_pxor_wpsm_ncentral.do
end

cap program drop make_tabE8
program define make_tabE8
	do code/exc_majorempcenters/exc_majorempcenters_pxor_race.do
end

cap program drop make_tabE9
program define make_tabE9
	do code/exc_majorempcenters/exc_majorempcenters_pxor_race_asymmetry.do
end

cap program drop make_tabE10
program define make_tabE10
	do code/exc_majorempcenters/exc_majorempcenters_pxor_race_ncentral.do
end

cap program drop make_dow
program define make_dow
	make_tabE11_E12
	make_tabE13_E14
	make_tabE15_E16
	make_tabE17_E18
	make_tabE19_E20
	make_tabE21_E22
end

cap program drop make_tabE11_E12
program define make_tabE11_E12
	do code/dow/dow_pxor_wpsm.do
end

cap program drop make_tabE13_E14
program define make_tabE13_E14
	do code/dow/dow_pxor_wpsm_r2p_p2r.do
end

cap program drop make_tabE15_E16
program define make_tabE15_E16
	do code/dow/dow_pxor_wpsm_ncentral.do
end

cap program drop make_tabE17_E18
program define make_tabE17_E18
	do code/dow/dow_pxor_race.do
end

cap program drop make_tabE19_E20
program define make_tabE19_E20
	do code/dow/dow_pxor_race_asymmetry.do
end

cap program drop make_tabE21_E22
program define make_tabE21_E22
	do code/dow/dow_pxor_race_ncentral.do
end


cap program drop make_adj_filter
program define make_adj_filter
	make_tabE23
	make_tabE24
	make_tabE25
	make_tabE26
	make_tabE27
	make_tabE28
end

cap program drop make_tabE23
program define make_tabE23
	do code/adjacency_filter/adjfilter_pxor_wpsm.do
end

cap program drop make_tabE24
program define make_tabE24
	do code/adjacency_filter/adjfilter_pxor_wpsm_r2p_p2r.do
end

cap program drop make_tabE25
program define make_tabE25
	do code/adjacency_filter/adjfilter_pxor_wpsm_ncentral.do
end

cap program drop make_tabE26
program define make_tabE26
	do code/adjacency_filter/adjfilter_pxor_race.do
end

cap program drop make_tabE27
program define make_tabE27
	do code/adjacency_filter/adjfilter_pxor_race_asymmetry.do
end

cap program drop make_tabE28
program define make_tabE28
	do code/adjacency_filter/adjfilter_pxor_race_ncentral.do
end


cap program drop make_tabH1
program define make_tabH1
	do code/additional_specifications/wpsm.do
end

cap program drop make_tabH2
program define make_tabH2
	do code/additional_specifications/cny_wpsm.do
end

* =========================================================
* Nbh flows and mismatch
* =========================================================
// make_fig4a
// make_fig4b

// make_fig6a
// make_fig6b

// make_fig7
// make_fig10

// make_robust
// make_top25p
// make_exc_emp
// make_dow
// make_adj_filter

// make_tabH1
// make_tabH2


* Cutoffs
// make_fig8
// make_fig9
// make_figE1

make_tabE24

* =========================================================
* Nbh flows and mismatch
* =========================================================
tictoc toc 1
beepme 5

// log close
// `myLog'
// translate `log'.smcl `log'.log linesize(150)
// translate `log'.smcl `log'.pdf
