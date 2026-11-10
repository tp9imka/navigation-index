"""Build any close-area-benchmark planner by id (`--planner bench:<id>`), synthetic sim only.

    pl, arm = make("dstar_lite", bench_dir, world)     # world = ArenaAdapter.world
    rows = describe(bench_dir)                          # id, label, sample, needs_world, loaded

- Loads samples/close-area-benchmark/bench.py by path (spec_from_file_location), like
  site/playground/worker.js loads sample folders: nothing in the hub is edited or installed.
  bench.py itself loads the arena and each planner sample from its own folder (`../<sample>`),
  so a copied-out team repo only needs the path to the hub's benchmark folder (`BENCH=`, `HUB=`).
- Every factory in `bench.PLANNERS` is called with the World. Ids whose factory reads the world
  (the area bounds as a geofence for the unknown-map log-odds map) are `needs_world`; the
  others ignore it. A JSON world (world_json.from_json) works as well as a generated one.
- `make()` returns (planner, filter arm or None). The arm is the benchmark row's filter
  (`astar_unknown_f2` => "F2"); this loop applies filters only through `--safety arm:F2`.
- Short module names that bench.py pops while importing samples (`arena`, `filters`, ...) are
  saved and put back afterwards (worker.js `_load_sample` does the same).

Stdlib at import time. bench.py imports numpy and scipy (the arena venv); `astar_mpc` also
needs osqp, which the arena requirements do not include: it is reported as not loaded.
"""
from __future__ import annotations

import importlib.util
import os
import sys

_MOD = "close_area_benchmark_bench"
# Short names bench.py's _load_sample pops from sys.modules (["arena"] + module names).
_SHORT = ("arena", "apf", "vfh_plus", "rrt_star", "mpc", "filters", "dwa", "bug", "dstar_lite",
          "thetastar", "mppi", "hybrid_astar")


def load_bench(bench_dir: str):
    """Import <bench_dir>/bench.py once, as module close_area_benchmark_bench."""
    if _MOD in sys.modules:
        return sys.modules[_MOD]
    path = os.path.join(os.path.abspath(bench_dir), "bench.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"bench.py not found at {path}: pass --bench-dir or set BENCH_DIR "
                                f"(the hub's samples/close-area-benchmark)")
    saved = {n: sys.modules[n] for n in _SHORT if n in sys.modules}
    spec = importlib.util.spec_from_file_location(_MOD, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MOD] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        sys.modules.pop(_MOD, None)
        raise
    finally:
        sys.modules.update(saved)
    return mod


def needs_world(bench, pid: str) -> bool:
    """True if the factory reads the world (calls bench._bounds(w)), from its code object."""
    code = bench.PLANNERS[pid][0].__code__
    return "_bounds" in code.co_names


def describe(bench_dir: str) -> list[dict]:
    b = load_bench(bench_dir)
    return [{"id": pid, "label": e[2], "sample": e[3], "filter": e[1], "needs_world": needs_world(b, pid),
             "loaded": bool(b.available(pid)), "default": pid in b.DEFAULT_PLANNERS}
            for pid, e in b.PLANNERS.items()]


def make(pid: str, bench_dir: str, world):
    """(planner, filter arm or None) for benchmark id pid, built with the given World."""
    b = load_bench(bench_dir)
    if pid not in b.PLANNERS:
        raise ValueError(f"bench:{pid} unknown; ids: {', '.join(b.PLANNERS)}")
    if not b.available(pid):
        raise ValueError(f"bench:{pid} did not load in bench.py (missing sample or package; "
                         f"see the [bench] line above)")
    factory, arm, _, _ = b.PLANNERS[pid]
    return factory(world), arm
