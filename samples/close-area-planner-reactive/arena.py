"""Load samples/close-area-arena as package close_area_arena (recipe from its CONTRACT.md "Import").

Its run.py / world.py never shadow files in this folder.
"""
import copy
import importlib
import importlib.util
import math
import os
import sys

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
Planner = base.Planner
Setpoint = adapter.Setpoint

# Fans. "default" is the arena default (72 beams, 360 deg, 6 m). "cf4" is a Crazyflie Multi-ranger
# style fan: 4 horizontal beams (with fov = 360 deg the arena places them at -180, -90, 0, +90 deg
# = back, right, front, left), 4 m range; noise and dropout kept at the arena defaults.
FANS = {
    "default": dict(run.DEFAULTS["sensor"]),
    "cf4": dict(run.DEFAULTS["sensor"], n_beams=4, fov=2 * math.pi, max_range=4.0),
}


def cfg_for(fan: str) -> dict:
    cfg = copy.deepcopy(run.DEFAULTS)
    cfg["sensor"] = dict(FANS[fan])
    return cfg
