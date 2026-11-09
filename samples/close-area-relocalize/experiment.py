"""Relocalization after VIO loss: A* known-map planner on the arena estimator with dropout / jump faults.

.venv/bin/python experiment.py --layouts 100 --seed 0            # random family, ~2-4 min on 8 cores
.venv/bin/python experiment.py --corridor --runs 20              # symmetric corridor case, ~30 s

Arms (all fly planners/astar_esdf.py known_map=True, scored on truth by the arena):
  truth       planner sees truth (reference, no estimator)
  estimator   (a) arena VIO-like estimator only, no relocalization
  hover_only  (a2) control arm: hover while lost (quality 0 / reset), then resume on the raw estimate
  single      (b) relocalize, commit to the best match on the first scan (rule disabled)
  multi       (c) relocalize, keep up to 5 hypotheses, RatioPersistence rule, hover until accept
  *_noinnov   ablation: b / c triggered only by reported loss (reset_counter, quality 0), no
              innovation test, to separate VIO-loss recovery from drift correction

hover_only / single / multi fly behind HoverGate: setpoint zero while pose.quality == 0.
Writes results/reloc_<family>_<seed>.json / .md, or results/reloc_corridor.json / .md.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import scipy

from arena import Planner, Setpoint, astar_esdf, estimator, faults, run, sensors, world
import relocalize as R

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
ARMS = ("truth", "estimator", "hover_only", "single", "multi", "single_noinnov", "multi_noinnov")
RELOC_ARMS = ("single", "multi", "single_noinnov", "multi_noinnov")
FAULTS = ("dropout", "jump")
WRONG_M = 0.5


class HoverGate(Planner):
    """Zero velocity while the pose source reports quality 0; replan at once on resume."""

    def __init__(self, inner):
        self.inner = inner
        self.uses_grid = inner.uses_grid
        self.name = "hover_gate+" + inner.name
        self.held = False

    def reset(self):
        self.inner.reset()
        self.held = False

    def step(self, pose, scan, goal, grid, dt):
        if pose.quality == 0:
            self.held = True
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        if self.held:
            self.held = False
            if hasattr(self.inner, "last_plan_t"):
                self.inner.last_plan_t = -math.inf
        return self.inner.step(pose, scan, goal, grid, dt)


def scan_fn_for(w, seed, index):
    """The relocalizer's lidar read: arena sensor model at the true pose, its own noise stream."""
    fan = sensors.RangeFan(rng=np.random.default_rng([seed, index, 4301]), **run.DEFAULTS["sensor"])
    return lambda truth: fan.scan(w, truth.x, truth.y, truth.yaw, truth.t)


def wrap(est, w, seed, index, arm):
    if arm == "estimator":
        return est
    return R.RelocPoseSource(est, w.grid, scan_fn_for(w, seed, index), mode=arm.split("_")[0] if arm != "hover_only" else arm,
                             innovation=not arm.endswith("_noinnov"))


def planner_for(arm):
    p = astar_esdf.make(known_map=True)
    return p if arm in ("truth", "estimator") else HoverGate(p)


def r4(v):
    return None if v is None else round(float(v), 4)


def row_extra(row, est, src, fault):
    e = np.array(src.errs if isinstance(src, R.RelocPoseSource) else est.errs)
    out = {"est_err_median_m": r4(np.median(e)), "est_err_max_m": r4(e.max()),
           "fault_log": fault.log if fault is not None else None}
    if isinstance(src, R.RelocPoseSource):
        ev = [x.to_dict() for x in src.events]
        out.update({"events": ev, "hover_s": round(src.hover_steps / run.DEFAULTS["plan_hz"], 2),
                    "wrong_commits": sum(1 for x in ev if x["err_m"] is not None and x["err_m"] > WRONG_M),
                    "match_ms_median": r4(np.median(src.match_ms)) if src.match_ms else None})
    return out


def run_cell(args):
    fault_name, arm, family, layouts, seed = args
    rows = []
    t0 = time.perf_counter()
    for i in range(layouts):
        w = world.make_world(family, seed, i)
        est = src = None
        if arm != "truth":
            sink = []
            est = estimator.make_pose_source_factory(fault_name, dark=True, sink=sink)(w, seed, i)
            src = wrap(est, w, seed, i, arm)
        row, _, _ = run.run_one(planner_for(arm), w, seed, i, run.DEFAULTS, src)
        if est is not None:
            row.update(row_extra(row, est, src, est.fault))
        rows.append(row)
    return fault_name, arm, rows, round(time.perf_counter() - t0, 1)


# ---- symmetric corridor ----
def corridor_world(index):
    """2 m wide, 14.8 m long corridor along x. Enter at the left end, leave at the right end.
    Area coordinates: lower wall x 2.6-20, y 8.7-9.0; upper wall x 0-17.4, y 11.0-11.3."""
    rng = np.random.default_rng([0, index, 4401])
    ax, ay = 1.5 + rng.uniform(-0.3, 0.3), 1.5 + rng.uniform(-0.3, 0.3)
    boxes = [(11.3, 8.85, 8.7, 0.15), (8.7, 11.15, 8.7, 0.15)]
    w = world.World(family="corridor", seed=0, xmin=-ax, ymin=-ay, xmax=20 - ax, ymax=20 - ay,
                    goal=(18.5 - ax, 18.5 - ay),
                    boxes=[world.Box(cx - ax, cy - ay, hx, hy) for cx, cy, hx, hy in boxes])
    w.grid = w.rasterize(world.RES)
    assert world.bfs_free_path(w.grid.inflated(world.RADIUS), w.grid.to_index(0, 0),
                               w.grid.to_index(*w.goal)) is not None
    w.area_origin = (ax, ay)
    return w


class CorridorJump(faults.Fault):
    """0.5 m VIO step along the corridor axis (sign seeded) when truth is at the corridor middle
    (area x 9.5-10.5, y 9-11), where no corridor end is within the 6 m range."""
    name = "corridor_jump"

    def __init__(self, w, rng, step_m=0.5):
        super().__init__(w, rng)
        self.sign = 1.0 if rng.random() < 0.5 else -1.0
        self.step_m, self.done = step_m, False
        self.log.update({"step_m": step_m, "sign": self.sign, "fired_t": None})

    def on_call(self, truth, est):
        ax, ay = self.world.area_origin
        if self.done or not (9.5 <= truth.x + ax <= 10.5 and 9.0 <= truth.y + ay <= 11.0):
            return None
        self.done = True
        self.log["fired_t"] = round(truth.t, 3)
        return self.sign * self.step_m, 0.0


def run_corridor_cell(args):
    arm, runs = args
    rows = []
    for i in range(runs):
        w = corridor_world(i)
        est = src = None
        if arm != "truth":
            f = CorridorJump(w, np.random.default_rng([0, i, 4402]))
            est = estimator.VioEstimator(np.random.default_rng([0, i, 4101]), [], f)
            src = wrap(est, w, 0, i, arm)
        row, _, _ = run.run_one(planner_for(arm), w, 0, i, run.DEFAULTS, src)
        if est is not None:
            row.update(row_extra(row, est, src, est.fault))
        rows.append(row)
    return "corridor_jump", arm, rows, 0.0


# ---- summaries ----
def summarize(rows):
    s = run.scorer.summarize(rows)
    ev = [e for x in rows for e in x.get("events", [])]
    acc = [e for e in ev if e["result"] == "accepted"]
    res = [e for e in ev if e["result"] in ("accepted", "resumed")]
    s.update({
        "events": len(ev),
        "events_by_reason": {k: sum(1 for e in ev if e["reason"] == k) for k in ("reset_counter", "quality_0", "innovation")},
        "accepted": len(acc),
        "wrong_commits": sum(1 for e in acc if e["err_m"] > WRONG_M),
        "runs_with_wrong_commit": sum(1 for x in rows if x.get("wrong_commits")),
        "open_at_end": sum(1 for e in ev if e["result"] == "open"),
        "open_by_last_verdict": {
            "none_too_few_returns": sum(1 for e in ev if e["result"] == "open" and e["last_verdict"] == "none"
                                        and e["last_returns"] is not None and e["last_returns"] < R.MIN_RETURNS),
            "none_low_score": sum(1 for e in ev if e["result"] == "open" and e["last_verdict"] == "none"
                                  and e["last_returns"] is not None and e["last_returns"] >= R.MIN_RETURNS),
            "ambiguous": sum(1 for e in ev if e["result"] == "open" and e["last_verdict"] == "ambiguous"),
            "ambiguous_truth_in_first_set": sum(1 for e in ev if e["result"] == "open" and e["last_verdict"] == "ambiguous"
                                                and e["truth_in_set"]),
            "pending_or_settling": sum(1 for e in ev if e["result"] == "open" and e["last_verdict"] in (None, "pending"))},
        "runs_ended_hovering": sum(1 for x in rows if any(e["result"] == "open" for e in x.get("events", []))
                                   and not x["reached"]),
        "no_returns": sum(1 for e in ev if e["result"] == "no_returns"),
        "truth_not_in_first_set": sum(1 for e in ev if e["truth_in_set"] is False),
        "median_recover_s": round(float(np.median([e["recover_s"] for e in res])), 2) if res else None,
        "p95_recover_s": round(float(np.percentile([e["recover_s"] for e in res], 95)), 2) if res else None,
        "median_hover_s": round(float(np.median([x["hover_s"] for x in rows if "hover_s" in x])), 2)
        if any("hover_s" in x for x in rows) else None,
        "median_est_err_m": r4(np.median([x["est_err_median_m"] for x in rows])) if rows and "est_err_median_m" in rows[0] else None,
        "median_run_max_err_m": r4(np.median([x["est_err_max_m"] for x in rows])) if rows and "est_err_max_m" in rows[0] else None,
        "fault_fired_runs": sum(1 for x in rows if (x.get("fault_log") or {}).get("fired_t") is not None),
    })
    return s


def f(v):
    return "-" if v is None else f"{v}"


HEAD = ("| fault | arm | runs | reached % | collision % | stuck % | timeout % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) "
        "| still hovering at end | median recover s | median run max err m | fault fired runs |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(fault, arm, s):
    rel = arm in RELOC_ARMS
    return (f"| {fault} | {arm} | {s['n']} | {s['reached_pct']} | {s['collision_pct']} | {s['stuck_pct']} | {s['timeout_pct']} "
            f"| {'/'.join(str(v) for v in s['events_by_reason'].values()) if s['events'] or arm == 'hover_only' else '-'} "
            f"| {s['accepted'] if rel else '-'} | {s['wrong_commits'] if rel else '-'} "
            f"| {s['open_at_end'] if arm in ('hover_only',) + RELOC_ARMS else '-'} "
            f"| {f(s['median_recover_s'])} | {f(s['median_run_max_err_m'])} "
            f"| {s['fault_fired_runs'] if arm != 'truth' else '-'} |")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--family", default="random", choices=world.FAMILIES)
    ap.add_argument("--corridor", action="store_true")
    ap.add_argument("--runs", type=int, default=20, help="corridor runs")
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    cmd = "python experiment.py " + " ".join(argv if argv is not None else sys.argv[1:])
    t0 = time.perf_counter()
    if a.corridor:
        cells = [(arm, a.runs) for arm in ARMS]
        fn, stem, faults_used = run_corridor_cell, "reloc_corridor", ("corridor_jump",)
    else:
        cells = [(fl, arm, a.family, a.layouts, a.seed) for fl in FAULTS for arm in ARMS if not (arm == "truth" and fl != FAULTS[0])]
        fn, stem, faults_used = run_cell, f"reloc_{a.family}_{a.seed}", FAULTS
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        out = list(ex.map(fn, cells))
    wall = time.perf_counter() - t0
    res = {}
    for fl, arm, rows, cw in out:
        res.setdefault(fl, {})[arm] = {"summary": summarize(rows), "cell_wall_s": cw, "runs": rows}
    lines = [HEAD]
    for fl in faults_used:
        for arm in ARMS:
            if arm in res.get(fl, {}):
                lines.append(line(fl, arm, res[fl][arm]["summary"]))
    if not a.corridor:                                 # truth ran once; show it under each fault
        lines.insert(len(ARMS) + 1, line(FAULTS[1], "truth", res[FAULTS[0]]["truth"]["summary"]))
    tab = "\n".join(lines)
    print(tab)
    print(f"\nwall {wall:.1f} s")
    os.makedirs(a.out, exist_ok=True)
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system()}
    params = {k: getattr(R, k) for k in ("SIGMA_M", "STEP_M", "W0_M", "W_MAX_M", "SEP_M", "K_MAX", "KEEP_FLOOR",
                                          "MIN_CLEAR_M", "MIN_RETURNS", "S_MIN", "RATIO", "N_SCANS", "ASSOC_M",
                                          "NONE_WIDEN", "S_INNOV", "INNOV_SCANS", "SETTLE_SCANS")}
    with open(os.path.join(a.out, stem + ".json"), "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "family": "corridor" if a.corridor else a.family,
                   "seed": a.seed, "wall_s": round(wall, 1), "workers": a.workers, "params": params,
                   "config": run.DEFAULTS, "env": env, "results": res}, fh, indent=1)
    with open(os.path.join(a.out, stem + ".md"), "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {wall:.1f} s, {a.workers} workers\n\n{tab}\n")
    print(f"wrote {stem}.json / .md")


if __name__ == "__main__":
    main()
