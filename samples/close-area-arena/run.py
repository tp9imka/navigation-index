"""Run a planner over seeded layouts and score every run on truth.

python run.py --planner straight --layouts 20 --seed 0 [--family random|u_trap|narrow_gap] [--plot]

Writes results/<planner>_<family>_<seed>.json (per-run rows + summary) and .md (the table it
prints). --plot also writes results/<planner>_<family>_<seed>_run<k>.png (map, path, A, B).
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import platform
import struct
import sys
import time
import zlib

import numpy as np
import scipy

try:
    from . import scorer, world as world_mod
    from .adapter import SimAdapter
    from .sensors import RangeFan
    from .vehicle import HZ, Vehicle
except ImportError:
    import scorer
    import world as world_mod
    from adapter import SimAdapter
    from sensors import RangeFan
    from vehicle import HZ, Vehicle

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")

DEFAULTS = {
    "max_time_s": 60.0, "plan_hz": 10, "z0": 1.0,
    "vehicle": {"tau": 0.15, "a_max": 3.0, "v_max": 2.0, "radius": world_mod.RADIUS},
    "sensor": {"n_beams": 72, "fov": 2 * math.pi, "max_range": 6.0, "noise_std": 0.02, "dropout": 0.02},
}


def load_planner(name: str, **kw):
    if __package__:
        mod = importlib.import_module(f".planners.{name}", __package__)
    else:
        mod = importlib.import_module(f"planners.{name}")
    return mod.make(**kw)


def run_one(planner, w, seed: int, index: int, cfg: dict = DEFAULTS, pose_source=None) -> dict:
    """Fly one layout. Returns score fields plus the truth trace (t, xy)."""
    goal = (w.goal[0], w.goal[1], cfg["z0"])
    vk = cfg["vehicle"]
    veh = Vehicle(0.0, 0.0, cfg["z0"], yaw=math.atan2(goal[1], goal[0]), **vk)
    sensor = RangeFan(rng=np.random.default_rng([seed, index, 7]), **cfg["sensor"])
    ad = SimAdapter(w, veh, sensor, pose_source=pose_source)
    planner.reset()
    plan_hz = cfg["plan_hz"]
    if HZ % plan_hz:
        raise ValueError(f"plan_hz must divide {HZ}")
    ratio, pdt = HZ // plan_hz, 1.0 / plan_hz
    n_steps = int(round(cfg["max_time_s"] * HZ))
    lag = int(round(scorer.STUCK_WINDOW_S * HZ))
    grid = w.grid if getattr(planner, "uses_grid", False) else None
    radius = vk["radius"]
    ts = [0.0]
    xy = [(0.0, 0.0)]
    plan_ms = []
    max_pose_err = 0.0
    for k in range(n_steps):
        if k % ratio == 0:
            pose = ad.pose()
            truth = ad.truth()
            max_pose_err = max(max_pose_err, math.hypot(pose.x - truth.x, pose.y - truth.y))
            scan = ad.ranges()
            t0 = time.perf_counter()
            sp = planner.step(pose, scan, goal, grid, pdt)
            plan_ms.append((time.perf_counter() - t0) * 1e3)
            ad.send_setpoint(sp)
        ad.tick()
        px, py = float(veh.p[0]), float(veh.p[1])
        ts.append(veh.t)
        xy.append((px, py))
        # online stop conditions, same definitions as scorer.score (which recomputes them)
        if math.hypot(px - goal[0], py - goal[1]) <= scorer.GOAL_TOL:
            break
        if w.clearance(px, py) < radius:
            break
        if len(xy) > lag and math.hypot(px - xy[-1 - lag][0], py - xy[-1 - lag][1]) < scorer.STUCK_DIST:
            break
    res = scorer.score(ts, xy, w, goal, radius)
    res.update({
        "index": index,
        "layout_attempts": w.attempts,
        "n_obstacles": len(w.boxes) + len(w.cylinders),
        "goal": [round(goal[0], 3), round(goal[1], 3)],
        "max_pose_error_m": round(max_pose_err, 4),
        "planner_ms_mean": round(float(np.mean(plan_ms)), 4),
        "planner_ms_max": round(float(np.max(plan_ms)), 4),
    })
    return res, np.array(ts), np.array(xy)


def evaluate(make_planner, family: str = "random", layouts: int = 20, seed: int = 0,
             cfg: dict = DEFAULTS, make_pose_source=None, keep_traces: bool = False):
    """Programmatic entry for later jobs. make_planner() -> Planner, called fresh per layout.
    make_pose_source(world, seed, index) -> PoseSource or None, also fresh per layout."""
    rows, traces = [], []
    for i in range(layouts):
        w = world_mod.make_world(family, seed, i, radius=cfg["vehicle"]["radius"])
        ps = make_pose_source(w, seed, i) if make_pose_source else None
        row, t, xy = run_one(make_planner(), w, seed, i, cfg, ps)
        rows.append(row)
        if keep_traces:
            traces.append((w, t, xy))
    return rows, scorer.summarize(rows), traces


def table(planner: str, family: str, s: dict) -> str:
    f = lambda v: "-" if v is None else f"{v}"
    return ("| planner | family | layouts | reached % | collision % | stuck % | timeout % "
            "| median time to goal s | median min clearance m |\n"
            "|---|---|---|---|---|---|---|---|---|\n"
            f"| {planner} | {family} | {s['n']} | {f(s['reached_pct'])} | {f(s['collision_pct'])} "
            f"| {f(s['stuck_pct'])} | {f(s['timeout_pct'])} | {f(s['median_time_to_goal_s'])} "
            f"| {f(s['median_min_clearance_m'])} |")


def runs_table(rows: list[dict]) -> str:
    out = ["| run | obstacles | outcome | time to goal s | min clearance m | path m |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['index']} | {r['n_obstacles']} | {r['outcome']} | "
                   f"{'-' if r['time_to_goal_s'] is None else r['time_to_goal_s']} | "
                   f"{r['min_clearance_m']} | {r['path_length_m']} |")
    return "\n".join(out)


# ---- PNG without matplotlib (zlib + struct) ----

def _png(path: str, rgb: np.ndarray) -> None:
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[r].astype(np.uint8).tobytes() for r in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def plot_run(path: str, w, xy: np.ndarray, row: dict, radius: float, px_per_cell: int = 4) -> None:
    g = w.grid
    infl = g.inflated(radius)
    img = np.full(g.occ.shape + (3,), 255, np.uint8)
    img[infl] = (205, 205, 205)
    img[g.occ] = (60, 60, 60)
    img = np.repeat(np.repeat(img, px_per_cell, 0), px_per_cell, 1)   # [ix, iy] pixels
    s = px_per_cell / g.res

    def put(x, y, color, r_px=1):
        cx, cy = (x - g.x0) * s, (y - g.y0) * s
        ix0, iy0 = int(cx), int(cy)
        for dx in range(-r_px, r_px + 1):
            for dy in range(-r_px, r_px + 1):
                if dx * dx + dy * dy <= r_px * r_px:
                    i, j = ix0 + dx, iy0 + dy
                    if 0 <= i < img.shape[0] and 0 <= j < img.shape[1]:
                        img[i, j] = color

    for (x0, y0), (x1, y1) in zip(xy[:-1], xy[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) * s * 2))
        for k in range(n + 1):
            put(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n, (30, 90, 220), 1)
    put(0.0, 0.0, (0, 170, 0), int(0.3 * s))                       # A, disc = goal tolerance size
    put(w.goal[0], w.goal[1], (220, 0, 0), int(0.3 * s))          # B
    end = {"collision": (255, 0, 255), "stuck": (255, 140, 0), "timeout": (120, 0, 160)}.get(row["outcome"])
    if end:
        put(xy[-1, 0], xy[-1, 1], end, int(0.2 * s))
    _png(path, np.flipud(np.transpose(img, (1, 0, 2))))           # rows = y down, so +y is up


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--planner", default="straight")
    ap.add_argument("--layouts", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--family", default="random", choices=world_mod.FAMILIES)
    ap.add_argument("--plot", action="store_true", help="write a PNG of one run")
    ap.add_argument("--plot-index", type=int, default=0)
    ap.add_argument("--out", default=RESULTS)
    a = ap.parse_args(argv)

    t0 = time.perf_counter()
    rows, summ, traces = evaluate(lambda: load_planner(a.planner), a.family, a.layouts, a.seed,
                                  keep_traces=a.plot)
    wall = time.perf_counter() - t0
    tab = table(a.planner, a.family, summ)
    print(tab)
    print(f"\nwall {wall:.1f} s for {a.layouts} layouts")
    os.makedirs(a.out, exist_ok=True)
    stem = os.path.join(a.out, f"{a.planner}_{a.family}_{a.seed}")
    cmd = "python run.py " + " ".join(argv if argv is not None else sys.argv[1:])
    with open(stem + ".json", "w") as fh:
        json.dump({
            "planner": a.planner, "family": a.family, "seed": a.seed, "layouts": a.layouts,
            "input": "synthetic", "command": cmd, "config": DEFAULTS, "summary": summ,
            "wall_s": round(wall, 2),
            "env": {"python": platform.python_version(), "numpy": np.__version__,
                    "scipy": scipy.__version__, "machine": platform.machine(),
                    "system": platform.system()},
            "runs": rows,
        }, fh, indent=1)
    with open(stem + ".md", "w") as fh:
        fh.write(f"`{cmd}` (synthetic), wall {wall:.1f} s\n\n{tab}\n\n{runs_table(rows)}\n")
    print(f"wrote {stem}.json, {stem}.md")
    if a.plot:
        k = min(max(a.plot_index, 0), len(traces) - 1)
        w, _, xy = traces[k]
        png = f"{stem}_run{k}.png"
        plot_run(png, w, xy, rows[k], DEFAULTS["vehicle"]["radius"])
        print(f"wrote {png} (run {k}: {rows[k]['outcome']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
