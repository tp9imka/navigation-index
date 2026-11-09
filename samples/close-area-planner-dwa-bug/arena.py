"""Load samples/close-area-arena as package close_area_arena (recipe from its CONTRACT.md "Import"),
and samples/close-area-planner-reactive as package close_area_planner_reactive (for APF and VFH+).

Neither folder's run.py / arena.py shadows files here. No file in either folder is edited.
"""
import copy
import heapq
import importlib
import importlib.util
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ARENA = os.path.normpath(os.path.join(HERE, "..", "close-area-arena"))
REACTIVE = os.path.normpath(os.path.join(HERE, "..", "close-area-planner-reactive"))


def _load_pkg(name: str, folder: str, init: str | None):
    if name in sys.modules:
        return sys.modules[name]
    if init is None:     # folder without __init__.py: namespace-like package
        spec = importlib.util.spec_from_loader(name, loader=None, is_package=True)
        pkg = importlib.util.module_from_spec(spec)
        pkg.__path__ = [folder]
        sys.modules[name] = pkg
        return pkg
    spec = importlib.util.spec_from_file_location(name, init, submodule_search_locations=[folder])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[name] = pkg
    spec.loader.exec_module(pkg)
    return pkg


_load_pkg("close_area_arena", ARENA, os.path.join(ARENA, "__init__.py"))
run = importlib.import_module("close_area_arena.run")
world = importlib.import_module("close_area_arena.world")
adapter = importlib.import_module("close_area_arena.adapter")
base = importlib.import_module("close_area_arena.planners.base")
Planner = base.Planner
Setpoint = adapter.Setpoint
VEHICLE = dict(run.DEFAULTS["vehicle"])      # tau 0.15 s, a_max 3 m/s^2, v_max 2 m/s, radius 0.15 m


def reactive():
    """(apf module, vfh_plus module) from the reactive sample, sharing this arena package."""
    _load_pkg("close_area_planner_reactive", REACTIVE, None)
    return (importlib.import_module("close_area_planner_reactive.apf"),
            importlib.import_module("close_area_planner_reactive.vfh_plus"))


# Same fans as the reactive sample: arena default (72 beams, 360 deg, 6 m) and "cf4", a
# Crazyflie Multi-ranger style fan of 4 beams (back, right, front, left), 4 m.
FANS = {
    "default": dict(run.DEFAULTS["sensor"]),
    "cf4": dict(run.DEFAULTS["sensor"], n_beams=4, fov=2 * math.pi, max_range=4.0),
}


def cfg_for(fan: str) -> dict:
    cfg = copy.deepcopy(run.DEFAULTS)
    cfg["sensor"] = dict(FANS[fan])
    return cfg


def astar_length(w, radius: float = VEHICLE["radius"]) -> float | None:
    """Known-map reference length, m: 8-connected A* on the layout's 0.1 m grid inflated by the
    vehicle radius, from A to B. Report only; planners never see it. 8-connected paths overestimate
    the any-angle shortest path by up to about 8 %, so path ratios against it are slightly low."""
    g = w.grid
    blocked = g.inflated(radius)
    nx, ny = blocked.shape
    s, t = g.to_index(0.0, 0.0), g.to_index(*w.goal)
    blk = blocked.tolist()
    sq2 = math.sqrt(2.0)
    h = lambda i, j: (abs(i - t[0]) + abs(j - t[1]) + (sq2 - 2) * min(abs(i - t[0]), abs(j - t[1])))
    best = {s: 0.0}
    pq = [(h(*s), 0.0, s)]
    moves = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
             (1, 1, sq2), (1, -1, sq2), (-1, 1, sq2), (-1, -1, sq2)]
    while pq:
        _, gc, (i, j) = heapq.heappop(pq)
        if (i, j) == t:
            return round(gc * g.res, 3)
        if gc > best.get((i, j), math.inf):
            continue
        for di, dj, c in moves:
            a, b = i + di, j + dj
            if not (0 <= a < nx and 0 <= b < ny) or blk[a][b]:
                continue
            if di and dj and (blk[i + di][j] or blk[i][j + dj]):
                continue                       # no corner cutting
            ng = gc + c
            if ng < best.get((a, b), math.inf):
                best[(a, b)] = ng
                heapq.heappush(pq, (ng + h(a, b), ng, (a, b)))
    return None


__all__ = ["run", "world", "adapter", "Planner", "Setpoint", "VEHICLE", "FANS", "cfg_for",
           "reactive", "astar_length", "np"]
