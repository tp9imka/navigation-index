"""Replay the VAARA Jammertest 2024 u-blox logs through the unmodified gnss-interference-monitor scorer
and score each labelled test window. Stdlib only.

  python3 replay.py --data DIR [--labels labels.json] [--static-ref] [--no-rx-clock] [--no-pos-drift]
                    [--baseline-max-score X] [--spp-clock DIR] [--out results.json]
                    [--epochs-csv DIR] [--only SUBSTR]

DIR is a VAARA checkout (or the .ubx files at their repo paths, decompressed from .ubx.xz).

Per window: detected (any non-clean verdict inside it), time to first alert from the logged start
(negative = alerts began before the logged start, i.e. the label is late), whether an alarm was
already latched at the start, fraction of epochs alerting, and which detectors fired. Quiet windows
and time outside every window give false-alarm counts (alarm raises per hour).

--static-ref feeds ref_vel = (0, 0) ("known parked") for files marked static, which turns on the
scorer's external-reference mode. Receiver time minus the reconstructed time axis is fed as
clk_bias_ns unless --no-rx-clock, so a receiver time jump > MAX_STEP_S reaches clock_jump; slower
time drags are absorbed by the reconstruction and are invisible on this path.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ubx_nmea_epochs import to_epochs  # noqa: E402
import scorer as scorer_mod  # noqa: E402
from scorer import InterferenceScorer, PositionConsistency, haversine_m  # noqa: E402

CAR_MAX_SPEED_MPS = 70.0
GPS_EPOCH = calendar.timegm((1980, 1, 6, 0, 0, 0))
GPS_UTC_LEAP_S = 18
WEEK_S = 604800
LEAD_S = 300  # alerts this long before a logged start still count toward that window (labels are approximate)
NS_PER_S = 1e9
REF_MARGIN_S = 120  # static truth = median fix at least this far from every labelled window


def utc(day: str, hms: str) -> float:
    y, m, d = (int(x) for x in day.split("-"))
    hh, mm, ss = (int(x) for x in hms.split(":"))
    return float(calendar.timegm((y, m, d, hh, mm, ss)))


def hms(t: float) -> str:
    t = int(round(t)) % 86400
    return f"{t // 3600:02d}:{t // 60 % 60:02d}:{t % 60:02d}"


class _NoPositionConsistency(PositionConsistency):
    """Turns off pos_drift / vel_mismatch without touching scorer.py: residuals read 0 so they never alert
    and never block the alarm from clearing."""

    def step(self, ep, armed, may_learn, hits, alerts):
        self.last_z = self.last_vz = 0.0


def make_scorer(pos_drift: bool = True) -> InterferenceScorer:
    scorer = InterferenceScorer(max_speed_mps=CAR_MAX_SPEED_MPS)
    if not pos_drift:
        scorer.pos = _NoPositionConsistency()
    return scorer


def read_spp_clock(stat_path: Path) -> dict[int, float]:
    """RTKLIB solution status $CLK (receiver clock vs GPS time, ns) keyed by whole UTC second."""
    out = {}
    for line in stat_path.read_text().splitlines():
        if line.startswith("$CLK"):
            f = line.split(",")
            clk = float(f[5])
            if clk != 0.0:  # 0 = no GPS satellite in that solution
                out[round(GPS_EPOCH + int(f[1]) * WEEK_S + float(f[2]) - GPS_UTC_LEAP_S)] = clk
    return out


def run_file(buf: bytes, spec: dict, static_ref: bool, rx_clock: bool, pos_drift: bool = True,
             spp_clock: dict[int, float] | None = None):
    scorer = make_scorer(pos_drift)
    rows = []
    for ep, info in to_epochs(buf, spec["day"], spec.get("period_s", 1.0)):
        if spp_clock is not None:
            ep.clk_bias_ns = spp_clock.get(round(ep.t))
        elif rx_clock and info["rx_t"] is not None:
            ep.clk_bias_ns = (info["rx_t"] - ep.t) * NS_PER_S
        if static_ref and spec.get("static"):
            ep.ref_vel_e = ep.ref_vel_n = 0.0
        a = scorer.assess(ep)
        rows.append({"t": ep.t, "verdict": a.verdict, "alarm": a.alarm.active,
                     "detectors": sorted({x.detector for x in a.alerts}), "fix": ep.has_fix,
                     "lat": ep.lat, "lon": ep.lon, "n_cn0": len(ep.cn0 or {}),
                     "med_cn0": statistics.median(ep.cn0.values()) if ep.cn0 else None,
                     "time_jump_s": info["time_jump_s"], "jam": a.jam_score, "spoof": a.spoof_score})
    return rows


def window_metrics(rows, start, end, lead_from=None):
    """lead_from: earliest time an alert may count toward this window (default start - LEAD_S; the
    caller passes the previous window's end when tests are back to back)."""
    lead_from = start - LEAD_S if lead_from is None else max(lead_from, start - LEAD_S)
    inside = [r for r in rows if start <= r["t"] <= end]
    lead = [r for r in rows if lead_from < r["t"] <= end]
    if not inside:
        return {"epochs": 0, "covered": False}
    first = next((r for r in lead if r["verdict"] != "clean"), None)
    det = Counter(d for r in inside if r["verdict"] != "clean" for d in r["detectors"])
    sub = Counter(d for r in inside if r["verdict"] == "clean" for d in r["detectors"])
    fam = Counter(f for r in inside if r["verdict"] != "clean" for f in r["verdict"].split("+"))
    before = [r for r in rows if r["t"] < start]
    return {
        "epochs": len(inside), "covered": True,
        "coverage_s": round(inside[-1]["t"] - inside[0]["t"]),
        "fix_fraction": round(sum(r["fix"] for r in inside) / len(inside), 3),
        "detected": any(r["verdict"] != "clean" for r in inside),
        "ttd_s": None if first is None else round(first["t"] - start),
        "first_alert_utc": None if first is None else hms(first["t"]),
        "first_detectors": None if first is None else first["detectors"],
        "alarm_latched_at_start": bool(before and before[-1]["alarm"]),
        "alert_epoch_fraction": round(sum(r["verdict"] != "clean" for r in inside) / len(inside), 3),
        "alarm_epoch_fraction": round(sum(r["alarm"] for r in inside) / len(inside), 3),
        "families": dict(fam), "detector_epochs": dict(det.most_common()),
        "sub_alert_epochs": dict(sub.most_common()),
        "max_time_jump_s": max((abs(r["time_jump_s"]) for r in inside), default=0.0),
    }


def false_alarms(rows, spans):
    """Alarm raises, alert epochs and detectors over the epochs inside the given (start, end) spans."""
    sel = [i for i, r in enumerate(rows) if any(s <= r["t"] <= e for s, e in spans)]
    raises = sum(1 for i in sel if rows[i]["alarm"] and (i == 0 or not rows[i - 1]["alarm"]))
    hours = len(sel) / 3600.0
    det = Counter(d for i in sel if rows[i]["verdict"] != "clean" for d in rows[i]["detectors"])
    sub = Counter(d for i in sel if rows[i]["verdict"] == "clean" for d in rows[i]["detectors"])
    return {"epochs": len(sel), "hours": round(hours, 2), "alarm_raises": raises,
            "raises_per_hour": round(raises / hours, 1) if hours else None,
            "alert_epochs": sum(rows[i]["verdict"] != "clean" for i in sel),
            "alarm_epoch_fraction": round(sum(rows[i]["alarm"] for i in sel) / len(sel), 3) if sel else None,
            "detector_epochs": dict(det.most_common()), "sub_alert_epochs": dict(sub.most_common())}


def static_position_error(rows, windows):
    """For a static receiver: reference = median fix more than REF_MARGIN_S from every labelled window."""
    out_fix = [r for r in rows if r["fix"] and not any(w[0] - REF_MARGIN_S <= r["t"] <= w[1] + REF_MARGIN_S for w in windows)]
    if len(out_fix) < 30:
        return None, {}
    ref = (statistics.median(r["lat"] for r in out_fix), statistics.median(r["lon"] for r in out_fix))
    per = {}
    for s, e, name in windows:
        errs = sorted(haversine_m(ref[0], ref[1], r["lat"], r["lon"]) for r in rows if r["fix"] and s <= r["t"] <= e)
        if errs:
            per[name] = {"median_m": round(statistics.median(errs), 1),
                         "p95_m": round(errs[int(0.95 * (len(errs) - 1))], 1), "max_m": round(errs[-1], 1)}
    base = sorted(haversine_m(ref[0], ref[1], r["lat"], r["lon"]) for r in out_fix)
    per["outside-windows"] = {"median_m": round(statistics.median(base), 1),
                              "p95_m": round(base[int(0.95 * (len(base) - 1))], 1), "max_m": round(base[-1], 1)}
    return ref, per


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--labels", type=Path, default=HERE / "labels.json")
    ap.add_argument("--static-ref", action="store_true")
    ap.add_argument("--no-rx-clock", action="store_true")
    ap.add_argument("--no-pos-drift", action="store_true", help="drop the position/velocity consistency detectors")
    ap.add_argument("--baseline-max-score", type=float,
                    help="what-if: override scorer.BASELINE_MAX_SCORE for this run (module attribute, file untouched)")
    ap.add_argument("--spp-clock", type=Path,
                    help="dir with <stem>.brdc.spp.pos.stat from run_rtklib_spp.sh; replaces the receiver-time clock")
    ap.add_argument("--only")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--epochs-csv", type=Path)
    ap.add_argument("--quiet", action="store_true", help="no per-file tables on stdout")
    args = ap.parse_args(argv)
    labels = json.loads(args.labels.read_text())
    shipped = scorer_mod.BASELINE_MAX_SCORE
    if args.baseline_max_score is not None:
        scorer_mod.BASELINE_MAX_SCORE = args.baseline_max_score
    try:
        _run(args, labels)
    finally:
        scorer_mod.BASELINE_MAX_SCORE = shipped


def _run(args, labels):
    results = []
    for spec in labels["files"]:
        if args.only and args.only not in spec["path"]:
            continue
        path = args.data / spec["path"]
        if not path.exists():
            print(f"skip (missing): {path}", file=sys.stderr)
            continue
        spp_clock = None
        if args.spp_clock:
            stat = args.spp_clock / (Path(spec["path"]).stem + ".brdc.spp.pos.stat")
            if not stat.exists():
                continue
            spp_clock = read_spp_clock(stat)
        rows = run_file(path.read_bytes(), spec, args.static_ref, not args.no_rx_clock, not args.no_pos_drift, spp_clock)
        if args.epochs_csv:
            args.epochs_csv.mkdir(parents=True, exist_ok=True)
            with open(args.epochs_csv / (Path(spec["path"]).stem + ".csv"), "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                w.writeheader()
                for r in rows:
                    w.writerow({**r, "detectors": " ".join(r["detectors"])})
        wins = [(utc(spec["day"], w["start"]), utc(spec["day"], w["end"]), w["test"]) for w in spec["windows"]]
        per = []
        for i, (w, (s, e, _)) in enumerate(zip(spec["windows"], wins)):
            prev_end = max((pe for ps, pe, _ in wins[:i] if pe < s), default=None)
            per.append({"test": w["test"], "kind": w["kind"], "source": w["source"], "start": w["start"],
                        "end": w["end"], **window_metrics(rows, s, e, prev_end)})
        quiet = [(s, e) for (s, e, _), w in zip(wins, spec["windows"]) if w["kind"] == "quiet"]
        t0, t1 = rows[0]["t"], rows[-1]["t"]
        gaps, cur = [], t0
        for s, e, _ in sorted(wins):
            if s - LEAD_S > cur:
                gaps.append((cur, s - LEAD_S))
            cur = max(cur, e + LEAD_S)
        if cur < t1:
            gaps.append((cur, t1))
        res = {"file": spec["path"], "epochs": len(rows), "span_utc": [hms(t0), hms(t1)],
               "static_ref": bool(args.static_ref and spec.get("static")), "windows": per,
               "quiet": false_alarms(rows, quiet) if quiet else None,
               "no_logged_test": false_alarms(rows, gaps)}
        if spec.get("static"):
            ref, perr = static_position_error(rows, wins)
            res["static_fix_error"] = {"reference": ref, "per_window": perr}
        results.append(res)
        if not args.quiet:
            print_file(res)
    if args.out:
        args.out.write_text(json.dumps({"static_ref": args.static_ref, "rx_clock": not args.no_rx_clock,
                                        "pos_drift": not args.no_pos_drift,
                                        "baseline_max_score": scorer_mod.BASELINE_MAX_SCORE,
                                        "spp_clock": bool(args.spp_clock),
                                        "results": results}, indent=1))


def print_file(res):
    print(f"\n== {res['file']}  {res['span_utc'][0]}-{res['span_utc'][1]} UTC, {res['epochs']} epochs"
          f"{'  [static ref]' if res['static_ref'] else ''}")
    print(f"{'test':<8} {'kind':<5} {'window':<17} {'det':<4} {'ttd_s':>6} {'latched':<7} {'alert%':>6} detectors (epochs)")
    for w in res["windows"]:
        if not w.get("covered"):
            print(f"{w['test']:<8} {w['kind']:<5} {w['start']}-{w['end']} not covered by the log")
            continue
        dets = ", ".join(f"{k} {v}" for k, v in list(w["detector_epochs"].items())[:5])
        ttd = "-" if w["ttd_s"] is None else str(w["ttd_s"])
        print(f"{w['test']:<8} {w['kind']:<5} {w['start'][:5]}-{w['end'][:5]}{'*' if w['source'] != 'vaara' else ' '}     "
              f"{'yes' if w['detected'] else 'no':<4} {ttd:>6} {str(w['alarm_latched_at_start']):<7} "
              f"{100 * w['alert_epoch_fraction']:>5.0f}% {dets}")
    for key in ("quiet", "no_logged_test"):
        fa = res.get(key)
        if fa:
            dets = ", ".join(f"{k} {v}" for k, v in list(fa["detector_epochs"].items())[:4])
            print(f"{key}: {fa['hours']} h, {fa['alarm_raises']} alarm raises ({fa['raises_per_hour']}/h), "
                  f"{fa['alert_epochs']} alert epochs; {dets}")
    if res.get("static_fix_error", {}).get("per_window"):
        print("receiver fix error vs median fix outside windows: " + "; ".join(
            f"{k} med {v['median_m']} / max {v['max_m']} m" for k, v in res["static_fix_error"]["per_window"].items()))


if __name__ == "__main__":
    main()
