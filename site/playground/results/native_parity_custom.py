"""Native CPython reference for custom vehicles and sensors in the playground run message (loop-75).
Sibling of native_parity.py: same driver (worker.js DRIVER_PY, extracted from the file), same score keys.

Run from the repo root with the arena venv:
    samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_custom.py

Cases (seed 0, truth pose, no filter, planner mppi_astar: MPPI on the unknown-map A* path, geofenced, so it maps
  from the range fan; the playground astar_unknown keeps the shipped map corner and does not move on office_0):
  1  presets/random_0.json      cfg.sensor = presets.SENSOR_SPECS["depth_cam_87"] (dict, not the name)
  2  presets/office_0.json      cfg.sensor = the same dict
  3  presets/narrow_gap_0.json  cfg.vehicle = {"radius_m": 0.25, v_max, a_max, tau as run.DEFAULTS}, sensor ideal
Checks:
  K1  cases 1, 2: driver with the sensor dict == driver with preset "depth_cam_87" (dict path = named path)
  K2  case 3: driver == run.run_one on the same JSON world with run.DEFAULTS["vehicle"]["radius"] = 0.25
      (360 deg sensor, so the yaw policy is off and the arena's own loop is a full reference)
Writes native_parity_custom.json for measure_custom.mjs to compare the browser against.
Input type: synthetic (preset worlds, simulated vehicle and sensors).
"""
import copy
import importlib
import json
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import native_parity as NP  # noqa: E402

PLANNER = "mppi_astar"
RADIUS_CASE_M = 0.25
OUT = os.path.join(HERE, "native_parity_custom.json")


def main():
    NP.load_arena()
    ns = NP.driver_ns()
    run = importlib.import_module("close_area_arena.run")
    WJ = importlib.import_module("close_area_arena.world_json")
    presets = importlib.import_module("close_area_arena.presets")
    import numpy as np
    import scipy
    cam = dict(presets.SENSOR_SPECS["depth_cam_87"])
    dv = run.DEFAULTS["vehicle"]
    veh = {"radius_m": RADIUS_CASE_M, "v_max": dv["v_max"], "a_max": dv["a_max"], "tau": dv["tau"]}
    cases = [
        {"world": "random_0", "planner": PLANNER, "preset": "ideal", "sensor": cam, "vehicle": None},
        {"world": "office_0", "planner": PLANNER, "preset": "ideal", "sensor": cam, "vehicle": None},
        {"world": "narrow_gap_0", "planner": PLANNER, "preset": "ideal", "sensor": None, "vehicle": veh},
    ]
    out = {"input": "synthetic",
           "command": "samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_custom.py",
           "env": json.loads(ns["env_json"]()), "keys": list(NP.KEYS), "cases": [], "checks": []}
    docs = {}
    for c in cases:
        doc = docs.setdefault(c["world"], json.load(open(os.path.join(NP.PG, "presets", c["world"] + ".json"))))
        t0 = time.perf_counter()
        r = ns["simulate"](doc, c["planner"], c["preset"], "truth", "none", 0,
                           vehicle=copy.deepcopy(c["vehicle"]), sensor=copy.deepcopy(c["sensor"]))
        wall = time.perf_counter() - t0
        row = dict(c, fault="truth", filter="none", seed=0, score=NP.pick(r["score"]), free_path=r["free_path"],
                   sim_s=r["sim_s"], native_wall_s=round(wall, 3), frames=len(r["frames"]), max_time_s=r["max_time_s"],
                   flown={"vehicle": r["vehicle"], "sensor": r["sensor"], "radius": r["radius"],
                          "n_beams": len(r["scan_angles"]), "max_range": r["max_range"]})
        out["cases"].append(row)
        print(c["world"], "sensor" if c["sensor"] else "vehicle", NP.pick(r["score"]), r["sensor"]["yaw_policy"],
              f"{wall:.2f}s", flush=True)

    def check(name, case, mine, ref):
        ok = mine == ref
        out["checks"].append({"check": name, "case": case, "same": ok, "driver": mine, "reference": ref})
        print("CHECK", name, case, "same" if ok else f"DIFF {mine} vs {ref}", flush=True)

    # K1: the same camera by name
    for c in out["cases"][:2]:
        r = ns["simulate"](docs[c["world"]], c["planner"], "depth_cam_87", "truth", "none", 0)
        check("K1 driver, preset name depth_cam_87", [c["world"], c["planner"]], c["score"], NP.pick(r["score"]))
    # K2: run.run_one with the bigger radius
    c = out["cases"][2]
    wj = WJ.from_json(docs[c["world"]])
    cfg = NP.cfg_for(ns, run, docs[c["world"]])
    cfg = dict(cfg, vehicle=dict(cfg["vehicle"], radius=RADIUS_CASE_M))
    mk = ns["PLANNERS"][c["planner"]]
    pl = mk(wj) if c["planner"] in ns["WORLD_PLANNERS"] else mk()
    row, _, _ = run.run_one(pl, wj, 0, 0, cfg)
    check("K2 run.run_one, vehicle radius 0.25 m, same JSON world", [c["world"], c["planner"]], c["score"], NP.pick(row))
    out["native_env"] = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                         "machine": platform.machine()}
    out["summary"] = f"{sum(k['same'] for k in out['checks'])}/{len(out['checks'])} checks (K1, K2) identical"
    print(out["summary"])
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    main()
