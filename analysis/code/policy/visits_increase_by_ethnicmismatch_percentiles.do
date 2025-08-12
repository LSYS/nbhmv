cap log close counterfactual
log using $logsavedir/visits_increase_by_ethnicmismatch_percentiles.txt, replace text name(counterfactual)

local ethnic_est = -0.184 // (-0.184) from Table 2. Effect of ethnic mismatch on movement

local FILENAME mismatch_eip
local FILEPATH ./code/policy/out

cap erase `FILEPATH'/`FILENAME'.dta


set more off

preserve

tictoc tic 99
qui bysort origin dest: gen dup = cond(_N==1,0,_n)
drop if dup > 1
count

forvalues cutoff = 0/100 {
	qui centile mismatch_race, centile(`cutoff')

	* Compute increase in visits from percentile reduction in mismatch
	local _x = 100*`ethnic_est'*-`r(c_1)' 
	// dis as result "p""`cutoff'"":" `r(c_1)' `_x'

	* Store estimate(s)
	tempfile temp
	qui save "`temp'", replace

	cap use "`FILEPATH'/`FILENAME'.dta", clear
	if _rc!=0 { /* Init empty dataset */
		clear
		gen int spec_id = .
		gen double increase_visits = .
		gen double centile_val = .
	}

	* update dataset size
	local n = 1 + _N
	qui set obs `n'
	qui replace spec_id = `cutoff' if _n==`n'
	qui replace increase_visits = `_x' if _n==`n'
	qui replace centile_val = `r(c_1)' if _n==`n'

	qui save "`FILEPATH'/`FILENAME'.dta", replace
	use `temp', clear

	noisily _dots `cutoff' 0
}

tictoc toc 99
restore
log close counterfactual
beepme 3
