#!/usr/bin/env python3
"""Per-flight EKF fault-handling metrics from fly.py logs, and the sweep table. Stdlib only.

    python3 spoof_analyse.py runs/*.raw.jsonl                    # table to stdout
    python3 spoof_analyse.py runs/*.raw.jsonl --out data/sweep_summary.json
    python3 spoof_analyse.py runs/px4-default-position-3.raw.jsonl --timeline data/tl.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

EARTH_R_M = 6371008.8
PX4_GPS_GLITCH = 1024        # ESTIMATOR_STATUS_FLAGS ESTIMATOR_GPS_GLITCH
AP_GPS_GLITCHING = 0x8000    # ardupilotmega EKF_STATUS_FLAGS EKF_GPS_GLITCHING
RESET_JUMP_M = 3.0           # EKF-minus-truth change within one sample that counts as a reset
RESET_MAX_DT_S = 0.3
MISSION_NE = [(400.0, 0.0), (400.0, 150.0), (0.0, 150.0)]   # golden-demo survey legs


def load(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def enu(lat, lon, lat0, lon0):
    return (math.radians(lon - lon0) * EARTH_R_M * math.cos(math.radians(lat0)),
            math.radians(lat - lat0) * EARTH_R_M)


def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    L2 = ax * ax + ay * ay
    k = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2))
    return math.hypot(p[0] - a[0] - k * ax, p[1] - a[1] - k * ay)


def path_deviation(p_en):
    pts = [(0.0, 0.0)] + [(e, n) for n, e in MISSION_NE]
    return min(seg_dist(p_en, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def interp(track, t):
    """track: sorted [(t, e, n)]"""
    if not track or t < track[0][0] or t > track[-1][0]:
        return None
    lo, hi = 0, len(track) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if track[mid][0] <= t else (lo, mid)
    a, b = track[lo], track[hi]
    k = 0.0 if b[0] == a[0] else (t - a[0]) / (b[0] - a[0])
    return a[1] + k * (b[1] - a[1]), a[2] + k * (b[2] - a[2])


def series(rows: list[dict]) -> dict:
    exp = next(r for r in rows if r["type"] == "EXPERIMENT")
    o = next(r for r in rows if r["type"] == "GPS_GLOBAL_ORIGIN")
    lat0, lon0 = o["latitude"] * 1e-7, o["longitude"] * 1e-7
    timed = [r for r in rows if r.get("t") is not None]
    if exp["autopilot"] == "px4":
        truth = [(r["t"], *enu(r["lat"] * 1e-7, r["lon"] * 1e-7, lat0, lon0)) for r in timed
                 if r["type"] == "HIL_STATE_QUATERNION"]
        status = [{"t": r["t"], "flag": bool(r["flags"] & PX4_GPS_GLITCH),
                   "pos_ratio": r["pos_horiz_ratio"], "vel_ratio": r["vel_ratio"]}
                  for r in timed if r["type"] == "ESTIMATOR_STATUS"]
    else:
        truth = [(r["t"], *enu(r["lat"] * 1e-7, r["lng"] * 1e-7, lat0, lon0)) for r in timed
                 if r["type"] == "SIMSTATE"]
        # Both report sqrt(test ratio): EKF_STATUS_REPORT *_variance (AP_NavEKF3_Outputs.cpp 495-496);
        # PX4 pos_horiz_ratio is sqrt of the filtered ratio, clipped at 2.0 (ekf_helper.cpp 516-550).
        status = [{"t": r["t"], "flag": bool(r["flags"] & AP_GPS_GLITCHING),
                   "pos_ratio": r["pos_horiz_variance"], "vel_ratio": r["velocity_variance"]}
                  for r in timed if r["type"] == "EKF_STATUS_REPORT"]
    ekf = [(r["t"], *enu(r["lat"] * 1e-7, r["lon"] * 1e-7, lat0, lon0)) for r in timed
           if r["type"] == "GLOBAL_POSITION_INT"]
    spoof = [(r["t"], r["offset_m"]) for r in timed if r["type"] == "COMPANION_SPOOF"]
    err = []
    for t, e, n in ekf:
        p = interp(truth, t)
        if p is not None:
            err.append((t, e - p[0], n - p[1]))
    return {"exp": exp, "truth": truth, "ekf": ekf, "err": err, "status": status, "spoof": spoof,
            "end": next((r for r in rows if r["type"] == "COMPANION_END"), None),
            "params": [r for r in rows if r["type"] == "PARAM_VALUE"],
            "statustext": [(r["t"], r["text"]) for r in timed if r["type"] == "STATUSTEXT"],
            "modes": [(r["t"], r["custom_mode"]) for r in timed if r["type"] == "HEARTBEAT" and r.get("autopilot") != 8],
            "odom_resets": [(r["t"], r["reset_counter"]) for r in timed if r["type"] == "ODOMETRY"]}


def spoof_at(spoof, t):
    v = 0.0
    for ts, off in spoof:
        if ts > t:
            break
        v = off
    return v


def resets(err, onset):
    out = []
    for (t0, e0, n0), (t1, e1, n1) in zip(err, err[1:]):
        if t1 < onset or t1 - t0 > RESET_MAX_DT_S:
            continue
        jump = math.hypot(e1 - e0, n1 - n0)
        if jump >= RESET_JUMP_M:
            out.append({"t_s": round(t1 - onset, 1), "jump_m": round(jump, 1), "jump_east_m": round(e1 - e0, 1)})
    return out


def mode_change_s(modes, onset):
    """Seconds after onset when the flight mode first left the mode it had at onset (failsafe)."""
    ref = next((m for t, m in modes if t >= onset), None)
    return next((round(t - onset, 1) for t, m in modes if t >= onset and m != ref), None)


def counter_steps(samples, onset):
    """Times (s after onset) where a monotonic counter increased."""
    out = []
    for (_, c0), (t1, c1) in zip(samples, samples[1:]):
        if t1 >= onset and c1 != c0:
            out.append([round(t1 - onset, 1), (c1 - c0) % 256])
    return out


def flag_intervals(status, onset):
    out, start = [], None
    for s in status:
        if s["t"] < onset:
            continue
        if s["flag"] and start is None:
            start = s["t"]
        elif not s["flag"] and start is not None:
            out.append([round(start - onset, 1), round(s["t"] - onset, 1)])
            start = None
    if start is not None:
        out.append([round(start - onset, 1), round(status[-1]["t"] - onset, 1)])
    return out


def param_echo(params, names):
    got = {}
    for r in params:
        pid = r["param_id"]
        if pid in names:
            v = r["param_value"]
            if r.get("param_type") == 6:          # MAV_PARAM_TYPE_INT32, PX4 bytewise
                import struct
                v = struct.unpack("<i", struct.pack("<f", v))[0]
            got[pid] = v
    return got


def summarise(rows: list[dict]) -> dict:
    s = series(rows)
    exp = s["exp"]
    onset = exp["onset_s"]
    after_err = [x for x in s["err"] if x[0] >= onset]
    after_status = [x for x in s["status"] if x["t"] >= onset]
    first_flag = next((x["t"] - onset for x in after_status if x["flag"]), None)
    t_end = after_err[-1][0] if after_err else onset
    final = after_err[-1] if after_err else (onset, 0.0, 0.0)
    off_end = spoof_at(s["spoof"], t_end)
    # Spoof is dragged east; EKF east error > 0 means the EKF believes it is east of truth (spoof side).
    captured = [x for x in after_err if spoof_at(s["spoof"], x[0]) > 0]
    dev = [path_deviation((e, n)) for t, e, n in s["truth"] if t >= onset]
    rs = resets(s["err"], onset)
    return {
        "case": f"{exp['autopilot']}-{exp['config']}-{exp['spoof']}-{(exp['rate_mps'] if exp['spoof'] != 'step' else exp['step_m']):g}",
        "autopilot": exp["autopilot"], "config": exp["config"], "params_requested": exp["params"],
        "params_echoed": param_echo(s["params"], set(exp["params"])),
        "spoof": exp["spoof"], "rate_mps": exp["rate_mps"], "step_m": exp["step_m"], "seed": exp["seed"],
        "outcome": s["end"]["outcome"] if s["end"] else "incomplete",
        # 1 Hz HEARTBEAT resolution; None when the mission completed (PX4 then switches to LOITER by itself)
        "failsafe_mode_change_s": (None if s["end"] and s["end"]["outcome"] == "mission_complete"
                                   else mode_change_s(s["modes"], onset)),
        "spoof_offset_end_m": round(off_end, 1),
        "first_gps_flag_s": None if first_flag is None else round(first_flag, 1),
        "gps_flag_reports": sum(1 for x in after_status if x["flag"]),
        "status_reports_after_onset": len(after_status),
        "gps_flag_intervals_s": flag_intervals(s["status"], onset),
        "max_pos_innov_norm": round(max((x["pos_ratio"] for x in after_status), default=0.0), 2),
        "max_vel_innov_norm": round(max((x["vel_ratio"] for x in after_status), default=0.0), 2),
        "resets": rs, "reset_count": len(rs),
        # PX4 only: ODOMETRY.reset_counter = quat + velNE + velD + posNE + posD resets (EKF2.cpp PublishOdometry)
        "px4_odometry_reset_steps": counter_steps(s["odom_resets"], onset) if exp["autopilot"] == "px4" else None,
        "ekf_err_east_end_m": round(final[1], 1),
        "ekf_err_end_m": round(math.hypot(final[1], final[2]), 1),
        "ekf_err_max_m": round(max((math.hypot(e, n) for _, e, n in after_err), default=0.0), 1),
        "capture_ratio_end": round(final[1] / off_end, 2) if off_end > 0 else None,
        "max_capture_shortfall_m": round(max((spoof_at(s["spoof"], t) - e for t, e, _ in captured), default=0.0), 1),
        "max_cross_track_dev_m": round(max(dev, default=0.0), 1),
        "statustext_after_onset": [[round(t - onset, 1), txt] for t, txt in s["statustext"] if t >= onset][:20],
    }


def timeline(rows: list[dict]) -> dict:
    s = series(rows)
    onset = s["exp"]["onset_s"]
    return {"case": summarise(rows)["case"], "onset_s": onset,
            "t": [round(t - onset, 2) for t, _, _ in s["err"]],
            "ekf_err_east_m": [round(e, 2) for _, e, _ in s["err"]],
            "spoof_m": [round(spoof_at(s["spoof"], t), 2) for t, _, _ in s["err"]],
            "flag_t": [round(x["t"] - onset, 2) for x in s["status"] if x["flag"]],
            "pos_ratio_t": [round(x["t"] - onset, 2) for x in s["status"]],
            "pos_ratio": [round(x["pos_ratio"], 3) for x in s["status"]]}


def fmt_row(r: dict) -> str:
    x = r["rate_mps"] if r["spoof"] != "step" else r["step_m"]
    return (f"{r['autopilot']:9} {r['config']:8} {r['spoof']:8} {x:>5g} | flag@{r['first_gps_flag_s']!s:>5} "
            f"n={r['gps_flag_reports']:>3} | resets {r['reset_count']:>2} "
            f"{[(z['t_s'], z['jump_m']) for z in r['resets']][:6]} | spoof {r['spoof_offset_end_m']:>5} "
            f"ekfE {r['ekf_err_east_end_m']:>6} max {r['ekf_err_max_m']:>6} dev {r['max_cross_track_dev_m']:>6} "
            f"| {r['outcome']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("logs", nargs="+", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--timeline", type=Path, help="write the time series of the first log")
    a = ap.parse_args(argv)
    if a.timeline:
        a.timeline.write_text(json.dumps(timeline(load(a.logs[0]))))
        return 0
    rows = []
    for p in sorted(a.logs):
        try:
            rows.append(summarise(load(p)))
        except (StopIteration, KeyError) as e:
            print(f"{p.name}: incomplete log ({e!r})", file=sys.stderr)
    for r in rows:
        print(fmt_row(r))
    if a.out:
        a.out.write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
