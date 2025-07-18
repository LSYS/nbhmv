cap program drop run_es
program define run_es
//////////////////////////////////////////////////////////////////////////////////////////
// Generate event study coefficients.													//
// Dependencies: 																		//
//		* regsave																		//
//		* reghdfe (for fixed effects)													//
// Returns: dta with four main columns:													//
//	(1) coefficient estimates															//
//  (2) Upper CI 																		//
//  (3) Lower CI 																		//
//	(4) Order variable for plotting (porder) relative to "day 0" 						//
// 	Syntax: 																			//
// 		run_es depvar timevar [if] [in] [weight], 	                                  	//
//			treattime(var) preperiods(#) postperiods(#) [options]						//
//	Example:   																			//
//		use http://pped.org/bacon_example.dta, clear									//												
//		run_e asmrs year, treattime(_nfd) preperiods(6) postperiods(12) ///				//
//			fe(stfips year) controls(pcinc asmrh cases copop) ///						//
//			cluster(stfips) confidence(95)											    //
//		twoway (line coef porder) (line uci porder) (line lci porder)					//
//	Caveats:																			//
//		Omitted (reference/base) period is hard set to -1 (period before treatment)		//
//////////////////////////////////////////////////////////////////////////////////////////
syntax varlist(min=2 max=2 numeric) [if] [in] [pw fw aw iw], /// 
	TREATtime(varlist) PREperiods(real) POSTperiods(real) ///
	[fe(string) CONTrols(string) CLUSTer(varlist) CONFidence(string)]

	local omittedperiod -1

	local yvar "`1'"
	local tvar: word 2 of `varlist'

	local count: word count `treattime'  
	// capture confirm scalar `count'==1
	if `count'==1 {
		dis in green "Treated time var is: `treattime'"
	}
	else {
		local treattime: word 1 of `treattime'
		dis in red "Only one treated time variable allowed" 
		dis in red "Assuming `treattime' (first) var is treated time."
	}

	local wt [`weight' `exp']

	qui cap gen t_to_treat = `tvar' - `treattime'
	label var t_to_treat "period relative to Day 0"

	local estperiods = `preperiods' + `postperiods'

	qui recode t_to_treat (.=`omittedperiod')
	qui recode t_to_treat (min/-`preperiods'=-`preperiods') (`postperiods'/max=`postperiods')
	char t_to_treat[omit] `omittedperiod'
	qui xi i.t_to_treat, prefix(_)

	if "`fe'"=="" {
		qui reg `yvar' _t_to_treat_* `controls' `if' `in' `wt', r cluster(`CLUSTer')
	}
	else {
		qui reghdfe `yvar' _t_to_treat_* `controls' `if' `in' `wt', absorb(`fe') cluster(`CLUSTer')
	}
	regsave

	local T = _N
	if "`controls'"!="" {
		local estperiods = `preperiods' + `postperiods'
		local row_to_drop_from = 2 + `estperiods'
		qui drop in `row_to_drop_from'/`T'
	}

	local last_row = 1 + `estperiods'
	qui replace var = "omitted" in `last_row'
	qui replace coef = 0		in `last_row'
	qui replace stderr = 0		in `last_row'		

	qui gen porder = `omittedperiod' in `last_row'
	label var porder 	"Running order indicate time periods to be plotted"

	qui gen order = _n
	qui gen pre = 1 if order < `preperiods'
	qui gen post = 1 if order >= `preperiods' & order < `last_row'

	qui replace porder = -`preperiods' + (order - 1) if order <= `preperiods' `omittedperiod'
	qui drop pre

	qui replace porder = order - `preperiods' if order > `preperiods' `omittedperiod' & order != `last_row'
	qui drop post

	qui drop order
	sort porder	

	* Reconstruct CI bounds
	if "`confidence'"=="" {
		local confidence 95
		local zscore = 1.96
	}
	else if "`confidence'"=="95" {
		local zscore = 1.96
	} 
	else if "`confidence'"=="90" {
		local zscore = 1.645
	}
	else if "`confidence'"=="99" {
		local zscore = 2.576
	}
	else {
		dis in red "Confidence level restricted to 90, 95, or 99."
		dis in red "You entered `confidence'%."
		dis in red "Using default of 95% confidence level."
		local confidence 95
		local zscore = 1.96	
	}
	qui gen uci = coef + `zscore' * stderr if porder!=`omittedperiod'
	label var uci "Upper bound of `confidence'% CI"

	qui gen lci = coef - `zscore' * stderr if porder!=`omittedperiod'
	label var lci "Lower bound of `confidence'% CI"

	dis in green "Depvar is: `yvar'"
	dis in green "Time var is: `tvar'"
	dis in green "Control variables are: |`controls'|"
	dis in green "Fixed effects are: |`fe'|"
	dis in green "Clustering se by: `cluster'"
	dis in green "if condition: |`if'|"
	dis in green "in condition: |`in'|"
	dis in green "Weight: |`weight' `exp'|"
end
