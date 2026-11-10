"""Flights: Hybrid A* vs astar_esdf (unknown map) on the stock and a turn-rate-limited vehicle.

.venv/bin/python bench.py --layouts 20 --seed 0 --workers 14        # results/bench_0.json, .md
.venv/bin/python bench.py --render bench_0                           # rebuild the .md from the .json

Planners (all build their own log-odds map from range hits; map corner on the area geofence, as
samples/close-area-benchmark's astar_unknown):
  astar_unknown      astar_esdf(known_map=False) + its carrot follower (the benchmark row)
  astar_unknown_pp   same, plus a turn-aware speed cap: v <= max(V_TURN, OMEGA_MAX * R), with
                     R = LOOKAHEAD_M / (2 sin|e|) the pure-pursuit radius to the carrot and e the
                     angle between the current velocity and the command (control arm: does slowing
                     at corners alone give what Hybrid A* gives?)
  hybrid_astar       hybrid_astar.HybridAStar(omega_max=1.0), same map, inflation, replan rule, follower
Vehicles: stock (close-area-arena vehicle.py) and turn1 (vehicle_turn.TurnLimitedVehicle,
  velocity direction turns at <= 1.0 rad/s). Presets: ideal on 8 families; crazyflie on random and
  office. The loop is close-area-benchmark/bench.py run_one without the filter branch (same stop
  conditions, sensor seeds and 120 s limit for maze and warehouse); scored on truth.
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import arena  # noqa: E402
import hybrid_astar  # noqa: E402
import metrics  # noqa: E402
from vehicle_turn import TurnLimitedVehicle  # noqa: E402

run, scorer, world_glass, presets = arena.mod("run"), arena.mod("scorer"), arena.mod("world_glass"), arena.mod("presets")
vehicle, adapter = arena.mod("vehicle"), arena.adapter
AE = arena.astar_esdf
RESULTS = os.path.join(HERE, "results")
BENCH_MATRIX = os.path.join(HERE, "..", "close-area-benchmark", "results", "matrix_0.json")

FAMILIES = ("random", "u_trap", "narrow_gap", "office", "warehouse", "forest", "maze", "glass_office")
CF_FAMILIES = ("random", "office")
LONG_FAMILIES = {"maze": 120.0, "warehouse": 120.0}
OMEGA_TURN = 1.0                      # rad/s, turn1 vehicle and the planners' turn-rate limit
VEHICLES = ("stock", "turn1")
PLANNERS = ("astar_unknown", "astar_unknown_pp", "hybrid_astar")
MOVING_MPS = 0.3                      # a "stuck" run whose truth speed over its last 0.5 s exceeds this was
                                      # passing back over where it was 10 s earlier (scorer rule), not hovering


class GeofencedAStar(AE.AStarESDF):
    """astar_esdf(known_map=False) with its map corner on the geofence (close-area-benchmark)."""

    def __init__(self, bounds, margin: float = 2.0):
        self.bounds, self.margin = bounds, margin
        super().__init__(known_map=False)

    def reset(self) -> None:
        super().reset()
        if self.map is not None:
            self.map.x0 = self.bounds[0] - self.margin
            self.map.y0 = self.bounds[1] - self.margin


class TurnAwareAStar(GeofencedAStar):
    """GeofencedAStar with a pure-pursuit speed cap for a turn-rate limit omega."""

    def __init__(self, bounds, omega: float = OMEGA_TURN, margin: float = 2.0):
        self.omega = omega
        super().__init__(bounds, margin)

    def step(self, pose, scan, goal, grid, dt):
        sp = super().step(pose, scan, goal, grid, dt)
        s = math.hypot(sp.vx, sp.vy)
        vh = math.hypot(pose.vx, pose.vy)
        if s < 1e-6 or vh < 0.3:
            return sp
        e = abs(hybrid_astar._wrap(math.atan2(sp.vy, sp.vx) - math.atan2(pose.vy, pose.vx)))
        if e >= math.pi / 2:
            cap = hybrid_astar.V_TURN
        else:
            cap = max(hybrid_astar.V_TURN, self.omega * AE.LOOKAHEAD_M / max(2 * math.sin(e), 1e-9))
        if s > cap:
            k = cap / s
            sp = adapter.Setpoint(sp.vx * k, sp.vy * k, sp.vz, sp.yaw_rate)
        return sp


def _bounds(w):
    return (w.xmin, w.ymin, w.xmax, w.ymax)


def make_planner(name, w):
    if name == "astar_unknown":
        return GeofencedAStar(_bounds(w))
    if name == "astar_unknown_pp":
        return TurnAwareAStar(_bounds(w))
    if name == "hybrid_astar":
        return hybrid_astar.make(bounds=_bounds(w), omega_max=OMEGA_TURN)
    raise KeyError(name)


def max_time(family):
    return LONG_FAMILIES.get(family, run.DEFAULTS["max_time_s"])


def run_one(planner, family, preset, veh_name, index, seed=0, keep_trace=False):
    cfg = run.DEFAULTS
    vk = cfg["vehicle"]
    radius = vk["radius"]
    w = world_glass.make_any_world(family, seed, index, radius=radius)
    pl = make_planner(planner, w)
    goal = (w.goal[0], w.goal[1], cfg["z0"])
    yaw0 = math.atan2(goal[1], goal[0])
    if veh_name == "stock":
        veh = vehicle.Vehicle(0.0, 0.0, cfg["z0"], yaw=yaw0, **vk)
    else:
        veh = TurnLimitedVehicle(0.0, 0.0, cfg["z0"], yaw=yaw0, omega_max=OMEGA_TURN, **vk)
    sensor = presets.make_sensor(preset, np.random.default_rng([seed, index, 7]))
    ad = adapter.SimAdapter(w, veh, sensor)
    pl.reset()
    HZ = vehicle.HZ
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    t_max = max_time(family)
    n_steps = int(round(t_max * HZ))
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    ts, xy = [0.0], [(0.0, 0.0)]
    t_wall = time.perf_counter()
    for k in range(n_steps):
        if k % ratio == 0:
            ad.send_setpoint(pl.step(ad.pose(), ad.ranges(), goal, None, pdt))
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
    tail = np.array(xy[-26:])                     # last 0.5 s of truth
    end_speed = float(np.hypot(*(tail[-1] - tail[0])) / (0.02 * (len(tail) - 1))) if len(tail) > 1 else 0.0
    res.update({"end_speed_mps": round(end_speed, 3),
                "stuck_while_moving": bool(res["outcome"] == "stuck" and end_speed > MOVING_MPS)})
    res.update({"planner": planner, "family": family, "preset": preset, "vehicle": veh_name, "index": index,
                "seed": seed, "max_time_s": t_max, "n_obstacles": len(w.boxes) + len(w.cylinders),
                "flown": metrics.heading_stats(np.array(xy)),
                "replan_ms": [round(m, 2) for m in pl.replan_ms],
                "wall_s": round(time.perf_counter() - t_wall, 2)})
    if planner == "hybrid_astar":
        res["grid_fallback_replans"] = pl.grid_fallbacks
        res["expansions_median"] = float(np.median(pl.expansions)) if pl.expansions else None
    res["hit_material"] = None
    if res["collision"]:
        for (x, y) in xy:
            if w.clearance(x, y) < radius:
                res["hit_material"], _ = world_glass.nearest_material(w, x, y)
                break
    if keep_trace:
        return res, (w, np.array(xy), getattr(pl, "path_xy", None))
    return res


def _task(a):
    return run_one(*a)


def tasks_for(layouts, seed, planners=PLANNERS, vehicles=VEHICLES, families=FAMILIES, cf_families=CF_FAMILIES):
    t = [(p, f, "ideal", v, i, seed) for p in planners for v in vehicles for f in families for i in range(layouts)]
    t += [(p, f, "crazyflie", v, i, seed) for p in planners for v in vehicles for f in cf_families
          for i in range(layouts)]
    return t


def _med(xs):
    xs = [x for x in xs if x is not None]
    return round(float(np.median(xs)), 3) if xs else None


def summarize(rows):
    s = scorer.summarize(rows)
    ms = [m for r in rows for m in r["replan_ms"]]
    s["median_path_length_m"] = _med([r["path_length_m"] for r in rows])
    s["median_flown_max_rad_per_m"] = _med([r["flown"]["max_rad_per_m"] for r in rows if r["reached"]])
    s["median_flown_p95_rad_per_m"] = _med([r["flown"]["p95_rad_per_m"] for r in rows if r["reached"]])
    s["replan_ms_median"] = round(float(np.median(ms)), 2) if ms else None
    s["replan_ms_p95"] = round(float(np.percentile(ms, 95)), 2) if ms else None
    s["replans"] = len(ms)
    s["stuck_while_moving_pct"] = round(100.0 * sum(r["stuck_while_moving"] for r in rows) / len(rows), 1)
    if any("grid_fallback_replans" in r for r in rows):
        s["grid_fallback_pct"] = round(100.0 * sum(r["grid_fallback_replans"] for r in rows) / max(1, len(ms)), 2)
    return s


def paired(rows, a, b, key):
    """Median of b - a on (family, preset, vehicle, index) runs that both reached."""
    ra = {(r["family"], r["preset"], r["vehicle"], r["index"]): r for r in rows if r["planner"] == a}
    d = []
    for r in rows:
        if r["planner"] != b:
            continue
        o = ra.get((r["family"], r["preset"], r["vehicle"], r["index"]))
        if o and o["reached"] and r["reached"]:
            d.append(r[key] - o[key])
    return (round(float(np.median(d)), 2) if d else None), len(d)


def parity(rows):
    """astar_unknown, stock vehicle, vs close-area-benchmark/results/matrix_0.json row by row."""
    if not os.path.exists(BENCH_MATRIX):
        return None
    ref = {(r["family"], r["preset"], r["index"]): r for r in json.load(open(BENCH_MATRIX))["runs"]
           if r["planner"] == "astar_unknown"}
    same = n = 0
    for r in rows:
        if r["planner"] == "astar_unknown" and r["vehicle"] == "stock":
            o = ref.get((r["family"], r["preset"], r["index"]))
            if o is None:
                continue
            n += 1
            same += int(o["outcome"] == r["outcome"] and o["min_clearance_m"] == r["min_clearance_m"]
                        and o["path_length_m"] == r["path_length_m"])
    return f"{same}/{n}"


def render(stem):
    d = json.load(open(stem + ".json"))
    rows = d["runs"]
    f = lambda v: "-" if v is None else f"{v:g}"        # noqa: E731
    out = [f"`{d['command']}` from samples/close-area-planner-hybrid-astar. Input: synthetic (simulated layouts, "
           f"vehicle and sensor). Seed {d['seed']}, {d['layouts']} layouts per cell, {d['workers']} processes, wall "
           f"{d['wall_s']} s. Planner maps: unknown (log-odds from range hits), geofenced.", "",
           f"Parity: astar_unknown on the stock vehicle vs close-area-benchmark/results/matrix_0.json, same outcome, "
           f"min clearance and path length: {d['parity_vs_benchmark']} runs.", "",
           "Replan ms are pooled over every replan of the cell, measured with all processes busy (not a clean "
           "timing; see timing_jobs1_0.md). Flown max / p95 heading change per metre: median over runs that "
           "reached B, truth path resampled every 0.25 m. Stuck while moving = scorer outcome stuck "
           "(|p(t) - p(t - 10 s)| < 0.2 m) with truth speed above 0.3 m/s over the last 0.5 s: the vehicle "
           "was flying back over the point it passed 10 s earlier (a dead end turned back from), not hovering. "
           "The arena scorer ends those runs; they count as stuck here too.", ""]
    cols = ("| vehicle | preset | planner | family | reached % | collision % | stuck % | timeout % | median time to B s "
            "| median path m | median min clearance m | flown max rad/m | flown p95 rad/m | replan ms median / p95 "
            "| grid fallback % of replans | stuck while moving % |")
    out += [cols, "|" + "---|" * 16]
    for v in d["vehicles"]:
        for pr in ("ideal", "crazyflie"):
            for p in d["planners"]:
                for fam in d["families"]:
                    s = d["summary"].get(v, {}).get(pr, {}).get(p, {}).get(fam)
                    if not s:
                        continue
                    out.append(f"| {v} | {pr} | {p} | {fam} | {f(s['reached_pct'])} | {f(s['collision_pct'])} | "
                               f"{f(s['stuck_pct'])} | {f(s['timeout_pct'])} | {f(s['median_time_to_goal_s'])} | "
                               f"{f(s['median_path_length_m'])} | {f(s['median_min_clearance_m'])} | "
                               f"{f(s['median_flown_max_rad_per_m'])} | {f(s['median_flown_p95_rad_per_m'])} | "
                               f"{f(s['replan_ms_median'])} / {f(s['replan_ms_p95'])} | "
                               f"{f(s.get('grid_fallback_pct'))} | {f(s['stuck_while_moving_pct'])} |")
    out += ["", "Totals per vehicle and preset (all families of the preset pooled):", "",
            "| vehicle | preset | planner | runs | reached % | collision % | stuck % | stuck while moving % | timeout % "
            "| replan ms median / p95 |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for k in d["totals"]:
        s = d["totals"][k]
        v, pr, p = k.split("|")
        out.append(f"| {v} | {pr} | {p} | {s['n']} | {f(s['reached_pct'])} | {f(s['collision_pct'])} | "
                   f"{f(s['stuck_pct'])} | {f(s['stuck_while_moving_pct'])} | {f(s['timeout_pct'])} | "
                   f"{f(s['replan_ms_median'])} / {f(s['replan_ms_p95'])} |")
    out += ["", "Replan wall time pooled over every replan of the file, per planner:", "",
            "| planner | replans | median ms | p95 ms | p99 ms | max ms | replans > 200 ms |", "|---|---|---|---|---|---|---|"]
    for p in d["planners"]:
        ms = np.array([m for r in rows if r["planner"] == p for m in r["replan_ms"]])
        if len(ms):
            out.append(f"| {p} | {len(ms)} | {np.median(ms):.2f} | {np.percentile(ms, 95):.2f} | "
                       f"{np.percentile(ms, 99):.2f} | {ms.max():.2f} | {int((ms > 200).sum())} |")
    out += ["", "Paired: median of (planner - astar_unknown) time to B on runs where both reached, per vehicle "
            "(both presets):", "", "| vehicle | planner | median delta time to B s | paired runs | median delta path m |",
            "|---|---|---|---|---|"]
    for v in d["vehicles"]:
        sel = [r for r in rows if r["vehicle"] == v]
        for p in d["planners"]:
            if p == "astar_unknown":
                continue
            dt, n = paired(sel, "astar_unknown", p, "time_to_goal_s")
            dl, _ = paired(sel, "astar_unknown", p, "path_length_m")
            out.append(f"| {v} | {p} | {f(dt)} | {n} | {f(dl)} |")
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(out) + "\n")


def env():
    return {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "machine": platform.machine(), "system": platform.system(), "cpus": os.cpu_count()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--planners", default=",".join(PLANNERS))
    ap.add_argument("--vehicles", default=",".join(VEHICLES))
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--cf-families", default=",".join(CF_FAMILIES), help="crazyflie preset families ('' = none)")
    ap.add_argument("--stem", default=None)
    ap.add_argument("--render", default=None, metavar="STEM")
    a = ap.parse_args(argv)
    if a.render:
        render(os.path.join(RESULTS, a.render))
        return 0
    cmd = "python bench.py " + " ".join(argv if argv is not None else sys.argv[1:])
    planners, vehicles = a.planners.split(","), a.vehicles.split(",")
    families = a.families.split(",")
    cf = [x for x in a.cf_families.split(",") if x]
    tasks = tasks_for(a.layouts, a.seed, planners, vehicles, families, cf)
    tasks.sort(key=lambda t: (t[1] not in LONG_FAMILIES, t[0] != "hybrid_astar"))
    t0 = time.perf_counter()
    rows = []
    if a.workers <= 1:
        for k, t in enumerate(tasks):
            rows.append(_task(t))
    else:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            for k, r in enumerate(ex.map(_task, tasks, chunksize=1)):
                rows.append(r)
                if (k + 1) % 100 == 0:
                    print(f"{k + 1}/{len(tasks)} runs, {time.perf_counter() - t0:.0f} s", flush=True)
    wall = round(time.perf_counter() - t0, 1)
    allfam = list(dict.fromkeys(families + cf))
    rows.sort(key=lambda r: (vehicles.index(r["vehicle"]), r["preset"] != "ideal", planners.index(r["planner"]),
                             allfam.index(r["family"]), r["index"]))
    summ, totals = {}, {}
    for v in vehicles:
        for pr in ("ideal", "crazyflie"):
            for p in planners:
                sel_p = [r for r in rows if r["vehicle"] == v and r["preset"] == pr and r["planner"] == p]
                if sel_p:
                    totals[f"{v}|{pr}|{p}"] = summarize(sel_p)
                for fam in allfam:
                    sel = [r for r in sel_p if r["family"] == fam]
                    if sel:
                        summ.setdefault(v, {}).setdefault(pr, {}).setdefault(p, {})[fam] = summarize(sel)
    os.makedirs(RESULTS, exist_ok=True)
    stem = os.path.join(RESULTS, a.stem or f"bench_{a.seed}")
    d = {"command": cmd, "input": "synthetic", "seed": a.seed, "layouts": a.layouts, "workers": a.workers,
         "wall_s": wall, "planners": planners, "vehicles": vehicles, "families": allfam,
         "omega_turn": OMEGA_TURN, "parity_vs_benchmark": parity(rows), "env": env(),
         "hybrid_constants": {k: v for k, v in vars(hybrid_astar).items() if k.isupper() and isinstance(v, (int, float))},
         "summary": summ, "totals": totals, "runs": rows}
    with open(stem + ".json", "w") as fh:
        json.dump(d, fh, indent=1)
    render(stem)
    print(open(stem + ".md").read())
    print(f"wall {wall} s; wrote {os.path.relpath(stem, HERE)}.json, .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
