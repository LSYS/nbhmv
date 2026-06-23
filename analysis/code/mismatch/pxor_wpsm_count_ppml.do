cap log close mismatch
log using $logsavedir/pxor_wpsm_count_ppml.txt, replace text name(mismatch)

set more off
local x mismatch_p25

cap drop inflow_count
gen double inflow_count = inflow * basecount / 100
label var inflow_count "OD flow count"

drop if missing(basecount) | basecount == 0

qui count if inflow_count == 0
local nzero = r(N)
qui count
local ntot = r(N)
local zshare : display %6.4f `nzero' / `ntot'
display "PPML diagnostics: inflow_count zeros = `nzero' / `ntot' (`zshare')"

qui levelsof date, local(__alldates)
local days : word count `__alldates'

eststo clear
forvalues i = 1/5 {
	eststo: ppmlhdfe inflow_count `x', absorb(\$s`i'_ppml) vce($se) tolerance(1e-6)
		estadd local timeFE 	"\multicolumn{1}{c}{\checkmark}"
		estadd local censusPA 	"\multicolumn{1}{c}{\checkmark}"
		estadd local days "\multicolumn{1}{c}{$ `days' $}"
		local clusters: display %9.0fc `e(N_clust1)'
		estadd local clusters "\multicolumn{1}{c}{$ `clusters' $}"
		local nobs: display %9.0fc `e(N)'
		estadd local nobs = "\multicolumn{1}{c}{$ `nobs' $}"
		if `i'==2 estadd local demo "\multicolumn{1}{c}{\checkmark}"
		else if `i'==3 {
			estadd local demo "\multicolumn{1}{c}{\checkmark}"
			estadd local business "\multicolumn{1}{c}{\checkmark}"
		}
		else if `i'==4 {
			estadd local demo "\multicolumn{1}{c}{\checkmark}"
			estadd local business "\multicolumn{1}{c}{\checkmark}"
			estadd local rain "\multicolumn{1}{c}{\checkmark}"
		}
		else if `i'==5 {
			estadd local demo "\multicolumn{1}{c}{\checkmark}"
			estadd local business "\multicolumn{1}{c}{\checkmark}"
			estadd local rain "\multicolumn{1}{c}{\checkmark}"
			estadd local POI "\multicolumn{1}{c}{\checkmark}"
		}
}

esttab using $tabsavedir/pxor-wpsm-count-ppml-frag.tex, ///
	b(%9.4fc) se(%9.4fc) star(* 0.1 ** 0.05 *** 0.01) ///
	obslast noomitted nobase noobs nonumbers nolines nogaps noeqlines nodepvars ///
	nomtitle varwidth(20) modelwidth(8) drop(_cons) coeflabel($coeff_labels) ///
	scalar("timeFE Day fixed effects" "censusPA Census area-by-day fixed effects" ///
		"demo Demographics" "business Businesses" "rain Neighborhood-specific rainfall" ///
		"POI Places of interest" "r2_p Pseudo R$^2$" "days Days" "clusters Clusters" "nobs Observations") ///
	alignment(D{.}{.}{-1}) substitute(\_ _) fragment replace compress

log close mismatch
