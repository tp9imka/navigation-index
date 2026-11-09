"""Export a few arena runs as compact replay JSON for the showcase page (site/showcase.html).

.venv/bin/python export_replay.py [--out ../../site/data/showcase/replays]

Runs four seed-0 layouts with traces (about 10-30 s, the A* run is the slow one):
  u_trap_straight      straight baseline on u_trap layout 0
  u_trap_astar         A* + ESDF, unknown map (builds its grid from ranges), same layout
  random_freest_beam   CONTRACT.md freest_beam example on random layout 0, planner sees truth
  random_freest_jump   same planner and layout, planner sees the VIO-like EKF (estimator.py)
                       with dark zones and the "jump" fault (faults.py)

Each file has the obstacles, A (origin), B, the truth path at 10 Hz, the estimated path the
planner saw (fault run only), truth clearance per kept step, and the scorer row. All inputs are
synthetic. Where results/ already holds the same (planner, case, family, seed, index) row, the
outcome is compared and printed, so a drift from the published tables shows up here.
Writes <out>/<name>.json and <out>/index.json (the run list the page reads).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time

import numpy as np

try:
    from . import estimator, run
    from .run_faults import FreestBeam
except ImportError:
    import estimator
    import run
    from run_faults import FreestBeam

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.normpath(os.path.join(HERE, "..", "..", "site", "data", "showcase", "replays"))
KEEP_EVERY = 5          # 50 Hz physics => 10 Hz in the file
MAX_BYTES = 150_000


class Recorder:
    """Wraps a PoseSource and keeps what the planner was told at every planner step."""

    def __init__(self, inner):
        self.inner = inner
        self.rows = []

    def __call__(self, truth):
        p = self.inner(truth)
        self.rows.append([round(p.t, 2), round(p.x, 3), round(p.y, 3),
                          round(p.sigma_xy, 3), int(p.quality)])
        return p


RUNS = [
    {"name": "u_trap_straight", "title": "U trap: straight line",
     "planner": "straight", "family": "u_trap", "index": 0, "case": None,
     "note": "Flies the A-B line and slows to a stop in front of the cup. Never steers.",
     "published": "straight_u_trap_0.json"},
    {"name": "u_trap_astar", "title": "U trap: A* + ESDF, unknown map",
     "planner": "astar_esdf", "kw": {"known_map": False}, "family": "u_trap", "index": 0, "case": None,
     "note": "Builds its map from range returns only, replans at 2-5 Hz, goes around the cup.",
     "published": None},
    {"name": "random_freest_beam", "title": "Clutter: freest beam, true pose",
     "planner": "freest_beam", "family": "random", "index": 0, "case": "truth",
     "note": "15-line reactive planner from CONTRACT.md. Planner sees the true pose.",
     "published": "faults_freest_beam_truth_0.json"},
    {"name": "random_freest_jump", "title": "Clutter: freest beam, drifting EKF + 0.5 m jump",
     "planner": "freest_beam", "family": "random", "index": 0, "case": "jump",
     "note": "Same planner and layout. It now sees a VIO-like EKF with dark zones and a 0.5 m "
             "position jump near an obstacle. Ranges and scoring stay on truth.",
     "published": "faults_freest_beam_jump_0.json"},
]


def factory(spec):
    if spec["planner"] == "freest_beam":
        return lambda: FreestBeam()
    kw = spec.get("kw", {})
    return lambda: run.load_planner(spec["planner"], **kw)


def export(spec, out_dir):
    recs, ests = [], []
    mps = None
    if spec["case"] not in (None, "truth"):
        inner = estimator.make_pose_source_factory(spec["case"], dark=True, sink=ests)

        def mps(world, seed, index):
            r = Recorder(inner(world, seed, index))
            recs.append(r)
            return r

    t0 = time.perf_counter()
    rows, _, traces = run.evaluate(factory(spec), spec["family"], spec["index"] + 1, 0,
                                   make_pose_source=mps, keep_traces=True)
    wall = time.perf_counter() - t0
    row = rows[spec["index"]]
    w, ts, xy = traces[spec["index"]]
    keep = list(range(0, len(ts), KEEP_EVERY))
    if keep[-1] != len(ts) - 1:
        keep.append(len(ts) - 1)
    clear = w.sdf(xy[keep])
    wd = w.to_dict()
    doc = {
        "name": spec["name"], "title": spec["title"], "note": spec["note"],
        "input": "synthetic", "planner": spec["planner"] + ("_unknown_map" if spec.get("kw") else ""),
        "case": spec["case"] or "truth", "family": spec["family"], "seed": 0, "index": spec["index"],
        "command": f"python export_replay.py ({spec['name']})",
        "area": wd["area"], "a": [0.0, 0.0], "b": [round(v, 3) for v in wd["goal"]],
        "boxes": [[round(v, 3) for v in b] for b in wd["boxes"]],
        "cylinders": [[round(v, 3) for v in c] for c in wd["cylinders"]],
        "radius": run.DEFAULTS["vehicle"]["radius"], "goal_tol_m": 0.3, "hz": 50 // KEEP_EVERY,
        "t": [round(float(ts[k]), 2) for k in keep],
        "truth": [[round(float(xy[k, 0]), 3), round(float(xy[k, 1]), 3)] for k in keep],
        "clearance": [round(float(c), 3) for c in clear],
        "est": recs[spec["index"]].rows if recs else None,
        "dark_zones": [z.to_list() for z in ests[spec["index"]].zones] if ests else [],
        "fault_log": ests[spec["index"]].fault.log if ests and ests[spec["index"]].fault else None,
        "score": {k: row[k] for k in ("outcome", "time_to_goal_s", "min_clearance_m", "path_length_m",
                                       "duration_s", "max_pose_error_m", "n_obstacles")},
        "env": {"python": platform.python_version(), "numpy": np.__version__,
                "machine": platform.machine(), "system": platform.system()},
    }
    path = os.path.join(out_dir, spec["name"] + ".json")
    with open(path, "w") as fh:
        json.dump(doc, fh, separators=(",", ":"), default=float)
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise SystemExit(f"{path} is {size} bytes, over {MAX_BYTES}")

    check = "no published row"
    if spec["published"]:
        pub = json.load(open(os.path.join(HERE, "results", spec["published"])))
        prow = next(r for r in pub["runs"] if r["index"] == spec["index"])
        same = (prow["outcome"] == row["outcome"] and prow["min_clearance_m"] == row["min_clearance_m"])
        check = f"matches results/{spec['published']}" if same else (
            f"DIFFERS from results/{spec['published']}: {prow['outcome']} {prow['min_clearance_m']}")
    print(f"{spec['name']}: {row['outcome']}, min clearance {row['min_clearance_m']} m, "
          f"path {row['path_length_m']} m, max pose err {row['max_pose_error_m']} m, "
          f"{size} bytes, wall {wall:.1f} s; {check}")
    return {"file": spec["name"] + ".json", "name": spec["name"], "title": spec["title"],
            "outcome": row["outcome"], "bytes": size}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    listing = [export(s, a.out) for s in RUNS]
    with open(os.path.join(a.out, "index.json"), "w") as fh:
        json.dump({"generated_by": "samples/close-area-arena/export_replay.py", "input": "synthetic",
                   "generated": time.strftime("%Y-%m-%d"), "runs": listing}, fh, indent=1)
    print(f"wrote {len(listing)} replays + index.json to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
