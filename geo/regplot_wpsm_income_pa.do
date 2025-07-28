cap here
if _rc == 0 {
	here, set
	cd ${here}
}
else {
	global here "\\wsl.localhost\Debian\home\lsys\nbhmv\geo"
	cd $here
}

adopath ++ ../analysis/code/ado

import delimited pa-price.csv, clear

rename region region_str
encode region_str, gen(region)

rename planning_area planning_area_str
encode planning_area_str, gen(planning_area)	

* Scale down wpsm by 1000
replace wpsm = wpsm / 1000
drop if missing(income) /* to avoid axis range going screwy, come on stata.. */

*===============================================================================
local y wpsm
local x income

qui reg `y' `x', r
local r2= e(r2)
local r2: display %5.2f e(r2)

local n = e(N)

mat coeffs = e(b)
local coeff = coeffs[1,1]
local se = _se[`x']
local tstat = `coeff' / `se'

local  coeff: display %5.3f `coeff'
local  se: display %5.2f `se'
local  tstat: display %5.2f `tstat'

// local REPORT_PRINT ({&beta}=`coeff', {it:t}-stat=`tstat'. R{sup:2}=`r2', N=`n')
local REPORT_PRINT (R{sup:2}=`r2', N=`n')
*===============================================================================

local LABSIZE large
local TITLESIZE huge

#delimit;
twoway 	(lfitci `y' `x',
			color(gs14*.8)
			xlabel(4000(1500)8000, labsize(`LABSIZE')) 
			ylabel(0(5)20, angle(360) labsize(`LABSIZE') nogrid ) 
			xtitle("{bf:Income}", size(`TITLESIZE'))
			ytitle("{bf:House price}", size(`TITLESIZE'))
			legend(off)
			graphregion(color(white) lc(white) lw(med) margin(0 0 0 0)) 
			plotregion(margin(0 1 0 0)) 
			text(.5 6500 "{bf:`REPORT_PRINT'}", placement(ne) size(huge))
		)
		(lfit `y' `x', color(navy*1.3) lpattern(solid) lwidth(vthick) )
		(scatter `y' `x' [aw=workpop], 
			msymbol(Oh) mlwidth(vvvthin) 
			msize(medlarge)
			mcolor(maroon)
		)
;
#delimit cr
savefig, path(../results/figures/supplementary/regplot-wpsm-price-pa) format(pdf png tif)
