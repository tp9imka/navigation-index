"""2.5D vs 3D on the window_bar family (world_z.py): does B behind a window need altitude?

.venv/bin/python run_z.py --layouts 50 --seed 0

Modes, same layouts, same vehicle (vehicle_z.VehicleZ, vz enabled), scored on truth in 3D:
  astar_esdf 2.5D  planners/astar_esdf.py (known map) holding z = 1.0 m. Its 2D map holds every
                   box whose z range overlaps the vehicle's height band 1.0 +- 0.15 m
                   (world_z.WorldZ.slice_2d), so a window or bar outside the band is a wall to it.
  astar_esdf_3d    planners/astar_esdf_3d.py on the 0.1 m OccGrid3 (20 x 20 x 3 m).
Scoring follows scorer.py with 3D distances: reached = within 0.3 m of B (3D), collision = 3D
clearance (to boxes, area walls, floor, ceiling) < 0.15 m, stuck = moved < 0.2 m in 10 s,
timeout = 60 s.

Writes results/z_window_bar_<seed>.json and .md, and results/z_window_bar_<seed>_run<k>.png
(side view along the 3D track above a top view; k = first layout where 2.5D fails and 3D reaches).
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
    from . import run as arena_run, scorer, world_z
    from .planners import astar_esdf, astar_esdf_3d
    from .sensors import RangeFan
    from .vehicle import HZ
    from .vehicle_z import SimAdapterZ, VehicleZ
except ImportError:
    import run as arena_run
    import scorer
    import world_z
    from planners import astar_esdf, astar_esdf_3d
    from sensors import RangeFan
    from vehicle import HZ
    from vehicle_z import SimAdapterZ, VehicleZ

CFG = {"max_time_s": 60.0, "plan_hz": 10, "z0": world_z.Z_AB,
       "vehicle": {"tau": 0.15, "a_max": 3.0, "v_max": 2.0, "vz_max": 1.0, "radius": world_z.RADIUS},
       "sensor": dict(arena_run.DEFAULTS["sensor"]),
       "band_2d": [world_z.Z_AB - world_z.RADIUS, world_z.Z_AB + world_z.RADIUS]}
MODES = ("astar_esdf 2.5D", "astar_esdf_3d")


def score3(t, xyz, w, goal, radius) -> dict:
    t, xyz = np.asarray(t, float), np.asarray(xyz, float)
    clr = w.sdf(xyz)
    dg = np.linalg.norm(xyz - np.asarray(goal), axis=1)
    reach = np.flatnonzero(dg <= scorer.GOAL_TOL)
    coll = np.flatnonzero(clr < radius)
    lag = np.searchsorted(t, t - scorer.STUCK_WINDOW_S + 1e-9)
    ok = t >= scorer.STUCK_WINDOW_S - 1e-9
    st = np.flatnonzero(ok & (np.linalg.norm(xyz - xyz[lag], axis=1) < scorer.STUCK_DIST))
    cands = [(int(a[0]), n) for a, n in ((reach, "reached"), (coll, "collision"), (st, "stuck")) if len(a)]
    end, outcome = min(cands) if cands else (len(t) - 1, "timeout")
    seg = np.linalg.norm(np.diff(xyz[:end + 1], axis=0), axis=1)
    return {"outcome": outcome, "reached": outcome == "reached", "collision": outcome == "collision",
            "stuck": outcome == "stuck", "timeout": outcome == "timeout",
            "time_to_goal_s": round(float(t[end]), 3) if outcome == "reached" else None,
            "min_clearance_m": round(float(clr[:end + 1].min()), 4),
            "path_length_m": round(float(seg.sum()), 3), "duration_s": round(float(t[end]), 3),
            "z_min_m": round(float(xyz[:end + 1, 2].min()), 3), "z_max_m": round(float(xyz[:end + 1, 2].max()), 3)}


def run_one(planner, w, grid, seed, index, cfg=CFG):
    goal = tuple(w.goal)
    vk = cfg["vehicle"]
    veh = VehicleZ(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **vk)
    sensor = RangeFan(rng=np.random.default_rng([seed, index, 7]), **cfg["sensor"])
    ad = SimAdapterZ(w, veh, sensor)
    planner.reset()
    ratio, pdt = HZ // cfg["plan_hz"], 1.0 / cfg["plan_hz"]
    n_steps = int(round(cfg["max_time_s"] * HZ))
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    radius = vk["radius"]
    ts, xyz, step_ms = [0.0], [tuple(veh.p)], []
    for k in range(n_steps):
        if k % ratio == 0:
            pose, scan = ad.pose(), ad.ranges()
            t0 = time.perf_counter()
            sp = planner.step(pose, scan, goal, grid, pdt)
            step_ms.append((time.perf_counter() - t0) * 1e3)
            ad.send_setpoint(sp)
        ad.tick()
        p = tuple(float(v) for v in veh.p)
        ts.append(veh.t)
        xyz.append(p)
        if math.dist(p, goal) <= scorer.GOAL_TOL or w.clearance(*p) < radius:
            break
        if len(xyz) > lag and math.dist(p, xyz[-1 - lag]) < scorer.STUCK_DIST:
            break
    row = score3(ts, xyz, w, goal, radius)
    row.update({"index": index, "layout_attempts": w.attempts,
                "elements": [e["kind"] for e in w.elements],
                "step_ms_mean": round(float(np.mean(step_ms)), 3), "step_ms_max": round(float(np.max(step_ms)), 3),
                "replans": len(planner.replan_ms), "fallback_replans": planner.fallbacks,
                "no_path_replans": planner.no_path})
    return row, np.array(ts), np.array(xyz)


def summarize(rows):
    s = scorer.summarize(rows)
    tt = [r["time_to_goal_s"] for r in rows if r["reached"]]
    s["p95_time_to_goal_s"] = round(float(np.percentile(tt, 95)), 2) if tt else None
    return s


# ---- plot ----

def _track_columns(xyz, step):
    """Resample a track at `step` m of horizontal arclength. Returns s, x, y, z arrays."""
    d = np.hypot(np.diff(xyz[:, 0]), np.diff(xyz[:, 1]))
    s = np.concatenate([[0.0], np.cumsum(d)])
    q = np.arange(0.0, s[-1] + 1e-9, step)
    return q, np.interp(q, s, xyz[:, 0]), np.interp(q, s, xyz[:, 1]), np.interp(q, s, xyz[:, 2])


def render(w, xyz3, xyz2, radius, px=4):
    res = world_z.RES
    # side view: curtain of the true geometry under the 3D track, x = horizontal arclength, y = z
    _, cx, cy, cz = _track_columns(xyz3, res)
    nz = int(round(w.zmax / res))
    zc = (np.arange(nz) + 0.5) * res
    pts = np.stack(np.broadcast_arrays(cx[:, None], cy[:, None], zc[None, :]), axis=-1)
    d = w.sdf(pts.reshape(-1, 3)).reshape(len(cx), nz)
    side = np.full((len(cx), nz, 3), 255, np.uint8)
    side[d < radius] = (205, 205, 205)
    side[d <= res / 2] = (60, 60, 60)
    side = np.repeat(np.repeat(side, px, 0), px, 1)

    def dot(img, i, j, color, r):
        for a in range(-r, r + 1):
            for b in range(-r, r + 1):
                if a * a + b * b <= r * r and 0 <= i + a < img.shape[0] and 0 <= j + b < img.shape[1]:
                    img[i + a, j + b] = color

    for k in range(len(cx)):
        dot(side, int((k + 0.5) * px), int(cz[k] / res * px), (30, 90, 220), 1)
    dot(side, 0, int(cz[0] / res * px), (0, 170, 0), 6)
    dot(side, side.shape[0] - 1, int(cz[-1] / res * px), (220, 0, 0), 6)
    side = np.flipud(np.transpose(side, (1, 0, 2)))
    # top view: dark = blocks the 2.5D band, light = only above or below it
    g3 = w.grid.occ.any(axis=2)
    g2 = w.slice_2d(*CFG["band_2d"]).occ
    top = np.full(g3.shape + (3,), 255, np.uint8)
    top[g3] = (175, 175, 175)
    top[g2] = (60, 60, 60)
    top = np.repeat(np.repeat(top, 3, 0), 3, 1)
    s = 3 / res
    for tr, color in ((xyz2, (255, 140, 0)), (xyz3, (30, 90, 220))):
        for p in tr[::5]:
            dot(top, int((p[0] - w.xmin) * s), int((p[1] - w.ymin) * s), color, 1)
    dot(top, int(-w.xmin * s), int(-w.ymin * s), (0, 170, 0), 6)
    dot(top, int((w.goal[0] - w.xmin) * s), int((w.goal[1] - w.ymin) * s), (220, 0, 0), 6)
    top = np.flipud(np.transpose(top, (1, 0, 2)))
    W = max(side.shape[1], top.shape[1])
    pad = lambda im: np.concatenate([im, np.full((im.shape[0], W - im.shape[1], 3), 255, np.uint8)], axis=1)
    return np.concatenate([pad(side), np.full((8, W, 3), 255, np.uint8), pad(top)], axis=0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=arena_run.RESULTS)
    a = ap.parse_args(argv)
    cmd = "python run_z.py " + " ".join(argv if argv is not None else sys.argv[1:])
    radius = CFG["vehicle"]["radius"]
    t_all = time.perf_counter()
    rows = {m: [] for m in MODES}
    plan = {m: {"ms": [], "setup_ms": [], "expansions": []} for m in MODES}
    traces, layouts = [], []
    for i in range(a.layouts):
        w = world_z.make_world("window_bar", a.seed, i, radius=radius)
        band = w.slice_2d(*CFG["band_2d"])
        passable = world_z.passable_2d(band, radius, (0.0, 0.0), w.goal[:2])
        layouts.append({"index": i, "elements": w.elements, "band_2d_passable": passable,
                        "n_boxes": len(w.boxes)})
        tr = {}
        for m in MODES:
            if m == "astar_esdf_3d":
                pl, grid = astar_esdf_3d.make(), w.grid
            else:
                pl, grid = astar_esdf.make(known_map=True), band
            row, _, xyz = run_one(pl, w, grid, a.seed, i)
            row["band_2d_passable"] = passable
            rows[m].append(row)
            plan[m]["ms"] += pl.replan_ms
            plan[m]["setup_ms"] += getattr(pl, "setup_ms", [])
            plan[m]["expansions"] += getattr(pl, "expansions", [])
            tr[m] = xyz
        traces.append((w, tr))
        print(i, [e["kind"] for e in w.elements], "2D-passable" if passable else "2D-blocked",
              {m: rows[m][-1]["outcome"] for m in MODES}, flush=True)
    wall = time.perf_counter() - t_all

    pct = lambda v: round(float(np.percentile(v, 95)), 2) if v else None
    med = lambda v: round(float(np.median(v)), 2) if v else None
    out = {"family": "window_bar", "seed": a.seed, "layouts": a.layouts, "input": "synthetic",
           "command": cmd, "config": CFG, "wall_s": round(wall, 1),
           "planner_constants": {"astar_esdf_3d": {k: v for k, v in vars(astar_esdf_3d).items()
                                                   if k.isupper() and isinstance(v, (int, float))}},
           "env": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                   "machine": platform.machine(), "system": platform.system()},
           "band_2d_passable_layouts": sum(l["band_2d_passable"] for l in layouts),
           "layouts_detail": layouts, "modes": {}}
    for m in MODES:
        p = plan[m]
        out["modes"][m] = {"summary": summarize(rows[m]),
                           "planning": {"replans": len(p["ms"]), "median_ms": med(p["ms"]), "p95_ms": pct(p["ms"]),
                                        "max_ms": round(max(p["ms"]), 2) if p["ms"] else None,
                                        "setup_median_ms": med(p["setup_ms"]),
                                        "expansions_median": med(p["expansions"]),
                                        "fallback_replans": sum(r["fallback_replans"] for r in rows[m]),
                                        "no_path_replans": sum(r["no_path_replans"] for r in rows[m])},
                           "runs": rows[m]}
    os.makedirs(a.out, exist_ok=True)
    stem = os.path.join(a.out, f"z_window_bar_{a.seed}")
    with open(stem + ".json", "w") as fh:
        json.dump(out, fh, indent=1)

    f = lambda v: "-" if v is None else f"{v}"
    n2 = out["band_2d_passable_layouts"]
    L = [f"`{cmd}` from samples/close-area-arena (synthetic: simulated layouts, vehicle and sensor), "
         f"wall {wall:.0f} s\n",
         f"Layouts where the 1.0 +- 0.15 m band has a 2D path A => B: {n2} of {a.layouts}.\n",
         "| planner | layouts | reached % | collision % | stuck % | timeout % | median time to goal s "
         "| p95 time to goal s | median min clearance m | replans | plan median ms | plan p95 ms "
         "| setup median ms | fallback replans | no-path replans |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODES:
        s, p = out["modes"][m]["summary"], out["modes"][m]["planning"]
        L.append(f"| {m} | {s['n']} | {f(s['reached_pct'])} | {f(s['collision_pct'])} | {f(s['stuck_pct'])} "
                 f"| {f(s['timeout_pct'])} | {f(s['median_time_to_goal_s'])} | {f(s['p95_time_to_goal_s'])} "
                 f"| {f(s['median_min_clearance_m'])} | {p['replans']} | {f(p['median_ms'])} | {f(p['p95_ms'])} "
                 f"| {f(p['setup_median_ms'])} | {p['fallback_replans']} | {p['no_path_replans']} |")
    # split by 2D passability
    L += ["", "Reached by layout class:", "", "| class | layouts | " + " | ".join(MODES) + " |",
          "|---|---|" + "---|" * len(MODES)]
    for name, want in (("band has a 2D path", True), ("band blocked (needs altitude)", False)):
        idx = [l["index"] for l in layouts if l["band_2d_passable"] == want]
        cells = [f"{sum(rows[m][i]['reached'] for i in idx)}" for m in MODES]
        L.append(f"| {name} | {len(idx)} | " + " | ".join(cells) + " |")
    L += ["", "Per run (outcome, min clearance m, z range flown m):", "",
          "| run | elements | band 2D path | " + " | ".join(MODES) + " |", "|---|---|---|" + "---|" * len(MODES)]
    for i, l in enumerate(layouts):
        el = ", ".join(f"window z {e['z_centre']}" if e["kind"] == "window" else
                       "bars z " + "/".join(str(z) for z in e["bar_z"]) for e in l["elements"])
        cells = [f"{rows[m][i]['outcome']} {rows[m][i]['min_clearance_m']} "
                 f"[{rows[m][i]['z_min_m']}, {rows[m][i]['z_max_m']}]" for m in MODES]
        L.append(f"| {i} | {el} | {'yes' if l['band_2d_passable'] else 'no'} | " + " | ".join(cells) + " |")
    k = next((i for i in range(a.layouts) if not rows[MODES[0]][i]["reached"] and rows[MODES[1]][i]["reached"]), 0)
    w, tr = traces[k]
    png = f"{stem}_run{k}.png"
    arena_run._png(png, render(w, tr[MODES[1]], tr[MODES[0]], radius))
    L += ["", f"Plot: [{os.path.basename(png)}]({os.path.basename(png)}), run {k} (first run where 2.5D "
          "did not reach B and 3D did). Top panel: side view, the true geometry under the 3D track "
          "(horizontal = distance along the track, vertical = height 0-3 m; dark = obstacle, grey = within "
          "0.15 m, blue = 3D height, green = A, red = B). Bottom panel: top view (dark = blocks the "
          "1.0 +- 0.15 m band, light grey = obstacle only above or below the band, orange = 2.5D track, "
          "blue = 3D track)."]
    with open(stem + ".md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    print(f"wrote {stem}.json, {stem}.md, {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
