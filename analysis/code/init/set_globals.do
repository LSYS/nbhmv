global graphsavedir ../results/figures/
global graphformats png pdf eps
global tabsavedir ../results/tables/
global logsavedir ./logs/

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
    schools ///
    hawkers ///
    shopping_malls

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

global exc_emp !inlist(dest, 8, 11, 29, 37, 38, 50, 57, 150, 157, 190, 200, 248)

*================
* Variable labels
*================
#delimit;
global coeff_labels
	"
    mismatch_p25 "Price \pxor{}"
	1.mismatch_p25 "Price \pxor{}"
    mismatch_p75 "Price \pxor{}"
	1.mismatch_p75 "Price \pxor{}"
	1.mismatch_p25_p2r " LP $\rightarrow$ HP"
	1.mismatch_p25_r2p " HP $\rightarrow$ LP"
    1.mismatch_p75_p2r " LP $\rightarrow$ HP"
    1.mismatch_p75_r2p " HP $\rightarrow$ LP"
    1.mismatch_p25#1.ncentral_d "Price \pxor{} $\times$ Non-central destination"
	1.mismatch_p75#1.ncentral_d	"Price \pxor{} $\times$ Non-central destination"
    mismatch_race_m2c   "Mnr $\rightarrow$ Maj"
    mismatch_race_c2m   "Maj $\rightarrow$ Mnr"
    eudist "$|\text{Price}_o - \text{Price}_d|$"
    lmismatch_race "log(Ethnic \pxor{})"
    mismatch_race   "Ethnic \pxor{}"
    1.ncentral_d#c.mismatch_race "Ethnic \pxor{} $\times$ Non-central destination"
    wpsm_home                   "Price in origin"
    wpsm_dest                   "Price in destination"
    1.cny_sat_sun#c.wpsm_home   "Price in origin $ \times \mathds{1}^{\text{CNY}} $"
    1.cny_sat_sun#c.wpsm_dest   "Price in destination $ \times \mathds{1}^{\text{CNY}} $"
    "
;
#delimit cr


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
assert_macros "dist popden demo rain landarea poi business se exc_emp"

// Check specification macros
assert_macros "s1 s2 s3 s4 s5"

assert_macros "MSIZE MLWIDTH CIWIDTH YLABSIZE XLABSIZE LEGEND_SIZE REFLINE_WIDTH"
