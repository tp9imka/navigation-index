"""COP outputs: CoT (via ../interference-geolocation-to-tak/tak_out.py and
../mavlink-to-tak-cot/cot.py, both unchanged) and navdash/1 files for templates/demo-dashboard."""
import json
import math
import os
import xml.etree.ElementTree as ET

import siblings  # noqa: F401
import cot  # noqa: E402
import tak_out  # noqa: E402

SENSOR_COT_TYPE = "a-f-G-E-S"    # friendly ground equipment, sensor; adjust to your unit's convention
NODE_STALE_S = 30
ELLIPSE_POINTS = 48
NODE_MARK_M = 25.0
JST_TEXT = {0: "unknown", 1: "ok", 2: "warning", 3: "critical"}


def best_sources(est):
    """[(label, lat, lon, ellipse95, eirp)] from the method we report on the COP."""
    meth = est.get("methods", {})
    ls = meth.get("ls")
    if ls and ls["k"] == 2:
        return [(f"ls2-{i + 1}", s["lat"], s["lon"], s["ellipse95"], s["eirp_dbm_model"])
                for i, s in enumerate(ls["sources"])]
    for key in ("grid+df", "grid"):
        g = meth.get(key)
        if g:
            return [(key, g["lat"], g["lon"], g["ellipse95"], g["eirp_dbm_model"])]
    if ls:
        s = ls["sources"][0]
        return [("ls", s["lat"], s["lon"], s["ellipse95"], s["eirp_dbm_model"])]
    return []


def cot_events(agg, est, now=None, uid_prefix="jsn-jammer"):
    evs = []
    for i, (label, lat, lon, ell, eirp) in enumerate(best_sources(est)):
        remarks = (f"GNSS jammer estimate ({label}) from {est['n_detecting']}/{est['n_nodes']} detecting nodes; "
                   f"95% ellipse {ell[0]:.0f} x {ell[1]:.0f} m; model EIRP {eirp:.0f} dBm (common-mode offsets "
                   f"included, not a calibrated power)")
        evs += tak_out.events_from_fix(f"{uid_prefix}-{i + 1}", lat, lon, ell, remarks, now=now)
    for n in agg.nodes():
        ev = ET.fromstring(cot.build_event(f"jsn-node-{n['id']}", n["lat"], n["lon"], 0.0, callsign=n["id"],
                                           now=now, stale_s=NODE_STALE_S, cot_type=SENSOR_COT_TYPE))
        ET.SubElement(ev.find("detail"), "remarks").text = (
            f"jammingState {JST_TEXT[n['jst']]}, fix {'yes' if n['fix'] else 'no'}, "
            f"J {n['kind']} {n['j_dbm']} dBm ({n['source']})")
        evs.append(ET.tostring(ev, encoding="utf-8"))
    return evs


def ellipse_ring(frame, x, y, ell, n=ELLIPSE_POINTS):
    a, b, ang = ell
    ue, un = math.sin(math.radians(ang)), math.cos(math.radians(ang))
    ring = []
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        e = x + a * math.cos(th) * ue + b * math.sin(th) * un
        nn = y + a * math.cos(th) * un - b * math.sin(th) * ue
        lat, lon, _ = frame.to_geodetic(e, nn)
        ring.append([round(lon, 7), round(lat, 7)])
    return ring


def zones(agg, ests, include_nodes=True):
    """navdash zones: per fuse step a 95% ellipse (kind jamming) and the model fix-loss
    radius (kind denial-model), each active until the next estimate."""
    feats = []
    ests = [e for e in ests if e and e.get("methods")]
    for k, est in enumerate(ests):
        t_end = ests[k + 1]["t"] if k + 1 < len(ests) else None
        for label, lat, lon, ell, eirp in best_sources(est):
            x, y, _ = agg.frame.to_enu(lat, lon)
            feats.append({"type": "Feature", "properties": {
                "kind": "jamming", "label": f"jammer 95% ellipse ({label})", "t_start": est["t"], "t_end": t_end},
                "geometry": {"type": "Polygon", "coordinates": [ellipse_ring(agg.frame, x, y, ell)]}})
        g = est["methods"].get("grid+df") or est["methods"].get("grid")
        if g and g["rss_used"] and est["methods"].get("ls", {}).get("k", 1) == 1:
            r = g["denial_radius_m"]
            feats.append({"type": "Feature", "properties": {
                "kind": "denial-model", "label": f"model fix-loss radius {r:.0f} m (typical SV, not measured)",
                "t_start": est["t"], "t_end": t_end},
                "geometry": {"type": "Polygon", "coordinates": [ellipse_ring(agg.frame, g["x"], g["y"], (r, r, 0))]}})
    if include_nodes:
        for n in agg.nodes():
            if n["static"]:
                x, y, _ = agg.frame.to_enu(n["lat"], n["lon"])
                feats.append({"type": "Feature", "properties": {"kind": "sensor", "label": f"node {n['id']}"},
                              "geometry": {"type": "Polygon", "coordinates": [
                                  ellipse_ring(agg.frame, x, y, (NODE_MARK_M, NODE_MARK_M, 0), 12)]}})
    return {"type": "FeatureCollection", "features": feats}


def _header(track, role, label, color, **extra):
    return {"header": {"schema": "navdash/1", "track": track, "role": role, "label": label, "color": color, **extra}}


def write_navdash(out_dir, agg, truth, title, vehicles=None):
    """truth: {name: [(t, lat, lon)]}; vehicles: {node_id: [(t, lat, lon, pf)]} as reported."""
    os.makedirs(out_dir, exist_ok=True)
    files = []

    def dump(name, head, lines):
        with open(os.path.join(out_dir, name), "w") as fh:
            fh.write(json.dumps(head) + "\n")
            for ln in lines:
                fh.write(json.dumps(ln) + "\n")
        files.append(name)

    for name, pts in truth.items():
        dump(f"truth-{name}.jsonl", _header(f"truth-{name}", "truth", f"jammer {name} (truth)", "#e0e0e0"),
             [{"t": t, "lat": la, "lon": lo} for t, la, lo in pts])
    ests = [e for e in agg.estimates if e.get("methods")]
    lines, first = [], True
    for e in ests:
        src = best_sources(e)
        if not src:
            continue
        _, la, lo, ell, _ = src[0]
        lines.append({"t": e["t"], "lat": la, "lon": lo, "r95_m": round(ell[0], 1), "health": "estimate",
                      "alarm": True, "sources": [s[0] for s in src]})
        if first:
            lines.append({"t": e["t"], "event": "alarm_raised",
                          "text": f"jamming detected by {e['n_detecting']} nodes"})
            first = False
    dump("estimate.jsonl", _header("estimate", "fused", "jammer estimate (first source)", "#4fc3f7", primary=True,
                                   r95_method="semi-major axis of the 95% ellipse"), lines)
    for nid, pts in (vehicles or {}).items():
        dump(f"node-{nid}.jsonl", _header(f"node-{nid}", "gnss", f"vehicle node {nid} (reported pos)", "#ffb300"),
             [{"t": t, "lat": la, "lon": lo, "health": pf} for t, la, lo, pf in pts])
    with open(os.path.join(out_dir, "zones.geojson"), "w") as fh:
        json.dump(zones(agg, ests), fh)
    with open(os.path.join(out_dir, "manifest.json"), "w") as fh:
        json.dump({"schema": "navdash/1", "title": title, "tracks": files, "zones": "zones.geojson"}, fh, indent=1)
    return files
