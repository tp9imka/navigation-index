#!/usr/bin/env python3
"""Raw companion logs (runs/<tag>-<scenario>.raw.jsonl) => navdash/1 tracks for
templates/demo-dashboard, summary.json (detection, cross-track vs distance, end of route) and
xte_vs_distance.csv / .svg. Stdlib only.

    python3 to_navdash_fw.py --runs runs --tag ref --out runs/navdash-ref
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "templates" / "project-repo" / "src"))

from navapp.geo import geodetic_to_enu  # noqa: E402

import fw_core  # noqa: E402

SCENARIOS = ["baseline", "day", "night", "dr"]
LABEL = {"baseline": "no monitor", "day": "day: VO + visual geoloc => ExtNav",
         "night": "night: airspeed DR + thermal geoloc => ExtNav", "dr": "airspeed DR only (EKF3 source set 3)"}
COLOR = {"baseline": "#66bb6a", "day": "#4fc3f7", "night": "#ba68c8", "dr": "#ffb74d"}
TRUTH_COLOR = {"baseline": "#ff7043", "day": "#ffffff", "night": "#ce93d8", "dr": "#ffe082"}
BIN_M = 2000.0
TURN_EXCLUDE_M = 600.0      # along-route distance around interior waypoints: turn overshoot ~30 m with no spoof
TRACK_DT_S = 1.0
# MAVLink ESTIMATOR_STATUS_FLAGS
POS_HORIZ_ABS, POS_HORIZ_REL, CONST_POS_MODE, GPS_GLITCH = 16, 8, 128, 1024


def load(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def first(rows, kind):
    return next((r for r in rows if r["type"] == kind), None)


def analyse(rows):
    start = first(rows, "COMPANION_START")
    origin = first(rows, "GPS_GLOBAL_ORIGIN")
    lat0, lon0 = origin["latitude"] * 1e-7, origin["longitude"] * 1e-7
    onset = start["spoof"]["onset_s"] if start["spoof"]["kind"] != "none" else None
    pts = fw_core.route_points_en(start["route_ne"])
    end_route = first(rows, "COMPANION_ROUTE_END")
    t_route_end = end_route["t"] if end_route else math.inf
    t_end = max(r["t"] for r in rows if r.get("t") is not None)

    truth = [(r["t"], *geodetic_to_enu(r["lat"] * 1e-7, r["lng"] * 1e-7, lat0, lon0))
             for r in rows if r["type"] == "SIMSTATE" and r.get("t") is not None]
    ekf = [(r["t"], *geodetic_to_enu(r["lat"] * 1e-7, r["lon"] * 1e-7, lat0, lon0))
           for r in rows if r["type"] == "GLOBAL_POSITION_INT" and r.get("t") is not None]
    mon = [r for r in rows if r["type"] == "COMPANION_MON" and r.get("t") is not None]

    def at(series, t):
        lo, hi = 0, len(series) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if series[mid][0] < t:
                lo = mid + 1
            else:
                hi = mid
        return series[lo]

    # Cross-track of the real aircraft vs distance flown since onset (along the truth path).
    xte_rows, flown, prev = [], 0.0, None
    for t, e, n in truth:
        if t < 0 or t > t_route_end:
            continue
        if prev is not None and onset is not None and t >= onset:
            flown += math.dist(prev, (e, n))
        prev = (e, n)
        d, along, _ = fw_core.cross_track((e, n), pts)
        xte_rows.append((t, flown if onset is not None and t >= onset else 0.0, d, along))
    after = [x for x in xte_rows if onset is not None and x[0] >= onset]
    bins = {}
    for _, f, d, _ in after:
        k = int(f // BIN_M)
        bins[k] = max(bins.get(k, 0.0), d)
    corners, run = [], 0.0
    for a, b in zip(pts[:-1], pts[1:-1]):
        run += math.dist(a, b)
        corners.append(run)
    straight = [x for x in after if all(abs(x[3] - c) > TURN_EXCLUDE_M for c in corners)]
    ekf_err = [(t, math.dist((e, n), at(truth, t)[1:])) for t, e, n in ekf if t >= 0]
    ref_err = []
    for r in mon:
        e, n = geodetic_to_enu(r["ref_lat"], r["ref_lon"], lat0, lon0)
        ref_err.append((r["t"], math.dist((e, n), at(truth, r["t"])[1:]), r["ref_sigma"]))

    dets = {r["detector"]: r["t"] for r in rows if r["type"] == "COMPANION_DETECT"}
    action = first(rows, "COMPANION_ACTION")
    ack = [r for r in rows if r["type"] == "COMMAND_ACK" and r.get("command") == 42007]
    final_wp = pts[-1]
    loiter = [x for x in truth if x[0] >= t_route_end]
    loiter_c = (sum(x[1] for x in loiter) / len(loiter), sum(x[2] for x in loiter) / len(loiter)) if loiter else None
    ekf_status = [r for r in rows if r["type"] == "EKF_STATUS_REPORT" and r.get("t") is not None]
    t_act = action["t"] if action and action["action"] == "set_ekf_source_set" else None
    post = [r for r in ekf_status if t_act is not None and r["t"] > t_act + 5]
    texts = [{"t": r["t"], "text": r["text"]} for r in rows if r["type"] == "STATUSTEXT"
             and r.get("t") is not None and (onset is None or r["t"] >= onset - 1)]

    def mx(series, t0=None, t1=math.inf):
        vals = [v[1] for v in series if (t0 is None or v[0] >= t0) and v[0] <= t1]
        return round(max(vals), 1) if vals else None

    s = {
        "scenario": start["scenario"], "seed": start["seed"], "ref_kind": start["ref_kind"],
        "fix_model": start["fix_model"], "spoof": start["spoof"],
        "route_length_m": round(fw_core.route_length_m(start["route_ne"]), 0),
        "outcome": end_route["outcome"] if end_route else "no route end",
        "t_route_end_s": None if t_route_end == math.inf else t_route_end,
        "first_detect_s": dets, "ttd_s": {k: round(v - onset, 1) for k, v in dets.items()} if onset is not None else {},
        "action": action and {k: action[k] for k in ("t", "action", "reason") if k in action} | (
            {"source_set": action.get("source_set")} if action.get("source_set") else {}),
        "source_set_ack": [r["result"] for r in ack],
        "flown_after_onset_m": round(after[-1][1], 0) if after else None,
        "xte_max_after_onset_m": round(max((x[2] for x in after), default=0.0), 1),
        "xte_max_straight_after_onset_m": round(max((x[2] for x in straight), default=0.0), 1),
        "xte_at_route_end_m": round(after[-1][2], 1) if after else None,
        "xte_max_per_2km_bin_m": {f"{int(k * BIN_M / 1000)}-{int((k + 1) * BIN_M / 1000)} km": round(v, 1)
                                  for k, v in sorted(bins.items())},
        "truth_to_final_wp_at_route_end_m": round(math.dist(at(truth, t_route_end)[1:], final_wp), 1)
        if t_route_end != math.inf else None,
        "loiter_center_offset_m": round(math.dist(loiter_c, final_wp), 1) if loiter_c else None,
        "loiter_s": round(loiter[-1][0] - loiter[0][0], 1) if loiter else 0.0,
        "ekf_err_max_after_onset_m": mx(ekf_err, onset) if onset is not None else mx(ekf_err),
        "ekf_err_at_route_end_m": round(at(ekf_err, t_route_end)[1], 1) if ekf_err and t_route_end != math.inf else None,
        "ekf_err_at_end_m": round(ekf_err[-1][1], 1) if ekf_err else None,
        "ref_err_max_after_alarm_m": mx(ref_err, t_act) if t_act is not None and start["fix_model"] else None,
        "ref_err_median_m": round(sorted(v[1] for v in ref_err if v[0] >= 0)[len([v for v in ref_err if v[0] >= 0]) // 2], 1)
        if ref_err else None,
        "ekf_gps_glitch_reports_after_onset": sum(1 for r in ekf_status if onset is not None and r["t"] >= onset
                                                  and r["flags"] & GPS_GLITCH),
        "ekf_after_switch": {"reports": len(post),
                             "pos_horiz_abs": sum(1 for r in post if r["flags"] & POS_HORIZ_ABS),
                             "pos_horiz_rel": sum(1 for r in post if r["flags"] & POS_HORIZ_REL),
                             "const_pos_mode": sum(1 for r in post if r["flags"] & CONST_POS_MODE),
                             "pos_horiz_variance_max": round(max((r["pos_horiz_variance"] for r in post), default=0.0), 2)}
        if t_act is not None else None,
        "fixes": {"attempts": sum(1 for r in rows if r["type"] in ("COMPANION_FIX", "COMPANION_FIX_FAIL")),
                  "produced": sum(1 for r in rows if r["type"] == "COMPANION_FIX")},
        "statustext_after_onset": texts[:40],
        "wall_s": round(max(r["t_host"] for r in rows), 0),
    }
    series = {"truth": truth, "ekf": ekf, "mon": mon, "xte": xte_rows, "ekf_err": ekf_err, "ref_err": ref_err,
              "lat0": lat0, "lon0": lon0, "onset": onset, "t_act": t_act, "dets": dets, "rows": rows}
    return s, series


def decimate(rows, dt=TRACK_DT_S):
    out, last = [], -math.inf
    for r in rows:
        if r["t"] - last >= dt - 1e-6:
            out.append(r)
            last = r["t"]
    return out


def write_jsonl(path, header, lines):
    with path.open("w") as f:
        f.write(json.dumps({"header": {"schema": "navdash/1", **header}}) + "\n")
        for line in lines:
            f.write(json.dumps(line) + "\n")


def write_tracks(out: Path, results: dict):
    tracks = []
    scen = [s for s in SCENARIOS if s in results]
    main = "day" if "day" in results else scen[0]
    for s in [main] + [x for x in scen if x != main]:
        _, se = results[s]
        rows = se["rows"]
        name = f"truth-{s}.jsonl"
        ev = []
        if s == main and se["onset"] is not None:
            ev.append({"t": se["onset"], "event": "attack_onset", "text": "coherent GPS drag starts", "ground_truth": True})
        write_jsonl(out / name, {"track": f"truth-{s}", "role": "truth", "label": f"truth ({LABEL[s]})",
                                 "color": TRUTH_COLOR[s]},
                    [{"t": r["t"], "lat": r["lat"] * 1e-7, "lon": r["lng"] * 1e-7}
                     for r in decimate([r for r in rows if r["type"] == "SIMSTATE" and r.get("t") is not None and r["t"] >= 0])] + ev)
        tracks.append(name)
    for s in [main] + [x for x in scen if x != main]:
        summ, se = results[s]
        rows = se["rows"]
        ev = []
        for k, t in se["dets"].items():
            ev.append({"t": t, "event": "spoof_suspected", "text": f"{k} detector alarm"})
        if se["t_act"] is not None:
            ev.append({"t": se["t_act"], "event": "source_switched",
                       "text": f"MAV_CMD_SET_EKF_SOURCE_SET {summ['action'].get('source_set')}"})
        alarm_t = min(se["dets"].values()) if se["dets"] else math.inf
        name = f"ekf-{s}.jsonl"
        write_jsonl(out / name, {"track": f"ekf-{s}", "role": "fused", "label": f"EKF ({LABEL[s]})",
                                 "color": COLOR[s], "primary": s == main,
                                 "r95_method": "not stated: ArduPilot reports no metric horizontal accuracy",
                                 "run_meta": {k: summ[k] for k in ("scenario", "seed", "spoof", "fix_model")}},
                    [{"t": r["t"], "lat": r["lat"] * 1e-7, "lon": r["lon"] * 1e-7,
                      "alarm": r["t"] >= alarm_t and s != "baseline",
                      "health": "excluded" if r["t"] >= alarm_t else "trusted"}
                     for r in decimate([r for r in rows if r["type"] == "GLOBAL_POSITION_INT" and r.get("t") is not None and r["t"] >= 0])] + ev)
        tracks.append(name)
    _, se = results[main]
    write_jsonl(out / "gnss.jsonl", {"track": "gnss", "role": "gnss", "label": f"GNSS as received ({main} run)"},
                [{"t": r["t"], "lat": r["lat"] * 1e-7, "lon": r["lon"] * 1e-7}
                 for r in decimate([r for r in se["rows"] if r["type"] == "GPS_RAW_INT" and r.get("t") is not None and r["t"] >= 0], 2.0)])
    tracks.append("gnss.jsonl")
    for s in ("day", "night"):
        if s in results:
            write_jsonl(out / f"fixes-{s}.jsonl", {"track": f"fixes-{s}", "role": "altpnt",
                                                   "label": f"{s} geoloc fixes (measured-model simulation)"},
                        [{"t": r["t"], "lat": r["lat"], "lon": r["lon"]} for r in results[s][1]["rows"]
                         if r["type"] == "COMPANION_FIX" and r.get("t") is not None and r["t"] >= 0])
            tracks.append(f"fixes-{s}.jsonl")
    lat0, lon0 = se["lat0"], se["lon0"]
    from navapp.geo import enu_to_geodetic
    ring = [enu_to_geodetic(7000 + 9000 * math.cos(a), 6500 + 9000 * math.sin(a), lat0, lon0)
            for a in [i * 2 * math.pi / 48 for i in range(49)]]
    zone = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {
        "kind": "spoofing", "label": "coherent GPS drag (scenario area, not an emitter footprint)",
        "t_start": se["onset"] or 0}, "geometry": {"type": "Polygon", "coordinates": [[[lo, la] for la, lo in ring]]}}]}
    (out / "zones.geojson").write_text(json.dumps(zone))
    (out / "manifest.json").write_text(json.dumps({
        "schema": "navdash/1", "title": "Fixed-wing golden demo: ArduPlane SITL, 27.6 km route, coherent GPS drag",
        "tracks": tracks, "zones": "zones.geojson"}, indent=1))


def write_xte(out: Path, results: dict):
    scen = [s for s in SCENARIOS if s in results]
    step = 500.0
    curves = {}
    for s in scen:
        xs = [x for x in results[s][1]["xte"] if results[s][1]["onset"] is not None and x[0] >= results[s][1]["onset"]]
        pts, k = [], 0
        for _, f, d, _ in xs:
            if f >= k * step:
                pts.append((round(f, 0), round(d, 1)))
                k = int(f // step) + 1
        curves[s] = pts
    if not any(curves.values()):
        return
    n = max(len(c) for c in curves.values())
    with (out / "xte_vs_distance.csv").open("w") as f:
        f.write("flown_after_onset_m," + ",".join(f"xte_{s}_m" for s in scen) + "\n")
        for i in range(n):
            d = i * step
            vals = []
            for s in scen:
                c = curves[s]
                vals.append(str(c[i][1]) if i < len(c) else "")
            f.write(f"{d:.0f}," + ",".join(vals) + "\n")
    W, H, P = 760, 380, 50
    xmax = max(c[-1][0] for c in curves.values() if c) or 1.0
    ymax = max(max(v for _, v in c) for c in curves.values() if c) or 1.0
    ymax = 10 ** math.ceil(math.log10(ymax)) if ymax > 0 else 1.0
    def X(x): return P + (W - 2 * P) * x / xmax
    def Y(y): return H - P - (H - 2 * P) * y / ymax
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="12">',
           f'<rect width="{W}" height="{H}" fill="#fff"/>',
           f'<line x1="{P}" y1="{H-P}" x2="{W-P}" y2="{H-P}" stroke="#333"/><line x1="{P}" y1="{P}" x2="{P}" y2="{H-P}" stroke="#333"/>',
           f'<text x="{W/2}" y="{H-12}" text-anchor="middle">distance flown after spoof onset (km)</text>',
           f'<text x="14" y="{H/2}" transform="rotate(-90 14 {H/2})" text-anchor="middle">true cross-track error (m)</text>']
    for i in range(0, int(xmax // 1000) + 1, 2):
        svg.append(f'<text x="{X(i*1000):.0f}" y="{H-P+16}" text-anchor="middle">{i}</text>')
    for j in range(6):
        y = ymax * j / 5
        svg.append(f'<text x="{P-6}" y="{Y(y)+4:.0f}" text-anchor="end">{y:.0f}</text>'
                   f'<line x1="{P}" y1="{Y(y):.0f}" x2="{W-P}" y2="{Y(y):.0f}" stroke="#eee"/>')
    plot_color = {"baseline": "#2e7d32", "day": "#0277bd", "night": "#7b1fa2", "dr": "#ef6c00"}
    for i, s in enumerate(scen):
        c = curves[s]
        svg.append(f'<polyline fill="none" stroke="{plot_color[s]}" stroke-width="2" points="'
                   + " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in c) + '"/>')
        svg.append(f'<text x="{P+10}" y="{P+16*i+4}" fill="{plot_color[s]}">{LABEL[s]}</text>')
    svg.append("</svg>")
    (out / "xte_vs_distance.svg").write_text("\n".join(svg))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=Path, default=HERE / "runs")
    ap.add_argument("--tag", default="ref")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    results = {}
    for s in SCENARIOS:
        p = a.runs / f"{a.tag}-{s}.raw.jsonl"
        if p.exists():
            results[s] = analyse(load(p))
    if not results:
        print("no runs found")
        return 1
    a.out.mkdir(parents=True, exist_ok=True)
    write_tracks(a.out, results)
    write_xte(a.out, results)
    summary = {s: r[0] for s, r in results.items()}
    (a.out / "summary.json").write_text(json.dumps(summary, indent=1))
    for s, r in summary.items():
        print(f"{s:9s} ttd {r['ttd_s']} xte max {r['xte_max_after_onset_m']} m, route end {r['xte_at_route_end_m']} m, "
              f"loiter offset {r['loiter_center_offset_m']} m, ekf err end {r['ekf_err_at_end_m']} m, {r['outcome']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
