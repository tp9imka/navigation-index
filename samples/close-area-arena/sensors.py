"""Ray-cast range fan (2D lidar / multi-zone ToF style) returning the published RangeScan."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

try:
    from .adapter import RangeScan
except ImportError:
    from adapter import RangeScan


@dataclass
class RangeScanDrops(RangeScan):
    """RangeScan plus a per-beam drop flag (loop-88, docs/upstream-findings.md section 22).

    distances are unchanged: a dropped beam still reads math.inf, so every consumer that only
    reads the published fields behaves as before. dropped[i] is True when beam i was dropped
    (no measurement), False when it was measured (a hit, or no surface within max_range).
    None = unknown (a real driver, or a scan rebuilt without the field): treat inf as no return.
    Only astar_esdf.LogOddsMap reads it."""
    dropped: list[bool] | None = None


class RangeFan:
    """n_beams evenly spread over fov (rad), body frame, 0 = forward, CCW positive.

    A full circle (fov >= 2 pi) does not repeat the end beam. Hits get Gaussian noise
    (noise_std, m, clipped at 0); each beam is dropped with probability dropout and then
    reads math.inf, as does any beam with no surface within max_range. The returned
    RangeScanDrops tells the two apart in .dropped.
    """

    def __init__(self, n_beams: int = 72, fov: float = 2 * math.pi, max_range: float = 6.0,
                 noise_std: float = 0.02, dropout: float = 0.02, rng=None):
        self.n_beams, self.fov, self.max_range = n_beams, fov, max_range
        self.noise_std, self.dropout = noise_std, dropout
        self.rng = rng if rng is not None else np.random.default_rng(0)
        if fov >= 2 * math.pi - 1e-9:
            self.angles = -math.pi + np.arange(n_beams) * (2 * math.pi / n_beams)
        elif n_beams == 1:
            self.angles = np.zeros(1)
        else:
            self.angles = np.linspace(-fov / 2, fov / 2, n_beams)

    def scan(self, world, x: float, y: float, yaw: float, t: float) -> RangeScan:
        d = world.raycast(x, y, self.angles + yaw, self.max_range)
        noise = self.rng.normal(0.0, self.noise_std, size=d.shape) if self.noise_std > 0 else 0.0
        drop = self.rng.random(d.shape) < self.dropout if self.dropout > 0 else np.zeros(d.shape, bool)
        d = np.where(np.isfinite(d), np.maximum(d + noise, 0.0), np.inf)
        d = np.where(drop | (d > self.max_range), np.inf, d)
        return RangeScanDrops(t=float(t), angles=[float(a) for a in self.angles],
                              distances=[math.inf if not np.isfinite(v) else float(v) for v in d],
                              max_range=float(self.max_range), dropped=[bool(v) for v in drop])
