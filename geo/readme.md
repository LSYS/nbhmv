## Readme

A collection of Jupyter notebooks for analyzing prices, device counts, and geospatial data.

## Quick Start

1. Link required input files (from `../build`):
   ```bash
   make link
   ```
2. Run all scripts using [runpynb](https://pypi.org/project/runpynb/) to execute relevant notebooks in sequence in a `venv` (see dependencies in [requirements.txt](https://github.com/LSYS/nbhmv/blob/main/assets/requirements.txt)) and the `make` recipe::
   ```bash
   make analysis
   ```

This will execute all notebooks and save the output versions to the `logs/` directory.

![Build dependency graph](../assets/geo.png)
