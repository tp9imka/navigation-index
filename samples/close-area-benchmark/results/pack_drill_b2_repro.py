"""loop-99 B2: Solver (worker.js DRIVER_PY) vs pack.py (bench.run_one) on the drill room, natively.

Run from the repo root with the benchmark venv:
    samples/close-area-benchmark/.venv/bin/python samples/close-area-benchmark/results/pack_drill_b2_repro.py [--seeds 0,1,2,3,4]

World docs/drill-2026-11/our_room.world.json, vehicle radius 0.2 m / v_max 1.5 / a_max 3 / tau 0.15,
sensor depth_cam_87, A and B per seed from pack.seed_jitter (the drill's Solver export shows the same points).
Four ways per (planner, seed):
  driver_inflate      worker.js simulate(), planners inflate by 0.2 m (what the Solver flew, loop-75b)
  driver_no_inflate   simulate(inflate=False): planners keep the shipped 0.15 m constants
  pack_shipped        pack.fly(inflate=False) = bench.run_one, shipped 0.15 m constants (the drill's pack run)
  pack_override       pack.fly(inflate=True), pack.py's own radius_override (loop-99 default)
The first confirmation run (pack_drill_b2_confirm.json) was made before pack.py had its override: there
pack_override was pack.fly() inside the driver's radius_override(0.2).
Writes pack_drill_b2_after_fix.json next to this file. Input: synthetic.
"""
import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = os.path.dirname(HERE)
ROOT = os.path.normpath(os.path.join(BENCH_DIR, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "site", "playground", "results"))
sys.path.insert(0, BENCH_DIR)
import native_parity as NP  # noqa: E402

KEYS = ("outcome", "time_to_goal_s", "min_clearance_m", "path_length_m")
WORLD = os.path.join(ROOT, "docs", "drill-2026-11", "our_room.world.json")
VEH = {"radius_m": 0.2, "v_max": 1.5, "a_max": 3.0, "tau": 0.15}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--planners", default="lazy_thetastar_unknown,thetastar_known,astar_known")
    a = ap.parse_args()
    NP.load_arena()                      # one close_area_arena package for the driver and bench
    import bench                         # before the driver: it leaves close-area-planner-reactive on sys.path,
    import pack                          # which has its own bench.py
    ns = NP.driver_ns()
    presets = bench.presets
    vk = presets.vehicle_kwargs(dict(VEH))
    base = json.load(open(WORLD))
    out = {"input": "synthetic", "world": os.path.relpath(WORLD, ROOT), "vehicle": VEH, "sensor": "depth_cam_87",
           "command": "samples/close-area-benchmark/.venv/bin/python samples/close-area-benchmark/results/"
                      "pack_drill_b2_repro.py --seeds " + a.seeds + " --planners " + a.planners,
           "rows": []}
    wj = bench.A("world_json")
    for s in [int(x) for x in a.seeds.split(",")]:
        j = pack.seed_jitter(base, s, 0.5, vk["radius"])
        doc = dict(base, a=j["a"], b=j["b"])
        for p in a.planners.split(","):
            row = {"planner": p, "seed": s, "a": j["a"], "b": j["b"]}
            for label, infl in (("driver_inflate", True), ("driver_no_inflate", False)):
                r = ns["simulate"](copy.deepcopy(doc), p, "depth_cam_87", "truth", "none", s,
                                   vehicle=dict(VEH), inflate=infl)
                row[label] = {k: r["score"][k] for k in KEYS}
            for label, infl in (("pack_shipped", False), ("pack_override", True)):
                r = pack.fly(p, wj.from_json(doc), "our_room", "depth_cam_87", "depth_cam_87", vk, 60.0, 0, s,
                             inflate=infl)
                row[label] = {k: r[k] for k in KEYS}
            row["same_inflate"] = row["driver_inflate"] == row["pack_override"]
            row["same_shipped"] = row["driver_no_inflate"] == row["pack_shipped"]
            out["rows"].append(row)
            print(p, "seed", s, *(f"{k}={row[k]['outcome']}/{row[k]['time_to_goal_s']}/{row[k]['min_clearance_m']}"
                                  for k in ("driver_inflate", "driver_no_inflate", "pack_shipped", "pack_override")),
                  "same_inflate", row["same_inflate"], "same_shipped", row["same_shipped"], flush=True)
    with open(os.path.join(HERE, "pack_drill_b2_after_fix.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
