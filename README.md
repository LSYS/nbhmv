# 📦 Replication Package: Mobility Panel Construction from Device-Level Logs

This repository contains code and build scripts to construct a subzone-level panel dataset from passively collected mobile location records in Singapore. Each step processes raw location or contextual data to generate intermediate outputs, culminating in a merged panel suitable for analysis.

Final output:  
**`cd-panel.csv`** — daily panel with device counts, mobility flows, housing type, POIs, and weather by subzone.

---

## 🚀 Build Order

| Step | Script | Purpose | Key Output |
|------|--------|---------|------------|
| 0a   | `0a_get-devicecount-subzone-day.ipynb` | Count daily Android/iOS devices per subzone | `devicecount-subzone-day.csv` |
| 0b   | `0b-get-subzones-from-records.ipynb` | Get unique subzones from raw records | `citydata-subzones.csv` |
| 1    | `1-get-device-appearances-count.ipynb` | Count total device appearances in sample | `tt_appearances_areadate/device-appearances-chunk*.csv.gz` |
| 2    | `2-get-IDs.ipynb` | Map device hash IDs to integer IDs | `deviceID-list/deviceID-list-chunk*.csv.gz` |
| 3    | `3-get-devicehome.ipynb` | Assign device to most frequent subzone ("home") | `device-area-maxcount.csv.gz` |
| 4    | `4-postal_to_2014subzonename.ipynb` | Crosswalk between postal codes and 2014 subzones | `postal_to_2014subzonename_xwalk.csv` |
| 5a   | `5a-clean-housetype.ipynb` | Clean housing type data by subzone | `htype.csv` |
| 5b   | `5b-compile-POI-count.ipynb` | Aggregate POIs to subzones | `subzones-poi-count.csv` |
| 5c   | `5c-map-weather.ipynb` | Map subzones to weather stations | `subzones2014-weatherstation-crosswalk.csv` |
| 5d   | `5d-get-movementcount.ipynb` | Compute daily origin-destination inflows | `daily-movecount.csv.gz` |
| 6    | `6-merge.ipynb` | Merge all components into final panel | `cd-panel.csv` |

---

## 📁 Key Output Examples

### `device-area-maxcount.csv.gz`

Most frequent subzone ("home") per device:

| device_xid | area_id | count |
|------------|---------|-------|
| 133438     | 0       | 89    |
| 260901     | 0       | 12    |
| 440462     | 0       | 86    |

---

### `daily-movecount.csv.gz`

Directional flows from home → area on date (Unix timestamp):

| date       | home | area_id | inflow_count |
|------------|------|---------|--------------|
| 1577808000 | 0    | 0       | 25           |
| 1577808000 | 0    | 8       | 1            |
| 1585584000 | 300  | 297     | 3            |
| 1585584000 | 300  | 300     | 2007         |

---

### `devicecount-subzone-day.csv`

Daily subzone counts by OS:

| subzone         | date       | android_count | ios_count |
|-----------------|------------|----------------|-----------|
| admiralty       | 2020-01-01 | 63             | 10        |
| alexandra north | 2020-01-01 | 362            | 74        |

---

### `deviceID-list-chunk*.csv.gz`

Device hash → integer ID mapping:

| hashid                                  | xid       |
|----------------------------------------|-----------|
| M200M21yaHQybmd0OTpoNzQ5dTFwYjMzN2g=    | 0         |
| dnZzdDFkZHQ2dGxpOjNpYzUyY3I2NzVrODE=    | 17492188  |

---

## 📂 Notable Files and Structure

