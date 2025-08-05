.DEFAULT_GOAL := help

VENVPATH ?= venv_nbhmv

ifeq ($(OS),Windows_NT)
	ACTIVATE_PATH := ../$(VENVPATH)/Scripts/activate
else
	ACTIVATE_PATH := ../$(VENVPATH)/bin/activate
endif

.PHONY: analysis
analysis: ## Run all notebooks with output versions (-o)
	@echo "==> Executing notebooks with runpynb in $(VENVPATH)"
	. $(ACTIVATE_PATH) && \
	runpynb -o \
	  bootstrap-r2.ipynb \
	  borders.ipynb \
	  choropleth-devices.ipynb \
	  choropleth-income.ipynb \
	  choropleth-price.ipynb \
	  get-devicecount-subzone-day.ipynb \
	  lower-vs-higher-ptiles.ipynb \
	  pa-price.ipynb
	mv *-out.ipynb logs/

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
# Notebook lint
########################################################################
NOTEBOOKS := \
    ./bootstrap-r2.ipynb \
    ./borders.ipynb \
    ./choropleth-devices.ipynb \
    ./choropleth-income.ipynb \
    ./choropleth-price.ipynb \
    ./get-devicecount-subzone-day.ipynb \
    ./lower-vs-higher-ptiles.ipynb \
    ./pa-price.ipynb

.PHONY: lint-notebooks
lint-notebooks: ## Run nbqa pyflakes and black --check on selected notebooks
	@echo "==> NBQA pyflakes"
	. $(ACTIVATE_PATH) && nbqa pyflakes $(NOTEBOOKS)
	@echo "==> NBQA black --check"
	. $(ACTIVATE_PATH) && nbqa black $(NOTEBOOKS)

########################################################################
# Other utilities
########################################################################
.PHONY: help
help: ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'