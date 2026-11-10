"""Export one search run as a replay JSON (close-area-replay/2 with the world in close-area-world/1).

.venv/bin/python export_replay.py [--family office --index 0 --arm nominal_frontier --region 5 --preset ideal]

Same top-level fields as samples/close-area-benchmark/export_replays.py writes to
site/data/showcase/replays_v2/ (schema close-area-replay/2): "world" is world_json.to_json of the
layout (close-area-world/1, B = the true B), truth path and clearance at 10 Hz, est null (true
pose), outcome and score. Added: "search" (region radius, nominal, detection range, time B was
detected, time at B). Written to results/, not to site/.
Input: synthetic. The run is recomputed and compared with the same row in results/bench_0.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

import explore
from arena import world_json

HERE = os.path.dirname(os.path.abspath(__file__))
KEEP_EVERY = 5          # 50 Hz physics => 10 Hz
MAX_BYTES = 150_000


def export(family, index, arm, region, preset, seed=0, out=None):
    row, w, ts, xy = explore.run_one(arm, family, seed, index, region, preset, keep_trace=True)
    keep = list(range(0, len(ts), KEEP_EVERY))
    if keep[-1] != len(ts) - 1:
        keep.append(len(ts) - 1)
    wd = world_json.to_json(w)
    wd["index"] = index
    doc = {
        "schema": "close-area-replay/2", "input": "synthetic",
        "generated_by": "samples/close-area-explore/export_replay.py",
        "planner": arm, "label": f"search: {arm}, region {'unknown' if region is None else f'{region:g} m'}",
        "planner_sample": "close-area-explore", "filter": None,
        "family": family, "preset": preset, "seed": seed, "index": index,
        "world": wd, "hz": 50.0 / KEEP_EVERY, "goal_tol_m": 0.3,
        "t": [round(float(ts[k]), 2) for k in keep],
        "truth": [[round(float(xy[k, 0]), 3), round(float(xy[k, 1]), 3)] for k in keep],
        "est": None,
        "clearance": [round(float(c), 3) for c in w.sdf(xy[keep])],
        "outcome": row["outcome"],
        "score": {k: row[k] for k in ("outcome", "time_to_goal_s", "min_clearance_m", "path_length_m",
                                      "duration_s")},
        "search": {"region_m": region, "nominal": row["nominal"], "nominal_err_m": row["nominal_err_m"],
                   "detect_range_m": explore.DETECT_RANGE_M, "found": row["found"],
                   "t_found": row["time_to_find_s"], "time_to_b_s": row["time_to_b_s"],
                   "search_targets": row["search_targets"], "known_free_m2": row["known_free_m2"]},
    }
    r = "unknown" if region is None else f"{region:g}"
    out = out or os.path.join(HERE, "results", f"replay_{family}_{index}_{arm}_r{r}_{preset}.json")
    with open(out, "w") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    size = os.path.getsize(out)
    if size > MAX_BYTES:
        raise SystemExit(f"{out} is {size} bytes, over {MAX_BYTES}")
    w2 = world_json.from_json(json.load(open(out))["world"])
    same_world = world_json.to_json(w2) == wd
    check = "no results/bench_0.json"
    pub = os.path.join(HERE, "results", "bench_0.json")
    if os.path.exists(pub) and seed == 0:
        runs = json.load(open(pub))["runs"]
        p = next((x for x in runs if x["family"] == family and x["index"] == index and x["arm"] == arm
                  and x["region_m"] == region and x["preset"] == preset), None)
        if p is None:
            check = "row not in results/bench_0.json"
        else:
            same = all(p[k] == row[k] for k in ("outcome", "time_to_find_s", "path_length_m", "min_clearance_m"))
            check = "matches results/bench_0.json" if same else "DIFFERS from results/bench_0.json"
            doc["matrix"] = {"row": "results/bench_0.json", "outcome": p["outcome"],
                             "min_clearance_m": p["min_clearance_m"], "match": same}
            with open(out, "w") as fh:
                json.dump(doc, fh, separators=(",", ":"))
    size = os.path.getsize(out)
    print(f"{os.path.relpath(out, HERE)}: {row['outcome']}, found at {row['time_to_find_s']} s, at B "
          f"{row['time_to_b_s']} s, {size} bytes, world round trip {'ok' if same_world else 'FAILED'}; {check}")
    return 0 if same_world else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--family", default="office")
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--arm", default="nominal_frontier", choices=explore.ARMS)
    ap.add_argument("--region", default="5", help="metres, or 'unknown'")
    ap.add_argument("--preset", default="ideal")
    a = ap.parse_args(argv)
    region = None if a.region == "unknown" else float(a.region)
    return export(a.family, a.index, a.arm, region, a.preset)


if __name__ == "__main__":
    sys.exit(main())
