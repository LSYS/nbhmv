set more off
local FILENAME mismatch-wpsm
local FILEPATH ./code/cutoffs/out
use `FILEPATH'/`FILENAME'.dta, clear

include ./code/cutoffs/graph_settings.do

local mainbeta = beta[25]

forval cutoff = 15/35 {
	cap gen areapos = .1 if p`cutoff'==1
	if _rc!=0 {
		replace areapos = .1 if p`cutoff'==1
	}
	
	cap gen areaneg = -.05 if p`cutoff'==1
	if _rc!=0 {
		replace areaneg = -.05 if p`cutoff'==1
	}
}


#delimit;
twoway 
	/* 1/N area filler */
	(area areapos spec_id, color(`AREA_COLOR') lcolor(`AREA_COLOR') lwidth(none) )
	(area areaneg spec_id, color(`AREA_COLOR') lcolor(`AREA_COLOR') lwidth(none) )
	/* 3/N line for beta coeffs */
	(line beta spec_id, 
		lpattern(solid) lcolor(`COEF_LINE_COLOR') lwidth(medthick)
		xlab(0(25)100, labsize(`XLAB_SIZE'))
		ylab(-.05(.05).1, noticks nogrid angle(horizontal) labsize(`YLAB_SIZE') )
		yscale(r(-.0 .1) )
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
	(line u95 spec_id, 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  	
	(line l95 spec_id, 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  		
	/* 6/N 90 CI */
	(line u90 spec_id, 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  	
	(line l90 spec_id, 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  			
	/* 8/N Draw horizontal ref line for Zero */
	(, yline(0,  lcolor(gs14) lwidth(medthick) ) )	
	/* 9/N Draw scatter point for main results */
	(scatter beta spec_id if p25==1, 
		symbol(Oh) color(maroon) mlwidth(medium) msize(large)
	)
	/* 10/N Draw vert ref line for 25th percentile */
	(scatteri -.05 25 .1 25, recast(line) lpattern(dash) lcolor(gs10))
	/* 11/N Draw horizontal ref line for 25th percentile */	
	(scatteri `mainbeta' 0 `mainbeta' 100, recast(line) lwidth(thick) lcolor(maroon))
;	
#delimit cr
savefig, path($graphsavedir/single-mismatch) format($graphformats)


*~~~~~~~~~~~~
* Plot sorted
*~~~~~~~~~~~~
sort beta
gen spec_id_sorted = _n
#delimit;
twoway 
	/* 1/N line for beta coeffs */
	(line beta spec_id_sorted, 
		lpattern(solid) lcolor(`COEF_LINE_COLOR') lwidth(medthick)
		xlab(0(25)100, labsize(`XLAB_SIZE'))
		ylab(-.05(.05).1, noticks nogrid angle(horizontal) labsize(`YLAB_SIZE') )
		xtitle("Specification (sorted by estimate size)", size(`XTITLE_SIZE') )
		ytitle("")
		legend(order(6 "Main estimate" 1 "Point estimates"  2 "95% CI" 4 "90% CI" ) 
			region(lcolor(white)) 
			pos(12) ring(0) rows(1) size(`LEGENDSIZE') symysize(medium) symxsize(medium)
			keygap(tiny)
		) 
		graphregion(fcolor(white) lcolor(white) margin(0 0 0 0) )
	   	plotregion(fcolor(white) lcolor(black) margin(0 4 0 0) lwidth(medium) )		
	)	
	/* 2/N 95 CI */
	(line u95 spec_id_sorted, 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  	
	(line l95 spec_id_sorted, 
		lcolor(`CI95_LCOLOR') lwidth(`CI95_LWIDTH') lpattern(`CI95_LPATTERN')
	)  		
	/* 4/N 90 CI */
	(line u90 spec_id_sorted, 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  	
	(line l90 spec_id_sorted, 
		lcolor(`CI90_LCOLOR') lwidth(`CI90_LWIDTH') lpattern(`CI90_LPATTERN')
	)  				
	/* 5/N Draw horizontal ref line for Zero */
	(, yline(0,  lcolor(gs14) lwidth(medthick) ) )	
	/* 6/N Scatter for main estimate */
	(scatter beta spec_id_sorted if p25==1, symbol(D) color(maroon) );	
#delimit cr
savefig, path($graphsavedir/sorted-single-mismatch) format($graphformats)
