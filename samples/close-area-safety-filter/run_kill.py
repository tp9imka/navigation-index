"""Kill test: safety filters (F0-F4) on the A* planner under estimator faults.

python run_kill.py --layouts 100 --seed 0 [--arms F0,F1,F2] [--cases truth,none,jump,bias,dropout]
                   [--unsensed on,off] [--workers 8] [--tag kill_a]
python run_kill.py --calibrate --layouts 100 --seed 1      # F4's fixed bound => kill_b_eps_calib_1.*

An arm may carry a labelled parameter variant: --arms F2,F4,"F4@eps_m=0.4". The filter gets
health["belief"] = the estimator's belief() (EKF mean, covariance, noise settings), None for truth.

Per run (one layout, one arm, one fault case, unsensed on or off):
  planner   arena planners/astar_esdf.py, make(known_map=True), 10 Hz, prior grid of the layout
            (with unsensed obstacles when on)
  estimate  arena estimator.py VIO-like EKF with dark zones and the faults.py case; called every
            50 Hz physics step so the filter sees a fresh estimate. "truth" = no estimator
  sensors   two arena RangeFans (72 beams, 360 deg, 6 m, defaults) wrapped by
            unsensed.VisibleOnlyFan: the planner's at 10 Hz (rng [seed, index, 7], same as the
            arena), the filter's every FILTER_SCAN_EVERY steps = 16.7 Hz (rng [seed, index, 8])
  filter    filters.make(arm), every 50 Hz step, between planner and vehicle
  scoring   arena scorer.py on truth: reached / collision / stuck / timeout, min clearance

Writes results/<tag>_unsensed_<on|off>_<seed>.json/.md and results/<tag>_summary_<seed>.md
(tag kill_a: part a, F0-F2; kill_b: part b, F2-F4).
All inputs are synthetic.
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

import arena
import filters
import unsensed

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
FAMILY = "random"
FILTER_SCAN_EVERY = 3          # physics steps (50 Hz / 3 = 16.7 Hz, doc 05 1.5: 15 Hz in flight)
CASES = ("truth", "none", "jump", "bias", "dropout")


def parse_arm(spec: str):
    """"F4" => ("F4", {}); "F4@eps_m=0.4" => ("F4", {"eps_m": 0.4}) (a labelled parameter variant)."""
    name, _, rest = spec.partition("@")
    kw = {}
    for item in filter(None, rest.split(";")):
        k, _, v = item.partition("=")
        kw[k] = float(v)
    return name, kw


def run_one(arm: str, case: str, uns_on: bool, index: int, seed: int, cfg=None, arm_kw=None) -> dict:
    run, scorer, Vehicle = arena.run, arena.scorer, arena.vehicle.Vehicle
    cfg = cfg or run.DEFAULTS
    w0 = arena.world.make_world(FAMILY, seed, index, radius=cfg["vehicle"]["radius"])
    w, placed = unsensed.add_unsensed(w0, seed, index) if uns_on else (w0, [])
    goal = (w.goal[0], w.goal[1], cfg["z0"])
    veh = Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **cfg["vehicle"])
    sensor = unsensed.VisibleOnlyFan(w0, rng=np.random.default_rng([seed, index, 7]), **cfg["sensor"])
    fsensor = unsensed.VisibleOnlyFan(w0, rng=np.random.default_rng([seed, index, 8]), **cfg["sensor"])
    est = None
    if case != "truth":
        est = arena.estimator.make_pose_source_factory(case, dark=True)(w, seed, index)
    ad = arena.adapter.SimAdapter(w, veh, sensor, pose_source=est)
    planner = arena.astar_esdf.make(known_map=True)
    planner.reset()
    name, kw = parse_arm(arm)
    filt = filters.make(name, **{**kw, **(arm_kw or {})})
    HZ, DT = arena.vehicle.HZ, arena.vehicle.DT
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    n_steps = int(round(cfg["max_time_s"] * HZ))
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    radius = cfg["vehicle"]["radius"]
    ts, xy = [0.0], [(0.0, 0.0)]
    sp_nom, fscan = None, None
    n_int = n_f = 0
    max_err = max_serr = 0.0
    t0 = time.perf_counter()
    for k in range(n_steps):
        pose = ad.pose()
        tr = ad.truth()
        max_err = max(max_err, math.hypot(pose.x - tr.x, pose.y - tr.y))
        max_serr = max(max_serr, math.sqrt((pose.x - tr.x) ** 2 + (pose.y - tr.y) ** 2
                                           + (pose.vx - tr.vx) ** 2 + (pose.vy - tr.vy) ** 2))
        if k % ratio == 0:
            sp_nom = planner.step(pose, ad.ranges(), goal, w.grid, pdt)
        if k % FILTER_SCAN_EVERY == 0:
            fscan = fsensor.scan(w, veh.p[0], veh.p[1], veh.yaw, veh.t)
        health = {"t": pose.t, "quality": pose.quality, "reset_counter": pose.reset_counter,
                  "sigma_xy": pose.sigma_xy, "belief": est.belief() if est is not None else None}
        sp, intervened = filt.filter(sp_nom, pose, fscan, w, health, DT)
        n_f += 1
        n_int += int(intervened)
        ad.send_setpoint(sp)
        ad.tick()
        px, py = float(veh.p[0]), float(veh.p[1])
        ts.append(veh.t)
        xy.append((px, py))
        if math.hypot(px - goal[0], py - goal[1]) <= scorer.GOAL_TOL:
            break
        if w.clearance(px, py) < radius:
            break
        if len(xy) > lag and math.hypot(px - xy[-1 - lag][0], py - xy[-1 - lag][1]) < scorer.STUCK_DIST:
            break
    res = scorer.score(ts, xy, w, goal, radius)
    hit_uns = None
    if res["collision"]:
        clr = w.sdf(np.asarray(xy))
        i = int(np.flatnonzero(clr < radius)[0])
        hit_uns = bool(unsensed.unsensed_sdf(placed, *xy[i]) < w0.clearance(*xy[i]))
    res.update({
        "arm": arm, "case": case, "unsensed": uns_on, "index": index,
        "n_unsensed": len(placed), "unsensed_obstacles": [u.to_list() for u in placed],
        "hit_unsensed": hit_uns, "intervention_frac": round(n_int / max(n_f, 1), 4),
        "max_pose_error_m": round(max_err, 4),
        "max_state_error": round(max_serr, 4),       # |(dp, dv)| in m and m/s together (F4 eps calibration)
        "filter_stats": ({k: (round(v, 4) if isinstance(v, float) else v) for k, v in filt.stats.items()}
                         if hasattr(filt, "stats") else None),
        "fault_log": est.fault.log if est is not None and est.fault is not None else None,
        "wall_s": round(time.perf_counter() - t0, 3),
    })
    return res


def _task(args):
    return run_one(*args)


def summarize(rows):
    n = len(rows)
    pct = lambda key: round(100.0 * sum(bool(r[key]) for r in rows) / n, 1)
    coll = [r for r in rows if r["collision"]]
    return {
        "n": n, "collision_pct": pct("collision"), "reached_pct": pct("reached"),
        "stuck_pct": pct("stuck"), "timeout_pct": pct("timeout"),
        "collisions": len(coll), "collisions_unsensed": sum(1 for r in coll if r["hit_unsensed"]),
        "intervention_frac_mean": round(float(np.mean([r["intervention_frac"] for r in rows])), 4),
        "median_min_clearance_m": round(float(np.median([r["min_clearance_m"] for r in rows])), 3),
        "median_time_to_goal_s": (round(float(np.median([r["time_to_goal_s"] for r in rows if r["reached"]])), 2)
                                  if any(r["reached"] for r in rows) else None),
        "median_max_pose_error_m": round(float(np.median([r["max_pose_error_m"] for r in rows])), 3),
        **_diag(rows),
    }


def _diag(rows):
    """Map-barrier diagnostics for F3/F4 (filter_stats); empty for arms without stats."""
    st = [r["filter_stats"] for r in rows if r.get("filter_stats")]
    if not st:
        return {}
    steps = sum(s["steps"] for s in st)
    out = {"map_active_step_frac": round(sum(s["map_active_steps"] for s in st) / max(steps, 1), 4),
           "slack_step_frac": round(sum(s["slack_steps"] for s in st) / max(steps, 1), 4),
           "runs_with_slack": sum(1 for s in st if s["slack_steps"] > 0)}
    if "margin_n" in st[0]:
        out["mean_margin_nearest_m"] = round(sum(s["margin_sum_m"] for s in st) / max(sum(s["margin_n"] for s in st), 1), 4)
        out["max_margin_m"] = round(max(s["margin_max_m"] for s in st), 4)
        out["max_gamma_m"] = round(max(s["gamma_max_m"] for s in st), 4)
    return out


DIAG_HEAD = ("| arm | case | map row active, fraction of steps | slack used, fraction of steps | runs with slack "
             "| mean k*sigma + gamma at nearest obstacle m | max k*sigma + gamma m | max gamma m |\n"
             "|---|---|---|---|---|---|---|---|")


def diag_line(arm, case, s):
    if "slack_step_frac" not in s:
        return None
    f = lambda k: "-" if k not in s else f"{s[k]}"
    return (f"| {arm} | {case} | {s['map_active_step_frac']} | {s['slack_step_frac']} | {s['runs_with_slack']} "
            f"| {f('mean_margin_nearest_m')} | {f('max_margin_m')} | {f('max_gamma_m')} |")


HEAD = ("| arm | case | layouts | collision % | of which unsensed | reached % | stuck % | timeout % "
        "| intervention fraction | median min clearance m | median time to goal s | median max pose err m |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(arm, case, s):
    f = lambda v: "-" if v is None else f"{v}"
    return (f"| {arm} | {case} | {s['n']} | {s['collision_pct']} | {s['collisions_unsensed']} of {s['collisions']} "
            f"| {s['reached_pct']} | {s['stuck_pct']} | {s['timeout_pct']} | {s['intervention_frac_mean']} "
            f"| {s['median_min_clearance_m']} | {f(s['median_time_to_goal_s'])} | {s['median_max_pose_error_m']} |")


def calibrate(layouts: int, seed: int, workers: int, out: str, cmd: str) -> int:
    """F4's fixed bound, Cosner practice: the worst state error |(dp, dv)| seen against truth in
    normal operation (case "none": dark zones, no injected fault), arm F2, unsensed off, on a
    seed the kill test does not use. Writes results/kill_b_eps_calib_<seed>.json/.md."""
    tasks = [("F2", "none", False, i, seed) for i in range(layouts)]
    t0 = time.perf_counter()
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            rows = list(ex.map(_task, tasks, chunksize=4))
    else:
        rows = [_task(t) for t in tasks]
    wall = time.perf_counter() - t0
    se = np.array([r["max_state_error"] for r in rows])
    pe = np.array([r["max_pose_error_m"] for r in rows])
    q = lambda a, x: round(float(np.quantile(a, x)), 4)
    stats = {"eps_m": round(float(se.max()), 4), "state_err_median": q(se, 0.5), "state_err_p95": q(se, 0.95),
             "state_err_max": round(float(se.max()), 4), "pos_err_median": q(pe, 0.5),
             "pos_err_p95": q(pe, 0.95), "pos_err_max": round(float(pe.max()), 4)}
    os.makedirs(out, exist_ok=True)
    stem = os.path.join(out, f"kill_b_eps_calib_{seed}")
    with open(stem + ".json", "w") as fh:
        json.dump({"command": cmd, "input": "synthetic", "family": FAMILY, "seed": seed, "layouts": layouts,
                   "arm": "F2", "case": "none", "unsensed": False, "stats": stats, "wall_s": round(wall, 1),
                   "per_run": [{"index": r["index"], "max_state_error": r["max_state_error"],
                                "max_pose_error_m": r["max_pose_error_m"], "outcome": r["outcome"]}
                               for r in rows]}, fh, indent=1)
    md = (f"`{cmd}` (synthetic), wall {wall:.1f} s\n\nF4 bound calibration: per-run maximum of the estimate's "
          f"state error |(dp, dv)| against truth, arm F2, case none (dark zones, no injected fault), unsensed "
          f"off, {layouts} layouts, seed {seed}.\n\n| statistic over runs | state error (m, m/s) | position "
          f"error m |\n|---|---|---|\n| median | {stats['state_err_median']} | {stats['pos_err_median']} |\n"
          f"| 95th percentile | {stats['state_err_p95']} | {stats['pos_err_p95']} |\n"
          f"| max (=> F4 eps_m) | {stats['state_err_max']} | {stats['pos_err_max']} |\n")
    with open(stem + ".md", "w") as fh:
        fh.write(md)
    print(md)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calibrate", action="store_true",
                    help="measure F4's fixed error bound instead (use --seed 1, not the test seed)")
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--arms", default="F0,F1,F2")
    ap.add_argument("--cases", default=",".join(CASES))
    ap.add_argument("--unsensed", default="on,off")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--out", default=RESULTS)
    ap.add_argument("--tag", default="kill_a")
    a = ap.parse_args(argv)
    arms = [x for x in a.arms.split(",") if x]
    cases = [x for x in a.cases.split(",") if x]
    uns = [x == "on" for x in a.unsensed.split(",") if x]
    cmd = "python run_kill.py " + " ".join(argv if argv is not None else sys.argv[1:])
    if a.calibrate:
        return calibrate(a.layouts, a.seed, a.workers, a.out, cmd)
    tasks = [(arm, c, u, i, a.seed) for u in uns for arm in arms for c in cases for i in range(a.layouts)]
    t0 = time.perf_counter()
    if a.workers > 1:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            rows = list(ex.map(_task, tasks, chunksize=4))
    else:
        rows = [_task(t) for t in tasks]
    wall = time.perf_counter() - t0
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system(), "workers": a.workers}
    os.makedirs(a.out, exist_ok=True)
    summary_md = [f"`{cmd}` (synthetic), wall {wall:.1f} s, {len(tasks)} runs, {a.workers} workers\n"]
    for u in uns:
        tag = "on" if u else "off"
        sub = [r for r in rows if r["unsensed"] == u]
        table, summ, dtab = [HEAD], {}, [DIAG_HEAD]
        for arm in arms:
            for c in cases:
                rr = [r for r in sub if r["arm"] == arm and r["case"] == c]
                s = summarize(rr)
                summ[f"{arm}/{c}"] = s
                table.append(line(arm, c, s))
                dl = diag_line(arm, c, s)
                if dl:
                    dtab.append(dl)
        if len(dtab) > 1:
            table += ["", "Map-barrier diagnostics (F3, F4):", "", *dtab]
        stem = os.path.join(a.out, f"{a.tag}_unsensed_{tag}_{a.seed}")
        params = {arm: filters.make(parse_arm(arm)[0], **parse_arm(arm)[1]).p for arm in arms}
        with open(stem + ".json", "w") as fh:
            json.dump({"command": cmd, "input": "synthetic", "family": FAMILY, "seed": a.seed,
                       "layouts": a.layouts, "unsensed": u, "planner": "astar_esdf known_map=True",
                       "filter_scan_every_steps": FILTER_SCAN_EVERY, "arena_config": arena.run.DEFAULTS,
                       "unsensed_config": {"n": unsensed.N_PER_LAYOUT, "path_frac": unsensed.PATH_FRAC,
                                           "lateral_m": unsensed.LATERAL_M, "pole_r": unsensed.POLE_R,
                                           "glass_len": unsensed.GLASS_LEN, "p_glass": unsensed.P_GLASS},
                       "filter_params": params, "summary": summ, "wall_s": round(wall, 1), "env": env,
                       "runs": sub}, fh, indent=1)
        n_placed = [r["n_unsensed"] for r in sub if r["arm"] == arms[0] and r["case"] == cases[0]]
        note = (f"Unsensed obstacles placed: {sum(n_placed)} in {len(n_placed)} layouts "
                f"(per layout min {min(n_placed)}, max {max(n_placed)}).\n" if u else "")
        md = f"`{cmd}` (synthetic), unsensed {tag}, wall {wall:.1f} s for the whole command\n\n{note}\n" + "\n".join(table) + "\n"
        with open(stem + ".md", "w") as fh:
            fh.write(md)
        summary_md.append(f"\n## Unsensed obstacles {tag}\n\n{note}\n" + "\n".join(table) + "\n")
        print(md, flush=True)
    with open(os.path.join(a.out, f"{a.tag}_summary_{a.seed}.md"), "w") as fh:
        fh.write("".join(summary_md))
    print(f"wall {wall:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
