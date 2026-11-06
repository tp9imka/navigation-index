#!/usr/bin/env python3
"""Small seed sweep: ./run.sh once per (seed, spoof, rate) with tag s<seed>-<spoof>-<rate>, then
an aggregate of every matching runs/*.raw.jsonl into data/sweep_summary.json (with --update-reference).

    python3 sweep.py --seeds 1 2 3                      # fly + aggregate, ~5 min wall per seed
    python3 sweep.py --seeds 1 2 3 --aggregate-only
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
import to_navdash_fw  # noqa: E402

KEYS = ("ttd_s", "xte_max_after_onset_m", "xte_at_route_end_m", "truth_to_final_wp_at_route_end_m",
        "loiter_center_offset_m", "ekf_err_at_route_end_m", "ref_err_max_after_alarm_m", "outcome",
        "ekf_gps_glitch_reports_after_onset", "flown_after_onset_m")


def tag(seed, spoof, rate):
    return f"s{seed}-{spoof}-{rate:g}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--spoof", default="coherent")
    ap.add_argument("--rates", type=float, nargs="+", default=[1.0])
    ap.add_argument("--aggregate-only", action="store_true")
    ap.add_argument("--update-reference", action="store_true")
    a = ap.parse_args(argv)
    if not a.aggregate_only:
        for seed in a.seeds:
            for rate in a.rates:
                env = os.environ | {"SEED": str(seed), "SPOOF": a.spoof, "RATE": f"{rate:g}", "TAG": tag(seed, a.spoof, rate)}
                r = subprocess.run([str(HERE / "run.sh")], env=env)
                if r.returncode:
                    print(f"seed {seed} rate {rate}: run.sh failed ({r.returncode})")
    out = {}
    for seed in a.seeds:
        for rate in a.rates:
            for s in to_navdash_fw.SCENARIOS:
                p = HERE / "runs" / f"{tag(seed, a.spoof, rate)}-{s}.raw.jsonl"
                if not p.exists():
                    continue
                summ, _ = to_navdash_fw.analyse(to_navdash_fw.load(p))
                out.setdefault(f"{a.spoof} {rate:g} m/s", {}).setdefault(s, {})[str(seed)] = {k: summ.get(k) for k in KEYS}
    for cond, by_s in out.items():
        for s, by_seed in by_s.items():
            xs = [v["xte_max_after_onset_m"] for v in by_seed.values()]
            ttd = [min(v["ttd_s"].values()) for v in by_seed.values() if v["ttd_s"]]
            print(f"{cond} {s:9s} seeds {sorted(by_seed)} xte max {xs} first alarm {ttd}")
    path = (HERE / "data" if a.update_reference else HERE / "runs") / "sweep_summary.json"
    path.write_text(json.dumps(out, indent=1))
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
