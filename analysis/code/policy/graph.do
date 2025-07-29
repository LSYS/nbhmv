include ./code/cutoffs/graph_settings.do
local FILEPATH ./code/policy/out

preserve

use `FILEPATH'/mismatch_eip.dta, clear

local no_asymm_increase = 2.8

local TITLE1 "Percentage increase in visits"
// local TITLE2 "  reduction in ethnic mismatch"
local TEXT "Increase from EIP = `no_asymm_increase'%"

#delimit;
twoway line increase_visits spec_id, 
	lwidth(`LWIDTH') lcolor(`lcolor')
	ylab(5(5)25, noticks nogrid angle(horizontal) labsize(`YLAB_SIZE') )
	yscale(r(0 25))
	xlab(0(20)100, labsize(`XLAB_SIZE'))
	xtitle("Percentile reduction in (non-directional) ethnic mismatch", size(`XTITLE_SIZE') )
	ytitle("")
	title("{bf:`TITLE1'}" "{bf:`TITLE2'}", pos(11) size(`TITLESIZE'))
	graphregion(fcolor(white) lcolor(white) margin(0 0 0 0) )
	plotregion(fcolor(white) margin(0 4 0 0) )	
	yline(`no_asymm_increase', lpattern(dash) lcolor(gs5))	
	text(`no_asymm_increase' 50 "`TEXT'", placement(n) size(`TEXTSIZE'))
;
#delimit cr
savefig, path($graphsavedir/mismatch-eip) format($graphformats)


*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
use `FILEPATH'/mismatch_c2m_eip.dta, clear

// local TITLE2 "  reduction in (maj {&rarr} mnr) ethnic mismatch"
local with_asymm_increase = 8.0
local TEXT "Increase from EIP = `with_asymm_increase'%"
local ref_centile 73
local ref_centile2 = `ref_centile' - 12 
#delimit;
twoway line increase_visits spec_id,
	lwidth(`LWIDTH') lcolor(`lcolor')
	ylab(5(5)25, noticks nogrid angle(horizontal) labsize(`YLAB_SIZE') )
	yscale(r(0 25))
	xlab(0(20)100, labsize(`XLAB_SIZE'))
	xtitle("Percentile reduction in (maj {&rarr} mnr) ethnic mismatch", size(`XTITLE_SIZE') )
	ytitle("")
	title("{bf:`TITLE1'}" "{bf:`TITLE2'}", pos(11) size(`TITLESIZE'))
	graphregion(fcolor(white) lcolor(white) margin(0 0 0 0) )
	plotregion(fcolor(white) margin(0 4 0 0) )	
	yline(`with_asymm_increase', lpattern(dash) lcolor(gs5))	
	xline(`ref_centile', lpattern(dash) lcolor(gs12))
	text(`with_asymm_increase' 50 "`TEXT'", placement(n) size(`TEXTSIZE')) ||
	// Add annotation
	pcarrowi 20 `ref_centile2' 20 `ref_centile',
	 legend(off) msize(vlarge) 
	 color(gs6) 
	 lw(medthick) barbsize(2)
	text(20 `ref_centile2' 
		"`ref_centile'th percentile in" "present-day ethnic mismatch", 
		placement(w) size(`TEXTSIZE')
		lcolor(gs8)
		box
		margin(medsmall)
		fcolor(white)
		lw(medthick)
		)
;
#delimit cr
savefig, path($graphsavedir/mismatch-c2m-eip) format($graphformats)

restore
