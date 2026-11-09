"""2.5D close-area world: axis-aligned boxes and cylinders in a walled 20 x 20 m area.

All coordinates are local ENU metres with the origin at point A. Geometry is kept exact
(analytic signed distance and ray casts); the 0.1 m occupancy grid is what a planner gets.
Layouts are deterministic by seed and resampled until a free path A => B exists on the grid
inflated by the vehicle radius (4-connected BFS).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import distance_transform_edt

AREA = 20.0          # m, square side
RES = 0.1            # m, grid cell
RADIUS = 0.15        # m, vehicle radius used for the free-path guarantee
FAMILIES = ("random", "u_trap", "narrow_gap")
_FAMILY_CODE = {name: i for i, name in enumerate(FAMILIES)}


@dataclass
class Box:            # axis-aligned, centre and half sizes, local frame
    cx: float
    cy: float
    hx: float
    hy: float


@dataclass
class Cylinder:       # vertical, infinite height in 2.5D
    cx: float
    cy: float
    r: float


@dataclass
class OccGrid:
    """occ[ix, iy] is True when the cell is occupied. Cell (ix, iy) covers
    x in [x0 + ix*res, x0 + (ix+1)*res), same for y. Outside the grid counts as occupied."""
    occ: np.ndarray
    res: float
    x0: float
    y0: float

    def to_index(self, x: float, y: float) -> tuple[int, int]:
        return int(np.floor((x - self.x0) / self.res)), int(np.floor((y - self.y0) / self.res))

    def to_xy(self, ix: int, iy: int) -> tuple[float, float]:
        return self.x0 + (ix + 0.5) * self.res, self.y0 + (iy + 0.5) * self.res

    def inflated(self, radius: float) -> np.ndarray:
        """Cells whose centre is closer than `radius` to an occupied cell or the boundary."""
        padded = np.pad(self.occ, 1, constant_values=True)
        d = distance_transform_edt(~padded) * self.res
        return (d <= radius + 1e-9)[1:-1, 1:-1]

    def esdf(self) -> np.ndarray:
        """Distance in metres from each free cell centre to the nearest occupied cell (0 inside)."""
        padded = np.pad(self.occ, 1, constant_values=True)
        return (distance_transform_edt(~padded) * self.res)[1:-1, 1:-1]


@dataclass
class World:
    family: str
    seed: int
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    goal: tuple[float, float]            # point B, local frame (A is the origin)
    boxes: list[Box] = field(default_factory=list)
    cylinders: list[Cylinder] = field(default_factory=list)
    grid: OccGrid | None = None
    attempts: int = 1                    # layouts drawn until a free path existed

    def __post_init__(self):
        self._pack()

    def _pack(self):
        self._bc = np.array([[b.cx, b.cy] for b in self.boxes]).reshape(-1, 2)
        self._bh = np.array([[b.hx, b.hy] for b in self.boxes]).reshape(-1, 2)
        self._cc = np.array([[c.cx, c.cy] for c in self.cylinders]).reshape(-1, 2)
        self._cr = np.array([c.r for c in self.cylinders])

    # ---- exact geometry ----
    def sdf(self, xy) -> np.ndarray:
        """Signed distance (m) from points (..., 2) to the nearest obstacle or wall surface.
        Positive in free space, negative inside an obstacle or outside the walls."""
        p = np.asarray(xy, dtype=float)
        shp = p.shape[:-1]
        p = p.reshape(-1, 2)
        d = np.minimum.reduce([p[:, 0] - self.xmin, self.xmax - p[:, 0],
                               p[:, 1] - self.ymin, self.ymax - p[:, 1]])
        if len(self._bc):
            q = np.abs(p[:, None, :] - self._bc[None]) - self._bh[None]
            outside = np.linalg.norm(np.maximum(q, 0.0), axis=2)
            inside = np.minimum(q.max(axis=2), 0.0)
            d = np.minimum(d, (outside + inside).min(axis=1))
        if len(self._cc):
            dc = np.linalg.norm(p[:, None, :] - self._cc[None], axis=2) - self._cr[None]
            d = np.minimum(d, dc.min(axis=1))
        return d.reshape(shp)

    def clearance(self, x: float, y: float) -> float:
        return float(self.sdf(np.array([x, y])))

    def raycast(self, x: float, y: float, angles: np.ndarray, max_range: float) -> np.ndarray:
        """Exact distance from (x, y) along world-frame `angles` to the first surface.
        Returns np.inf where nothing is hit within max_range, 0 if the origin is inside."""
        a = np.asarray(angles, dtype=float)
        dx, dy = np.cos(a), np.sin(a)
        best = np.full(a.shape, np.inf)
        with np.errstate(divide="ignore", invalid="ignore"):
            # walls: exit distance of the area box (origin assumed inside)
            tx = np.where(dx > 0, (self.xmax - x) / dx, np.where(dx < 0, (self.xmin - x) / dx, np.inf))
            ty = np.where(dy > 0, (self.ymax - y) / dy, np.where(dy < 0, (self.ymin - y) / dy, np.inf))
            best = np.minimum(best, np.maximum(np.minimum(tx, ty), 0.0))
            if len(self._bc):
                lo = self._bc - self._bh
                hi = self._bc + self._bh
                inv_x = 1.0 / dx[:, None]
                inv_y = 1.0 / dy[:, None]
                t1x = (lo[None, :, 0] - x) * inv_x
                t2x = (hi[None, :, 0] - x) * inv_x
                t1y = (lo[None, :, 1] - y) * inv_y
                t2y = (hi[None, :, 1] - y) * inv_y
                tmin = np.maximum(np.minimum(t1x, t2x), np.minimum(t1y, t2y))
                tmax = np.minimum(np.maximum(t1x, t2x), np.maximum(t1y, t2y))
                tmin = np.nan_to_num(tmin, nan=-np.inf)
                tmax = np.nan_to_num(tmax, nan=-np.inf)
                hit = (tmax >= np.maximum(tmin, 0.0))
                th = np.where(hit, np.maximum(tmin, 0.0), np.inf)
                best = np.minimum(best, th.min(axis=1))
            if len(self._cc):
                ox = x - self._cc[None, :, 0]
                oy = y - self._cc[None, :, 1]
                b = ox * dx[:, None] + oy * dy[:, None]
                c = ox ** 2 + oy ** 2 - self._cr[None] ** 2
                disc = b * b - c
                sq = np.sqrt(np.maximum(disc, 0.0))
                t0 = -b - sq
                t1 = -b + sq
                tc = np.where(c <= 0, 0.0, np.where(t0 >= 0, t0, np.inf))
                tc = np.where((disc >= 0) & (t1 >= 0), tc, np.inf)
                best = np.minimum(best, tc.min(axis=1))
        return np.where(best <= max_range, best, np.inf)

    def rasterize(self, res: float = RES) -> OccGrid:
        """Cell is occupied when its centre is within res/2 of a surface or inside one."""
        nx = int(round((self.xmax - self.xmin) / res))
        ny = int(round((self.ymax - self.ymin) / res))
        xs = self.xmin + (np.arange(nx) + 0.5) * res
        ys = self.ymin + (np.arange(ny) + 0.5) * res
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        occ = np.zeros((nx, ny), dtype=bool)
        pts = np.stack([X.ravel(), Y.ravel()], axis=1)
        for k in range(0, len(pts), 8000):          # chunk to bound memory
            occ.ravel()[k:k + 8000] = self._sdf_obstacles(pts[k:k + 8000]) <= res / 2
        return OccGrid(occ=occ, res=res, x0=self.xmin, y0=self.ymin)

    def _sdf_obstacles(self, p: np.ndarray) -> np.ndarray:
        d = np.full(len(p), np.inf)
        if len(self._bc):
            q = np.abs(p[:, None, :] - self._bc[None]) - self._bh[None]
            d = np.minimum(d, (np.linalg.norm(np.maximum(q, 0.0), axis=2)
                               + np.minimum(q.max(axis=2), 0.0)).min(axis=1))
        if len(self._cc):
            d = np.minimum(d, (np.linalg.norm(p[:, None, :] - self._cc[None], axis=2)
                               - self._cr[None]).min(axis=1))
        return d

    def to_dict(self) -> dict:
        return {
            "family": self.family, "seed": self.seed, "attempts": self.attempts,
            "area": [self.xmin, self.ymin, self.xmax, self.ymax], "goal": list(self.goal),
            "boxes": [[b.cx, b.cy, b.hx, b.hy] for b in self.boxes],
            "cylinders": [[c.cx, c.cy, c.r] for c in self.cylinders],
        }


def bfs_free_path(blocked: np.ndarray, start: tuple[int, int], goal: tuple[int, int]) -> int | None:
    """4-connected BFS on a boolean blocked grid. Returns the hop count or None."""
    nx, ny = blocked.shape
    (sx, sy), (gx, gy) = start, goal
    if not (0 <= sx < nx and 0 <= sy < ny and 0 <= gx < nx and 0 <= gy < ny):
        return None
    if blocked[sx, sy] or blocked[gx, gy]:
        return None
    dist = np.full(blocked.shape, -1, dtype=np.int32)
    dist[sx, sy] = 0
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        if x == gx and y == gy:
            return int(dist[x, y])
        d = dist[x, y] + 1
        for nx_, ny_ in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx_ < nx and 0 <= ny_ < ny and dist[nx_, ny_] < 0 and not blocked[nx_, ny_]:
                dist[nx_, ny_] = d
                q.append((nx_, ny_))
    return None


# ---- layout families (area frame: [0, AREA]^2, shifted to the A origin at the end) ----

def _random_obstacle(rng, boxes, cyls, keep_out, lo=0.0, hi=AREA):
    cx, cy = rng.uniform(lo + 0.5, hi - 0.5, size=2)
    if rng.random() < 0.5:
        hx, hy = rng.uniform(0.25, 1.5, size=2)
        cand = ("box", (cx, cy, hx, hy))
        reach = float(np.hypot(hx, hy))
    else:
        r = rng.uniform(0.2, 0.8)
        cand = ("cyl", (cx, cy, r))
        reach = r
    for (kx, ky, kr) in keep_out:
        if np.hypot(cx - kx, cy - ky) < kr + reach:
            return False
    (boxes if cand[0] == "box" else cyls).append(cand[1])
    return True


def _layout(family: str, rng) -> tuple[tuple, tuple, list, list]:
    a = (1.5 + rng.uniform(-0.5, 0.5), 1.5 + rng.uniform(-0.5, 0.5))
    b = (AREA - 1.5 + rng.uniform(-0.5, 0.5), AREA - 1.5 + rng.uniform(-0.5, 0.5))
    boxes: list = []
    cyls: list = []
    keep_out = [(a[0], a[1], 1.0), (b[0], b[1], 1.0)]
    if family == "random":
        n = int(rng.integers(8, 16))
        tries = 0
        while len(boxes) + len(cyls) < n and tries < 500:
            _random_obstacle(rng, boxes, cyls, keep_out)
            tries += 1
    elif family == "u_trap":
        # cup whose inside corner sits on the A-B line, opening towards A
        f = rng.uniform(0.5, 0.65)
        kx, ky = a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])
        arm = rng.uniform(3.0, 5.0)
        lip = rng.uniform(0.8, 1.5)
        t = 0.15                                              # wall half thickness
        boxes.append((kx - arm / 2 + t, ky + t, arm / 2, t))  # top wall, extends to -x
        boxes.append((kx + t, ky - arm / 2 + t, t, arm / 2))  # right wall, extends to -y
        boxes.append((kx - arm + 2 * t, ky + t - lip / 2, t, lip / 2))   # lip down from top-left end
        boxes.append((kx + t - lip / 2, ky - arm + 2 * t, lip / 2, t))   # lip left from right-bottom end
        keep_out.append((kx - arm / 2, ky - arm / 2, arm * 0.9))
        n = int(rng.integers(2, 6))
        tries = 0
        while len(boxes) + len(cyls) < 4 + n and tries < 500:
            _random_obstacle(rng, boxes, cyls, keep_out)
            tries += 1
    elif family == "narrow_gap":
        gap = rng.uniform(0.5, 0.9)
        pos = rng.uniform(8.0, 12.0)              # wall position along its normal axis
        gc = rng.uniform(3.0, AREA - 3.0)         # gap centre along the wall
        t = 0.15
        lo_len = gc - gap / 2
        hi_len = AREA - (gc + gap / 2)
        vertical = bool(rng.random() < 0.5)       # True: wall at x = pos
        segs = [(lo_len / 2, lo_len / 2), (gc + gap / 2 + hi_len / 2, hi_len / 2)]
        for c, h in segs:
            boxes.append((pos, c, t, h) if vertical else (c, pos, h, t))
        if vertical:
            keep_out.append((pos, gc, 1.5))
        else:
            keep_out.append((gc, pos, 1.5))
        n = int(rng.integers(3, 7))
        tries = 0
        while len(boxes) + len(cyls) < 2 + n and tries < 500:
            _random_obstacle(rng, boxes, cyls, keep_out)
            tries += 1
        # drop clutter within 0.6 m of the wall line (it could seal the gap or merge with the wall)
        axis = 0 if vertical else 1
        boxes = boxes[:2] + [bx for bx in boxes[2:] if abs(bx[axis] - pos) > bx[2 + axis] + t + 0.6]
        cyls = [c for c in cyls if abs(c[axis] - pos) > c[2] + t + 0.6]
    else:
        raise ValueError(f"unknown family {family!r}, expected one of {FAMILIES}")
    return a, b, boxes, cyls


def make_world(family: str = "random", seed: int = 0, index: int = 0,
               radius: float = RADIUS, res: float = RES, max_attempts: int = 200) -> World:
    """Deterministic layout for (family, seed, index). Resamples until BFS finds a free path."""
    rng = np.random.default_rng([seed, index, _FAMILY_CODE[family]])
    for attempt in range(1, max_attempts + 1):
        a, b, boxes, cyls = _layout(family, rng)
        ax, ay = a
        w = World(family=family, seed=seed,
                  xmin=-ax, ymin=-ay, xmax=AREA - ax, ymax=AREA - ay,
                  goal=(b[0] - ax, b[1] - ay),
                  boxes=[Box(cx - ax, cy - ay, hx, hy) for cx, cy, hx, hy in boxes],
                  cylinders=[Cylinder(cx - ax, cy - ay, r) for cx, cy, r in cyls],
                  attempts=attempt)
        w.grid = w.rasterize(res)
        blocked = w.grid.inflated(radius)
        if bfs_free_path(blocked, w.grid.to_index(0.0, 0.0), w.grid.to_index(*w.goal)) is not None:
            return w
    raise RuntimeError(f"no free layout for {family} seed {seed} index {index} in {max_attempts} tries")
