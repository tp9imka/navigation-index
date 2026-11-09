"""Native CPython reference for the playground: runs worker.js's DRIVER_PY (extracted from the file,
not a copy) on the preset worlds, and checks it against the arena's own entry points.

Run from the repo root with the arena venv:
    samples/close-area-arena/.venv/bin/python site/playground/results/native_parity.py

Checks (fields: outcome, time_to_goal_s, duration_s, min_clearance_m, path_length_m):
  A  driver on presets/<w>.json  ==  run.run_one on WJ.from_json(<same json>)          (loop parity, truth pose, ideal sensor)
  B  driver on presets/<w>.json  ==  run.run_one on world.make_world(family, 0, 0)    (JSON round trip changes nothing)
  C  driver with a fault         ==  run.run_one on the same JSON world with estimator.make_pose_source_factory(fault)  (run.evaluate path)
  E  driver (6 sample planners)  ==  run.run_one on the same JSON world with the planner built by
                                    samples/close-area-benchmark/bench.py PLANNERS[name][0](world)
  F  (information) driver (6 sample planners) vs the benchmark's results/matrix_0.json row (preset ideal,
     layout 0, generated world, not JSON, so the 4-decimal rounding of check B applies)
  D  driver with F2              ==  close-area-safety-filter/run_kill.run_one("F2", case, unsensed off)  (random family only;
                                    run_kill builds its world with world.make_world, not from JSON)
Writes native_parity.json (cases + native scores) for measure_playground.mjs to compare the browser against.
Input type: synthetic (seeded generated layouts, simulated vehicle and sensors).
"""
import importlib
import importlib.util
import json
import os
import platform
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PG = os.path.normpath(os.path.join(HERE, ".."))
ROOT = os.path.normpath(os.path.join(PG, "..", ".."))
ARENA = os.path.join(ROOT, "samples", "close-area-arena")
REACTIVE = os.path.join(ROOT, "samples", "close-area-planner-reactive")
SAFETY = os.path.join(ROOT, "samples", "close-area-safety-filter")
DWABUG = os.path.join(ROOT, "samples", "close-area-planner-dwa-bug")
DSTAR = os.path.join(ROOT, "samples", "close-area-planner-dstar")
SAMPLING = os.path.join(ROOT, "samples", "close-area-planner-sampling")
BENCH = os.path.join(ROOT, "samples", "close-area-benchmark", "bench.py")
KEYS = ("outcome", "time_to_goal_s", "duration_s", "min_clearance_m", "path_length_m")

# Cases the browser run must reproduce: (world file, planner, preset, fault, filter)
CASES = [
    ("random_0", "straight", "ideal", "truth", "none"),
    ("random_0", "freest_beam", "ideal", "truth", "none"),
    ("random_0", "astar_known", "ideal", "truth", "none"),
    ("random_0", "astar_unknown", "ideal", "truth", "none"),
    ("random_0", "apf", "ideal", "truth", "none"),
    ("random_0", "vfh_plus", "ideal", "truth", "none"),
    ("random_0", "astar_known", "ideal", "jump", "none"),
    ("random_0", "astar_known", "ideal", "jump", "F2"),
    ("random_0", "freest_beam", "ideal", "bias", "none"),
    ("random_0", "astar_known", "ideal", "dropout", "F2"),
    ("office_0", "astar_known", "ideal", "truth", "none"),
    ("office_0", "freest_beam", "ideal", "truth", "none"),
    ("office_0", "freest_beam", "crazyflie", "none", "none"),
    ("glass_office_0", "astar_unknown", "crazyflie", "truth", "none"),
    ("u_trap_0", "astar_known", "crazyflie_bright", "bias", "F2"),
    # loop-62: the 6 benchmark planners added to the playground, one preset each
    ("random_0", "dwa", "ideal", "truth", "none"),
    ("u_trap_0", "dwa_mem", "ideal", "truth", "none"),
    ("office_0", "bug2", "ideal", "truth", "none"),
    ("forest_0", "tangent_bug", "ideal", "truth", "none"),
    ("narrow_gap_0", "dstar_lite", "ideal", "truth", "none"),
    ("office_0", "informed_rrt_star", "ideal", "truth", "none"),
]
NEW = ("dwa", "dwa_mem", "bug2", "tangent_bug", "dstar_lite", "informed_rrt_star")
MATRIX = os.path.join(ROOT, "samples", "close-area-benchmark", "results", "matrix_0.json")


def load_arena():
    spec = importlib.util.spec_from_file_location("close_area_arena", os.path.join(ARENA, "__init__.py"),
                                                  submodule_search_locations=[ARENA])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["close_area_arena"] = pkg
    spec.loader.exec_module(pkg)


def driver_ns():
    js = open(os.path.join(PG, "worker.js")).read()
    src = re.search(r"const DRIVER_PY = String\.raw`([\s\S]*?)`;", js).group(1)
    ns = {"REACTIVE_DIR": REACTIVE, "FILTER_DIR": SAFETY, "DWABUG_DIR": DWABUG, "DSTAR_DIR": DSTAR,
          "SAMPLING_DIR": SAMPLING, "__name__": "playground_driver"}
    exec(compile(src, "worker.js:DRIVER_PY", "exec"), ns)
    return ns


def pick(row):
    return {k: row[k] for k in KEYS}


def main():
    load_arena()
    ns = driver_ns()
    run = importlib.import_module("close_area_arena.run")
    WJ = importlib.import_module("close_area_arena.world_json")
    WM = importlib.import_module("close_area_arena.world")
    est_mod = importlib.import_module("close_area_arena.estimator")
    import numpy as np
    import scipy
    out = {"input": "synthetic", "command": "samples/close-area-arena/.venv/bin/python site/playground/results/native_parity.py",
           "env": json.loads(ns["env_json"]()), "keys": list(KEYS), "cases": [], "checks": []}
    docs = {}
    for wname, planner, preset, fault, filt in CASES:
        doc = docs.setdefault(wname, json.load(open(os.path.join(PG, "presets", wname + ".json"))))
        t0 = time.perf_counter()
        r = ns["simulate"](doc, planner, preset, fault, filt, 0)
        wall = time.perf_counter() - t0
        out["cases"].append({"world": wname, "planner": planner, "preset": preset, "fault": fault, "filter": filt,
                             "score": pick(r["score"]), "max_pose_error_m": r["score"]["max_pose_error_m"],
                             "free_path": r["free_path"], "sim_s": r["sim_s"], "native_wall_s": round(wall, 3),
                             "frames": len(r["frames"])})
        print(wname, planner, preset, fault, filt, pick(r["score"]), f"{wall:.2f}s", flush=True)

    def check(name, case, ref):
        mine = next(c for c in out["cases"] if (c["world"], c["planner"], c["preset"], c["fault"], c["filter"]) == case)
        ok = mine["score"] == pick(ref)
        out["checks"].append({"check": name, "case": list(case), "same": ok, "driver": mine["score"], "reference": pick(ref)})
        print("CHECK", name, case, "same" if ok else f"DIFF {mine['score']} vs {pick(ref)}")

    fac = {"straight": lambda: run.load_planner("straight"), "astar_known": lambda: ns["PLANNERS"]["astar_known"](),
           "astar_unknown": lambda: ns["PLANNERS"]["astar_unknown"](), "freest_beam": lambda: ns["PLANNERS"]["freest_beam"](),
           "apf": lambda: ns["PLANNERS"]["apf"](), "vfh_plus": lambda: ns["PLANNERS"]["vfh_plus"]()}
    # A and B: truth pose, ideal sensor, no filter
    for case in [c for c in CASES if c[2:] == ("ideal", "truth", "none") and c[1] not in NEW]:
        wname, planner = case[0], case[1]
        wj = WJ.from_json(docs[wname])
        row, _, _ = run.run_one(fac[planner](), wj, 0, 0)
        check("A run.run_one on the same JSON world", case, row)
        fam = docs[wname]["family"]
        wg = WM.make_world(fam, 0, 0)
        row, _, _ = run.run_one(fac[planner](), wg, 0, 0)
        check("B run.run_one on world.make_world (no JSON)", case, row)
    # C: estimator faults, no filter, ideal sensor (run.evaluate path)
    for case in [c for c in CASES if c[2] == "ideal" and c[3] not in ("truth",) and c[4] == "none"]:
        wname, planner, _, fault, _ = case
        wg = WJ.from_json(docs[wname])
        ps = est_mod.make_pose_source_factory(fault, dark=True)(wg, 0, 0)
        row, _, _ = run.run_one(fac[planner](), wg, 0, 0, run.DEFAULTS, ps)
        check("C run.run_one + estimator fault (run.evaluate path)", case, row)
    # E: the 6 sample planners, built the benchmark's way, through run.run_one on the same JSON world
    spec = importlib.util.spec_from_file_location("close_area_benchmark_bench", BENCH)
    bench = importlib.util.module_from_spec(spec)
    saved = sys.modules.pop("arena", None)
    try:
        spec.loader.exec_module(bench)
    finally:
        if saved is not None:
            sys.modules["arena"] = saved
    for case in [c for c in CASES if c[1] in NEW]:
        wj = WJ.from_json(docs[case[0]])
        row, _, _ = run.run_one(bench.PLANNERS[case[1]][0](wj), wj, 0, 0)
        check("E run.run_one + bench.py planner factory, same JSON world", case, row)
    # F: information only, against the benchmark matrix on generated worlds
    mx = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in json.load(open(MATRIX))["runs"]}
    out["matrix_rows"] = []
    for case in [c for c in CASES if c[1] in NEW]:
        fam = docs[case[0]]["family"]
        ref = mx.get((case[1], fam, "ideal", docs[case[0]].get("index", 0)))
        mine = next(c for c in out["cases"] if (c["world"], c["planner"], c["preset"], c["fault"], c["filter"]) == case)
        row = {"case": list(case), "matrix": pick(ref) if ref else None, "driver": mine["score"],
               "same": bool(ref) and pick(ref) == mine["score"],
               "same_outcome": bool(ref) and ref["outcome"] == mine["score"]["outcome"]}
        out["matrix_rows"].append(row)
        print("MATRIX", case, "same" if row["same"] else f"differs: matrix {row['matrix']}")
    # D: F2 on astar known, random family (run_kill.py loop, unsensed off)
    sys.path.insert(0, SAFETY)
    saved = sys.modules.pop("arena", None)            # reactive arena.py; run_kill needs its own arena.py
    try:
        run_kill = importlib.import_module("run_kill")
        for case in [c for c in CASES if c[4] == "F2" and c[0] == "random_0" and c[1] == "astar_known" and c[2] == "ideal"]:
            row = run_kill.run_one("F2", case[3], False, 0, 0)
            check("D run_kill.run_one F2, unsensed off", case, row)
    finally:
        sys.path.remove(SAFETY)
        if saved is not None:
            sys.modules["arena"] = saved
    out["native_env"] = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                         "machine": platform.machine()}
    n_ok = sum(c["same"] for c in out["checks"])
    out["summary"] = f"{n_ok}/{len(out['checks'])} checks identical"
    nm = out["matrix_rows"]
    out["matrix_summary"] = (f"{sum(r['same'] for r in nm)}/{len(nm)} identical to matrix_0.json, "
                             f"{sum(r['same_outcome'] for r in nm)}/{len(nm)} same outcome (generated vs JSON world)")
    print(out["matrix_summary"])
    print(out["summary"])
    with open(os.path.join(HERE, "native_parity.json"), "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    main()
