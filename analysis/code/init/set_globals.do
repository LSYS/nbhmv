global graphsavedir ../results/figures/
global tabsavedir ../results/tables/

global coeff_labels `"mismatch_p25 "Income \pxor{}""'


global dist ///
    centroid_distance ///
    contiguous

global popden ///
    lnpop_origin ///
    lnpop_dest ///
    lndevice_origin ///
    lndevice_dest

global demo ///
    age_20_o ///
    age_20_d ///
    age20_40_o ///
    age20_40_d ///
    age65__o ///
    age65__d ///
    females_o ///
    females_d

global rain ///
    rain_dest ///
    rain_origin

global landarea ///
    area_o ///
    area_d

global poi ///
    libraries ///
    supermarkets ///
    parks ///
    preschools ///
    schzones ///
    silverzones ///
    sport_facilities ///
    transit ///
    tour ///
    schools

global business ///
    manufacturing ///
    construction ///
    services

global se cluster odid

* Specifications
global s1 i.date##c.($dist $popden $landarea ) i.date##i.pa_origin i.date##i.pa_dest /* baseline */
global s2 $s1 i.date##c.($demo) 	/* + Demo */
global s3 $s2 i.date##c.($business) /* + business */
global s4 $s3 i.date##c.($rain) 	/* + rainfall */
global s5 $s4 i.date##c.($poi)		/* + POIs */

*========================
* Coefplot Graph settings
*========================
global MSIZE huge
global MLWIDTH vvvthin
global CIWIDTH medthick
global YLABSIZE vlarge
global XLABSIZE medlarge
global LEGEND_SIZE large
global REFLINE_WIDTH thick

*================
* Validate macros
*================
// Check directory and label macros
assert_macros "graphsavedir tabsavedir coeff_labels"

// Check variable group macros
assert_macros "dist popden demo rain landarea poi business se"

// Check specification macros
assert_macros "s1 s2 s3 s4 s5"
