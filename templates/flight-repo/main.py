"""Fly A=>B through the flight loop and print a one-line score.

    python main.py --mock                       # A=(0,0,1) => B=(5,3,1), wall beside the line
    python main.py --mock --scenario blocked    # B=(6,0,1) behind the wall: must stop, not crash
    python main.py --mock --scenario blocked --planner blind --safety pass_through   # crashes
    python main.py --mock --planner arena:straight --arena /path/to/navigation-index/samples/close-area-arena

Arena world (needs the arena venv: make venv, then .venv python of the arena):
    python main.py --adapter arena:random:0 --planner arena:astar_esdf --safety arm:F2 [--fault jump]
    --adapter arena:<family>:<seed>[:<index>]   layout from samples/close-area-arena/world.py
    --fault none|jump|bias|dropout|overconfident  arena estimator.py with dark zones; omit => truth pose
    --safety arm:F0|F1|F2                        kill-test arm from samples/close-area-safety-filter
The arena log is close-area-log/1 (log_format.md); score it with the arena's score_log.py.

The score line is on truth: the mock's own state, or the arena's sim truth.
"""
from __future__ import annotations

import argparse
import importlib
import math
import os
import sys

from flightloop import GoToGoal, MockAdapter, PassThrough, RangeStop, run
from flightloop.arena_adapter import load_arena

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ARENA = os.environ.get("ARENA_DIR", os.path.join(HERE, "..", "..", "samples", "close-area-arena"))
DEFAULT_SAFETY_DIR = os.environ.get("SAFETY_DIR", os.path.join(HERE, "..", "..", "samples", "close-area-safety-filter"))
TIMEOUT_MOCK_S = 30.0
TIMEOUT_ARENA_S = 60.0              # arena run.DEFAULTS["max_time_s"]
FAULTS = ("none", "jump", "bias", "dropout", "overconfident")   # arena faults.CASES
ARMS = ("F0", "F1", "F2")           # close-area-safety-filter filters.REGISTRY
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
    try:
        load_arena(arena_dir)
    except FileNotFoundError as e:
        sys.exit(str(e))
    return importlib.import_module(f"close_area_arena.planners.{name}").make()


def make_safety(name: str, safety_dir: str, world=None):
    if name == "range_stop":
        return RangeStop()
    if name == "pass_through":
        return PassThrough()
    from flightloop.safety_shim import ArmShim
    try:
        return ArmShim(name.split(":", 1)[1], safety_dir, world=world)
    except FileNotFoundError as e:
        sys.exit(str(e))
    except ImportError as e:
        sys.exit(f"{name} needs numpy ({e}): run with the arena venv python (make venv)")


def fly_arena(a, safety_name: str) -> int:
    from flightloop.arena_adapter import ArenaAdapter, CloseAreaLog
    try:
        ad = ArenaAdapter.from_spec(a.adapter, a.arena, fault=a.fault)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(str(e))
    except ImportError as e:
        sys.exit(f"the arena needs numpy and scipy ({e}): run with the arena venv python (make venv)")
    planner = (load_arena_planner(a.planner.split(":", 1)[1], a.arena)
               if a.planner.startswith("arena:") else PLANNERS[a.planner]())
    safety = make_safety(safety_name, a.safety_dir, world=ad.world)
    getattr(safety, "reset", lambda: None)()
    stem = a.adapter.replace(":", "_") + ("" if a.fault is None else f"_{a.fault}")
    log_path = a.log or os.path.join("runs", f"{stem}.jsonl")
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    source = (f"flight-repo loop, close-area-arena {ad.family} seed {ad.seed} index {ad.index}, "
              f"planner {a.planner}, safety {safety.name}, pose {'truth' if a.fault is None else 'estimator fault ' + a.fault}")
    timeout = TIMEOUT_ARENA_S if a.timeout is None else a.timeout
    with open(log_path, "w", buffering=1) as fh:
        log = CloseAreaLog(fh, ad, planner, source=source,
                           notes="filter_intervened = safety arm changed the setpoint; loop_mode = flight-loop mode")
        r = run(ad, planner, safety, ad.goal, grid=ad.grid, log=log, timeout_s=timeout,
                realtime=a.realtime)
    tr = ad.sim.truth()
    d_goal = math.hypot(tr.x - ad.goal[0], tr.y - ad.goal[1])
    modes = ",".join(f"{k}:{v}" for k, v in sorted(r.modes.items()))
    health = ",".join(f"{k}:{v}" for k, v in sorted(r.health.items()))
    print(f"score input=synthetic adapter={a.adapter} fault={a.fault or 'truth'} planner={a.planner} "
          f"safety={safety.name} reached={d_goal < REACHED_M and not ad.collided} final_dist_m={d_goal:.3f} "
          f"t_s={r.t_s:.2f} collided={ad.collided} min_clearance_m={ad.min_clearance:.3f} "
          f"max_pose_error_m={ad.max_pose_error:.3f} ticks={r.ticks} intervened={r.intervened_ticks} "
          f"keepalive={r.keepalive_ticks} planner_errors={r.planner_errors} modes={modes} health={health} log={log_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mock", action="store_true", help="fly the stdlib MockAdapter (= --adapter mock)")
    ap.add_argument("--adapter", default=None, help="mock or arena:<family>:<seed>[:<index>]")
    ap.add_argument("--fault", choices=FAULTS, default=None,
                    help="arena only: fly on the arena estimator with this fault (default: truth pose)")
    ap.add_argument("--safety-dir", default=DEFAULT_SAFETY_DIR, help="path to samples/close-area-safety-filter")
    ap.add_argument("--scenario", choices=sorted(SCENARIOS), default="open")
    ap.add_argument("--planner", default="go_to_goal", help="go_to_goal, blind, or arena:<module>")
    ap.add_argument("--arena", default=DEFAULT_ARENA, help="path to samples/close-area-arena")
    ap.add_argument("--safety", default="range_stop", help="range_stop, pass_through or arm:F0|F1|F2")
    ap.add_argument("--timeout", type=float, default=None,
                    help=f"flight time limit, s (default {TIMEOUT_MOCK_S:g} mock, {TIMEOUT_ARENA_S:g} arena)")
    ap.add_argument("--log", default=None, help="JSONL path (default runs/<scenario>.jsonl)")
    ap.add_argument("--realtime", action="store_true", help="pace at 20 Hz wall time")
    a = ap.parse_args(argv)
    if a.planner not in PLANNERS and not a.planner.startswith("arena:"):
        ap.error(f"--planner must be one of {sorted(PLANNERS)} or arena:<module>")
    if a.safety not in ("range_stop", "pass_through") and a.safety not in (f"arm:{x}" for x in ARMS):
        ap.error(f"--safety must be range_stop, pass_through or arm:<{'|'.join(ARMS)}>")
    if a.adapter and a.adapter.startswith("arena:"):
        return fly_arena(a, a.safety)
    if a.fault is not None:
        ap.error("--fault needs --adapter arena:...")
    if not (a.mock or a.adapter == "mock"):
        sys.exit("no real driver yet: write drivers/<platform>.py (see README) and wire it here")

    start, goal = SCENARIOS[a.scenario]
    ad = MockAdapter(start=start)
    planner = (load_arena_planner(a.planner.split(":", 1)[1], a.arena)
               if a.planner.startswith("arena:") else PLANNERS[a.planner]())
    safety = make_safety(a.safety, a.safety_dir)
    log_path = a.log or os.path.join("runs", f"{a.scenario}.jsonl")
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "w") as log:
        r = run(ad, planner, safety, goal, log=log, realtime=a.realtime,
                timeout_s=TIMEOUT_MOCK_S if a.timeout is None else a.timeout)
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
