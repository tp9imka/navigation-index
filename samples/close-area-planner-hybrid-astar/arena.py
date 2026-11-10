"""Load samples/close-area-arena as package close_area_arena (recipe from its CONTRACT.md "Import").

Its run.py / world.py never shadow files in this folder. Imports only the arena modules the
planner needs (adapter, planners.base, planners.astar_esdf), so hybrid_astar.py also loads in the
browser playground, where close_area_arena is already in sys.modules.
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


def mod(name: str):
    """close_area_arena.<name>, e.g. mod("run") or mod("world_glass")."""
    load()
    return importlib.import_module(f"close_area_arena.{name}")


load()
adapter = mod("adapter")
base = mod("planners.base")
astar_esdf = mod("planners.astar_esdf")
Planner = base.Planner
Setpoint = adapter.Setpoint
Pose = adapter.Pose
