"""GeoJSON and Cursor-on-Target output for alerts (stdlib + ../mavlink-to-tak-cot/cot.py)."""
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mavlink-to-tak-cot"))
import cot  # noqa: E402

VESSEL_COT_TYPE = "a-u-S"          # unknown surface track; change to your unit's convention
HOW_REPORTED = "m-g"
COT_STALE_S = 600
KN_TO_MS = 0.514444


def _iso(t):
    return datetime.fromtimestamp(t, timezone.utc).isoformat().replace("+00:00", "Z")


def last_pre_alert_fix(track, alert):
    prior = [f for f in track.fixes if f.t < alert.start]
    return prior[-1] if prior else None


def to_geojson(alerts, tracks_by_mmsi):
    feats = []
    for a in alerts:
        tr = tracks_by_mmsi[a.mmsi]
        props = {"mmsi": a.mmsi, "name": tr.name, "ship_type": tr.ship_type, "start": _iso(a.start),
                 "end": _iso(a.end), "detectors": dict(a.kinds),
                 "first_detail": a.flags[0].detail}
        seg = [f for f in tr.fixes if a.start <= f.t <= a.end]
        if len(seg) >= 2:
            feats.append({"type": "Feature", "geometry": {"type": "LineString",
                          "coordinates": [[round(f.lon, 6), round(f.lat, 6)] for f in seg]},
                          "properties": {**props, "role": "suspect_track"}})
        last = a.flags[-1]
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [last.lon, last.lat]},
                      "properties": {**props, "role": "last_flagged_position"}})
        good = last_pre_alert_fix(tr, a)
        if good:
            feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [good.lon, good.lat]},
                          "properties": {**props, "role": "last_pre_alert_position", "time": _iso(good.t)}})
    return {"type": "FeatureCollection", "features": feats}


def to_cot(alert, track, now=None):
    """Point at the last fix before the alert (not proven clean, just pre-alert); the flagged
    reported position goes in remarks. Falls back to the flagged position when no earlier fix exists."""
    good = last_pre_alert_fix(track, alert)
    last = alert.flags[-1]
    p = good or last
    course = p.cog if getattr(p, "cog", None) is not None else None
    speed = p.sog * KN_TO_MS if getattr(p, "sog", None) is not None else None
    xml = cot.build_event(f"ais-{track.mmsi}", p.lat, p.lon, 0.0, course=course, speed=speed,
                          callsign=track.name or str(track.mmsi), now=now, stale_s=COT_STALE_S,
                          cot_type=VESSEL_COT_TYPE)
    ev = ET.fromstring(xml)
    ev.set("how", HOW_REPORTED)
    remarks = ET.SubElement(ev.find("detail"), "remarks")
    kinds = ", ".join(f"{k} x{n}" for k, n in alert.kinds.most_common())
    remarks.text = (f"AIS/GNSS anomaly {_iso(alert.start)}..{_iso(alert.end)}: {kinds}. "
                    f"Point = {'last fix before alert' if good else 'flagged report (no earlier fix)'}; "
                    f"flagged report at {last.lat:.5f},{last.lon:.5f}: {last.detail}")
    return ET.tostring(ev, encoding="utf-8")


def write_outputs(alerts, tracks_by_mmsi, out_dir, stem, max_cot=None):
    os.makedirs(out_dir, exist_ok=True)
    gj = os.path.join(out_dir, f"{stem}.geojson")
    with open(gj, "w") as fh:
        json.dump(to_geojson(alerts, tracks_by_mmsi), fh)
    cot_path = os.path.join(out_dir, f"{stem}.cot.xml")
    with open(cot_path, "wb") as fh:
        fh.write(b"<events>\n")
        for a in alerts[:max_cot]:
            fh.write(to_cot(a, tracks_by_mmsi[a.mmsi],
                            now=datetime.fromtimestamp(a.end, timezone.utc)) + b"\n")
        fh.write(b"</events>\n")
    return gj, cot_path
