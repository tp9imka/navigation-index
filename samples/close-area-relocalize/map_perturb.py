"""Imperfect prior maps for the relocalization runs (run_stalemap.py). Adds to the sample, edits nothing.

The world the sensor sees and the scorer scores ("real") and the grid the planner and the
relocalizer get ("map") are built separately. run.run_one hands `w.grid` to a known-map planner
and ray-casts / scores against the exact geometry of `w`, so a real World whose `.grid` is the
stale map is all the arena needs.

Rungs (base = world.make_world("random", seed, index), the layout the team was given):

  a_exact     real = base, map = base grid (the README headline case)
  b_removed   1-2 mapped obstacles are gone in reality (map has phantoms). Picked among the
              obstacles within REMOVE_NEAR_M of the nominal path, so the vehicle sees the gap
  c_added     1-2 unmapped obstacles in reality (box half sizes U(0.25, 0.75) m or cylinder
              r U(0.2, 0.5) m), surface ADD_GAP_M = U(0.45, 1.5) m from the nominal path,
              not touching a mapped obstacle or wall, >= 1 m from A and B. They do not block the
              nominal path (else every arm hits them: the known-map planner ignores scans), but
              they are where scans and 1-2 m disambiguating moves reach. Nominal path = the
              truth trace the known-map A* flies on the base layout with the truth pose, so the
              truth arm never hits them by construction (a selection, stated in the results)
  d_shift01   every obstacle (not the walls) moved 0.1 m in its own random direction
  d_shift02   same, 0.2 m ("furniture moved between runs", Day-1 intake Q7 default)
  e_selfmap   built in run_stalemap.py: map = log-odds grid of the unknown-map A* after an
              outbound A => B leg on the VIO-like estimator (no fault, dark zones on); see
              selfmap_grids() and shift_world()

Every perturbed real world keeps a 4-connected free path A => B at the vehicle radius (same
guarantee as world.make_world), resampled up to MAX_TRIES times. Seeds: [seed, index, 5500 + rung].
"""
from __future__ import annotations

import math

import numpy as np

from arena import astar_esdf, run, world

RUNGS = ("a_exact", "b_removed", "c_added", "d_shift01", "d_shift02", "e_selfmap")
_CODE = {r: k for k, r in enumerate(RUNGS)}
REMOVE_NEAR_M = 3.0
ADD_GAP_M = (0.45, 1.5)
ADD_END_KEEP_M = 1.5        # added obstacles sit along the path, not within this of A or B (path length)
MAX_TRIES = 300


# ---- shapes ----
def shapes(w):
    return [("box", (b.cx, b.cy, b.hx, b.hy)) for b in w.boxes] + [("cyl", (c.cx, c.cy, c.r)) for c in w.cylinders]


def shape_dist(shape, pts) -> np.ndarray:
    """Signed distance from points (N, 2) to one box or cylinder surface."""
    p = np.asarray(pts, float).reshape(-1, 2)
    kind, s = shape
    if kind == "box":
        q = np.abs(p - np.array(s[:2])) - np.array(s[2:])
        return np.linalg.norm(np.maximum(q, 0.0), axis=1) + np.minimum(q.max(axis=1), 0.0)
    return np.hypot(p[:, 0] - s[0], p[:, 1] - s[1]) - s[2]


def build(base, shp) -> world.World:
    """Real world with the given obstacle list; .grid is left to the caller (the map)."""
    return world.World(family=base.family, seed=base.seed, xmin=base.xmin, ymin=base.ymin,
                       xmax=base.xmax, ymax=base.ymax, goal=base.goal,
                       boxes=[world.Box(*s) for k, s in shp if k == "box"],
                       cylinders=[world.Cylinder(*s) for k, s in shp if k == "cyl"],
                       attempts=base.attempts)


def free_ok(w) -> bool:
    g = w.rasterize(world.RES)
    if w.clearance(0.0, 0.0) <= world.RADIUS or w.clearance(*w.goal) <= world.RADIUS:
        return False
    return world.bfs_free_path(g.inflated(world.RADIUS), g.to_index(0.0, 0.0), g.to_index(*w.goal)) is not None


def nominal_path(w, seed: int, index: int) -> np.ndarray:
    """Truth trace of planners/astar_esdf.py (known map, truth pose) flown A => B on the base layout,
    every 5th 50 Hz sample. The known-map planner ignores scans, so with the truth pose it flies this
    exact trace whatever is added off it: the truth arm cannot hit an obstacle placed clear of it."""
    _, _, xy = run.run_one(astar_esdf.make(known_map=True), w, seed, index, run.DEFAULTS, None)
    return xy[::5]


def changed_cells(map_grid, real) -> int:
    return int((map_grid.occ != real.rasterize(world.RES).occ).sum())


# ---- rungs a-d ----
def perturb(base, rung: str, seed: int, index: int):
    """(real World with .grid = map, info dict). Map is always base.grid for a-d."""
    rng = np.random.default_rng([seed, index, 5500 + _CODE[rung]])
    shp = shapes(base)
    info = {"rung": rung}
    if rung == "a_exact":
        real = build(base, shp)
    elif rung == "b_removed":
        path = nominal_path(base, seed, index)
        near = [k for k, s in enumerate(shp) if shape_dist(s, path).min() < REMOVE_NEAR_M] or list(range(len(shp)))
        n = min(int(rng.integers(1, 3)), len(near))
        drop = sorted(int(v) for v in rng.choice(near, size=n, replace=False))
        real = build(base, [s for k, s in enumerate(shp) if k not in drop])
        info.update({"removed": [shp[k] for k in drop], "near_candidates": len(near)})
    elif rung == "c_added":
        path = nominal_path(base, seed, index)
        seg = np.hypot(*np.diff(path, axis=0).T)
        s_along = np.concatenate([[0.0], np.cumsum(seg)])
        mid = np.flatnonzero((s_along > ADD_END_KEEP_M) & (s_along < s_along[-1] - ADD_END_KEEP_M))
        n = int(rng.integers(1, 3))
        added, tries = [], 0
        while len(added) < n and tries < MAX_TRIES:
            tries += 1
            j = int(rng.choice(mid))
            t = path[min(j + 1, len(path) - 1)] - path[max(j - 1, 0)]
            t = t / (np.hypot(*t) or 1.0)
            nrm = np.array([-t[1], t[0]]) * (1.0 if rng.random() < 0.5 else -1.0)
            gap = float(rng.uniform(*ADD_GAP_M))
            if rng.random() < 0.5:
                hx, hy = (float(v) for v in rng.uniform(0.25, 0.75, size=2))
                reach = float(np.hypot(hx, hy))
                c = path[j] + nrm * (gap + reach)
                cand = ("box", (float(c[0]), float(c[1]), hx, hy))
            else:
                r = float(rng.uniform(0.2, 0.5))
                reach = r
                c = path[j] + nrm * (gap + r)
                cand = ("cyl", (float(c[0]), float(c[1]), r))
            if shape_dist(cand, path).min() < ADD_GAP_M[0]:
                continue
            if base.clearance(*c) < reach + 0.1:                     # touches a mapped obstacle or wall
                continue
            if any(shape_dist(cand, [p]).min() < 1.0 for p in ((0.0, 0.0), base.goal)):
                continue
            if any(math.hypot(c[0] - a[1][0], c[1] - a[1][1]) < reach + 0.5 for a in added):
                continue
            if not free_ok(build(base, shp + added + [cand])):
                continue
            added.append(cand)
        real = build(base, shp + added)
        info.update({"added": added, "tries": tries,
                     "added_gap_m": [round(float(shape_dist(a, path).min()), 3) for a in added]})
    elif rung in ("d_shift01", "d_shift02"):
        step = 0.1 if rung == "d_shift01" else 0.2
        for tries in range(1, MAX_TRIES + 1):
            ang = rng.uniform(-math.pi, math.pi, size=len(shp))
            moved = []
            for (kind, s), a in zip(shp, ang):
                dx, dy = step * math.cos(a), step * math.sin(a)
                moved.append((kind, (s[0] + dx, s[1] + dy) + tuple(s[2:])))
            real = build(base, moved)
            if free_ok(real):
                break
        info.update({"shift_m": step, "tries": tries, "free_path": free_ok(real)})
    else:
        raise ValueError(rung)
    real.grid = base.grid
    info["changed_cells"] = changed_cells(base.grid, real)
    return real, info


# ---- rung e: self-built map ----
def shift_world(w, ox: float, oy: float, goal_xy) -> world.World:
    """Same geometry in a frame with origin (ox, oy) of the old frame; goal given in the old frame."""
    return world.World(family=w.family, seed=w.seed, xmin=w.xmin - ox, ymin=w.ymin - oy,
                       xmax=w.xmax - ox, ymax=w.ymax - oy, goal=(goal_xy[0] - ox, goal_xy[1] - oy),
                       boxes=[world.Box(b.cx - ox, b.cy - oy, b.hx, b.hy) for b in w.boxes],
                       cylinders=[world.Cylinder(c.cx - ox, c.cy - oy, c.r) for c in w.cylinders],
                       attempts=w.attempts)


def selfmap_layers(lo: np.ndarray):
    """(occupied, unknown) bool layers of a planners/astar_esdf.py LogOddsMap log-odds array."""
    return lo > astar_esdf.LO_OCC, (lo <= astar_esdf.LO_OCC) & (lo >= astar_esdf.LO_FREE)


def selfmap_grids(occ: np.ndarray, unk: np.ndarray, ox: float, oy: float):
    """Self-built layers => (match_grid, plan_grid), shifted by (ox, oy).
    match_grid: occupied cells only (what a scan can be matched against).
    plan_grid: occupied or unknown (fly only where the outbound leg saw free space)."""
    x0, y0 = astar_esdf.MAP_X0 - ox, astar_esdf.MAP_Y0 - oy
    res = astar_esdf.MAP_RES
    return world.OccGrid(occ.copy(), res, x0, y0), world.OccGrid(occ | unk, res, x0, y0)


def selfmap_stats(match_grid, real) -> dict:
    """Map vs real geometry (both in the return frame), over mapped occupied cells inside the area walls:
    phantom_frac = share of cell centres more than 0.2 m out in free space from any real surface
    (VIO drift or a bad hit); median_abs_sdf_m = median |distance| of cell centres to the real surface."""
    ix, iy = np.nonzero(match_grid.occ)
    xy = np.column_stack([match_grid.x0 + (ix + 0.5) * match_grid.res, match_grid.y0 + (iy + 0.5) * match_grid.res])
    inside = (xy[:, 0] > real.xmin) & (xy[:, 0] < real.xmax) & (xy[:, 1] > real.ymin) & (xy[:, 1] < real.ymax)
    d = real.sdf(xy[inside]) if inside.any() else np.zeros(0)
    return {"occ_cells": int(len(xy)), "occ_cells_inside": int(inside.sum()),
            "phantom_frac": round(float((d > 0.2).mean()), 4) if len(d) else None,
            "median_abs_sdf_m": round(float(np.median(np.abs(d))), 4) if len(d) else None}
