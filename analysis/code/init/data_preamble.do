// // import delimited cd-panel.csv, rowr(1:5000)
// if $SCRATCH == 1 {
// 	// import delimited ../build/cd-panel.csv, rowr(1:5000)
// 	import delimited cd-panel.csv, rowr(1:5000)
// }
// else {
// 	import delimited ../build/cd-panel.csv
// 	// import delimited cd-panel.csv
// }
import delimited ../build/cd-panel.csv
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

gen cny_fri_sun = (date>=td(24jan2020)) & (date<=td(26jan2020))
label var cny_fri_sun "==1 for CNY2020 Fri-Sun"

gen cny_thu_sat = ( date>=td(23jan2020) & date<=td(25jan2020) )
label var cny_thu_sat "==1 for CNY2020 Thu-Sat"

gen cny_sat_sun = ( date>=td(25jan2020) & date<=td(26jan2020) )
label var cny_sat_sun "==1 for CNY2020 weekend (Sat-Sun)"

gen cny_fri_sat = ( date>=td(24jan2020) & date<=td(25jan2020) )
label var cny_fri_sat "==1 for CNY2020 Fri-Sat"

gen cny_fri = date==td(24jan2020)
label var cny_fri "==1 for CNY2020 Fri"

gen cny = ( date>=td(24jan2020) & date<=td(27jan2020) )
label var cny "==1 for CNY2020 Fri-Mon"

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

egen odid = group(pa_origin pa_dest)
label var odid "Origin-by-destination group ID"

rename region_o region_o_str
rename region_d region_d_str
encode region_o_str, gen(region_o)
encode region_d_str, gen(region_d)

gen central_o = (region_o_str=="CR")
label var central_o "==1 if origin is Central Region"

gen central_d = (region_d_str=="CR")
label var central_d "==1 if destination is Central Region"

gen ncentral_o = 1 - central_o
label var ncentral_o "==1 if origin is non-Central Region"

gen ncentral_d = 1 - central_d
label var ncentral_d "==1 if destination is non-Central Region"

*==========================
* Distance & Area Variables
*==========================
replace centroid_distance = ln(centroid_distance)
label var centroid_distance "Dist. b/w area and destination, using centroid"

replace centroid_distance_epsg = ln(centroid_distance_epsg)
label var centroid_distance_epsg "Dist. b/w area and destination, using centroid (EPSG)"

gen contiguous = 0
replace contiguous = 1 if edge_distance==0
label var contiguous "==1 if area and destination is contiguous"

label var area_o "Land area of origin subzone (km2)"
label var area_d "Land area of destination subzone (km2)"

*=====================
* Population Variables
*=====================
label var basecount "#devices captured in origin subzone-date"
label var dest_basecount "#devices captured in destination subzone-date"
label var inflow "%devices from origin to destination"
label var resident_count_home "#residents in origin subzone"
label var resident_count_dest "#residents in destination subzone"

gen lnpop_origin = ln(1+resident_count_home)
label var lnpop_origin "Log population in origin subzone"

gen lnpop_dest = ln(1+resident_count_dest)
label var lnpop_dest "Log population in destination subzone"

gen lndevice_origin = ln(basecount)
label var lndevice_origin "Log devices in origin subzone"

gen lndevice_dest = ln(dest_basecount)
label var lndevice_dest "Log devices in destination subzone"

*==================
* Weather Variables
*==================
rename rain_home rain_origin
label var rain_origin "Rainfall (mm) in origin subzone-date"
label var rain_dest "Rainfall (mm) in destination subzone-date"

*==================
* Housing Variables
*==================
forval i = 3/5 {
	rename rm`i'_home rm`i'_origin 
	label var rm`i'_origin "%residents living in `i'-room flats in origin subzone"
	label var rm`i'_dest "%residents living in `i'-room flats in destination subzone"
}

ren rm12_home rm12_origin 
label var rm12_origin "%residents living in 1/2-room flats in origin subzone"
label var rm12_dest "%residents living in 1/2-room flats in destination subzone"

ren private_home private_origin 
label var private_origin "%residents living in private house in origin subzone"
label var private_dest "%residents living in private house in destination subzone"

label var rm12_rental_pct_home "%house units that are 1to2 room public rentals in origin subzone"
label var rm12_rental_pct_dest "%house units that are 1to2 room public rentals in destination subzone"
label var rental_pct_home "%house units that are public rentals in origin subzone"
label var rental_pct_dest "%house units that are public rentals in destination subzone"

*=======================================
* Scale housing variables to percentages
*=======================================
foreach var of varlist rm12_* private_* {
	replace `var' = `var'/100
}

*===============
* Race Variables
*===============
gen notchinese_o = (100 - chinese_o)/100
label var notchinese_o "Proportion non-Chinese in origin"

gen notchinese_d = (100 - chinese_d)/100
label var notchinese_d "Proportion non-Chinese in destination"

*=================
* Income Variables
*=================
replace wpsm_home = wpsm_home/1000
replace wpsm_dest = wpsm_dest/1000

gen eudist = abs(wpsm_home/1000 - wpsm_dest/1000)
label var eudist "Euclidean distance in income (PSM) between origin and destination"

foreach var of varlist wpsm_home wpsm_dest {
	qui su `var', d
	gen p25_`var' = (`var' < `r(p25)') if ~missing(`var')
	gen p75_`var' = (`var' < `r(p75)') if ~missing(`var')
}
label var p25_wpsm_home "==1 if origin income below 25th percentile"
label var p25_wpsm_dest "==1 if destination income below 25th percentile"
label var p75_wpsm_home "==1 if origin income below 75th percentile"
label var p75_wpsm_dest "==1 if destination income below 75th percentile"

gen y = ln(inflow)
label var y "Log OD inflow"

*===================================
* MAIN SEGREGATION/MISMATCH MEASURES
*===================================

*==================================
* Poverty Mismatch (1-2 room flats)
*==================================
gen mismatch_rm12_p2r = rm12_origin * (1 - rm12_dest)
label var mismatch_rm12_p2r "Poor→Rich poverty mismatch (1-2 room flats)"

gen mismatch_rm12_r2p = rm12_dest * (1 - rm12_origin)
label var mismatch_rm12_r2p "Rich→Poor poverty mismatch (1-2 room flats)"

gen mismatch_rm12 = mismatch_rm12_p2r + mismatch_rm12_r2p
label var mismatch_rm12 "Mismatch in poverty b/w origin and destination"

*==================================
* Wealth Mismatch (private housing)
*==================================
gen mismatch_pri = (private_origin) * (1 - private_dest) + (private_dest) * (1 - private_origin)
label var mismatch_pri "Mismatch in wealth b/w origin and destination"

*=====================
* Race/Ethnic Mismatch
*=====================
gen mismatch_race_m2c = notchinese_o*(1-notchinese_d)
label var mismatch_race_m2c "Minority→Majority ethnic mismatch"

gen mismatch_race_c2m = notchinese_d*(1-notchinese_o)
label var mismatch_race_c2m "Majority→Minority ethnic mismatch"

gen mismatch_race = mismatch_race_m2c + mismatch_race_c2m
label var mismatch_race "Mismatch in race b/w origin and destination"

gen lmismatch_race = ln(mismatch_race)

*========================
* Public Rentals Mismatch
*========================
gen mismatch_pubrentals = (rental_pct_home) * (1 - rental_pct_dest) + (rental_pct_dest) * (1 - rental_pct_home)
label var mismatch_pubrentals "Mismatch in HDB public rentals b/w origin and destination"

*==================================
* Income Mismatch (25th percentile)
*==================================
gen mismatch_p25_p2r = p25_wpsm_home * (1 - p25_wpsm_dest)
label var mismatch_p25_p2r "Poor→Rich income mismatch (25th percentile)"

gen mismatch_p25_r2p = p25_wpsm_dest * (1- p25_wpsm_home)
label var mismatch_p25_r2p "Rich→Poor income mismatch (25th percentile)"

gen mismatch_p25 = mismatch_p25_p2r + mismatch_p25_r2p
label var mismatch_p25 "Income mismatch b/w origin and destination (25th percentile)"

gen mismatch_p75_p2r = p75_wpsm_home * (1 - p75_wpsm_dest)
label var mismatch_p75_p2r "Non-rich→Rich income mismatch (75th percentile)"

gen mismatch_p75_r2p = p75_wpsm_dest * (1- p75_wpsm_home)
label var mismatch_p75_r2p "Rich→Non-rich income mismatch (75th percentile)"

gen mismatch_p75 = mismatch_p75_r2p + mismatch_p75_p2r
label var mismatch_p75 "Income mismatch b/w origin and destination (75th percentile)"
