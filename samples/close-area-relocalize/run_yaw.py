"""Yaw bias after the jump fault: (f) multi_ig without yaw search vs (f) with a +-15 deg yaw search.

.venv/bin/python run_yaw.py --layouts 100 --seed 2            # random family, biases 0 / 5 / 10 deg
.venv/bin/python run_yaw.py --corridor --runs 20              # corridor, biases 10 / 180 deg + twin check

Fault model (sim side, YawBias): from the planner step where the arena jump fault fires (0.5 m VIO
step, reset_counter + 1), the estimate is rotated by the bias about the pose at that step: later
position and velocity deltas are rotated by the bias and the reported yaw is truth + bias. The
sign is seeded per run (rng [seed, index, 4601]); 180 deg has no sign.

Vehicle model (RotExec, both arms): the flight controller turns the map-frame velocity setpoint
into thrust with its own yaw estimate, so the vehicle moves along the setpoint rotated by
(true yaw - reported yaw). Without it a yaw error would only bend the estimate, not the flight.

Arms (A* known map behind disambiguate.DisambGate, scored on truth by the arena):
  f_noyaw   (f) disambiguate.DisambPoseSource "infogain", unchanged: xy search at the estimator yaw
  f_yaw     (f) + relocalize_yaw.YawDisambPoseSource: 3-DoF search, +-15 deg in 2.5 deg steps,
            refined at 0.25 deg; the accepted dyaw corrects the heading
  f_yaw_hf  f_yaw + heading_first: apply the heading once all live hypotheses agree on it for
            3 scans, before the xy verdict (added after the first corridor run: f_yaw collided
            during disambiguating moves flown with the uncorrected heading)
Corridor mode also runs a static twin check: at 20 poses near the corridor middle (area x 9.5-10.5),
score of the true pose vs its 180 deg twin (mirror about the corridor centre, yaw + 180), and the
top hypotheses of a full-circle (+-180 deg) search.
Writes results/yaw_<family>_<seed>.json / .md or results/yaw_corridor.json / .md.
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
from dataclasses import replace

import numpy as np
import scipy

from arena import Planner, Setpoint, astar_esdf, estimator, run, sensors, world
import disambiguate as D
import experiment as X
import relocalize as R
import relocalize_yaw as Y
import run_disambiguate as RD

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
ARMS = ("f_noyaw", "f_yaw", "f_yaw_hf")
LABEL = {"f_noyaw": "(f) no yaw search", "f_yaw": "(f) + yaw search +-15 deg",
         "f_yaw_hf": "(f) + yaw search + heading first"}


class YawBias:
    """Wraps the VioEstimator. Rotates the estimate by bias_deg from the step the fault fires."""

    def __init__(self, est, bias_deg: float):
        self.est, self.fault = est, est.fault
        self.b = math.radians(bias_deg)
        self.on, self.prev, self.out = False, None, None
        self.truth_yaw = 0.0
        self.fired_t = None

    def __call__(self, truth):
        raw = self.est(truth)
        self.truth_yaw = truth.yaw
        p = np.array([raw.x, raw.y])
        if not self.on and self.fault.log.get("fired_t") is not None:
            self.on, self.out, self.fired_t = True, p.copy(), truth.t
        elif self.on:
            self.out = self.out + Y.rot(self.b) @ (p - self.prev)
        self.prev = p
        if not self.on:
            return raw
        v = Y.rot(self.b) @ np.array([raw.vx, raw.vy])
        return replace(raw, x=float(self.out[0]), y=float(self.out[1]), vx=float(v[0]), vy=float(v[1]),
                       yaw=Y.wrap_pi(truth.yaw + self.b))


class RotExec(Planner):
    """Vehicle side: the setpoint is flown rotated by (true yaw - reported yaw). Logs the yaw error."""

    def __init__(self, inner, bias_src):
        self.inner, self.bs = inner, bias_src
        self.uses_grid = inner.uses_grid
        self.name = "rot_exec+" + inner.name
        self.yaw_errs: list[float] = []

    def reset(self):
        self.inner.reset()
        self.yaw_errs = []

    def step(self, pose, scan, goal, grid, dt):
        sp = self.inner.step(pose, scan, goal, grid, dt)
        d = Y.wrap_pi(self.bs.truth_yaw - pose.yaw)
        self.yaw_errs.append(abs(math.degrees(d)))
        if d == 0.0:
            return sp
        c, s = math.cos(d), math.sin(d)
        return Setpoint(c * sp.vx - s * sp.vy, s * sp.vx + c * sp.vy, sp.vz, sp.yaw_rate)


def build(arm, w, est, seed, index):
    rng = np.random.default_rng([seed, index, 4501])
    scan_fn = X.scan_fn_for(w, seed, index)
    if arm == "f_noyaw":
        src = D.DisambPoseSource(est, w.grid, scan_fn, "infogain", rng=rng, goal=w.goal)
    else:
        src = Y.YawDisambPoseSource(est, w.grid, scan_fn, "infogain", rng=rng, goal=w.goal,
                                    heading_first=arm == "f_yaw_hf")
    return src, RD.DisambGate(astar_esdf.make(known_map=True), src)


def fly(arm, w, est, bias_deg, seed, index):
    yb = YawBias(est, bias_deg)
    src, gate = build(arm, w, yb, seed, index)
    planner = RotExec(gate, yb)
    row, _, _ = run.run_one(planner, w, seed, index, run.DEFAULTS, src)
    row.update(RD.extra(row, est, src, est.fault))
    fixes = getattr(src, "yaw_fixes", {})
    early = getattr(src, "heading_fixes", {})
    for i, ev in enumerate(row["events"]):
        ev["yaw_fix"] = fixes.get(i)
        ev["heading_fixes"] = early.get(i, [])
    jump = None
    if yb.fired_t is not None:
        jump = next((i for i, ev in enumerate(row["events"]) if ev["reason"] == "reset_counter"
                     and ev["t_trigger"] >= yb.fired_t - 1e-6), None)
    row.update({"bias_deg": round(math.degrees(yb.b), 3), "yaw_fault_t": yb.fired_t, "jump_event": jump,
                "yaw_err_end_deg": round(planner.yaw_errs[-1], 3) if planner.yaw_errs else None,
                "match_ms_all": [round(v, 3) for v in src.match_ms]})
    return row


def bias_for(bias, seed, index):
    if bias in (0, 180):
        return float(bias)
    return float(bias) * (1.0 if np.random.default_rng([seed, index, 4601]).random() < 0.5 else -1.0)


def run_chunk(args):
    arm, bias, family, seed, lo, hi = args
    rows = []
    t0 = time.perf_counter()
    for i in range(lo, hi):
        w = world.make_world(family, seed, i)
        est = estimator.make_pose_source_factory("jump", dark=True, sink=[])(w, seed, i)
        rows.append(fly(arm, w, est, bias_for(bias, seed, i), seed, i))
    return arm, bias, lo, rows, time.perf_counter() - t0


def run_corridor_chunk(args):
    arm, bias, _, _, lo, hi = args
    rows = []
    t0 = time.perf_counter()
    for i in range(lo, hi):
        w = X.corridor_world(i)
        f = X.CorridorJump(w, np.random.default_rng([0, i, 4402]))
        est = estimator.VioEstimator(np.random.default_rng([0, i, 4101]), [], f)
        rows.append(fly(arm, w, est, bias_for(bias, 0, i), 0, i))
    return arm, bias, lo, rows, time.perf_counter() - t0


# ---- static 180 deg twin check (corridor) ----
def twin_check(n=20):
    out = []
    for i in range(n):
        w = X.corridor_world(i)
        full = Y.YawScanMatcher(w.grid, half_deg=180.0)
        ax, ay = w.area_origin
        rng = np.random.default_rng([0, i, 4602])
        x, y = 10.0 + rng.uniform(-0.5, 0.5) - ax, 10.0 + rng.uniform(-0.3, 0.3) - ay
        yaw = math.atan2(w.goal[1], w.goal[0])
        tx, ty = 20.0 - 2 * ax - x, 20.0 - 2 * ay - y              # mirror about area (10, 10)
        fan = sensors.RangeFan(rng=np.random.default_rng([0, i, 4603]), **run.DEFAULTS["sensor"])
        sc = fan.scan(w, x, y, yaw, 0.0)
        s_true = full.score_at(sc, yaw, (x, y))
        s_twin = full.score_at(sc, yaw + math.pi, (tx, ty))
        t0 = time.perf_counter()
        hy = full.hypotheses(sc, yaw, (x, y))
        ms = (time.perf_counter() - t0) * 1e3
        local = Y.YawScanMatcher(w.grid)                    # +-15 deg, as flown
        ht = local.hypotheses(sc, yaw, (x, y))
        hf = local.hypotheses(sc, yaw + math.pi, (x, y))   # what a 180 deg-off heading would give

        def kind(h):
            if abs(math.degrees(Y.wrap_pi(h.dyaw))) <= 5.0:
                return "true_heading"
            if abs(math.degrees(Y.wrap_pi(h.dyaw - math.pi))) <= 5.0:
                return "flipped_heading"
            return "other"
        out.append({"index": i, "truth": [round(x, 3), round(y, 3)], "twin": [round(tx, 3), round(ty, 3)],
                    "score_true": round(s_true, 4), "score_twin": round(s_twin, 4),
                    "ratio_true_over_twin": round(s_true / s_twin, 4),
                    "best_true_heading": round(ht[0].score, 4), "best_flipped_heading": round(hf[0].score, 4),
                    "ratio_best_true_over_best_flipped": round(ht[0].score / hf[0].score, 4),
                    "flipped_best_err_twin_m": round(math.hypot(hf[0].x - tx, hf[0].y - ty), 3),
                    "flipped_best_err_true_m": round(math.hypot(hf[0].x - x, hf[0].y - y), 3),
                    "full_circle_top": [{"x": round(h.x, 3), "y": round(h.y, 3), "dyaw_deg": round(math.degrees(h.dyaw), 2),
                                         "score": round(h.score, 4), "kind": kind(h),
                                         "err_true_m": round(math.hypot(h.x - x, h.y - y), 3),
                                         "err_twin_m": round(math.hypot(h.x - tx, h.y - ty), 3)} for h in hy],
                    "full_circle_ms": round(ms, 2)})
    r = [o["ratio_true_over_twin"] for o in out]
    first = [o["full_circle_top"][0]["kind"] for o in out if o["full_circle_top"]]
    flip_in_set = sum(1 for o in out if any(h["kind"] == "flipped_heading" for h in o["full_circle_top"]))
    return {"poses": out, "ratio_min": min(r), "ratio_median": round(float(np.median(r)), 4), "ratio_max": max(r),
            "poses_ratio_below_rule": sum(1 for v in r if v < R.RATIO),
            "best_is_flipped": first.count("flipped_heading"), "best_is_true": first.count("true_heading"),
            "flipped_in_top5": flip_in_set,
            "best_ratio_true_over_flipped_median": round(float(np.median([o["ratio_best_true_over_best_flipped"] for o in out])), 4),
            "best_ratio_min": min(o["ratio_best_true_over_best_flipped"] for o in out),
            "best_ratio_max": max(o["ratio_best_true_over_best_flipped"] for o in out),
            "flipped_best_score_median": round(float(np.median([o["best_flipped_heading"] for o in out])), 4),
            "flipped_best_score_min": min(o["best_flipped_heading"] for o in out),
            "full_circle_ms_median": round(float(np.median([o["full_circle_ms"] for o in out])), 1)}


# ---- summaries ----
def summarize(rows):
    s = RD.summarize(rows)
    fired = [x for x in rows if x["yaw_fault_t"] is not None]
    jev = [x["events"][x["jump_event"]] for x in fired if x["jump_event"] is not None]
    jrec = [e["recover_s"] for e in jev if e["result"] == "accepted"]
    allms = [v for x in rows for v in x["match_ms_all"]]
    per_run = [x["match_ms_median"] for x in rows if x.get("match_ms_median") is not None]
    yend = [x["yaw_err_end_deg"] for x in fired if x["yaw_err_end_deg"] is not None]
    fixes = [e["yaw_fix"]["yaw_err_after_deg"] for x in rows for e in x["events"] if e.get("yaw_fix")]
    s.update({
        "yaw_fault_runs": len(fired),
        "reached_of_fired": sum(1 for x in fired if x["reached"]),
        "jump_events": len(jev),
        "jump_accepted": len(jrec),
        "jump_wrong": sum(1 for e in jev if e["result"] == "accepted" and e["err_m"] > X.WRONG_M),
        "jump_open": sum(1 for e in jev if e["result"] == "open"),
        "jump_recover_median_s": round(float(np.median(jrec)), 2) if jrec else None,
        "jump_recover_p95_s": round(float(np.percentile(jrec, 95)), 2) if jrec else None,
        "match_scans": len(allms),
        "match_ms_median_all": round(float(np.median(allms)), 2) if allms else None,
        "match_ms_p95_all": round(float(np.percentile(allms, 95)), 2) if allms else None,
        "match_ms_median_of_run_medians": round(float(np.median(per_run)), 2) if per_run else None,
        "yaw_err_end_deg_median": round(float(np.median(yend)), 2) if yend else None,
        "yaw_err_end_deg_max": round(float(np.max(yend)), 2) if yend else None,
        "yaw_err_after_accept_deg_median_abs": round(float(np.median(np.abs(fixes))), 2) if fixes else None,
        "yaw_err_after_accept_deg_p95_abs": round(float(np.percentile(np.abs(fixes), 95)), 2) if fixes else None,
    })
    return s


def f(v):
    return "-" if v is None else f"{v}"


HEAD = ("| case | bias deg | arm | runs | yaw fault fired | reached % | collision % | stuck % | wrong commits (> 0.5 m), all events "
        "| jump event => accepted / wrong / open | jump event recover s median / p95 | all events recover s median / p95 "
        "| still hovering at end | yaw err at end deg median / max | ms per matched scan median / p95 (scans) | median run max err m |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def line(case, bias, arm, s):
    return (f"| {case} | {bias} | {LABEL[arm]} | {s['n']} | {s['yaw_fault_runs']} | {s['reached_pct']} | {s['collision_pct']} "
            f"| {s['stuck_pct']} | {s['wrong_commits']} "
            f"| {s['jump_events']} => {s['jump_accepted']} / {s['jump_wrong']} / {s['jump_open']} "
            f"| {f(s['jump_recover_median_s'])} / {f(s['jump_recover_p95_s'])} "
            f"| {f(s['median_recover_s'])} / {f(s['p95_recover_s'])} | {s['open_at_end']} "
            f"| {f(s['yaw_err_end_deg_median'])} / {f(s['yaw_err_end_deg_max'])} "
            f"| {f(s['match_ms_median_all'])} / {f(s['match_ms_p95_all'])} ({s['match_scans']}) "
            f"| {f(s['median_run_max_err_m'])} |")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=100)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--family", default="random", choices=world.FAMILIES)
    ap.add_argument("--biases", default=None, help="comma list, deg (default 0,5,10; corridor 10,180)")
    ap.add_argument("--corridor", action="store_true")
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--chunk", type=int, default=10)
    ap.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)
    biases = [int(b) for b in (a.biases or ("10,180" if a.corridor else "0,5,10")).split(",")]
    cmd = "python run_yaw.py " + " ".join(argv if argv is not None else sys.argv[1:])
    n = a.runs if a.corridor else a.layouts
    fn = run_corridor_chunk if a.corridor else run_chunk
    case = "corridor_jump" if a.corridor else "jump"
    stem = "yaw_corridor" if a.corridor else f"yaw_{a.family}_{a.seed}"
    cells = [(arm, b, a.family, a.seed, lo, min(n, lo + a.chunk)) for b in biases for arm in ARMS
             for lo in range(0, n, a.chunk)]
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        out = list(ex.map(fn, cells))
    twin = twin_check(a.runs) if a.corridor else None
    wall = time.perf_counter() - t0
    acc: dict = {}
    for arm, b, lo, rows, cw in sorted(out, key=lambda o: (o[1], o[0], o[2])):
        cell = acc.setdefault(str(b), {}).setdefault(arm, {"runs": [], "cpu_s": 0.0})
        cell["runs"].extend(rows)
        cell["cpu_s"] = round(cell["cpu_s"] + cw, 1)
    lines = [HEAD]
    for b in biases:
        for arm in ARMS:
            c = acc[str(b)][arm]
            c["summary"] = summarize(c["runs"])
            lines.append(line(case, b if b in (0, 180) else f"+-{b}", arm, c["summary"]))
    tab = "\n".join(lines)
    print(tab)
    if twin:
        tw = {k: v for k, v in twin.items() if k != "poses"}
        print("\ntwin check:", json.dumps(tw))
    print(f"\nwall {wall:.1f} s")
    os.makedirs(a.out, exist_ok=True)
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system()}
    params = {k: getattr(Y, k) for k in ("YAW_HALF_DEG", "YAW_STEP_DEG", "YAW_FINE_STEP_DEG")}
    params.update({k: getattr(R, k) for k in ("S_MIN", "RATIO", "N_SCANS", "W0_M", "SEP_M", "K_MAX", "S_INNOV")})
    params.update({k: getattr(D, k) for k in ("HOVER_TIMEOUT_S", "MAX_MOVES")})
    with open(os.path.join(a.out, stem + ".json"), "w") as fh:
        json.dump({"input": "synthetic", "command": cmd, "family": "corridor" if a.corridor else a.family,
                   "seed": 0 if a.corridor else a.seed, "biases_deg": biases, "wall_s": round(wall, 1),
                   "workers": a.workers, "params": params, "config": run.DEFAULTS, "env": env,
                   "twin_check": twin, "results": acc}, fh, indent=1)
    with open(os.path.join(a.out, stem + ".md"), "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {wall:.1f} s, {a.workers} workers\n\n{tab}\n")
        if twin:
            fh.write("\nStatic 180 deg twin check, " + str(len(twin["poses"])) + " poses near the corridor middle: "
                     + json.dumps({k: v for k, v in twin.items() if k != "poses"}) + "\n")
    print(f"wrote {stem}.json / .md")


if __name__ == "__main__":
    main()
