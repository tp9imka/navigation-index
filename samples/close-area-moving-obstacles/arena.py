"""Load the arena, the F2 filter and the APF planner from their sibling samples, by path.

Arena: samples/close-area-arena as package close_area_arena (recipe from its CONTRACT.md
"Import"; copied from samples/close-area-safety-filter/arena.py). filters.py comes from
samples/close-area-safety-filter and apf.py from samples/close-area-planner-reactive, each
loaded under its own module name so the sibling arena.py files never shadow this one. apf.py
does `from arena import Planner, Setpoint`; this module exports both, so that import resolves
here. No sibling file is edited.
"""
import importlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.normpath(os.path.join(HERE, ".."))
ARENA = os.path.join(SAMPLES, "close-area-arena")


def load():
    if "close_area_arena" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "close_area_arena", os.path.join(ARENA, "__init__.py"), submodule_search_locations=[ARENA])
        pkg = importlib.util.module_from_spec(spec)
        sys.modules["close_area_arena"] = pkg
        spec.loader.exec_module(pkg)
    return sys.modules["close_area_arena"]


def _by_path(name: str, path: str):
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


load()
run = importlib.import_module("close_area_arena.run")
world = importlib.import_module("close_area_arena.world")
adapter = importlib.import_module("close_area_arena.adapter")
sensors = importlib.import_module("close_area_arena.sensors")
vehicle = importlib.import_module("close_area_arena.vehicle")
scorer = importlib.import_module("close_area_arena.scorer")
astar_esdf = importlib.import_module("close_area_arena.planners.astar_esdf")
Planner = importlib.import_module("close_area_arena.planners.base").Planner
Setpoint = adapter.Setpoint

if "arena" not in sys.modules:          # run as a script: make `from arena import ...` find this file
    sys.modules["arena"] = sys.modules[__name__]

filters = _by_path("safety_filter_filters", os.path.join(SAMPLES, "close-area-safety-filter", "filters.py"))
apf = _by_path("reactive_apf", os.path.join(SAMPLES, "close-area-planner-reactive", "apf.py"))
