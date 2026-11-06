"""GPSJam-style hex map of ADS-B GNSS-quality degradation from ADS-B Exchange free samples.

ADS-B Exchange publishes the complete readsb-hist feed (global aircraft.json snapshots every
5 s) for the 1st of each month, no login. This pulls a time window, keeps one region, and per
H3 hex counts distinct aircraft whose own broadcast NACp says their GNSS position is bad.

Usage: python adsb_hexmap.py --date 2026-10-01 --start 03:51 --end 05:51 --step 60
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import logging
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import h3

log = logging.getLogger("adsb_hexmap")
HERE = Path(__file__).parent
SAMPLES_URL = "https://samples.adsbexchange.com/readsb-hist/{d:%Y/%m/%d}/{d:%H%M%S}Z.json.gz"

NACP_GOOD_MIN = 8        # NACp 8 => EPU < 92.6 m; same cut as samples/gnss-interference-monitor
NIC_GOOD_MIN = 7         # NIC 7 => Rc < 0.2 NM; reported, not used for the level
MAX_POS_AGE_S = 30.0
HEX_RES = 4
YELLOW_PCT = 2.0         # GPSJam FAQ bands: low < 2 %, medium 2-10 %, high > 10 %
RED_PCT = 10.0
MIN_AIRCRAFT = 3
SNAPSHOT_STEP_S = 5      # readsb-hist cadence; requested times are rounded to it
FETCH_WORKERS = 4
FETCH_RETRIES = 4
POSITION_TYPES = ("adsb_icao", "adsb_icao_nt", "adsr_icao", "mlat")


def snapshot_times(day: dt.date, start: str, end: str, step_s: int):
    t = dt.datetime.combine(day, dt.time.fromisoformat(start))
    t1 = dt.datetime.combine(day, dt.time.fromisoformat(end))
    step = dt.timedelta(seconds=max(SNAPSHOT_STEP_S, step_s - step_s % SNAPSHOT_STEP_S))
    while t <= t1:
        yield t
        t += step


def in_bbox(ac, bbox):
    lat, lon = ac.get("lat"), ac.get("lon")
    return lat is not None and lon is not None and bbox[1] <= lat <= bbox[3] and bbox[0] <= lon <= bbox[2]


def fetch(t: dt.datetime, bbox, cache: Path):
    """Download one global snapshot, keep only aircraft in bbox; cached filtered copy."""
    f = cache / f"{t:%Y%m%d_%H%M%S}.json"
    if f.exists():
        return json.loads(f.read_text())
    req = urllib.request.Request(SAMPLES_URL.format(d=t), headers={"User-Agent": "navigation-index-sample"})
    for attempt in range(FETCH_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            break
        except OSError as e:
            if attempt == FETCH_RETRIES - 1:
                raise
            log.warning("%s: %s, retrying", t, e)
            time.sleep(2 ** attempt)
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    snap = json.loads(raw)
    keep = {"now": snap["now"], "aircraft": [a for a in snap.get("aircraft", []) if in_bbox(a, bbox)]}
    f.write_text(json.dumps(keep))
    return keep


def classify(ac: dict):
    """None = cannot classify (no quality field, stale or non-ADS-B position)."""
    if ac.get("seen_pos", 0.0) > MAX_POS_AGE_S or ac.get("type") not in POSITION_TYPES:
        return None
    if "gpsOkBefore" in ac:
        return True
    nacp = ac.get("nac_p")
    if nacp is None or "nac_p" in ac.get("mlat", ()):
        return None
    return nacp < NACP_GOOD_MIN


def percent_bad(n_good: int, n_bad: int) -> float:
    """GPSJam: 100 * (bad - 1) / total, floored at 0 - one bad aircraft alone is not a signal."""
    total = n_good + n_bad
    return max(0.0, 100.0 * (n_bad - 1) / total) if total else 0.0


def level(pct: float, total: int) -> str:
    if total < MIN_AIRCRAFT:
        return "no-data"
    return "red" if pct > RED_PCT else "yellow" if pct >= YELLOW_PCT else "green"


def aggregate(snaps, res=HEX_RES):
    """{hex: {icao: {'bad': bool, 'nic_bad': bool, 'mlat': bool}}} plus per-report points."""
    hexes = defaultdict(dict)
    points = []
    for snap in snaps:
        for ac in snap["aircraft"]:
            bad = classify(ac)
            if bad is None:
                continue
            cell = h3.latlng_to_cell(ac["lat"], ac["lon"], res)
            rec = hexes[cell].setdefault(ac["hex"], {"bad": False, "nic_bad": False, "mlat": False})
            rec["bad"] |= bad
            nic = None if "nic" in ac.get("mlat", ()) else ac.get("nic")  # MLAT-derived NIC says nothing about GNSS
            rec["nic_bad"] |= nic is not None and nic < NIC_GOOD_MIN
            rec["mlat"] |= ac.get("type") == "mlat"
            points.append({"now": snap["now"], "lat": ac["lat"], "lon": ac["lon"], "hex": ac["hex"],
                           "bad": bad, "nac_p": ac.get("nac_p"), "nic": nic, "type": ac.get("type")})
    return hexes, points


def summarize(hexes):
    rows = []
    for cell, acs in hexes.items():
        n_bad = sum(a["bad"] for a in acs.values())
        n_good = len(acs) - n_bad
        pct = percent_bad(n_good, n_bad)
        rows.append({"h3": cell, "n_aircraft": len(acs), "n_good": n_good, "n_bad": n_bad,
                     "pct_bad": round(pct, 1), "level": level(pct, len(acs)),
                     "n_nic_bad": sum(a["nic_bad"] for a in acs.values()),
                     "n_mlat_position": sum(a["mlat"] for a in acs.values())})
    return sorted(rows, key=lambda r: r["h3"])


def to_geojson(rows, t_start_s, t_end_s):
    feats = []
    for r in rows:
        ring = [[lo, la] for la, lo in h3.cell_to_boundary(r["h3"])]
        ring.append(ring[0])
        kind = "jamming" if r["level"] in ("red", "yellow") else "adsb-" + r["level"]
        feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                      "properties": {"kind": kind, "method": "adsb-nacp",
                                     "label": f"ADS-B {r['pct_bad']}% bad ({r['n_bad']}/{r['n_aircraft']} ac)",
                                     "t_start": t_start_s, "t_end": t_end_s, **r}})
    return {"type": "FeatureCollection", "features": feats}


def navdash_tracks(points, t0, out: Path):
    """Aircraft reports as navdash/1 point tracks (t = s since window start) for the demo dashboard."""
    for name, bad, color, label in (("adsb-bad", True, "#ef5350", f"ADS-B NACp<{NACP_GOOD_MIN} reports"),
                                    ("adsb-good", False, "#66bb6a", f"ADS-B NACp>={NACP_GOOD_MIN} reports")):
        with open(out / f"{name}.jsonl", "w") as fh:
            fh.write(json.dumps({"header": {"schema": "navdash/1", "track": name, "role": "gnss",
                                            "label": label, "color": color, "t0_unix": t0}}) + "\n")
            for p in points:
                if p["bad"] == bad:
                    fh.write(json.dumps({"t": round(p["now"] - t0, 1), "lat": p["lat"], "lon": p["lon"],
                                         "health": "suspect" if bad else "trusted", "icao": p["hex"],
                                         "nac_p": p["nac_p"], "nic": p["nic"]}) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-10-01", help="ADS-B Exchange samples exist for the 1st of each month")
    ap.add_argument("--start", default="03:51")
    ap.add_argument("--end", default="05:51")
    ap.add_argument("--step", type=int, default=60, help="seconds between snapshots (multiple of 5)")
    ap.add_argument("--bbox", type=float, nargs=4, default=[18.0, 53.5, 25.0, 57.0],
                    metavar=("W", "S", "E", "N"))
    ap.add_argument("--res", type=int, default=HEX_RES)
    ap.add_argument("--cache", type=Path, default=HERE / "cache" / "adsb")
    ap.add_argument("--out", type=Path, default=HERE / "out")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    day = dt.date.fromisoformat(args.date)
    if day.day != 1:
        log.warning("ADS-B Exchange free samples are only published for the 1st of the month")
    args.cache.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)

    times = list(snapshot_times(day, args.start, args.end, args.step))
    with ThreadPoolExecutor(FETCH_WORKERS) as ex:
        snaps = list(ex.map(lambda t: fetch(t, args.bbox, args.cache), times))
    log.info("%d snapshots, %d aircraft reports in bbox", len(snaps), sum(len(s["aircraft"]) for s in snaps))

    hexes, points = aggregate(snaps, args.res)
    rows = summarize(hexes)
    t0 = snaps[0]["now"]
    t1 = snaps[-1]["now"] - t0
    (args.out / "adsb_cells.geojson").write_text(json.dumps(to_geojson(rows, 0.0, round(t1, 1))))
    navdash_tracks(points, t0, args.out)
    n_ac = len({p["hex"] for p in points})
    n_bad_ac = len({p["hex"] for p in points if p["bad"]})
    summary = {"date": args.date, "window_utc": [args.start, args.end], "step_s": args.step,
               "n_snapshots": len(snaps), "t0_unix": t0, "bbox": args.bbox, "hex_res": args.res,
               "n_aircraft_classified": n_ac, "n_aircraft_bad": n_bad_ac,
               "n_reports": len(points), "n_reports_bad": sum(p["bad"] for p in points),
               "levels": {lv: sum(r["level"] == lv for r in rows) for lv in ("red", "yellow", "green", "no-data")},
               "hexes": rows}
    (args.out / "adsb_summary.json").write_text(json.dumps(summary, indent=1))
    log.info("aircraft %d (bad %d), hexes %s", n_ac, n_bad_ac, summary["levels"])


if __name__ == "__main__":
    main()
