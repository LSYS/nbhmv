.DEFAULT_GOAL := help

VENVPATH ?= venv_nbhmv

.PHONY: data
data: ## Run all notebooks in sequence with output versions (-o)
	@echo "==> Executing notebooks with runpynb in $(VENVPATH)"
	. $(ACTIVATE_PATH) && \
	runpynb -s -o \
	  1-get-device-appearances-count.ipynb

# .PHONY: data
# data: ## Run all notebooks in sequence with output versions (-o)
# 	@runpynb -s -o \
# 	  0a-get-devicecount-subzone-day.ipynb \
# 	  0b-get-subzones-from-records.ipynb \
# 	  1-get-device-appearances-count.ipynb \
# 	  2-get-IDs.ipynb \
# 	  3-get-devicehome.ipynb

########################################################################
# Other utilities
########################################################################
.PHONY: clean
clean: ## Clean all symlinks aux reports
clean: clean_sl clean_sl_task

.PHONY: help
help: ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'