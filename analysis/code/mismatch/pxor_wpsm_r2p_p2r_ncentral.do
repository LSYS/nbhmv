cap log close ncdir
log using $logsavedir/pxor_wpsm_r2p_p2r_ncentral.txt, replace text name(ncdir)
set more off

eststo clear
forvalues i = 1/5 {
	eststo p`i': reghdfe y i.mismatch_p25_p2r##i.ncentral_d ///
	                       i.mismatch_p25_r2p##i.ncentral_d, ///
	                       absorb(\$s`i') vce($se)
		estadd local timeFE 	"\multicolumn{1}{c}{\checkmark}"
		estadd local censusPA 	"\multicolumn{1}{c}{\checkmark}"
		mat femat = e(dof_table)
		local days = femat[1,1]
		estadd local days "\multicolumn{1}{c}{$ `days' $}"
		local clusters: display %9.0fc `e(N_clust1)'
		estadd local clusters "\multicolumn{1}{c}{$ `clusters' $}"
		local nobs: display %9.0fc `e(N)'
		estadd local nobs = "\multicolumn{1}{c}{$ `nobs' $}"
		di as txt "  LP->HP, non-central net effect:"
		lincom 1.mismatch_p25_p2r + 1.mismatch_p25_p2r#1.ncentral_d
		qui test 1.mismatch_p25_p2r + 1.mismatch_p25_p2r#1.ncentral_d = 0
		estadd local pval_p2r = cond(`r(p)' < 0.0005, "<.001", string(round(`r(p)', 0.001)))
		di as txt "  HP->LP, non-central net effect:"
		lincom 1.mismatch_p25_r2p + 1.mismatch_p25_r2p#1.ncentral_d
		qui test 1.mismatch_p25_r2p + 1.mismatch_p25_r2p#1.ncentral_d = 0
		estadd local pval_r2p = cond(`r(p)' < 0.0005, "<.001", string(round(`r(p)', 0.001)))
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
#delimit ;
coefplot (p1, msymbol(O)  msize(vlarge) mlwidth(vvthin))
         (p2, msymbol(Oh) msize(vlarge) mlwidth(vvthin))
         (p3, msymbol(dh) msize(vlarge) mlwidth(vvthin))
         (p4, msymbol(th) msize(vlarge) mlwidth(vvthin))
         (p5, msymbol(sh) msize(vlarge) mlwidth(vvthin)),
        keep(1.mismatch_p25_p2r 1.mismatch_p25_p2r#1.ncentral_d
             1.mismatch_p25_r2p 1.mismatch_p25_r2p#1.ncentral_d)
        order(1.mismatch_p25_p2r 1.mismatch_p25_p2r#1.ncentral_d
              1.mismatch_p25_r2p 1.mismatch_p25_r2p#1.ncentral_d)
        level(90)
        ciopts(recast(rcap) lwidth(medthick))
        xlabel(-.08(.04).08, labsize(medlarge))
        xscale(range(-.1 .1))
        ylabel(, angle(horizontal) labsize(medlarge))
        rename(1.mismatch_p25_p2r = "{bf:LP {&rarr} HP}"
               1.mismatch_p25_p2r#1.ncentral_d = "{bf:LP {&rarr} HP} x {bf:Non-central dest.}"
               1.mismatch_p25_r2p = "{bf:HP {&rarr} LP}"
               1.mismatch_p25_r2p#1.ncentral_d = "{bf:HP {&rarr} LP} x {bf:Non-central dest.}")
        legend(label(2 "Baseline") label(4 "+ Demographics")
               label(6 "+ Businesses") label(8 "+ Rainfall") label(10 "+ POIs")
               col(1) ring(0) bplacement(sw) size(small) symysize(*.6) rowgap(*.5) region(fcolor(white) lcolor(white)))
        scheme(lean2)
        plotregion(lcolor(black) lwidth(medthin) margin(0 0 0 0))
        graphregion(color(white) margin(0 0 0 0))
        xline(0, lpattern(longdash) lcolor(red*1.3) lwidth(thick))
        ;
savefig, path($graphsavedir/pxor-wpsm-r2p-p2r-ncentral) format($graphformats);
#delimit cr

*~~~~~~~~~~~~~~~~~~~~~~~~~~
* Make LaTex Table Fragment
*~~~~~~~~~~~~~~~~~~~~~~~~~~
#delimit ;
esttab p1 p2 p3 p4 p5 using $tabsavedir/pxor-wpsm-r2p-p2r-ncentral-frag.tex,
	b(%9.4fc)
	se(%9.4fc)
	star (* 0.1 ** 0.05 *** 0.01)
	obslast
	noomitted nobase noobs
	nonumbers nolines nogaps noeqlines nodepvars
	nomtitle
	varwidth(20)
	modelwidth(8)
	keep(1.mismatch_p25_p2r 1.mismatch_p25_p2r#1.ncentral_d
	     1.mismatch_p25_r2p 1.mismatch_p25_r2p#1.ncentral_d)
	order(1.mismatch_p25_p2r 1.mismatch_p25_p2r#1.ncentral_d
	      1.mismatch_p25_r2p 1.mismatch_p25_r2p#1.ncentral_d)
	coeflabel($coeff_labels)
	scalar(
		"timeFE Day fixed effects"
		"censusPA Census area-by-day fixed effects"
		"demo Demographics"
		"business Businesses"
		"rain Neighborhood-specific rainfall"
		"POI Places of interest"
		"pval_p2r $ p $-val: net (LP $\rightarrow$ HP) = 0"
		"pval_r2p $ p $-val: net (HP $\rightarrow$ LP) = 0"
		"r2 R$^2$"
		"days Days"
		"clusters Clusters"
		"nobs Observations")
	alignment(D{.}{.}{-1})
	substitute(\_ _)
	fragment replace
	compress;
#delimit cr

log close ncdir
