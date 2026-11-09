"""Load samples/close-area-arena as package close_area_arena (recipe from its CONTRACT.md "Import").

Its run.py / world.py never shadow files in this folder. Also builds narrow_gap layouts with a
fixed gap width for the sweep (gap_world), without editing the arena.
"""
import importlib
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ARENA = os.path.normpath(os.path.join(HERE, "..", "close-area-arena"))


def load():
    if "close_area_arena" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "close_area_arena", os.path.join(ARENA, "__init__.py"), submodule_search_locations=[ARENA])
        pkg = importlib.util.module_from_spec(spec)
        sys.modules["close_area_arena"] = pkg
        spec.loader.exec_module(pkg)
    return sys.modules["close_area_arena"]


load()
run = importlib.import_module("close_area_arena.run")
world = importlib.import_module("close_area_arena.world")
adapter = importlib.import_module("close_area_arena.adapter")
base = importlib.import_module("close_area_arena.planners.base")
astar_esdf = importlib.import_module("close_area_arena.planners.astar_esdf")
Planner = base.Planner
Setpoint = adapter.Setpoint
Pose = adapter.Pose


def _narrow_gap_layout(rng, gap_override):
    """Copy of the narrow_gap branch of world._layout. Draws the same random numbers in the same
    order, then replaces the drawn gap width with gap_override (None keeps the drawn one)."""
    AREA = world.AREA
    a = (1.5 + rng.uniform(-0.5, 0.5), 1.5 + rng.uniform(-0.5, 0.5))
    b = (AREA - 1.5 + rng.uniform(-0.5, 0.5), AREA - 1.5 + rng.uniform(-0.5, 0.5))
    boxes, cyls = [], []
    keep_out = [(a[0], a[1], 1.0), (b[0], b[1], 1.0)]
    gap = rng.uniform(0.5, 0.9)
    if gap_override is not None:
        gap = float(gap_override)
    pos = rng.uniform(8.0, 12.0)
    gc = rng.uniform(3.0, AREA - 3.0)
    t = 0.15
    lo_len = gc - gap / 2
    hi_len = AREA - (gc + gap / 2)
    vertical = bool(rng.random() < 0.5)
    segs = [(lo_len / 2, lo_len / 2), (gc + gap / 2 + hi_len / 2, hi_len / 2)]
    for c, h in segs:
        boxes.append((pos, c, t, h) if vertical else (c, pos, h, t))
    keep_out.append((pos, gc, 1.5) if vertical else (gc, pos, 1.5))
    n = int(rng.integers(3, 7))
    tries = 0
    while len(boxes) + len(cyls) < 2 + n and tries < 500:
        world._random_obstacle(rng, boxes, cyls, keep_out)
        tries += 1
    axis = 0 if vertical else 1
    boxes = boxes[:2] + [bx for bx in boxes[2:] if abs(bx[axis] - pos) > bx[2 + axis] + t + 0.6]
    cyls = [c for c in cyls if abs(c[axis] - pos) > c[2] + t + 0.6]
    return a, b, boxes, cyls, gap


def gap_world(gap, seed=0, index=0, radius=world.RADIUS, res=world.RES, max_attempts=200):
    """narrow_gap layout (seed, index) with its gap set to `gap` metres. Same rng stream as
    world.make_world("narrow_gap", seed, index), so gap=None reproduces the arena layout and the
    widths of one index share wall position, gap centre and clutter (unless BFS resampled)."""
    rng = np.random.default_rng([seed, index, world.FAMILIES.index("narrow_gap")])
    for attempt in range(1, max_attempts + 1):
        a, b, boxes, cyls, g = _narrow_gap_layout(rng, gap)
        ax, ay = a
        w = world.World(family="narrow_gap", seed=seed,
                        xmin=-ax, ymin=-ay, xmax=world.AREA - ax, ymax=world.AREA - ay,
                        goal=(b[0] - ax, b[1] - ay),
                        boxes=[world.Box(cx - ax, cy - ay, hx, hy) for cx, cy, hx, hy in boxes],
                        cylinders=[world.Cylinder(cx - ax, cy - ay, r) for cx, cy, r in cyls],
                        attempts=attempt)
        w.gap_m = g
        w.grid = w.rasterize(res)
        blocked = w.grid.inflated(radius)
        if world.bfs_free_path(blocked, w.grid.to_index(0.0, 0.0), w.grid.to_index(*w.goal)) is not None:
            return w
    return None          # no free path at this width (the 4-connected BFS rejects it)
