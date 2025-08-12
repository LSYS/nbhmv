cap log close cny
log using $logsavedir/cny_wpsm.txt, replace text name(cny)

set more off

local x wpsm_home wpsm_dest

*~~~~~~~~~~~~~~~~~~~~~~~~
* Estimate specifications
*~~~~~~~~~~~~~~~~~~~~~~~~
eststo clear
forvalues i = 1/5 {
	eststo: reghdfe y `x', absorb(\$s`i') vce($se)
		* Add indicators for baseline 
		estadd local timeFE 	"\multicolumn{1}{c}{\checkmark}"
		estadd local censusPA 	"\multicolumn{1}{c}{\checkmark}"
		* Add sample sizes report
		mat femat = e(dof_table)
		local days = femat[1,1]
		estadd local days "\multicolumn{1}{c}{$ `days' $}"		
		local clusters: display %9.0fc `e(N_clust1)'
		estadd local clusters "\multicolumn{1}{c}{$ `clusters' $}"		
		local nobs: display %9.0fc `e(N)'
		estadd local nobs = "\multicolumn{1}{c}{$ `nobs' $}"	
		* Add indicators for additional controls
		if `i'==2 {
			estadd local demo 		"\multicolumn{1}{c}{\checkmark}"				
		}
		else if `i'==3 {
			estadd local demo 		"\multicolumn{1}{c}{\checkmark}"	
			estadd local business 	"\multicolumn{1}{c}{\checkmark}"	
		}
		else if `i'==4 {
			estadd local demo 		"\multicolumn{1}{c}{\checkmark}"	
			estadd local business 	"\multicolumn{1}{c}{\checkmark}"				
			estadd local rain 		"\multicolumn{1}{c}{\checkmark}"				
		}
		else if `i'==5 {
			estadd local demo 		"\multicolumn{1}{c}{\checkmark}"	
			estadd local business 	"\multicolumn{1}{c}{\checkmark}"				
			estadd local rain 		"\multicolumn{1}{c}{\checkmark}"			
			estadd local POI 		"\multicolumn{1}{c}{\checkmark}"			
		}
}


*~~~~~~~~~~~~~~~~~
* Make LaTex Table
*~~~~~~~~~~~~~~~~~
#delimit;
esttab using $tabsavedir/wpsm-frag.tex, 
	b(%9.3fc)
	se(%9.3fc)
	star (* 0.1 ** 0.05 *** 0.01)
	obslast
	noomitted        
	noobs
	nonumbers nolines nogaps noeqlines nodepvars
	nomtitle
	varwidth(20)
	modelwidth(8)
	drop(_cons)
	nobase
	coeflabel($coeff_labels)
	scalar(
		"timeFE Day fixed effects"
		"censusPA Census area-by-day fixed effects"
		"demo Demographics"
		"business Businesses"
		"rain Neighborhood-specific rainfall"
		"POI Places of interests"
		"r2 R$^2$" 
		"days Days"
		"clusters Clusters"
		"nobs Observations") 
	alignment(D{.}{.}{-1})	
	substitute(\_ _)
	fragment replace
	compress;		
#delimit cr
beep 
