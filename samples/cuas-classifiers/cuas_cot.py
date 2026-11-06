"""Report radar tracks classified as UAS to TAK as Cursor-on-Target events.

Reuses samples/mavlink-to-tak-cot/cot.py (imported, not copied). Detections go out with
unknown affiliation (a-u-A-M-H-Q, rotor-wing drone): a classifier score is not an
identification, so hostile (a-h-) is left to an operator via --affiliation.

The NRC dataset does not publish radar site coordinates or boresight bearing, so the
--site / --boresight values are placeholders and the plotted positions are illustrative.

Usage:
  python cuas_cot.py --model out/radar_model.pkl \
      --xlsx data/radar/data/Demo-6/Echodyne_Log_20210318_105543.xlsx \
      --site 45.55 -73.75 30 --boresight 0 [--threshold 0.5] [--out out/cot_events.xml]
"""
import argparse
import math
import pickle
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mavlink-to-tak-cot"))
import cot  # noqa: E402

from radar_features import MIN_UPDATES, track_features  # noqa: E402

UAS_ROTOR_TYPE = "a-{aff}-A-M-H-Q"  # CoTtypes.xml: Air/Mil/Rotor/Drone,RPV,UAV
HOW_TRACKER = "m-a"  # CoTtypes.xml: how "tracker"
EARTH_R_M = 6_378_137.0
DETECTION_STALE_S = 10


def radar_to_geodetic(site_lat, site_lon, site_hae, boresight_deg, az_deg, el_deg, range_m):
    """Flat-earth placement, fine for the <2 km ranges in this dataset.
    Assumes positive azimuth is clockwise from boresight (not verified against a site survey)."""
    bearing = math.radians(boresight_deg + az_deg)
    ground = range_m * math.cos(math.radians(el_deg))
    north, east = ground * math.cos(bearing), ground * math.sin(bearing)
    lat = site_lat + math.degrees(north / EARTH_R_M)
    lon = site_lon + math.degrees(east / (EARTH_R_M * math.cos(math.radians(site_lat))))
    return lat, lon, site_hae + range_m * math.sin(math.radians(el_deg))


def detection_event(track_id, p_uav, last, site, boresight_deg, affiliation="u", now=None):
    lat, lon, hae = radar_to_geodetic(*site, boresight_deg, last["azimuth"], last["elevation"], last["range"])
    # radar frame: X lateral, Y up, Z along boresight
    course = (boresight_deg + math.degrees(math.atan2(last["veloX"], last["veloZ"]))) % 360.0
    speed = math.hypot(last["veloX"], last["veloZ"])
    raw = cot.build_event(uid=f"radar-trk-{track_id}", lat=lat, lon=lon, hae=hae, course=course,
                          speed=speed, callsign=f"UAS-{track_id}", now=now, stale_s=DETECTION_STALE_S,
                          cot_type=UAS_ROTOR_TYPE.format(aff=affiliation))
    ev = ET.fromstring(raw)
    ev.set("how", HOW_TRACKER)
    ET.SubElement(ev.find("detail"), "remarks").text = f"radar track {track_id}, classifier P(UAV)={p_uav:.2f}"
    return ET.tostring(ev, encoding="utf-8")


def classify_session(xlsx, bundle):
    df = pd.read_excel(xlsx, sheet_name=0)
    df = df[pd.to_numeric(df["SystemTrackID"], errors="coerce").notna()]
    out = []
    for tid, t in df.groupby("SystemTrackID", sort=False):
        if len(t) < MIN_UPDATES:
            continue
        f = track_features(t[["posX", "posY", "posZ"]].to_numpy(), t[["veloX", "veloY", "veloZ"]].to_numpy(),
                           t["rcs"].to_numpy())
        x = pd.DataFrame([f])[bundle["features"]].to_numpy(float)
        out.append((int(tid), float(bundle["model"].predict_proba(x)[0, 1]), t.iloc[-1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--site", nargs=3, type=float, metavar=("LAT", "LON", "HAE"), required=True)
    ap.add_argument("--boresight", type=float, default=0.0, help="radar boresight bearing, deg true")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--affiliation", choices=["u", "s", "h"], default="u")
    ap.add_argument("--out")
    a = ap.parse_args()

    bundle = pickle.loads(Path(a.model).read_bytes())
    results = classify_session(a.xlsx, bundle)
    events = [detection_event(tid, p, last, a.site, a.boresight, a.affiliation)
              for tid, p, last in results if p >= a.threshold]
    print(f"{len(results)} tracks, {len(events)} reported as UAS (P>={a.threshold})", file=sys.stderr)
    text = "\n".join(e.decode() for e in events)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
