#!/usr/bin/env python3
"""Convert two PX4 companion raw logs (monitor run, baseline run) into navdash/1 tracks for
templates/demo-dashboard, plus summary.json and a comparison with the ArduPilot golden demo.

PX4 rows are first normalised to the shapes samples/golden-demo/to_navdash.py reads
(HIL_STATE_QUATERNION => SIMSTATE), then its analysis and track helpers run unchanged. The
ArduPilot-only fields (EKF_STATUS_REPORT, lane switches, MAV_CMD_SET_EKF_SOURCE_SET ACK) are
replaced by their PX4 counterparts (ESTIMATOR_STATUS, PARAM_VALUE echo of EKF2_GPS_CTRL).

    python to_navdash_px4.py runs/px4-monitor.raw.jsonl runs/px4-baseline.raw.jsonl            # => runs/navdash-px4
    python to_navdash_px4.py runs/px4-monitor.raw.jsonl runs/px4-baseline.raw.jsonl --out data # refresh reference
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOLDEN = HERE.parent / "golden-demo"
sys.path.insert(0, str(GOLDEN))

import to_navdash as T  # noqa: E402

ESTIMATOR_GPS_GLITCH = 1024          # MAVLink ESTIMATOR_STATUS_FLAGS
ESTIMATOR_POS_HORIZ_ABS = 16
TEST_RATIO_WARN = 1.0                # PX4 innovation test ratios fail above 1
ARDUPILOT_ONLY = ("ekf_lane_switches", "ekf_lane_switches_after_action", "source_set_ack",
                  "ekf_gps_glitching_reports", "ekf_max_pos_horiz_variance_after_onset",
                  "ekf_reports_over_0p5_after_onset")
SRC = {"source": "PX4 v1.17.0 SIH (sihsim_quadx, Docker), logged by companion_px4.py"}


MAV_PARAM_TYPE_INT32 = 6


def param_value(r: dict):
    """PX4 sends INT32 params bytewise in the float field."""
    if r.get("param_type") == MAV_PARAM_TYPE_INT32:
        return struct.unpack("<i", struct.pack("<f", r["param_value"]))[0]
    return r["param_value"]


def normalise(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        if r["type"] == "HIL_STATE_QUATERNION":
            out.append({"type": "SIMSTATE", "t": r.get("t"), "lat": r["lat"], "lng": r["lon"]})
        out.append(r)
    return out


def px4_fields(rows: list[dict], s: dict) -> dict:
    onset = s["spoof"]["onset_s"]
    est = [r for r in T.by_type(rows, "ESTIMATOR_STATUS") if r["t"] >= onset]
    act = T.first(T.by_type(rows, "COMPANION_PX4_ACTION"), lambda r: True)
    ack = None
    if act:
        ack = T.first(T.by_type(rows, "PARAM_VALUE"),
                      lambda r: r["param_id"] == "EKF2_GPS_CTRL" and r["t"] >= act["t"] - 0.01)
    for k in ARDUPILOT_ONLY:
        s.pop(k, None)
    s.update({
        "px4_action_params": act and act["params"],
        "gps_ctrl_echo": ack and {"value": param_value(ack), "t_s": round(ack["t"], 2)},
        "ekf_gps_glitch_reports": sum(1 for r in est if r["flags"] & ESTIMATOR_GPS_GLITCH),
        "ekf_max_pos_horiz_ratio_after_onset": round(max((r["pos_horiz_ratio"] for r in est), default=0), 3),
        "ekf_pos_horiz_ratio_over_1_after_onset": sum(1 for r in est if r["pos_horiz_ratio"] > TEST_RATIO_WARN),
        "ekf_max_eph_after_onset_m": round(max((r["pos_horiz_accuracy"] for r in est), default=0), 2),
        "ekf_reports_without_abs_pos_after_onset": sum(1 for r in est if not r["flags"] & ESTIMATOR_POS_HORIZ_ABS),
    })
    return s


def analyse(rows: list[dict]) -> dict:
    return px4_fields(rows, T.analyse(rows))


def relabel(lines: list[dict], summary: dict) -> list[dict]:
    p = summary.get("px4_action_params") or {}
    for ln in lines:
        if ln.get("event") == "source_switched":
            ln["text"] = ("PARAM_SET " + ", ".join(f"{k}={v}" for k, v in p.items())
                          + f" (GNSS out of EKF2, external vision in); echo {summary.get('gps_ctrl_echo')}")
    return lines


def convert(mon_rows, base_rows, out: Path) -> dict:
    mon_rows, base_rows = normalise(mon_rows), normalise(base_rows)
    out.mkdir(parents=True, exist_ok=True)
    s_mon, s_base = analyse(mon_rows), analyse(base_rows)
    onset = s_mon["spoof"]["onset_s"]
    sp = s_mon["spoof"]
    T.write_track(out / "truth.jsonl", T.header("truth", "truth", "Truth, monitor run (SIH HIL_STATE_QUATERNION)",
                                                "#e8eaed", **SRC),
                  [T.pos(r) for r in T.decimate(T.truth_rows(mon_rows), T.TRACK_PERIOD_S)]
                  + [{"t": onset, "event": "attack_onset", "ground_truth": True,
                      "text": f"GPS drag starts: {sp['rate_mps']} m/s toward {sp['bearing_deg']} deg ({sp['kind']})"}])
    T.write_track(out / "ss-monitor.jsonl",
                  T.header("ss-monitor", "fused", "Companion integrity solution (SS FDE main filter) + HPL", "#ffd54f",
                           primary=True, alert_limit_m=T.SS_ALERT_LIMIT_M, **SRC,
                           pl_method="solution separation, samples/golden-demo/ss_fde.py (P_FA 1e-5, P_MD 1e-3, IR_ff 1e-7)",
                           note="VIO dead reckoning + GNSS + visual geoloc; PL bounds this solution, not PX4 EKF2"),
                  T.ss_lines(mon_rows))
    T.write_track(out / "ekf-monitor.jsonl",
                  T.header("ekf-monitor", "fused", "PX4 EKF2 output, integrity monitor on", "#4fc3f7", primary=False,
                           **SRC, note="GLOBAL_POSITION_INT; after the alarm EKF2 runs on external vision (ODOMETRY)"),
                  relabel(T.primary_lines(mon_rows, s_mon | {"source_set_ack": None}), s_mon))
    T.write_track(out / "truth-baseline.jsonl",
                  T.header("truth-baseline", "truth", "Truth, no monitor (where the copter really went)", "#ff8a65", **SRC),
                  [T.pos(r) for r in T.decimate(T.truth_rows(base_rows), T.TRACK_PERIOD_S)])
    T.write_track(out / "ekf-baseline.jsonl",
                  T.header("ekf-baseline", "fused", "PX4 EKF2 output, no monitor (what the copter believed)", "#9ccc65", **SRC),
                  [T.pos(r, sources=["gps"]) for r in T.decimate(T.ekf_rows(base_rows), T.TRACK_PERIOD_S)]
                  + T.statustext_events(base_rows, onset))
    gps = [{"t": r["t"], "lat": r["lat"] * 1e-7, "lon": r["lon"] * 1e-7} for r in T.by_type(mon_rows, "GPS_RAW_INT")]
    T.write_track(out / "gnss.jsonl", T.header("gnss", "gnss", "GPS_RAW_INT as received (spoofed HIL_GPS), monitor run",
                                               "#ef5350", **SRC),
                  [T.pos(r) for r in T.decimate(gps, T.FIX_PERIOD_S)])
    T.write_track(out / "vgeo.jsonl", T.header("vgeo", "altpnt", T.VGEO_LABEL[s_mon["vgeo"]], "#ba68c8", **SRC),
                  [T.pos(r) for r in T.decimate(T.by_type(mon_rows, "COMPANION_VGEO"), T.FIX_PERIOD_S)])
    z = T.zone(mon_rows)
    z["features"][0]["properties"]["label"] = f"GPS drag {sp['rate_mps']} m/s (HIL_GPS, {sp['kind']})"
    (out / "zones.geojson").write_text(json.dumps(z))
    manifest = {"schema": "navdash/1",
                "title": f"Golden demo PX4: SIH GPS drag ({sp['kind']}, {sp['rate_mps']} m/s), monitor vs none",
                "tracks": ["truth.jsonl", "truth-baseline.jsonl", "ss-monitor.jsonl", "ekf-monitor.jsonl",
                           "ekf-baseline.jsonl", "gnss.jsonl", "vgeo.jsonl"],
                "zones": "zones.geojson"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    summary = {"monitor": s_mon, "baseline": s_base}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


COMPARE_KEYS = ("time_to_detect_s", "spoof_offset_at_alarm_m", "max_path_deviation_after_onset_m",
                "path_deviation_at_end_m", "max_ekf_error_m", "outcome", "mission_duration_s")


def compare(px4: dict, ardupilot: dict) -> dict:
    """Side by side headline numbers; None where a run did not produce the value."""
    return {k: {f"{plat}_{mode}": src[mode].get(k) for plat, src in (("px4", px4), ("ardupilot", ardupilot))
                for mode in ("monitor", "baseline")} for k in COMPARE_KEYS}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("monitor_log", type=Path)
    ap.add_argument("baseline_log", type=Path)
    ap.add_argument("--out", type=Path, default=HERE / "runs" / "navdash-px4")
    ap.add_argument("--ardupilot", type=Path, default=GOLDEN / "data" / "v2" / "summary.json",
                    help="ArduPilot summary to compare against (default: golden-demo v2 reference)")
    a = ap.parse_args(argv)
    s = convert(T.load(a.monitor_log), T.load(a.baseline_log), a.out)
    if a.ardupilot.exists():
        (a.out / "compare.json").write_text(json.dumps(compare(s, json.loads(a.ardupilot.read_text())), indent=2) + "\n")
    for k in ("monitor", "baseline"):
        r = s[k]
        print(f"{k:8s} alarm t={r['alarm_t_s']} (TTD {r['time_to_detect_s']} s, spoof {r['spoof_offset_at_alarm_m']} m)"
              f" max path dev after onset={r['max_path_deviation_after_onset_m']} m at end={r['path_deviation_at_end_m']} m"
              f" max EKF err={r['max_ekf_error_m']} m gps_glitch={r['ekf_gps_glitch_reports']}"
              f" outcome={r['outcome']} detect={ {d: v['t_s'] for d, v in r['detect'].items()} }")
    return 0


if __name__ == "__main__":
    sys.exit(main())
