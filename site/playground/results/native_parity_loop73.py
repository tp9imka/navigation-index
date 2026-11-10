"""Native CPython reference for the planners added in loop-73 (Theta* / Lazy Theta*, MPPI, Hybrid A*).
Sibling of native_parity.py: same driver (worker.js DRIVER_PY, extracted from the file), same score keys.

Run from the repo root with the arena venv:
    samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_loop73.py

Cases: every new playground planner on presets/random_0.json and presets/maze_0.json, seed 0, sensor ideal,
truth pose, no filter. Checks:
  E  driver == run.run_one on the same JSON world with the planner built by
     samples/close-area-benchmark/bench.py PLANNERS[name][0](world)
  F  (information) driver vs the benchmark's results/matrix_0.json row (preset ideal, layout 0, generated
     world, not JSON; maze runs there have a 120 s limit, the playground keeps run.py's 60 s)
Writes native_parity_loop73.json for measure_loop73.mjs. `--matrix-only` recomputes only F from the saved file
(run after the benchmark rows exist; the cases and their native wall times stay as they were).
Input type: synthetic (seeded generated layouts, simulated vehicle and sensors).
"""
import importlib
import importlib.util
import json
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import native_parity as NP  # noqa: E402

WORLDS = ("random_0", "maze_0")
NEW = ("thetastar_known", "lazy_thetastar_known", "lazy_thetastar_unknown", "mppi", "mppi_astar", "hybrid_astar")
CASES = [(w, p, "ideal", "truth", "none") for p in NEW for w in WORLDS]


def matrix_check(out):
    """F: information only, against the benchmark matrix on generated worlds."""
    docs = {w: json.load(open(os.path.join(NP.PG, "presets", w + ".json"))) for w in WORLDS}
    mx = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in json.load(open(NP.MATRIX))["runs"]}
    out["matrix_rows"] = []
    for case in CASES:
        doc = docs[case[0]]
        ref = mx.get((case[1], doc["family"], "ideal", doc.get("index", 0)))
        mine = next(c for c in out["cases"] if (c["world"], c["planner"]) == case[:2])
        row = {"case": list(case), "matrix": NP.pick(ref) if ref else None, "driver": mine["score"],
               "same": bool(ref) and NP.pick(ref) == mine["score"],
               "same_outcome": bool(ref) and ref["outcome"] == mine["score"]["outcome"]}
        out["matrix_rows"].append(row)
        print("MATRIX", case[:2], "same" if row["same"] else f"differs: matrix {row['matrix']}")
    nm = out["matrix_rows"]
    out["matrix_summary"] = (f"{sum(r['same'] for r in nm)}/{len(nm)} identical to matrix_0.json, "
                             f"{sum(r['same_outcome'] for r in nm)}/{len(nm)} same outcome (generated vs JSON world; "
                             "maze has a 120 s limit in the matrix, 60 s here)")
    print(out["matrix_summary"])


def main():
    if "--matrix-only" in sys.argv:
        path = os.path.join(HERE, "native_parity_loop73.json")
        out = json.load(open(path))
        matrix_check(out)
        with open(path, "w") as fh:
            json.dump(out, fh, indent=1)
            fh.write("\n")
        return
    NP.load_arena()
    ns = NP.driver_ns()
    if any(k in ns["LOAD_ERRORS"] for k in ("thetastar", "mppi", "hybrid_astar")):
        raise SystemExit(f"load errors: {ns['LOAD_ERRORS']}")
    run = importlib.import_module("close_area_arena.run")
    WJ = importlib.import_module("close_area_arena.world_json")
    import numpy as np
    import scipy
    out = {"input": "synthetic",
           "command": "samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_loop73.py",
           "env": json.loads(ns["env_json"]()), "keys": list(NP.KEYS), "cases": [], "checks": []}
    docs = {w: json.load(open(os.path.join(NP.PG, "presets", w + ".json"))) for w in WORLDS}
    for wname, planner, preset, fault, filt in CASES:
        t0 = time.perf_counter()
        r = ns["simulate"](docs[wname], planner, preset, fault, filt, 0)
        wall = time.perf_counter() - t0
        out["cases"].append({"world": wname, "planner": planner, "preset": preset, "fault": fault, "filter": filt,
                             "score": NP.pick(r["score"]), "free_path": r["free_path"], "sim_s": r["sim_s"],
                             "native_wall_s": round(wall, 3), "frames": len(r["frames"])})
        print(wname, planner, NP.pick(r["score"]), f"{wall:.2f}s", flush=True)
    # E: bench.py factories through run.run_one on the same JSON world
    spec = importlib.util.spec_from_file_location("close_area_benchmark_bench", NP.BENCH)
    bench = importlib.util.module_from_spec(spec)
    saved = sys.modules.pop("arena", None)
    try:
        spec.loader.exec_module(bench)
    finally:
        if saved is not None:
            sys.modules["arena"] = saved
    for case in CASES:
        wj = WJ.from_json(docs[case[0]])
        row, _, _ = run.run_one(bench.PLANNERS[case[1]][0](wj), wj, 0, 0)
        mine = next(c for c in out["cases"] if (c["world"], c["planner"]) == case[:2])
        ok = mine["score"] == NP.pick(row)
        out["checks"].append({"check": "E run.run_one + bench.py planner factory, same JSON world", "case": list(case),
                              "same": ok, "driver": mine["score"], "reference": NP.pick(row)})
        print("CHECK E", case[:2], "same" if ok else f"DIFF {mine['score']} vs {NP.pick(row)}", flush=True)
    matrix_check(out)
    out["native_env"] = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                         "machine": platform.machine()}
    out["summary"] = f"{sum(c['same'] for c in out['checks'])}/{len(out['checks'])} checks (E) identical"
    print(out["summary"])
    with open(os.path.join(HERE, "native_parity_loop73.json"), "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    main()
