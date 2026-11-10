"""Moving people with prediction: arms (d) space-time A* and (e) VO gate vs the existing three.

python run_predict.py --layouts 50 --seeds 0,1 [--speeds 0.5,1.0] [--arms astar,astar_f2,apf,st_astar,astar_vo]
                      [--workers 14] [--replay-seed 1 --replay-speed 1.0]

Arms
  astar     run_moving.run_one("astar")     A* replan, prior + latest scan (existing, unchanged)
  astar_f2  run_moving.run_one("astar_f2")  the same + F2 PX4-CBF range filter (existing)
  apf       run_moving.run_one("apf")       APF with escape (existing)
  st_astar  planners_st.SpaceTimeAStar      predict.py tracks, space-time A*, 0.2 s x 8 s, 5 Hz
  astar_vo  vo.VOGate                       astar + velocity-obstacle gate on predict.py tracks
The new arms reuse run_moving.run_one, the exact harness of the existing arms (layouts, movers,
sensors, 50 Hz physics, truth scoring, warning time): run_one builds its "astar" arm with
astar_replan.make(), and this script points that name at the new planner for the duration of one
call (run_moving's module global is swapped and restored; no file is edited). With no filter,
the "astar" path of run_one is just "planner.step at 10 Hz on the prior grid", which is all a
new arm needs.

Seed 0 is the tuning seed (the predictor and planner constants were set by looking at seed 0
only). Seed 1 is held out. Verdict rule, fixed before the seed-1 run: an arm gains over
A* + F2 when, on seed 1 pooled over both speeds (100 paired runs), it has no more collisions
than astar_f2 and reaches B in more runs, with an exact two-sided sign test on the layouts where
exactly one of the two reached giving p < 0.05. Otherwise FAIL.

All inputs are synthetic. The sim people walk straight segments at constant speed (instant
U-turn at the ends): exactly the constant-velocity model, so this favours the predictor.

Writes results/predict_<seeds>.json, results/predict_<seeds>.md, and one replay
results/predict_replay_<arm>_s<seed>_v<speed>_i<index>.json per replayed arm (astar, st_astar,
astar_vo on one layout: the first held-out layout at 1.0 m/s where astar collides and both new
arms reach B).
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
import astar_replan
import moving
import planners_st
import predict
import run_moving
import vo

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
EXISTING = ("astar", "astar_f2", "apf")
NEW = {"st_astar": planners_st.make, "astar_vo": vo.make}
ARMS = EXISTING + tuple(NEW)
LABELS = dict(run_moving.LABELS, st_astar="space-time A* over constant-velocity predicted footprints "
              "(0.2 s x 8 s, 5 Hz replan)", astar_vo="A* replan + velocity-obstacle gate on tracked people")
Z = 1.959964                       # 95 % two-sided normal quantile


class Recorder(arena.Planner):
    """Delegates to a planner and keeps the pose it was given at every planner step."""

    def __init__(self, inner):
        self.inner, self.rows = inner, []
        self.name, self.uses_grid = inner.name, getattr(inner, "uses_grid", True)

    def reset(self):
        self.inner.reset()
        self.rows = []

    @property
    def replan_t(self):
        return getattr(self.inner, "replan_t", None)

    def step(self, pose, scan, goal, grid, dt):
        self.rows.append([round(pose.t, 2), round(pose.x, 3), round(pose.y, 3)])
        return self.inner.step(pose, scan, goal, grid, dt)


class _Shim:
    """Stands in for the astar_replan module inside run_moving for one run_one call."""

    def __init__(self, factory):
        self.factory, self.made = factory, None

    def make(self, **kw):
        self.made = self.factory()
        return self.made


def fly(arm, speed, index, seed, record=False):
    """One run through run_moving.run_one. Returns (row, planner or None)."""
    if arm in EXISTING and not record:
        return run_moving.run_one(arm, speed, index, seed), None
    if arm == "apf":
        raise ValueError("replay of apf is not wired")
    base = "astar_f2" if arm == "astar_f2" else "astar"
    fac = NEW.get(arm, astar_replan.make)
    shim = _Shim((lambda: Recorder(fac())) if record else fac)
    orig = run_moving.astar_replan
    run_moving.astar_replan = shim
    try:
        row = run_moving.run_one(base, speed, index, seed)
    finally:
        run_moving.astar_replan = orig
    row["arm"] = arm
    return row, shim.made


def predictor_errors(tracker, movers, speed, taus=(0.0, 1.0, 3.0), every_s=0.5, assoc_m=0.5):
    """Errors of confirmed-track predictions against the true mover centres (truth used only here).
    Returns {tau: [errors m]}, plus speed errors."""
    out = {f"err_{tau:g}s": [] for tau in taus}
    out["speed_err"] = []
    if not movers:
        return out
    for t, tid, x, y, vx, vy in tracker.log:
        if abs(t / every_s - round(t / every_s)) > 1e-6:
            continue
        truth = np.array([m.at(t, speed) for m in movers])
        d = np.hypot(truth[:, 0] - x, truth[:, 1] - y)
        j = int(np.argmin(d))
        if d[j] > assoc_m:
            continue
        m = movers[j]
        for tau in taus:
            px, py = x + vx * min(tau, predict.HORIZON_S), y + vy * min(tau, predict.HORIZON_S)
            tx, ty = m.at(t + tau, speed)
            out[f"err_{tau:g}s"].append(round(math.hypot(px - tx, py - ty), 3))
        out["speed_err"].append(round(math.hypot(vx, vy) - speed, 3))
    return out


def _task(args):
    arm, speed, index, seed = args
    row, planner = fly(arm, speed, index, seed)
    if arm in NEW:
        pl = planner
        row["planner_stats"] = {k: getattr(pl, k) for k in ("n_capped", "n_relaxed", "n_escape", "n_gated", "n_no_free")
                                if hasattr(pl, k)}
        ms = getattr(pl, "replan_ms", None) or getattr(getattr(pl, "inner", None), "replan_ms", None)
        row["plan_ms"] = [round(float(np.median(ms)), 2), round(float(np.max(ms)), 2)] if ms else None
        w0 = arena.world.make_world(run_moving.FAMILY, seed, index, radius=arena.run.DEFAULTS["vehicle"]["radius"])
        movers, _ = moving.draw_movers(w0, seed, index)
        row["pred"] = predictor_errors(pl.tracker, movers, speed)
    return row


# ---- statistics ----
def wilson(k, n):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return (round(100 * max(0.0, c - h), 1), round(100 * min(1.0, c + h), 1))


def sign_test(a_only, b_only):
    """Exact two-sided binomial test p for a_only vs b_only discordant pairs."""
    n = a_only + b_only
    if n == 0:
        return 1.0
    k = min(a_only, b_only)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return float(f"{min(1.0, 2 * p):.3g}")


def _q(v, q):
    return round(float(np.percentile(v, q)), 2) if v else None


def summarize(rows):
    n = len(rows)
    s = {"n": n}
    for key in ("reached", "collision", "stuck", "timeout"):
        k = sum(bool(r[key]) for r in rows)
        s[key] = k
        s[key + "_pct"] = round(100 * k / n, 1) if n else None
        s[key + "_pct_ci"] = wilson(k, n)
    tb = [r["time_to_goal_s"] for r in rows if r["reached"]]
    wn = [r["warning_s"] for r in rows if r["collision"] and r["warning_s"] is not None]
    mm = [r["min_mover_clearance_m"] for r in rows if r["min_mover_clearance_m"] is not None]
    s.update({"time_to_b_median_s": _q(tb, 50), "time_to_b_p25_s": _q(tb, 25), "time_to_b_p75_s": _q(tb, 75),
              "warning_n": len(wn), "warning_median_s": _q(wn, 50), "warning_min_s": _q(wn, 0),
              "warning_max_s": _q(wn, 100),
              "coll_mover": sum(r["hit"] == "mover" for r in rows if r["collision"]),
              "median_min_mover_clearance_m": _q(mm, 50)})
    pe = [r["pred"] for r in rows if r.get("pred")]
    if pe:
        s["pred"] = {k: {"n": len(v), "median": _q(v, 50), "p90": _q(v, 90)}
                     for k in pe[0] for v in [[x for p in pe for x in p[k]]]}
        s["pred"]["speed_err"]["median_abs"] = _q([abs(x) for p in pe for x in p["speed_err"]], 50)
    ms = [r["plan_ms"] for r in rows if r.get("plan_ms")]
    if ms:
        s["plan_ms_median_of_medians"] = _q([m[0] for m in ms], 50)
        s["plan_ms_max"] = round(max(m[1] for m in ms), 1)
    st = [r["planner_stats"] for r in rows if r.get("planner_stats")]
    if st:
        s["planner_stats_total"] = {k: sum(x.get(k, 0) for x in st) for k in st[0]}
    return s


def paired(rows, arm, ref, seed, speeds):
    by = {(r["arm"], r["seed"], r["speed_mps"], r["index"]): r for r in rows}
    a_only = b_only = ca = cb = 0
    for (a, sd, sp, i), r in by.items():
        if a != arm or sd != seed or sp not in speeds:
            continue
        q = by[(ref, sd, sp, i)]
        a_only += int(r["reached"] and not q["reached"])
        b_only += int(q["reached"] and not r["reached"])
        ca += int(r["collision"])
        cb += int(q["collision"])
    p = sign_test(a_only, b_only)
    gain = ca <= cb and a_only > b_only and p < 0.05
    return {"arm_only_reached": a_only, "ref_only_reached": b_only, "sign_test_p": p,
            "collisions_arm": ca, "collisions_ref": cb, "verdict": "PASS" if gain else "FAIL"}


# ---- replay ----
def replay(arm, speed, index, seed, out_dir):
    row, rec = fly(arm, speed, index, seed, record=True)
    w0 = arena.world.make_world(run_moving.FAMILY, seed, index, radius=arena.run.DEFAULTS["vehicle"]["radius"])
    movers, _ = moving.draw_movers(w0, seed, index)
    wd = w0.to_dict()
    ts = [r[0] for r in rec.rows]
    tracks = getattr(rec.inner, "tracker", None)
    doc = {
        "name": f"moving_predict_{arm}_s{seed}_v{speed:g}_i{index}", "input": "synthetic",
        "title": f"Walking people at {speed:g} m/s: {arm}",
        "note": "Arena random layout with 1-3 simulated people on straight segments (constant speed, "
                "instant U-turn). Path at the 10 Hz planner rate, truth pose. People positions are truth. "
                "pred = confirmed constant-velocity tracks the planner used (none for astar).",
        "planner": arm, "family": run_moving.FAMILY, "seed": seed, "index": index, "mover_speed_mps": speed,
        "command": f"python run_predict.py --replay-seed {seed} --replay-speed {speed:g} --replay-index {index}",
        "area": wd["area"], "a": [0.0, 0.0], "b": [round(v, 3) for v in wd["goal"]],
        "boxes": [[round(v, 3) for v in b] for b in wd["boxes"]],
        "cylinders": [[round(v, 3) for v in c] for c in wd["cylinders"]],
        "radius": arena.run.DEFAULTS["vehicle"]["radius"], "goal_tol_m": arena.scorer.GOAL_TOL, "hz": 10,
        "t": ts, "truth": [[r[1], r[2]] for r in rec.rows],
        "person_radius": moving.PERSON_R,
        "people": [[[round(v, 3) for v in m.at(t, speed)] for m in movers] for t in ts],
        "pred": tracks.log if tracks is not None else None,
        "pred_fields": ["t", "track_id", "x", "y", "vx", "vy"],
        "score": {k: row[k] for k in ("outcome", "time_to_goal_s", "min_clearance_m", "min_mover_clearance_m",
                                       "path_length_m", "duration_s", "hit", "t_collision_s", "warning_s")},
    }
    path = os.path.join(out_dir, f"predict_replay_{arm}_s{seed}_v{speed:g}_i{index}.json")
    with open(path, "w") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    return path, row["outcome"], os.path.getsize(path)


def table(summ, arms, seeds, speeds):
    f = lambda v: "-" if v is None else f"{v}"
    ci = lambda s, k: f"{s[k]} ({s[k + '_ci'][0]}-{s[k + '_ci'][1]})"   # k = "<event>_pct"
    out = ["| seed | arm | people m/s | n | reached % (95 % CI) | collision % (95 % CI) | stuck % (95 % CI) "
           "| timeout % | time to B median s (p25-p75) | warning s median (min-max, n collided) "
           "| median min person clearance m |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for sd in seeds:
        for arm in arms:
            for sp in speeds:
                s = summ[f"{sd}/{arm}/{sp}"]
                warn = "-" if not s["warning_n"] else f"{s['warning_median_s']} ({s['warning_min_s']}-{s['warning_max_s']}, {s['warning_n']})"
                out.append(f"| {sd} | {arm} | {sp} | {s['n']} | {ci(s, 'reached_pct')} | {ci(s, 'collision_pct')} "
                           f"| {ci(s, 'stuck_pct')} | {s['timeout_pct']} | {f(s['time_to_b_median_s'])} "
                           f"({f(s['time_to_b_p25_s'])}-{f(s['time_to_b_p75_s'])}) | {warn} "
                           f"| {f(s['median_min_mover_clearance_m'])} |")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--speeds", default="0.5,1.0")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--out", default=RESULTS)
    ap.add_argument("--tag", default="predict")
    ap.add_argument("--replay-seed", type=int, default=None)
    ap.add_argument("--replay-speed", type=float, default=1.0)
    ap.add_argument("--replay-index", type=int, default=None,
                    help="layout to replay; default: first seed-1 layout where astar collides and both new arms reach")
    a = ap.parse_args(argv)
    arms = [x for x in a.arms.split(",") if x]
    seeds = [int(x) for x in a.seeds.split(",") if x]
    speeds = [float(x) for x in a.speeds.split(",") if x]
    cmd = "python run_predict.py " + " ".join(argv if argv is not None else sys.argv[1:])
    tasks = [(arm, sp, i, sd) for sd in seeds for arm in arms for sp in speeds for i in range(a.layouts)]
    t0 = time.perf_counter()
    if a.workers > 1:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            rows = list(ex.map(_task, tasks, chunksize=1))
    else:
        rows = [_task(t) for t in tasks]
    wall = time.perf_counter() - t0
    for r, (arm, sp, i, sd) in zip(rows, tasks):
        r["seed"] = sd
    summ = {f"{sd}/{arm}/{sp}": summarize([r for r in rows if r["arm"] == arm and r["seed"] == sd and r["speed_mps"] == sp])
            for sd in seeds for arm in arms for sp in speeds}
    pooled = {f"{sd}/{arm}": summarize([r for r in rows if r["arm"] == arm and r["seed"] == sd])
              for sd in seeds for arm in arms}
    verdicts = {}
    if "astar_f2" in arms:
        for arm in arms:
            if arm != "astar_f2":
                for sd in seeds:
                    verdicts[f"{sd}/{arm}"] = paired(rows, arm, "astar_f2", sd, speeds)
    # existing arms on seed 0 must match results/moving_0.json row for row
    check = None
    ref_path = os.path.join(RESULTS, "moving_0.json")
    if 0 in seeds and os.path.exists(ref_path):
        ref = {(r["arm"], r["speed_mps"], r["index"]): r for r in json.load(open(ref_path))["runs"]}
        keys = ("outcome", "min_clearance_m", "duration_s", "warning_s")
        same = diff = 0
        for r in rows:
            q = ref.get((r["arm"], r["speed_mps"], r["index"]))
            if r["seed"] == 0 and r["arm"] in EXISTING and q is not None:
                if all(r[k] == q[k] for k in keys):
                    same += 1
                else:
                    diff += 1
        check = {"matched": same, "differ": diff, "fields": keys}
    # replay: one paired layout, astar and the two new arms
    replays = []
    rs = a.replay_seed if a.replay_seed is not None else (1 if 1 in seeds else seeds[0])
    if all(x in arms for x in ("astar", "st_astar", "astar_vo")):
        idx = a.replay_index
        if idx is None:
            by = {(r["arm"], r["seed"], r["speed_mps"], r["index"]): r for r in rows}
            idx = next((i for i in range(a.layouts)
                        if by[("astar", rs, a.replay_speed, i)]["collision"]
                        and by[("st_astar", rs, a.replay_speed, i)]["reached"]
                        and by[("astar_vo", rs, a.replay_speed, i)]["reached"]), 0)
        for arm in ("astar", "st_astar", "astar_vo"):
            p, outcome, size = replay(arm, a.replay_speed, idx, rs, a.out)
            agrees = next(r for r in rows if r["arm"] == arm and r["seed"] == rs and r["speed_mps"] == a.replay_speed
                          and r["index"] == idx)["outcome"] == outcome
            replays.append({"file": os.path.basename(p), "outcome": outcome, "bytes": size,
                            "same_outcome_as_batch": agrees})

    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system(), "workers": a.workers}
    consts = lambda mod: {k: v for k, v in vars(mod).items() if k.isupper() and isinstance(v, (int, float, tuple))}
    os.makedirs(a.out, exist_ok=True)
    stem = os.path.join(a.out, f"{a.tag}_{'_'.join(map(str, seeds))}")
    with open(stem + ".json", "w") as fh:
        json.dump({"command": cmd, "input": "synthetic", "family": run_moving.FAMILY, "seeds": seeds,
                   "tuning_seed": 0, "held_out_seeds": [s for s in seeds if s != 0], "layouts": a.layouts,
                   "speeds": speeds, "arms": {k: LABELS[k] for k in arms},
                   "constants": {"predict": consts(predict), "planners_st": consts(planners_st), "vo": consts(vo)},
                   "summary": summ, "pooled": pooled, "verdicts_vs_astar_f2": verdicts,
                   "seed0_existing_arms_vs_moving_0": check, "replays": replays,
                   "wall_s": round(wall, 1), "env": env, "runs": rows}, fh, indent=1)

    f = lambda v: "-" if v is None else f"{v}"
    lines = [f"`{cmd}` (synthetic), wall {wall:.1f} s, {len(tasks)} runs, {a.workers} workers, CPython {env['python']}, "
             f"numpy {env['numpy']}, scipy {env['scipy']}, {env['system']} {env['machine']}", "",
             "Inputs are synthetic: arena `random` layouts, simulated people (1-3 per layout, r 0.25 m, straight "
             "segments at constant speed with an instant U-turn), simulated 72-beam fan, truth pose. The people walk "
             "straight lines, which is the constant-velocity model: this favours the predictor arms.", "",
             "Seed 0 = tuning seed, seed 1 = held out. 95 % CI = Wilson score interval. Warning = contact time minus "
             "first step the hit person was visible to the fan (collided runs only).", ""]
    lines += table(summ, arms, seeds, speeds)
    lines += ["", "Pooled over both speeds (100 runs per seed and arm):", "",
              "| seed | arm | reached % (95 % CI) | collision % (95 % CI) | stuck % (95 % CI) | time to B median s |",
              "|---|---|---|---|---|---|"]
    for sd in seeds:
        for arm in arms:
            s = pooled[f"{sd}/{arm}"]
            lines.append(f"| {sd} | {arm} | {s['reached_pct']} ({s['reached_pct_ci'][0]}-{s['reached_pct_ci'][1]}) "
                         f"| {s['collision_pct']} ({s['collision_pct_ci'][0]}-{s['collision_pct_ci'][1]}) "
                         f"| {s['stuck_pct']} ({s['stuck_pct_ci'][0]}-{s['stuck_pct_ci'][1]}) | {f(s['time_to_b_median_s'])} |")
    if verdicts:
        lines += ["", "Paired against astar_f2 (same layouts, both speeds). Rule: PASS when collisions <= astar_f2's, "
                  "more runs reach B, and the exact sign test on layouts where only one of the two reached gives "
                  "p < 0.05. The verdict that counts is the held-out seed 1.", "",
                  "| seed | arm | reached only by arm | reached only by astar_f2 | sign test p | collisions arm / astar_f2 | verdict |",
                  "|---|---|---|---|---|---|---|"]
        for k, v in verdicts.items():
            sd, arm = k.split("/")
            lines.append(f"| {sd} | {arm} | {v['arm_only_reached']} | {v['ref_only_reached']} | {v['sign_test_p']} "
                         f"| {v['collisions_arm']} / {v['collisions_ref']} | {v['verdict']} |")
    lines += ["", "Predictor accuracy (confirmed tracks sampled every 0.5 s, each matched to the nearest true person "
              "within 0.5 m; truth used only for this table). err_tau = distance between the constant-velocity "
              "prediction tau s ahead and where the person really is then.", "",
              "| seed | arm | people m/s | samples | err 0 s median / p90 m | err 1 s median / p90 m "
              "| err 3 s median / p90 m | median abs speed error m/s | plan ms (median of run medians, max) |",
              "|---|---|---|---|---|---|---|---|---|"]
    for sd in seeds:
        for arm in arms:
            for sp in speeds:
                s = summ[f"{sd}/{arm}/{sp}"]
                if "pred" not in s:
                    continue
                p = s["pred"]
                lines.append(f"| {sd} | {arm} | {sp} | {p['err_0s']['n']} | {p['err_0s']['median']} / {p['err_0s']['p90']} "
                             f"| {p['err_1s']['median']} / {p['err_1s']['p90']} | {p['err_3s']['median']} / {p['err_3s']['p90']} "
                             f"| {p['speed_err']['median_abs']} | {f(s.get('plan_ms_median_of_medians'))}, {f(s.get('plan_ms_max'))} |")
    lines += ["", "Planner counters (summed over runs): st_astar n_capped = searches that hit the expansion cap, "
              "n_relaxed = searches that needed PERSON_MARGIN 0, n_escape = no path, stepped away; astar_vo "
              "n_gated = 10 Hz steps the VO changed the command, n_no_free = steps with no VO-free candidate.", ""]
    for sd in seeds:
        for arm in arms:
            for sp in speeds:
                s = summ[f"{sd}/{arm}/{sp}"]
                if "planner_stats_total" in s:
                    lines.append(f"- seed {sd} {arm} {sp} m/s: {s['planner_stats_total']}")
    if check:
        lines += ["", f"Reuse check: existing arms on seed 0 vs results/moving_0.json on {', '.join(check['fields'])}: "
                  f"{check['matched']} runs identical, {check['differ']} differ."]
    if replays:
        lines += ["", "Replays (seed {}, {} m/s, layout {}): ".format(rs, a.replay_speed, idx)
                  + "; ".join(f"[{r['file']}]({r['file']}) {r['outcome']}, {r['bytes']} bytes, "
                              f"same outcome as batch: {r['same_outcome_as_batch']}" for r in replays)]
    lines += ["", "Every collided run:", "", "| seed | arm | speed | layout | hit | t_collision s | warning s "
              "| vehicle speed at contact m/s |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["collision"]:
            lines.append(f"| {r['seed']} | {r['arm']} | {r['speed_mps']} | {r['index']} | {r['hit']} | {r['t_collision_s']} "
                         f"| {f(r['warning_s'])} | {r['speed_at_contact_mps']} |")
    md = "\n".join(lines) + "\n"
    with open(stem + ".md", "w") as fh:
        fh.write(md)
    print(md)
    print(f"wrote {stem}.json, {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
