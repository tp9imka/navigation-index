# Copied verbatim from templates/drone-adapter/mock.py (navigation-index hub, 2026-11-09).
"""MockAdapter: kinematic point mass at 20 Hz with one wall. No simulator needed.

- Lockstep: each `send_setpoint()` advances simulated time by `dt` (0.05 s), so a
  planner loop runs as fast as Python allows and gives the same result every run.
- Velocity follows the command with an acceleration limit (no attitude, no drag, no noise).
- `ranges()` ray-casts a horizontal body-frame scan against one wall segment.
- Touching the wall (closer than `radius`) sets `collided` and freezes the vehicle.
- Pose is perfect: quality 100, reset_counter 0, sigma_xy 0.0. Inject faults yourself.
"""
from __future__ import annotations

import math

try:                                    # works as a package or as a flat folder
    from .adapter import Pose, RangeScan, Setpoint, body_to_world, wrap_pi
except ImportError:
    from adapter import Pose, RangeScan, Setpoint, body_to_world, wrap_pi

Point = tuple[float, float]


class MockAdapter:
    def __init__(
        self,
        start: tuple[float, float, float] = (0.0, 0.0, 0.0),
        wall: tuple[Point, Point] = ((4.0, -1.0), (4.0, 1.0)),
        dt: float = 0.05,
        a_max: float = 3.0,
        v_max: float = 2.0,
        n_beams: int = 8,
        max_range: float = 4.0,
        radius: float = 0.15,
    ) -> None:
        self.t = 0.0
        self.x, self.y, self.z = start
        self.vx = self.vy = self.vz = 0.0
        self.yaw = 0.0
        self.wall = wall
        self.dt, self.a_max, self.v_max = dt, a_max, v_max
        self.angles = [wrap_pi(2.0 * math.pi * i / n_beams) for i in range(n_beams)]
        self.max_range = max_range
        self.radius = radius
        self.collided = False
        self.min_wall_dist = self._wall_dist()

    # --- Adapter protocol ---------------------------------------------------
    def pose(self) -> Pose:
        return Pose(self.t, self.x, self.y, self.z, self.vx, self.vy, self.vz, self.yaw,
                    quality=100, reset_counter=0, sigma_xy=0.0)

    def ranges(self) -> RangeScan:
        dists = [self._cast(a) for a in self.angles]
        return RangeScan(self.t, list(self.angles), dists, self.max_range)

    def send_setpoint(self, sp: Setpoint) -> None:
        if not self.collided:
            self._step(sp)
        self.t += self.dt

    # --- internals ----------------------------------------------------------
    def _step(self, sp: Setpoint) -> None:
        cmd = [sp.vx, sp.vy, sp.vz]
        n = math.sqrt(sum(c * c for c in cmd))
        if n > self.v_max:
            cmd = [c * self.v_max / n for c in cmd]
        dv = [c - v for c, v in zip(cmd, (self.vx, self.vy, self.vz))]
        dn = math.sqrt(sum(d * d for d in dv))
        lim = self.a_max * self.dt
        if dn > lim:
            dv = [d * lim / dn for d in dv]
        self.vx += dv[0]; self.vy += dv[1]; self.vz += dv[2]
        self.x += self.vx * self.dt
        self.y += self.vy * self.dt
        self.z = max(0.0, self.z + self.vz * self.dt)
        self.yaw = wrap_pi(self.yaw + sp.yaw_rate * self.dt)
        d = self._wall_dist()
        self.min_wall_dist = min(self.min_wall_dist, d)
        if d < self.radius:
            self.collided = True
            self.vx = self.vy = self.vz = 0.0

    def _wall_dist(self) -> float:
        (ax, ay), (bx, by) = self.wall
        ex, ey = bx - ax, by - ay
        L2 = ex * ex + ey * ey
        u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((self.x - ax) * ex + (self.y - ay) * ey) / L2))
        return math.hypot(self.x - (ax + u * ex), self.y - (ay + u * ey))

    def _cast(self, body_angle: float) -> float:
        dx, dy, _ = body_to_world((math.cos(body_angle), math.sin(body_angle), 0.0), self.yaw)
        (ax, ay), (bx, by) = self.wall
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            return math.inf
        wx, wy = ax - self.x, ay - self.y
        t = (wx * ey - wy * ex) / den     # distance along the ray
        u = (wx * dy - wy * dx) / den     # position along the wall, 0..1
        if t < 0.0 or not 0.0 <= u <= 1.0 or t > self.max_range:
            return math.inf
        return t
