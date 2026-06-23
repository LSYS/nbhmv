use ../build/cd-panel-ppml.dta, clear

*===============
* Time Variables
*===============
rename date date_str
gen date = date(date_str, "YMD")
format date %td

gen dow = dow(date)
replace dow = 7 if dow==0
label var dow "Day of week"

gen woy = week(date)
label var woy "Week of year"

gen wkend = (dow > 5)
label var wkend "==1 if weekend"

gen cny_sat_sun = ( date>=td(25jan2020) & date<=td(26jan2020) )
label var cny_sat_sun "==1 for CNY2020 weekend (Sat-Sun)"

*=====================
* Geographic Variables
*=====================
rename home origin
label var origin "Origin subzone"

rename area dest
label var dest "Destination subzone"

label var pa_dest "Destination planning/census area"

rename pa_home pa_origin
label var pa_origin "Origin planning/census area"

cap confirm string variable pa_origin
if _rc == 0 {
	tempvar tmp
	encode pa_origin, gen(`tmp')
	drop pa_origin
	rename `tmp' pa_origin
	label var pa_origin "Origin planning/census area"
}
cap confirm string variable pa_dest
if _rc == 0 {
	tempvar tmp
	encode pa_dest, gen(`tmp')
	drop pa_dest
	rename `tmp' pa_dest
	label var pa_dest "Destination planning/census area"
}

egen odid = group(pa_origin pa_dest)
label var odid "Origin-by-destination group ID"

rename region_o region_o_str
rename region_d region_d_str
encode region_o_str, gen(region_o)
encode region_d_str, gen(region_d)

gen central_o = (region_o_str=="CR")
gen central_d = (region_d_str=="CR")
gen ncentral_o = 1 - central_o
gen ncentral_d = 1 - central_d

*==========================
* Distance & Area Variables
*==========================
replace centroid_distance = ln(centroid_distance)
replace centroid_distance_epsg = ln(centroid_distance_epsg)

gen contiguous = 0
replace contiguous = 1 if edge_distance==0

*=====================
* Population Variables
*=====================
gen lnpop_origin = ln(1+resident_count_home)
gen lnpop_dest = ln(1+resident_count_dest)

gen lndevice_origin = ln(basecount) if basecount > 0 & !missing(basecount)
gen lndevice_dest = ln(dest_basecount) if dest_basecount > 0 & !missing(dest_basecount)

*==================
* Weather Variables
*==================
rename rain_home rain_origin

*===============
* Race Variables
*===============
gen notchinese_o = (100 - chinese_o)/100
gen notchinese_d = (100 - chinese_d)/100

*=======================
* Income/price Variables
*=======================
replace wpsm_home = wpsm_home/1000
replace wpsm_dest = wpsm_dest/1000

gen eudist = abs(wpsm_home/1000 - wpsm_dest/1000)

foreach var of varlist wpsm_home wpsm_dest {
	qui su `var', d
	gen p25_`var' = (`var' < `r(p25)') if ~missing(`var')
	gen p75_`var' = (`var' < `r(p75)') if ~missing(`var')
}

gen y = ln(inflow) if inflow > 0

*===================================
* MAIN SEGREGATION/MISMATCH MEASURES
*===================================
gen mismatch_race_m2c = notchinese_o*(1-notchinese_d)
gen mismatch_race_c2m = notchinese_d*(1-notchinese_o)
gen mismatch_race = mismatch_race_m2c + mismatch_race_c2m
gen lmismatch_race = ln(mismatch_race) if mismatch_race > 0

gen mismatch_p25_p2r = p25_wpsm_home * (1 - p25_wpsm_dest)
gen mismatch_p25_r2p = p25_wpsm_dest * (1- p25_wpsm_home)
gen mismatch_p25 = mismatch_p25_p2r + mismatch_p25_r2p

gen mismatch_p75_p2r = p75_wpsm_home * (1 - p75_wpsm_dest)
gen mismatch_p75_r2p = p75_wpsm_dest * (1- p75_wpsm_home)
gen mismatch_p75 = mismatch_p75_r2p + mismatch_p75_p2r

display "=== Zero-filled panel diagnostics ==="
qui count
display "Total rows: " r(N)
qui count if inflow == 0
display "Rows with inflow == 0: " r(N)
qui count if inflow > 0 & !missing(inflow)
display "Rows with inflow > 0:  " r(N)
