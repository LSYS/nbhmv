set more off
local FILENAME mismatch-wpsm-ncentral
local FILEPATH ./code/cutoffs/out

preserve
use `FILEPATH'/`FILENAME'.dta, clear

include ./code/cutoffs/graph_settings.do

*=============================
* Plot mismatch (uninteracted)
*=============================
forval cutoff = 15/35 {
	cap gen areapos = .2 if p`cutoff'==1
	if _rc!=0 {
		replace areapos = .2 if p`cutoff'==1
	}
	
	cap gen areaneg = -.1 if p`cutoff'==1
	if _rc!=0 {
		replace areaneg = -.1 if p`cutoff'==1
	}
}

local y mismatch
local mainbeta = beta_`y'[25]

#delimit;
twoway 
	/* 1/N area filler */
	(area areapos spec_id, color(`AREA_COLOR') lcolor(`AREA_COLOR') lwidth(none) )
	(area areaneg spec_id, color(`AREA_COLOR') lcolor(`AREA_COLOR') lwidth(none) )			
	(line beta_`y' spec_id, 
		lpattern(solid) lcolor(`COEF_LINE_COLOR') lwidth(medthick)
		xlab(0(25)100, labsize(`XLAB_SIZE'))
		ylab(-.1(.1).2, noticks nogrid angle(horizontal) labsize(`YLAB_SIZE') )
		xtitle("Percentile used for cutoff", size(`XTITLE_SIZE') )
		ytitle("")
		legend(order(8 "Main estimate" 3 "Point estimates"  4 "95% CI" 6 "90% CI" ) 
			region(lcolor(white)) 
			colgap(5)
			pos(12) ring(0) rows(1) size(`LEGENDSIZE') symysize(medium) symxsize(medium)
			keygap(tiny)
		) 
		graphregion(fcolor(white) lcolor(white) margin(0 0 0 0) )
		plotregion(fcolor(white) lcolor(black) margin(0 4 0 0) lwidth(medium) )		
	)
	/* 4/N 95 CI */
	(line u95_`y' spec_id, 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  	
	(line l95_`y' spec_id, 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)
	/* 6/N 90 CI */
	(line u90_`y' spec_id, 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  	
	(line l90_`y' spec_id, 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  			
	/* 8/N Draw horizontal ref line for Zero */
	(, yline(0,  lcolor(gs14) lwidth(medthick) ) )	
	/* 9/N Draw scatter point for main results */
	(scatter beta_`y' spec_id if p25==1, 
		symbol(Oh) color(maroon) mlwidth(medium) msize(large)
	)
	/* 10/N Draw vert ref line for 25th percentile */
	(scatteri -.1 25 .2 25, recast(line) lpattern(dash) lcolor(gs10))
	/* 11/N Draw horizontal ref line for 25th percentile */	
	(scatteri `mainbeta' 0 `mainbeta' 100, recast(line) lwidth(thick) lcolor(maroon))
;	
#delimit cr
savefig, path($graphsavedir/`y'-baseline-ncentral) format($graphformats)

*===========================
* Plot mismatch x ncentral_d
*===========================
forval cutoff = 15/35 {
	cap gen areapos = .6 if p`cutoff'==1
	if _rc!=0 {
		replace areapos = .6 if p`cutoff'==1
	}
	
	cap gen areaneg = -.2 if p`cutoff'==1
	if _rc!=0 {
		replace areaneg = -.2 if p`cutoff'==1
	}
}

local y mismatchxncentral_d
local mainbeta = beta_`y'[25]

#delimit;
twoway 
	/* 1/N area filler */
	(area areapos spec_id, color(`AREA_COLOR') lcolor(`AREA_COLOR') lwidth(none) )
	(area areaneg spec_id, color(`AREA_COLOR') lcolor(`AREA_COLOR') lwidth(none) )			
	(line beta_`y' spec_id, 
		lpattern(solid) lcolor(`COEF_LINE_COLOR') lwidth(medthick)
		xlab(0(25)100, labsize(`XLAB_SIZE'))
		ylab(-.2(.2).6, noticks nogrid angle(horizontal) labsize(`YLAB_SIZE') )
		xtitle("Percentile used for cutoff", size(`XTITLE_SIZE') )
		ytitle("")
		legend(order(8 "Main estimate" 3 "Point estimates"  4 "95% CI" 6 "90% CI" ) 
			region(lcolor(white)) 
			colgap(5)
			pos(12) ring(0) rows(1) size(`LEGENDSIZE') symysize(medium) symxsize(medium)
			keygap(tiny)
		) 
		graphregion(fcolor(white) lcolor(white) margin(0 0 0 0) )
		plotregion(fcolor(white) lcolor(black) margin(0 4 0 0) lwidth(medium) )		
	)	
	/* 4/N 95 CI */
	(line u95_`y' spec_id, 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  	
	(line l95_`y' spec_id, 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  		
	/* 6/N 90 CI */
	(line u90_`y' spec_id, 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  	
	(line l90_`y' spec_id, 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  			
	/* 8/N Draw horizontal ref line for Zero */
	(, yline(0,  lcolor(gs14) lwidth(medthick) ) )	
	/* 9/N Draw scatter point for main results */
	(scatter beta_`y' spec_id if p25==1, 
		symbol(Oh) color(maroon) mlwidth(medium) msize(large)
	)
	/* 10/N Draw vert ref line for 25th percentile */
	(scatteri -.2 25 .6 25, recast(line) lpattern(dash) lcolor(gs10))
	/* 11/N Draw horizontal ref line for 25th percentile */	
	(scatteri `mainbeta' 0 `mainbeta' 100, recast(line) lwidth(thick) lcolor(maroon))
;	
#delimit cr
savefig, path($graphsavedir/`y'-interacted-ncentral) format($graphformats)


*====================================
* Plot sorted mismatch (uninteracted)
*====================================
local y mismatch

sort beta_`y'
gen spec_id_`y' = _n
#delimit;
twoway 
	/* 1/N line for beta coeffs */
	(line beta_`y' spec_id_`y', 
		lpattern(solid) lcolor(`COEF_LINE_COLOR') lwidth(medthick)
		xlab(0(20)100, labsize(`XLAB_SIZE'))
		ylab(-.1(.1).2, noticks nogrid angle(horizontal) labsize(`YLAB_SIZE') )
		xtitle("Specification (sorted by size)", size(`XTITLE_SIZE'))
		ytitle("")
		legend(order(6 "Main estimate" 1 "Point estimates"  3 "95% CI" 1 "90% CI" ) 
			region(lcolor(white)) 
			colgap(5)
			pos(12) ring(0) rows(1) size(`LEGENDSIZE') symysize(medium) symxsize(medium)
			keygap(tiny)
		) 
		graphregion(fcolor(white) lcolor(white) margin(0 0 0 0) )
	   	plotregion(fcolor(white) lcolor(black) margin(0 4 0 0) lwidth(medium) )		
	)
	/* 2/N 95 CI */
	(line u95_`y' spec_id_`y', 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  	
	(line l95_`y' spec_id_`y', 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  		
	/* 4/N 90 CI */
	(line u90_`y' spec_id_`y', 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  	
	(line l90_`y' spec_id_`y', 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  			
	/* /N Draw horizontal ref line for 0 */
	(, yline(0,  lcolor(`ZERO_LCOLOR') lwidth(`ZERO_LWIDTH') ) )
	/* 6/N Scatter for main estimate */
	(scatter beta_`y' spec_id_`y' if p25==1, symbol(D) color(maroon) )
;
#delimit cr
savefig, path($graphsavedir/sorted-`y'-baseline-ncentral) format($graphformats)


*====================================
* Plot sorted mismatch x noncentral_d
*====================================
local y mismatchxncentral_d

sort beta_`y'
gen spec_id_`y' = _n
#delimit;
twoway 
	/* 1/N line for beta coeffs */
	(line beta_`y' spec_id_`y', 
		lpattern(solid) lcolor(`COEF_LINE_COLOR') lwidth(medthick)
		xlab(0(20)100, labsize(`XLAB_SIZE'))
		ylab(-.2(.2).6, noticks nogrid angle(horizontal) labsize(`YLAB_SIZE') )
		xtitle("Specification (sorted by size)", size(`XTITLE_SIZE'))
		ytitle("")
		legend(order(6 "Main estimate" 1 "Point estimates"  3 "95% CI" 1 "90% CI" ) 
			region(lcolor(white)) 
			colgap(5)
			pos(12) ring(0) rows(1) size(`LEGENDSIZE') symysize(medium) symxsize(medium)
			keygap(tiny)
		) 
		graphregion(fcolor(white) lcolor(white) margin(0 0 0 0) )
	   	plotregion(fcolor(white) lcolor(black) margin(0 4 0 0) lwidth(medium) )		
	)
	/* 2/N 95 CI */
	(line u95_`y' spec_id_`y', 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  	
	(line l95_`y' spec_id_`y', 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  		
	/* 4/N 90 CI */
	(line u90_`y' spec_id_`y', 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  	
	(line l90_`y' spec_id_`y', 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  			
	/* /N Draw horizontal ref line for 0 */
	(, yline(0,  lcolor(`ZERO_LCOLOR') lwidth(`ZERO_LWIDTH') ) )
	/* 6/N Scatter for main estimate */
	(scatter beta_`y' spec_id_`y' if p25==1, symbol(D) color(maroon) )
;
#delimit cr
savefig, path($graphsavedir/sorted-`y'-interacted-ncentral) format($graphformats)


restore
