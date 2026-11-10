# close-area-planner-thetastar: Theta* and Lazy Theta* (any-angle A*) against A* + shortcut

Use this when you want to know whether an any-angle grid search beats the arena's default
global path (8-connected A* on the inflated grid, then a line-of-sight shortcut) for a close-area
A=>B flight, and what it costs per replan.

Theta* (Daniel, Nash, Koenig, Felner 2010) and Lazy Theta* (Nash, Koenig, Tovey 2010) run on the
same inflated 0.1 m grid and the same ESDF clearance cost as
[astar_esdf](../close-area-arena/planners/astar_esdf.py), and fly with its follower. Only the
global path differs. All inputs are **synthetic** (simulated layouts, vehicle and range sensor);
nothing here is SITL or a flight.

- `thetastar.py`: `theta_star(blocked, cost, start, goal, lazy=False)` and the flying planner
  `ThetaStarESDF`, a subclass of `AStarESDF`. When v is generated from u, the search also tries
  the straight edge parent(u) => v. That edge is priced by the A* cost rule integrated along the
  segment (sampled every half cell, length x mean cell cost) and must not touch a blocked cell.
  The cheaper edge wins, so the clearance cost still pushes the path off walls. Lazy Theta*
  trusts that edge with an estimated cost and checks it once, when v is expanded. There is no
  post-hoc shortcut: the Theta* vertices are the path. Same two inflation levels (0.25 m, then
  0.15 m), same replan schedule, same log-odds map on the unknown map.
- An exact speed-up: inside regions of one cost value (free and far from walls = 1.0; unknown
  and far from walls = 2.0), a segment covered by the uniform discs of its two ends is priced
  without walking it. On 80 searches (5 families x 4 layouts x 2 cost maps x 2 variants) it
  returned the same paths and costs as the plain walk.
- `make()` = Theta* on the known map (same default as `astar_esdf.make()`). `make(lazy=True)` =
  Lazy Theta*. `make(known_map=False, bounds=(xmin, ymin, xmax, ymax))` = unknown map with the
  log-odds map corner on the area bounds - 2 m, the geofence close-area-benchmark gives
  `astar_unknown`. numpy + scipy only, so it can run in Pyodide (not tried there).
- `bench.py`: `flights` reuses close-area-benchmark's `run_one` (layouts, presets, time limits,
  scorer) by adding rows to its `PLANNERS` at import time. Nothing in that sample is edited.
  `plans` is planning only, one process. `check` compares the A* rows with the benchmark matrix.

## Run

```sh
cd samples/close-area-planner-thetastar
uv venv --python 3.12 .venv && uv pip install --python .venv -r requirements.txt   # numpy + scipy, from the arena
.venv/bin/python bench.py flights --layouts 20 --seed 0 --workers 14   # 13 min, results/flights_0.*
.venv/bin/python bench.py plans --layouts 20 --seed 0 --repeats 3      # 2 min, results/plans_0.*
.venv/bin/python bench.py flights --layouts 1 --seed 0 --workers 1 --no-crazyflie \
    --planners astar_unknown,thetastar_unknown,lazy_thetastar_unknown --stem timing_unknown_jobs1   # 5 min
.venv/bin/python bench.py check                                        # A* rows vs close-area-benchmark
.venv/bin/python -m unittest test_smoke -v                             # skips without numpy
```

From another sample: `import arena, thetastar` then
`arena.run.evaluate(lambda: thetastar.make(lazy=True), "u_trap", 20, 0)`.

## Results (ran 2026-11-10, Apple silicon arm64, 16 CPUs, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

The machine was shared with other jobs: 1-minute load average 38-256 at the start or end of the
runs (each results file records it). Every ms number below is wall time under that load and is pessimistic. Outcomes,
times to B, path lengths and clearances are simulated time and do not depend on load. The arena
loop is synchronous, so a slow replan does not cost flight time here. On a real drone it would
mean flying on a stale path.

Total run time of the three commands: 781.5 s + 123 s + 296.3 s, about 20 min.

### Headline: faster flights, slightly longer paths, 3.5-5.5x the planning time

Paired by layout, seed 0, 20 layouts per family, preset ideal (72 rays, 6 m). Ratio = Theta* /
A* + shortcut on the same layout, median over layouts both planners reached
([results/flights_0.md](results/flights_0.md)).

| map | family | time to B ratio | faster runs | flown length ratio | min clearance gain m |
|---|---|---|---|---|---|
| known | random | 0.937 | 17 / 20 | 1.006 | 0.275 |
| known | u_trap | 0.916 | 20 / 20 | 1.008 | 0.31 |
| known | narrow_gap | 0.931 | 20 / 20 | 1.011 | 0.039 |
| known | office | 0.864 | 20 / 20 | 1.04 | 0.015 |
| known | warehouse | 0.659 | 20 / 20 | 1.018 | 0.08 |
| known | forest | 0.797 | 20 / 20 | 1.016 | 0.268 |
| known | maze | 0.725 | 20 / 20 | 1.065 | 0.204 |
| known | glass_office | 0.848 | 20 / 20 | 1.038 | 0.008 |
| unknown | random | 0.908 | 17 / 20 | 1.005 | 0.245 |
| unknown | u_trap | 0.88 | 20 / 20 | 1.008 | 0.282 |
| unknown | narrow_gap | 0.892 | 18 / 18 | 1.009 | 0.047 |
| unknown | office | 0.871 | 18 / 18 | 1.052 | 0.019 |
| unknown | warehouse | 0.835 | 11 / 11 | 1.014 | 0.012 |
| unknown | forest | 0.797 | 20 / 20 | 1.014 | 0.183 |
| unknown | maze | 0.749 | 16 / 18 | 1.073 | 0.194 |
| unknown | glass_office | 0.845 | 18 / 18 | 1.04 | 0.008 |

- **Faster to B, not shorter.** Theta* reached B sooner in 157 of 160 known-map layouts (median
  6-34 % less time per family) and in 138 of the 143 unknown-map layouts that both reached. The
  flown path was 0.5-7.3 % *longer* (median per family). Lazy Theta* gives the same picture
  (all rows in [results/flights_0.md](results/flights_0.md)).
- **Why (planning-only check, [results/plans_0.md](results/plans_0.md)):** on the known map,
  Theta* plans have a lower clearance-weighted cost than A* + shortcut in 157 of 160 layouts
  (median ratio 0.855), 1.2 % more length, and more clearance (median exact clearance 0.655 m vs
  0.582 m). The A* shortcut keeps the clearance of the sub-path it replaces, capped at 0.6 m;
  Theta* trades a little length for clearance along the whole path. The follower flies faster
  with more clearance (speed scales with the ESDF between vehicle and carrot). That speed link
  is our reading of the numbers; it was not isolated by an experiment.
- **Same success with a dense sensor.** Known map: 100 % reached, 0 % collision on all 8
  families for all three planners. Unknown map: 0 % collision, reached within one run (5 %) of
  A* in every family except warehouse, where both Theta* variants reached more (60 % and 65 %
  vs 55 %).
- **Worse with 4 beams in office.** Crazyflie preset (4 cone beams, 3 m), unknown map, office:
  collisions A* 25 %, Theta* 60 %, Lazy Theta* 35 %, all with matte walls. Random: 100 %
  reached for all three. The cause was not traced. One candidate: the extra map clearance makes
  the follower fly faster towards walls the 4 beams have not seen yet.
- **Planning cost: FAIL against the ~200 ms per replan budget for plain Theta*, borderline for
  Lazy Theta*.** See the next table.

### Planning time per replan

| source | planner | median ms | p95 ms | replans over 200 ms |
|---|---|---|---|---|
| plan-only, known map, 1 process, 160 plans | A* + shortcut | 18.41 | 63.44 | - |
| plan-only, known map, 1 process, 160 plans | Theta* | 118.38 | 265.7 | - |
| plan-only, known map, 1 process, 160 plans | Lazy Theta* | 72.59 | 183.95 | - |
| in flight, unknown map, 1 process, 8 runs | A* unknown | 15.68 | 75.34 | 0 % |
| in flight, unknown map, 1 process, 8 runs | Theta* unknown | 74.15 | 1878.59 | 37.6 % |
| in flight, unknown map, 1 process, 8 runs | Lazy Theta* unknown | 35.68 | 388.03 | 21.4 % |
| in flight, 14 processes, all 160 ideal runs | A* known / unknown | 6.98 / 21.97 | 68.95 / 83.58 | 0 % / 0 % |
| in flight, 14 processes, all 160 ideal runs | Theta* known / unknown | 45.61 / 131.31 | 326.73 / 1955.97 | 10.7 % / 44.4 % |
| in flight, 14 processes, all 160 ideal runs | Lazy known / unknown | 27.28 / 56.61 | 195.59 / 471.3 | 4.8 % / 25.5 % |

Sources: [results/plans_0.md](results/plans_0.md) (row "all"),
[results/timing_unknown_jobs1.md](results/timing_unknown_jobs1.md) (one layout per family, the
whole flight), [results/flights_0.md](results/flights_0.md) (pooled table). On the same layout and
in the same process, Theta* took a median 5.51x and Lazy Theta* 3.46x the A* + shortcut time
(plans_0.md). Plain Theta* ran a median 2.77 line checks per expansion, Lazy Theta* 0.92
(plans_0.json; segments priced by the uniform-disc skip are not counted).

- Known map: Lazy Theta* meets ~200 ms at p95 (183.95 ms) in the plan-only run; Theta* does
  not (265.7 ms).
- Unknown map: both miss it. Our reading (expansion counts were not saved for these flights):
  unexplored cells cost 2 per cell but the Euclidean heuristic assumes 1, so the search expands
  a large part of the 240 x 240 map, and each Theta* expansion costs more than an A* one. A*
  has the same weak heuristic and stays at 75.34 ms p95.
- Each A* row in results/flights_0.json equals close-area-benchmark's
  [matrix_0.json](../close-area-benchmark/results/matrix_0.json) run by run on outcome, min
  clearance, path length and time to goal: 160/160 known, 160/160 unknown, 40/40 crazyflie
  ([results/matrix_check_0.md](results/matrix_check_0.md)). So the Theta* rows can be read
  against the benchmark directly.

### Full flight table

`python bench.py flights --layouts 20 --seed 0 --workers 14`, wall 781.5 s, 1080 runs
([results/flights_0.md](results/flights_0.md), console in `results/flights_stdout.txt`; the .md
was rebuilt from the .json with `bench.py render` to add the pooled replan table). Time limits:
60 s, 120 s for warehouse and maze.

| preset | planner | family | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | replans | replan ms median | replan ms p95 | replan ms max | fallback replans | no-path replans |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ideal | astar_known | random | 100 | 0 | 0 | 0 | 18.46 | 23.94 | 0.633 | 947 | 1.63 | 41.99 | 124.85 | 0 | 0 |
| ideal | astar_known | u_trap | 100 | 0 | 0 | 0 | 19.24 | 24.8 | 0.617 | 980 | 2.38 | 56.55 | 110.72 | 0 | 0 |
| ideal | astar_known | narrow_gap | 100 | 0 | 0 | 0 | 24.48 | 24.57 | 0.277 | 1241 | 5.76 | 89.7 | 162.82 | 0 | 0 |
| ideal | astar_known | office | 100 | 0 | 0 | 0 | 21.01 | 10.51 | 0.265 | 1116 | 6.64 | 66.81 | 140.27 | 0 | 0 |
| ideal | astar_known | warehouse | 100 | 0 | 0 | 0 | 43.74 | 35.02 | 0.539 | 2212 | 10.08 | 33.96 | 68.24 | 0 | 0 |
| ideal | astar_known | forest | 100 | 0 | 0 | 0 | 22.72 | 24.16 | 0.616 | 1160 | 4.7 | 72.32 | 200.77 | 0 | 0 |
| ideal | astar_known | maze | 100 | 0 | 0 | 0 | 41.03 | 35.79 | 0.594 | 2127 | 16.66 | 68.27 | 123.09 | 0 | 0 |
| ideal | astar_known | glass_office | 100 | 0 | 0 | 0 | 25.12 | 12.39 | 0.265 | 1302 | 8.22 | 102.55 | 166.35 | 0 | 0 |
| ideal | thetastar_known | random | 100 | 0 | 0 | 0 | 17.09 | 24.06 | 0.943 | 862 | 22.01 | 237.41 | 644.77 | 0 | 0 |
| ideal | thetastar_known | u_trap | 100 | 0 | 0 | 0 | 17.66 | 25.04 | 0.931 | 891 | 39.32 | 263.28 | 491.93 | 0 | 0 |
| ideal | thetastar_known | narrow_gap | 100 | 0 | 0 | 0 | 22.36 | 24.91 | 0.34 | 1136 | 53.99 | 613.63 | 1085.44 | 0 | 0 |
| ideal | thetastar_known | office | 100 | 0 | 0 | 0 | 18.05 | 10.96 | 0.283 | 928 | 41.39 | 324.44 | 620.08 | 0 | 0 |
| ideal | thetastar_known | warehouse | 100 | 0 | 0 | 0 | 27.46 | 35.68 | 0.603 | 1457 | 51.49 | 178 | 294.76 | 0 | 0 |
| ideal | thetastar_known | forest | 100 | 0 | 0 | 0 | 18.12 | 24.63 | 0.891 | 924 | 44.36 | 217.92 | 548.48 | 0 | 0 |
| ideal | thetastar_known | maze | 100 | 0 | 0 | 0 | 30.07 | 38.09 | 0.797 | 1542 | 52.09 | 199.22 | 333.8 | 0 | 0 |
| ideal | thetastar_known | glass_office | 100 | 0 | 0 | 0 | 21.17 | 13.19 | 0.266 | 1100 | 49.83 | 700.2 | 1231.76 | 0 | 0 |
| ideal | lazy_thetastar_known | random | 100 | 0 | 0 | 0 | 17.11 | 24.07 | 0.933 | 862 | 14.91 | 163.08 | 415.95 | 0 | 0 |
| ideal | lazy_thetastar_known | u_trap | 100 | 0 | 0 | 0 | 17.68 | 25.02 | 0.921 | 892 | 17.64 | 179.05 | 329.67 | 0 | 0 |
| ideal | lazy_thetastar_known | narrow_gap | 100 | 0 | 0 | 0 | 22.36 | 24.92 | 0.347 | 1136 | 40.32 | 453.22 | 715.7 | 0 | 0 |
| ideal | lazy_thetastar_known | office | 100 | 0 | 0 | 0 | 18.03 | 11.02 | 0.288 | 927 | 26.47 | 181.03 | 320.92 | 0 | 0 |
| ideal | lazy_thetastar_known | warehouse | 100 | 0 | 0 | 0 | 27.53 | 35.67 | 0.597 | 1459 | 33.73 | 114.63 | 201.11 | 0 | 0 |
| ideal | lazy_thetastar_known | forest | 100 | 0 | 0 | 0 | 18.17 | 24.63 | 0.895 | 925 | 24.68 | 123.62 | 278.61 | 0 | 0 |
| ideal | lazy_thetastar_known | maze | 100 | 0 | 0 | 0 | 29.96 | 38.09 | 0.797 | 1541 | 30.7 | 105.31 | 174.61 | 0 | 0 |
| ideal | lazy_thetastar_known | glass_office | 100 | 0 | 0 | 0 | 20.94 | 13.22 | 0.264 | 1094 | 24.07 | 265.81 | 592.35 | 0 | 0 |
| ideal | astar_unknown | random | 100 | 0 | 0 | 0 | 19.01 | 23.96 | 0.615 | 960 | 26.73 | 77.98 | 133.1 | 0 | 0 |
| ideal | astar_unknown | u_trap | 100 | 0 | 0 | 0 | 22.12 | 26 | 0.597 | 1110 | 40.47 | 81.87 | 119.77 | 0 | 0 |
| ideal | astar_unknown | narrow_gap | 90 | 0 | 5 | 5 | 37.51 | 37.7 | 0.254 | 1920 | 45.65 | 84.54 | 178.7 | 17 | 0 |
| ideal | astar_unknown | office | 95 | 0 | 5 | 0 | 22.8 | 10.64 | 0.261 | 1252 | 7.62 | 23.1 | 74.08 | 0 | 0 |
| ideal | astar_unknown | warehouse | 55 | 0 | 45 | 0 | 49.12 | 27.9 | 0.304 | 2708 | 24.28 | 84.37 | 247.01 | 0 | 0 |
| ideal | astar_unknown | forest | 100 | 0 | 0 | 0 | 23.31 | 24.17 | 0.603 | 1206 | 29.37 | 80.64 | 173.18 | 0 | 0 |
| ideal | astar_unknown | maze | 95 | 0 | 5 | 0 | 50.06 | 39.41 | 0.589 | 2651 | 33.83 | 96.32 | 217.76 | 0 | 0 |
| ideal | astar_unknown | glass_office | 95 | 0 | 5 | 0 | 30.34 | 14.42 | 0.273 | 1623 | 7.45 | 30.18 | 95.67 | 12 | 0 |
| ideal | thetastar_unknown | random | 100 | 0 | 0 | 0 | 17.26 | 24.13 | 0.917 | 873 | 186.25 | 1968.05 | 2462.35 | 0 | 0 |
| ideal | thetastar_unknown | u_trap | 100 | 0 | 0 | 0 | 18.73 | 26.25 | 0.875 | 966 | 320.31 | 1927.62 | 2638.21 | 0 | 0 |
| ideal | thetastar_unknown | narrow_gap | 90 | 0 | 10 | 0 | 31.88 | 38.49 | 0.296 | 1683 | 417.28 | 1692.05 | 2481.57 | 13 | 0 |
| ideal | thetastar_unknown | office | 90 | 0 | 10 | 0 | 19 | 11.24 | 0.272 | 1051 | 27.86 | 111.5 | 441.19 | 0 | 0 |
| ideal | thetastar_unknown | warehouse | 60 | 0 | 40 | 0 | 38.87 | 29.42 | 0.345 | 2087 | 174.37 | 1929.53 | 3362.24 | 0 | 0 |
| ideal | thetastar_unknown | forest | 100 | 0 | 0 | 0 | 18.26 | 24.7 | 0.809 | 967 | 202.85 | 1977.1 | 2863.82 | 0 | 0 |
| ideal | thetastar_unknown | maze | 95 | 0 | 5 | 0 | 37.72 | 43.41 | 0.774 | 1976 | 288.81 | 2746.18 | 3700.26 | 0 | 0 |
| ideal | thetastar_unknown | glass_office | 90 | 0 | 10 | 0 | 25.4 | 14.49 | 0.269 | 1296 | 28.47 | 279.97 | 1855.4 | 13 | 0 |
| ideal | lazy_thetastar_unknown | random | 100 | 0 | 0 | 0 | 17.4 | 24.12 | 0.91 | 879 | 71.17 | 453.25 | 634.33 | 0 | 0 |
| ideal | lazy_thetastar_unknown | u_trap | 100 | 0 | 0 | 0 | 18.85 | 26.24 | 0.869 | 955 | 90.84 | 465.59 | 663.21 | 0 | 0 |
| ideal | lazy_thetastar_unknown | narrow_gap | 90 | 0 | 5 | 5 | 29.43 | 34.92 | 0.29 | 1603 | 157.54 | 476.98 | 791.68 | 0 | 0 |
| ideal | lazy_thetastar_unknown | office | 90 | 0 | 10 | 0 | 18.1 | 10.83 | 0.277 | 997 | 22.08 | 57.88 | 211.48 | 0 | 0 |
| ideal | lazy_thetastar_unknown | warehouse | 65 | 0 | 35 | 0 | 39.1 | 28.69 | 0.421 | 2089 | 65.43 | 466.86 | 1295.28 | 0 | 0 |
| ideal | lazy_thetastar_unknown | forest | 100 | 0 | 0 | 0 | 18.28 | 24.56 | 0.856 | 961 | 69.08 | 459.58 | 723.9 | 0 | 0 |
| ideal | lazy_thetastar_unknown | maze | 90 | 0 | 10 | 0 | 35 | 41.19 | 0.758 | 1917 | 93.59 | 653.34 | 1308.13 | 0 | 0 |
| ideal | lazy_thetastar_unknown | glass_office | 95 | 0 | 5 | 0 | 25.92 | 14.89 | 0.279 | 1327 | 23.08 | 110.29 | 545.94 | 13 | 0 |
| crazyflie | astar_unknown | random | 100 | 0 | 0 | 0 | 22.51 | 24.63 | 0.59 | 1129 | 39.08 | 105.69 | 155.16 | 0 | 0 |
| crazyflie | astar_unknown | office | 35 | 25 | 35 | 5 | 18.84 | 7.6 | 0.225 | 1235 | 10.36 | 33.8 | 90.66 | 62 | 0 |
| crazyflie | thetastar_unknown | random | 100 | 0 | 0 | 0 | 19.34 | 25.63 | 0.715 | 995 | 663.8 | 4121.4 | 6556.8 | 0 | 0 |
| crazyflie | thetastar_unknown | office | 35 | 60 | 5 | 0 | 26.04 | 9.64 | 0.149 | 1082 | 110.73 | 881.62 | 1735.34 | 44 | 0 |
| crazyflie | lazy_thetastar_unknown | random | 100 | 0 | 0 | 0 | 19.95 | 26.01 | 0.787 | 1003 | 238.57 | 1274.41 | 2825.3 | 0 | 0 |
| crazyflie | lazy_thetastar_unknown | office | 45 | 35 | 15 | 5 | 26.32 | 8.86 | 0.169 | 1375 | 45.47 | 188.86 | 686.16 | 21 | 0 |

### Reading: when to pick it

- **Prior map, dense or no sensor, replan budget of a few hundred ms:** Lazy Theta*
  (`make(lazy=True)`). Same success as A*, 6-34 % less time to B per family here, more
  clearance. Plain Theta* gives nearly the same paths (median planned length 25.17 vs 25.18 m)
  at 1.6x the Lazy time (median 118.38 vs 72.59 ms, plans_0.md).
- **No map:** keep `astar_unknown` (or `dstar_lite`) unless you can afford replans of 0.39 s (Lazy) to
  1.88 s (Theta*) at p95, or plan less often. The flights were faster, but 21-38 % of unknown-map replans took more than
  200 ms, and with 4 beams office collisions rose from 25 % to 35-60 %.
- **Short paths are not the gain.** On these layouts the any-angle paths are 0.5-7 % longer than
  A* + shortcut. If shortest length is the goal, A* + shortcut already gets it.
- A null result for "shorter": Theta*'s published advantage (shorter paths than A* with
  post-smoothing, JAIR abstract) is for length-only cost. With this clearance cost the search
  trades length for clearance instead.

## Limits

- Synthetic 2.5D arena, truth pose, point-mass vehicle; one seed (0), which is also the seed the
  A* constants were tuned on (arena README). Inherits every arena and benchmark limit.
- Timing: wall time on a shared machine at load average 24-255, CPython only. Pyodide was not
  run; expect it slower than CPython. The playground lines in INTEGRATION.md are untested.
- The Theta* cost model is our adaptation: the papers use length-only cost on corner-vertex
  grids. Here vertices are cell centres, the edge cost is the A* cell cost integrated along the
  segment, and Lazy Theta*'s trusted edge uses the mean of the two end-cell costs as its estimate
  (not a bound), then is re-priced exactly on expansion.
- Line checks sample every half cell, the same approximation as the A* shortcut; a segment can
  clip a cell corner. Exact clearance of every planned path was still at least 0.241 m on the
  known map (plans_0.md), above the 0.15 m radius.
- The crazyflie office result (more collisions) is 20 layouts, not traced to a cause.
- Single-process unknown-map timing used one layout per family (8 flights, 519-626 replans per
  planner).
- No Angle-Propagation Theta*, no Field D*, no 3D version.

## Sources

- [peer] Daniel, Nash, Koenig, Felner, "Theta*: Any-Angle Path Planning on Grids", JAIR 39, 2010
  ([arXiv 1401.3843](https://arxiv.org/abs/1401.3843)). Abstract checked; the algorithm (Basic
  Theta*, parent(u) => v line-of-sight edge) follows its description. No hub record (proposed
  in INTEGRATION.md).
- [peer] Nash, Koenig, Tovey, "Lazy Theta*: Any-Angle Path Planning and Path Length Analysis in
  3D", AAAI 2010 ([AAAI page](https://aaai.org/papers/00153-18152-lazy-theta-any-angle-path-planning-and-path-length-analysis-in-3d/)).
  Abstract checked; the full paper was not re-read.
- [code] `repo:ai-winter/python_motion_planning` (has a Theta*) and Nav2's Theta* planner
  (`repo:ros-navigation/navigation2`) are hub records; neither was used or run here.
- Hub: [arena CONTRACT](../close-area-arena/CONTRACT.md),
  [close-area-benchmark](../close-area-benchmark/README.md),
  [close-area-planner-sampling](../close-area-planner-sampling/README.md) (same pattern, RRT*),
  [close-area-planner-dstar](../close-area-planner-dstar/README.md),
  [close-area-nav research](../../docs/research/close-area-nav/README.md).
