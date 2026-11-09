"""Export one replay per arena family x planner for the showcase and the playground.

.venv/bin/python export_replays.py [--out ../../site/data/showcase/replays_v2]
.venv/bin/python export_replays.py --merge --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite
    (export only these planners; index.json keeps every other planner's entry and file as it was)

For every family in bench.FAMILIES, layout 0, seed 0, every planner in bench.DEFAULT_PLANNERS is
flown again through bench.run_one with its trace kept. Preset: crazyflie for glass_office (so
the glass is invisible to the rangers), ideal for every other family.

Each <family>__<planner>.json holds:
  schema "close-area-replay/2", input "synthetic", planner / family / preset / seed / index,
  world      world_json.to_json(world) (close-area-world/1, the playground format)
  hz, t      kept sample rate and times (s)
  truth      [[x, y], ...] truth path at the kept samples
  est        null (every matrix run gives the planner the true pose)
  clearance  truth clearance per kept sample (m, centre to nearest surface)
  outcome    and the scorer row (time_to_goal_s, min_clearance_m, path_length_m, duration_s, ...)
  matrix     the same row in results/matrix_0.json and whether outcome and min clearance match
The path is kept at 10 Hz and thinned further if a file would pass MAX_BYTES (120 KB); the last
sample is always kept. index.json lists the files grouped by family.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time

import bench

world_json = importlib.import_module("close_area_arena.world_json")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.normpath(os.path.join(HERE, "..", "..", "site", "data", "showcase", "replays_v2"))
MATRIX = os.path.join(HERE, "results", "matrix_0.json")
MAX_BYTES = 120_000
SCORE_KEYS = ("outcome", "time_to_goal_s", "min_clearance_m", "path_length_m", "duration_s",
              "n_obstacles", "n_glass", "hit_material", "intervention_frac", "max_time_s")


def preset_for(family: str) -> str:
    return "crazyflie" if family == "glass_office" else "ideal"


def _doc(row, w, ts, xy, every, planner, preset, check):
    keep = list(range(0, len(ts), every))
    if keep[-1] != len(ts) - 1:
        keep.append(len(ts) - 1)
    clr = w.sdf(xy[keep])
    _, filt, label, sample = bench.PLANNERS[planner]
    return {
        "schema": "close-area-replay/2", "input": "synthetic",
        "generated_by": "samples/close-area-benchmark/export_replays.py",
        "planner": planner, "label": label, "planner_sample": sample, "filter": filt,
        "family": row["family"], "preset": preset, "seed": row["seed"], "index": row["index"],
        "world": world_json.to_json(w),
        "hz": round(50 / every, 3), "goal_tol_m": 0.3,
        "t": [round(float(ts[k]), 2) for k in keep],
        "truth": [[round(float(xy[k, 0]), 3), round(float(xy[k, 1]), 3)] for k in keep],
        "est": None,
        "clearance": [round(float(c), 3) for c in clr],
        "outcome": row["outcome"],
        "score": {k: row.get(k) for k in SCORE_KEYS},
        "matrix": check,
    }


def export_one(planner, family, out_dir, matrix_rows):
    preset = preset_for(family)
    t0 = time.perf_counter()
    row, (w, ts, xy) = bench.run_one(planner, family, preset, 0, 0, keep_trace=True)
    wall = time.perf_counter() - t0
    ref = matrix_rows.get((planner, family, preset, 0))
    if ref is None:
        check = {"row": None, "match": None, "note": "no row in results/matrix_0.json"}
    else:
        same = ref["outcome"] == row["outcome"] and ref["min_clearance_m"] == row["min_clearance_m"]
        check = {"row": "results/matrix_0.json", "outcome": ref["outcome"],
                 "min_clearance_m": ref["min_clearance_m"], "match": bool(same)}
    every = 5                                    # 50 Hz physics => 10 Hz
    while True:
        text = json.dumps(_doc(row, w, ts, xy, every, planner, preset, check), separators=(",", ":"))
        if len(text.encode()) <= MAX_BYTES or every >= len(ts):
            break
        every *= 2
    name = f"{family}__{planner}.json"
    with open(os.path.join(out_dir, name), "w") as fh:
        fh.write(text)
    size = len(text.encode())
    wd = json.loads(text)["world"]
    rt = world_json.to_json(world_json.from_json(wd)) == wd   # playground format round trip
    print(f"{name}: {row['outcome']}, min clearance {row['min_clearance_m']} m, {size} bytes, "
          f"{50 / every:g} Hz, world JSON round trip {'ok' if rt else 'FAILED'}, wall {wall:.1f} s; matrix {'match' if check['match'] else check}", flush=True)
    return {"file": name, "planner": planner, "label": bench.PLANNERS[planner][2], "outcome": row["outcome"],
            "time_to_goal_s": row["time_to_goal_s"], "min_clearance_m": row["min_clearance_m"],
            "bytes": size, "hz": round(50 / every, 3), "matches_matrix": check["match"], "world_roundtrip": rt}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--families", default=",".join(bench.FAMILIES))
    ap.add_argument("--planners", default=",".join(bench.DEFAULT_PLANNERS))
    ap.add_argument("--merge", action="store_true",
                    help="keep the entries of index.json for planners not exported this time (their files are "
                         "not rewritten); new entries are inserted in bench.DEFAULT_PLANNERS order")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    kept = {}                                   # family => existing index entries kept by --merge
    idx_path = os.path.join(a.out, "index.json")
    if a.merge and os.path.exists(idx_path):
        redo = set(a.planners.split(","))
        for g in json.load(open(idx_path))["families"]:
            kept[g["family"]] = [r for r in g["runs"] if r["planner"] not in redo
                                 and os.path.exists(os.path.join(a.out, r["file"]))]
    matrix_rows = {}
    if os.path.exists(MATRIX):
        for r in json.load(open(MATRIX))["runs"]:
            matrix_rows[(r["planner"], r["family"], r["preset"], r["index"])] = r
    t0 = time.perf_counter()
    groups = []
    for fam in a.families.split(","):
        runs = [export_one(p, fam, a.out, matrix_rows) for p in a.planners.split(",") if bench.available(p)]
        if kept.get(fam):
            order = {p: k for k, p in enumerate(bench.DEFAULT_PLANNERS)}
            runs = sorted(kept[fam] + runs, key=lambda r: order.get(r["planner"], len(order)))
        groups.append({"family": fam, "preset": preset_for(fam), "seed": 0, "index": 0, "runs": runs})
    allr = [r for g in groups for r in g["runs"]]
    idx = {"schema": "close-area-replay-index/2", "generated_by": "samples/close-area-benchmark/export_replays.py",
           "input": "synthetic", "generated": time.strftime("%Y-%m-%d"),
           "note": "Layout 0, seed 0 of each family. Preset crazyflie for glass_office, ideal otherwise. "
                   "Planner sees the true pose; scored on truth.",
           "max_bytes": MAX_BYTES, "n_files": len(allr),
           "matches_matrix": sum(bool(r["matches_matrix"]) for r in allr), "families": groups}
    with open(os.path.join(a.out, "index.json"), "w") as fh:
        json.dump(idx, fh, indent=1)
    n_kept = sum(len(v) for v in kept.values())
    if n_kept:
        print(f"--merge: kept {n_kept} existing index entries (files not rewritten, match flags as stored)")
    print(f"wrote {len(allr) - n_kept} replays, index.json lists {len(allr)} to {os.path.relpath(a.out, HERE)}; {idx['matches_matrix']}/{len(allr)} match "
          f"results/matrix_0.json; world JSON round trip ok {sum(r['world_roundtrip'] for r in allr)}/{len(allr)}; max {max(r['bytes'] for r in allr)} bytes; wall {time.perf_counter() - t0:.1f} s")
    return 0 if idx["matches_matrix"] == len(allr) else 1


if __name__ == "__main__":
    sys.exit(main())
