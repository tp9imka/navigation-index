"""Hover timeout + disambiguating move vs hover-only multi-hypothesis and single + consistency check.

.venv/bin/python run_disambiguate.py --corridor --runs 20       # symmetric corridor, corridor_jump
.venv/bin/python run_disambiguate.py --layouts 100 --seed 0     # random family, dropout and jump

Arms (all A* known map behind a gate that hovers while pose quality is 0, scored on truth):
  single        (b) commit to the best match at once + innovation test (experiment.py, unchanged)
  multi         (c) RatioPersistence, hover until accept (experiment.py, unchanged)
  multi_random  (d) (c) + after 1 s, a random collision-free move from the library
  multi_sep     (e) (c) + after 1 s, the move with the largest expected matcher-score separation
  multi_ig      (f) (c) + after 1 s, the move with the largest expected entropy reduction (Fox 1998)
Writes results/disamb_corridor.json / .md or results/disamb_<family>_<seed>.json / .md.
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

from arena import Setpoint, astar_esdf, estimator, run, world
import disambiguate as D
import experiment as X
import relocalize as R

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
ARMS = ("single", "multi", "multi_random", "multi_sep", "multi_ig")
LABEL = {"single": "(b)", "multi": "(c)", "multi_random": "(d)", "multi_sep": "(e)", "multi_ig": "(f)"}
KIND = {"multi_random": "random", "multi_sep": "separation", "multi_ig": "infogain"}
FAULTS = ("dropout", "jump")


class DisambGate(X.HoverGate):
    """HoverGate that flies src.cmd (the disambiguating move) instead of zero while lost."""

    def __init__(self, inner, src):
        super().__init__(inner)
        self.src = src
        self.name = "disamb_gate+" + inner.name

    def step(self, pose, scan, goal, grid, dt):
        if pose.quality == 0 and self.src.cmd is not None:
            self.held = True
            return Setpoint(self.src.cmd[0], self.src.cmd[1], 0.0, 0.0)
        return super().step(pose, scan, goal, grid, dt)


def build(arm, w, est, seed, index):
    if arm in KIND:
        src = D.DisambPoseSource(est, w.grid, X.scan_fn_for(w, seed, index), KIND[arm],
                                 rng=np.random.default_rng([seed, index, 4501]), goal=w.goal)
        return src, DisambGate(astar_esdf.make(known_map=True), src)
    return X.wrap(est, w, seed, index, arm), X.planner_for(arm)


def extra(row, est, src, fault):
    out = X.row_extra(row, est, src, fault)
    if isinstance(src, D.DisambPoseSource):
        for i, ev in enumerate(out["events"]):
            ev["moves"] = src.moves.get(i, [])
        out["move_s"] = round(src.move_steps / run.DEFAULTS["plan_hz"], 2)
    return out


def run_cell(args):
    fault_name, arm, family, layouts, seed = args
    rows = []
    t0 = time.perf_counter()
    for i in range(layouts):
        w = world.make_world(family, seed, i)
        est = estimator.make_pose_source_factory(fault_name, dark=True, sink=[])(w, seed, i)
        src, planner = build(arm, w, est, seed, i)
        row, _, _ = run.run_one(planner, w, seed, i, run.DEFAULTS, src)
        row.update(extra(row, est, src, est.fault))
        rows.append(row)
    return fault_name, arm, rows, round(time.perf_counter() - t0, 1)


def run_corridor_cell(args):
    arm, runs = args
    rows = []
    t0 = time.perf_counter()
    for i in range(runs):
        w = X.corridor_world(i)
        f = X.CorridorJump(w, np.random.default_rng([0, i, 4402]))
        est = estimator.VioEstimator(np.random.default_rng([0, i, 4101]), [], f)
        src, planner = build(arm, w, est, 0, i)
        row, _, _ = run.run_one(planner, w, 0, i, run.DEFAULTS, src)
        row.update(extra(row, est, src, est.fault))
        rows.append(row)
    return "corridor_jump", arm, rows, round(time.perf_counter() - t0, 1)


def summarize(rows):
    s = X.summarize(rows)
    ev = [e for x in rows for e in x.get("events", [])]
    real = lambda e: [m for m in e.get("moves", []) if m.get("move") is not None]
    nm = [len(real(e)) for e in ev]
    with_moves = [e for e in ev if real(e)]
    acc_after = [e for e in with_moves if e["result"] == "accepted"]
    rec_after = [e["recover_s"] for e in acc_after]
    s.update({
        "moves_total": int(sum(nm)),
        "events_with_moves": len(with_moves),
        "events_with_moves_accepted": len(acc_after),
        "events_with_moves_wrong": sum(1 for e in acc_after if e["err_m"] > X.WRONG_M),
        "events_with_moves_open": sum(1 for e in with_moves if e["result"] == "open"),
        "runs_with_moves": sum(1 for x in rows if any(real(e) for e in x.get("events", []))),
        "median_moves_per_moving_event": float(np.median([n for n in nm if n])) if any(nm) else None,
        "median_recover_s_after_move": round(float(np.median(rec_after)), 2) if rec_after else None,
        "p95_recover_s": s["p95_recover_s"],
        "max_recover_s": round(max(e["recover_s"] for e in ev if e["recover_s"] is not None), 2)
        if any(e["recover_s"] is not None for e in ev) else None,
        "move_basis": {b: sum(1 for e in ev for m in real(e) if m["basis"] == b)
                       for b in ("hypotheses", "returns", "random")},
        "no_feasible_move": sum(1 for e in ev for m in e.get("moves", []) if m.get("move") is None),
    })
    return s


HEAD = ("| fault | arm | runs | reached % | collision % | stuck % | relocs accepted | wrong commits (> 0.5 m) "
        "| still hovering at end | median / p95 / max recover s | moves flown | events with a move => accepted / wrong / open "
        "| median recover s after a move | median run max err m |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def f(v):
    return "-" if v is None else f"{v}"


def line(fault, arm, s):
    mv = arm in KIND
    return (f"| {fault} | {LABEL[arm]} {arm} | {s['n']} | {s['reached_pct']} | {s['collision_pct']} | {s['stuck_pct']} "
            f"| {s['accepted']} | {s['wrong_commits']} | {s['open_at_end']} "
            f"| {f(s['median_recover_s'])} / {f(s['p95_recover_s'])} / {f(s['max_recover_s'])} "
            f"| {s['moves_total'] if mv else '-'} "
            f"| {(str(s['events_with_moves']) + ' => ' + str(s['events_with_moves_accepted']) + ' / ' + str(s['events_with_moves_wrong']) + ' / ' + str(s['events_with_moves_open'])) if mv else '-'} "
            f"| {f(s['median_recover_s_after_move']) if mv else '-'} | {f(s['median_run_max_err_m'])} |")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--family", default="random", choices=world.FAMILIES)
    ap.add_argument("--corridor", action="store_true")
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    arms = [x for x in a.arms.split(",") if x]
    cmd = "python run_disambiguate.py " + " ".join(argv if argv is not None else sys.argv[1:])
    t0 = time.perf_counter()
    if a.corridor:
        cells = [(arm, a.runs) for arm in arms]
        fn, stem, faults_used = run_corridor_cell, "disamb_corridor", ("corridor_jump",)
    else:
        cells = [(fl, arm, a.family, a.layouts, a.seed) for fl in FAULTS for arm in arms]
        fn, stem, faults_used = run_cell, f"disamb_{a.family}_{a.seed}", FAULTS
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        out = list(ex.map(fn, cells))
    wall = time.perf_counter() - t0
    res = {}
    for fl, arm, rows, cw in out:
        res.setdefault(fl, {})[arm] = {"summary": summarize(rows), "cell_wall_s": cw, "runs": rows}
    lines = [HEAD] + [line(fl, arm, res[fl][arm]["summary"]) for fl in faults_used for arm in arms if arm in res.get(fl, {})]
    tab = "\n".join(lines)
    print(tab)
    print(f"\nwall {wall:.1f} s")
    os.makedirs(a.out, exist_ok=True)
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system()}
    params = {k: getattr(D, k) for k in ("N_DIRS", "MOVE_DISTS_M", "CLEAR_M", "HOVER_TIMEOUT_S", "MAX_MOVES",
                                          "MOVE_SPEED", "K_MOVE", "MOVE_DONE_M", "MOVE_TIMEOUT_S", "LIVE_FRAC",
                                          "SIGMA_B", "EPS", "BEAM_DECIM", "TIE_REL")}
    params.update({k: getattr(R, k) for k in ("S_MIN", "RATIO", "N_SCANS", "W0_M", "SEP_M", "K_MAX")})
    with open(os.path.join(a.out, stem + ".json"), "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "family": "corridor" if a.corridor else a.family,
                   "seed": a.seed, "wall_s": round(wall, 1), "workers": a.workers, "params": params,
                   "config": run.DEFAULTS, "env": env, "results": res}, fh, indent=1)
    with open(os.path.join(a.out, stem + ".md"), "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {wall:.1f} s, {a.workers} workers\n\n{tab}\n")
    print(f"wrote {stem}.json / .md")


if __name__ == "__main__":
    main()
