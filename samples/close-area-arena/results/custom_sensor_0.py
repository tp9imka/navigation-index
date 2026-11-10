"""Forward depth camera vs the ideal 360 deg fan (loop-75), synthetic, seed 0.

Run from the repo root with the arena venv:
    samples/close-area-arena/.venv/bin/python samples/close-area-arena/results/custom_sensor_0.py

Flies the playground driver (site/playground/worker.js DRIVER_PY, extracted by
site/playground/results/native_parity.py driver_ns) on site/playground/presets/{random_0, office_0, maze_0}.json,
truth pose, no filter, with three sensor configs:
  ideal              72 rays, 360 deg, 6 m (run.DEFAULTS sensor), yaw fixed toward B as in run.py
  depth_cam_87       presets.SENSOR_SPECS["depth_cam_87"], look-where-you-go yaw (worker.js look_where_you_go)
  depth_cam_87 fixed the same camera with the yaw policy off (yaw fixed toward B), to show what the policy buys
Planners:
  astar_unknown      bench.py GeofencedAStar (map corner on the area bounds), the benchmark matrix_0.json definition
  mppi_astar         MPPI on the unknown-map A* path, geofenced (the playground entry = bench.py)
  astar_unknown_pg   the playground's astar_unknown entry (shipped map corner at (-2.5, -2.5)), for reference
Writes custom_sensor_0.json and custom_sensor_0.md next to this file.
"""
import importlib
import importlib.util
import json
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "site", "playground", "results"))
import native_parity as NP  # noqa: E402

WORLDS = ("random_0", "office_0", "maze_0")
PLANNERS = ("astar_unknown", "mppi_astar", "astar_unknown_pg")
SENSORS = (("ideal", "auto"), ("depth_cam_87", "auto"), ("depth_cam_87", "off"))
SENSOR_LABEL = {("ideal", "auto"): "ideal", ("depth_cam_87", "auto"): "depth_cam_87",
                ("depth_cam_87", "off"): "depth_cam_87 fixed yaw"}
SEED = 0


def main():
    NP.load_arena()
    ns = NP.driver_ns()
    spec = importlib.util.spec_from_file_location("close_area_benchmark_bench", NP.BENCH)
    bench = importlib.util.module_from_spec(spec)
    saved = sys.modules.pop("arena", None)
    try:
        spec.loader.exec_module(bench)
    finally:
        if saved is not None:
            sys.modules["arena"] = saved
    pg_astar = ns["PLANNERS"]["astar_unknown"]
    ns["PLANNERS"]["astar_unknown_pg"] = pg_astar
    ns["PLANNERS"]["astar_unknown"] = lambda w: bench.PLANNERS["astar_unknown"][0](w)
    ns["WORLD_PLANNERS"].add("astar_unknown")
    docs = {w: json.load(open(os.path.join(NP.PG, "presets", w + ".json"))) for w in WORLDS}
    rows = []
    t_all = time.perf_counter()
    for wname in WORLDS:
        for planner in PLANNERS:
            for preset, yaw in SENSORS:
                t0 = time.perf_counter()
                r = ns["simulate"](docs[wname], planner, preset, "truth", "none", SEED, yaw_policy=yaw)
                rows.append({"world": wname, "planner": planner, "sensor": SENSOR_LABEL[(preset, yaw)],
                             "preset": preset, "yaw_policy": r["sensor"]["yaw_policy"], "score": NP.pick(r["score"]),
                             "max_time_s": r["max_time_s"], "wall_s": round(time.perf_counter() - t0, 3)})
                print(wname, planner, SENSOR_LABEL[(preset, yaw)], NP.pick(r["score"]), flush=True)
    import numpy as np
    import scipy
    presets = sys.modules["close_area_arena.presets"]
    out = {"input": "synthetic", "seed": SEED,
           "command": "samples/close-area-arena/.venv/bin/python samples/close-area-arena/results/custom_sensor_0.py",
           "sensors": {"ideal": presets.describe_sensor("ideal"), "depth_cam_87": presets.describe_sensor("depth_cam_87")},
           "yaw_policy": {"cap_rad_s": ns["YAW_RATE_CAP"], "gain_per_s": ns["YAW_GAIN"], "slow_mps": ns["YAW_SLOW_MPS"]},
           "env": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                   "machine": platform.machine()},
           "wall_s": round(time.perf_counter() - t_all, 1), "runs": rows}
    with open(os.path.join(HERE, "custom_sensor_0.json"), "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    f = lambda v: "-" if v is None else v  # noqa: E731
    lines = []
    for wname in WORLDS:
        for planner in PLANNERS:
            cells = []
            for preset, yaw in SENSORS:
                s = next(r for r in rows if (r["world"], r["planner"], r["sensor"]) == (wname, planner, SENSOR_LABEL[(preset, yaw)]))["score"]
                cells.append(f"{s['outcome']} / {f(s['time_to_goal_s'])} / {s['min_clearance_m']}")
            lines.append(f"| {wname} | {planner} | " + " | ".join(cells) + " |")
    with open(os.path.join(HERE, "custom_sensor_0.table.md"), "w") as fh:
        fh.write("| world | planner | ideal | depth_cam_87 | depth_cam_87 fixed yaw |\n|---|---|---|---|---|\n"
                 + "\n".join(lines) + "\n")
    print(f"wall {out['wall_s']} s; wrote custom_sensor_0.json, custom_sensor_0.table.md")


if __name__ == "__main__":
    main()
