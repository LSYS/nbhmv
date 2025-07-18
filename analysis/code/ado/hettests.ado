version 13.1
/* This program helps me run a series of heteroskedastic test using the Stata hettest command
	post-regression. 
	
	Dependencies: TestStatSig.ado */

capture program drop hettests
program define hettests
	/* Generates Hettests for a varlist, depends on TestStatSig */
	version 13.1
	syntax varlist
	foreach var in `varlist' {
		qui estat hettest `var'
		TestStatSig r(chi2) r(p)
		estadd local hettest_`var' = r(StatStars)
	}
end
