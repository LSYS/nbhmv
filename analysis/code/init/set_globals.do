global graphsavedir ../results/figures/
global graphformats png pdf eps
global tabsavedir ../results/tables/

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


*================
* Variable labels
*================
#delimit;
global coeff_labels
	"
	mismatch_p25 "Income \pxor{}"
	mismatch_p75 "Income \pxor{}"
	1.mismatch_p25_p2r "P $\rightarrow$ NP"
	1.mismatch_p25_r2p "NP $\rightarrow$ P"
	1.mismatch_p25#1.ncentral_d	"Income \pxor{} $\times$ Non-central destination"
    mismatch_race_m2c   "Mnr $\rightarrow$ Maj"
    mismatch_race_c2m   "Maj $\rightarrow$ Mnr"
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
assert_macros "dist popden demo rain landarea poi business se"

// Check specification macros
assert_macros "s1 s2 s3 s4 s5"

*======================================
* Linking scripts to exhibits numbering
*======================================
// program define make_fig4a
//     do code/mismatch/pxor_wpsm.do
// end

// program define make_fig4b
//     do code/mismatch/pxor_wpsm_r2p_p2r.do
// end

// program define make_fig6a
// 	do code/mismatch/pxor_race.do
// end

// program define make_fig6b
//     do code/mismatch/pxor_race_asymmetry.do
// end

// program define make_fig7
// 	do code/mismatch/pxor_wpsm_ncentral.do
// end

// program define make_fig8
// 	do code/cutoffs/cutoffs_pxor_wpsm.do
// 	do code/cutoffs/graph_cutoffs_pxor_wpsm.do
// end 
