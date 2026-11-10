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
    --reloc [--odom PATH]                        relocalize after VIO loss (close-area-relocalize arm
                                                 multi_ig), ODOMETRY-like dry-run JSONL with reset_counter
Any close-area-benchmark planner, in an arena layout or a close-area-world/1 file (playground preset):
    python main.py --adapter world:../../site/playground/presets/narrow_gap_0.json --planner bench:dstar_lite --safety arm:F2
    --planner bench:<id>                         samples/close-area-benchmark/bench.py PLANNERS[id](world)
    --planner bench:list                         print the ids, which read the world, which loaded
    --adapter world:<file.json>[:<seed>]         world_json.from_json; seed = run seed (default 0)
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
DEFAULT_BENCH_DIR = os.environ.get("BENCH_DIR", os.path.join(HERE, "..", "..", "samples", "close-area-benchmark"))
DEFAULT_RELOC_DIR = os.environ.get("RELOC_DIR", os.path.join(HERE, "..", "..", "samples", "close-area-relocalize"))
TIMEOUT_MOCK_S = 30.0
TIMEOUT_ARENA_S = 60.0              # arena run.DEFAULTS["max_time_s"]
LONG_FAMILIES = {"maze": 120.0, "warehouse": 120.0}   # close-area-benchmark bench.py LONG_FAMILIES (= playground)
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


def load_bench_planner(pid: str, bench_dir: str, world):
    """close-area-benchmark bench.PLANNERS[pid](world), loaded by path (flightloop/bench_planner.py)."""
    from flightloop import bench_planner
    try:
        pl, arm = bench_planner.make(pid, bench_dir, world)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(str(e))
    except ImportError as e:
        sys.exit(f"bench.py needs numpy and scipy ({e}): run with the arena venv python (make venv)")
    if arm:
        print(f"note: benchmark row bench:{pid} runs filter {arm} at 50 Hz; here only the planner is built. "
              f"Add --safety arm:{arm} for the filter (20 Hz, this loop)", file=sys.stderr)
    return pl


def print_bench_list(bench_dir: str) -> int:
    from flightloop import bench_planner
    try:
        rows = bench_planner.describe(bench_dir)
    except FileNotFoundError as e:
        sys.exit(str(e))
    except ImportError as e:
        sys.exit(f"bench.py needs numpy and scipy ({e}): run with the arena venv python (make venv)")
    print(f"{'id':24s} {'needs_world':11s} {'loaded':6s} {'filter':6s} sample / label")
    for r in rows:
        print(f"{r['id']:24s} {str(r['needs_world']):11s} {str(r['loaded']):6s} {r['filter'] or '-':6s} "
              f"{r['sample']} / {r['label']}{'' if r['default'] else ' [not in bench.DEFAULT_PLANNERS]'}")
    return 0


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
    if a.planner.startswith("bench:"):
        planner = load_bench_planner(a.planner.split(":", 1)[1], a.bench_dir, ad.world)
    elif a.planner.startswith("arena:"):
        planner = load_arena_planner(a.planner.split(":", 1)[1], a.arena)
    else:
        planner = PLANNERS[a.planner]()
    safety = make_safety(safety_name, a.safety_dir, world=ad.world)
    getattr(safety, "reset", lambda: None)()
    stem = os.path.splitext(os.path.basename(a.adapter))[0].replace(":", "_") + ("" if a.fault is None else f"_{a.fault}") + ("_reloc" if a.reloc else "")
    log_path = a.log or os.path.join("runs", f"{stem}.jsonl")
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    shim, odom_fh = None, None
    if a.reloc:
        from flightloop.reloc_shim import RelocShim
        odom_path = a.odom or os.path.splitext(log_path)[0] + "_odometry.jsonl"
        os.makedirs(os.path.dirname(odom_path) or ".", exist_ok=True)
        odom_fh = open(odom_path, "w", buffering=1)
        try:
            shim = RelocShim(ad, a.reloc_dir, odom=odom_fh)
        except (FileNotFoundError, ValueError) as e:
            sys.exit(str(e))
    where = (f"world file {ad.world_file} ({ad.family}, run seed {ad.seed}, index {ad.index})"
             if getattr(ad, "world_file", None) else f"close-area-arena {ad.family} seed {ad.seed} index {ad.index}")
    source = (f"flight-repo loop, {where}, "
              f"planner {a.planner}, safety {safety.name}, pose {'truth' if a.fault is None else 'estimator fault ' + a.fault}"
              f"{', relocalization close-area-relocalize multi_ig' if shim else ''}")
    timeout = LONG_FAMILIES.get(ad.family, TIMEOUT_ARENA_S) if a.timeout is None else a.timeout
    with open(log_path, "w", buffering=1) as fh:
        log = CloseAreaLog(fh, ad, planner, source=source,
                           notes="filter_intervened = safety arm changed the setpoint; loop_mode = flight-loop mode")
        r = run(ad, planner, safety, ad.goal, grid=ad.grid, log=log, timeout_s=timeout,
                realtime=a.realtime, reloc=shim)
    if odom_fh is not None:
        odom_fh.close()
    tr = ad.sim.truth()
    d_goal = math.hypot(tr.x - ad.goal[0], tr.y - ad.goal[1])
    modes = ",".join(f"{k}:{v}" for k, v in sorted(r.modes.items()))
    health = ",".join(f"{k}:{v}" for k, v in sorted(r.health.items()))
    print(f"score input=synthetic adapter={a.adapter} fault={a.fault or 'truth'} planner={a.planner} "
          f"safety={safety.name} reached={d_goal < REACHED_M and not ad.collided} final_dist_m={d_goal:.3f} "
          f"t_s={r.t_s:.2f} collided={ad.collided} min_clearance_m={ad.min_clearance:.3f} "
          f"max_pose_error_m={ad.max_pose_error:.3f} ticks={r.ticks} intervened={r.intervened_ticks} "
          f"keepalive={r.keepalive_ticks} planner_errors={r.planner_errors} outcome={r.outcome} modes={modes} health={health} log={log_path}")
    if shim is not None:
        s = shim.summary()
        print(f"reloc arm=multi_ig events={s['events']} reanchors={s['reanchors']} wrong_commits={s['wrong_commits']} "
              f"open_at_end={s['open_at_end']} moves={s['moves']} reasons={','.join(s['reasons']) or '-'} "
              f"odometry_reset_counter={s['reset_counter_out']} increments_t={s['increments_t']} "
              f"odometry_lines={shim.odom.lines} odom={odom_fh.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mock", action="store_true", help="fly the stdlib MockAdapter (= --adapter mock)")
    ap.add_argument("--adapter", default=None, help="mock, arena:<family>:<seed>[:<index>] or world:<file.json>[:<seed>]")
    ap.add_argument("--fault", choices=FAULTS, default=None,
                    help="arena only: fly on the arena estimator with this fault (default: truth pose)")
    ap.add_argument("--safety-dir", default=DEFAULT_SAFETY_DIR, help="path to samples/close-area-safety-filter")
    ap.add_argument("--scenario", choices=sorted(SCENARIOS), default="open")
    ap.add_argument("--planner", default="go_to_goal", help="go_to_goal, blind, arena:<module>, bench:<id> or bench:list")
    ap.add_argument("--bench-dir", default=DEFAULT_BENCH_DIR, help="path to samples/close-area-benchmark")
    ap.add_argument("--arena", default=DEFAULT_ARENA, help="path to samples/close-area-arena")
    ap.add_argument("--safety", default="range_stop", help="range_stop, pass_through or arm:F0|F1|F2")
    ap.add_argument("--timeout", type=float, default=None,
                    help=f"flight time limit, s (default {TIMEOUT_MOCK_S:g} mock, {TIMEOUT_ARENA_S:g} arena, 120 maze/warehouse)")
    ap.add_argument("--log", default=None, help="JSONL path (default runs/<scenario>.jsonl)")
    ap.add_argument("--realtime", action="store_true", help="pace at 20 Hz wall time")
    ap.add_argument("--reloc", action="store_true",
                    help="arena + --fault only: relocalize after VIO loss (close-area-relocalize multi_ig)")
    ap.add_argument("--reloc-dir", default=DEFAULT_RELOC_DIR, help="path to samples/close-area-relocalize")
    ap.add_argument("--odom", default=None, help="ODOMETRY-like JSONL (default <log>_odometry.jsonl)")
    a = ap.parse_args(argv)
    if a.planner == "bench:list":
        return print_bench_list(a.bench_dir)
    if a.planner not in PLANNERS and not a.planner.startswith(("arena:", "bench:")):
        ap.error(f"--planner must be one of {sorted(PLANNERS)}, arena:<module> or bench:<id>")
    if a.safety not in ("range_stop", "pass_through") and a.safety not in (f"arm:{x}" for x in ARMS):
        ap.error(f"--safety must be range_stop, pass_through or arm:<{'|'.join(ARMS)}>")
    if a.reloc and a.fault is None:
        ap.error("--reloc needs --fault (a pose estimator to relocalize)")
    if a.adapter and a.adapter.startswith(("arena:", "world:")):
        return fly_arena(a, a.safety)
    if a.fault is not None or a.reloc:
        ap.error("--fault and --reloc need --adapter arena:... or world:...")
    if a.planner.startswith("bench:"):
        ap.error("bench:<id> planners need a world: --adapter arena:... or world:<file.json>")
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
