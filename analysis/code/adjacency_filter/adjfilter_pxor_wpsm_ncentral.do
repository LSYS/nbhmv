cap log close adjacency_filter
log using $logsavedir/adjfilter_pxor_wpsm_ncentral.txt, replace text name(adjacency_filter)

set more off

local x mismatch_p25

*~~~~~~~~~~~~~~~~~~~~~~~~
* Estimate specifications
*~~~~~~~~~~~~~~~~~~~~~~~~
eststo clear
forvalues i = 1/5 {
	eststo: reghdfe y i.`x'##i.ncentral_d if contiguous==0, absorb(\$s`i') vce($se)
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
		* Test mismatch + mismatch*ncentral = 0 [total effect outside central]
		qui test 1.`x' + 1.`x'#1.ncentral_d = 0
		estadd local pval = cond(`r(p)' < 0.0005, "<.001", string(round(`r(p)', 0.001)))
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

*~~~~~~~~~~~~~~
* Plot coefplot
*~~~~~~~~~~~~~~
local MSIZE vlarge
local YLABSIZE medlarge
local LEGEND_SIZE medlarge
#delimit;
coefplot (est1, msymbol(O)  msize(`MSIZE') mlwidth($MLWIDTH) )
		 (est2, msymbol(Oh) msize(`MSIZE') mlwidth($MLWIDTH) offset())
		 (est3, msymbol(dh) msize(`MSIZE') mlwidth($MLWIDTH) offset())
		 (est4, msymbol(th) msize(`MSIZE') mlwidth($MLWIDTH) offset()) 
		 (est5, msymbol(sh) msize(`MSIZE') mlwidth($MLWIDTH) offset()),
			keep(*`x'*)
		 level(90)
		 ciopts(recast(rcap) lwidth($CIWIDTH))	
		 asequation 
		 xlabel(-.08(.04).08, labsize($XLABSIZE) )
		 xscale(range(-.1 .1))
		 ylabel(, angle(horizontal) labsize(`YLABSIZE'))
		 rename(1.`x' = "{bf: Income mismatch}"
		 		1.`x'#1.ncentral_d = "x {bf:Non-central dest.}"
		 		)
		 legend(label(2 "{bf:Baseline}") label(4 "{bf:+ Demographics}") 
				label(6 "{bf:+ Businesses}") 	 label(8 "{bf:+ Rainfall}") label(10 "{bf:+ POIs}")
				col(1) ring(0) bplacement(se) size(`LEGEND_SIZE')
				)
		scheme(lean2)
		plotregion(lcolor(black) lwidth(medthin) margin(0 0 0 0)) 	
		graphregion(color(white) margin(0 0 0 0)) 
		xline(0, lpattern(longdash) lcolor(red*1.3) lwidth($REFLINE_WIDTH))
		;
savefig, path($graphsavedir/adjfilter-pxor-wpsm-ncentral) format($graphformats);
#delimit cr


*~~~~~~~~~~~~~~~~~
* Make LaTex Table
*~~~~~~~~~~~~~~~~~
#delimit;
esttab using $tabsavedir/adjfilter-pxor-wpsm-ncentral-frag.tex, 
	b(%9.4fc)
	se(%9.4fc)
	star (* 0.1 ** 0.05 *** 0.01)
	obslast
	noomitted        
	nobase noobs
	nonumbers nolines nogaps noeqlines nodepvars
	nomtitle
	varwidth(20)
	modelwidth(8)
	drop(_cons)
	coeflabel($coeff_labels)
	scalar(
		"timeFE Day fixed effects"
		"censusPA Census area-by-day fixed effects"
		"demo Demographics"
		"business Businesses"
		"rain Neighborhood-specific rainfall"
		"POI Places of interest"
		"pval $ p$-val: $\hat{\beta}$ + $\hat{\gamma} = 0 $"
		"r2 R$^2$" 
		"days Days"
		"clusters Clusters"
		"nobs Observations") 
	alignment(D{.}{.}{-1})	
	substitute(\_ _)
	fragment replace
	compress;		
#delimit cr

log close adjacency_filter
