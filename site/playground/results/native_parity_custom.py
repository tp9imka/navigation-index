"""Native CPython reference for custom vehicles and sensors in the playground run message (loop-75, loop-75b).
Sibling of native_parity.py: same driver (worker.js DRIVER_PY, extracted from the file), same score keys.

Run from the repo root with the arena venv:
    samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_custom.py

Cases (seed 0, truth pose, no filter):
  1  random_0      mppi_astar     cfg.sensor = presets.SENSOR_SPECS["depth_cam_87"] (dict), cfg.yaw = look_where_you_go
  2  office_0      mppi_astar     the same (1 and 2 are the loop-75 cases; loop-75b made the yaw policy opt-in)
  3  office_0      mppi_astar     the same camera, cfg.yaw absent (default "fixed")
  4  narrow_gap_0  mppi_astar     cfg.vehicle radius_m 0.25 (v_max, a_max, tau as run.DEFAULTS), sensor ideal
  5  narrow_gap_0  mppi_astar     radius_m 0.35
  6  narrow_gap_0  astar_unknown  radius_m 0.25
  7  narrow_gap_0  astar_unknown  radius_m 0.35
  Cases 4-7 also store "before": the same run with inflate=False (planners keep the shipped 0.15 m, as before
  loop-75b; native only, the run message has no such field).
Checks:
  K1  cases 1-3: driver with the sensor dict == driver with preset "depth_cam_87" and the same yaw
  K2  cases 4-7: driver == run.run_one on the same JSON world with run.DEFAULTS["vehicle"]["radius"] = r and the
      planner built inside the driver's radius_override(r) (loop parity with the override)
  K3  no leak: after cases 4-7 every overridden constant is back at its import value, and narrow_gap_0
      mppi_astar at the default radius == the same run made before any custom radius
  K4  case 3 (cfg.yaw absent) == simulate(yaw_policy="off"), the loop-75 "fixed yaw" path
  K5  cfg.vehicle with the default radius 0.15 m == no cfg.vehicle (nothing overridden at 0.15 m)
Information: case 3 vs samples/close-area-arena/results/custom_sensor_0.json (depth_cam_87 fixed yaw, office_0).
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

OUT = os.path.join(HERE, "native_parity_custom.json")
CUSTOM_SENSOR_0 = os.path.join(NP.ARENA, "results", "custom_sensor_0.json")
LWYG = "look_where_you_go"


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
    veh = lambda r: {"radius_m": r, "v_max": dv["v_max"], "a_max": dv["a_max"], "tau": dv["tau"]}
    cases = [
        {"world": "random_0", "planner": "mppi_astar", "preset": "ideal", "sensor": cam, "vehicle": None, "yaw": LWYG},
        {"world": "office_0", "planner": "mppi_astar", "preset": "ideal", "sensor": cam, "vehicle": None, "yaw": LWYG},
        {"world": "office_0", "planner": "mppi_astar", "preset": "ideal", "sensor": cam, "vehicle": None, "yaw": None},
        {"world": "narrow_gap_0", "planner": "mppi_astar", "preset": "ideal", "sensor": None, "vehicle": veh(0.25), "yaw": None},
        {"world": "narrow_gap_0", "planner": "mppi_astar", "preset": "ideal", "sensor": None, "vehicle": veh(0.35), "yaw": None},
        {"world": "narrow_gap_0", "planner": "astar_unknown", "preset": "ideal", "sensor": None, "vehicle": veh(0.25), "yaw": None},
        {"world": "narrow_gap_0", "planner": "astar_unknown", "preset": "ideal", "sensor": None, "vehicle": veh(0.35), "yaw": None},
    ]
    out = {"input": "synthetic",
           "command": "samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_custom.py",
           "env": json.loads(ns["env_json"]()), "keys": list(NP.KEYS), "cases": [], "checks": []}
    docs = {}
    for c in cases + [{"world": "narrow_gap_0"}]:
        docs.setdefault(c["world"], json.load(open(os.path.join(NP.PG, "presets", c["world"] + ".json"))))
    sim = lambda c, **kw: ns["simulate"](docs[c["world"]], c["planner"], c["preset"], "truth", "none", 0,
                                         vehicle=copy.deepcopy(c["vehicle"]), sensor=copy.deepcopy(c["sensor"]),
                                         yaw=c["yaw"] or "fixed", **kw)
    consts0 = {lbl: getattr(m, a) for m, a, _, lbl in ns["RADIUS_TABLE"]}
    plain = {"world": "narrow_gap_0", "planner": "mppi_astar", "preset": "ideal", "sensor": None, "vehicle": None, "yaw": None}
    first_default = NP.pick(sim(plain)["score"])
    for c in cases:
        t0 = time.perf_counter()
        r = sim(c)
        wall = time.perf_counter() - t0
        row = dict(c, fault="truth", filter="none", seed=0, score=NP.pick(r["score"]), free_path=r["free_path"],
                   sim_s=r["sim_s"], native_wall_s=round(wall, 3), frames=len(r["frames"]), max_time_s=r["max_time_s"],
                   flown={"vehicle": r["vehicle"], "sensor": r["sensor"], "radius": r["radius"], "yaw": r["yaw"],
                          "n_beams": len(r["scan_angles"]), "max_range": r["max_range"]},
                   inflation=r["inflation"])
        if c["vehicle"] is not None:
            row["before"] = NP.pick(sim(c, inflate=False)["score"])
        out["cases"].append(row)
        print(c["world"], c["planner"], "sensor" if c["sensor"] else "vehicle", r["yaw"], r["radius"], NP.pick(r["score"]),
              "before", row.get("before"), f"{wall:.2f}s", flush=True)

    def check(name, case, mine, ref):
        ok = mine == ref
        out["checks"].append({"check": name, "case": case, "same": ok, "driver": mine, "reference": ref})
        print("CHECK", name, case, "same" if ok else f"DIFF {mine} vs {ref}", flush=True)

    # K1: the same camera by name, same yaw
    for c in [c for c in out["cases"] if c["sensor"]]:
        r = ns["simulate"](docs[c["world"]], c["planner"], "depth_cam_87", "truth", "none", 0, yaw=c["yaw"] or "fixed")
        check("K1 driver, preset name depth_cam_87", [c["world"], c["planner"], c["yaw"] or "fixed"], c["score"],
              NP.pick(r["score"]))
    # K2: run.run_one with the bigger radius, planner built inside the driver's override
    for c in [c for c in out["cases"] if c["vehicle"]]:
        rr = c["vehicle"]["radius_m"]
        wj = WJ.from_json(docs[c["world"]])
        cfg = NP.cfg_for(ns, run, docs[c["world"]])
        cfg = dict(cfg, vehicle=dict(cfg["vehicle"], radius=rr))
        with ns["radius_override"](rr):
            row, _, _ = run.run_one(ns["build_planner"](c["planner"], wj, rr), wj, 0, 0, cfg)
        check(f"K2 run.run_one + radius_override, vehicle radius {rr} m, same JSON world", [c["world"], c["planner"], rr],
              c["score"], NP.pick(row))
    # K3: nothing leaks between runs
    consts1 = {lbl: getattr(m, a) for m, a, _, lbl in ns["RADIUS_TABLE"]}
    check("K3 overridden constants restored after the runs", "RADIUS_TABLE", consts1, consts0)
    check("K3 default-radius run after the custom-radius runs == the same run before them", ["narrow_gap_0", "mppi_astar"],
          NP.pick(sim(plain)["score"]), first_default)
    # K4: default yaw = the loop-75 fixed-yaw path
    c3 = out["cases"][2]
    r = ns["simulate"](docs["office_0"], "mppi_astar", "depth_cam_87", "truth", "none", 0, yaw_policy="off")
    check("K4 cfg.yaw absent == yaw_policy off (loop-75 fixed yaw)", ["office_0", "mppi_astar"], c3["score"], NP.pick(r["score"]))
    # K5: an explicit default radius changes nothing
    r = sim(dict(plain, vehicle=veh(dv["radius"])))
    check("K5 cfg.vehicle radius 0.15 m == no cfg.vehicle", ["narrow_gap_0", "mppi_astar"], NP.pick(r["score"]), first_default)
    # information: case 3 vs the arena's custom_sensor_0.json row
    try:
        rows = json.load(open(CUSTOM_SENSOR_0))["runs"]
        ref = next(x for x in rows if x["world"] == "office_0" and x["planner"] == "mppi_astar"
                   and x["preset"] == "depth_cam_87" and x["yaw_policy"] == "off")
        out["custom_sensor_0"] = {"case": ["office_0", "mppi_astar", "depth_cam_87", "fixed"], "published": ref["score"],
                                  "same": ref["score"] == c3["score"],
                                  "source": "samples/close-area-arena/results/custom_sensor_0.json"}
        print("CUSTOM_SENSOR_0", "same" if out["custom_sensor_0"]["same"] else f"differs: {ref['score']}")
    except (OSError, KeyError, StopIteration) as e:
        out["custom_sensor_0"] = {"error": repr(e)}
    out["native_env"] = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                         "machine": platform.machine()}
    out["summary"] = f"{sum(k['same'] for k in out['checks'])}/{len(out['checks'])} checks (K1-K5) identical"
    print(out["summary"])
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")


if __name__ == "__main__":
    main()
