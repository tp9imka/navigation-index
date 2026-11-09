"""Load samples/close-area-arena as package close_area_arena (recipe from its CONTRACT.md "Import").

Its run.py / world.py never shadow files in this folder. No arena file is edited.
"""
import importlib
import importlib.util
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
astar_esdf = importlib.import_module("close_area_arena.planners.astar_esdf")
Setpoint = adapter.Setpoint
