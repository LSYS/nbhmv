version 13.1

capture program drop price_tier_cache
program define price_tier_cache
	syntax , ORIGIN(varname) DEST(varname) PERCENTILES(numlist integer >0 <100)
	///////////////////////////////////////////////////////////////////////////////
	// Description:
	// ------------
	//		Precomputes the price cutoff for each percentile in a list. Saves
	//		make_price_tiers from rebuilding the neighborhood list on every call.
	//
	// Syntax:
	// -------
	//		price_tier_cache, origin(var) dest(var) percentiles(numlist)
	//
	// Sets:
	// --------
	//		globals		PTC_<percentile> per cutoff, PTC_N for the count
	//
	// MWE:
	// ----
	//		price_tier_cache, origin(wpsm_home) dest(wpsm_dest) percentiles(1/99)
	//////////////////////////////////////////////////////////////////////////////
	macro drop PTC_*

	preserve
		qui stack `origin' `dest', into(_wpsm_tier) clear
		qui keep _wpsm_tier
		qui drop if missing(_wpsm_tier)
		qui duplicates drop
		qui count
		local n_nbh = r(N)
		foreach k of local percentiles {
			qui centile _wpsm_tier, centile(`k')
			global PTC_`k' = r(c_1)
		}
	restore

	global PTC_N = `n_nbh'

	local nk : word count `percentiles'
	di as txt "price_tier_cache: cached " as result "`nk'" ///
	   as txt " cutoffs over " as result `n_nbh' as txt " priced neighborhoods"
end
