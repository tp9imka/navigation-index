"""Obstacles the range fan cannot see: in the prior map and in truth collision checks, not in scans.

They model a glass panel, a thin pole, or anything outside the fan (doc 04 section 3.4: "unsensed
(outside FoV, plus ... two map-only thin poles the range sensor misses)").

- add_unsensed(world, seed, index) returns a new arena World with N_PER_LAYOUT extra obstacles
  placed on the reference A* path (arena planners/astar_esdf.py, known map, planned from A on the
  layout without them), plus the list of what was added. The new World's sdf/clearance and its
  0.1 m grid include them, so the scorer counts a hit and the known-map planner plans around them.
- VisibleOnlyFan wraps the arena RangeFan: it ray-casts against the layout WITHOUT the unsensed
  obstacles, whatever world it is handed. No arena file is edited.

Placement per obstacle (seeded by default_rng([seed, index, RNG_CODE])): arc fraction along the
reference path drawn from PATH_FRAC[k], lateral offset U(-LATERAL_M, LATERAL_M); kind "pole"
(cylinder, radius POLE_R) or "glass" (axis-aligned panel GLASS_LEN long, 2 * GLASS_HALF_T thick,
oriented across the path). Rejected and redrawn (up to MAX_TRIES) if it is within KEEP_AB_M of A
or B, overlaps an existing obstacle, or breaks the arena's free-path guarantee (4-connected BFS
on the grid inflated by the vehicle radius). If no draw fits, that obstacle is skipped.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np

import arena

N_PER_LAYOUT = 2
PATH_FRAC = ((0.2, 0.45), (0.55, 0.8))
LATERAL_M = 0.15
POLE_R = (0.04, 0.08)        # m, thin pole radius range
GLASS_LEN = (0.6, 1.2)       # m, panel length range
GLASS_HALF_T = 0.02          # m, half thickness (4 cm panel)
P_GLASS = 0.5
KEEP_AB_M = 1.0
MIN_GAP_M = 0.05             # m, centre-to-existing-surface margin beyond the obstacle's own size
MAX_TRIES = 30
RNG_CODE = 9100


@dataclass
class Unsensed:
    kind: str                # "pole" | "glass"
    cx: float
    cy: float
    r: float = 0.0           # pole radius
    hx: float = 0.0          # glass half sizes
    hy: float = 0.0

    def reach(self) -> float:
        return self.r if self.kind == "pole" else math.hypot(self.hx, self.hy)

    def to_list(self):
        return [self.kind, round(self.cx, 3), round(self.cy, 3), round(self.r, 3),
                round(self.hx, 3), round(self.hy, 3)]


def reference_path(w) -> np.ndarray:
    """Shortcut A* path (k, 2) from A to B on the layout's own grid, arena planner settings."""
    pl = arena.astar_esdf.make(known_map=True)
    pl._plan(SimpleNamespace(x=0.0, y=0.0), (w.goal[0], w.goal[1], 1.0), w.grid)
    if pl.path_xy is None:
        return np.array([[0.0, 0.0], [w.goal[0], w.goal[1]]])
    return np.vstack([[0.0, 0.0], pl.path_xy])


def _at_fraction(path: np.ndarray, f: float):
    seg = np.diff(path, axis=0)
    L = np.hypot(seg[:, 0], seg[:, 1])
    s = f * L.sum()
    i = int(np.searchsorted(np.cumsum(L), s))
    i = min(i, len(L) - 1)
    s0 = s - (np.cumsum(L)[i] - L[i])
    t = seg[i] / max(L[i], 1e-9)
    return path[i] + t * s0, t


def _build(w, extra: list[Unsensed]):
    W = arena.world
    boxes = list(w.boxes) + [W.Box(u.cx, u.cy, u.hx, u.hy) for u in extra if u.kind == "glass"]
    cyls = list(w.cylinders) + [W.Cylinder(u.cx, u.cy, u.r) for u in extra if u.kind == "pole"]
    nw = W.World(family=w.family, seed=w.seed, xmin=w.xmin, ymin=w.ymin, xmax=w.xmax, ymax=w.ymax,
                 goal=w.goal, boxes=boxes, cylinders=cyls, attempts=w.attempts)
    nw.grid = nw.rasterize(w.grid.res)
    return nw


def _free_path(nw) -> bool:
    blocked = nw.grid.inflated(arena.world.RADIUS)
    return arena.world.bfs_free_path(blocked, nw.grid.to_index(0.0, 0.0), nw.grid.to_index(*nw.goal)) is not None


def add_unsensed(w, seed: int, index: int, n: int = N_PER_LAYOUT):
    """Return (world_with_unsensed, [Unsensed, ...]). The input world is not modified."""
    rng = np.random.default_rng([seed, index, RNG_CODE])
    path = reference_path(w)
    placed: list[Unsensed] = []
    cur = w
    for k in range(n):
        lo, hi = PATH_FRAC[k % len(PATH_FRAC)]
        for _ in range(MAX_TRIES):
            f = float(rng.uniform(lo, hi))
            lat = float(rng.uniform(-LATERAL_M, LATERAL_M))
            glass = bool(rng.random() < P_GLASS)
            size = float(rng.uniform(*(GLASS_LEN if glass else POLE_R)))
            pt, t = _at_fraction(path, f)
            c = pt + lat * np.array([-t[1], t[0]])
            if glass:   # axis-aligned panel across the path: long along the axis least aligned with travel
                if abs(t[0]) >= abs(t[1]):
                    u = Unsensed("glass", float(c[0]), float(c[1]), hx=GLASS_HALF_T, hy=size / 2)
                else:
                    u = Unsensed("glass", float(c[0]), float(c[1]), hx=size / 2, hy=GLASS_HALF_T)
            else:
                u = Unsensed("pole", float(c[0]), float(c[1]), r=size)
            if math.hypot(u.cx, u.cy) < KEEP_AB_M + u.reach():
                continue
            if math.hypot(u.cx - w.goal[0], u.cy - w.goal[1]) < KEEP_AB_M + u.reach():
                continue
            if cur.clearance(u.cx, u.cy) < u.reach() + MIN_GAP_M:
                continue
            cand = _build(w, placed + [u])
            if not _free_path(cand):
                continue
            placed.append(u)
            cur = cand
            break
    return (cur if placed else w), placed


def unsensed_sdf(placed: list[Unsensed], x: float, y: float) -> float:
    """Distance from (x, y) to the nearest unsensed obstacle surface (inf if none)."""
    best = math.inf
    for u in placed:
        if u.kind == "pole":
            d = math.hypot(x - u.cx, y - u.cy) - u.r
        else:
            qx, qy = abs(x - u.cx) - u.hx, abs(y - u.cy) - u.hy
            d = math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0)
        best = min(best, d)
    return best


class VisibleOnlyFan(arena.sensors.RangeFan):
    """Arena RangeFan that ray-casts against `visible_world` (the layout without unsensed obstacles)."""

    def __init__(self, visible_world, **kw):
        super().__init__(**kw)
        self.visible_world = visible_world

    def scan(self, world, x, y, yaw, t):
        return super().scan(self.visible_world, x, y, yaw, t)
