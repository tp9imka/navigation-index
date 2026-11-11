"""Baseline grid planner: A* on an inflated occupancy grid with an ESDF clearance cost.

make(known_map=True)  => plans on the arena's prior 0.1 m OccGrid (upper bound, uses_grid=True).
make(known_map=False) => builds its own log-odds grid from RangeScan hits only (unknown / free /
                         occupied, free space ray-traced) and treats unknown cells as traversable
                         with a cost penalty. A beam the sensor flags dropped adds nothing
                         (loop-88, SKIP_DROPPED_BEAMS); a beam with no return is traced free.

Every replan (REPLAN_PERIOD_S, plus at once when a newly seen obstacle touches the current
path):
  1. ESDF = scipy distance_transform_edt over occupied cells (unknown counts as not occupied).
  2. Blocked = ESDF <= RADIUS + TRACK_MARGIN. If A* finds no path, retry once with RADIUS only
     (the arena guarantees a 4-connected path at that inflation on the true grid).
  3. 8-connected A*, step cost = length * (1 + CLEARANCE_WEIGHT * max(0, 1 - esdf / CLEARANCE_SOFT_M)
     + UNKNOWN_PENALTY if the cell is unknown). Octile heuristic (admissible: cost >= length).
  4. Line-of-sight shortcut: jump from waypoint i to the farthest j whose straight segment keeps
     the clearance of the A* sub-path it replaces (capped at SHORTCUT_CLEAR_M), so shortcutting
     does not undo the clearance cost.
Between replans: carrot follower. The carrot is LOOKAHEAD_M ahead along the path from the
closest path point, pulled back to as little as LOOKAHEAD_MIN_M when the straight chord to it
would pass closer than CARROT_CLEAR_M to an occupied cell; speed = V_CRUISE scaled by the minimum ESDF between vehicle and carrot
(V_MIN_FRAC at V_CLEAR_STOP_M, full at V_CLEAR_FULL_M) and capped by K_GOAL * distance to B.

Run the comparison (50 layouts, seed 0, three families, straight + both modes):
    cd samples/close-area-arena && .venv/bin/python -m planners.astar_esdf --layouts 50 --seed 0
"""
from __future__ import annotations

import heapq
import math
import time

import numpy as np
from scipy.ndimage import distance_transform_edt

try:
    from ..adapter import Setpoint
    from .base import Planner
except ImportError:
    from adapter import Setpoint
    from planners.base import Planner

# ---- vehicle and inflation ----
RADIUS = 0.15                 # m, vehicle radius (CONTRACT.md)
TRACK_MARGIN = 0.10           # m, extra inflation for carrot tracking error
# ---- costs ----
CLEARANCE_WEIGHT = 4.0        # extra cost per metre at zero clearance
CLEARANCE_SOFT_M = 1.0        # m, ESDF above which the clearance cost is zero
UNKNOWN_PENALTY = 1.0         # extra cost per metre through an unknown cell (known_map=False)
SHORTCUT_CLEAR_M = 0.6        # m, a shortcut segment must keep min(this, sub-path clearance)
# ---- replanning ----
REPLAN_PERIOD_S = 0.4         # s => 2.5 Hz; a blocked path triggers an immediate replan
# ---- follower ----
LOOKAHEAD_M = 0.8             # m, carrot distance along the path
LOOKAHEAD_MIN_M = 0.2         # m, shortest carrot distance when the chord is tight
LOOKAHEAD_STEP_M = 0.1        # m, pull-back step
CARROT_CLEAR_M = RADIUS + TRACK_MARGIN   # m, ESDF the chord vehicle => carrot must keep
V_CRUISE = 1.5                # m/s
V_CLEAR_STOP_M = 0.25         # m, ESDF at which speed is V_MIN_FRAC * V_CRUISE
V_CLEAR_FULL_M = 1.0          # m, ESDF at which speed is V_CRUISE
V_MIN_FRAC = 0.2              # speed fraction at or below V_CLEAR_STOP_M
K_GOAL = 1.0                  # 1/s, speed cap = K_GOAL * distance to B
K_YAW = 1.5                   # 1/s, yaw towards the travel direction
# ---- mapping (known_map=False) ----
MAP_X0, MAP_Y0 = -2.5, -2.5   # m, operating-area prior (geofence) in the local frame
MAP_SIZE_M = 24.0             # m, square side; outside counts as occupied
MAP_RES = 0.1                 # m, same as the arena grid
LO_HIT, LO_MISS = 0.9, 0.4    # log-odds increment for a hit, decrement for a pass-through
LO_MIN, LO_MAX = -2.0, 3.5    # log-odds clamp
LO_OCC, LO_FREE = 0.5, -0.3   # occupied above, free below, unknown between
SKIP_DROPPED_BEAMS = False    # True: a beam the sensor flags dropped (scan.dropped) adds nothing to the map.
                              # Off until the benchmark is regenerated with it (loop-88c), so the published
                              # numbers match the code; False traces a dropped beam free to max_range.
NO_RETURN_FREE_TO_MAX_RANGE = True   # a measured beam with no return clears free space out to max_range
                                     # (False = option A of loop-85: such a beam adds nothing either)
NO_TRACE_REACH = -1.0         # m, free-space reach of a beam that adds nothing: below every sample (r >= 0)

SQRT2 = math.sqrt(2.0)


def astar(blocked: np.ndarray, cost: np.ndarray, start: tuple[int, int], goal: tuple[int, int]):
    """8-connected A* on cell grids [ix, iy]. cost >= 1 per cell (multiplies step length).
    Returns a list of (ix, iy) from start to goal, or None."""
    nx, ny = blocked.shape
    blk = blocked.ravel().tolist()
    cst = cost.ravel().tolist()
    s = start[0] * ny + start[1]
    g = goal[0] * ny + goal[1]
    gx, gy = goal
    if blk[g]:
        return None
    nbrs = [(-ny - 1, -1, -1, SQRT2), (-ny, -1, 0, 1.0), (-ny + 1, -1, 1, SQRT2), (-1, 0, -1, 1.0),
            (1, 0, 1, 1.0), (ny - 1, 1, -1, SQRT2), (ny, 1, 0, 1.0), (ny + 1, 1, 1, SQRT2)]
    gscore = {s: 0.0}
    parent = {s: -1}
    closed = set()
    heap = [(0.0, 0.0, s)]
    push, pop = heapq.heappush, heapq.heappop
    while heap:
        _, gc, u = pop(heap)
        if u == g:
            path = []
            while u != -1:
                path.append(divmod(u, ny))
                u = parent[u]
            return path[::-1]
        if u in closed:
            continue
        closed.add(u)
        ux, uy = divmod(u, ny)
        for off, dx, dy, ln in nbrs:
            vx, vy = ux + dx, uy + dy
            if vx < 0 or vy < 0 or vx >= nx or vy >= ny:
                continue
            v = u + off
            if blk[v] or v in closed:
                continue
            ng = gc + ln * cst[v]
            if ng < gscore.get(v, math.inf):
                gscore[v] = ng
                parent[v] = u
                ax, ay = abs(vx - gx), abs(vy - gy)
                h = (ax + ay) + (SQRT2 - 2.0) * min(ax, ay)
                push(heap, (ng + h * 1.0001, ng, v))      # tiny tie-break towards the goal
    return None


def _segment_cells(a, b):
    """Cells sampled every half cell on the segment between cells a and b (inclusive)."""
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
    t = np.linspace(0.0, 1.0, n + 1)
    xs = np.rint(a[0] + (b[0] - a[0]) * t).astype(int)
    ys = np.rint(a[1] + (b[1] - a[1]) * t).astype(int)
    return xs, ys


def shortcut(path, esdf: np.ndarray, blocked: np.ndarray):
    """Greedy line-of-sight shortcut that keeps the clearance of the replaced sub-path."""
    if len(path) <= 2:
        return list(path)
    pe = np.array([esdf[c] for c in path])
    out = [path[0]]
    i, n = 0, len(path)
    while i < n - 1:
        j_ok = i + 1
        for j in range(n - 1, i + 1, -1):
            need = min(SHORTCUT_CLEAR_M, float(pe[i:j + 1].min()))
            xs, ys = _segment_cells(path[i], path[j])
            if not blocked[xs, ys].any() and esdf[xs, ys].min() >= need - 1e-9:
                j_ok = j
                break
        out.append(path[j_ok])
        i = j_ok
    return out


class LogOddsMap:
    """Occupancy from range hits only. Unknown until observed."""

    def __init__(self):
        n = int(round(MAP_SIZE_M / MAP_RES))
        self.lo = np.zeros((n, n), np.float32)
        self.res, self.x0, self.y0 = MAP_RES, MAP_X0, MAP_Y0

    def update(self, pose, scan) -> np.ndarray:
        """Integrate one scan. Returns (k, 2) indices of cells that became occupied.

        A hit clears free space up to a cell short of the hit. A beam with no return (inf) clears
        free space out to max_range (NO_RETURN_FREE_TO_MAX_RANGE), except a beam the sensor flags
        dropped (scan.dropped, sensors.RangeScanDrops), which adds nothing (SKIP_DROPPED_BEAMS).
        Scans without the flag (real drivers) treat every inf as no return."""
        n = self.lo.shape[0]
        ang = pose.yaw + np.asarray(scan.angles)
        d = np.asarray(scan.distances, float)
        hit = np.isfinite(d)
        reach = np.where(hit, d - self.res, scan.max_range)     # free space stops a cell short
        if not NO_RETURN_FREE_TO_MAX_RANGE:
            reach = np.where(hit, reach, NO_TRACE_REACH)
        dropped = getattr(scan, "dropped", None)
        if SKIP_DROPPED_BEAMS and dropped is not None:
            drop = np.asarray(dropped, bool)
            if drop.shape != d.shape:
                raise ValueError(f"scan.dropped has {drop.size} flags for {d.size} beams")
            reach = np.where(drop, NO_TRACE_REACH, reach)
            hit = hit & ~drop       # sensors write inf for a dropped beam; a flagged beam never counts as a hit
        ca, sa = np.cos(ang), np.sin(ang)
        step = self.res / 2
        k = np.arange(int(scan.max_range / step) + 1) * step
        r = k[None, :]
        m = r < reach[:, None]
        fx = (pose.x + r * ca[:, None] - self.x0) / self.res
        fy = (pose.y + r * sa[:, None] - self.y0) / self.res
        fi = np.floor(fx[m]).astype(int)
        fj = np.floor(fy[m]).astype(int)
        hx = np.floor((pose.x + d[hit] * ca[hit] - self.x0) / self.res).astype(int)
        hy = np.floor((pose.y + d[hit] * sa[hit] - self.y0) / self.res).astype(int)
        ok = (hx >= 0) & (hy >= 0) & (hx < n) & (hy < n)
        hx, hy = hx[ok], hy[ok]
        okf = (fi >= 0) & (fj >= 0) & (fi < n) & (fj < n)
        free = np.unique(fi[okf] * n + fj[okf])
        hits = np.unique(hx * n + hy)
        free = np.setdiff1d(free, hits, assume_unique=True)
        flat = self.lo.ravel()
        was_occ = flat[hits] > LO_OCC
        flat[free] = np.maximum(flat[free] - LO_MISS, LO_MIN)
        flat[hits] = np.minimum(flat[hits] + LO_HIT, LO_MAX)
        new = hits[(~was_occ) & (flat[hits] > LO_OCC)]
        return np.stack(divmod(new, n), axis=1) if len(new) else np.zeros((0, 2), int)

    def occupied(self) -> np.ndarray:
        return self.lo > LO_OCC

    def unknown(self) -> np.ndarray:
        return (self.lo <= LO_OCC) & (self.lo >= LO_FREE)


class AStarESDF(Planner):
    name = "astar_esdf"

    def __init__(self, known_map: bool = True):
        self.known_map = known_map
        self.uses_grid = known_map
        self.name = "astar_esdf_known" if known_map else "astar_esdf_unknown"
        self.replan_ms: list[float] = []      # kept across runs of this instance
        self.fallbacks = 0                    # replans that needed RADIUS-only inflation
        self.no_path = 0                      # replans with no path at either inflation
        self.reset()

    def reset(self) -> None:
        self.map = None if self.known_map else LogOddsMap()
        self.path_xy = None                   # (k, 2) waypoints after shortcutting
        self.dense_xy = None                  # (m, 2) samples along the path for block checks
        self.esdf = None
        self.static = None                    # (occ, esdf) cache for the known map
        self.last_plan_t = -math.inf
        self.geo = None                       # (res, x0, y0, nx, ny)

    # ---- map views ----
    def _layers(self, grid):
        if self.known_map:
            if self.static is None:
                padded = np.pad(grid.occ, 1, constant_values=True)
                esdf = (distance_transform_edt(~padded) * grid.res)[1:-1, 1:-1]
                self.static = (np.zeros_like(grid.occ), esdf)
                self.geo = (grid.res, grid.x0, grid.y0) + grid.occ.shape
            return self.static
        occ = self.map.occupied()
        padded = np.pad(occ, 1, constant_values=True)
        esdf = (distance_transform_edt(~padded) * self.map.res)[1:-1, 1:-1]
        self.geo = (self.map.res, self.map.x0, self.map.y0) + occ.shape
        return self.map.unknown(), esdf

    def _idx(self, x, y):
        res, x0, y0, nx, ny = self.geo
        return (min(max(int((x - x0) // res), 0), nx - 1), min(max(int((y - y0) // res), 0), ny - 1))

    def _xy(self, c):
        res, x0, y0, _, _ = self.geo
        return x0 + (c[0] + 0.5) * res, y0 + (c[1] + 0.5) * res

    # ---- planning ----
    def _plan(self, pose, goal, grid):
        t0 = time.perf_counter()
        unknown, esdf = self._layers(grid)
        self.esdf = esdf
        cost = 1.0 + CLEARANCE_WEIGHT * np.clip(1.0 - esdf / CLEARANCE_SOFT_M, 0.0, None)
        cost = cost + UNKNOWN_PENALTY * unknown
        g = self._idx(goal[0], goal[1])
        path = blocked = None
        for k, infl in enumerate((RADIUS + TRACK_MARGIN, RADIUS)):
            blocked = esdf <= infl + 1e-9
            s = self._idx(pose.x, pose.y)
            if blocked[s]:                    # inside the inflation: start from the nearest free cell
                free = np.argwhere(~blocked)
                if not len(free):
                    continue
                dd = np.hypot(free[:, 0] - s[0], free[:, 1] - s[1])
                s = tuple(int(v) for v in free[int(np.argmin(dd))])
            path = astar(blocked, cost, s, g)
            if path is not None:
                self.fallbacks += k
                break
        if path is None:
            self.no_path += 1
            self.path_xy = self.dense_xy = None
        else:
            sc = shortcut(path, esdf, blocked)
            self.path_xy = np.array([self._xy(c) for c in sc])
            self.path_xy[-1] = goal[:2]
            self.dense_xy = np.array([self._xy(c) for c in path])
        self.replan_ms.append((time.perf_counter() - t0) * 1e3)

    def _blocked_by(self, new_cells) -> bool:
        if self.dense_xy is None or not len(new_cells):
            return False
        res, x0, y0, _, _ = self.geo
        c = np.column_stack([x0 + (new_cells[:, 0] + 0.5) * res, y0 + (new_cells[:, 1] + 0.5) * res])
        d = np.hypot(self.dense_xy[:, None, 0] - c[None, :, 0], self.dense_xy[:, None, 1] - c[None, :, 1])
        return bool(d.min() <= RADIUS + TRACK_MARGIN)

    # ---- following ----
    def _carrot(self, px, py):
        """Carrot at LOOKAHEAD_M along the path, pulled back (LOOKAHEAD_STEP_M at a time, down to
        LOOKAHEAD_MIN_M) while the chord vehicle => carrot has less ESDF than CARROT_CLEAR_M (or
        than the vehicle's own ESDF, if that is lower). Stops the carrot cutting gap corners."""
        here = self._min_esdf((px, py), (px, py))
        need = min(CARROT_CLEAR_M, here)
        look = LOOKAHEAD_M
        while True:
            c = self._carrot_at(px, py, look)
            if look <= LOOKAHEAD_MIN_M or self._min_esdf((px, py), c) >= need - 1e-9:
                return c
            look -= LOOKAHEAD_STEP_M

    def _carrot_at(self, px, py, look):
        P = self.path_xy
        if len(P) == 1:
            return P[0]
        a, b = P[:-1], P[1:]
        ab = b - a
        L = np.maximum((ab ** 2).sum(1), 1e-12)
        t = np.clip(((px - a[:, 0]) * ab[:, 0] + (py - a[:, 1]) * ab[:, 1]) / L, 0, 1)
        q = a + t[:, None] * ab
        i = int(np.argmin(np.hypot(q[:, 0] - px, q[:, 1] - py)))
        left, pt = look, q[i]
        while i < len(P) - 1:
            seg = math.hypot(*(P[i + 1] - pt))
            if seg >= left:
                return pt + (P[i + 1] - pt) * (left / max(seg, 1e-9))
            left -= seg
            pt, i = P[i + 1], i + 1
        return P[-1]

    def _min_esdf(self, p0, p1) -> float:
        res, x0, y0, nx, ny = self.geo
        n = int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / (res / 2)) + 2
        t = np.linspace(0, 1, n)
        xi = np.clip(((p0[0] + (p1[0] - p0[0]) * t - x0) // res).astype(int), 0, nx - 1)
        yi = np.clip(((p0[1] + (p1[1] - p0[1]) * t - y0) // res).astype(int), 0, ny - 1)
        return float(self.esdf[xi, yi].min())

    def step(self, pose, scan, goal, grid, dt):
        new_occ = np.zeros((0, 2), int)
        if not self.known_map:
            new_occ = self.map.update(pose, scan)
        due = pose.t - self.last_plan_t >= REPLAN_PERIOD_S - 1e-9
        if due or self.path_xy is None or self._blocked_by(new_occ):
            self._plan(pose, goal, grid)
            self.last_plan_t = pose.t
        if self.path_xy is None:
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        dist_goal = math.hypot(ex, ey)
        c = self._carrot(pose.x, pose.y)
        cx, cy = c[0] - pose.x, c[1] - pose.y
        dc = math.hypot(cx, cy)
        if dc < 1e-6:
            return Setpoint(0.0, 0.0, 0.0, 0.0)
        clr = self._min_esdf((pose.x, pose.y), c)
        frac = (clr - V_CLEAR_STOP_M) / (V_CLEAR_FULL_M - V_CLEAR_STOP_M)
        speed = V_CRUISE * min(1.0, max(V_MIN_FRAC, frac))
        speed = min(speed, K_GOAL * dist_goal)
        h = math.atan2(cy, cx)
        yaw_err = (h - pose.yaw + math.pi) % (2 * math.pi) - math.pi
        return Setpoint(speed * cx / dc, speed * cy / dc, 0.0, K_YAW * yaw_err)


def make(**kw) -> Planner:
    return AStarESDF(**kw)


# ---- comparison driver: python -m planners.astar_esdf ----

def _render(w, xy, row, path_xy, radius, px=3):
    g = w.grid
    img = np.full(g.occ.shape + (3,), 255, np.uint8)
    img[g.inflated(radius)] = (205, 205, 205)
    img[g.occ] = (60, 60, 60)
    img = np.repeat(np.repeat(img, px, 0), px, 1)
    s = px / g.res

    def put(x, y, color, r):
        i0, j0 = int((x - g.x0) * s), int((y - g.y0) * s)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r and 0 <= i0 + dx < img.shape[0] and 0 <= j0 + dy < img.shape[1]:
                    img[i0 + dx, j0 + dy] = color

    def line(pts, color):
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) * s * 2))
            for k in range(n + 1):
                put(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n, color, 0)

    if path_xy is not None:
        line(path_xy, (0, 170, 0))
    line(xy, (30, 90, 220))
    put(0.0, 0.0, (0, 170, 0), int(0.3 * s))
    put(w.goal[0], w.goal[1], (220, 0, 0), int(0.3 * s))
    end = {"collision": (255, 0, 255), "stuck": (255, 140, 0), "timeout": (120, 0, 160)}.get(row["outcome"])
    if end:
        put(xy[-1, 0], xy[-1, 1], end, int(0.2 * s))
    return np.flipud(np.transpose(img, (1, 0, 2)))


def main(argv=None) -> int:
    import argparse
    import json
    import os
    import platform
    import sys
    import scipy
    try:
        from .. import run as arena_run
        from . import straight
    except ImportError:
        import run as arena_run
        from planners import straight

    ap = argparse.ArgumentParser()
    ap.add_argument("--layouts", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--families", default="random,u_trap,narrow_gap")
    a = ap.parse_args(argv)
    cmd = "python -m planners.astar_esdf " + " ".join(argv if argv is not None else sys.argv[1:])
    os.makedirs(arena_run.RESULTS, exist_ok=True)
    radius = arena_run.DEFAULTS["vehicle"]["radius"]
    consts = {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float))}

    for fam in a.families.split(","):
        out = {"family": fam, "seed": a.seed, "layouts": a.layouts, "input": "synthetic",
               "command": cmd, "config": arena_run.DEFAULTS, "planner_constants": consts,
               "env": {"python": platform.python_version(), "numpy": np.__version__,
                       "scipy": scipy.__version__, "machine": platform.machine(),
                       "system": platform.system()},
               "modes": {}}
        traces, tables, keep = {}, [], {}
        for mode in ("straight", "known", "unknown"):
            made = []

            def factory(mode=mode, made=made):
                p = straight.make() if mode == "straight" else AStarESDF(known_map=(mode == "known"))
                made.append(p)
                return p

            t0 = time.perf_counter()
            rows, summ, tr = arena_run.evaluate(factory, fam, a.layouts, a.seed, keep_traces=True)
            wall = time.perf_counter() - t0
            name = "straight" if mode == "straight" else f"astar_esdf {mode}_map"
            ms = [m for p in made for m in getattr(p, "replan_ms", [])]
            for r, p in zip(rows, made):
                if hasattr(p, "replan_ms"):
                    r["replans"] = len(p.replan_ms)
                    r["fallback_replans"] = p.fallbacks
                    r["no_path_replans"] = p.no_path
            plan = {"replans": len(ms),
                    "median_ms": round(float(np.median(ms)), 2) if ms else None,
                    "p95_ms": round(float(np.percentile(ms, 95)), 2) if ms else None,
                    "max_ms": round(float(np.max(ms)), 2) if ms else None,
                    "fallback_replans": sum(getattr(p, "fallbacks", 0) for p in made),
                    "no_path_replans": sum(getattr(p, "no_path", 0) for p in made)}
            out["modes"][name] = {"summary": summ, "planning": plan, "wall_s": round(wall, 1), "runs": rows}
            traces[name], keep[name] = tr, made
            print(f"{fam} {name}: {summ} plan {plan} wall {wall:.1f} s", flush=True)

        stem = os.path.join(arena_run.RESULTS, f"astar_esdf_{fam}_{a.seed}")
        with open(stem + ".json", "w") as fh:
            json.dump(out, fh, indent=1)
        f = lambda v: "-" if v is None else f"{v}"
        lines = [f"`{cmd}` from samples/close-area-arena (synthetic: simulated layouts, vehicle and sensor)\n",
                 "| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s "
                 "| median min clearance m | replans | plan median ms | plan p95 ms | fallback replans | no-path replans | wall s |",
                 "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, m in out["modes"].items():
            s, p = m["summary"], m["planning"]
            lines.append(f"| {name} | {fam} | {s['n']} | {f(s['reached_pct'])} | {f(s['collision_pct'])} | "
                         f"{f(s['stuck_pct'])} | {f(s['timeout_pct'])} | {f(s['median_time_to_goal_s'])} | "
                         f"{f(s['median_min_clearance_m'])} | {p['replans']} | {f(p['median_ms'])} | "
                         f"{f(p['p95_ms'])} | {p['fallback_replans']} | {p['no_path_replans']} | {m['wall_s']} |")
        names = list(out["modes"])
        lines += ["", "Per run (outcome, min clearance m):", "",
                  "| run | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
        for i in range(a.layouts):
            cells = [f"{out['modes'][n]['runs'][i]['outcome']} {out['modes'][n]['runs'][i]['min_clearance_m']}"
                     for n in names]
            lines.append(f"| {i} | " + " | ".join(cells) + " |")
        unk = out["modes"]["astar_esdf unknown_map"]["runs"]
        k = next((r["index"] for r in unk if r["outcome"] != "reached"), 0)
        panels = []
        for name in names:
            w, _, xy = traces[name][k]
            pl = keep[name][k]
            panels.append(_render(w, xy, out["modes"][name]["runs"][k], getattr(pl, "path_xy", None), radius))
            panels.append(np.full((panels[-1].shape[0], 6, 3), 255, np.uint8))
        png = f"{stem}_run{k}.png"
        arena_run._png(png, np.concatenate(panels[:-1], axis=1))
        lines += ["", f"Plot: [{os.path.basename(png)}]({os.path.basename(png)}), run {k} (first run the "
                  "unknown-map mode did not reach B, else run 0). Panels left to right: " + ", ".join(names)
                  + ". Blue = truth path, green = last planned path, grey band = 0.15 m inflation, "
                  "orange = stuck, magenta = collision, purple = timeout."]
        with open(stem + ".md", "w") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"wrote {stem}.json, {stem}.md, {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
