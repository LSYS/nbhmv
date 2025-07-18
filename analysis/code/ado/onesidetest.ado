capture program drop onesidetest
program define onesidetest, rclass
	args varname side round star
	if ("`e(cmd)'"!="regress") & ("`e(cmd)'"!="reghdfe") {
		error 301
	}

	scalar var_coef = _b[`varname']
	scalar var_se = _se[`varname']
	scalar tstat = var_coef/var_se

	if "`side'"=="right" {
		scalar pval = ttail(e(df_r), tstat)
	}
	else if "`side'"=="left" {
		scalar pval = 1 - ttail(e(df_r), tstat)
	}
	else {
		dis in red "Choose 'left' or 'right' side."
		exit
	}
	scalar list var_coef var_se tstat pval

	if "`star'"=="star" {
		if pval < 0.01 { /* sig. at 1 percent */
			local StatStars = string(round(pval, `round')) + "\sym{***}"
		}
		else if 0.01 <= pval < 0.05 { /* sig. at 5 percent */
			local StatStars = string(round(pval, `round')) + "\sym{**}"
		}
		
		else if 0.05 <= pval < 0.1 { /* sig. at 10 percent */
			local StatStars = string(round(pval, `round')) + "\sym{*}"
		}
		
		else if 0.1 <= pval {
			local StatStars = string(round(pval, `round'))
		}
		return local pval `StatStars'
	}
	else { /* just check for rounding, return, and end */
		if "`round'"!= "" {
			return local pval = round(pval, `round')
		}	
		else {
			return local pval = pval
		}	
	}
end


/*
MWE
---
. sysuse auto
. reg price weight length
. onesidetest length right
  var_coef = -97.960312
    var_se =  39.174598
     tstat =  -2.500608
      pval =  .99264594
*/
