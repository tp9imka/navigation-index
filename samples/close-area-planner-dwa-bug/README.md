# close-area-planner-dwa-bug: DWA, Bug2 and TangentBug in the shared arena, next to APF and VFH+

Goal: measure two more classic local planners for close-area A=>B where only the pose and a
range scan are available, and say which local planner to pick for a Crazyflie-like 4-beam
sensor. Everything runs in the shared [close-area-arena](../close-area-arena/README.md), is
scored there on truth, and sits next to APF (with its wall-follow escape) and VFH+ imported
unchanged from [close-area-planner-reactive](../close-area-planner-reactive/README.md).

- `dwa.py`: dynamic window approach (Fox, Burgard and Thrun 1997), the idea behind the DWB
  local controller in ROS Nav2. Holonomic form: samples (vx, vy) in the window the arena
  vehicle can reach (a_max 3 m/s^2, window 0.2 s => +/- 0.6 m/s per axis, 11 x 11 samples),
  rolls each one forward 1.5 s through the arena's velocity-lag model, rejects rollouts that
  come within 0.08 m of a return or cannot brake in time, and maximises
  `1.0 * heading to B + 0.6 * clearance + 0.2 * speed`. All constants are named at the top of
  the file. `make(memory_s=3.0)` (row `dwa_mem`) also keeps the last 3 s of returns as world
  points, like the obstacle layer of a local costmap.
- `bug.py`: Bug2 (Lumelsky and Stepanov 1987: m-line, wall follow with a fixed side, leave on
  the m-line closer than the hit point, "unreachable" exit back at the hit point) and
  TangentBug (Kamon, Rivlin and Rimon 1998: head to B if the segment is clear, else to the
  range-discontinuity tangent point minimising `|p - O| + |O - B|`, wall-follow when that
  heuristic rises, leave when a visible free point is closer to B than the followed obstacle).
  The state machines, and where they are simplified, are in the file's docstring.
- `bench.py`: the six planners x two fans x three families, 50 layouts each, seed 0.
- `tune.py`: dev-seed sweep (seed 1, 20 layouts) and a narrow-gap time-budget check.
- `arena.py`: loads the arena and the reactive sample as packages (recipe from the arena
  CONTRACT.md "Import"), defines the fans and a known-map A* length for the path ratio.

## Run

```sh
cd samples/close-area-planner-dwa-bug
uv venv .venv && uv pip install --python .venv -r requirements.txt   # numpy + scipy, from the arena
.venv/bin/python bench.py --layouts 50 --seed 0        # ~12 min, writes results/dwa_bug_0.*
.venv/bin/python tune.py                               # ~12 min, writes results/dev_seed1_tuning.md
.venv/bin/python tune.py --budget-check                # ~15 s, writes results/dev_seed1_budget.md
.venv/bin/python -m unittest test_smoke -v             # ~3 s, skips without numpy
```

Most of the bench time is DWA on the 72-beam fan (27-37 s per cell) and `dwa_mem` (128-158 s
per 72-beam cell); Bug2, TangentBug, APF and VFH+ take 3-9 s per cell
([results/bench_stdout.txt](results/bench_stdout.txt)). `--only dwa,bug2` runs a subset.

From another sample: `import arena, dwa, bug` then
`arena.run.evaluate(lambda: bug.make("tangent_bug"), "u_trap", 50, 0, cfg=arena.cfg_for("cf4"))`.
No file in the arena or the reactive sample is edited.

Fans (same as the reactive sample):

| fan | beams | FoV | range | noise | dropout |
|---|---|---|---|---|---|
| default | 72 | 360 deg | 6 m | 0.02 m | 2 % |
| cf4 | 4 (back, right, front, left; body frame) | 360 deg | 4 m | 0.02 m | 2 % |

All planners here yaw towards their commanded velocity, so the cf4 front beam faces travel.

## Results (ran 2026-11-09, Apple M3 Max, macOS 26.6.2, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

All inputs are **synthetic**: simulated layouts, vehicle and sensor. Nothing here is a flight or
SITL result.

`python bench.py --layouts 50 --seed 0`, wall 730.7 s
([results/dwa_bug_0.md](results/dwa_bug_0.md), per-run rows in `results/dwa_bug_0.json`,
console in [results/bench_stdout.txt](results/bench_stdout.txt)). 50 layouts per cell, seed 0.
"Path / A*" is the median, over reached runs, of the flown path length divided by an
8-connected A* length on the known grid inflated by 0.15 m. Two biases push it below 1: an
8-connected path is up to about 8 % longer than the true shortest path, and a run ends 0.3 m
before B. Read it as "close to the shortest path" at about 1.0, and as a detour at 1.2 and up.

| planner | fan | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | median path / A* known |
|---|---|---|---|---|---|---|---|---|---|---|
| dwa | default | random | 50 | 86.0 | 0.0 | 8.0 | 6.0 | 34.86 | 0.28 | 0.98 |
| dwa | default | u_trap | 50 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.292 | - |
| dwa | default | narrow_gap | 50 | 12.0 | 0.0 | 48.0 | 40.0 | 51.19 | 0.272 | 0.96 |
| dwa | cf4 | random | 50 | 30.0 | 52.0 | 18.0 | 0.0 | 26.16 | 0.15 | 0.98 |
| dwa | cf4 | u_trap | 50 | 0.0 | 10.0 | 90.0 | 0.0 | - | 0.196 | - |
| dwa | cf4 | narrow_gap | 50 | 0.0 | 58.0 | 22.0 | 20.0 | - | 0.15 | - |
| dwa_mem | default | random | 50 | 84.0 | 0.0 | 10.0 | 6.0 | 38.43 | 0.264 | 0.98 |
| dwa_mem | default | u_trap | 50 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.289 | - |
| dwa_mem | default | narrow_gap | 50 | 12.0 | 0.0 | 58.0 | 30.0 | 50.91 | 0.263 | 0.96 |
| dwa_mem | cf4 | random | 50 | 36.0 | 18.0 | 40.0 | 6.0 | 26.22 | 0.197 | 0.98 |
| dwa_mem | cf4 | u_trap | 50 | 0.0 | 4.0 | 94.0 | 2.0 | - | 0.225 | - |
| dwa_mem | cf4 | narrow_gap | 50 | 6.0 | 20.0 | 46.0 | 28.0 | 52.72 | 0.182 | 0.96 |
| bug2 | default | random | 50 | 92.0 | 0.0 | 0.0 | 8.0 | 30.16 | 0.498 | 1.02 |
| bug2 | default | u_trap | 50 | 94.0 | 0.0 | 2.0 | 4.0 | 44.44 | 0.476 | 1.29 |
| bug2 | default | narrow_gap | 50 | 0.0 | 0.0 | 0.0 | 100.0 | - | 0.483 | - |
| bug2 | cf4 | random | 50 | 74.0 | 20.0 | 4.0 | 2.0 | 28.62 | 0.297 | 1.0 |
| bug2 | cf4 | u_trap | 50 | 0.0 | 74.0 | 0.0 | 26.0 | - | 0.147 | - |
| bug2 | cf4 | narrow_gap | 50 | 0.0 | 8.0 | 2.0 | 90.0 | - | 0.275 | - |
| tangent_bug | default | random | 50 | 92.0 | 0.0 | 8.0 | 0.0 | 24.66 | 0.418 | 0.97 |
| tangent_bug | default | u_trap | 50 | 86.0 | 0.0 | 14.0 | 0.0 | 31.06 | 0.422 | 1.04 |
| tangent_bug | default | narrow_gap | 50 | 58.0 | 0.0 | 32.0 | 10.0 | 28.0 | 0.318 | 0.95 |
| tangent_bug | cf4 | random | 50 | 38.0 | 62.0 | 0.0 | 0.0 | 24.42 | 0.149 | 0.98 |
| tangent_bug | cf4 | u_trap | 50 | 30.0 | 46.0 | 0.0 | 24.0 | 31.66 | 0.182 | 1.06 |
| tangent_bug | cf4 | narrow_gap | 50 | 4.0 | 96.0 | 0.0 | 0.0 | 26.61 | 0.149 | 0.97 |
| apf | default | random | 50 | 98.0 | 0.0 | 2.0 | 0.0 | 26.0 | 0.774 | 0.99 |
| apf | default | u_trap | 50 | 92.0 | 0.0 | 6.0 | 2.0 | 43.78 | 0.65 | 1.24 |
| apf | default | narrow_gap | 50 | 0.0 | 0.0 | 94.0 | 6.0 | - | 0.646 | - |
| apf | cf4 | random | 50 | 82.0 | 8.0 | 10.0 | 0.0 | 26.58 | 0.474 | 1.01 |
| apf | cf4 | u_trap | 50 | 2.0 | 54.0 | 24.0 | 20.0 | 38.96 | 0.15 | 1.07 |
| apf | cf4 | narrow_gap | 50 | 6.0 | 34.0 | 28.0 | 32.0 | 40.56 | 0.301 | 1.08 |
| vfh_plus | default | random | 50 | 96.0 | 0.0 | 4.0 | 0.0 | 25.68 | 0.278 | 0.98 |
| vfh_plus | default | u_trap | 50 | 0.0 | 0.0 | 94.0 | 6.0 | - | 0.956 | - |
| vfh_plus | default | narrow_gap | 50 | 62.0 | 0.0 | 38.0 | 0.0 | 27.56 | 0.274 | 0.98 |
| vfh_plus | cf4 | random | 50 | 28.0 | 72.0 | 0.0 | 0.0 | 24.62 | 0.148 | 0.99 |
| vfh_plus | cf4 | u_trap | 50 | 0.0 | 98.0 | 2.0 | 0.0 | - | 0.146 | - |
| vfh_plus | cf4 | narrow_gap | 50 | 4.0 | 96.0 | 0.0 | 0.0 | 29.13 | 0.148 | 1.0 |

The APF and VFH+ rows match the reactive sample's published table cell for cell
([reactive_0.md](../close-area-planner-reactive/results/reactive_0.md), numpy 2.4.6 there), so
the import path changes nothing. References from the arena on the same 50 layouts per family:
the known-map `astar_esdf` reached 100 % on u_trap
([astar_esdf_u_trap_0.md](../close-area-arena/results/astar_esdf_u_trap_0.md)); the straight
baseline reached 40 % random and 0 % u_trap / narrow_gap on its 20-layout set
([straight_random_0.md](../close-area-arena/results/straight_random_0.md)).

Counters in `results/dwa_bug_0.json` (per cell): DWA found no admissible sample at least once
in 50 of 50 cf4 u_trap runs and 47 of 50 cf4 narrow_gap runs (7 and 19 with 72 beams). Bug2 took
its "unreachable" exit in 1 of 150 runs with 72 beams (u_trap) and in none with cf4.

### Reading

- **72 beams, which planner gets out of a U trap.** The two Bug planners and APF with its
  escape do; DWA and VFH+ do not. Bug2 94 %, APF 92 %, TangentBug 86 %; DWA 0 % (100 % stuck)
  and VFH+ 0 %. DWA with only a heading-to-B term is a local method and settles in the cup's
  inside corner ([plot](results/dwa_default_u_trap_0_run0.png)); Nav2 runs it under a global
  planner for that reason. TangentBug pays less for the escape than Bug2: median 31.06 s and a
  path 1.04 x A*, against Bug2's 44.44 s and 1.29 x.
- **72 beams, narrow gap (0.5-0.9 m).** TangentBug 58 % and VFH+ 62 % are the only planners
  above 12 %. Bug2 reaches 0 %, all 50 runs time out. On the dev seed with a 180 s budget,
  Bug2 still reached 0 of 20 and all 20 ended with its "back at the hit point" exit
  ([results/dev_seed1_budget.md](results/dev_seed1_budget.md)): the wall follower holds
  0.45 m clearance, too far out to turn into the gap, so it walks the whole room boundary and
  passes the gap by. Bug2's completeness assumes a follower that traces the boundary itself.
  DWA gets 12 %: going sideways to a gap scores low on the heading term.
- **4 beams (cf4): which local planner to pick.** None is good; APF with its escape is the
  least bad. On random clutter APF reached 82 % with 8 % collisions; next are Bug2 (74 %,
  20 % collisions), TangentBug (38 %, 62 %), `dwa_mem` (36 %, 18 %), DWA (30 %, 52 %) and
  VFH+ (28 %, 72 %). In the U trap only TangentBug gets out at all (30 %, with 46 %
  collisions); APF reaches 2 % and the rest 0 %. Through the narrow gap every planner is at
  6 % or below. A median min clearance at or near the 0.15 m radius means about half or more
  of that cell's runs touched an obstacle. In the plotted Bug2 cf4 u_trap run, the vehicle
  follows the cup's top wall and runs into the lip end, which lies between beams
  ([plot](results/bug2_cf4_u_trap_0_run0.png)).
- **Memory helps the sparse fan more than the planner choice.** The same DWA with 3 s of
  remembered returns cut cf4 collisions from 52 % to 18 % on random, 10 % to 4 % on u_trap and
  58 % to 20 % on narrow_gap, without raising reached much (30 % => 36 % on random). With 72
  beams memory changed little (86 % => 84 % random). The pose here is truth, so this memory has
  no odometry drift; on a Crazyflie the Flow-deck drift would eat into it
  ([08 Crazyflie sensing limits](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md)).
- **What to do on a Crazyflie-like 4-beam drone.** Use APF with the wall-follow escape from the
  reactive sample as the local layer, add a short scan memory (the DWA result says it removes
  about two thirds of the collisions; it was not tried on APF), and do not count on any local
  planner for U traps or narrow gaps. If whoever set the task gives you the map, the known-map A* in the
  arena reached 100 % on u_trap. With 72 beams and no map, TangentBug is the best all-round
  pick here: 92 % random, 86 % u_trap, 58 % narrow_gap, 0 % collisions.

Dev-seed sweep (seed 1, 20 layouts per cell,
[results/dev_seed1_tuning.md](results/dev_seed1_tuning.md)): no DWA setting tried
(W_CLEAR 0.3 or 1.0, HORIZON_S 1.0 or 2.5, SAFETY_M 0.04, memory 3 or 6 s) moved u_trap above
0 % or cf4 random above 30 %. Reached changed by at most 2 layouts of 20 in any cell, and
SAFETY_M 0.04 raised cf4 narrow_gap collisions from 50 % to 100 %, so the defaults were kept. TangentBug without the dropout hold reached 55 % u_trap against 90 % with
it. V_WF 0.9 and D_DES 0.35 gave Bug2 the same 95 % u_trap as the default; they were not
adopted.

### Plots (u_trap, seed 0, run 0; blue = truth path, orange = stuck, magenta = collision, purple = timeout)

| planner | default fan | cf4 fan |
|---|---|---|
| dwa | [stuck in cup](results/dwa_default_u_trap_0_run0.png) | [stuck](results/dwa_cf4_u_trap_0_run0.png) |
| dwa_mem | [stuck](results/dwa_mem_default_u_trap_0_run0.png) | [stuck](results/dwa_mem_cf4_u_trap_0_run0.png) |
| bug2 | [reached](results/bug2_default_u_trap_0_run0.png) | [collision at the lip](results/bug2_cf4_u_trap_0_run0.png) |
| tangent_bug | [reached](results/tangent_bug_default_u_trap_0_run0.png) | [timeout](results/tangent_bug_cf4_u_trap_0_run0.png) |
| apf | [reached](results/apf_default_u_trap_0_run0.png) | [collision](results/apf_cf4_u_trap_0_run0.png) |
| vfh_plus | [stuck](results/vfh_plus_default_u_trap_0_run0.png) | [collision](results/vfh_plus_cf4_u_trap_0_run0.png) |

Determinism: a second run of `bench.py --layouts 50 --seed 0 --only dwa,bug2,tangent_bug
--no-write` printed the same table rows for all 18 DWA, Bug2 and TangentBug cells
([results/rerun_stdout.txt](results/rerun_stdout.txt)); `dwa_mem` was not re-run. `test_smoke.py` re-runs u_trap run 0
for DWA, Bug2 and TangentBug on both fans and checks outcome and path length against
`results/dwa_bug_0.json`.

## Limits

- Everything inherits the arena limits: 2.5D, point-mass vehicle with a velocity lag, ideal ray
  casts with Gaussian noise and dropout, axis-aligned boxes and cylinders, no dynamic obstacles,
  60 s budget.
- cf4 is a geometry model of the Multi-ranger (no beam cone, arena noise and dropout), as in the
  reactive sample. Its collision rates are for this geometry, not a Crazyflie prediction.
- DWA is the holonomic textbook form, not Nav2's DWB plugin: no global path, no path-align or
  path-distance critics, no costmap inflation layer, no oscillation critic. In Nav2 it would
  follow a global plan, which removes the U-trap failure measured here.
- Bug2 and TangentBug are simplified (see the `bug.py` docstring): TangentBug's d_reach counts
  free-space points only, its d_followed is seeded from the returns blocking the way to B, and
  a one-scan dropout hold filters the arena's dropout. Bug2 uses a fixed side; choosing the
  side per hit was not tried.
- `dwa_mem` uses the truth pose for its memory. Memory was not added to APF, VFH+ or the Bug
  planners.
- Parameters were set by hand and checked on seed 1 with 20 layouts; other settings may do
  better. The path ratio has the biases listed above the table.

## Sources

- [peer] Fox, Burgard and Thrun, The dynamic window approach to collision avoidance, IEEE
  Robotics and Automation Magazine 4(1), 1997, doi 10.1109/100.580977. Not re-read: window,
  admissible-velocity rule and the heading + clearance + velocity objective follow the common
  description; weights here are our own.
- [docs] ROS 2 Nav2, DWB controller (`dwb_core`, critics such as GoalAlign, PathAlign,
  BaseObstacle), docs.nav2.org. Not re-read for this sample; named only to place DWA.
- [peer] Lumelsky and Stepanov, Path-planning strategies for a point mobile automaton moving
  amidst unknown obstacles of arbitrary shape, Algorithmica 2, 1987, doi 10.1007/BF01840369
  (Bug1 / Bug2). Not re-read.
- [peer] Kamon, Rivlin and Rimon, TangentBug: a range-sensor-based navigation algorithm, IJRR
  17(9), 1998, doi 10.1177/027836499801700903. Not re-read; the d_followed / d_reach leave rule
  is from the common description.
- Hub: [close-area-planner-reactive](../close-area-planner-reactive/README.md) (APF, VFH+, cf4
  fan), [close-area-arena CONTRACT](../close-area-arena/CONTRACT.md),
  [01 planning and mapping](../../docs/research/close-area-nav/01-planning-and-mapping.md)
  (local replanners, failure modes),
  [08 Crazyflie sensing limits](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md).
