# Constructing panel of daily neighborhood O-D linkages w/ demogarphics & POIs

![Build dependency graph](./assets/build-pipeline.png)

## Setup Requirements

Set up `venv` from `root` using 

```bash
make setup
```

which uses dependencies listed in [`requirements.txt`](https://github.com/LSYS/nbhmv/blob/main/assets/requirements.txt).

Do a 

```
make data
```

to build `cd-panel.csv` using [runpynb](https://pypi.org/project/runpynb/) to execute relevant notebooks in sequence in a `venv` (see dependencies in [requirements.txt](https://github.com/LSYS/nbhmv/blob/main/assets/requirements.txt)) and the `make` recipe:

```make

```
.PHONY: data
data: ## Run all notebooks in sequence with output versions (-o)
	@echo "==> Executing notebooks with runpynb in $(VENVPATH)"
	. $(ACTIVATE_PATH) && \
	runpynb -s -o \
	  0-get-subzones-from-records.ipynb \
	  1-get-IDs.ipynb \
	  2-get-devicehome.ipynb \
	  3-get-movementcount.ipynb \
	  4-postal_to_2014subzonename.ipynb \
	  5-compile-POI-count.ipynb \
	  6a-clean-housetype.ipynb \
	  6b-map-weather.ipynb \
	  7-merge.ipynb
	mv *-out.ipynb logs/
---

## Build Order

| Step | Script                              | Purpose                                         | Key Input(s)                                        | Key Output(s)                                          |
|------|-------------------------------------|-------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------|
| 0    | `0-get-subzones-from-records.py`   | Extract unique subzones with integer IDs        | `sg_subzones_devices/`                              | `citydata-subzones.csv`                               |
| 1    | `1-get-IDs.py`                     | Map device hash IDs to integer IDs              | `tt_appearances_areadate/device-appearances-chunk*.csv.gz` | `deviceID-list/deviceID-list-chunk*.csv.gz`           |
| 2    | `2-get-devicehome.py`              | Assign home location to each device             | `citydata-subzones.csv`, `deviceID-list/`, `sg_subzones_devices/` | `device-area-maxcount.csv.gz`                         |
| 3    | `3-get-movementcount.py`           | Compute directional flows per day (home → dest) | `device-area-maxcount.csv.gz`                       | `daily-movecount.csv.gz`                              |
| 4    | `4-postal_to_2014subzonename.py`   | Postal-to-subzone name crosswalk (2014)         | `buildings.json`, subzone boundaries                 | `fixed_postal_subzone_xwalk.csv`                      |
| 5    | `5-compile-POI-count.py`           | Count POIs per subzone (enhanced with hawkers & malls) | Various POI sources, OSM data                       | `subzones-poi-count.csv`                              |
| 6a   | `6a-clean-housetype.py`            | Clean housing type statistics                   | `singapore-residents-by-subzone-and-type-of-dwelling-2011-2019.csv` | `htype.csv`                              |
| 6b   | `6b-map-weather.py`                | Crosswalk subzones to weather stations          | Subzone shapefiles, SWEAT metadata                  | `subzones2014-weatherstation-crosswalk.csv`           |
| 7    | `7-merge.py`                       | Merge all features into panel dataset           | All above outputs                                   | `cd-panel.csv`                    

Final output:  
**`cd-panel.csv`** — daily panel with device counts, mobility flows, housing type, POIs, and weather by subzone, etc.

## 📘 Supplementary Script Descriptions

---

### 📄 `get-subzones-from-records.ipynb`

**Purpose**: Extracts the list of subzones found in the Citydata raw records and assigns each a unique integer ID.

**Output**: `intermediate-files/citydata-subzones.csv`

Example:

| subzone       | areaid |
|---------------|--------|
| Admiralty     | 0      |
| Airport Road  | 1      |
| Alexandra Hill| 2      |
| ...           | ...    |
| Yuhua West    | 299    |
| Yunnan        | 300    |


---

### 📄 `get-IDs.ipynb`

**Purpose**: Maps each unique hashed device ID to a numeric integer ID (`xid`).

**Output**: `intermediate-files/deviceID-list/deviceID-list-chunk*.csv.gz`

Example:

| hashid                                  | xid       |
|----------------------------------------|-----------|
| M200M21yaHQybmd0OTpoNzQ5dTFwYjMzN2g=    | 0         |
| M200M21yaHQybmd0cDpoNzQ5dHVwYjMzN3Q=    | 1         |
| ...                                     | ...       |
| dnZzbjBmYzBpajl2OmNsYTVzdWV0cjFwNDk=    | 17492187  |
| dnZzdDFkZHQ2dGxpOjNpYzUyY3I2NzVrODE=    | 17492188  |

---

### 📄 `get-devicehome.ipynb`

**Purpose**: Infers home based on modal appearances for each device.  
Both `device` and `area_id` are anonymized integer IDs.

**Outputs (in `intermediate-files/`)**:
- `device-xid.npy`
- `subzones-xid.npy`
- `device-area-maxcount.csv.gz`

Example (`device-area-maxcount.csv.gz`):

| device_xid | area_id | count |
|------------|---------|-------|
| 133438     | 0       | 89    |
| 260901     | 0       | 12    |
| 440462     | 0       | 86    |
| ...        | ...     | ...   |
| 17438569   | 300     | 1     |
| 17486911   | 300     | 1     |

E.g., device `440462` appears in area `0` a total of 86 times during the sample period.


---

### 📄 `get-movementcount.ipynb`

**Purpose**: Computes daily directional movement (counts) between home and visited areas.  
Each row represents a `(date [Unix time], origin [home], destination)` tuple.

**Output**: `daily-movecount.csv.gz`

Example:

| date       | home | area_id | inflow_count |
|------------|------|---------|--------------|
| 1577808000 | 0    | 0       | 25           |
| 1577808000 | 0    | 8       | 1            |
| 1577808000 | 0    | 9       | 2            |
| ...        | ...  | ...     | ...          |
| 1585584000 | 300  | 297     | 3            |
| 1585584000 | 300  | 298     | 24           |
| 1585584000 | 300  | 299     | 12           |
| 1585584000 | 300  | 300     | 2007         |
