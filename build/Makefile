.DEFAULT_GOAL := help

VENVPATH ?= venv_nbhmv

ifeq ($(OS),Windows_NT)
	ACTIVATE_PATH := ../$(VENVPATH)/Scripts/activate
else
	ACTIVATE_PATH := ../$(VENVPATH)/bin/activate
endif

.PHONY: data
data: ## Run all notebooks in sequence with output versions (-o)
	@echo "==> Executing notebooks with runpynb in $(VENVPATH)"
	. $(ACTIVATE_PATH) && \
	runpynb -s -o \
	  7-merge.ipynb
	mv *-out.ipynb logs/
	
# .PHONY: data
# data: ## Run all notebooks in sequence with output versions (-o)
# 	@echo "==> Executing notebooks with runpynb in $(VENVPATH)"
# 	. $(ACTIVATE_PATH) && \
# 	runpynb -s -o \
# 	  0-get-subzones-from-records.ipynb \
# 	  1-get-IDs.ipynb \
# 	  2-get-devicehome.ipynb \
# 	  3-get-movementcount.ipynb \
# 	  4-postal_to_2014subzonename.ipynb \
# 	  5-compile-POI-count.ipynb \
# 	  6a-clean-housetype.ipynb \
# 	  6b-map-weather.ipynb \
# 	  7-merge.ipynb
# 	mv *-out.ipynb logs/

# .PHONY: data
# data: ## Run all notebooks in sequence with output versions (-o)
# 	@echo "==> Executing notebooks with runpynb in $(VENVPATH)"
# 	. $(ACTIVATE_PATH) && \
# 	runpynb -s -o \
# 	  0a-get-devicecount-subzone-day.ipynb \
# 	  0b-get-subzones-from-records.ipynb \
# 	  1-get-device-appearances-count.ipynb \
# 	  2-get-IDs.ipynb \
# 	  3-get-devicehome.ipynb \
# 	  4-postal_to_2014subzonename.ipynb \
# 	  5a-clean-housetype.ipynb \
# 	  5b-compile-POI-count.ipynb \
# 	  5c-map-weather.ipynb \
# 	  5d-get-movementcount.ipynb \
# 	  6-merge.ipynb

########################################################################
# Jupytext sync to .py
########################################################################
.PHONY: sync-setup
sync-setup: ## Set up jupytext sync for all notebooks (creates .py files in logs/)
	@echo "==> Setting up jupytext sync in $(VENVPATH)"
	@mkdir -p logs
	. $(ACTIVATE_PATH) && \
	jupytext --set-formats ipynb,logs//py *.ipynb
	@echo "All notebooks now synced with Python files in logs/"

.PHONY: sync
sync: ## Manually sync w/ Jupytext all paired notebooks with their .py files
	@echo "==> Syncing notebooks with Python files"
	. $(ACTIVATE_PATH) && \
	jupytext --sync *.ipynb
	@echo "Sync complete"

########################################################################
# Other utilities
########################################################################
.PHONY: help
help: ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'