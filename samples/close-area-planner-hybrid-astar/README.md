# close-area-planner-hybrid-astar: Hybrid A* against A* + follower in the close-area arena

Goal: answer one question with numbers. On a vehicle with a turn-rate limit, does a
kinematically feasible plan (Hybrid A*) reduce collisions or time to B compared with the
arena's grid A* plus carrot follower ([planners/astar_esdf.py](../close-area-arena/planners/astar_esdf.py))?
Everything runs in the shared [close-area-arena](../close-area-arena/README.md). numpy + scipy
only, so the planner can load in the browser playground (not tried, see Limits).

Short answer (synthetic arena, seed 0): **no for collisions, yes for time, at a cost in reached %.**
Hybrid A* had the same collision rate (0 % on preset ideal for every planner; 17.5 % vs 17.5 % on
the crazyflie preset with the turn-limited vehicle). When both reached B it was 0.94 s faster
(median, turn-limited vehicle, 152 paired runs). It reached B less often: 81.9 % vs 91.2 % on
the turn-limited vehicle over 8 families. Most of that gap comes from runs the arena scores
`stuck` while the vehicle was flying back over its own track.

## Files

- `hybrid_astar.py`: `HybridAStar` subclasses `AStarESDF`. Search over continuous
  (x, y, heading), closed set binned 0.25 m x 0.25 m x 10 deg. Primitives:
  - fast arcs at 1.5 m/s, 0.6 m long, turn rate 0, +-0.5 or +-1.0 x `OMEGA_MAX` (1.0 rad/s);
  - slow arcs at 0.5 m/s, 0.4 m long, +-1.0 rad/s (radius 0.5 m);
  - turns in place of +-45 deg.

  Lateral acceleration stays at or below 1.5 m/s^2, so the arena's 3 m/s^2 limit holds.
  There is no Reeds-Shepp expansion. Every 3 expansions the search tries a straight shot to B
  and accepts it if the segment keeps the inflation plus min(0.5 m, node clearance, B clearance)
  of ESDF. A heading change above 0.4 rad at the start of the shot is paid as a turn in place.
  The cost is flight time x (1 + astar_esdf's clearance cost + unknown-cell penalty). The
  heuristic is a cost-weighted 2D Dijkstra from B (`scipy.sparse.csgraph`), weighted 1.5.
  The planner keeps astar_esdf's log-odds map, its two inflation levels (0.25 m, then 0.15 m),
  its 2.5 Hz replan rule and its carrot follower. The one addition is a speed profile:
  primitive speed, 0.2 m/s at turns in place, and a backward pass at 1.5 m/s^2. It caps the
  follower's speed. If no path is found within 4000 expansions, the planner falls back to
  astar_esdf's grid path; this happened in 0 % of replans. `make()` needs no arguments.
  `make(bounds=(xmin, ymin, xmax, ymax))` puts the map on the geofence, as the benchmark does.
- `vehicle_turn.py`: `TurnLimitedVehicle`, a subclass of the arena vehicle that clips the
  acceleration normal to the velocity to `omega_max * |v|`. The velocity direction then turns
  at 1.0 rad/s at most. Below 0.05 m/s there is no clip, so the vehicle can turn in place.
  This is a model chosen for this test (for example, a forward sensor that must face the
  direction of travel with a capped yaw rate), not a measured vehicle. The stock arena vehicle
  has no turn-rate limit beyond |a| <= 3 m/s^2: that is 2 rad/s at 1.5 m/s, and no limit near
  standstill.
- `bench.py`: flights. Three planners, all on an unknown map built from range hits, geofenced:
  `astar_unknown` (the benchmark row), `astar_unknown_pp` (the same planner with a pure-pursuit
  turn speed cap, v <= max(0.2, 1.0 rad/s x R); a control arm for "just slow down at
  corners"), and `hybrid_astar`. Each runs on two vehicles: `stock` and `turn1`. The loop is
  close-area-benchmark's `run_one` without the filter branch.
- `plan_quality.py`: planning only, on the known map. Each planner plans once from A. The
  script reports path shape and the minimum time to B under the same limits for both planners
  (`metrics.py`).
- `metrics.py`: heading change per metre (polyline resampled every 0.25 m) and the minimum
  rest-to-rest time along a path (|v| <= 1.5 m/s, |a| <= 3 m/s^2, lateral <= 3 m/s^2, and
  optionally turn rate <= 1.0 rad/s).
- `arena.py`: loads the arena as package `close_area_arena` (the recipe in CONTRACT.md). No
  arena file is edited.

## Run

```sh
cd samples/close-area-planner-hybrid-astar
uv venv --python 3.12 .venv && uv pip install --python .venv -r requirements.txt   # numpy + scipy, from the arena
.venv/bin/python bench.py --layouts 20 --seed 0 --workers 14     # ~3.5 min, results/bench_0.*
.venv/bin/python plan_quality.py --layouts 20 --seed 0           # ~15 s, results/plan_quality_0.*
.venv/bin/python bench.py --layouts 5 --seed 0 --workers 1 --planners astar_unknown,hybrid_astar \
    --vehicles stock --families random,office,maze --cf-families "" --stem timing_jobs1_0   # ~1 min
.venv/bin/python -m unittest test_smoke -v                       # skips without numpy
```

From another sample: `import arena, hybrid_astar` then
`arena.mod("run").evaluate(lambda: hybrid_astar.make(), "maze", 20, 0)`.

## Results (ran 2026-11-10, Apple M3 Max, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

Ran before the 2026-11-12 dropped-beam fix ([upstream-findings section 22](../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls)): rows that plan on a map built from range hits used the old mapper and were not re-run here. The [benchmark matrix](../close-area-benchmark/README.md#results-ran-2026-11-12-synthetic) has the regenerated rows.

All inputs are **synthetic**: simulated layouts, vehicle and sensor. Nothing here is SITL or a
flight. The host was shared with other jobs (load average 128-266 seen right after the runs),
so every ms figure is an upper bound for this machine.

### Flights: 8 families x 20 layouts, preset ideal, plus crazyflie on random and office

`python bench.py --layouts 20 --seed 0 --workers 14`: 1200 flights, wall 207.5 s
([results/bench_0.md](results/bench_0.md), all runs in `results/bench_0.json`, console in
`results/bench_stdout.txt`). An earlier run of the same command gave the same reached,
collision and stuck numbers. Parity check: the `astar_unknown` rows on the stock vehicle
equal close-area-benchmark's
[results/matrix_0.json](../close-area-benchmark/results/matrix_0.json) in **200/200** runs
(same outcome, min clearance and path length).

Totals over the 8 families (ideal, 160 runs per row) or over random + office (crazyflie, 40 runs):

| vehicle | preset | planner | runs | reached % | collision % | stuck % | stuck while moving % | timeout % | replan ms median / p95 |
|---|---|---|---|---|---|---|---|---|---|
| stock | ideal | astar_unknown | 160 | 91.2 | 0 | 8.1 | 6.9 | 0.6 | 22.38 / 84.86 |
| stock | ideal | astar_unknown_pp | 160 | 90.6 | 0 | 8.8 | 7.5 | 0.6 | 22.85 / 89.81 |
| stock | ideal | hybrid_astar | 160 | 86.2 | 0 | 11.9 | 9.4 | 1.9 | 13.36 / 24.94 |
| stock | crazyflie | astar_unknown | 40 | 67.5 | 12.5 | 17.5 | 7.5 | 2.5 | 14.21 / 84.45 |
| stock | crazyflie | astar_unknown_pp | 40 | 70 | 22.5 | 7.5 | 2.5 | 0 | 14.19 / 83.18 |
| stock | crazyflie | hybrid_astar | 40 | 67.5 | 25 | 7.5 | 5 | 0 | 13.23 / 24.28 |
| turn1 | ideal | astar_unknown | 160 | 91.2 | 0 | 6.2 | 4.4 | 2.5 | 22.64 / 87.32 |
| turn1 | ideal | astar_unknown_pp | 160 | 88.1 | 0 | 10 | 6.9 | 1.9 | 22.35 / 87.71 |
| turn1 | ideal | hybrid_astar | 160 | 81.9 | 0 | 16.9 | 14.4 | 1.2 | 13.26 / 23.82 |
| turn1 | crazyflie | astar_unknown | 40 | 67.5 | 17.5 | 12.5 | 5 | 2.5 | 14.97 / 79.77 |
| turn1 | crazyflie | astar_unknown_pp | 40 | 65 | 17.5 | 15 | 2.5 | 2.5 | 14.4 / 81.44 |
| turn1 | crazyflie | hybrid_astar | 40 | 65 | 17.5 | 17.5 | 10 | 0 | 13.31 / 28.58 |

"Stuck while moving" is a run the scorer ended as `stuck` (|p(t) - p(t - 10 s)| < 0.2 m)
while the truth speed over its last 0.5 s was above 0.3 m/s. In the two runs inspected
(narrow_gap 1, glass_office 9), the vehicle had explored a dead end in the unknown map, turned
back, and was flying at 1.5 m/s over the point it had passed 10 s earlier. The arena rule ends
such runs, so they count as stuck here too.

Per family, both vehicles, astar_unknown vs hybrid_astar (columns copied from
[results/bench_0.md](results/bench_0.md), which also has timeout %, flown heading change,
astar_unknown_pp and grid fallback %):

| vehicle | preset | planner | family | reached % | collision % | stuck % | median time to B s | median path m | median min clearance m | replan ms median / p95 | stuck while moving % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| stock | ideal | astar_unknown | random | 100 | 0 | 0 | 19.01 | 23.962 | 0.615 | 25.29 / 81.23 | 0 |
| stock | ideal | astar_unknown | u_trap | 100 | 0 | 0 | 22.12 | 26.002 | 0.597 | 41.71 / 84.82 | 0 |
| stock | ideal | astar_unknown | narrow_gap | 90 | 0 | 5 | 37.51 | 37.698 | 0.254 | 46.67 / 86.07 | 5 |
| stock | ideal | astar_unknown | office | 95 | 0 | 5 | 22.8 | 10.637 | 0.261 | 7.56 / 21.74 | 5 |
| stock | ideal | astar_unknown | warehouse | 55 | 0 | 45 | 49.12 | 27.901 | 0.304 | 25.48 / 81.04 | 40 |
| stock | ideal | astar_unknown | forest | 100 | 0 | 0 | 23.31 | 24.17 | 0.603 | 29.52 / 86.21 | 0 |
| stock | ideal | astar_unknown | maze | 95 | 0 | 5 | 50.06 | 39.409 | 0.589 | 34.47 / 95.95 | 5 |
| stock | ideal | astar_unknown | glass_office | 95 | 0 | 5 | 30.34 | 14.416 | 0.273 | 7.61 / 30.55 | 0 |
| stock | ideal | hybrid_astar | random | 100 | 0 | 0 | 18.44 | 24.169 | 0.67 | 12.87 / 22.46 | 0 |
| stock | ideal | hybrid_astar | u_trap | 100 | 0 | 0 | 20.08 | 26.472 | 0.71 | 12.96 / 21.82 | 0 |
| stock | ideal | hybrid_astar | narrow_gap | 70 | 0 | 25 | 32.1 | 30.916 | 0.285 | 13.39 / 23.88 | 20 |
| stock | ideal | hybrid_astar | office | 90 | 0 | 5 | 20.19 | 11.057 | 0.264 | 13.73 / 24.05 | 5 |
| stock | ideal | hybrid_astar | warehouse | 55 | 0 | 45 | 48.28 | 27.405 | 0.259 | 13.27 / 26.6 | 40 |
| stock | ideal | hybrid_astar | forest | 100 | 0 | 0 | 22.47 | 24.334 | 0.552 | 13.03 / 20.87 | 0 |
| stock | ideal | hybrid_astar | maze | 90 | 0 | 5 | 46.46 | 42.498 | 0.46 | 13.7 / 26.97 | 5 |
| stock | ideal | hybrid_astar | glass_office | 85 | 0 | 15 | 29.2 | 13.239 | 0.26 | 13.64 / 25.63 | 5 |
| stock | crazyflie | astar_unknown | random | 100 | 0 | 0 | 22.51 | 24.634 | 0.59 | 35.69 / 95.6 | 0 |
| stock | crazyflie | astar_unknown | office | 35 | 25 | 35 | 18.84 | 7.6 | 0.225 | 9.91 / 29.53 | 15 |
| stock | crazyflie | hybrid_astar | random | 95 | 5 | 0 | 21.24 | 24.558 | 0.601 | 13.13 / 20.7 | 0 |
| stock | crazyflie | hybrid_astar | office | 40 | 45 | 15 | 28.32 | 9.944 | 0.19 | 13.45 / 26.83 | 10 |
| turn1 | ideal | astar_unknown | random | 100 | 0 | 0 | 18.99 | 23.979 | 0.615 | 29.27 / 82.29 | 0 |
| turn1 | ideal | astar_unknown | u_trap | 100 | 0 | 0 | 22.64 | 26.107 | 0.596 | 43.65 / 96.13 | 0 |
| turn1 | ideal | astar_unknown | narrow_gap | 90 | 0 | 0 | 37.62 | 39.037 | 0.267 | 45.84 / 86.85 | 0 |
| turn1 | ideal | astar_unknown | office | 90 | 0 | 5 | 21.89 | 10.782 | 0.265 | 7.82 / 21.41 | 5 |
| turn1 | ideal | astar_unknown | warehouse | 70 | 0 | 30 | 50.86 | 27.98 | 0.305 | 22.11 / 80.75 | 25 |
| turn1 | ideal | astar_unknown | forest | 100 | 0 | 0 | 23.37 | 24.154 | 0.588 | 29.85 / 86.2 | 0 |
| turn1 | ideal | astar_unknown | maze | 90 | 0 | 5 | 48.76 | 39.534 | 0.587 | 39.57 / 101.49 | 5 |
| turn1 | ideal | astar_unknown | glass_office | 90 | 0 | 10 | 30.92 | 14.164 | 0.273 | 8.22 / 36.76 | 0 |
| turn1 | ideal | hybrid_astar | random | 100 | 0 | 0 | 18.17 | 24.085 | 0.709 | 12.7 / 21.94 | 0 |
| turn1 | ideal | hybrid_astar | u_trap | 100 | 0 | 0 | 19.91 | 26.593 | 0.775 | 12.65 / 21.73 | 0 |
| turn1 | ideal | hybrid_astar | narrow_gap | 70 | 0 | 30 | 38.31 | 34.373 | 0.282 | 13.22 / 24.37 | 25 |
| turn1 | ideal | hybrid_astar | office | 85 | 0 | 10 | 20.72 | 12.335 | 0.264 | 13.77 / 23.61 | 0 |
| turn1 | ideal | hybrid_astar | warehouse | 45 | 0 | 55 | 49.96 | 27.328 | 0.258 | 13.18 / 25.01 | 55 |
| turn1 | ideal | hybrid_astar | forest | 100 | 0 | 0 | 22.09 | 24.426 | 0.547 | 12.95 / 20.08 | 0 |
| turn1 | ideal | hybrid_astar | maze | 80 | 0 | 15 | 44.35 | 41.986 | 0.466 | 13.58 / 24.18 | 15 |
| turn1 | ideal | hybrid_astar | glass_office | 75 | 0 | 25 | 30.16 | 14.138 | 0.27 | 13.67 / 23.94 | 20 |
| turn1 | crazyflie | astar_unknown | random | 100 | 0 | 0 | 22.17 | 24.833 | 0.628 | 35.75 / 87.68 | 0 |
| turn1 | crazyflie | astar_unknown | office | 35 | 35 | 25 | 19.46 | 8.007 | 0.214 | 10.39 / 35.2 | 10 |
| turn1 | crazyflie | hybrid_astar | random | 100 | 0 | 0 | 21.77 | 24.776 | 0.618 | 13.13 / 21.54 | 0 |
| turn1 | crazyflie | hybrid_astar | office | 30 | 35 | 35 | 23.44 | 9.551 | 0.184 | 13.72 / 33.02 | 20 |

Paired, runs where both planners reached B (both presets), median of (planner - astar_unknown):

| vehicle | planner | median delta time to B s | paired runs | median delta path m |
|---|---|---|---|---|
| stock | astar_unknown_pp | 0 | 170 | 0 |
| stock | hybrid_astar | -1.21 | 160 | 0.37 |
| turn1 | astar_unknown_pp | 0 | 166 | 0 |
| turn1 | hybrid_astar | -0.94 | 152 | 0.37 |

### Plan shape and time at the same limits (known map, planning only)

`python plan_quality.py --layouts 20 --seed 0`, single process, wall 13.3 s
([results/plan_quality_0.md](results/plan_quality_0.md)). One plan from A per layout,
160 layouts. The table shows medians over all families; per-family rows are in the file.
Both planners found a path on every layout, and Hybrid A* never fell back to the grid path.

| planner | plan ms median / p95 | path m | max heading change rad/m | p95 rad/m | share of joints > 0.67 rad/m | total turn rad | min time stock s | min time turn1 s | min sdf m |
|---|---|---|---|---|---|---|---|---|---|
| astar_esdf | 18.27 / 47.04 | 25.06 | 3.248 | 0.202 | 0.04 | 2.8 | 17.43 | 18.085 | 0.583 |
| hybrid_astar | 7.54 / 15.07 | 25.647 | 2.131 | 0.677 | 0.084 | 6.429 | 17.7 | 18.055 | 0.483 |

Paired per layout (hybrid_astar - astar_esdf): the minimum time under the 1 rad/s turn limit
is 0.435 s lower (median; lower on 68.1 % of layouts). Under stock limits it is 0.065 s
higher (lower on 43.1 %). The path is 0.482 m longer, and the max heading change is
1.021 rad/m lower (lower on 76.2 %).

### Replan time (requirement: one replan under ~200 ms in CPython)

| run | planner | replans | median ms | p95 ms | p99 ms | max ms |
|---|---|---|---|---|---|---|
| bench_0, 14 processes | astar_unknown | 32003 | 20.67 | 85.55 | 105.76 | 199.63 |
| bench_0, 14 processes | hybrid_astar | 30451 | 13.30 | 24.75 | 33.58 | 142.18 |
| timing_jobs1_0, 1 process, random / office / maze x 5, stock | astar_unknown | 1171 | 14.12 | 75.57 | 92.01 | 129.06 |
| timing_jobs1_0, 1 process, random / office / maze x 5, stock | hybrid_astar | 1324 | 11.88 | 21.48 | 33.43 | 60.12 |

Sources: [results/bench_0.md](results/bench_0.md) and
[results/timing_jobs1_0.md](results/timing_jobs1_0.md), section "Replan wall time". **PASS**:
no Hybrid A* replan took more than 200 ms. Hybrid A* replans are faster than the A* baseline
because its heuristic is a C Dijkstra (scipy) and the straight shot to B usually ends the
search after a few dozen expansions. The A* baseline runs a pure-Python heap search over the
whole grid.

### Reading

- **Collisions: no reduction.** On preset ideal no planner collided on either vehicle. With the
  crazyflie preset (4 cone beams 90 deg apart, 3 m), every collision was with a matte wall
  (`hit_material` in `results/bench_0.json`). Walls between the beams get into the map late,
  and a feasible plan does not help with that: on turn1, 17.5 % vs 17.5 %; on the stock vehicle,
  25 % vs 12.5 % (40 runs each, so a 5-run difference).
- **Time: about 1 s faster when both reach B.** The median paired delta is -1.21 s (stock) and
  -0.94 s (turn1), with paths 0.37 m longer. The plans turn less sharply (max heading change
  2.131 vs 3.248 rad/m), and the speed profile stops the follower slowing for each grid
  corner. In planning only, the time gain appears only under the turn limit (-0.435 s), not
  under stock limits (+0.065 s).
- **Reached: worse, mostly through dead-end turnbacks.** On the turn-limited vehicle,
  "stuck while moving" was 14.4 % vs 4.4 %. The largest losses are narrow_gap (70 % vs 90 %),
  glass_office (75 % vs 90 %) and maze (80 % vs 90 %). Our reading, not isolated by an
  experiment: a faster vehicle runs further into unknown dead ends before the map closes them,
  then turns back over its own track and trips the 10 s stuck rule.
- **The turn limit barely changed A*.** astar_unknown reached 91.2 % on both vehicles. The
  pure-pursuit speed cap (astar_unknown_pp) changed the median time by 0 s. The A* follower
  already slows near walls (speed by ESDF), and that is where the corners are, so a 1 rad/s
  limit rarely binds in this arena. A tighter limit or a faster cruise would make the
  question harder; neither was run.
- **Plans are less sharp but wigglier.** The worst turn is gentler, but total turning is
  higher: 6.429 vs 2.8 rad, and 8.4 % vs 4.0 % of joints are above 0.67 rad/m. The cause is the
  10 deg heading bins and the discrete arcs. Dolgov et al. smooth the path after the search
  (conjugate-gradient smoothing on a Voronoi field); this sample does not, which is the obvious
  next step.
- **Pick it when** the platform really cannot turn in place at speed (fixed-wing-like, a
  heading-locked sensor with a low yaw-rate cap) and time matters more than the last few
  percent of reached. For a multirotor in a 20 x 20 m area, A* + follower stays the default.

Baseline for scale (arena, 20 layouts): the straight planner reached 40 % on random
([straight_random_0.md](../close-area-arena/results/straight_random_0.md)).

## Limits

- Own implementation, tuned only enough to run (`H_WEIGHT` 1.5, bins, primitive set). No
  path smoothing and no Voronoi cost, unlike the paper. No reverse motion (not needed for a
  drone).
- The turn-limited vehicle is a model chosen for this test, not a measured airframe.
  Only one limit (1.0 rad/s) was run.
- The speed profile ignores the 0.15 s velocity lag (it brakes at half of a_max for margin).
- Synthetic 2.5D arena, one seed, 20 layouts per cell (crazyflie cells: 40 runs). Differences
  of one run are 5 points per family.
- ms were measured on a host shared with other jobs. They were not measured in Pyodide: the
  browser constraint (numpy + scipy only, `scipy.sparse.csgraph`) is met by the imports, but
  this sample was never loaded in the playground.
- "Stuck while moving" was inspected by hand in 2 runs; the rest rely on the 0.3 m/s rule.

## Sources

- Dolgov, Thrun, Montemerlo, Diebel, "Practical search techniques in path planning for
  autonomous driving", AAAI workshop (STAIR), 2008. Bibliographic data written from memory,
  not checked.
- Dolgov, Thrun, Montemerlo, Diebel, "Path planning for autonomous vehicles in unknown
  semi-structured environments", IJRR 2010, doi 10.1177/0278364909359210: hub record
  [res:dolgov-hybrid-astar-ijrr-2010](../../catalog/resources/dolgov-hybrid-astar-ijrr-2010.md).
- Lane 01 of the close-area research, Hybrid A* and kinodynamic rows:
  [01-planning-and-mapping.md](../../docs/research/close-area-nav/01-planning-and-mapping.md).
