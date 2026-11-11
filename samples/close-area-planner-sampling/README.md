# close-area-planner-sampling: RRT* and Informed RRT* against A* in the close-area arena

Goal: show with numbers why A* on the inflated grid is the default global planner for a small
close-area A=>B flight. RRT* and Informed RRT* (own numpy implementation) plan on the same
known inflated 0.1 m grid as the A* baseline
([planners/astar_esdf.py](../close-area-arena/planners/astar_esdf.py)) and fly with the same
carrot follower, in the shared [close-area-arena](../close-area-arena/README.md). The test
family is narrow_gap, the case where sampling planners are known to struggle
([01-planning-and-mapping.md](../../docs/research/close-area-nav/01-planning-and-mapping.md)
section 2: "narrow passages are its classic weakness").

- `rrt_star.py`: RRT* with rewiring and subtree cost update; `informed=True` samples the
  ellipse with foci A and B once a solution exists (Gammell et al. 2014). Goal bias 5 %, step
  1.0 m, rewire radius from the RRT* bound capped at 2.0 m. Same two-level inflation as A*
  (ESDF > 0.25 m, then 0.15 m if no path), then the A* baseline's own `shortcut`. The flying
  planner `RRTStarPlanner` subclasses `AStarESDF`, so the carrot, the speed-by-clearance law
  and the yaw law are the baseline's code. It plans once and replans only when the vehicle is
  more than 0.6 m off the path.
- `arena.py`: loads the arena as package `close_area_arena` (CONTRACT.md recipe) and builds
  narrow_gap layouts with a fixed gap width (`gap_world`). It draws the arena's random numbers
  in the same order and only replaces the gap width, so `gap_world(None, 0, i)` equals the
  arena layout (checked for indices 0-49) and widths of one index share wall, gap centre and
  clutter. No arena file is edited.
- `sweep.py`: planning only (no flight), gap widths 0.4-1.2 m. `bench.py`: flights in the
  arena. `clearance.py`: exact clearance of the swept paths.

## Run

```sh
cd samples/close-area-planner-sampling
uv venv --python 3.12 .venv && uv pip install --python .venv -r requirements.txt   # numpy + scipy, from the arena
.venv/bin/python sweep.py --layouts 30 --seeds 10        # ~3.5 min on 14 processes, results/sweep_0.*
.venv/bin/python bench.py --layouts 50 --seed 0          # ~1 min 50 s, results/arena_*_0.*
python3 clearance.py                                     # stdlib, results/sweep_0_clearance.md
.venv/bin/python -m unittest test_smoke -v               # skips without numpy
```

From another sample: `import arena, rrt_star` then
`arena.run.evaluate(lambda: rrt_star.make(iters=5000, informed=True), "narrow_gap", 50, 0)`.

## Results (ran 2026-11-09, Apple M3 Max, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

All inputs are **synthetic**: simulated layouts, vehicle and sensor. Nothing here is SITL or a
flight.

### Sweep: success vs gap width (planning only)

`python sweep.py --layouts 30 --seeds 10`, wall 173.7 s on 14 processes
([results/sweep_0.md](results/sweep_0.md), 8610 plans in `results/sweep_0.json`). Per gap
width: arena narrow_gap layouts 0-29 of seed 0 with the gap set to that width. A* plans once
per layout (deterministic); each RRT* setting plans 10 times per layout with RNG seeds 0-9,
so 300 plans per cell. Success = a path within the budget at either inflation level.
Budget = samples drawn per inflation level.

Success %:

| gap m | A* | RRT* 1000 | RRT* 5000 | Informed RRT* 1000 | Informed RRT* 5000 |
|---|---|---|---|---|---|
| 0.4 | 100.0 | 28.3 | 85.7 | 28.3 | 85.7 |
| 0.5 | 100.0 | 60.3 | 99.3 | 60.3 | 99.3 |
| 0.6 | 100.0 | 82.7 | 100.0 | 82.7 | 100.0 |
| 0.7 | 100.0 | 92.0 | 100.0 | 92.0 | 100.0 |
| 0.8 | 100.0 | 98.0 | 100.0 | 98.0 | 100.0 |
| 1.0 | 100.0 | 99.3 | 100.0 | 99.3 | 100.0 |
| 1.2 | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |

Informed and plain RRT* have the same success by construction: the two share the RNG stream
and differ only after the first solution.

Planning time (ms, median / p95) and path length (successful plans; std is over the 10 RNG
seeds of a layout, averaged over layouts; "/ A*" is the mean ratio to the A* path of the same
layout):

| gap m | A* ms | RRT* 5000 ms | Informed 5000 ms | A* length m | Informed 5000 length m | Informed 5000 std m | Informed 5000 / A* | RRT* 1000 std m |
|---|---|---|---|---|---|---|---|---|
| 0.4 | 76.2 / 95.8 | 612.5 / 737.4 | 652.1 / 784.0 | 25.51 | 25.09 | 0.069 | 0.984 | 0.314 |
| 0.6 | 34.9 / 55.0 | 320.6 / 624.0 | 396.6 / 723.5 | 25.58 | 25.1 | 0.088 | 0.981 | 0.26 |
| 0.8 | 33.6 / 56.1 | 320.9 / 397.9 | 416.2 / 578.0 | 25.6 | 24.97 | 0.027 | 0.976 | 0.347 |
| 1.2 | 30.0 / 43.4 | 309.7 / 352.3 | 436.7 / 643.3 | 25.58 | 24.88 | 0.013 | 0.973 | 0.261 |

All 7 widths and the 1000-budget columns are in [results/sweep_0.md](results/sweep_0.md).
The sweep ran 14 processes at once, so its ms are inflated by load. A single-process rerun
on 5 layouts x 3 seeds at 0.4, 0.8 and 1.2 m
([results/timing_jobs1/sweep_0.md](results/timing_jobs1/sweep_0.md), wall 39.6 s) gave
A* 68.7 / 29.7 / 25.8 ms median and Informed RRT* 5000 509.6 / 302.3 / 345.3 ms median.
A* ms include its own distance transform and cost map; RRT* ms do not (the sweep passes the
ESDF in), which favours RRT*.

Exact clearance of the planned paths (world.sdf every 2 cm,
[results/sweep_0_clearance.md](results/sweep_0_clearance.md)): every path planned at the
0.25 m level keeps at least 0.211 m. At the 0.15 m fallback level, paths dip below the 0.15 m
vehicle radius: A* 17 of 60 (min 0.119 m), RRT* 5000 57 of 588, Informed RRT* 5000 35 of 588
(min 0.113 m). The cause is the grid, not the planner: a cell is free when its centre is
0.15 m from an occupied cell centre, and the obstacle surface can sit up to half a cell
inside an occupied cell.

### Arena flights (best setting: Informed RRT*, 5000 samples)

`python bench.py --layouts 50 --seed 0 --iters 5000 --informed 1`, 1 min 46 s total
([results/arena_random_0.md](results/arena_random_0.md),
[results/arena_narrow_gap_0.md](results/arena_narrow_gap_0.md), console in
`results/bench_stdout.txt`). A* was rerun in the same command; its summary scores equal the arena's
[results/astar_esdf_random_0.md](../close-area-arena/results/astar_esdf_random_0.md) and
[results/astar_esdf_narrow_gap_0.md](../close-area-arena/results/astar_esdf_narrow_gap_0.md).
Arena narrow_gap gaps are 0.5-0.9 m.

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | replans | plan median ms | plan p95 ms | fallback replans | no-path replans | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_esdf known_map | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 18.81 | 0.635 | 2379 | 1.26 | 10.98 | 0 | 0 | 11.8 |
| informed_rrt_star iters=5000 | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 23.58 | 0.269 | 50 | 466.94 | 612.76 | 0 | 0 | 29.4 |
| astar_esdf known_map | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 24.23 | 0.276 | 3115 | 3.91 | 40.31 | 272 | 0 | 38.8 |
| informed_rrt_star iters=5000 | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 27.56 | 0.251 | 50 | 330.27 | 615.54 | 12 | 0 | 24.2 |

A* replans at 2.5 Hz on a cached ESDF (hence 1-4 ms medians); Informed RRT* planned once per
run and never needed a replan, and 12 of its 50 narrow_gap plans used the 0.15 m fallback. A second run of the command gave identical outcomes, path
lengths and clearances in all 4 cells. Baseline for scale (arena, 20 layouts): straight
reached 40 % random, 0 % narrow_gap
([straight_random_0.md](../close-area-arena/results/straight_random_0.md)).

### Reading: when is sampling worth it here?

- **Not in this arena.** A* is complete on the grid: 100 % at every width from 0.4 to 1.2 m,
  one deterministic path per layout, 30-76 ms median including its distance transform.
  RRT* with 1000 samples drops to 28.3 % at 0.4 m and 60.3 % at 0.5 m; 5000 samples brings it
  to 85.7 % and 99.3 % at 8-10x the A* time.
- **A failed sampling plan cannot tell "no path" from "not found yet".** When the 0.25 m
  level is closed (0.4 and 0.5 m gaps), A* finds that fast and falls back; RRT* burns its whole
  budget first. Worse, a budget miss at an open 0.25 m level also drops to the tighter 0.15 m
  level: RRT* 1000 used the fallback in 7.3 % of its 1.2 m plans, where A* used it in 0 %.
- **Shorter, but closer to walls.** Informed RRT* 5000 paths are 1.6-2.7 % shorter than A*
  (ratio 0.973-0.984), because the A* baseline pays a clearance cost and RRT* minimises length
  only. In flight this cost time: median time to goal 23.58 s against 18.81 s on random, with
  median min clearance 0.269 m against 0.635 m. Our reading (not isolated by an experiment):
  the follower slows near walls, and the RRT* path stays near walls longer.
- **Informed mode helps only after the first solution.** It does not change success; it
  shrinks the run-to-run length spread (0.013-0.088 m std against 0.21-0.35 m for RRT* 1000)
  and costs 6-41 % more median time per plan than plain RRT* at 5000 samples.
- **Where sampling would pay** (from the literature and lane 01, not measured here): large or
  fine 3D volumes where a grid gets too big, kinodynamic or higher-dimensional state, or a
  continuous map without a grid. For a 20 x 20 m 2.5D area at 0.1 m (40 000 cells), the grid
  is cheap. If you fly a sampling planner for real, give it a budget big enough for the
  narrowest gap and check its result, rather than trusting a silent fallback.

## Limits

- 2.5D, known static map, point-mass vehicle with a velocity lag; inherits all arena limits.
  The unknown-map case (astar_esdf known_map=False) was not tried with RRT*.
- Edge checks sample every half cell on the grid, the same approximation as the A* shortcut;
  a diagonal edge can clip a cell corner. The exact-geometry check above is how this was
  measured.
- One step size (1.0 m), goal bias (5 %) and rewire cap (2.0 m); not tuned. Two budgets
  (1000, 5000). No RRT-Connect, BIT* or narrow-passage samplers (bridge test, Gaussian), which
  target exactly this case.
- Planning times are wall time on one machine; the sweep times were taken under 14-process load.
- A* constants were tuned on arena layouts that are part of the seed 0 set (arena README);
  RRT* settings were picked before the sweep and not tuned.

## Sources

- [peer] Karaman and Frazzoli, Sampling-based algorithms for optimal motion planning, IJRR 2011
  (hub record `res:karaman-frazzoli-rrtstar-ijrr-2011`, arXiv 1105.1186). Not re-read; the
  RRT* rewire radius bound follows the paper's form for d = 2.
- [peer] Gammell, Srinivasa and Barfoot, Informed RRT*: optimal sampling-based path planning
  focused via direct sampling of an admissible ellipsoidal heuristic, IROS 2014 (no hub record;
  proposed in INTEGRATION.md). Not re-read; the ellipse sampling is the textbook form.
- [code] zhm-real/PathPlanning (`repo:zhm-real/pathplanning`) and OMPL (`repo:ompl/ompl`) are
  the reference implementations named in lane 01; neither was used or run here.
- Hub docs: [close-area-nav README](../../docs/research/close-area-nav/README.md),
  [01 planning and mapping](../../docs/research/close-area-nav/01-planning-and-mapping.md)
  section 2, [arena CONTRACT](../close-area-arena/CONTRACT.md).
