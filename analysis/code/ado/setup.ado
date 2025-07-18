cap program drop setup
program define setup
	args ssc_packages

	if "`ssc_packages'"!="" {
		dis "Installing ssc packages, please wait..."
		local i = 1

		foreach pkg in `ssc_packages' {
			capture which `pkg'
			if _rc==111 { 
				cap ssc install `pkg'

				if _rc==601 { 
					noisily _dots `i' 1
					local error_pkg `error_pkg' `pkg'
				}
				else { 
					noisily _dots `i' 0
				}
			}
			else { /* pkg already installed */
				qui ssc install `pkg', replace
				noisily _dots `i' 0
			}
		local ++i
		}

		if "`error_pkg'"!="" {
			dis ""
			noisily dis "These packages failed to install: `error_pkg'"			
		}

		dis ""
		noisily dis in green "Setup of requirements completed."	
	}
	else {
		noisily dis "No requirements stated..."
	}
end
