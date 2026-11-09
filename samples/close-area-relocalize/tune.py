"""Dev-seed calibration of the matcher thresholds (seed 1, so seed 0 stays held out).

.venv/bin/python tune.py [--layouts 30] [--poses 20]

Static, no flight: random free poses (clearance >= 0.3 m) in random-family layouts, one scan from
the true pose (arena sensor defaults), then
  - score at truth and at 0.3 m / 0.5 m offsets (sets S_INNOV),
  - hypotheses in the default window centred 0.5 m off truth (sets S_MIN and RATIO): how often
    the best is within 0.5 m of truth, and the best / second ratio when it is right vs wrong.
Writes results/tune_seed1.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np

from arena import run, sensors, world
import relocalize as R

SIGMAS = (0.06, 0.08, 0.1, 0.15)
RATIOS = (1.01, 1.02, 1.05, 1.1, 1.15)
HERE = os.path.dirname(os.path.abspath(__file__))


def q(a, ps=(5, 50, 95)):
    a = np.asarray(a, float)
    return {f"p{p}": round(float(np.percentile(a, p)), 4) for p in ps} if len(a) else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--layouts", type=int, default=30)
    ap.add_argument("--poses", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    s_truth, s_03, s_05, rows = [], [], [], []
    sweep = {sg: [] for sg in SIGMAS}
    for i in range(a.layouts):
        w = world.make_world("random", a.seed, i)
        m = R.ScanMatcher(w.grid)
        ms = {sg: R.ScanMatcher(w.grid, sigma=sg) for sg in SIGMAS}
        fan = sensors.RangeFan(rng=np.random.default_rng([a.seed, i, 4302]), **run.DEFAULTS["sensor"])
        rng = np.random.default_rng([a.seed, i, 4303])
        n = 0
        while n < a.poses:
            x, y = rng.uniform(w.xmin + 0.3, w.xmax - 0.3), rng.uniform(w.ymin + 0.3, w.ymax - 0.3)
            if w.clearance(x, y) < 0.3:
                continue
            n += 1
            yaw = rng.uniform(-math.pi, math.pi)
            scan = fan.scan(w, x, y, yaw, 0.0)
            st = m.score_at(scan, yaw, (x, y))
            if st is None:
                rows.append({"returns": "too_few"})
                continue
            s_truth.append(st)
            for d, sink in ((0.3, s_03), (0.5, s_05)):
                th = rng.uniform(-math.pi, math.pi)
                v = m.score_at(scan, yaw, (x + d * math.cos(th), y + d * math.sin(th)))
                if v is not None and v >= 0:
                    sink.append(v)
            th = rng.uniform(-math.pi, math.pi)
            c = (x + 0.5 * math.cos(th), y + 0.5 * math.sin(th))
            for sg, mm in ms.items():
                h2 = mm.hypotheses(scan, yaw, c)
                if h2:
                    sweep[sg].append((math.hypot(h2[0].x - x, h2[0].y - y),
                                      h2[0].score / h2[1].score if len(h2) > 1 and h2[1].score > 0 else 99.0))
            hy = m.hypotheses(scan, yaw, c)
            if not hy:
                rows.append({"returns": "ok", "hyps": 0})
                continue
            e = math.hypot(hy[0].x - x, hy[0].y - y)
            ratio = hy[0].score / hy[1].score if len(hy) > 1 and hy[1].score > 0 else None
            rows.append({"returns": "ok", "hyps": len(hy), "best_err": e, "best": hy[0].score, "ratio": ratio})
    ok = [r for r in rows if r.get("hyps")]
    right = [r for r in ok if r["best_err"] <= 0.5]
    wrong = [r for r in ok if r["best_err"] > 0.5]
    out = {
        "input": "synthetic", "seed": a.seed, "layouts": a.layouts, "poses_per_layout": a.poses,
        "command": "python tune.py " + " ".join(argv or []),
        "poses_total": len(rows), "too_few_returns": sum(1 for r in rows if r["returns"] == "too_few"),
        "score_at_truth": q(s_truth), "score_at_0p3m": q(s_03), "score_at_0p5m": q(s_05),
        "frac_truth_below_S_INNOV": round(float(np.mean(np.array(s_truth) < R.S_INNOV)), 4),
        "frac_0p3m_below_S_INNOV": round(float(np.mean(np.array(s_03) < R.S_INNOV)), 4),
        "frac_0p5m_below_S_INNOV": round(float(np.mean(np.array(s_05) < R.S_INNOV)), 4),
        "window_hyps": {"scans": len(ok), "best_within_0p5m": len(right), "best_wrong": len(wrong),
                        "best_score_right": q([r["best"] for r in right]),
                        "best_score_wrong": q([r["best"] for r in wrong]),
                        "ratio_right": q([r["ratio"] for r in right if r["ratio"]]),
                        "ratio_wrong": q([r["ratio"] for r in wrong if r["ratio"]]),
                        "frac_right_passing_rule": round(float(np.mean([r["best"] >= R.S_MIN and (r["ratio"] is None or r["ratio"] >= R.RATIO) for r in right])), 4) if right else None,
                        "wrong_passing_rule": sum(1 for r in wrong if r["best"] >= R.S_MIN and (r["ratio"] is None or r["ratio"] >= R.RATIO))},
        "sigma_ratio_sweep": {str(sg): {
            "scans": len(v), "best_wrong": sum(1 for e, _ in v if e > 0.5),
            "right_pass_frac": {str(rt): round(float(np.mean([r >= rt for e, r in v if e <= 0.5])), 4) for rt in RATIOS},
            "wrong_pass": {str(rt): sum(1 for e, r in v if e > 0.5 and r >= rt) for rt in RATIOS}}
            for sg, v in sweep.items()},
        "thresholds": {"S_INNOV": R.S_INNOV, "S_MIN": R.S_MIN, "RATIO": R.RATIO, "SIGMA_M": R.SIGMA_M},
    }
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", f"tune_seed{a.seed}.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
