"""Planners x layout families x sensor presets, scored on truth.

python run_sensors.py --layouts 50 --seed 0 [--planners freest_beam,astar_unknown]
                      [--families random,glass] [--presets ideal,crazyflie,crazyflie_bright]

run.evaluate builds its own RangeFan from cfg["sensor"] and its world from world.make_world, so
it cannot take a cone sensor or the glass family. run_one below is run.run_one with two
arguments added (sensor, world); the loop, stop conditions and scorer are the same.
--parity reruns ideal x random through run.evaluate and checks the outcomes match.

Planners: freest_beam (CONTRACT.md example, from run_faults.py) and astar_unknown
(planners/astar_esdf.py, known_map=False: map from range hits only).

Writes results/sensors_<seed>.json (config, presets, per-run rows) and results/sensors_<seed>.md.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import time

import numpy as np
import scipy

try:
    from . import presets, run, scorer, world_glass
    from .adapter import SimAdapter
    from .planners.astar_esdf import AStarESDF
    from .run_faults import FreestBeam
    from .vehicle import HZ, Vehicle
except ImportError:
    import presets
    import run
    import scorer
    import world_glass
    from adapter import SimAdapter
    from planners.astar_esdf import AStarESDF
    from run_faults import FreestBeam
    from vehicle import HZ, Vehicle

PLANNERS = {
    "freest_beam": lambda: FreestBeam(),
    "astar_unknown": lambda: AStarESDF(known_map=False),
}


def run_one(planner, w, sensor, seed: int, index: int, cfg: dict = run.DEFAULTS) -> dict:
    """run.run_one with the sensor passed in. Same loop, stop conditions and scorer."""
    goal = (w.goal[0], w.goal[1], cfg["z0"])
    vk = cfg["vehicle"]
    veh = Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **vk)
    ad = SimAdapter(w, veh, sensor)
    planner.reset()
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    n_steps = int(round(cfg["max_time_s"] * HZ))
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    grid = w.grid if getattr(planner, "uses_grid", False) else None
    radius = vk["radius"]
    ts, xy = [0.0], [(0.0, 0.0)]
    for k in range(n_steps):
        if k % ratio == 0:
            ad.send_setpoint(planner.step(ad.pose(), ad.ranges(), goal, grid, pdt))
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
    mats = getattr(w, "materials", {}) or {}
    res.update({
        "index": index, "layout_attempts": w.attempts,
        "n_obstacles": len(w.boxes) + len(w.cylinders),
        "n_glass": mats.get("boxes", []).count("glass"),
        "n_poles": mats.get("cylinders", []).count("pole"),
        "goal": [round(goal[0], 3), round(goal[1], 3)],
    })
    if res["collision"]:
        # material of the surface hit: nearest surface to the first truth point inside the radius
        for (x, y) in xy:
            if w.clearance(x, y) < radius:
                res["hit_material"], _ = world_glass.nearest_material(w, x, y)
                break
    return res


def evaluate(planner: str, family: str, preset: str, layouts: int, seed: int):
    rows = []
    for i in range(layouts):
        w = world_glass.make_any_world(family, seed, i, radius=run.DEFAULTS["vehicle"]["radius"])
        sensor = presets.make_sensor(preset, np.random.default_rng([seed, i, 7]))   # run.py noise stream
        rows.append(run_one(PLANNERS[planner](), w, sensor, seed, i))
    s = scorer.summarize(rows)
    hits: dict = {}
    for r in rows:
        if r.get("hit_material"):
            hits[r["hit_material"]] = hits.get(r["hit_material"], 0) + 1
    s["collisions_by_material"] = hits
    return rows, s


def parity(layouts: int, seed: int) -> dict:
    """ideal x random through this loop vs run.evaluate (same sensor class, rng and worlds)."""
    out = {}
    for name, fac in PLANNERS.items():
        mine, _ = evaluate(name, "random", "ideal", layouts, seed)
        ref, _, _ = run.evaluate(fac, "random", layouts, seed)
        same = sum(a["outcome"] == b["outcome"] and a["min_clearance_m"] == b["min_clearance_m"]
                   for a, b in zip(mine, ref))
        out[name] = {"layouts": layouts, "identical_outcome_and_clearance": same}
    return out


def fmt(v):
    return "-" if v is None else f"{v}"


HEAD = ("| planner | family | preset | layouts | reached % | collision % | stuck % | timeout % "
        "| median min clearance m | collisions by material |\n"
        "|---|---|---|---|---|---|---|---|---|---|")


def line(p, f, pr, s):
    hm = ", ".join(f"{k} {v}" for k, v in sorted(s["collisions_by_material"].items())) or "-"
    return (f"| {p} | {f} | {pr} | {s['n']} | {fmt(s['reached_pct'])} | {fmt(s['collision_pct'])} "
            f"| {fmt(s['stuck_pct'])} | {fmt(s['timeout_pct'])} | {fmt(s['median_min_clearance_m'])} | {hm} |")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--planners", default="freest_beam,astar_unknown")
    ap.add_argument("--families", default="random,glass")
    ap.add_argument("--presets", default="ideal,crazyflie,crazyflie_bright")
    ap.add_argument("--parity", action="store_true", help="check ideal x random against run.evaluate")
    ap.add_argument("--out", default=run.RESULTS)
    a = ap.parse_args(argv)
    cmd = "python run_sensors.py " + " ".join(argv if argv is not None else sys.argv[1:])
    t_all = time.perf_counter()
    combos, lines = [], []
    for p in a.planners.split(","):
        for f in a.families.split(","):
            for pr in a.presets.split(","):
                t0 = time.perf_counter()
                rows, s = evaluate(p, f, pr, a.layouts, a.seed)
                s["wall_s"] = round(time.perf_counter() - t0, 1)
                combos.append({"planner": p, "family": f, "preset": pr, "summary": s, "runs": rows})
                lines.append(line(p, f, pr, s))
                print(lines[-1], f"wall {s['wall_s']} s", flush=True)
    par = parity(a.layouts, a.seed) if a.parity else None
    wall = round(time.perf_counter() - t_all, 1)
    os.makedirs(a.out, exist_ok=True)
    stem = os.path.join(a.out, f"sensors_{a.seed}")
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
           "machine": platform.machine(), "system": platform.system()}
    with open(stem + ".json", "w") as fh:
        json.dump({"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts,
                   "config": run.DEFAULTS, "presets": presets.SENSOR_PRESETS, "parity": par,
                   "wall_s": wall, "env": env, "combos": combos}, fh, indent=1, default=list)
    md = [f"`{cmd}` from samples/close-area-arena. Input: synthetic (simulated layouts, vehicle and "
          f"sensor). Scored on truth. Wall {wall} s.", "", HEAD] + lines
    if par:
        md += ["", "Parity, ideal x random, this loop vs run.evaluate (runs with identical outcome and "
               "min clearance): " + ", ".join(f"{k} {v['identical_outcome_and_clearance']}/{v['layouts']}"
                                               for k, v in par.items())]
    md += ["", "Collisions (planner, family, preset: run => material hit, min clearance m):", ""]
    for c in combos:
        hit = [f"{r['index']} => {r.get('hit_material')} {r['min_clearance_m']}" for r in c["runs"] if r["collision"]]
        if hit:
            md.append(f"- {c['planner']}, {c['family']}, {c['preset']}: " + "; ".join(hit))
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(md) + "\n")
    print(f"wrote {stem}.json, {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
