"""Check: every bench:<id> through this loop on one world file, plus the arena's own
10 Hz reference loop for narrow_gap_0 / dstar_lite. Synthetic. Run from templates/flight-repo:

    .venv/bin/python results/bench_parity.py [--hub ../..] > results/bench_parity.txt

1. Reference: run.run_one (10 Hz planner, 50 Hz physics, no filter) on world_json.from_json(file),
   planner from bench.PLANNERS["dstar_lite"][0](world), seed 0: the playground driver's check E recipe.
2. Sweep: main.py --adapter world:<file> --planner bench:<id> --safety arm:F0 and arm:F2 for every
   id in bench.PLANNERS, one process each, score line kept as printed (truth, 50 Hz physics).
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub", default=os.path.join(REPO, "..", ".."))
    ap.add_argument("--world", default=None, help="default <hub>/site/playground/presets/narrow_gap_0.json")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    hub = os.path.abspath(a.hub)
    bench_dir = os.path.join(hub, "samples", "close-area-benchmark")
    arena_dir = os.path.join(hub, "samples", "close-area-arena")
    safety_dir = os.path.join(hub, "samples", "close-area-safety-filter")
    world = a.world or os.path.join(hub, "site", "playground", "presets", "narrow_gap_0.json")
    rel = lambda p: os.path.relpath(p, REPO)                     # noqa: E731

    from flightloop import bench_planner
    from flightloop.arena_adapter import load_arena
    load_arena(arena_dir)
    import numpy, scipy                                          # noqa: E401
    rows = bench_planner.describe(bench_dir)
    print(f"# bench_parity, {time.strftime('%Y-%m-%d %H:%M')}, input synthetic, world {rel(world)}, "
          f"Python {sys.version.split()[0]}, numpy {numpy.__version__}, scipy {scipy.__version__}")

    run = importlib.import_module("close_area_arena.run")
    wj = importlib.import_module("close_area_arena.world_json")
    b = bench_planner.load_bench(bench_dir)
    doc = json.load(open(world))
    w = wj.from_json(doc)
    pl = b.PLANNERS["dstar_lite"][0](w)
    t0 = time.perf_counter()
    r, _, _ = run.run_one(pl, w, 0, doc.get("index") or 0, run.DEFAULTS)
    keep = {k: r[k] for k in ("outcome", "time_to_goal_s", "min_clearance_m", "path_length_m", "duration_s", "planner_ms_mean", "planner_ms_max") if k in r}
    print(f"REFERENCE run.run_one 10 Hz, no filter, dstar_lite: {json.dumps(keep)} wall_s={time.perf_counter() - t0:.2f}")

    def fly(pid, arm):
        cmd = [sys.executable, "main.py", "--adapter", f"world:{rel(world)}", "--planner", f"bench:{pid}",
               "--safety", f"arm:{arm}", "--arena", rel(arena_dir), "--safety-dir", rel(safety_dir),
               "--bench-dir", rel(bench_dir), "--log", os.path.join("runs", f"bench_{pid}_{arm}.jsonl")]
        t = time.perf_counter()
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        line = next((ln for ln in p.stdout.splitlines() if ln.startswith("score ")), None)
        err = p.stderr.strip().splitlines()[-1] if p.returncode and p.stderr.strip() else ""
        return pid, arm, p.returncode, line, err, time.perf_counter() - t

    jobs = [(r["id"], arm) for r in rows for arm in ("F0", "F2")]
    with ThreadPoolExecutor(a.workers) as ex:
        out = list(ex.map(lambda j: fly(*j), jobs))
    info = {r["id"]: r for r in rows}
    print("id | needs_world | arm | rc | reached | final_dist_m | t_s | min_clearance_m | keepalive | wall_s")
    for pid, arm, rc, line, err, wall in out:
        f = dict(kv.split("=", 1) for kv in (line or "").split()[1:] if "=" in kv)
        if line:
            print(f"{pid} | {info[pid]['needs_world']} | {arm} | {rc} | {f['reached']} | {f['final_dist_m']} | "
                  f"{f['t_s']} | {f['min_clearance_m']} | {f['keepalive']} | {wall:.1f}")
        else:
            print(f"{pid} | {info[pid]['needs_world']} | {arm} | {rc} | not flown: {err} | | | | | {wall:.1f}")
    print("FULL", "dstar_lite F0:", next(o[3] for o in out if o[0] == "dstar_lite" and o[1] == "F0"))
    print("FULL", "dstar_lite F2:", next(o[3] for o in out if o[0] == "dstar_lite" and o[1] == "F2"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
