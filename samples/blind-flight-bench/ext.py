"""Load modules from sibling samples by file path, so their sim.py/core.py never shadow ours."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HEIGHTMAP_PF = os.path.join(HERE, "..", "terrain-heightmap-pf")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fetch_dem = _load("hpf_fetch_dem", os.path.join(HEIGHTMAP_PF, "fetch_dem.py"))
hpf_core = _load("hpf_core", os.path.join(HEIGHTMAP_PF, "core.py"))
