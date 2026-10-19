cap log close ncdir
log using $logsavedir/pxor_race_asymmetry_ncentral.txt, replace text name(ncdir)
set more off

eststo clear
forvalues i = 1/5 {
	eststo r`i': reghdfe y c.mismatch_race_m2c##i.ncentral_d ///
	                       c.mismatch_race_c2m##i.ncentral_d, ///
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
		di as txt "  Maj->Mnr, non-central net effect:"
		lincom mismatch_race_c2m + 1.ncentral_d#c.mismatch_race_c2m
		qui test mismatch_race_c2m + 1.ncentral_d#c.mismatch_race_c2m = 0
		estadd local pval_c2m = cond(`r(p)' < 0.0005, "<.001", string(round(`r(p)', 0.001)))
		di as txt "  Mnr->Maj, non-central net effect:"
		lincom mismatch_race_m2c + 1.ncentral_d#c.mismatch_race_m2c
		qui test mismatch_race_m2c + 1.ncentral_d#c.mismatch_race_m2c = 0
		estadd local pval_m2c = cond(`r(p)' < 0.0005, "<.001", string(round(`r(p)', 0.001)))
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
coefplot (r1, msymbol(O)  msize(vlarge) mlwidth(vvthin))
         (r2, msymbol(Oh) msize(vlarge) mlwidth(vvthin))
         (r3, msymbol(dh) msize(vlarge) mlwidth(vvthin))
         (r4, msymbol(th) msize(vlarge) mlwidth(vvthin))
         (r5, msymbol(sh) msize(vlarge) mlwidth(vvthin)),
        keep(mismatch_race_m2c 1.ncentral_d#c.mismatch_race_m2c
             mismatch_race_c2m 1.ncentral_d#c.mismatch_race_c2m)
        order(mismatch_race_m2c 1.ncentral_d#c.mismatch_race_m2c
              mismatch_race_c2m 1.ncentral_d#c.mismatch_race_c2m)
        level(90)
        ciopts(recast(rcap) lwidth(medthick))
        xlabel(-1(.5).5, labsize(medlarge))
        xscale(range(-1.2 .9))
        ylabel(, angle(horizontal) labsize(medlarge))
        rename(mismatch_race_c2m = "{bf:Maj {&rarr} Mnr}"
               1.ncentral_d#c.mismatch_race_c2m = "{bf:Maj {&rarr} Mnr} x {bf:Non-central dest.}"
               mismatch_race_m2c = "{bf:Mnr {&rarr} Maj}"
               1.ncentral_d#c.mismatch_race_m2c = "{bf:Mnr {&rarr} Maj} x {bf:Non-central dest.}")
        legend(label(2 "Baseline") label(4 "+ Demographics")
               label(6 "+ Businesses") label(8 "+ Rainfall") label(10 "+ POIs")
               col(1) ring(0) bplacement(se) size(small) symysize(*.6) rowgap(*.5) region(fcolor(white) lcolor(white)))
        scheme(lean2)
        plotregion(lcolor(black) lwidth(medthin) margin(0 0 0 0))
        graphregion(color(white) margin(0 0 0 0))
        xline(0, lpattern(longdash) lcolor(red*1.3) lwidth(thick))
        ;
savefig, path($graphsavedir/pxor-race-asymmetry-ncentral) format($graphformats);
#delimit cr

*~~~~~~~~~~~~~~~~~~~~~~~~~~
* Make LaTex Table Fragment
*~~~~~~~~~~~~~~~~~~~~~~~~~~
#delimit ;
esttab r1 r2 r3 r4 r5 using $tabsavedir/pxor-race-asymmetry-ncentral-frag.tex,
	b(%9.4fc)
	se(%9.4fc)
	star (* 0.1 ** 0.05 *** 0.01)
	obslast
	noomitted nobase noobs
	nonumbers nolines nogaps noeqlines nodepvars
	nomtitle
	varwidth(20)
	modelwidth(8)
	keep(mismatch_race_m2c 1.ncentral_d#c.mismatch_race_m2c
	     mismatch_race_c2m 1.ncentral_d#c.mismatch_race_c2m)
	order(mismatch_race_m2c 1.ncentral_d#c.mismatch_race_m2c
	      mismatch_race_c2m 1.ncentral_d#c.mismatch_race_c2m)
	coeflabel($coeff_labels)
	scalar(
		"timeFE Day fixed effects"
		"censusPA Census area-by-day fixed effects"
		"demo Demographics"
		"business Businesses"
		"rain Neighborhood-specific rainfall"
		"POI Places of interest"
		"pval_m2c $ p $-val: net (Mnr $\rightarrow$ Maj) = 0"
		"pval_c2m $ p $-val: net (Maj $\rightarrow$ Mnr) = 0"
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
