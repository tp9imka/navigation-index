"""Build the committed fixtures from public data (stdlib only).

  python3 fetch_data.py chart            # OSM coastline, Oresund bridge, wind turbines, seamarks via Overpass
  python3 fetch_data.py ais --dma-csv aisdk-2026-10-20.head100mb.csv   # cut a window of real DMA AIS

Without --dma-csv the AIS step pulls the first 100 MB of the daily DMA file with the HTTP Range
trick from ../maritime-ais-spoofing/dma.py.
"""
import argparse
import csv
import gzip
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
BBOX = (55.45, 12.45, 55.78, 13.05)  # S, W, N, E: southern Oresund, Drogden, Copenhagen approach
OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.private.coffee/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"]
UA = "navigation-index-sample/usv-gnss-denied-nav"
RADAR_POINT_TYPES = ("buoy_", "beacon_", "light_major", "light_minor")
AIS_WINDOW = ("20/10/2026 02:00:00", 75 * 60)
AIS_DECIMATE_S = 10
COORD_DIGITS = 6


def overpass(query, retries=4):
    data = urllib.parse.urlencode({"data": query}).encode()
    wait = 10
    for attempt in range(retries):
        for url in OVERPASS:
            try:
                req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
                raw = urllib.request.urlopen(req, timeout=200).read()
                return json.loads(raw)
            except (OSError, ValueError) as e:
                print(f"overpass {url}: {e}", file=sys.stderr)
        time.sleep(wait)
        wait *= 2
    raise RuntimeError("all Overpass endpoints failed")


def r(v):
    return round(v, COORD_DIGITS)


def build_chart(from_dir=None):
    """from_dir: a folder holding coast.json, structures.json, seamarks.json saved from the same queries."""
    s, w, n, e = BBOX
    bb = f"({s},{w},{n},{e})"
    queries = {
        "coast": f'[out:json][timeout:150];way["natural"="coastline"]{bb};out geom;',
        "structures": f'[out:json][timeout:120];(way["man_made"="bridge"]["name"="Øresundsbron"]{bb};'
                      f'node["generator:source"="wind"]{bb};);out geom;',
        "seamarks": f'[out:json][timeout:90];node["seamark:type"]{bb};out;',
    }
    if from_dir:
        got = {k: json.loads((Path(from_dir) / f"{k}.json").read_text()) for k in queries}
    else:
        got = {k: overpass(q) for k, q in queries.items()}
    coast, struct, marks = got["coast"], got["structures"], got["seamarks"]
    struct["elements"] = [el for el in struct["elements"]
                          if el["type"] == "node" or el["tags"].get("name") == "Øresundsbron"]
    out = {
        "source": "OpenStreetMap contributors via Overpass API",
        "license": "ODbL 1.0, (c) OpenStreetMap contributors, https://www.openstreetmap.org/copyright",
        "bbox_swne": BBOX,
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "osm_base": coast.get("osm3s", {}).get("timestamp_osm_base"),
        "coast": [[[r(p["lon"]), r(p["lat"])] for p in el["geometry"]] for el in coast["elements"]],
        "structures": [{"name": el["tags"].get("name", ""), "line": [[r(p["lon"]), r(p["lat"])] for p in el["geometry"]]}
                       for el in struct["elements"] if el["type"] == "way"],
        "points": [{"kind": "wind_turbine", "lon": r(el["lon"]), "lat": r(el["lat"])}
                   for el in struct["elements"] if el["type"] == "node"],
    }
    for el in marks["elements"]:
        t = el["tags"].get("seamark:type", "")
        if t.startswith(RADAR_POINT_TYPES):
            out["points"].append({"kind": t, "name": el["tags"].get("seamark:name", el["tags"].get("name", "")),
                                  "lon": r(el["lon"]), "lat": r(el["lat"])})
    FIX.mkdir(exist_ok=True)
    with gzip.open(FIX / "oresund_chart.json.gz", "wt") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"coast ways {len(out['coast'])}, vertices {sum(map(len, out['coast']))}, "
          f"structures {len(out['structures'])}, point targets {len(out['points'])}")


def build_ais(dma_csv):
    if dma_csv is None:
        sys.path.insert(0, str(HERE.parent / "maritime-ais-spoofing"))
        import dma
        dma_csv = dma.fetch("2026-10-20", 100, HERE / "fixtures")
    t0 = datetime.strptime(AIS_WINDOW[0], "%d/%m/%Y %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
    s, w, n, e = BBOX
    last = {}
    rows = []
    with open(dma_csv, newline="") as f:
        rd = csv.DictReader(f)
        for row in rd:
            try:
                lat, lon = float(row["Latitude"]), float(row["Longitude"])
                ts = datetime.strptime(row["# Timestamp"], "%d/%m/%Y %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
            except ValueError:
                continue
            if not (s < lat < n and w < lon < e) or not (t0 <= ts <= t0 + AIS_WINDOW[1]):
                continue
            mmsi = row["MMSI"]
            if ts - last.get(mmsi, -1e9) < AIS_DECIMATE_S:
                continue
            last[mmsi] = ts
            rows.append((int(ts - t0), mmsi, r(lat), r(lon), row["SOG"], row["Length"], row["Ship type"]))
    buf = io.StringIO()
    wr = csv.writer(buf)
    wr.writerow(["t_rel_s", "mmsi", "lat", "lon", "sog_kn", "length_m", "ship_type"])
    wr.writerows(sorted(rows))
    with gzip.open(FIX / "oresund_ais_window.csv.gz", "wt") as f:
        f.write(f"# Danish Maritime Authority AIS, window start {AIS_WINDOW[0]} UTC, {AIS_WINDOW[1]} s, "
                f"bbox {BBOX}, one fix per MMSI per {AIS_DECIMATE_S} s\n")
        f.write(buf.getvalue())
    print(f"AIS rows {len(rows)}, vessels {len(last)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["chart", "ais"])
    ap.add_argument("--dma-csv")
    ap.add_argument("--from-dir", help="build the chart from saved Overpass JSON instead of querying")
    a = ap.parse_args()
    build_chart(a.from_dir) if a.what == "chart" else build_ais(a.dma_csv)
