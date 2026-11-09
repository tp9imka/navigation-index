"""Layout family "glass": obstacles a Crazyflie Multi-ranger misses, on the arena world generator.

Each layout (area frame, then shifted to the A origin like world.make_world):
- 1-3 glass panels (axis-aligned boxes, 0.04 m thick, 1.2-3.0 m long) centred on or within
  0.6 m of the A-B line, between 25 % and 80 % of the way. Material "glass".
- 2-5 thin poles (cylinders, diameter 0.02-0.05 m) within 0.8 m of the A-B line. Material "pole".
  Poles are matte for the sensor; they are missed only through the cone fill rule.
- 4-8 clutter obstacles from world._random_obstacle; each is "dark" with probability 0.3, else
  "matte".
Basis: doc 08 sections 2.4 and 6 (glass doors and thin poles are the unsensed classes; the
family itself is the proposal from section 6). Sizes are arena choices, not measurements.

Materials live in world.materials = {"boxes": [...], "cylinders": [...]}, parallel to
world.boxes / world.cylinders. Only sensors_cone.ConeRangeFan reads them. Truth geometry
(world.sdf, world.clearance, the prior grid, the free-path check) contains every obstacle.

make_any_world(family, seed, index) serves "glass" here and the arena families via
world.make_world (all obstacles "matte").
"""
from __future__ import annotations

import numpy as np

try:
    from . import world as W
except ImportError:
    import world as W

FAMILIES = W.FAMILIES + ("glass",)
GLASS_CODE = 10                  # rng stream id; arena families use 0-2
PANEL_HALF_T = 0.02              # m, half thickness of a glass panel
PANEL_HALF_LEN = (0.6, 1.5)      # m
POLE_R = (0.01, 0.025)           # m, radius => 0.02-0.05 m diameter
DARK_P = 0.3


def _glass_layout(rng):
    A = W.AREA
    a = (1.5 + rng.uniform(-0.5, 0.5), 1.5 + rng.uniform(-0.5, 0.5))
    b = (A - 1.5 + rng.uniform(-0.5, 0.5), A - 1.5 + rng.uniform(-0.5, 0.5))
    ab = np.array([b[0] - a[0], b[1] - a[1]])
    u = ab / np.linalg.norm(ab)
    nrm = np.array([-u[1], u[0]])
    boxes, bmat, cyls, cmat = [], [], [], []
    keep_out = [(a[0], a[1], 1.0), (b[0], b[1], 1.0)]

    def on_line(f, off):
        p = np.array(a) + f * ab + off * nrm
        return float(p[0]), float(p[1])

    for _ in range(int(rng.integers(1, 4))):
        cx, cy = on_line(rng.uniform(0.25, 0.8), rng.uniform(-0.6, 0.6))
        hl = rng.uniform(*PANEL_HALF_LEN)
        if rng.random() < 0.5:
            boxes.append((cx, cy, hl, PANEL_HALF_T))
        else:
            boxes.append((cx, cy, PANEL_HALF_T, hl))
        bmat.append("glass")
    for _ in range(int(rng.integers(2, 6))):
        cx, cy = on_line(rng.uniform(0.15, 0.85), rng.uniform(-0.8, 0.8))
        cyls.append((cx, cy, rng.uniform(*POLE_R)))
        cmat.append("pole")
    n = int(rng.integers(4, 9))
    placed, tries = 0, 0
    while placed < n and tries < 500:
        nb = len(boxes)
        if W._random_obstacle(rng, boxes, cyls, keep_out):
            m = "dark" if rng.random() < DARK_P else "matte"
            (bmat if len(boxes) > nb else cmat).append(m)
            placed += 1
        tries += 1
    return a, b, boxes, cyls, bmat, cmat


def make_glass_world(seed: int = 0, index: int = 0, radius: float = W.RADIUS,
                     res: float = W.RES, max_attempts: int = 200) -> W.World:
    """Deterministic glass layout for (seed, index). Resamples until BFS finds a free path on
    the true grid (glass included) inflated by `radius`."""
    rng = np.random.default_rng([seed, index, GLASS_CODE])
    for attempt in range(1, max_attempts + 1):
        a, b, boxes, cyls, bmat, cmat = _glass_layout(rng)
        ax, ay = a
        w = W.World(family="glass", seed=seed,
                    xmin=-ax, ymin=-ay, xmax=W.AREA - ax, ymax=W.AREA - ay,
                    goal=(b[0] - ax, b[1] - ay),
                    boxes=[W.Box(cx - ax, cy - ay, hx, hy) for cx, cy, hx, hy in boxes],
                    cylinders=[W.Cylinder(cx - ax, cy - ay, r) for cx, cy, r in cyls],
                    attempts=attempt)
        w.materials = {"boxes": bmat, "cylinders": cmat}
        w.grid = w.rasterize(res)
        for c in w.cylinders:            # a 0.02 m pole can fall between cell centres
            ix, iy = w.grid.to_index(c.cx, c.cy)
            if 0 <= ix < w.grid.occ.shape[0] and 0 <= iy < w.grid.occ.shape[1]:
                w.grid.occ[ix, iy] = True
        blocked = w.grid.inflated(radius)
        if W.bfs_free_path(blocked, w.grid.to_index(0.0, 0.0), w.grid.to_index(*w.goal)) is not None:
            return w
    raise RuntimeError(f"no free glass layout for seed {seed} index {index} in {max_attempts} tries")


def make_any_world(family: str, seed: int = 0, index: int = 0, radius: float = W.RADIUS) -> W.World:
    if family == "glass":
        return make_glass_world(seed, index, radius)
    w = W.make_world(family, seed, index, radius=radius)
    w.materials = {"boxes": ["matte"] * len(w.boxes), "cylinders": ["matte"] * len(w.cylinders)}
    return w


def nearest_material(w: W.World, x: float, y: float) -> tuple[str, float]:
    """Material of the surface closest to (x, y) ("wall" for the area walls) and its distance."""
    p = np.array([x, y])
    best = ("wall", min(x - w.xmin, w.xmax - x, y - w.ymin, w.ymax - y))
    mats = getattr(w, "materials", {}) or {}
    for i, bx in enumerate(w.boxes):
        q = np.abs(p - (bx.cx, bx.cy)) - (bx.hx, bx.hy)
        d = float(np.linalg.norm(np.maximum(q, 0.0)) + min(q.max(), 0.0))
        if d < best[1]:
            best = (mats.get("boxes", ["matte"] * (i + 1))[i], d)
    for i, c in enumerate(w.cylinders):
        d = float(np.hypot(x - c.cx, y - c.cy) - c.r)
        if d < best[1]:
            best = (mats.get("cylinders", ["matte"] * (i + 1))[i], d)
    return best[0], round(best[1], 4)


def to_dict(w: W.World) -> dict:
    d = w.to_dict()
    d["materials"] = getattr(w, "materials", None)
    return d
