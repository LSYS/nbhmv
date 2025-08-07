cap log close exc_emp
log using $logsavedir/exc_majorempcenters_pxor_wpsm_r2p_p2r.txt, replace text name(exc_emp)

preserve
drop if inlist(pa_origin, 201, 37, 157, 8, 249, 150, 11, 57, 50, 38, 29, 190)
drop if inlist(pa_dest, 201, 37, 157, 8, 249, 150, 11, 57, 50, 38, 29, 190)

set more off
local x1 mismatch_p25_p2r
local x2 mismatch_p25_r2p
// local x1 mismatch_p75_p2r
// local x2 mismatch_p75_r2p
// local x1 mismatch_p80_p2r
// local x2 mismatch_p80_r2p

*~~~~~~~~~~~~~~~~~~~~~~~~
* Estimate specifications
*~~~~~~~~~~~~~~~~~~~~~~~~
eststo clear
forvalues i = 1/5 {
	eststo: reghdfe y i.`x1' i.`x2', absorb(\$s`i') vce($se)
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
		* Test r2p + p2r = 0
		qui test 1.`x1' + 1.`x2' = 0
		estadd local pval = string(round(`r(p)', 0.001))
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
#delimit;
coefplot (est1, msymbol(O)  msize($MSIZE) mlwidth($MLWIDTH) )
		 (est2, msymbol(Oh) msize($MSIZE) mlwidth($MLWIDTH) offset())
		 (est3, msymbol(dh) msize($MSIZE) mlwidth($MLWIDTH) offset())
		 (est4, msymbol(th) msize($MSIZE) mlwidth($MLWIDTH) offset()) 
		 (est5, msymbol(sh) msize($MSIZE) mlwidth($MLWIDTH) offset()),
			keep(1.`x1' 1.`x2')
		 level(90)
		 ciopts(recast(rcap) lwidth($CIWIDTH))	
		 asequation 
		 xlabel(-.04(.02).06, labsize($XLABSIZE) )
		 xscale(range(-.05 .08))
		 ylabel(, angle(vertical) labsize($YLABSIZE))
		 rename(1.`x1' = "{bf:P {&rarr} NP}"
		 		1.`x2' = "{bf:NP {&rarr} P}"
		 		)
		 legend(label(2 "{bf:Baseline}") label(4 "{bf:+ Demographics}") 
				label(6 "{bf:+ Businesses}") 	 label(8 "{bf:+ Rainfall}") label(10 "{bf:+ POIs}")
				col(1) ring(0) bplacement(se) size($LEGEND_SIZE)
				)
		scheme(lean2)
		plotregion(lcolor(black) lwidth(medthin) margin(0 0 0 0)) 	
		graphregion(color(white) margin(0 0 0 0)) 
		xline(0, lpattern(longdash) lcolor(red*1.3) lwidth($REFLINE_WIDTH))
		;
savefig, path($graphsavedir/exc-majorempcenters-pxor-wpsm-r2p-p2r) format($graphformats);

*~~~~~~~~~~~~~~~~~
* Make LaTex Table 
*~~~~~~~~~~~~~~~~~
#delimit;
esttab using $tabsavedir/exc-majorempcenters-pxor-wpsm-r2p-p2r-frag.tex, 
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
		"pval $ p $-val: (P $\rightarrow$ NP) $\neq$ (NP $\rightarrow$ P)"
		"r2 R$^2$" 
		"days Days"
		"clusters Clusters"
		"nobs Observations") 	
	alignment(D{.}{.}{-1})	
	substitute(\_ _)
	fragment replace
	compress;
#delimit cr

restore

log close exc_emp
