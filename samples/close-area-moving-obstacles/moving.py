"""Moving obstacles on top of an arena layout: person-sized cylinders on seeded segments.

Mover model (constant speed, ping-pong):
  - 1-3 cylinders of radius PERSON_R per layout (count drawn per layout).
  - Each walks a straight segment P0 => P1 and back at constant speed v, forever. Position at
    time t: s = (s0 + v t) mod 2L, folded back when s > L. Only the turn-around points change
    the velocity; there is no acceleration phase.
  - Segments cross the A-B corridor: centre near the A-B line at 30-70 % of the way, direction
    within +-45 deg of perpendicular to A-B, half-length 1.5-3.0 m.
  - The whole segment keeps STATIC_CLEAR_M from static obstacles and walls (a person does not
    walk through a box), KEEP_A_M from A and KEEP_B_M from B. A segment that fails is redrawn,
    up to MAX_TRIES; then that mover is dropped (logged as n_movers < n_drawn).
  - Segments and start phases come from rng [seed, index, MOVER_SEED] and do not depend on the
    speed, so speed 0.0 / 0.5 / 1.0 runs of one layout share the same movers (paired).
  - Speed 0.0 = the movers frozen at their start phase: unmapped static obstacles (control).

MovingWorld wraps the static arena World. set_time(t) moves the cylinders; after that, sdf(),
clearance() and raycast() (the range fan and the truth collision check) see the current
positions. .grid stays the static prior OccGrid: movers are never in the prior map.
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass

import numpy as np

try:
    from . import arena
except ImportError:
    import arena

PERSON_R = 0.25          # m, standing adult, about 0.5 m across the shoulders
MOVER_SEED = 4301        # rng constant, distinct from the arena's 7, 8, 4001, 4101
N_MIN, N_MAX = 1, 3
STATIC_CLEAR_M = 0.2     # m, segment keeps this much space from static surfaces (beyond PERSON_R)
KEEP_A_M = 1.5           # m, segment never comes closer to A than this (beyond PERSON_R)
KEEP_B_M = 1.0           # m, same for B
MAX_TRIES = 60


@dataclass
class Mover:
    x0: float
    y0: float
    x1: float
    y1: float
    s0: float            # m, start phase along the 2L ping-pong cycle
    r: float = PERSON_R

    @property
    def length(self) -> float:
        return math.hypot(self.x1 - self.x0, self.y1 - self.y0)

    def at(self, t: float, speed: float) -> tuple[float, float]:
        L = self.length
        if L < 1e-9:
            return self.x0, self.y0
        s = (self.s0 + speed * t) % (2 * L)
        if s > L:
            s = 2 * L - s
        f = s / L
        return self.x0 + f * (self.x1 - self.x0), self.y0 + f * (self.y1 - self.y0)

    def to_list(self):
        return [round(v, 4) for v in (self.x0, self.y0, self.x1, self.y1, self.s0, self.r)]


def draw_movers(w, seed: int, index: int) -> tuple[list[Mover], int]:
    """Seeded movers for static layout w. Returns (movers, n_drawn)."""
    rng = np.random.default_rng([seed, index, MOVER_SEED])
    n = int(rng.integers(N_MIN, N_MAX + 1))
    gx, gy = w.goal
    lab = math.hypot(gx, gy)
    ux, uy = gx / lab, gy / lab                 # A => B unit vector (A is the origin)
    px, py = -uy, ux
    out = []
    for _ in range(n):
        for _try in range(MAX_TRIES):
            f = rng.uniform(0.3, 0.7)
            lat = rng.uniform(-1.0, 1.0)
            cx, cy = f * gx + lat * px, f * gy + lat * py
            ang = math.atan2(py, px) + rng.uniform(-math.pi / 4, math.pi / 4)
            hl = rng.uniform(1.5, 3.0)
            s0 = rng.uniform(0.0, 4 * hl)
            x0, y0 = cx - hl * math.cos(ang), cy - hl * math.sin(ang)
            x1, y1 = cx + hl * math.cos(ang), cy + hl * math.sin(ang)
            k = np.linspace(0.0, 1.0, 41)
            pts = np.column_stack([x0 + k * (x1 - x0), y0 + k * (y1 - y0)])
            if w.sdf(pts).min() < PERSON_R + STATIC_CLEAR_M:
                continue
            if np.hypot(pts[:, 0], pts[:, 1]).min() < PERSON_R + KEEP_A_M:
                continue
            if np.hypot(pts[:, 0] - gx, pts[:, 1] - gy).min() < PERSON_R + KEEP_B_M:
                continue
            out.append(Mover(x0, y0, x1, y1, s0))
            break
    return out, n


class MovingWorld:
    """Arena World plus movers. Call set_time(t) before every sdf / raycast query."""

    def __init__(self, static_world, movers: list[Mover], speed: float):
        self.static = static_world
        self.movers = movers
        self.speed = float(speed)
        self.grid = static_world.grid            # prior map: static obstacles only
        self.goal = static_world.goal
        self.boxes = static_world.boxes
        self.attempts = static_world.attempts
        self._cur = copy.copy(static_world)      # shares boxes; cylinders replaced per time
        self._static_cyls = list(static_world.cylinders)
        self.t = None
        self.set_time(0.0)

    @property
    def cylinders(self):
        return self._cur.cylinders

    def positions(self, t: float | None = None) -> list[tuple[float, float]]:
        t = self.t if t is None else t
        return [m.at(t, self.speed) for m in self.movers]

    def set_time(self, t: float) -> None:
        if self.t is not None and abs(t - self.t) < 1e-12:
            return
        self.t = t
        Cyl = arena.world.Cylinder
        self._cur.cylinders = self._static_cyls + [Cyl(x, y, m.r) for (x, y), m in zip(self.positions(t), self.movers)]
        self._cur._pack()

    # ---- World interface used by the adapter, sensors and harness ----
    def sdf(self, xy):
        return self._cur.sdf(xy)

    def clearance(self, x: float, y: float) -> float:
        return self._cur.clearance(x, y)

    def raycast(self, x, y, angles, max_range):
        return self._cur.raycast(x, y, angles, max_range)

    def mover_distances(self, x: float, y: float) -> list[float]:
        """Centre-to-surface distance from (x, y) to each mover at the current time."""
        return [math.hypot(x - mx, y - my) - m.r for (mx, my), m in zip(self.positions(), self.movers)]
