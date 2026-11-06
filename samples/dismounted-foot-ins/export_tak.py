"""Blue-force output for one hallway trial: CoT events (via samples/mavlink-to-tak-cot/cot.py)
and navdash/1 JSONL tracks for templates/demo-dashboard.

The dataset is not georeferenced. The building frame (x, y in metres) is placed at an
illustrative anchor ORIGIN with x => east and y => north. Do not read the map position
as the real building location.

usage:
  python3 export_tak.py data/hallway/walk/0/2018-04-07-15-39-07 --out out/walk0
  python3 export_tak.py <trial> --out out/walk0 --udp 127.0.0.1:4242   # also stream CoT
"""
import argparse
import json
import math
import os
import socket
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import detectors
import run_hallway as R

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mavlink-to-tak-cot"))
import cot  # noqa: E402

ORIGIN = (43.7825, -79.4660)  # illustrative anchor near UTIAS, Toronto; not surveyed
EARTH_R = 6378137.0
COT_TYPE_INFANTRY = "a-f-G-U-C-I"  # friendly ground unit, combat, infantry
HOW_FUSED = "m-f"
COT_PERIOD_S = 1.0
R95_PER_SIGMA = 2.45
TRACK_DT_S = 0.2
R95_METHOD = "max(2.45 * filter sigma_h, 0.02 * distance walked since last UWB epoch)"


def to_latlon(x, y):
    lat = ORIGIN[0] + math.degrees(y / EARTH_R)
    lon = ORIGIN[1] + math.degrees(x / (EARTH_R * math.cos(math.radians(ORIGIN[0]))))
    return round(lat, 8), round(lon, 8)


def header(track, role, label, color, **extra):
    h = {"schema": "navdash/1", "track": track, "role": role, "label": label, "color": color}
    h.update(extra)
    return {"header": h}


def write_jsonl(path, rows):
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def with_r95(track, ts0, fix_times):
    """95 % radius = max(filter 2.45 sigma_h, DRIFT_FRAC x distance walked since the last UWB epoch):
    the ZUPT filter's own covariance is overconfident (see README)."""
    d, last, fixes = 0.0, None, sorted(fix_times)
    for t, p, sh, _ in track:
        if last is not None:
            d += math.hypot(p[0] - last[0], p[1] - last[1])
        last = p
        while fixes and t - ts0 >= fixes[0]:
            fixes.pop(0)
            d = 0.0
        yield t, p, sh, max(R95_PER_SIGMA * sh, R.DRIFT_FRAC * d)


def cot_event(uid, callsign, t_abs, x, y, r95, how, speed, course):
    lat, lon = to_latlon(x, y)
    xml = cot.build_event(uid, lat, lon, 0.0, course=course, speed=speed, callsign=callsign,
                          ce=r95, now=t_abs, stale_s=10, cot_type=COT_TYPE_INFANTRY)
    ev = ET.fromstring(xml)
    ev.set("how", how)
    ET.SubElement(ev.find("detail"), "remarks").text = "foot-mounted INS, ZUPT; indoor, not GNSS"
    return ET.tostring(ev, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("trial_dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--udp", help="host:port to also send each CoT event to (TAK server / ATAK)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    tr = R.load_trial(os.path.join(a.trial_dir, "processed_data.mat"))
    tr["gi_set"] = set(tr["gi"])
    trial = os.path.basename(os.path.normpath(a.trial_dir))
    t_base = datetime.strptime(trial, "%Y-%m-%d-%H-%M-%S").replace(tzinfo=timezone.utc)  # folder time, tz not stated
    ts0 = tr["ts"][0]
    zv = detectors.stance(detectors.shoe(tr["acc"], tr["gyro"]), R.DEFAULT_DET[1])
    yaw0 = R.entry_yaw(tr, zv)

    runs = {}
    for name, kw in (("ins", {}), ("fused", {"hde": True, "floor": True, "uwb": "inflated"})):
        est, st, track = R.run(tr, zv, yaw0=yaw0, keep_track=True, rng_seed=7, **kw)
        runs[name] = (est, st, track)

    truth = [header("truth", "truth", "Surveyed floor markers (gt)", "#e8eaed",
                    note="straight lines between markers; true path between markers not recorded")]
    for k, g in zip(tr["gi"], tr["gt"]):
        lat, lon = to_latlon(g[0], g[1])
        truth.append({"t": round(tr["ts"][k] - ts0, 3), "lat": lat, "lon": lon})
    write_jsonl(os.path.join(a.out, "truth.jsonl"), truth)

    labels = {"ins": ("ins", "Foot INS + ZUPT (no aiding)", "#ffb74d", {}),
              "fused": ("fused", "Foot INS + corridor heading + floor + UWB (simulated)", "#4fc3f7",
                        {"primary": True})}
    uwb_times = [tr["ts"][tr["gi"][m]] - ts0 for m in range(1, len(tr["gi"]), 2)]
    events = []
    for name, (est, st, track) in runs.items():
        role, label, color, extra = labels[name]
        rows = [header(name, role, label, color, r95_method=R95_METHOD, **extra)]
        last_t = -1e9
        for t, p, sh, r95 in with_r95(track, ts0, uwb_times if name == "fused" else []):
            t_rel = t - ts0
            if t_rel - last_t < TRACK_DT_S:
                continue
            last_t = t_rel
            lat, lon = to_latlon(p[0], p[1])
            rows.append({"t": round(t_rel, 3), "lat": lat, "lon": lon, "r95_m": round(r95, 3),
                         "health": "trusted", "sources": ["ins", "zupt"] + (["corridor", "floor", "uwb"] if name == "fused" else [])})
        write_jsonl(os.path.join(a.out, name + ".jsonl"), rows)
    for m in range(1, len(tr["gi"]), 2):
        events.append({"t": round(tr["ts"][tr["gi"][m]] - ts0, 3), "event": "uwb_ranging",
                       "text": "simulated UWB ranges to anchors within 25 m (30 % NLOS draws)"})
    with open(os.path.join(a.out, "fused.jsonl"), "a") as fh:
        for e in events:
            fh.write(json.dumps(e) + "\n")

    zones = {"type": "FeatureCollection", "features": []}
    for i, anc in enumerate(R.ANCHORS):
        ring = [list(reversed(to_latlon(anc[0] + R.UWB_MAX_RANGE * math.cos(b), anc[1] + R.UWB_MAX_RANGE * math.sin(b))))
                for b in [2 * math.pi * j / 36 for j in range(37)]]
        zones["features"].append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                                  "properties": {"kind": "uwb", "label": "UWB anchor %d reach (simulated)" % (i + 1)}})
    with open(os.path.join(a.out, "zones.geojson"), "w") as fh:
        json.dump(zones, fh)
    with open(os.path.join(a.out, "manifest.json"), "w") as fh:
        json.dump({"schema": "navdash/1", "title": "Foot INS hallway %s (real IMU, simulated UWB)" % trial,
                   "tracks": ["truth.jsonl", "fused.jsonl", "ins.jsonl"], "zones": "zones.geojson"}, fh, indent=1)

    sock, dest = None, None
    if a.udp:
        host, port = a.udp.rsplit(":", 1)
        sock, dest = socket.socket(socket.AF_INET, socket.SOCK_DGRAM), (host, int(port))
    n = 0
    with open(os.path.join(a.out, "cot.xml"), "wb") as fh:
        fh.write(b"<events>\n")
        next_t, prev = 0.0, None
        for t, p, sh, r95 in with_r95(runs["fused"][2], ts0, uwb_times):
            t_rel = t - ts0
            if t_rel < next_t:
                continue
            speed = course = None
            if prev:
                dt = t_rel - prev[0]
                dx, dy = p[0] - prev[1][0], p[1] - prev[1][1]
                speed, course = math.hypot(dx, dy) / dt, math.degrees(math.atan2(dx, dy)) % 360.0
            ev = cot_event("foot-ins-1", "DISMOUNT-1", t_base + timedelta(seconds=t_rel), p[0], p[1], r95,
                           HOW_FUSED, speed, course)
            fh.write(ev + b"\n")
            if sock:
                sock.sendto(ev, dest)
            prev, next_t, n = (t_rel, p), next_t + COT_PERIOD_S, n + 1
        fh.write(b"</events>\n")
    print("wrote %s: truth/fused/ins.jsonl, zones.geojson, manifest.json, cot.xml (%d events)" % (a.out, n))
    for name in ("ins", "fused"):
        m = R.metrics(tr, runs[name][0])
        print("%-5s ARMSE %.2f m, final %.2f m (%.2f %%), max %.2f m" % (name, m["armse3d"], m["final_h"], m["final_pct"], m["max_h"]))


if __name__ == "__main__":
    main()
