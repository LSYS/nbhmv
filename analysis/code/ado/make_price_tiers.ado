version 13.1

capture program drop make_price_tiers
program define make_price_tiers, rclass
	syntax , PERCENTILE(real)          ///
	         ORIGIN(varname)           ///
	         DEST(varname)             ///
	         GENORIGIN(name)           ///
	         GENDEST(name)
	///////////////////////////////////////////////////////////////////////////////
	// Description:
	// ------------
	//		Makes LP/HP price tier dummies from one cutoff over the unique priced
	//		neighborhoods, pooling origins and destinations. Eq. (2) in the paper.
	//
	//		Looks up the cutoff if price_tier_cache has run, else builds it.
	//
	// Syntax:
	// -------
	//		make_price_tiers, percentile(#) origin(var) dest(var) ///
	//		                  genorigin(newvar) gendest(newvar)
	//
	// Returns:
	// --------
	//		r(cutoff)	the cutoff applied
	//		r(n_nbh)	number of unique priced neighborhoods
	//
	// MWE:
	// ----
	//		make_price_tiers, percentile(25) origin(wpsm_home) dest(wpsm_dest) ///
	//		                  genorigin(p25_wpsm_home) gendest(p25_wpsm_dest)
	//////////////////////////////////////////////////////////////////////////////
	local pkey = `percentile'
	if "${PTC_`pkey'}" != "" {
		local cut   = ${PTC_`pkey'}
		local n_nbh = $PTC_N
	}
	else {
		preserve
			qui stack `origin' `dest', into(_wpsm_tier) clear
			qui keep _wpsm_tier
			qui drop if missing(_wpsm_tier)
			qui duplicates drop
			qui count
			local n_nbh = r(N)
			qui centile _wpsm_tier, centile(`percentile')
			local cut = r(c_1)
		restore
	}

	cap drop `genorigin'
	cap drop `gendest'
	qui gen byte `genorigin' = (`origin' < `cut') if ~missing(`origin')
	qui gen byte `gendest'   = (`dest'   < `cut') if ~missing(`dest')

	return scalar cutoff = `cut'
	return scalar n_nbh  = `n_nbh'
end
