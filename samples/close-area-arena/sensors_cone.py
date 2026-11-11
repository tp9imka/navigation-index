"""Cone-beam range sensor with materials, a drop-in for sensors.RangeFan.

ConeRangeFan.scan(world, x, y, yaw, t) -> RangeScan, same signature and output as RangeFan, so
SimAdapter takes it unchanged. What it adds, per beam:

- Cone: n_sub sub-rays spread evenly over cone_deg (full angle) around the beam centre, in the
  horizontal plane (2.5D). The beam reports the k-th closest sub-ray hit, k = ceil(min_fill *
  n_sub): the closest range at which at least min_fill of the cone returns. A wall reads at about
  its nearest point; a thin pole that fills less than min_fill of the cone is missed. Doc 08
  section 2.3 says the VL53L1x reports the closest detection in its cone, and section 2.4 says
  narrow objects are missed; min_fill is the arena's way to get both, not a measured value.
- Materials: world.materials = {"boxes": [...], "cylinders": [...]} (strings, parallel to
  world.boxes / world.cylinders; world_glass.py sets it). Missing => every obstacle "matte".
  Materials in `invisible` (default glass, mirror) return nothing and the ray passes through
  to whatever is behind them. "dark" surfaces return only within dark_max_range (the detection
  range is scaled down for low-reflectance targets). Walls of the area are matte.
- Minimum range: a true range below min_range reads uniform in [0, min_range] (detected, not
  accurate, doc 08 section 2.1). With the arena radius 0.15 m this only happens after contact.
- Noise: Gaussian with std(d) = sqrt(noise_std^2 + zr(d)^2) when noise_model == "zranger",
  zr(d) = 0.0025 (1 + exp(k (d - 2.5))), k = ln(80) / 1.5 (Bitcraze zranger2.c, doc 08 section
  2.3), else std = noise_std. Readings are clipped at 0; above max_range => inf.
- Dropout: each beam reads inf with probability dropout. The returned sensors.RangeScanDrops
  flags these beams in .dropped (a beam with no surface in range is not flagged).

Truth geometry is untouched: world.sdf / world.clearance (collision, scoring) see every
obstacle, whatever its material.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from .sensors import RangeScanDrops
except ImportError:
    from sensors import RangeScanDrops

ZR_A = 0.0025                     # m, zranger2.c noise at short range (doc 08 2.3)
ZR_K = math.log(80.0) / 1.5       # 1/m
ZR_D0 = 2.5                       # m


def zranger_std(d: np.ndarray) -> np.ndarray:
    return ZR_A * (1.0 + np.exp(ZR_K * (np.minimum(d, 10.0) - ZR_D0)))


def raycast_per_obstacle(world, x: float, y: float, angles: np.ndarray):
    """Exact hit distance of each ray against each obstacle, without taking the minimum.

    Returns (walls (n,), boxes (n, nb), cyls (n, nc)); np.inf where a ray misses. Same maths as
    World.raycast, kept per obstacle so materials can be applied."""
    a = np.asarray(angles, dtype=float)
    dx, dy = np.cos(a), np.sin(a)
    bc, bh = world._bc, world._bh
    cc, cr = world._cc, world._cr
    with np.errstate(divide="ignore", invalid="ignore"):
        tx = np.where(dx > 0, (world.xmax - x) / dx, np.where(dx < 0, (world.xmin - x) / dx, np.inf))
        ty = np.where(dy > 0, (world.ymax - y) / dy, np.where(dy < 0, (world.ymin - y) / dy, np.inf))
        walls = np.maximum(np.minimum(tx, ty), 0.0)
        boxes = np.full((len(a), len(bc)), np.inf)
        if len(bc):
            lo, hi = bc - bh, bc + bh
            inv_x, inv_y = 1.0 / dx[:, None], 1.0 / dy[:, None]
            t1x = (lo[None, :, 0] - x) * inv_x
            t2x = (hi[None, :, 0] - x) * inv_x
            t1y = (lo[None, :, 1] - y) * inv_y
            t2y = (hi[None, :, 1] - y) * inv_y
            tmin = np.nan_to_num(np.maximum(np.minimum(t1x, t2x), np.minimum(t1y, t2y)), nan=-np.inf)
            tmax = np.nan_to_num(np.minimum(np.maximum(t1x, t2x), np.maximum(t1y, t2y)), nan=-np.inf)
            hit = tmax >= np.maximum(tmin, 0.0)
            boxes = np.where(hit, np.maximum(tmin, 0.0), np.inf)
        cyls = np.full((len(a), len(cc)), np.inf)
        if len(cc):
            ox = x - cc[None, :, 0]
            oy = y - cc[None, :, 1]
            b = ox * dx[:, None] + oy * dy[:, None]
            c = ox ** 2 + oy ** 2 - cr[None] ** 2
            disc = b * b - c
            sq = np.sqrt(np.maximum(disc, 0.0))
            t0, t1 = -b - sq, -b + sq
            tc = np.where(c <= 0, 0.0, np.where(t0 >= 0, t0, np.inf))
            cyls = np.where((disc >= 0) & (t1 >= 0), tc, np.inf)
    return walls, boxes, cyls


class ConeRangeFan:
    """RangeFan-compatible sensor: cone beams, minimum range, range-dependent noise, materials."""

    def __init__(self, n_beams: int = 4, fov: float = 2 * math.pi, max_range: float = 3.0,
                 noise_std: float = 0.02, dropout: float = 0.05, rng=None,
                 noise_model: str = "zranger", cone_deg: float = 27.0, n_sub: int = 11,
                 min_fill: float = 0.15, min_range: float = 0.04,
                 invisible=("glass", "mirror"), dark_max_range: float | None = 1.0):
        self.n_beams, self.fov, self.max_range = n_beams, fov, max_range
        self.noise_std, self.dropout, self.noise_model = noise_std, dropout, noise_model
        self.cone = math.radians(cone_deg)
        self.n_sub = max(1, int(n_sub))
        self.k = min(self.n_sub, max(1, math.ceil(min_fill * self.n_sub - 1e-9)))
        self.min_range = min_range
        self.invisible = tuple(invisible)
        self.dark_max_range = max_range if dark_max_range is None else dark_max_range
        self.rng = rng if rng is not None else np.random.default_rng(0)
        if fov >= 2 * math.pi - 1e-9:
            self.angles = -math.pi + np.arange(n_beams) * (2 * math.pi / n_beams)
        elif n_beams == 1:
            self.angles = np.zeros(1)
        else:
            self.angles = np.linspace(-fov / 2, fov / 2, n_beams)
        if self.n_sub == 1 or self.cone <= 0:
            self.sub = np.zeros(1)
            self.n_sub, self.k = 1, 1
        else:
            self.sub = np.linspace(-self.cone / 2, self.cone / 2, self.n_sub)
        self._mat_cache = (None, None)

    def _masks(self, world):
        """(visible_box, visible_cyl, dark_box, dark_cyl) bool arrays for this world."""
        mats = getattr(world, "materials", None) or {}
        key = (id(world), id(mats), len(world.boxes), len(world.cylinders))
        if self._mat_cache[0] == key:
            return self._mat_cache[1]
        mb = list(mats.get("boxes", [])) + ["matte"] * (len(world.boxes) - len(mats.get("boxes", [])))
        mc = list(mats.get("cylinders", [])) + ["matte"] * (len(world.cylinders) - len(mats.get("cylinders", [])))
        out = (np.array([m not in self.invisible for m in mb], bool),
               np.array([m not in self.invisible for m in mc], bool),
               np.array([m == "dark" for m in mb], bool),
               np.array([m == "dark" for m in mc], bool))
        self._mat_cache = (key, out)
        return out

    def true_ranges(self, world, x: float, y: float, yaw: float) -> np.ndarray:
        """Noise-free beam ranges after cone and materials (np.inf = no return)."""
        vb, vc, db, dc = self._masks(world)
        ang = (self.angles[:, None] + self.sub[None, :]).ravel() + yaw
        walls, boxes, cyls = raycast_per_obstacle(world, x, y, ang)
        boxes = np.where(vb[None] & ~(db[None] & (boxes > self.dark_max_range)), boxes, np.inf)
        cyls = np.where(vc[None] & ~(dc[None] & (cyls > self.dark_max_range)), cyls, np.inf)
        d = walls
        if boxes.shape[1]:
            d = np.minimum(d, boxes.min(axis=1))
        if cyls.shape[1]:
            d = np.minimum(d, cyls.min(axis=1))
        d = np.where(d <= self.max_range, d, np.inf).reshape(self.n_beams, self.n_sub)
        return np.sort(d, axis=1)[:, self.k - 1]

    def scan(self, world, x: float, y: float, yaw: float, t: float) -> RangeScan:
        d = self.true_ranges(world, x, y, yaw)
        shape = d.shape
        z = self.rng.normal(0.0, 1.0, size=shape)
        u = self.rng.random(shape)
        drop = self.rng.random(shape) < self.dropout
        fin = np.isfinite(d)
        df = np.where(fin, d, 0.0)
        std = np.full(shape, self.noise_std)
        if self.noise_model == "zranger":
            std = np.sqrt(std ** 2 + zranger_std(df) ** 2)
        meas = np.maximum(df + z * std, 0.0)
        meas = np.where(df < self.min_range, u * self.min_range, meas)
        meas = np.where(fin & ~drop & (meas <= self.max_range), meas, np.inf)
        return RangeScanDrops(t=float(t), angles=[float(a) for a in self.angles],
                              distances=[math.inf if not np.isfinite(v) else float(v) for v in meas],
                              max_range=float(self.max_range), dropped=[bool(v) for v in drop])
