cap log close cutoffs
log using $logsavedir/cutoffs_pxor_wpsm_p2r_r2p.txt, replace text name(cutoffs)

set more off

preserve

local LOW_RANGE = 1
local UPP_RANGE = 99
local FILENAME mismatch-wpsm-p2r-r2p
local FILEPATH ./code/cutoffs/out

* del exisiting file
cap erase `FILEPATH'/`FILENAME'.dta

tictoc tic 99

price_tier_cache, origin(wpsm_home) dest(wpsm_dest) ///
                  percentiles(`LOW_RANGE'/`UPP_RANGE')


quietly {
forvalues cutoff = `LOW_RANGE'/`UPP_RANGE' {
	noisily dis in green "Working on `cutoff' of range `LOW_RANGE'/`UPP_RANGE' "

	* Generate new dummies for origin and dest based on cutoff
	tempvar p`cutoff'_wpsm_home p`cutoff'_wpsm_dest
	make_price_tiers, percentile(`cutoff') origin(wpsm_home) dest(wpsm_dest) ///
	                  genorigin(`p`cutoff'_wpsm_home') gendest(`p`cutoff'_wpsm_dest')

	* Generate mismatch measure based on new cutoff
	tempvar mismatch_`cutoff'_p2r mismatch_`cutoff'_r2p mismatch_`cutoff'
	cap gen mismatch_p2r = `p`cutoff'_wpsm_home' * (1 - `p`cutoff'_wpsm_dest')
	if _rc!=0 {
		replace mismatch_p2r = `p`cutoff'_wpsm_home' * (1 - `p`cutoff'_wpsm_dest')
	}
	 cap gen mismatch_r2p = `p`cutoff'_wpsm_dest' * (1 - `p`cutoff'_wpsm_home')
	if _rc!=0 {
		replace mismatch_r2p = `p`cutoff'_wpsm_dest' * (1 - `p`cutoff'_wpsm_home')
	}
	
	* Run regression
	qui reghdfe y mismatch_p2r mismatch_r2p, absorb($s5) vce($se)

	* Store estimate(s)
	storespecs mismatch_p2r mismatch_r2p, spec_name(p`cutoff') file(`FILEPATH'/`FILENAME')
}
}

tictoc toc 99
restore
log close cutoffs
beepme 3
