# close-area-arena contract

What later jobs (planners, estimators with faults, safety filters) code against. Changing a
field name here breaks every sample that imports the arena, and breaks the port to
`templates/drone-adapter`. Add fields with defaults; do not rename or remove.

## Frames and units

- Local ENU, metres, seconds, radians. Origin at point A. Yaw CCW from +x.
- 2.5D: obstacles are vertical prisms; the vehicle holds z = 1.0 m and ignores `vz`.
- Area: 20 x 20 m with walls on all four sides. B is near the opposite corner from A.
- Range scans are in the body frame: angle 0 = forward (along yaw), CCW positive.

## Adapter (adapter.py)

`Pose`, `RangeScan`, `Setpoint` and `Adapter` are copied verbatim from the published interface.

| Call | Sim behaviour |
|---|---|
| `pose() -> Pose` | Truth with `quality=100`, `sigma_xy=0.0`, unless a `pose_source` is set |
| `ranges() -> RangeScan` | Ray cast from the **true** pose: 72 beams, 360 deg, 6 m, noise 0.02 m, dropout 2 % (defaults in `run.DEFAULTS`) |
| `send_setpoint(sp)` | Velocity held until the next call. Older than 0.5 s => zero velocity |
| `tick(n=1)` (sim only) | Advance n physics steps of 1/50 s |
| `truth() -> Pose` (sim only) | Truth, for scoring and logging. Planners must not call it |

Vehicle (vehicle.py): 50 Hz double integrator, first-order velocity lag tau = 0.15 s,
|a| <= 3 m/s^2, |v| <= 2 m/s, |yaw rate| <= 2 rad/s, radius 0.15 m.

## pose_source hook

```python
PoseSource = Callable[[Pose], Pose]     # receives truth, returns what the planner sees
SimAdapter(world, vehicle, sensor, pose_source=my_estimator)
run.evaluate(make_planner, family, layouts, seed, make_pose_source=lambda world, seed, index: my_estimator)
```

- Called once per `pose()` call, which `run.py` makes once per planner step (10 Hz default).
  Use `truth.t` for elapsed time. Keep state in the callable (a class with `__call__`).
- Build a fresh one per layout in `make_pose_source` so faults are seeded per run:
  `np.random.default_rng([seed, index, <your constant>])`.
- To model a fault, return a shifted or drifting pose; set `quality`, `reset_counter` and
  `sigma_xy` as your estimator would report them (overconfident is allowed and expected).
- The scorer never sees the output. `max_pose_error_m` in each run row is the largest
  horizontal |reported - truth| seen at planner steps.

### Reference pose source (estimator.py)

Use this before writing your own. `estimator.make_pose_source_factory(fault_name="none",
dark=True, sink=None)` returns a `make_pose_source(world, seed, index)` for `run.evaluate`.
Each call builds a `VioEstimator`: a position/velocity EKF fed by a 30 Hz VIO-like source and
a 50 Hz IMU-like accel, with 2 seeded dark zones per layout when `dark=True`. It sets
`quality`, `reset_counter` and `sigma_xy`.

```python
estimator = importlib.import_module("close_area_arena.estimator")   # see Import
sink = []
mps = estimator.make_pose_source_factory("bias", dark=True, sink=sink)
rows, summary, _ = arena_run.evaluate(lambda: MyPlanner(), "random", 50, 0, make_pose_source=mps)
# sink holds one VioEstimator per layout, for its logs after the run
```

- `fault_name` is one of `faults.CASES`: `none`, `jump`, `bias`, `dropout`, `overconfident`.
- Seeds: dark zones `[seed, index, 4001]`, estimator noise `[seed, index, 4101]`. Use another
  constant for your own source.
- `run_faults.py --planner <name>` runs every case plus `truth` and `none_nodark` and writes
  `results/faults_<planner>_*`. Results: README "Estimator and faults".

## Planner (planners/base.py)

```python
class Planner:
    name = "base"
    uses_grid = False                 # True => grid is the prior 0.1 m OccGrid, else None
    def reset(self) -> None: ...      # once before each run
    def step(self, pose, scan, goal, grid_or_None, dt) -> Setpoint: ...
```

- `goal` is `(x, y, z)` of B in the local frame. `dt` is the planner period (0.1 s default).
- Read only the arguments. Do not import the world or the vehicle.
- `OccGrid`: `occ[ix, iy]` bool, `res` 0.1 m, `x0, y0` corner of cell (0, 0), `to_index(x, y)`,
  `to_xy(ix, iy)` (cell centre), `inflated(radius)`, `esdf()` (metres). Outside the grid is
  occupied.

## Scorer fields (scorer.py, always on truth)

| Field | Definition |
|---|---|
| `outcome` | First event in time: `reached`, `collision`, `stuck` or `timeout` (run ends there) |
| `reached` | Truth within 0.3 m of B |
| `collision` | Truth clearance < radius (0.15 m) |
| `stuck` | `\|p(t) - p(t - 10 s)\| < 0.2 m` at some t >= 10 s |
| `timeout` | None of the above in 60 s |
| `time_to_goal_s` | Time of reaching B, `null` otherwise |
| `min_clearance_m` | Minimum distance from the vehicle centre to the nearest surface (obstacle or wall) |
| `path_length_m` | Truth path length up to the end of the run |
| `duration_s` | Time of the end event |

Extra per-run fields from `run.py`: `index`, `layout_attempts`, `n_obstacles`, `goal`,
`max_pose_error_m`, `planner_ms_mean`, `planner_ms_max` (timings vary with load, so they are
excluded from determinism checks). `scorer.summarize(rows)` gives the percentages and medians.

## Determinism

Layout `(family, seed, index)` uses `np.random.default_rng([seed, index, family_code])`; sensor
noise uses `[seed, index, 7]`. Same command => same scores on the same numpy version.

## Add a planner

1. Write `planners/<name>.py` with a `Planner` subclass and `def make(**kw) -> Planner`.
2. Run `.venv/bin/python run.py --planner <name> --layouts 20 --seed 0 --family u_trap`.
3. Or, from another sample, pass your own factory to `run.evaluate` (see Import).

Example (15 lines of planner): steer to the beam nearest the goal direction that has 1 m of
room, plus a push away from returns closer than 0.6 m (a beam only checks the centre line, so
without the push it grazes walls it slides along).

```python
import math
from planners.base import Planner
from adapter import Setpoint

class FreestBeam(Planner):
    name = "freest_beam"
    def step(self, pose, scan, goal, grid, dt):
        ex, ey = goal[0] - pose.x, goal[1] - pose.y
        hg = math.atan2(ey, ex)
        wrap = lambda a: (a + math.pi) % (2 * math.pi) - math.pi
        ok = [pose.yaw + a for a, d in zip(scan.angles, scan.distances) if d > 1.0]
        h = min(ok, key=lambda a: abs(wrap(a - hg)), default=hg + math.pi)
        v = min(1.0, math.hypot(ex, ey))
        vx, vy = v * math.cos(h), v * math.sin(h)
        for a, d in zip(scan.angles, scan.distances):
            if d < 0.6:
                vx -= 2 * (0.6 - d) * math.cos(pose.yaw + a); vy -= 2 * (0.6 - d) * math.sin(pose.yaw + a)
        return Setpoint(vx, vy, 0.0, 1.5 * wrap(hg - pose.yaw))

def make(**kw): return FreestBeam()
```

This block was executed against `run.evaluate` on all three families (seed 0, 20 layouts).
Those runs were not saved to results/, so they are not quoted. The same code now ships as
`FreestBeam` in `run_faults.py`. There it reached 86 % on 50 random layouts with the truth pose
([results/faults_freest_beam_summary_0.md](results/faults_freest_beam_summary_0.md), synthetic).
Being reactive, it does not get out of the u_trap or find the narrow gap. Run it with
`run_faults.py --planner freest_beam`. `run.py --planner` only loads `planners/<name>.py`.

## Reference grid planner (planners/astar_esdf.py)

`astar_esdf` is the map-based baseline that safety filters sit on. It runs A* on a grid
inflated by radius + 0.10 m, with an ESDF clearance cost, shortcutting and a carrot follower,
and replans at 2-5 Hz.

| Call | Gives |
|---|---|
| `make(known_map=True)` | Plans on the prior 0.1 m `OccGrid` (`uses_grid = True`, name `astar_esdf_known`). Upper bound |
| `make(known_map=False)` | Builds its own log-odds grid from `RangeScan` hits only. Unknown cells are passable at a cost (`uses_grid = False`, name `astar_esdf_unknown`) |
| `run.py --planner astar_esdf` | Known-map variant, through the normal CLI |
| `python -m planners.astar_esdf --layouts 50 --seed 0` | straight vs known vs unknown on all three families, writes `results/astar_esdf_<family>_<seed>.*` |

To wrap it (for example a safety filter), call its `step()` and modify the returned
`Setpoint`. The planner-level tuning constants are module globals at the top of the file.
Results: README "A* + ESDF grid planner".

## Flight log format (log_format.md)

Every flight log, from the arena, SITL or a real drone, uses
[log_format.md](log_format.md) (`close-area-log/1`, JSONL: one header line, then one line per
`send_setpoint()` call, local ENU frame with origin at A). The header `input` field is `real`,
`sitl` or `synthetic`, and every score prints it. Score any log with `score_log.py` (numpy +
matplotlib, no arena import), so sim and real flights give the same fields. Do not invent a
second log format. Add optional fields with defaults, as for the adapter.

## Import from a sibling sample

Load the folder as package `close_area_arena`, so its `run.py` / `world.py` never shadow yours
(the same reason samples/blind-flight-bench/ext.py loads files by path):

```python
import importlib, importlib.util, os, sys
ARENA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "close-area-arena")
spec = importlib.util.spec_from_file_location(
    "close_area_arena", os.path.join(ARENA, "__init__.py"), submodule_search_locations=[ARENA])
pkg = importlib.util.module_from_spec(spec); sys.modules["close_area_arena"] = pkg
spec.loader.exec_module(pkg)
arena_run = importlib.import_module("close_area_arena.run")
Pose = importlib.import_module("close_area_arena.adapter").Pose
rows, summary, _ = arena_run.evaluate(lambda: MyPlanner(), "u_trap", 20, 0)
```

Inside the arena, every sibling import is written `try: from .x import ... except ImportError:
from x import ...`, so the same files work as scripts and as a package. `test_smoke.py` loads
the arena this way.
