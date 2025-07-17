# Constructing panel of daily neighborhood O-D linkages w/ demogarphics & POIs


Final output:  
**`cd-panel.csv`** — daily panel with device counts, mobility flows, housing type, POIs, and weather by subzone, etc.

---

## 🚀 Build Order

| ix   | Script                              | Purpose                                         | Key Input(s)                                        | Key Output(s)                                          |
|------|-------------------------------------|-------------------------------------------------|-----------------------------------------------------|--------------------------------------------------------|
| 0a   | `0a_get-devicecount-subzone-day.ipynb`      | Count Android/iOS devices per subzone per day   | `sg_subzones_devices/`                              | `devicecount-subzone-day.csv`                         |
| 0b   | `0b-get-subzones-from-records.ipynb`        | Extract unique subzones with integer IDs        | `sg_subzones_devices/`                              | `citydata-subzones.csv`                               |
| 1    | `1-get-device-appearances-count.ipynb`      | Count total appearances per device              | `sg_subzones_devices/`                              | `tt_appearances_areadate/device-appearances-chunk*.csv.gz` |
| 2    | `2-get-IDs.ipynb`                           | Map device hash IDs to integer IDs              | `device-appearances-chunk*.csv.gz`                  | `deviceID-list/deviceID-list-chunk*.csv.gz`           |
| 3    | `3-get-devicehome.ipynb`                    | Assign home location to each device             | `citydata-subzones.csv`, `deviceID-list/`, `sg_subzones_devices/` | `device-area-maxcount.csv.gz`                         |
| 4    | `4-postal_to_2014subzonename.ipynb`         | Postal-to-subzone name crosswalk (2014)         | Postal shapefile or raw xwalk table                 | `postal_to_2014subzonename_xwalk.csv`                 |
| 5a   | `5a-clean-housetype.ipynb`                  | Clean housing type statistics                   | `planning-area-subzone-age-group-sex-and-type-of-dwelling-june-2011-2019.csv` | `htype.csv`                              |
| 5b   | `5b-compile-POI-count.ipynb`                | Count POIs per subzone                          | `postal_to_2014subzonename_xwalk.csv`               | `subzones-poi-count.csv`                              |
| 5c   | `5c-map-weather.ipynb`                      | Crosswalk subzones to weather stations          | Subzone shapefiles, SWEAT metadata                  | `subzones2014-weatherstation-crosswalk.csv`           |
| 5d   | `5d-get-movementcount.ipynb`                | Compute directional flows per day (home → dest) | `device-area-maxcount.csv.gz`                       | `daily-movecount.csv.gz`                              |
| 6    | `6-merge.ipynb`                             | Merge all features into panel dataset           | All above outputs                                   | `cd-panel.csv`                                        |

## 📘 Script Descriptions and Output Examples

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

---

### 📄 `get-devicehome.ipynb`

**Purpose**: Determines the area with the most appearances for each device.  
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

> ⚠️ See also: `*_get-devicehome.ipynb` (previous failed version).  
> That version outputs `path_area_date.csv`, e.g.:

| path                                               | subzone_name     | date       |
|----------------------------------------------------|------------------|------------|
| ../raw-files/sg_subzones_devices/2020-03-07/swiss… | swiss club       | 2020-03-07 |
| ../raw-files/sg_subzones_devices/2020-03-07/keat…  | keat hong        | 2020-03-07 |
| ../raw-files/sg_subzones_devices/2020-03-07/port…  | port             | 2020-03-07 |
| ../raw-files/sg_subzones_devices/2020-03-07/alex…  | alexandra north  | 2020-03-07 |
| ../raw-files/sg_subzones_devices/2020-03-07/tanj…  | tanjong pagar    | 2020-03-07 |

---

### 📄 `get-devicecount-subzone-day.ipynb`

**Purpose**: Counts the number of Android and iOS devices observed in each subzone per day.

**Output**: `devicecount-subzone-day.csv`

Example:

| subzone         | date       | android_count | ios_count |
|-----------------|------------|----------------|-----------|
| admiralty       | 2020-01-01 | 63             | 10        |
| airport road    | 2020-01-01 | 54             | 3         |
| alexandra hill  | 2020-01-01 | 1080           | 203       |
| alexandra north | 2020-01-01 | 362            | 74        |
| ...             | ...        | ...            | ...       |
| yunnan          | 2020-03-31 | 2662           | 896       |

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
| ...                                    | ...       |
| dnZzbjBmYzBpajl2OmNsYTVzdWV0cjFwNDk=    | 17492187  |
| dnZzdDFkZHQ2dGxpOjNpYzUyY3I2NzVrODE=    | 17492188  |

---

### 📄 `get-device-appearances-count.ipynb`

**Purpose**: Computes the total number of appearances per device across all areas and dates in the sample period.

**Output**: `intermediate-files/tt_appearances_areadate/device-appearances-chunk*.csv.gz`

Example:

| deviceID                              | tt_appearances_areadate |
|--------------------------------------|--------------------------|
| OHZ2YzQ2M29nM2gydTphbnU5ODBpbWJxcmRk | 5538                     |
| MWxuM2Rqa2xlNjA0NjozMHVtdGcyMThsbmVn | 5020                     |
| ZWdiNmdwZXVibnRyaTo2YWlsbjc2cm10ZXUw | 4934                     |
| ...                                  | ...                      |

---

### 📄 `missing-subzones.ipynb`

**Purpose**: Diagnostic tool to identify dates when no devices were recorded in a given subzone.  
Useful for spotting gaps in coverage due to zero-observation days.

**Output**: None (prints/report only).
