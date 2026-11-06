#!/usr/bin/env python3
"""Small PX4 sweep: spoof type x drag rate x seed, each flown with the monitor acting and in
shadow (baseline), plus no-spoof flights for false alarms. Parallel lanes of run.sh; stdlib.

    python3 sweep.py                        # 20 flights, 3 lanes, ~30 min here
    python3 sweep.py --aggregate-only       # rebuild the table from runs/sweep/
    python3 sweep.py --update-reference     # also write data/sweep_summary.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import to_navdash_px4 as P  # noqa: E402

OUT = HERE / "runs" / "sweep"


def cases(seeds, rates):
    for kind, rate, seed in itertools.product(("position", "coherent"), rates, seeds):
        yield kind, rate, seed
    for seed in seeds:
        yield "none", 1.0, seed


def tag(kind, rate, seed):
    return f"sweep/{kind}-{rate:g}-s{seed}"


def fly(lane_q, case):
    lane = lane_q.get()
    try:
        kind, rate, seed = case
        env = os.environ | {"NAME": f"px4golden-l{lane}", "SPOOF": kind, "RATE": str(rate), "SEED": str(seed),
                            "TAG": tag(kind, rate, seed)}
        log = OUT / f"{kind}-{rate:g}-s{seed}.console.txt"
        with log.open("w") as f:
            rc = subprocess.call([str(HERE / "run.sh")], env=env, stdout=f, stderr=subprocess.STDOUT)
        print(f"lane {lane} {case} rc={rc}", flush=True)
    finally:
        lane_q.put(lane)


def aggregate(seeds, rates) -> list[dict]:
    rows = []
    for kind, rate, seed in cases(seeds, rates):
        t = tag(kind, rate, seed)
        mon, base = HERE / "runs" / f"{t}-monitor.raw.jsonl", HERE / "runs" / f"{t}-baseline.raw.jsonl"
        if not (mon.exists() and base.exists()):
            rows.append({"spoof": kind, "rate": rate, "seed": seed, "missing": True})
            continue
        sm = P.analyse(P.normalise(P.T.load(mon)))
        sb = P.analyse(P.normalise(P.T.load(base)))
        rows.append({"spoof": kind, "rate": rate, "seed": seed,
                     "detect_monitor": {d: v for d, v in sm["detect"].items() if d in ("chi2", "ss", "vel", "ss+vel")},
                     "detect_baseline": {d: v for d, v in sb["detect"].items() if d in ("chi2", "ss", "vel", "ss+vel")},
                     "dev_monitor_m": sm["max_path_deviation_after_onset_m"],
                     "dev_baseline_m": sb["max_path_deviation_after_onset_m"],
                     "ekf_err_monitor_m": sm["max_ekf_error_m"], "ekf_err_baseline_m": sb["max_ekf_error_m"],
                     "gps_glitch_baseline": sb["ekf_gps_glitch_reports"],
                     "outcome": [sm["outcome"], sb["outcome"]]})
    return rows


def show(rows):
    print(f"{'spoof':9s} {'rate':>4s} {'seed':>4s} {'TTD ss+vel':>10s} {'FA':>3s} {'dev mon':>8s} {'dev base':>8s}"
          f" {'glitch base':>11s}  outcome")
    for r in rows:
        if r.get("missing"):
            print(f"{r['spoof']:9s} {r['rate']:4g} {r['seed']:4d}  missing")
            continue
        d = r["detect_monitor"]["ss+vel"]
        print(f"{r['spoof']:9s} {r['rate']:4g} {r['seed']:4d} {str(d['ttd_s']):>10s} {int(d['false_alarm']):3d}"
              f" {r['dev_monitor_m']:8.1f} {r['dev_baseline_m']:8.1f} {r['gps_glitch_baseline']:11d}  {r['outcome']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--rates", type=float, nargs="+", default=[1.0, 3.0])
    ap.add_argument("--lanes", type=int, default=3)
    ap.add_argument("--aggregate-only", action="store_true")
    ap.add_argument("--update-reference", action="store_true")
    a = ap.parse_args(argv)
    if not a.aggregate_only:
        OUT.mkdir(parents=True, exist_ok=True)
        import queue
        q = queue.Queue()
        for k in range(a.lanes):
            q.put(k)
        with ThreadPoolExecutor(a.lanes) as ex:
            list(ex.map(lambda c: fly(q, c), list(cases(a.seeds, a.rates))))
    rows = aggregate(a.seeds, a.rates)
    show(rows)
    (OUT / "sweep_summary.json").write_text(json.dumps(rows, indent=2) + "\n")
    if a.update_reference:
        (HERE / "data").mkdir(exist_ok=True)
        (HERE / "data" / "sweep_summary.json").write_text(json.dumps(rows, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
