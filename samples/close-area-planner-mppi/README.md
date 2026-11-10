# close-area-planner-mppi: MPPI (sampling-based MPC) from range returns, alone and on an A* path

Goal: measure whether MPPI (Model Predictive Path Integral control, Williams et al. 2017) fixes
the local-minimum failures of the reactive planners (u_trap, maze), and how it compares with the
unknown-map A* (`astar_esdf`, the benchmark's `astar_unknown`). Everything runs in the shared
[close-area-arena](../close-area-arena/README.md) and is scored there, on truth.

Short answer (synthetic arena, 20 layouts per family, seed 0, details below):

- **MPPI alone does not fix local minima.** With the goal term as the straight-line distance to
  B, it reached 0 % on u_trap and 0 % on maze, stuck in every run. A 4 s horizon and 1024 samples
  lift maze only to 10 % (1 of 10). The horizon (1-4 s, 1.5-6 m at 1.5 m/s) is shorter than the
  detour a trap needs.
- **MPPI on an A* lookahead point (guide='astar') reaches as often as A* or more**: 100 / 100 /
  95 / 100 / 65 / 100 / 95 / 95 % against A*'s 100 / 100 / 90 / 95 / 55 / 100 / 95 / 95 %
  (random, u_trap, narrow_gap, office, warehouse, forest, maze, glass_office), 0 % collisions for
  both. Median time to B is shorter in 7 of 8 families (maze 33.62 vs 50.06 s, warehouse 24.3 vs
  49.12 s). Median min clearance is lower in random, u_trap, forest and maze (u_trap 0.471 vs
  0.597 m, maze 0.365 vs 0.589 m) and slightly higher in narrow_gap, office, warehouse and
  glass_office (+0.018 to +0.027 m). One layout = 5 points, so the 5-10 point reach differences
  are 1-2 layouts.
- **With the Crazyflie 4-beam preset MPPI collides much more than A***: random 20 % vs 0 %,
  office 85 % vs 25 % collisions. Do not fly it on a 4-beam sensor without more work.
- One step costs 4-5 ms median in CPython; with the A* replans inside, p95 is 57-64 ms and the max
  87 ms in one process (target: under 200 ms).

It differs from [close-area-planner-mpc](../close-area-planner-mpc/README.md): that sample is a
QP (OSQP) path follower inside a convex corridor on the **known** map. This one samples
trajectories, has no solver, needs only numpy + scipy, builds its map from range hits, and so can
run in the browser playground (Pyodide ships no osqp wheel).

## The planner (mppi.py)

Every planner step (10 Hz):

1. Map: the scan goes into the arena's log-odds grid (`astar_esdf.LogOddsMap`, range hits only,
   no prior map). ESDF by `scipy.ndimage.distance_transform_edt`, outside the map = occupied.
2. Sample K velocity-setpoint sequences `U + eps` over H steps of 0.1 s. `eps` is AR(1) in time
   (`eps_t = beta eps_t-1 + sqrt(1 - beta^2) n_t`, `n_t ~ N(0, sigma^2)` per axis). Three fixed
   samples: the nominal U, hover (all zero), and "straight at the target, slowing on it".
3. Roll all K out at once (numpy, shape K x H x 2) on the arena's model: first-order velocity lag
   tau 0.15 s, |a| <= 3 m/s^2, |v| <= 2 m/s, 5 Euler substeps per step (the 50 Hz physics step).
   `test_smoke.py` checks the rollout against `vehicle.py` to 1e-9 m.
4. Cost per sample:
   - goal: `W_GOAL * sum_t |p_t - target| * dt + W_TERM * |p_H - target|`. target = B
     (`guide='none'`), or the point 2.0 m along the A* path from the vehicle's projection on it
     (`guide='astar'`);
   - path (astar only): `W_PATH * sum_t (distance to the A* polyline) * dt`;
   - obstacle: `W_OBS * sum relu(D_SAFE - d)^2 * dt_sub`, plus `W_COLL` once if any substep has
     d < 0.15 m (d = ESDF minus half a cell, an estimate of the distance to the surface);
   - smoothness: `W_SMOOTH * sum_t |u_t - u_t-1|^2`;
   - control: `gamma * sum_t u_t . eps_t / sigma^2` (the information-theoretic cross term).
5. Weights `w_k = exp(-(S_k - min S) / lambda)`, `U <- U + sum w_k eps_k / sum w_k`.
6. Send `U[0]`, yaw towards it (1.5/s), shift U by one step (warm start).

`guide='astar'` runs the arena's `AStarESDF(known_map=False)` on the same map (same constants,
replan every 0.4 s or when a new hit touches the path). MPPI replaces its carrot follower.

```python
import mppi
p = mppi.make()                                   # guide='none', K=256, H=20, lambda=1, sigma=0.6
p = mppi.make(guide="astar", bounds=(xmin, ymin, xmax, ymax))   # geofence for the map corner
```

`bounds` puts the 24 m map corner at bounds - 2 m, as the benchmark does for `astar_unknown`.
Without it the corner is picked on the first step at (min(0, Bx) - 2.5, min(0, By) - 2.5).

### Parameters and what each changes

Numbers in this table come from [results/sweep_0.md](results/sweep_0.md) (K, horizon) or from
the dev-seed runs described under "How the defaults were set".

| parameter | default | what it changes |
|---|---|---|
| K (`K`) | 256 | Samples per step. Cost is linear in K x H: 2.2 ms (64 x 10) to 10.4 ms (1024 x 40) per step. In the sweep K changed outcomes by at most 1 of 10 layouts per cell; 64 x 40 is the only cell with a collision (maze, 1 of 10) |
| horizon (`horizon`) | 20 steps = 2 s | How far each rollout looks. 4 s gives faster flights (random 17.07 vs 20.24 s with A*) but cuts maze clearance about in half (0.194 vs 0.373 m). Even 4 s does not get guide='none' out of a maze |
| lambda (`lam`) | 1.0 | Temperature of the softmin. Lower => the update follows the few best samples (greedy, jumpy). Higher => weights flatten towards a plain average of the noise and the vehicle slows down. Compare it with the cost scale: W_TERM = 3 per metre of end distance. Not swept |
| sigma (`sigma`) | 0.6 m/s | Per-axis noise std. Larger explores wider (around obstacles, through gaps it was not aimed at) but fewer samples land on precise moves near walls and B. On dev seed 1, narrow_gap, sigma 0.4 reached 3 of 12 layouts where 0.6 reached 10 of 12 (before W_PATH and the third fixed sample; console only, not saved). Not swept on seed 0 |
| beta (`beta`) | 0.8 | Time correlation of the noise. With white noise (beta 0) the smoothness cost makes every noisy sample worse than the nominal one: the first version was stuck at A in all 30 dev runs (5 layouts x 3 families x 2 guides, console only) |
| gamma (`gamma`) | 0.1 | Weight of the cross term. In a single-run check (seed 0, random layout 0, guide none, 4 s horizon, before the fix below) gamma 0.1 took 27.4 s to B against 18.2 s at 0. Console only, not saved |
| D_SAFE, W_OBS | 0.4 m, 100 | Where the obstacle cost starts and how steep it is. With D_SAFE 0.6 m a dev narrow_gap run hovered 1 m in front of a 0.66 m gap; 0.4 m reached 5 of 6 dev narrow_gap layouts against 4 of 6 (console only) |
| W_PATH | 3.0 | Pulls samples towards the A* polyline (astar only). Dev narrow_gap, 12 layouts: 10 reached at 0, 11 at 3, 7 at 10 (with a 3 m lookahead). Console only |
| LOOKAHEAD_M | 2.0 m | Distance of the target along the A* path. Dev narrow_gap, 12 layouts, W_PATH 0: 3 reached at 1.0 m against 10 at 2.0 m (console only) |

## Run

```sh
cd samples/close-area-planner-mppi
uv venv .venv && uv pip install --python .venv -r requirements.txt   # numpy + scipy, from the arena
.venv/bin/python bench.py --preset ideal --layouts 20 --seed 0 --workers 14     # ~100 s
.venv/bin/python bench.py --preset crazyflie --families random,office --layouts 20 --seed 0 --workers 14   # ~16 s
.venv/bin/python bench.py --timing --workers 1                                  # ~66 s, one process
.venv/bin/python sweep.py --layouts 10 --seed 0 --workers 14                    # ~95 s
.venv/bin/python -m unittest test_smoke -v                                      # ~3 s; skips without numpy
```

From another sample: `import arena, mppi` then
`arena.run.evaluate(lambda: mppi.make(guide="astar"), "u_trap", 20, 0)` (the folder on
`sys.path`). `arena.py` loads the arena folder as package `close_area_arena` (CONTRACT.md
"Import"), or reuses it when it is already imported. No arena file is edited.

`bench.py` copies the flight loop of [close-area-benchmark](../close-area-benchmark/README.md)
(`run_one` without the safety filter, `world_glass.make_any_world`, `presets.make_sensor`, 60 s
limit, 120 s for maze and warehouse). Its `astar_unknown` row matches the benchmark matrix run by
run: 160/160 identical (outcome, min clearance, path length) on ideal and 40/40 on crazyflie.

## Results (ran 2026-11-10, Apple M3 Max, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

All inputs are **synthetic**: simulated layouts, vehicle and sensor, true pose. Nothing here is
a flight or SITL result.

### Eight families, ideal sensor (72 rays, 6 m)

`python bench.py --preset ideal --layouts 20 --seed 0 --workers 14`, wall 99.1 s
([results/bench_ideal_0.md](results/bench_ideal_0.md), per-run rows in
`results/bench_ideal_0.json`). Step ms here were measured with 14 processes sharing the machine.
Median time to B is over the runs that reached B only.

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | step ms median | step ms p95 | A* replan ms median | A* replan ms p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | random | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 19.01 | 23.96 | 0.615 | 0.65 | 63.58 | 24.99 | 77.41 |
| astar_unknown | u_trap | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 22.12 | 26.0 | 0.597 | 0.67 | 69.24 | 40.89 | 85.23 |
| astar_unknown | narrow_gap | 20 | 90.0 | 0.0 | 5.0 | 5.0 | 37.51 | 37.7 | 0.254 | 0.66 | 68.3 | 45.19 | 83.23 |
| astar_unknown | office | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 22.8 | 10.64 | 0.261 | 0.54 | 14.53 | 7.39 | 20.51 |
| astar_unknown | warehouse | 20 | 55.0 | 0.0 | 45.0 | 0.0 | 49.12 | 27.9 | 0.304 | 0.5 | 63.65 | 25.49 | 84.88 |
| astar_unknown | forest | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 23.31 | 24.17 | 0.603 | 0.7 | 68.94 | 29.98 | 85.28 |
| astar_unknown | maze | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 50.06 | 39.41 | 0.589 | 0.54 | 77.43 | 35.25 | 98.25 |
| astar_unknown | glass_office | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 30.34 | 14.42 | 0.273 | 0.58 | 17.14 | 7.83 | 32.69 |
| mppi_none | random | 20 | 90.0 | 0.0 | 10.0 | 0.0 | 20.35 | 23.94 | 0.45 | 4.11 | 8.16 | - | - |
| mppi_none | u_trap | 20 | 0.0 | 0.0 | 100.0 | 0.0 | - | 13.11 | 0.685 | 4.16 | 10.88 | - | - |
| mppi_none | narrow_gap | 20 | 25.0 | 0.0 | 75.0 | 0.0 | 22.76 | 20.42 | 0.561 | 3.96 | 8.85 | - | - |
| mppi_none | office | 20 | 25.0 | 0.0 | 75.0 | 0.0 | 8.4 | 2.65 | 0.579 | 3.8 | 8.7 | - | - |
| mppi_none | warehouse | 20 | 15.0 | 0.0 | 85.0 | 0.0 | 27.1 | 21.52 | 0.288 | 3.88 | 8.1 | - | - |
| mppi_none | forest | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 20.29 | 23.91 | 0.435 | 4.12 | 8.82 | - | - |
| mppi_none | maze | 20 | 0.0 | 0.0 | 100.0 | 0.0 | - | 8.67 | 0.382 | 3.91 | 16.55 | - | - |
| mppi_none | glass_office | 20 | 10.0 | 0.0 | 90.0 | 0.0 | 5.83 | 2.3 | 0.611 | 3.81 | 8.71 | - | - |
| mppi_astar | random | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 20.24 | 23.94 | 0.605 | 4.71 | 72.44 | 29.56 | 82.05 |
| mppi_astar | u_trap | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 21.93 | 25.82 | 0.471 | 4.78 | 80.06 | 39.8 | 94.59 |
| mppi_astar | narrow_gap | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 33.92 | 38.35 | 0.281 | 4.96 | 80.71 | 46.94 | 92.41 |
| mppi_astar | office | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 11.35 | 11.91 | 0.286 | 4.89 | 19.91 | 8.26 | 20.69 |
| mppi_astar | warehouse | 20 | 65.0 | 0.0 | 35.0 | 0.0 | 24.3 | 28.77 | 0.322 | 5.41 | 69.29 | 25.34 | 90.18 |
| mppi_astar | forest | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 20.4 | 24.08 | 0.563 | 4.98 | 78.88 | 30.95 | 100.94 |
| mppi_astar | maze | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 33.62 | 37.19 | 0.365 | 4.92 | 83.97 | 36.82 | 100.27 |
| mppi_astar | glass_office | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 15.06 | 14.6 | 0.292 | 4.9 | 25.53 | 8.61 | 38.29 |

Against the reactive planners on the same layouts (ideal preset, reached %, from
[close-area-benchmark/results/matrix_0.md](../close-area-benchmark/results/matrix_0.md)):
u_trap: APF with escape 90, Bug2 90, TangentBug 90, VFH+ 0, DWA 0, mppi_none 0. maze: Bug2 20,
TangentBug 15, APF 10, VFH+ 10, DWA 0, mppi_none 0. So MPPI without a global plan sits with the
planners that have no escape rule. It is a better local controller than DWA in open clutter
(random 90 vs 80 %, forest 100 vs 90 %), not a fix for traps.

A second run of the same command gave identical outcome, min clearance, path length and time to
B in 480 of 480 runs ([results/determinism_check.txt](results/determinism_check.txt)).

### Crazyflie preset (4 cone beams, 3 m, glass invisible)

`python bench.py --preset crazyflie --families random,office --layouts 20 --seed 0 --workers 14`,
wall 15.2 s ([results/bench_crazyflie_0.md](results/bench_crazyflie_0.md)):

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | step ms median | step ms p95 | A* replan ms median | A* replan ms p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | random | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 22.51 | 24.63 | 0.59 | 0.33 | 84.6 | 41.14 | 112.74 |
| astar_unknown | office | 20 | 35.0 | 25.0 | 35.0 | 5.0 | 18.84 | 7.6 | 0.225 | 0.39 | 22.24 | 11.75 | 38.44 |
| mppi_none | random | 20 | 55.0 | 40.0 | 5.0 | 0.0 | 20.3 | 23.39 | 0.422 | 3.85 | 8.64 | - | - |
| mppi_none | office | 20 | 5.0 | 75.0 | 20.0 | 0.0 | 9.9 | 2.79 | 0.143 | 3.89 | 7.86 | - | - |
| mppi_astar | random | 20 | 80.0 | 20.0 | 0.0 | 0.0 | 20.37 | 23.95 | 0.535 | 4.98 | 86.36 | 42.75 | 101.22 |
| mppi_astar | office | 20 | 10.0 | 85.0 | 5.0 | 0.0 | 8.1 | 4.08 | 0.142 | 5.24 | 28.28 | 11.58 | 34.96 |

MPPI treats unknown cells as free, like the A*. A likely cause (not tested) is that its sampled
trajectories cut sideways into space the 4 beams have not seen, where the A* carrot moves along
its path with the front beam facing travel. Candidates to try: a cost on unknown cells, or limit
samples to the beam directions seen in the last second.

### Step timing, one process

`python bench.py --timing --workers 1` (random and maze, 5 layouts, nothing else running), wall
65.8 s ([results/timing_0.md](results/timing_0.md)). Max from `results/timing_0.json`.

| planner | family | steps | step ms median | step ms p95 | step ms max | A* replan ms median / p95 |
|---|---|---|---|---|---|---|
| astar_unknown | random | 935 | 0.65 | 51.88 | 67.07 | 22.42 / 59.86 |
| astar_unknown | maze | 2246 | 0.48 | 59.13 | 78.51 | 22.01 / 72.35 |
| mppi_none | random | 989 | 3.77 | 4.03 | 6.33 | - |
| mppi_none | maze | 1219 | 3.63 | 3.91 | 4.66 | - |
| mppi_astar | random | 1014 | 4.18 | 57.09 | 70.64 | 22.64 / 60.69 |
| mppi_astar | maze | 1525 | 4.33 | 64.3 | 86.99 | 23.01 / 72.77 |

Against the 200 ms per replan target: PASS in one process (max 87 ms). Under the 14-process
load of the main bench the largest mppi_astar step was 224.85 ms (warehouse, in
`results/bench_ideal_0.json` `step_ms_max`); the A* search inside, not the MPPI update, sets the
tail. MPPI itself is 2-10 ms for K x H from 64 x 10 to 1024 x 40 (next table).

### Sweep of K and horizon (random and maze, 10 layouts)

`python sweep.py --layouts 10 --seed 0 --workers 14`, flights wall 91.6 s
([results/sweep_0.md](results/sweep_0.md), runs in `results/sweep_0.json`). lambda, sigma, beta
at their defaults. Step ms: one `step()` with guide none on random layout 0, 30 calls, one
process.

| guide | K | horizon | random reached % | random median time to B s | random median min clearance m | maze reached % | maze collision % | maze median time to B s | maze median min clearance m | step ms median / p95 (one process) |
|---|---|---|---|---|---|---|---|---|---|---|
| none | 64 | 10 (1 s) | 90 | 23.34 | 0.41 | 0 | 0 | - | 0.412 | 2.19 / 2.37 |
| none | 64 | 20 (2 s) | 90 | 20.64 | 0.389 | 0 | 0 | - | 0.381 | 2.65 / 3.0 |
| none | 64 | 40 (4 s) | 90 | 17.86 | 0.351 | 0 | 0 | - | 0.492 | 3.67 / 4.0 |
| none | 256 | 10 (1 s) | 90 | 22.6 | 0.423 | 0 | 0 | - | 0.441 | 2.62 / 2.74 |
| none | 256 | 20 (2 s) | 90 | 20.46 | 0.423 | 0 | 0 | - | 0.411 | 3.45 / 3.81 |
| none | 256 | 40 (4 s) | 90 | 18.24 | 0.425 | 0 | 0 | - | 0.341 | 5.01 / 5.21 |
| none | 1024 | 10 (1 s) | 90 | 22.5 | 0.423 | 0 | 0 | - | 0.426 | 3.93 / 4.13 |
| none | 1024 | 20 (2 s) | 100 | 20.8 | 0.39 | 0 | 0 | - | 0.404 | 6.09 / 6.29 |
| none | 1024 | 40 (4 s) | 100 | 18.73 | 0.408 | 10 | 0 | 21.74 | 0.329 | 10.36 / 10.96 |
| astar | 64 | 10 (1 s) | 100 | 22.08 | 0.595 | 90 | 0 | 34.62 | 0.359 | 2.19 / 2.37 |
| astar | 64 | 20 (2 s) | 100 | 18.75 | 0.599 | 90 | 0 | 29.52 | 0.282 | 2.65 / 3.0 |
| astar | 64 | 40 (4 s) | 100 | 17.05 | 0.583 | 80 | 10 | 26.82 | 0.197 | 3.67 / 4.0 |
| astar | 256 | 10 (1 s) | 100 | 21.79 | 0.615 | 90 | 0 | 34.8 | 0.387 | 2.62 / 2.74 |
| astar | 256 | 20 (2 s) | 100 | 20.24 | 0.589 | 90 | 0 | 32.62 | 0.373 | 3.45 / 3.81 |
| astar | 256 | 40 (4 s) | 100 | 17.07 | 0.58 | 90 | 0 | 26.66 | 0.194 | 5.01 / 5.21 |
| astar | 1024 | 10 (1 s) | 100 | 21.85 | 0.612 | 90 | 0 | 34.24 | 0.384 | 3.93 / 4.13 |
| astar | 1024 | 20 (2 s) | 100 | 21.77 | 0.61 | 90 | 0 | 35.82 | 0.427 | 6.09 / 6.29 |
| astar | 1024 | 40 (4 s) | 100 | 17.23 | 0.589 | 90 | 0 | 27.52 | 0.213 | 10.36 / 10.96 |

Reading: the horizon matters more than K. Longer horizons fly faster and closer to walls. K
above 256 bought nothing here.

### How the defaults were set

Constants were tuned by hand on dev seed 1 (layouts 0-11, random, u_trap and narrow_gap): AR(1)
noise instead of white noise, D_SAFE 0.6 => 0.4 m, the collision threshold radius + 0.05 => the
radius, W_PATH 0 => 3. Those intermediate runs were not saved. The final dev run is
[results/bench_ideal_1.md](results/bench_ideal_1.md) (10 layouts, all 8 families).
The third fixed sample (straight at the target) was added after the **first seed-0 sweep**
showed MPPI stalling short of B at a 4 s horizon (three console checks: 0.55-0.73 m short) (random: astar guide 0 % reached at
H = 40 for every K, [results/sweep_0_before_direct_sample.md](results/sweep_0_before_direct_sample.md),
superseded). So seed 0 is not fully held out for that change. All seed-0 numbers above are from
the code after it.

## Limits

- Synthetic 2.5D point-mass arena, ideal ray casts or the arena's cone model, true pose. No
  estimator faults, no SITL, no real drone.
- 20 layouts per cell (10 in the sweep): one layout is 5 (10) points. The reach differences
  between mppi_astar and astar_unknown are 0-2 layouts per family.
- Unknown cells are free in the cost. With 4 beams that is where the collisions come from (see
  above); there is no fix in this sample.
- No hard constraint: a collision is a cost (`W_COLL`), not a guarantee. Put a range safety
  filter under it, as for every planner in the hub
  ([close-area-safety-filter](../close-area-safety-filter/README.md)).
- lambda and sigma were not swept on seed 0. The control term uses the per-axis sigma and
  ignores the AR(1) correlation of the noise, a simplification of the paper's update.
- Browser: written for Pyodide (numpy + scipy only, no other imports) and loaded through the
  playground's `_load_sample` recipe in CPython from a copy of the manifest file layout. **Not
  run in Pyodide**; Pyodide timing is not measured.
- Timings are CPython on an M3 Max laptop, not a flight computer.

## Sources

- G. Williams, N. Wagener, B. Goldfain, P. Drews, J. M. Rehg, B. Boots, E. A. Theodorou,
  "Information Theoretic MPC for Model-Based Reinforcement Learning", ICRA 2017
  ([PDF](https://homes.cs.washington.edu/~bboots/files/InformationTheoreticMPC.pdf)). The
  update in step 5 and the control cross term.
- G. Williams, P. Drews, B. Goldfain, J. M. Rehg, E. A. Theodorou, "Information Theoretic Model
  Predictive Control: Theory and Applications to Autonomous Driving", IEEE T-RO 2018
  ([arXiv:1707.02342](https://arxiv.org/abs/1707.02342)).
- Nav2 ships an MPPI local controller for ground robots
  ([catalog record](../../catalog/repos/ros-navigation__navigation2.md)); not used or compared here.
- Arena, scorer, unknown-map A*: [close-area-arena](../close-area-arena/README.md),
  [CONTRACT.md](../close-area-arena/CONTRACT.md); benchmark matrix:
  [close-area-benchmark](../close-area-benchmark/README.md).
