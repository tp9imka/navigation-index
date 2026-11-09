"""3D close-area world: walls with windows, horizontal bars, pillars and crates under a 3 m ceiling.

Family 'window_bar' (IMAV indoor style). Two walls cross the whole 20 m width between A and B.
Each wall carries one element:
  window  a 0.6 x 0.6 m hole, centre height uniform in [0.5, 2.5] m
  bars    a 1.2-2.0 m wide floor-to-ceiling opening crossed by 1 or 2 horizontal bars
          (0.1 m thick) at heights in [0.4, 2.6] m: fly under, between or over them
At least one of the two walls is a window. Between the walls: 2-5 floor-to-ceiling pillars and
0-3 crates (floor to 0.4-1.4 m) that a 3D planner can fly over.

Frames: local ENU, metres, origin of x, y at point A. z is height above the floor (floor z = 0,
ceiling z = CEILING). A and B are at z = 1.0 m. Every obstacle is an axis-aligned Box3 with its own
z range. Truth geometry is exact (analytic signed distance in 3D); the 0.1 m OccGrid3 is what a
planner gets. Layouts are deterministic by (family, seed, index) and resampled until the 3D grid
inflated by the vehicle radius has a 6-connected free path A => B.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import distance_transform_edt, label

try:
    from . import world as world2d
except ImportError:
    import world as world2d

AREA = 20.0          # m, square side
CEILING = 3.0        # m
RES = 0.1            # m, grid cell
RADIUS = 0.15        # m, vehicle radius (CONTRACT.md)
Z_AB = 1.0           # m, height of A and B
WINDOW = 0.6         # m, window side
WALL_HALF = 0.1      # m, wall half thickness
BAR_HALF = 0.05      # m, bar half thickness (z)
FAMILIES = ("window_bar",)
_FAMILY_CODE = {"window_bar": 40}     # 0-2 world.py, 20-24 worlds_complex.py


@dataclass
class Box3:           # axis-aligned, centre and half sizes
    cx: float
    cy: float
    cz: float
    hx: float
    hy: float
    hz: float
    kind: str = "box"  # wall | bar | pillar | crate

    @property
    def zlo(self) -> float:
        return self.cz - self.hz

    @property
    def zhi(self) -> float:
        return self.cz + self.hz


@dataclass
class OccGrid3:
    """occ[ix, iy, iz] is True when the cell is occupied. Cell (ix, iy, iz) covers
    x in [x0 + ix*res, x0 + (ix+1)*res), same for y and z. Outside the grid (walls, floor,
    ceiling) counts as occupied."""
    occ: np.ndarray
    res: float
    x0: float
    y0: float
    z0: float

    def to_index(self, x: float, y: float, z: float) -> tuple[int, int, int]:
        return (int(np.floor((x - self.x0) / self.res)), int(np.floor((y - self.y0) / self.res)),
                int(np.floor((z - self.z0) / self.res)))

    def to_xyz(self, ix: int, iy: int, iz: int) -> tuple[float, float, float]:
        return (self.x0 + (ix + 0.5) * self.res, self.y0 + (iy + 0.5) * self.res,
                self.z0 + (iz + 0.5) * self.res)

    def esdf(self) -> np.ndarray:
        """Distance in metres from each free cell centre to the nearest occupied cell (0 inside)."""
        padded = np.pad(self.occ, 1, constant_values=True)
        return (distance_transform_edt(~padded) * self.res)[1:-1, 1:-1, 1:-1]


def _index_range(lo: float, hi: float, origin: float, res: float, n: int) -> tuple[int, int]:
    """Cells whose centre lies in [lo - res/2, hi + res/2] (same rule as world.rasterize)."""
    a = int(math.ceil((lo - res / 2 - origin) / res - 0.5 - 1e-9))
    b = int(math.floor((hi + res / 2 - origin) / res - 0.5 + 1e-9))
    return max(a, 0), min(b, n - 1)


@dataclass
class WorldZ:
    family: str
    seed: int
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    goal: tuple[float, float, float]     # point B
    boxes: list[Box3] = field(default_factory=list)
    zmin: float = 0.0
    zmax: float = CEILING
    grid: OccGrid3 | None = None
    attempts: int = 1
    elements: list[dict] = field(default_factory=list)   # per wall: kind, height(s), position

    def __post_init__(self):
        self._pack()

    def _pack(self):
        self._c = np.array([[b.cx, b.cy, b.cz] for b in self.boxes]).reshape(-1, 3)
        self._h = np.array([[b.hx, b.hy, b.hz] for b in self.boxes]).reshape(-1, 3)

    # ---- exact geometry ----
    def sdf(self, xyz) -> np.ndarray:
        """Signed distance (m) from points (..., 3) to the nearest obstacle, wall, floor or ceiling.
        Positive in free space."""
        p = np.asarray(xyz, dtype=float)
        shp = p.shape[:-1]
        p = p.reshape(-1, 3)
        d = np.minimum.reduce([p[:, 0] - self.xmin, self.xmax - p[:, 0], p[:, 1] - self.ymin,
                               self.ymax - p[:, 1], p[:, 2] - self.zmin, self.zmax - p[:, 2]])
        if len(self._c):
            for k in range(0, len(p), 4000):
                q = np.abs(p[k:k + 4000, None, :] - self._c[None]) - self._h[None]
                db = (np.linalg.norm(np.maximum(q, 0.0), axis=2) + np.minimum(q.max(axis=2), 0.0)).min(axis=1)
                d[k:k + 4000] = np.minimum(d[k:k + 4000], db)
        return d.reshape(shp)

    def clearance(self, x: float, y: float, z: float) -> float:
        return float(self.sdf(np.array([x, y, z])))

    def raycast(self, x: float, y: float, z: float, angles: np.ndarray, max_range: float) -> np.ndarray:
        """Horizontal rays from (x, y, z) along world-frame `angles`. Only boxes whose z range
        contains z can be hit. Returns np.inf where nothing is hit within max_range."""
        a = np.asarray(angles, dtype=float)
        dx, dy = np.cos(a), np.sin(a)
        best = np.full(a.shape, np.inf)
        sel = (self._c[:, 2] - self._h[:, 2] <= z) & (z <= self._c[:, 2] + self._h[:, 2])
        c, h = self._c[sel, :2], self._h[sel, :2]
        with np.errstate(divide="ignore", invalid="ignore"):
            tx = np.where(dx > 0, (self.xmax - x) / dx, np.where(dx < 0, (self.xmin - x) / dx, np.inf))
            ty = np.where(dy > 0, (self.ymax - y) / dy, np.where(dy < 0, (self.ymin - y) / dy, np.inf))
            best = np.minimum(best, np.maximum(np.minimum(tx, ty), 0.0))
            if len(c):
                lo, hi = c - h, c + h
                t1x = (lo[None, :, 0] - x) / dx[:, None]
                t2x = (hi[None, :, 0] - x) / dx[:, None]
                t1y = (lo[None, :, 1] - y) / dy[:, None]
                t2y = (hi[None, :, 1] - y) / dy[:, None]
                tmin = np.nan_to_num(np.maximum(np.minimum(t1x, t2x), np.minimum(t1y, t2y)), nan=-np.inf)
                tmax = np.nan_to_num(np.minimum(np.maximum(t1x, t2x), np.maximum(t1y, t2y)), nan=-np.inf)
                th = np.where(tmax >= np.maximum(tmin, 0.0), np.maximum(tmin, 0.0), np.inf)
                best = np.minimum(best, th.min(axis=1))
        return np.where(best <= max_range, best, np.inf)

    def at_height(self, z: float):
        """View with the 2D raycast signature (x, y, angles, max_range) at a fixed height,
        so sensors.RangeFan works unchanged."""
        w = self

        class _View:
            def raycast(self, x, y, angles, max_range):
                return w.raycast(x, y, z, angles, max_range)
        return _View()

    def box_in(self, b: Box3, x: float, y: float, z: float) -> bool:
        return abs(x - b.cx) <= b.hx and abs(y - b.cy) <= b.hy and abs(z - b.cz) <= b.hz

    # ---- grids ----
    def rasterize(self, res: float = RES) -> OccGrid3:
        """Cell is occupied when its centre is inside a box grown by res/2 on every side."""
        nx = int(round((self.xmax - self.xmin) / res))
        ny = int(round((self.ymax - self.ymin) / res))
        nz = int(round((self.zmax - self.zmin) / res))
        occ = np.zeros((nx, ny, nz), dtype=bool)
        for b in self.boxes:
            i0, i1 = _index_range(b.cx - b.hx, b.cx + b.hx, self.xmin, res, nx)
            j0, j1 = _index_range(b.cy - b.hy, b.cy + b.hy, self.ymin, res, ny)
            k0, k1 = _index_range(b.zlo, b.zhi, self.zmin, res, nz)
            if i0 <= i1 and j0 <= j1 and k0 <= k1:
                occ[i0:i1 + 1, j0:j1 + 1, k0:k1 + 1] = True
        return OccGrid3(occ=occ, res=res, x0=self.xmin, y0=self.ymin, z0=self.zmin)

    def slice_2d(self, z_lo: float, z_hi: float, res: float = RES) -> world2d.OccGrid:
        """2D OccGrid (world.OccGrid) of every box whose z range overlaps [z_lo, z_hi]:
        the map a 2.5D planner flying in that height band needs."""
        nx = int(round((self.xmax - self.xmin) / res))
        ny = int(round((self.ymax - self.ymin) / res))
        occ = np.zeros((nx, ny), dtype=bool)
        for b in self.boxes:
            if b.zlo <= z_hi and b.zhi >= z_lo:
                i0, i1 = _index_range(b.cx - b.hx, b.cx + b.hx, self.xmin, res, nx)
                j0, j1 = _index_range(b.cy - b.hy, b.cy + b.hy, self.ymin, res, ny)
                if i0 <= i1 and j0 <= j1:
                    occ[i0:i1 + 1, j0:j1 + 1] = True
        return world2d.OccGrid(occ=occ, res=res, x0=self.xmin, y0=self.ymin)

    def to_dict(self) -> dict:
        return {"family": self.family, "seed": self.seed, "attempts": self.attempts,
                "area": [self.xmin, self.ymin, self.zmin, self.xmax, self.ymax, self.zmax],
                "goal": list(self.goal), "elements": self.elements,
                "boxes": [[b.cx, b.cy, b.cz, b.hx, b.hy, b.hz, b.kind] for b in self.boxes]}


def free_path_3d(blocked: np.ndarray, start, goal) -> bool:
    """6-connected: start and goal cells in the same free component."""
    for c in (start, goal):
        if not all(0 <= c[i] < blocked.shape[i] for i in range(3)) or blocked[c]:
            return False
    lab, _ = label(~blocked)
    return bool(lab[start] == lab[goal])


def passable_2d(grid2d: world2d.OccGrid, radius: float, start_xy, goal_xy) -> bool:
    """4-connected BFS on the 2D grid inflated by radius (world.bfs_free_path)."""
    blk = grid2d.inflated(radius)
    return world2d.bfs_free_path(blk, grid2d.to_index(*start_xy), grid2d.to_index(*goal_xy)) is not None


# ---- layout (area frame [0, AREA]^2, shifted to the A origin at the end) ----

def _wall_boxes(y, kind, rng):
    """Boxes of one full-width wall at y, plus a description of its element."""
    t, H = WALL_HALF, CEILING
    boxes = []

    def span(x_lo, x_hi, z_lo, z_hi, k="wall"):
        if x_hi - x_lo > 1e-6 and z_hi - z_lo > 1e-6:
            boxes.append(((x_lo + x_hi) / 2, y, (z_lo + z_hi) / 2, (x_hi - x_lo) / 2, t, (z_hi - z_lo) / 2, k))

    if kind == "window":
        wx = rng.uniform(2.5, AREA - 2.5)
        wz = rng.uniform(0.5, 2.5)
        h = WINDOW / 2
        span(0.0, wx - h, 0.0, H)
        span(wx + h, AREA, 0.0, H)
        span(wx - h, wx + h, 0.0, wz - h)
        span(wx - h, wx + h, wz + h, H)
        elem = {"kind": "window", "x": round(wx, 3), "y": round(y, 3), "z_centre": round(wz, 3),
                "z_range": [round(wz - h, 3), round(wz + h, 3)]}
        return boxes, elem, (wx, y)
    ox = rng.uniform(2.5, AREA - 2.5)
    ow = rng.uniform(1.2, 2.0)
    span(0.0, ox - ow / 2, 0.0, H)
    span(ox + ow / 2, AREA, 0.0, H)
    n = int(rng.integers(1, 3))
    zs = [float(rng.uniform(0.4, 2.6))]
    if n == 2:
        for _ in range(50):
            z2 = float(rng.uniform(0.4, 2.6))
            if abs(z2 - zs[0]) >= 0.8:
                zs.append(z2)
                break
    zs.sort()
    for bz in zs:
        boxes.append((ox, y, bz, ow / 2, t, BAR_HALF, "bar"))
    elem = {"kind": "bars", "x": round(ox, 3), "y": round(y, 3), "opening_m": round(ow, 3),
            "bar_z": [round(z, 3) for z in zs]}
    return boxes, elem, (ox, y)


def _layout(rng):
    a = (1.5 + rng.uniform(-0.5, 0.5), 1.5 + rng.uniform(-0.5, 0.5))
    b = (AREA - 1.5 + rng.uniform(-0.5, 0.5), AREA - 1.5 + rng.uniform(-0.5, 0.5))
    ys = [rng.uniform(6.0, 8.0), rng.uniform(12.0, 14.0)]
    kinds = ["window" if rng.random() < 0.5 else "bars" for _ in ys]
    if "window" not in kinds:
        kinds[int(rng.integers(0, 2))] = "window"
    boxes, elements, keep = [], [], [(a[0], a[1], 1.2), (b[0], b[1], 1.2)]
    for y, k in zip(ys, kinds):
        bx, el, c = _wall_boxes(y, k, rng)
        boxes += bx
        elements.append(el)
        keep.append((c[0], c[1], 1.5))
    bands = [(ys[0] + 1.0, ys[1] - 1.0), (0.5, ys[0] - 1.0), (ys[1] + 1.0, AREA - 0.5)]

    def place(kind, n, tries=300):
        k = 0
        while n > 0 and k < tries:
            k += 1
            y_lo, y_hi = bands[int(rng.integers(0, 3))]
            if kind == "pillar":
                hx, hy = rng.uniform(0.15, 0.5, size=2)
                z_lo, z_hi = 0.0, CEILING
            else:
                hx, hy = rng.uniform(0.3, 1.0, size=2)
                z_lo, z_hi = 0.0, float(rng.uniform(0.4, 1.4))
            if y_hi - y_lo < 2 * hy + 0.2:
                continue
            cx = rng.uniform(0.5 + hx, AREA - 0.5 - hx)
            cy = rng.uniform(y_lo + hy, y_hi - hy)
            reach = math.hypot(hx, hy)
            if any(math.hypot(cx - kx, cy - ky) < kr + reach for kx, ky, kr in keep):
                continue
            boxes.append((cx, cy, (z_lo + z_hi) / 2, hx, hy, (z_hi - z_lo) / 2, kind))
            keep.append((cx, cy, reach + 0.3))
            n -= 1

    place("pillar", int(rng.integers(2, 6)))
    place("crate", int(rng.integers(0, 4)))
    return a, b, boxes, elements


def make_world(family: str = "window_bar", seed: int = 0, index: int = 0, radius: float = RADIUS,
               res: float = RES, max_attempts: int = 200) -> WorldZ:
    """Deterministic layout for (family, seed, index). Resamples until a 3D free path exists."""
    if family not in _FAMILY_CODE:
        raise ValueError(f"unknown family {family!r}, expected one of {FAMILIES}")
    rng = np.random.default_rng([seed, index, _FAMILY_CODE[family]])
    for attempt in range(1, max_attempts + 1):
        a, b, boxes, elements = _layout(rng)
        ax, ay = a
        for el in elements:
            el["x"], el["y"] = round(el["x"] - ax, 3), round(el["y"] - ay, 3)
        w = WorldZ(family=family, seed=seed, xmin=-ax, ymin=-ay, xmax=AREA - ax, ymax=AREA - ay,
                   goal=(b[0] - ax, b[1] - ay, Z_AB),
                   boxes=[Box3(cx - ax, cy - ay, cz, hx, hy, hz, k) for cx, cy, cz, hx, hy, hz, k in boxes],
                   attempts=attempt, elements=elements)
        w.grid = w.rasterize(res)
        blocked = w.grid.esdf() <= radius + 1e-9
        if free_path_3d(blocked, w.grid.to_index(0.0, 0.0, Z_AB), w.grid.to_index(*w.goal)):
            return w
    raise RuntimeError(f"no free layout for {family} seed {seed} index {index} in {max_attempts} tries")
