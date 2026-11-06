#!/usr/bin/env python3
"""Convert two companion raw logs (monitor run, baseline run) into navdash/1 tracks for
templates/demo-dashboard, plus summary.json with the headline numbers.

    python to_navdash.py runs/monitor.raw.jsonl runs/baseline.raw.jsonl              # => runs/navdash
    python to_navdash.py runs/monitor.raw.jsonl runs/baseline.raw.jsonl --out data   # refresh reference
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "templates" / "project-repo" / "src"))

from navapp.geo import enu_to_geodetic, geodetic_to_enu  # noqa: E402

TRACK_PERIOD_S = 0.5
FIX_PERIOD_S = 1.0
ALERT_LIMIT_M = 10.0          # v1 logs (no PL in the track)
SS_ALERT_LIMIT_M = 50.0       # v2 SS protection level vs this; the samples/altpnt-integrity default AL
ZONE_PAD_M = 120.0
ZONE_POINTS = 48
GPS_GLITCHING_FLAG = 0x8000
EKF_VARIANCE_WARN = 0.5        # threshold from the EKF_STATUS_REPORT comment in ardupilotmega.xml
SOURCE_LABEL = {1: "gps", 2: "extnav"}


def load(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def by_type(rows: list[dict], kind: str) -> list[dict]:
    return [r for r in rows if r["type"] == kind and r.get("t") is not None]


def meta(rows: list[dict]) -> dict:
    return next(r for r in rows if r["type"] == "COMPANION_START")


def origin(rows: list[dict]) -> tuple[float, float]:
    o = next(r for r in rows if r["type"] == "GPS_GLOBAL_ORIGIN")
    return o["latitude"] * 1e-7, o["longitude"] * 1e-7


def decimate(rows: list[dict], period: float) -> list[dict]:
    out, next_t = [], -math.inf
    for r in rows:
        if r["t"] >= next_t:
            out.append(r)
            next_t = r["t"] + period
    return out


def seg_dist(p, a, b) -> float:
    ax, ay = b[0] - a[0], b[1] - a[1]
    L2 = ax * ax + ay * ay
    k = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2))
    return math.hypot(p[0] - a[0] - k * ax, p[1] - a[1] - k * ay)


def path_deviation(p_en, mission_ne) -> float:
    """Cross-track distance from the planned AUTO path (home => WP1 => ... in east/north)."""
    pts = [(0.0, 0.0)] + [(e, n) for n, e in mission_ne]
    return min(seg_dist(p_en, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def truth_rows(rows):
    return [{"t": r["t"], "lat": r["lat"] * 1e-7, "lon": r["lng"] * 1e-7} for r in by_type(rows, "SIMSTATE")]


def ekf_rows(rows):
    return [{"t": r["t"], "lat": r["lat"] * 1e-7, "lon": r["lon"] * 1e-7}
            for r in by_type(rows, "GLOBAL_POSITION_INT")]


def interp(track, t):
    if not track or t < track[0]["t"] or t > track[-1]["t"]:
        return None
    lo, hi = 0, len(track) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if track[mid]["t"] <= t else (lo, mid)
    a, b = track[lo], track[hi]
    k = 0.0 if b["t"] == a["t"] else (t - a["t"]) / (b["t"] - a["t"])
    return a["lat"] + k * (b["lat"] - a["lat"]), a["lon"] + k * (b["lon"] - a["lon"])


def first(rows, pred):
    return next((r for r in rows if pred(r)), None)


def detections(rows, onset, kind):
    """First detection per detector. v2 logs carry COMPANION_DETECT; v1 logs only the chi-square
    verdict. Only the first alarm per detector counts: one before onset (or in a no-spoof run) is
    a false alarm and leaves no TTD for that run."""
    first = {}
    for r in by_type(rows, "COMPANION_DETECT"):
        first.setdefault(r["detector"], r["t"])
    if not first:
        a = next((r for r in by_type(rows, "COMPANION_MONITOR") if r["alarm"]), None)
        if a:
            first["chi2"] = a["t"]
    if first:
        first["any"] = min(first.values())
    if "ss" in first or "vel" in first:
        first["ss+vel"] = min(first[k] for k in ("ss", "vel") if k in first)
    out = {}
    for det in ("chi2", "ss", "vel", "ss+vel", "any"):
        t = first.get(det)
        fa = t is not None and (kind == "none" or t < onset)
        out[det] = {"t_s": None if t is None else round(t, 1), "false_alarm": fa,
                    "ttd_s": None if t is None or fa else round(t - onset, 1)}
    return out


def ss_stats(rows, truth, onset, lat0, lon0):
    ss = by_type(rows, "COMPANION_SS")
    if not ss:
        return {"hpl_median_before_onset_m": None, "misleading_epochs": 0, "epochs": 0,
                "unavailable_epochs": 0, "max_error_m": None}
    errs, mi, unav = [], 0, 0
    for r in ss:
        tp = interp(truth, r["t"])
        if not tp:
            continue
        e = math.hypot(*geodetic_to_enu(r["lat"], r["lon"], *tp))
        errs.append(e)
        mi += e > r["hpl"]
        unav += r["hpl"] >= SS_ALERT_LIMIT_M or r["ambiguous"]
    before = sorted(r["hpl"] for r in ss if r["t"] < onset)
    return {"hpl_median_before_onset_m": round(before[len(before) // 2], 1) if before else None,
            "misleading_epochs": mi, "epochs": len(errs), "unavailable_epochs": unav,
            "max_error_m": round(max(errs), 1) if errs else None,
            "alert_limit_m": SS_ALERT_LIMIT_M}


def analyse(rows: list[dict]) -> dict:
    m, (lat0, lon0) = meta(rows), origin(rows)
    m["spoof"].setdefault("kind", "position")
    onset = m["spoof"]["onset_s"]
    truth, ekf = truth_rows(rows), ekf_rows(rows)
    mon = by_type(rows, "COMPANION_MONITOR")
    action = first(by_type(rows, "COMPANION_ACTION"), lambda r: True)
    alarm = action or first(mon, lambda r: r["alarm"])
    ack = first(by_type(rows, "COMMAND_ACK"), lambda r: r["command"] == 42007)
    spoof = by_type(rows, "COMPANION_SPOOF")
    off_at = lambda t: max((s["offset_m"] for s in spoof if s["t"] <= t), default=0.0)  # noqa: E731
    dev = [(r["t"], path_deviation(geodetic_to_enu(r["lat"], r["lon"], lat0, lon0), m["mission_ne"]))
           for r in truth]
    err = []
    for r in ekf:
        tp = interp(truth, r["t"])
        if tp:
            e = geodetic_to_enu(r["lat"], r["lon"], *tp)
            err.append((r["t"], math.hypot(*e)))
    ekf_st = by_type(rows, "EKF_STATUS_REPORT")
    after = [r for r in ekf_st if r["t"] >= onset]
    end_t = truth[-1]["t"]
    return {
        "mode": m["mode"],
        "seed": m.get("seed"),
        "spoof": m["spoof"],
        "gps": m.get("gps", "sitl"),
        "vgeo": m["vgeo"].get("mode", "sim") if isinstance(m.get("vgeo"), dict) else "sim",
        "detector": m.get("detector", "chi2"),
        "detect": detections(rows, onset, m["spoof"]["kind"]),
        "ss": ss_stats(rows, truth, onset, lat0, lon0),
        "vgeo_fixes": len(by_type(rows, "COMPANION_VGEO")),
        "vgeo_failures": len(by_type(rows, "COMPANION_VGEO_FAIL")),
        "ekf_lane_switches": sum(1 for r in by_type(rows, "STATUSTEXT") if r["text"].startswith("EKF3 lane switch")),
        "ekf_lane_switches_after_action": sum(1 for r in by_type(rows, "STATUSTEXT")
                                              if r["text"].startswith("EKF3 lane switch") and action
                                              and r["t"] >= action["t"]),
        "outcome": next((r.get("outcome", "mission_complete") for r in rows if r["type"] == "COMPANION_END"), None),
        "mission_duration_s": round(end_t, 1),
        "spoof_offset_at_end_m": round(off_at(end_t), 1),
        "alarm_t_s": alarm and round(alarm["t"], 1),
        "time_to_detect_s": alarm and round(alarm["t"] - onset, 1),
        "spoof_offset_at_alarm_m": alarm and round(off_at(alarm["t"]), 1),
        "action": action and action["action"],
        "source_set_ack": ack and ack["result"],
        "max_path_deviation_after_onset_m": round(max((d for t, d in dev if t >= onset), default=0), 1),
        "max_path_deviation_before_onset_m": round(max((d for t, d in dev if t < onset), default=0), 1),
        "path_deviation_at_end_m": round(dev[-1][1], 1),
        "max_ekf_error_m": round(max(e for _, e in err), 1),
        "max_ekf_error_t_s": round(max(err, key=lambda x: x[1])[0], 1),
        "ekf_gps_glitching_reports": sum(1 for r in after if r["flags"] & GPS_GLITCHING_FLAG),
        "ekf_max_pos_horiz_variance_after_onset": round(max((r["pos_horiz_variance"] for r in after), default=0), 3),
        "ekf_reports_over_0p5_after_onset": sum(1 for r in after if r["pos_horiz_variance"] > EKF_VARIANCE_WARN),
        "statustext_after_onset": [f'{r["t"]:.1f}: {r["text"]}' for r in by_type(rows, "STATUSTEXT")
                                   if r["t"] >= onset],
    }


def header(track, role, label, color, **extra):
    return {"header": {"schema": "navdash/1", "track": track, "role": role, "label": label,
                       "color": color, **extra}}


def write_track(path: Path, head: dict, lines: list[dict]) -> None:
    with path.open("w") as f:
        f.write(json.dumps(head) + "\n")
        for line in sorted(lines, key=lambda x: x["t"]):
            f.write(json.dumps(line) + "\n")


def pos(r, **extra):
    return {"t": round(r["t"], 2), "lat": round(r["lat"], 7), "lon": round(r["lon"], 7), **extra}


def statustext_events(rows, onset):
    return [{"t": round(r["t"], 2), "event": "autopilot", "text": r["text"]}
            for r in by_type(rows, "STATUSTEXT")
            if r["t"] >= onset - 5 and not r["text"].startswith("EKF primary changed")]


def primary_lines(rows, summary):
    """EKF output of the monitored run, tagged with the companion monitor's verdict."""
    mon = by_type(rows, "COMPANION_MONITOR")
    action_t = summary["alarm_t_s"] if summary["action"] == "set_ekf_source_set" else None
    out, mi = [], 0
    for r in decimate(ekf_rows(rows), TRACK_PERIOD_S):
        while mi + 1 < len(mon) and mon[mi + 1]["t"] <= r["t"]:
            mi += 1
        v = mon[mi] if mon and mon[0]["t"] <= r["t"] else None
        src = "extnav" if action_t is not None and r["t"] >= action_t else "gps"
        extra = {"sources": [src]}
        if v:
            extra |= {"health": v["health"], "alarm": v["alarm"]}
        out.append(pos(r, **extra))
    events, prev = [], None
    for v in mon:
        if v["health"] != prev and v["health"] in ("suspect", "excluded"):
            events.append({"t": round(v["t"], 2), "event": "spoof_suspected" if v["health"] == "excluded"
                           else "fix_excluded",
                           "text": f'GNSS {v["health"]}: {v["reason"]} (stat {v["statistic"]:.1f} / gate {v["threshold"]:.1f})'})
        prev = v["health"]
    if action_t is not None:
        events.append({"t": action_t, "event": "source_switched",
                       "text": f"MAV_CMD_SET_EKF_SOURCE_SET 2 (ExternalNav), ACK result {summary['source_set_ack']}"})
    return out + events + statustext_events(rows, summary["spoof"]["onset_s"])


def zone(rows) -> dict:
    """Synthetic polygon around the monitored run's flight area during the attack window."""
    lat0, lon0 = origin(rows)
    pts = [geodetic_to_enu(r["lat"], r["lon"], lat0, lon0) for r in truth_rows(rows)]
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    rad = max(math.hypot(p[0] - cx, p[1] - cy) for p in pts) + ZONE_PAD_M
    ring = [list(reversed(enu_to_geodetic(cx + rad * math.cos(a), cy + rad * math.sin(a), lat0, lon0)))
            for a in (2 * math.pi * i / ZONE_POINTS for i in range(ZONE_POINTS + 1))]
    ring = [[round(x, 7) for x in p] for p in ring]
    m = meta(rows)
    return {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {
        "kind": "spoofing", "label": f"GPS drag {m['spoof']['rate_mps']} m/s ("
        + ("SIM_GPS_GLITCH ramp" if m.get("gps", "sitl") == "sitl" else f"GPS_INPUT, {m['spoof'].get('kind', 'position')}") + ")",
        "t_start": m["spoof"]["onset_s"], "t_end": None,
        "note": "drawn around the flight area; not an emitter footprint"},
        "geometry": {"type": "Polygon", "coordinates": [ring]}}]}


VGEO_LABEL = {"sim": "Simulated visual geoloc (truth + 1.5 m noise)",
              "replay": "Visual geoloc, replayed real matches (NAIP 2019 frame vs 2023 map)",
              "live": "Visual geoloc, live ALIKED+LightGlue matching (NAIP 2019 frame vs 2023 map)"}


def ss_lines(rows):
    """The companion's own fused solution (SS main filter) with its protection level."""
    out = []
    for r in decimate(by_type(rows, "COMPANION_SS"), FIX_PERIOD_S):
        health = ("unavailable" if r["ambiguous"] or r["hpl"] >= SS_ALERT_LIMIT_M
                  else "excluded" if r["excluded"] else "trusted")
        srcs = ["vio"] + [s for s in ("gnss", "vgeo") if s not in r["excluded"]]
        out.append(pos(r, pl_m=round(r["hpl"], 2), health=health, alarm=bool(r["excluded"]) or r["ambiguous"],
                       sources=srcs))
    for r in by_type(rows, "COMPANION_SS"):
        for e in r["events"]:
            if not e.startswith("gate:"):
                out.append({"t": round(r["t"], 2), "event": "ss_" + e.split(":")[0], "text": f"SS FDE {e}"})
    for r in by_type(rows, "COMPANION_DETECT"):
        out.append({"t": round(r["t"], 2), "event": "detected", "text": f"detector {r['detector']} fired"})
    return out


def convert(mon_rows, base_rows, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    s_mon, s_base = analyse(mon_rows), analyse(base_rows)
    onset = s_mon["spoof"]["onset_s"]
    src = {"source": "ArduCopter Copter-4.6.3 SITL (Docker), logged by companion.py"}
    write_track(out / "truth.jsonl", header("truth", "truth", "Truth, monitor run (SIMSTATE)", "#e8eaed", **src),
                [pos(r) for r in decimate(truth_rows(mon_rows), TRACK_PERIOD_S)]
                + [{"t": onset, "event": "attack_onset", "ground_truth": True,
                    "text": f"GPS drag starts: {s_mon['spoof']['rate_mps']} m/s toward {s_mon['spoof']['bearing_deg']} deg"}])
    has_ss = bool(by_type(mon_rows, "COMPANION_SS"))
    if has_ss:
        write_track(out / "ss-monitor.jsonl",
                    header("ss-monitor", "fused", "Companion integrity solution (SS FDE main filter) + HPL", "#ffd54f",
                           primary=True, alert_limit_m=SS_ALERT_LIMIT_M, **src,
                           pl_method="solution separation, ported from samples/altpnt-integrity (P_FA 1e-5, P_MD 1e-3, IR_ff 1e-7)",
                           note="VIO dead reckoning + GNSS + visual geoloc; PL bounds this solution, not the autopilot EKF"),
                    ss_lines(mon_rows))
    write_track(out / "ekf-monitor.jsonl",
                header("ekf-monitor", "fused", "EKF3 output, integrity monitor on", "#4fc3f7", primary=not has_ss,
                       alert_limit_m=ALERT_LIMIT_M, **src,
                       note="GLOBAL_POSITION_INT; health/alarm from companion chi-square monitor; no PL/r95 (autopilot reports none in metres)"),
                primary_lines(mon_rows, s_mon))
    write_track(out / "truth-baseline.jsonl",
                header("truth-baseline", "truth", "Truth, no monitor (where the copter really went)", "#ff8a65", **src),
                [pos(r) for r in decimate(truth_rows(base_rows), TRACK_PERIOD_S)])
    write_track(out / "ekf-baseline.jsonl",
                header("ekf-baseline", "fused", "EKF3 output, no monitor (what the copter believed)", "#9ccc65", **src),
                [pos(r, sources=["gps"]) for r in decimate(ekf_rows(base_rows), TRACK_PERIOD_S)]
                + statustext_events(base_rows, onset))
    gps = [{"t": r["t"], "lat": r["lat"] * 1e-7, "lon": r["lon"] * 1e-7} for r in by_type(mon_rows, "GPS_RAW_INT")]
    write_track(out / "gnss.jsonl", header("gnss", "gnss", "GPS_RAW_INT as received (spoofed), monitor run", "#ef5350", **src),
                [pos(r) for r in decimate(gps, FIX_PERIOD_S)])
    vg = by_type(mon_rows, "COMPANION_VGEO")
    write_track(out / "vgeo.jsonl",
                header("vgeo", "altpnt", VGEO_LABEL[s_mon["vgeo"]], "#ba68c8", **src),
                [pos(r) for r in decimate(vg, FIX_PERIOD_S)])
    (out / "zones.geojson").write_text(json.dumps(zone(mon_rows)))
    tracks = ["truth.jsonl", "truth-baseline.jsonl", "ekf-monitor.jsonl", "ekf-baseline.jsonl",
              "gnss.jsonl", "vgeo.jsonl"]
    if has_ss:
        tracks.insert(2, "ss-monitor.jsonl")
    kind = s_mon["spoof"]["kind"]
    manifest = {"schema": "navdash/1",
                "title": f"Golden demo: ArduCopter SITL GPS drag ({kind}, {s_mon['spoof']['rate_mps']} m/s), monitor vs none",
                "tracks": tracks, "zones": "zones.geojson"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    summary = {"monitor": s_mon, "baseline": s_base}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("monitor_log", type=Path)
    ap.add_argument("baseline_log", type=Path)
    ap.add_argument("--out", type=Path, default=HERE / "runs" / "navdash",
                    help="default runs/navdash (git-ignored); pass data to refresh the committed reference")
    a = ap.parse_args(argv)
    s = convert(load(a.monitor_log), load(a.baseline_log), a.out)
    for k in ("monitor", "baseline"):
        r = s[k]
        print(f"{k:8s} alarm t={r['alarm_t_s']} (TTD {r['time_to_detect_s']} s, spoof {r['spoof_offset_at_alarm_m']} m)"
              f" action={r['action']} max path dev after onset={r['max_path_deviation_after_onset_m']} m"
              f" at end={r['path_deviation_at_end_m']} m max EKF err={r['max_ekf_error_m']} m"
              f" EKF GPS_GLITCHING reports={r['ekf_gps_glitching_reports']} detect={ {k: v['t_s'] for k, v in r['detect'].items()} }")
    return 0


if __name__ == "__main__":
    sys.exit(main())
