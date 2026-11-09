"""Fly A=>B through the flight loop and print a one-line score.

    python main.py --mock                       # A=(0,0,1) => B=(5,3,1), wall beside the line
    python main.py --mock --scenario blocked    # B=(6,0,1) behind the wall: must stop, not crash
    python main.py --mock --scenario blocked --planner blind --safety pass_through   # crashes
    python main.py --mock --planner arena:straight --arena /path/to/navigation-index/samples/close-area-arena

The score is on the mock's own state, which is truth (the mock pose is perfect).
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import math
import os
import sys

from flightloop import GoToGoal, MockAdapter, PassThrough, RangeStop, run

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ARENA = os.environ.get("ARENA_DIR", os.path.join(HERE, "..", "..", "samples", "close-area-arena"))
SCENARIOS = {                       # name: (start, goal)
    "open": ((0.0, 0.0, 1.0), (5.0, 3.0, 1.0)),
    "blocked": ((0.0, 0.0, 1.0), (6.0, 0.0, 1.0)),
}
REACHED_M = 0.3                     # same as the arena scorer
PLANNERS = {                        # built-in planners; arena:<module> loads from the arena
    "go_to_goal": GoToGoal,
    "blind": lambda: GoToGoal(stop_dist=0.0),   # never stops: shows what the safety filter catches
}


def load_arena_planner(name: str, arena_dir: str):
    """Load samples/close-area-arena as package close_area_arena (CONTRACT.md "Import")."""
    arena_dir = os.path.abspath(arena_dir)
    init = os.path.join(arena_dir, "__init__.py")
    if not os.path.exists(init):
        sys.exit(f"arena not found at {arena_dir}: pass --arena or set ARENA_DIR")
    spec = importlib.util.spec_from_file_location(
        "close_area_arena", init, submodule_search_locations=[arena_dir])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules["close_area_arena"] = pkg
    spec.loader.exec_module(pkg)
    return importlib.import_module(f"close_area_arena.planners.{name}").make()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mock", action="store_true", help="fly the stdlib MockAdapter")
    ap.add_argument("--scenario", choices=sorted(SCENARIOS), default="open")
    ap.add_argument("--planner", default="go_to_goal", help="go_to_goal, blind, or arena:<module>")
    ap.add_argument("--arena", default=DEFAULT_ARENA, help="path to samples/close-area-arena")
    ap.add_argument("--safety", choices=["range_stop", "pass_through"], default="range_stop")
    ap.add_argument("--timeout", type=float, default=30.0, help="flight time limit, s")
    ap.add_argument("--log", default=None, help="JSONL path (default runs/<scenario>.jsonl)")
    ap.add_argument("--realtime", action="store_true", help="pace at 20 Hz wall time")
    a = ap.parse_args(argv)
    if not a.mock:
        sys.exit("no real driver yet: write drivers/<platform>.py (see README) and wire it here")
    if a.planner not in PLANNERS and not a.planner.startswith("arena:"):
        ap.error(f"--planner must be one of {sorted(PLANNERS)} or arena:<module>")

    start, goal = SCENARIOS[a.scenario]
    ad = MockAdapter(start=start)
    planner = (load_arena_planner(a.planner.split(":", 1)[1], a.arena)
               if a.planner.startswith("arena:") else PLANNERS[a.planner]())
    safety = RangeStop() if a.safety == "range_stop" else PassThrough()
    log_path = a.log or os.path.join("runs", f"{a.scenario}.jsonl")
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "w") as log:
        r = run(ad, planner, safety, goal, log=log, timeout_s=a.timeout, realtime=a.realtime)
    truth = ad.pose()
    d_goal = math.dist((truth.x, truth.y, truth.z), goal)
    modes = ",".join(f"{k}:{v}" for k, v in sorted(r.modes.items()))
    print(f"score scenario={a.scenario} planner={a.planner} safety={safety.name} "
          f"reached={d_goal < REACHED_M} final_dist_m={d_goal:.3f} t_s={r.t_s:.2f} "
          f"collided={ad.collided} min_wall_dist_m={ad.min_wall_dist:.2f} ticks={r.ticks} "
          f"intervened={r.intervened_ticks} keepalive={r.keepalive_ticks} overruns={r.overrun_ticks} modes={modes} log={log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
