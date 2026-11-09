"""Moving-obstacle family: A* replan, A* + F2 (PX4-CBF style range filter) and APF vs walking people.

python run_moving.py --layouts 50 --seed 0 [--speeds 0.0,0.5,1.0] [--arms astar,astar_f2,apf] [--workers 14]

Per run (one layout, one mover speed, one arm):
  layout   arena world.make_world("random", seed, index): the static boxes and cylinders, and the
           prior OccGrid the A* arms plan on
  movers   moving.draw_movers: 1-3 cylinders r = 0.25 m on seeded segments across the A-B corridor,
           constant speed ping-pong; speed 0.0 = frozen (unmapped static control)
  world    moving.MovingWorld: the range fans and the truth collision check see the movers where
           they are at the current physics step
  arms     astar     astar_replan.AStarReplan on prior grid + latest scan hits, 2.5-5 Hz replans,
                     setpoint at 10 Hz
           astar_5hz the same planner with a 5 Hz periodic replan (rate sensitivity)
           astar_f2  the astar planner, then filters.make("F2") (samples/close-area-safety-filter,
                     PX4-CBF as shipped) every 50 Hz step on its own fan at 16.7 Hz, as run_kill.py
           apf       samples/close-area-planner-reactive apf.make() defaults, scan only, 10 Hz
  pose     truth (no estimator fault in this family)
  scoring  on truth, arena scorer definitions (reached 0.3 m, collision clearance < 0.15 m, stuck,
           timeout 60 s), with clearance against static AND current mover positions

Extra fields per run: hit (mover / static), vehicle speed at contact, vehicle_closing_mps
(vehicle velocity component towards the hit mover's centre at contact; near 0 or negative =>
the mover walked into the vehicle), t_collision_s (time from
take-off), warning_s (time from the first scan in which the hit mover was visible to contact),
min_mover_clearance_m, replan rate. All inputs are synthetic.

Writes results/moving_<seed>.json (per-run rows) and results/moving_<seed>.md (tables).
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

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
FAMILY = "random"
ARMS = ("astar", "astar_5hz", "astar_f2", "apf")
LABELS = {"astar": "A* replan (prior + latest scan, 2.5 Hz periodic, early replan up to 5 Hz)",
          "astar_5hz": "A* replan, 5 Hz periodic (replan rate sensitivity)",
          "astar_f2": "A* replan + F2 (PX4-CBF style range filter)",
          "apf": "APF (range only, wall-follow escape)"}
FILTER_SCAN_EVERY = 3          # physics steps => 16.7 Hz filter scan, same as close-area-safety-filter
STOPPED_MPS = 0.2              # vehicle speed below this at contact => "struck while (nearly) stopped"


def ray_circle(x, y, ang, cx, cy, r):
    """Distance along each world-frame angle to a circle, inf on a miss."""
    dx, dy = np.cos(ang), np.sin(ang)
    ox, oy = x - cx, y - cy
    b = ox * dx + oy * dy
    c = ox * ox + oy * oy - r * r
    disc = b * b - c
    sq = np.sqrt(np.maximum(disc, 0.0))
    t0 = -b - sq
    t = np.where(c <= 0, 0.0, np.where(t0 >= 0, t0, np.inf))
    return np.where((disc >= 0) & (-b + sq >= 0), t, np.inf)


def score_trace(ts, xy, clr, goal, radius) -> dict:
    """arena scorer.score with a precomputed (time-varying) clearance array."""
    sc = arena.scorer
    ts, xy, clr = np.asarray(ts, float), np.asarray(xy, float), np.asarray(clr, float)
    i_r, i_c, i_s = sc.first_events(ts, xy, clr, goal, radius)
    cands = [(i, n) for i, n in ((i_r, "reached"), (i_c, "collision"), (i_s, "stuck")) if i is not None]
    end, outcome = min(cands) if cands else (len(ts) - 1, "timeout")
    seg = np.hypot(np.diff(xy[: end + 1, 0]), np.diff(xy[: end + 1, 1]))
    return {
        "outcome": outcome, "reached": outcome == "reached", "collision": outcome == "collision",
        "stuck": outcome == "stuck", "timeout": outcome == "timeout",
        "time_to_goal_s": round(float(ts[end]), 3) if outcome == "reached" else None,
        "min_clearance_m": round(float(clr[: end + 1].min()), 4),
        "path_length_m": round(float(seg.sum()), 3),
        "duration_s": round(float(ts[end]), 3),
    }, end


def run_one(arm: str, speed: float, index: int, seed: int, cfg=None) -> dict:
    run, Vehicle, HZ, DT = arena.run, arena.vehicle.Vehicle, arena.vehicle.HZ, arena.vehicle.DT
    cfg = cfg or run.DEFAULTS
    radius = cfg["vehicle"]["radius"]
    w0 = arena.world.make_world(FAMILY, seed, index, radius=radius)
    movers, n_drawn = moving.draw_movers(w0, seed, index)
    mw = moving.MovingWorld(w0, movers, speed)
    goal = (w0.goal[0], w0.goal[1], cfg["z0"])
    veh = Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **cfg["vehicle"])
    RF = arena.sensors.RangeFan
    sensor = RF(rng=np.random.default_rng([seed, index, 7]), **cfg["sensor"])
    fsensor = RF(rng=np.random.default_rng([seed, index, 8]), **cfg["sensor"])
    ad = arena.adapter.SimAdapter(mw, veh, sensor)
    if arm in ("astar", "astar_f2"):
        planner, grid = astar_replan.make(), w0.grid
    elif arm == "astar_5hz":
        planner, grid = astar_replan.make(replan_period_s=0.2), w0.grid
    elif arm == "apf":
        planner, grid = arena.apf.make(), None
    else:
        raise ValueError(f"unknown arm {arm!r}")
    planner.reset()
    filt = arena.filters.make("F2") if arm == "astar_f2" else None
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    n_steps = int(round(cfg["max_time_s"] * HZ))
    lag = int(round(arena.scorer.STUCK_WINDOW_S * HZ))
    max_range = cfg["sensor"]["max_range"]

    mw.set_time(0.0)
    ts, xy = [0.0], [(0.0, 0.0)]
    clr = [mw.clearance(0.0, 0.0)]
    mclr = [min(mw.mover_distances(0.0, 0.0), default=math.inf)]
    spd = [0.0]
    vel = [(0.0, 0.0)]
    first_seen = [None] * len(movers)
    sp_nom, fscan = None, None
    n_int = n_f = 0
    t0 = time.perf_counter()
    for k in range(n_steps):
        mw.set_time(veh.t)
        if k % ratio == 0:
            pose = ad.pose()
            scan = ad.ranges()
            sp_nom = planner.step(pose, scan, goal, grid, pdt)
            if filt is None:
                ad.send_setpoint(sp_nom)
            # which movers the fan can see now (exact geometry, before noise and dropout)
            if movers:
                ang = np.asarray(sensor.angles) + veh.yaw
                d_full = mw.raycast(veh.p[0], veh.p[1], ang, max_range)
                for j, ((mx, my), m) in enumerate(zip(mw.positions(), movers)):
                    if first_seen[j] is None:
                        dj = ray_circle(veh.p[0], veh.p[1], ang, mx, my, m.r)
                        if np.any(np.isfinite(d_full) & (dj <= d_full + 1e-6)):
                            first_seen[j] = round(veh.t, 3)
        if filt is not None:
            pose = ad.pose()
            if k % FILTER_SCAN_EVERY == 0:
                fscan = fsensor.scan(mw, veh.p[0], veh.p[1], veh.yaw, veh.t)
            health = {"t": pose.t, "quality": pose.quality, "reset_counter": pose.reset_counter,
                      "sigma_xy": pose.sigma_xy}
            sp, intervened = filt.filter(sp_nom, pose, fscan, w0, health, DT)
            n_f += 1
            n_int += int(intervened)
            ad.send_setpoint(sp)
        ad.tick()
        mw.set_time(veh.t)
        px, py = float(veh.p[0]), float(veh.p[1])
        ts.append(veh.t)
        xy.append((px, py))
        c = mw.clearance(px, py)
        clr.append(c)
        mclr.append(min(mw.mover_distances(px, py), default=math.inf))
        spd.append(math.hypot(veh.v[0], veh.v[1]))
        vel.append((float(veh.v[0]), float(veh.v[1])))
        if math.hypot(px - goal[0], py - goal[1]) <= arena.scorer.GOAL_TOL:
            break
        if c < radius:
            break
        if len(xy) > lag and math.hypot(px - xy[-1 - lag][0], py - xy[-1 - lag][1]) < arena.scorer.STUCK_DIST:
            break
    res, end = score_trace(ts, xy, clr, goal, radius)
    hit = v_hit = warn = t_coll = closing = None
    if res["collision"]:
        t_coll = res["duration_s"]
        px, py = xy[end]
        mw.set_time(ts[end])
        md = mw.mover_distances(px, py)
        sd = w0.clearance(px, py)
        if md and min(md) < sd:
            j = int(np.argmin(md))
            hit = "mover"
            mx, my = mw.positions()[j]
            dn = max(math.hypot(mx - px, my - py), 1e-9)
            closing = round((vel[end][0] * (mx - px) + vel[end][1] * (my - py)) / dn, 3)
            warn = None if first_seen[j] is None else round(t_coll - first_seen[j], 3)
        else:
            hit = "static"
        v_hit = round(spd[end], 3)
    mc = [v for v in mclr[: end + 1] if math.isfinite(v)]
    replans = getattr(planner, "replan_t", None)
    res.update({
        "arm": arm, "speed_mps": speed, "index": index, "n_movers": len(movers), "n_movers_drawn": n_drawn,
        "movers": [m.to_list() for m in movers], "n_static": len(w0.boxes) + len(w0.cylinders),
        "min_mover_clearance_m": round(min(mc), 4) if mc else None,
        "hit": hit, "speed_at_contact_mps": v_hit,
        "vehicle_closing_mps": closing, "t_collision_s": t_coll, "warning_s": warn,
        "first_seen_s": first_seen,
        "replans": len(replans) if replans is not None else None,
        "replan_hz": round(len(replans) / max(res["duration_s"], 1e-9), 2) if replans else None,
        "intervention_frac": round(n_int / n_f, 4) if n_f else None,
        "wall_s": round(time.perf_counter() - t0, 3),
    })
    return res


def _task(args):
    return run_one(*args)


def _q(vals, q):
    return round(float(np.percentile(vals, q)), 2) if vals else None


def summarize(rows):
    n = len(rows)
    pct = lambda key: round(100.0 * sum(bool(r[key]) for r in rows) / n, 1)
    coll = [r for r in rows if r["collision"]]
    tc = [r["t_collision_s"] for r in coll]
    wn = [r["warning_s"] for r in coll if r["warning_s"] is not None]
    rhz = [r["replan_hz"] for r in rows if r["replan_hz"] is not None]
    mm = [r["min_mover_clearance_m"] for r in rows if r["min_mover_clearance_m"] is not None]
    reached = [r["time_to_goal_s"] for r in rows if r["reached"]]
    return {
        "n": n, "reached_pct": pct("reached"), "collision_pct": pct("collision"),
        "stuck_pct": pct("stuck"), "timeout_pct": pct("timeout"),
        "collisions": len(coll), "coll_mover": sum(r["hit"] == "mover" for r in coll),
        "coll_static": sum(r["hit"] == "static" for r in coll),
        "coll_stopped": sum(r["speed_at_contact_mps"] < STOPPED_MPS for r in coll),
        "median_min_clearance_m": round(float(np.median([r["min_clearance_m"] for r in rows])), 3),
        "median_min_mover_clearance_m": round(float(np.median(mm)), 3) if mm else None,
        "median_time_to_goal_s": round(float(np.median(reached)), 2) if reached else None,
        "t_collision_s": {"min": _q(tc, 0), "p25": _q(tc, 25), "median": _q(tc, 50), "p75": _q(tc, 75), "max": _q(tc, 100)},
        "median_vehicle_closing_mps": _q([r["vehicle_closing_mps"] for r in coll if r["vehicle_closing_mps"] is not None], 50),
        "warning_s": {"n": len(wn), "min": _q(wn, 0), "median": _q(wn, 50), "max": _q(wn, 100)},
        "median_replan_hz": round(float(np.median(rhz)), 2) if rhz else None,
    }


def tables(summ, arms, speeds, rows):
    f = lambda v: "-" if v is None else f"{v}"
    out = ["| arm | mover speed m/s | layouts | reached % | collision % | stuck % | timeout % "
           "| collisions with mover / static | of which vehicle < 0.2 m/s | median min clearance m "
           "| median min mover clearance m | median time to goal s | median replan Hz |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm in arms:
        for sp in speeds:
            s = summ[f"{arm}/{sp}"]
            out.append(f"| {arm} | {sp} | {s['n']} | {s['reached_pct']} | {s['collision_pct']} | {s['stuck_pct']} "
                       f"| {s['timeout_pct']} | {s['coll_mover']} / {s['coll_static']} | {s['coll_stopped']} "
                       f"| {s['median_min_clearance_m']} | {f(s['median_min_mover_clearance_m'])} "
                       f"| {f(s['median_time_to_goal_s'])} | {f(s['median_replan_hz'])} |")
    out += ["", "Collided runs: time from take-off to contact (s) and warning time = contact minus the first "
            "scan in which the hit mover was visible (s, mover hits only).", "",
            "| arm | mover speed m/s | collisions | t_collision min | p25 | median | p75 | max "
            "| warning n | warning min | warning median | warning max | median vehicle closing speed m/s |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for arm in arms:
        for sp in speeds:
            s = summ[f"{arm}/{sp}"]
            t, w = s["t_collision_s"], s["warning_s"]
            out.append(f"| {arm} | {sp} | {s['collisions']} | {f(t['min'])} | {f(t['p25'])} | {f(t['median'])} "
                       f"| {f(t['p75'])} | {f(t['max'])} | {w['n']} | {f(w['min'])} | {f(w['median'])} | {f(w['max'])} "
                       f"| {f(s['median_vehicle_closing_mps'])} |")
    out += ["", "Every collided run:", "",
            "| arm | speed | layout | movers | hit | t_collision s | warning s | vehicle speed at contact m/s "
            "| vehicle closing speed m/s |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["collision"]:
            out.append(f"| {r['arm']} | {r['speed_mps']} | {r['index']} | {r['n_movers']} | {r['hit']} "
                       f"| {r['t_collision_s']} | {f(r['warning_s'])} | {r['speed_at_contact_mps']} "
                       f"| {f(r['vehicle_closing_mps'])} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--speeds", default="0.0,0.5,1.0")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--out", default=RESULTS)
    ap.add_argument("--tag", default="moving")
    a = ap.parse_args(argv)
    arms = [x for x in a.arms.split(",") if x]
    speeds = [float(x) for x in a.speeds.split(",") if x]
    cmd = "python run_moving.py " + " ".join(argv if argv is not None else sys.argv[1:])
    tasks = [(arm, sp, i, a.seed) for arm in arms for sp in speeds for i in range(a.layouts)]
    t0 = time.perf_counter()
    if a.workers > 1:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            rows = list(ex.map(_task, tasks, chunksize=2))
    else:
        rows = [_task(t) for t in tasks]
    wall = time.perf_counter() - t0
    summ = {f"{arm}/{sp}": summarize([r for r in rows if r["arm"] == arm and r["speed_mps"] == sp])
            for arm in arms for sp in speeds}
    first = [r for r in rows if r["arm"] == arms[0] and r["speed_mps"] == speeds[0]]
    nm = [r["n_movers"] for r in first]
    dropped = sum(r["n_movers_drawn"] - r["n_movers"] for r in first)
    note = (f"Movers: {sum(nm)} in {len(nm)} layouts (1 mover: {nm.count(1)}, 2: {nm.count(2)}, 3: {nm.count(3)}, "
            f"0: {nm.count(0)}); {dropped} drawn movers dropped because no valid segment fit. "
            f"Mover radius {moving.PERSON_R} m. Speed 0.0 = movers frozen at their start point (control).")
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system(), "workers": a.workers}
    os.makedirs(a.out, exist_ok=True)
    stem = os.path.join(a.out, f"{a.tag}_{a.seed}")
    with open(stem + ".json", "w") as fh:
        json.dump({"command": cmd, "input": "synthetic", "family": FAMILY, "seed": a.seed, "layouts": a.layouts,
                   "arms": {k: LABELS[k] for k in arms}, "speeds": speeds, "arena_config": arena.run.DEFAULTS,
                   "mover_config": {"r": moving.PERSON_R, "n_min": moving.N_MIN, "n_max": moving.N_MAX,
                                    "static_clear_m": moving.STATIC_CLEAR_M, "keep_a_m": moving.KEEP_A_M,
                                    "keep_b_m": moving.KEEP_B_M, "rng": [a.seed, "index", moving.MOVER_SEED]},
                   "planner_config": {"replan_period_s": astar_replan.REPLAN_PERIOD_S,
                                      "min_replan_s": astar_replan.MIN_REPLAN_S},
                   "f2_params": arena.filters.make("F2").p, "filter_scan_every_steps": FILTER_SCAN_EVERY,
                   "summary": summ, "wall_s": round(wall, 1), "env": env, "runs": rows}, fh, indent=1)
    md = (f"`{cmd}` (synthetic), wall {wall:.1f} s, {len(tasks)} runs, {a.workers} workers, "
          f"CPython {env['python']}, numpy {env['numpy']}, scipy {env['scipy']}\n\n{note}\n\n"
          + tables(summ, arms, speeds, rows) + "\n")
    with open(stem + ".md", "w") as fh:
        fh.write(md)
    print(md)
    print(f"wrote {stem}.json, {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
