"""Native CPython reference for the playground: runs worker.js's DRIVER_PY (extracted from the file,
not a copy) on the preset worlds, and checks it against the arena's own entry points.

Run from the repo root with the arena venv:
    samples/close-area-arena/.venv/bin/python site/playground/results/native_parity.py

Checks (fields: outcome, time_to_goal_s, duration_s, min_clearance_m, path_length_m):
  A  driver on presets/<w>.json  ==  run.run_one on WJ.from_json(<same json>)          (loop parity, truth pose, ideal sensor)
  B  driver on presets/<w>.json  ==  run.run_one on world.make_world(family, 0, 0)    (JSON round trip changes nothing)
  C  driver with a fault         ==  run.run_one on the same JSON world with estimator.make_pose_source_factory(fault)  (run.evaluate path)
  Run time limit (loop-73b): the driver takes it from the world family (worker.js max_time_for, the
  bench.py LONG_FAMILIES table: maze and warehouse 120 s, else 60 s); every reference loop below gets
  the same limit through cfg_for.
  E  driver (6 sample planners, and astar_unknown since loop-75b)  ==  run.run_one on the same JSON world with the planner built by
                                    samples/close-area-benchmark/bench.py PLANNERS[name][0](world)
  F  (information) driver (6 sample planners, A* known map on maze / warehouse, astar_unknown) vs the benchmark's results/matrix_0.json row (preset ideal,
     layout 0, generated world, not JSON, so the 4-decimal rounding of check B applies)
  D  driver with F2              ==  close-area-safety-filter/run_kill.run_one("F2", case, unsensed off)  (random family only;
                                    run_kill builds its world with world.make_world, not from JSON)
  G  driver with recovery=<arm>  ==  run.run_one on the same JSON world with the pose source and planner from
                                    samples/close-area-relocalize/run_disambiguate.build(arm, ...) (its run_cell recipe);
                                    score fields + per loss event (trigger t, reason, result, recover s, err m, moves)
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
RELOC = os.path.join(ROOT, "samples", "close-area-relocalize")
THETASTAR = os.path.join(ROOT, "samples", "close-area-planner-thetastar")
MPPI = os.path.join(ROOT, "samples", "close-area-planner-mppi")
HYBRID = os.path.join(ROOT, "samples", "close-area-planner-hybrid-astar")
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
    # loop-73b: run time limit by family (worker.js max_time_for = bench.py LONG_FAMILIES: maze, warehouse 120 s)
    ("maze_0", "astar_known", "ideal", "truth", "none"),
    ("warehouse_0", "astar_known", "ideal", "truth", "none"),
    ("maze_0", "bug2", "ideal", "truth", "none"),
    ("warehouse_0", "bug2", "ideal", "truth", "none"),
    ("maze_0", "informed_rrt_star", "ideal", "truth", "none"),
    # loop-75b: astar_unknown is geofenced as bench.py GeofencedAStar; office_0's B was outside the shipped map
    ("office_0", "astar_unknown", "ideal", "truth", "none"),
]
NEW = ("dwa", "dwa_mem", "bug2", "tangent_bug", "dstar_lite", "informed_rrt_star")
# loop-75b: planners also checked against bench.py's factory (E) and matrix_0.json (F), besides A and B
BENCH_TOO = ("astar_unknown",)
# loop-63: VIO loss recovery arms (world, planner, preset, fault, filter, seed, recovery). The demo world is
# world.make_world("random", 1, 97) through world_json (templates/presenting/live-demo-script-close-area.md H1), saved by this script.
DEMO = "reloc_demo_random_1_97"
RELOC_CASES = [
    (DEMO, "astar_known", "ideal", "jump", "none", 1, "single"),
    (DEMO, "astar_known", "ideal", "jump", "none", 1, "multi"),
    (DEMO, "astar_known", "ideal", "jump", "none", 1, "multi_ig"),
    ("u_trap_0", "astar_known", "ideal", "dropout", "none", 0, "multi_ig"),
]
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
    if PG not in sys.path:                 # pg_reloc.py, as /home/pyodide in the browser
        sys.path.insert(0, PG)
    ns = {"REACTIVE_DIR": REACTIVE, "FILTER_DIR": SAFETY, "DWABUG_DIR": DWABUG, "DSTAR_DIR": DSTAR,
          "SAMPLING_DIR": SAMPLING, "RELOC_DIR": RELOC,
          "THETASTAR_DIR": THETASTAR, "MPPI_DIR": MPPI, "HYBRID_DIR": HYBRID, "__name__": "playground_driver"}
    exec(compile(src, "worker.js:DRIVER_PY", "exec"), ns)
    return ns


def pick(row):
    return {k: row[k] for k in KEYS}


def cfg_for(ns, run, doc):
    """run.DEFAULTS with the driver's run time limit for this world (worker.js max_time_for, the
    bench.py LONG_FAMILIES rule), so the reference loops get the same limit as the driver."""
    return dict(run.DEFAULTS, max_time_s=ns["max_time_for"](doc)[0])


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
                             "frames": len(r["frames"]), "max_time_s": r["max_time_s"],
                             "max_time_source": r["max_time_source"]})
        print(wname, planner, preset, fault, filt, pick(r["score"]), f"{wall:.2f}s", flush=True)

    # VIO loss recovery cases: same score fields plus the relocalization events
    pg_reloc = sys.modules["pg_reloc"]
    demo = WJ.to_json(WM.make_world("random", 1, 97))
    demo["index"] = 97                     # make_world sets no .index; the driver seeds dark zones and the fault with it
    with open(os.path.join(HERE, DEMO + ".json"), "w") as fh:
        json.dump(demo, fh, indent=1)
        fh.write("\n")
    docs[DEMO] = json.load(open(os.path.join(HERE, DEMO + ".json")))
    out["reloc_cases"], out["reloc_checks"] = [], []
    for wname, planner, preset, fault, filt, seed, arm in RELOC_CASES:
        if wname not in docs:
            docs[wname] = json.load(open(os.path.join(PG, "presets", wname + ".json")))
        doc = docs[wname]
        t0 = time.perf_counter()
        r = ns["simulate"](doc, planner, preset, fault, filt, seed, recovery=arm)
        wall = time.perf_counter() - t0
        ev = r["reloc"]["events"]
        out["reloc_cases"].append({"world": wname, "planner": planner, "preset": preset, "fault": fault, "filter": filt,
                                   "seed": seed, "recovery": arm, "score": pick(r["score"]),
                                   "max_pose_error_m": r["score"]["max_pose_error_m"], "summary": r["reloc"]["summary"],
                                   "events": pg_reloc.event_key(ev), "fired_t": (r["fault_log"] or {}).get("fired_t"),
                                   "hyp_frames": len(r["reloc"]["hyps"]), "sim_s": r["sim_s"], "native_wall_s": round(wall, 3)})
        print("RELOC", wname, fault, seed, arm, pick(r["score"]), r["reloc"]["summary"], f"{wall:.2f}s", flush=True)
        # G: the same arm through run.run_one with run_disambiguate.build (run_disambiguate.py run_cell recipe)
        wj = WJ.from_json(doc)
        est = est_mod.make_pose_source_factory(fault, dark=True, sink=[])(wj, seed, doc.get("index", 0))
        src, planner_obj = pg_reloc.M["run_disambiguate"].build(arm, wj, est, seed, doc.get("index", 0))
        row, _, _ = run.run_one(planner_obj, wj, seed, doc.get("index", 0), cfg_for(ns, run, doc), src)
        row.update(pg_reloc.M["run_disambiguate"].extra(row, est, src, est.fault))
        ref = {"score": pick(row), "events": pg_reloc.event_key(row["events"])}
        mine = {"score": pick(r["score"]), "events": pg_reloc.event_key(ev)}
        ok = ref == mine
        out["reloc_checks"].append({"check": "G run.run_one + run_disambiguate.build, same JSON world",
                                    "case": [wname, fault, seed, arm], "same": ok, "driver": mine, "reference": ref})
        print("CHECK G", wname, fault, seed, arm, "same" if ok else f"DIFF {mine} vs {ref}")
    # H (information): demo cases vs the sample's own published run (generated world, not JSON)
    pub = json.load(open(os.path.join(RELOC, "results", "disamb_random_1.json")))["results"]
    out["reloc_published"] = []
    for c in [c for c in out["reloc_cases"] if c["world"] == DEMO]:
        row = pub[c["fault"]][c["recovery"]]["runs"][97]
        ref = {"score": pick(row), "events": pg_reloc.event_key(row["events"])}
        same_ = ref == {"score": c["score"], "events": c["events"]}
        out["reloc_published"].append({"case": [c["world"], c["fault"], c["seed"], c["recovery"]], "same": same_,
                                       "published": ref, "source": "samples/close-area-relocalize/results/disamb_random_1.json runs[97]"})
        print("PUBLISHED", c["recovery"], "same" if same_ else f"differs: {ref}")

    def check(name, case, ref):
        mine = next(c for c in out["cases"] if (c["world"], c["planner"], c["preset"], c["fault"], c["filter"]) == case)
        ok = mine["score"] == pick(ref)
        out["checks"].append({"check": name, "case": list(case), "same": ok, "driver": mine["score"], "reference": pick(ref)})
        print("CHECK", name, case, "same" if ok else f"DIFF {mine['score']} vs {pick(ref)}")

    # factories take the world (loop-75b: astar_unknown is geofenced on its bounds)
    fac = {"straight": lambda w: run.load_planner("straight"), "astar_known": lambda w: ns["PLANNERS"]["astar_known"](),
           "astar_unknown": lambda w: ns["PLANNERS"]["astar_unknown"](w), "freest_beam": lambda w: ns["PLANNERS"]["freest_beam"](),
           "apf": lambda w: ns["PLANNERS"]["apf"](), "vfh_plus": lambda w: ns["PLANNERS"]["vfh_plus"]()}
    # A and B: truth pose, ideal sensor, no filter
    for case in [c for c in CASES if c[2:] == ("ideal", "truth", "none") and c[1] not in NEW]:
        wname, planner = case[0], case[1]
        wj = WJ.from_json(docs[wname])
        cfg = cfg_for(ns, run, docs[wname])
        row, _, _ = run.run_one(fac[planner](wj), wj, 0, 0, cfg)
        check("A run.run_one on the same JSON world", case, row)
        fam = docs[wname]["family"]
        wg = WM.make_world(fam, 0, 0)
        row, _, _ = run.run_one(fac[planner](wg), wg, 0, 0, cfg)
        check("B run.run_one on world.make_world (no JSON)", case, row)
    # C: estimator faults, no filter, ideal sensor (run.evaluate path)
    for case in [c for c in CASES if c[2] == "ideal" and c[3] not in ("truth",) and c[4] == "none"]:
        wname, planner, _, fault, _ = case
        wg = WJ.from_json(docs[wname])
        ps = est_mod.make_pose_source_factory(fault, dark=True)(wg, 0, 0)
        row, _, _ = run.run_one(fac[planner](wg), wg, 0, 0, cfg_for(ns, run, docs[wname]), ps)
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
    for case in [c for c in CASES if c[1] in NEW or (c[1] in BENCH_TOO and c[2:] == ("ideal", "truth", "none"))]:
        wj = WJ.from_json(docs[case[0]])
        row, _, _ = run.run_one(bench.PLANNERS[case[1]][0](wj), wj, 0, 0, cfg_for(ns, run, docs[case[0]]))
        check("E run.run_one + bench.py planner factory, same JSON world", case, row)
    # F: information only, against the benchmark matrix on generated worlds
    mx = {(r["planner"], r["family"], r["preset"], r["index"]): r for r in json.load(open(MATRIX))["runs"]}
    out["matrix_rows"] = []
    # loop-73b: also A* known map on the long families (maze, warehouse), same 120 s limit as the matrix
    long_fams = ns["LONG_FAMILIES"]
    for case in [c for c in CASES if c[1] in NEW or ((docs[c[0]]["family"] in long_fams or c[1] in BENCH_TOO)
                                                     and c[2:] == ("ideal", "truth", "none"))]:
        fam = docs[case[0]]["family"]
        ref = mx.get((case[1], fam, "ideal", docs[case[0]].get("index", 0)))
        mine = next(c for c in out["cases"] if (c["world"], c["planner"], c["preset"], c["fault"], c["filter"]) == case)
        row = {"case": list(case), "matrix": pick(ref) if ref else None, "driver": mine["score"],
               "max_time_s": {"driver": mine["max_time_s"], "matrix": ref.get("max_time_s") if ref else None},
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
    g = out["reloc_checks"]
    out["reloc_summary"] = f"{sum(c['same'] for c in g)}/{len(g)} relocalization checks (G) identical"
    print(out["reloc_summary"])
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
