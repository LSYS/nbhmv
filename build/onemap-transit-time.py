import geopandas as gpd
import janitor
import pandas as pd
import requests
import time
import yaml
from collections import Counter
from itertools import product
from pathlib import Path
from tqdm import tqdm

# Configs
ROUTE_URL = "https://www.onemap.gov.sg/api/public/routingsvc/route"
QUERY_DATE = "05-07-2026"
QUERY_TIME = "08:00:00"
SHP_PATH = "raw-data/master-plan-2014-subzone-boundary-no-sea/master-plan-2014-subzone-boundary-no-sea-shp.zip"
OUTPUT_PATH = Path("intermediate-output/transit_time_subzone.csv")
BATCH_SIZE = 500
SLEEP_BETWEEN = 0.25  # 300 calls/min limit


def get_transit_time(
    origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float, token: str
) -> tuple[int | None, str, float]:
    """Query OneMap for public transit travel time in seconds.

    Parameters
    ----------
    origin_lat : float
        Latitude of origin centroid.
    origin_lon : float
        Longitude of origin centroid.
    dest_lat : float
        Latitude of destination centroid.
    dest_lon : float
        Longitude of destination centroid.
    token : str
        OneMap bearer token.

    Returns
    -------
    duration : int or None
        Duration in seconds of the first itinerary, or None on failure.
    status : str
        Diagnostic status: "ok", "http_NNN", "timeout", "no_route", "exception:<class>".
    elapsed : float
        Wall-clock seconds for the request.
    """
    params = {
        "start": f"{origin_lat},{origin_lon}",
        "end": f"{dest_lat},{dest_lon}",
        "routeType": "pt",
        "date": QUERY_DATE,
        "time": QUERY_TIME,
        "mode": "TRANSIT",
        "numItineraries": "1",
    }
    t0 = time.time()
    try:
        resp = requests.get(
            ROUTE_URL,
            headers={"Authorization": token},
            params=params,
            timeout=30,
        )
        elapsed = time.time() - t0
        if resp.status_code != 200:
            return None, f"http_{resp.status_code}", elapsed
        data = resp.json()
        if "plan" not in data or not data["plan"].get("itineraries"):
            return None, "no_route", elapsed
        return data["plan"]["itineraries"][0]["duration"], "ok", elapsed
    except requests.exceptions.Timeout:
        return None, "timeout", time.time() - t0
    except Exception as e:
        return None, f"exception:{type(e).__name__}", time.time() - t0


# Get API key
with open("../secrets.yml") as f:
    TOKEN = yaml.safe_load(f)["onemap"]["token"]
print(f"Token loaded, length: {len(TOKEN)}")

# get locations to query
gdf_subzones = gpd.read_file(f"zip://{SHP_PATH}")
df_centroids = (
    gdf_subzones.to_crs(epsg=4326)
    .assign(
        lat=lambda df_: df_.geometry.centroid.y,
        lon=lambda df_: df_.geometry.centroid.x,
    )
    .select_columns(["SUBZONE_C", "SUBZONE_N", "lat", "lon"])
    .rename_columns({"SUBZONE_C": "subzone_code", "SUBZONE_N": "subzone_name"})
)

df_dist = pd.read_csv("preprocessed-data/distance_subzone_2014.csv", usecols=["Subzone Code_o"])
panel_codes = set(df_dist["Subzone Code_o"].unique())
df_centroids = df_centroids.query("subzone_code in @panel_codes").reset_index(drop=True)
print(f"{len(df_centroids)} subzones in panel")

# enumerate pairs for query
if OUTPUT_PATH.exists():
    df_done = pd.read_csv(OUTPUT_PATH)
    done_pairs = set(
        zip(
            df_done.loc[df_done["transit_time_sec"].notna(), "Subzone Code_o"],
            df_done.loc[df_done["transit_time_sec"].notna(), "Subzone Code_d"],
        )
    )
    df_done = df_done.dropna(subset=["transit_time_sec"]).reset_index(drop=True)
    print(f"Resuming: {len(done_pairs):,} successful pairs loaded")
else:
    df_done = pd.DataFrame()
    done_pairs = set()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

centroid_dict = df_centroids.set_index("subzone_code")[["lat", "lon"]].to_dict("index")
all_pairs = [
    (o, d)
    for o, d in product(df_centroids["subzone_code"], repeat=2)
    if o != d and (o, d) not in done_pairs
]
print(f"{len(all_pairs):,} pairs remaining")

# query
ERROR_LOG = Path("intermediate-output/onemap-errors.log")
ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
err_fh = open(ERROR_LOG, "a")
err_fh.write(f"\n=== Run started {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

results = []
batch_status = Counter()
batch_elapsed = []

for _i, (o, d) in enumerate(tqdm(all_pairs)):
    _o_info = centroid_dict[o]
    _d_info = centroid_dict[d]
    duration, status, elapsed = get_transit_time(
        _o_info["lat"], _o_info["lon"],
        _d_info["lat"], _d_info["lon"],
        TOKEN,
    )
    results.append({
        "Subzone Code_o": o,
        "Subzone Code_d": d,
        "transit_time_sec": duration,
    })
    batch_status[status] += 1
    batch_elapsed.append(elapsed)

    if status != "ok":
        err_fh.write(f"{time.strftime('%H:%M:%S')} {o}->{d} status={status} elapsed={elapsed:.2f}s\n")
        err_fh.flush()

    if (_i + 1) % BATCH_SIZE == 0:
        df_batch = pd.DataFrame(results)
        df_done = pd.concat([df_done, df_batch], ignore_index=True)
        df_done.to_csv(OUTPUT_PATH, index=False)
        results = []
        median_elapsed = sorted(batch_elapsed)[len(batch_elapsed)//2]
        max_elapsed = max(batch_elapsed)
        status_str = " ".join(f"{k}={v}" for k, v in batch_status.most_common())
        print(f"  Checkpoint: {len(df_done):,} total saved | "
              f"median={median_elapsed:.2f}s max={max_elapsed:.2f}s | {status_str}")
        batch_status = Counter()
        batch_elapsed = []

    time.sleep(SLEEP_BETWEEN)

if results:
    df_batch = pd.DataFrame(results)
    df_done = pd.concat([df_done, df_batch], ignore_index=True)
    df_done.to_csv(OUTPUT_PATH, index=False)

err_fh.close()
print(f"Done: {len(df_done):,} total pairs saved to {OUTPUT_PATH}")
print(f"Error log: {ERROR_LOG}")

df_transit = pd.read_csv(OUTPUT_PATH)
print(f"\nTotal pairs: {len(df_transit):,}")
print(f"Missing (API failures): {df_transit['transit_time_sec'].isna().sum():,}")
print(f"\nTravel time (minutes):")
print((df_transit["transit_time_sec"].dropna() / 60).describe().round(1))
