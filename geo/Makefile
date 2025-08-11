.DEFAULT_GOAL := help

VENVPATH ?= venv_nbhmv

ifeq ($(OS),Windows_NT)
	ACTIVATE_PATH := ../$(VENVPATH)/Scripts/activate
else
	ACTIVATE_PATH := ../$(VENVPATH)/bin/activate
endif

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
    ./pa-price.ipynb \
    ./bootstrap-r2.ipynb \
    ./get-devicecount-subzone-day.ipynb \
    ./choropleth-devices.ipynb \
    ./choropleth-income.ipynb \
    ./choropleth-price.ipynb \
    ./borders.ipynb \
    ./lower-vs-higher-ptiles.ipynb \
    ./ping-variation.ipynb

.PHONY: lint-notebooks
lint-notebooks: ## Run nbqa pyflakes and black --check on selected notebooks
	@echo "==> NBQA pyflakes"
	. $(ACTIVATE_PATH) && nbqa pyflakes $(NOTEBOOKS)
	@echo "==> NBQA black --check"
	. $(ACTIVATE_PATH) && nbqa black $(NOTEBOOKS)

########################################################################
# Run notebooks
########################################################################
.PHONY: analysis
analysis: ## Run all notebooks with output versions (-o)
	@echo "==> Executing notebooks with runpynb in $(VENVPATH)"
	. $(ACTIVATE_PATH) && \
	runpynb -s -o \
		pa-price.ipynb \
	    bootstrap-r2.ipynb \
	    get-devicecount-subzone-day.ipynb \
	    choropleth-devices.ipynb \
	    choropleth-income.ipynb \
	    choropleth-price.ipynb \
	    borders.ipynb \
	    lower-vs-higher-ptiles.ipynb \
	    ping-variation.ipynb
	mv *-out.ipynb logs/


########################################################################
# Symlink
# Link assets into input/
########################################################################
SYMLINK_OPTS = --symbolic --force --verbose
.PHONY: link
link: ## Symlink assets
	@echo "==> $@"
	@echo "Cleaning existing symlinks in input/..."
	@find input -type l -delete 2>/dev/null || true
	@echo "Making symlinks..."
	cd input && ln $(SYMLINK_OPTS) ../../build/cd-panel-labels.csv .
	cd input && ln $(SYMLINK_OPTS) ../../build/cd-panel.csv .
	cd input && ln $(SYMLINK_OPTS) ../../build/intermediate-output/citydata-subzones.csv .
	cd input && ln $(SYMLINK_OPTS) ../../build/intermediate-output/propprice-subzone.csv .
	cd input && ln $(SYMLINK_OPTS) ../../build/intermediate-output/htype.csv .
	cd input && ln $(SYMLINK_OPTS) ../../build/preprocessed-data/realis_with_postal_code_complete.csv.gz .
	cd input && ln $(SYMLINK_OPTS) ../../build/preprocessed-data/hdb_saledata_with_geodata.csv.gz .
	cd input && ln $(SYMLINK_OPTS) ../../build/raw-data/master-plan-2014-subzone-boundary-no-sea/ .
	cd input && ln $(SYMLINK_OPTS) ../../build/raw-data/master-plan-2014-planning-area-boundary-no-sea/ .
	cd input && ln $(SYMLINK_OPTS) ../../build/raw-data/master-plan-2014-region-boundary-no-sea/ .
	cd input && ln $(SYMLINK_OPTS) ../../build/raw-data/resident-working-persons-aged-15-years-over-by-planning-area-gross-monthly-income-from-work-2015/ .
	cd input && ln $(SYMLINK_OPTS) ../../build/raw-data/sg_subzones_devices/sg_subzones_devices/ .
	@echo "==> Done."

########################################################################
# Other utilities
########################################################################
.PHONY: help
help: ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'