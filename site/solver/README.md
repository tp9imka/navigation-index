# Solver: which navigation algorithm is best for this map?

Open [index.html](index.html) from the repo root: `python3 -m http.server 8000`, then
`http://localhost:8000/site/solver/`. Pick a map, choose the sweep, press **Run sweep** (or **Quick** /
**Thorough**). The page flies every planner on every variation for N seeds in your browser, draws the
race, and ranks the planners with 95 % Wilson intervals.

**SYNTHETIC SIMULATION, 2.5D POINT MASS. Scored on truth. Not a flight result.** Every run is the hub's
close-area arena ([samples/close-area-arena](../../samples/close-area-arena/README.md)) with a simulated
vehicle, range sensor and VIO. N seeds on one map is a small sample.

## How it works

| Part | File | What it does |
|---|---|---|
| Map | [solver.js](solver.js) | 8 presets from [../playground/presets/](../playground/presets/index.json), import a `close-area-world/1` JSON, open a link with `#w=`, or paste a playground link. Read-only preview. **Edit in playground** opens the current world in [the playground](../playground/README.md) via `#w=` |
| Sweep | [sweep.js](sweep.js) | Planners (from the worker's `ready` env.planners, all checked, playground labels), sensor presets ideal, crazyflie, depth_cam_87 and lidar_2d, **Your drone** (vehicle, sensor or Custom, yaw; below), VIO fault (truth only, or truth + one of none / jump / bias / dropout), seeds 0..N-1 (default 5), **Jitter A and B per seed** (default on, radius 0.25 / 0.5 / 1.0 m, default 0.5 m), **Run time limit** (Auto by map family, 60, 120 or 180 s). Shows the run count, a time estimate and the limit the map gets |
| Engine | [pool.js](pool.js) | K = min(4, `navigator.hardwareConcurrency` - 1), at least 1, ES-module workers of [../playground/worker.js](../playground/worker.js), unchanged. Each loads Pyodide once. One FIFO queue. Cancel terminates the pool |
| Race | [solver.js](solver.js) | All finished trajectories on one canvas, one colour per planner, legend with live counters. **Animate race** replays one variation + seed in sim time, with a timeline slider |
| Result | [sweep.js](sweep.js), [solver.js](solver.js) | Ranking, headline, planner x variation matrix, cell details, CSV / JSON export, share link, **Recommend** ([recommend.js](recommend.js), section Recommend) |

Details:

- **Start/goal jitter.** With the ideal sensor and truth pose a deterministic planner flies the identical
  run on every seed (the old Quick file had A* + ESDF known map at 19.38 s, 0.5647 m on seeds 0, 1 and 2).
  So seed 0 flies the exact map, and seed k > 0 moves A and B by a pseudo-random offset, uniform in a disc
  of the chosen radius (mulberry32 PRNG seeded from k, in sweep.js `seedJitter`). The offsets depend only
  on the world, the seed and the radius: every planner, sensor preset and fault flies the same A and B for
  a seed, so planners stay comparable. A draw is rejected if it is inside an obstacle, closer than the
  vehicle radius (`radius` in the world, else 0.15 m) + 0.1 m to any obstacle surface or to the bounds
  (the arena treats the bounds as walls), or outside the bounds. After 50 rejected draws the exact point is
  kept and recorded (`a_kept` / `b_kept`, a note under the pool line). The page edits a copy of the world
  dict (`a`, `b`) before posting the run; [worker.js](../playground/worker.js) is unchanged and re-centres
  on A as before. Each record carries the `a` and `b` it flew; the JSON export has `jitter.per_seed`, the CSV
  has `a_x, a_y, b_x, b_y`. The race view draws A and B of the chosen seed and a small + at the exact map's
  A and B. Jitter off => every seed flies the exact map. The setting is in the share link (`jitter=0.5`,
  `jitter=0` = off).
- **Identical runs.** Within a cell (planner x variation), two runs are identical when outcome, time to B
  and path length rounded to 3 dp match. `n` counts every run, `n_distinct` the distinct ones. Identical
  runs count as one trial: the success rate and the Wilson interval are computed on the distinct runs
  (distinct runs that reached B / n_distinct). The cell then shows "n=3, 1 distinct" and
  "deterministic: k identical runs" (k = runs that have an identical twin). Error records are never
  collapsed: each error is its own failed trial. The pooled row keeps variations apart (the variation is
  part of the run signature).
- **Run time limit (loop-73b).** Seconds of sim time before a run ends as `timeout`. **Auto** (default) uses
  the benchmark's rule: [worker.js](../playground/worker.js) `max_time_for` copies
  `samples/close-area-benchmark/bench.py` `LONG_FAMILIES`, so maze and warehouse get 120 s and every other
  family 60 s (`run.DEFAULTS`). The rule reads the world's `family`: a preset edited in the playground keeps
  its family, a world drawn from "New empty" has family `custom` and gets 60 s, as does a world without a
  family (the select's tooltip says so). Under Auto the page sends no limit and the worker applies the rule;
  60 / 120 / 180 s is sent as `cfg.max_time_s` (the worker clamps any value to 10-300 s). Every result
  reports `max_time_s`, and the result header shows the limit the runs used, for example "Run time limit:
  120 s of sim time (Auto: maze family, as the benchmark)." The watchdog grows with the limit: 180 s wall
  per run at 60 s of sim time, 360 s at 120 s, 540 s at 180 s.
- **Run order.** `buildRuns` puts the seed outermost and the planner innermost, so all planners advance
  at the same pace and the race fills evenly.
- **Pool start.** The first worker starts alone; the other K-1 start when it is ready, so a cold load
  downloads the 22 MB once and the others read the browser cache. Runs start as soon as one worker is ready.
- **Errors.** A worker `error` message, a worker crash (`onerror`), a fatal load error with a run on it
  or no result within the watchdog time (180 s, scaled with the run time limit; the worker is replaced) all end the run with outcome `error`.
  An error counts in n as not reached. The legend and the cell details show error counts and messages.
  Cancelled runs are not results: the progress line says how many were not run.
- **Cell.** Success rate = distinct runs that reached B / n_distinct, with its 95 % Wilson score interval
  (z = 1.96) on n_distinct, n (and n_distinct when smaller), and the median time to B over all runs that
  reached it (duplicates included). Click => median path length, lowest min clearance,
  collision rate, mean wall time per run, and the race view switches to that variation.
- **Ranking.** Pooled over all variations of the sweep. Order: success rate, then median time to B,
  then planner id.
- **Headline.** Uses the same distinct-run intervals. If the best planner's Wilson interval overlaps the
  runner-up's, it says "No clear winner: A and B are within noise on this map (n=..)". Otherwise it names the
  winner with both intervals. If no planner reached B, it says so. When identical runs were collapsed, the n
  reads "n=3, 1 distinct" and the headline adds "Identical runs count once in the interval."
- **Estimate.** Before the first results it uses a prior per planner (browser Python seconds from the
  [playground README](../playground/README.md)). After that it uses the mean worker time per planner
  measured in this browser, summed over the remaining runs and divided by K. The pool's load time is not included.
- **Quick** = 3 seeds, ideal only, truth pose only, then runs. **Thorough** = 10 seeds, ideal + crazyflie,
  keeps the fault choice, then runs. Neither changes the planner selection or the jitter setting.
- **Share link.** `index.html?planners=..&presets=..&fault=..&seeds=..&jitter=..&tlim=auto|60|120|180&src=<preset>#w=<world>`.
  A link without `tlim` opens with Auto. The world
  is coded the playground way (deflate + base64url, code copied into sweep.js, playground.js is not
  imported). Results are not in the link. `?map=<preset>` opens a preset directly; `?pyodide=cdn|local|auto`
  is passed to the worker.
- **Exports.** CSV: one row per run, with the A and B it flew and `max_time_s`. JSON (`navidx-solver-sweep/1`): spec (incl.
  `jitter` and `time_limit`), records (incl. `a`, `b`, `max_time_s`), `time_limit` (choice, expected and
  used limits, the family table), jitter (radius, minimum clearance, per-seed A/B), ranking and matrix
  (incl. `n_distinct`, `identical`), headline, the exact world, worker env, pool size and timings. Trajectories are not exported.
- Safety filter is always `none`, VIO loss recovery `none` (the playground covers those).

## How to add a planner

Add it to `PLANNERS` in `DRIVER_PY` in [../playground/worker.js](../playground/worker.js) (and its files
to [../playground/manifest.json](../playground/manifest.json)). The worker lists it in `env.planners`, and
the Solver shows it automatically. Add a label to `PLANNER_LABELS` in [sweep.js](sweep.js) to get a
readable name instead of the id, and a time to `PRIOR_WALL_S` for the first estimate. Colours are taken by
position in `env.planners` (12 colours, then they repeat; with the 18 planners since loop-73, planners 13-18
reuse the first 6 colours).

## Result: one real Quick sweep on random_0, jitter on

Source: [results/quick_random_0.json](results/quick_random_0.json) (exported by the page with
`SOLVER.exportJSON()`, the function behind **Export JSON**) and
[results/solver_check.json](results/solver_check.json), both written by
[results/measure_solver.mjs](results/measure_solver.mjs) in headless Chrome 140 on an Apple M3 Max
(16 cores, shared host, load average 14 / 53 / 75). Input type: synthetic.

- Quick = 12 planners x ideal x truth pose x 3 seeds = **36 runs, 36 done, 0 errors, 12.0 s** on K = 4
  workers, jitter on (default 0.5 m). Python ready 6.8 s after navigation (fresh profile).
- A and B per seed (synthetic): seed 0 exact, A (0, 0), B (16.404, 16.747); seed 1 A (-0.060, 0.387),
  B (16.098, 16.538); seed 2 A (-0.108, 0.278), B (16.075, 16.756). Each took 1 draw (no rejection, no
  exact point kept).
- 33 reached B, 3 stuck (all 3 are `straight`). All 36 runs are distinct (n_distinct = n = 3 in every cell),
  so no cell is marked deterministic.
- Headline: **No clear winner**: D* Lite, unknown map (geofenced) and A* + ESDF, unknown map are within
  noise on this map (n=3). 11 planners reached B 3/3 (95 % Wilson 44-100 %); straight 0/3 (0-56 %).
  With 3 seeds per planner, no ranking among the 11 is significant.
- Ranking by median time to B (synthetic): D* Lite 18.66 s, A* unknown map 18.70 s, A* known map 18.94 s,
  TangentBug 24.16 s, ..., DWA + 3 s memory 44.84 s.
- Against the previous file (jitter off, same map, 36 runs, not kept): the headline named the same pair in
  the other order (A* unknown map 18.68 s, D* Lite 18.72 s). Recomputed with duplicate collapsing, that old
  file had A* known map and Informed RRT* at 1 distinct run of 3 (95 % Wilson 21-100 %) and straight at 2 of
  3: those seeds were not independent trials. With jitter on, every cell has 3 distinct runs.
- Cross-check: seed 0 is the exact map, and A* + ESDF known map gives 19.38 s to B and 0.5647 m min clearance
  there, the same as the browser = native case in [the playground README](../playground/README.md)
  (random_0, seed 0).
- Time estimate: before the sweep, the prior said about 13 s for the default 60 runs. Treat it as rough;
  earlier runs of the same script under host load around 60 took 23.8 s and 25.0 s.
- 390 px phone viewport (dark theme): `scrollWidth` 390 = viewport width, no horizontal scroll.
- Share link: 748 characters; reopening it restored the identical world (`random_0`), the 12 planners,
  3 seeds, the ideal preset and jitter on at 0.5 m.
- Cancel: started a 36-run sweep, cancelled after the first result: progress showed "1/36, cancelled: 35
  runs not run", and a new pool started.
- No console errors or warnings.

Screenshots (viewport only): [desktop result matrix](results/solver_matrix_desktop.png) (1280 x 900,
light), [race mid-animation](results/solver_race_mid.png) (random_0, ideal, seed 1 with jittered A and B,
at 22.8 s of 45.6 s, 12 runs), [phone 390 px](results/solver_phone_390.png) (390 x 844 at 2x, dark).

Re-run (Chrome at the macOS default path or `CHROME=...`, network for cdn.jsdelivr.net):

```sh
node site/solver/results/measure_solver.mjs     # about 1 minute
node --test site/solver/test_sweep.mjs          # sweep.js unit tests, plain node
```

## Result: one Quick sweep on maze_0, 18 planners, benchmark time limit (loop-73b)

Source: [results/quick_maze_0.json](results/quick_maze_0.json) (`SOLVER.exportJSON()`) and
[results/solver_check_maze_0.json](results/solver_check_maze_0.json), written by
[results/measure_solver_maze.mjs](results/measure_solver_maze.mjs) (a copy of measure_solver.mjs with only
the sweep step) in headless Chrome 140 on an Apple M3 Max (16 cores, shared host, load average 51.9 at the
start). Input type: synthetic.

- Run time limit **Auto => 120 s** (maze family, as the benchmark). Every record has `max_time_s` 120, and
  the result header read "Run time limit: 120 s of sim time (Auto: maze family, as the benchmark)."
- The worker lists **18 planners** (the 12 above plus Theta* known map, Lazy Theta* known map, Lazy
  Theta* unknown map, MPPI goal only, MPPI on the unknown-map A* path, Hybrid A*; see the
  [playground README](../playground/README.md)).
- Quick = 18 planners x ideal x truth pose x 3 seeds = **54 runs, 54 done, 0 errors, 82.9 s** on K = 4
  workers, jitter on (0.5 m). Python ready 6.1 s after navigation.
- Headline (unchanged): **No clear winner**: MPPI on the unknown-map A* path and Theta* (any-angle), known
  map are within noise on this map (n=3). 9 planners reached B 3/3 (95 % Wilson 44-100 %), Bug2 1/3
  (6-79 %), the other 8 0/3.
- Ranking by median time to B (synthetic): MPPI + A* 31.28 s, Theta* known 31.44 s, Lazy Theta* known
  31.48 s, Lazy Theta* unknown 34.16 s, Hybrid A* 39.26 s, A* known 40.92 s, D* Lite 44.9 s, A* unknown
  48.7 s, Informed RRT* 69.7 s, Bug2 105.22 s.
- Outcomes: 28 reached, 23 stuck, 3 timeout (were 24 / 23 / 7 at the old 60 s limit). Changed runs:
  Informed RRT* seeds 0, 1, 2 timeout => reached (69.7 s, 68.66 s, 75.38 s); Bug2 seed 0 timeout =>
  reached (105.22 s). Still timeout at 120 s: Bug2 seeds 1 and 2, TangentBug seed 2.
- Cross-check: seed 0 is the exact map. A* known (41.26 s), Bug2 (105.22 s), Informed RRT* (69.7 s),
  Theta* known (31.88 s) and MPPI + A* (31.28 s) give the same time to B as the browser = native cases on
  maze_0 in [playground_loop73b.md](../playground/results/playground_loop73b.md), and as the benchmark's
  `matrix_0.json` maze rows (layout 0, seed 0, ideal).
- Slowest run in the worker: Lazy Theta* unknown map, 30.7 s (watchdog 360 s at the 120 s limit).

## Your drone (loop-76)

A collapsible **Your drone** panel in the Sweep section. Input type of every run: synthetic.

- **Vehicle** (every run): radius, v_max, a_max, with the arena defaults shown (run.DEFAULTS: 0.15 m,
  2 m/s, 3 m/s^2; tau 0.15 s is kept and not editable). Values are clamped to the worker's `VEHICLE_CLAMP`.
  The page sends `cfg.vehicle` only when it differs from the default. The start/goal jitter keeps the larger
  of the world's and the vehicle's radius + 0.1 m from every surface.
- **Sensor**: any preset name or **Custom** (beams, FoV, max range, min range, noise; defaults = the
  depth_cam_87 numbers). A preset name checks that preset. Custom is one more variation key, `custom`,
  next to the checked presets, labelled for example "custom 30 beams 87 deg 5 m". It is sent as
  `cfg.sensor` (no `cfg.preset`); cone 0 deg and dropout 0.02 come from the worker defaults
  (presets.py `SENSOR_SPEC_DEFAULTS`). The preset multi-select now also offers depth_cam_87 (30 beams, 87 deg
  forward, 0.3-5 m) and lidar_2d (360 beams, 0.15-12 m), specs copied from
  [presets.py](../../samples/close-area-arena/presets.py) into `PRESET_SPECS` in sweep.js.
- **Yaw**: fixed (default) or look where you go. Sent as `cfg.yaw` only when not fixed (the interface another
  job is adding to the worker). Each record stores the asked `yaw` and the `yaw_policy` the worker reported.
- **Quick** = 3 seeds, the drone's sensor only (ideal by default, Custom => the custom variation alone).
  **Thorough** = 10 seeds, ideal + crazyflie + the drone's sensor.
- **Records and exports.** Every record has `vehicle`, `sensor` (the custom dict, or the preset's spec),
  `yaw`, `yaw_policy`. CSV adds `sensor_label`, `sensor_beams`, `sensor_fov_deg`, `sensor_max_range_m`,
  `sensor_min_range_m`, `sensor_noise_sigma_m`, `vehicle_radius_m`, `vehicle_v_max`, `vehicle_a_max`,
  `vehicle_tau`, `yaw`, `yaw_policy`. JSON adds `spec.vehicle / sensor_choice / sensor / yaw` and a `drone`
  block (asked vs default, sent or not, yaw policies flown, sensor spec per variation).
- **Share link** adds `veh=radius_m,v_max,a_max,tau`, `sensor=<preset>|custom`,
  `cs=beams,fov_deg,max_range_m,min_range_m,noise_sigma_m` (Custom only) and `yaw=look_where_you_go`
  (only when not fixed). Links without them open with the defaults.
- **Estimate.** The prior per planner is scaled by beams / 72 (the priors were measured on the 72-beam ideal
  sensor), at least x 0.25 [proposal]. Times measured in this browser are used unscaled.

### Result: one Quick sweep on office_0 with depth_cam_87

Source: [results/quick_office_0_depth_cam.json](results/quick_office_0_depth_cam.json) (`SOLVER.exportJSON()`)
and [results/solver_check_drone.json](results/solver_check_drone.json), written by
[results/measure_solver_drone.mjs](results/measure_solver_drone.mjs) (a copy of measure_solver_maze.mjs that
picks depth_cam_87 in the panel, then presses Quick) in headless Chrome 140 on an Apple M3 Max (16 cores,
shared host, load average 45.0 at the start). Input type: synthetic.

- Quick = 18 planners x depth_cam_87 x truth pose x 3 seeds = **54 runs, 54 done, 0 errors, 17.5 s** on K = 4
  workers, jitter on (0.5 m), run time limit Auto => 60 s (office family). Arena default vehicle (not sent).
  Re-run by the loop driver after loop-75b landed: yaw fixed (not sent), the worker reports yaw policy
  `off` on all 54 runs, and `astar_unknown` is geofenced.
- Outcomes: 25 reached, 26 stuck, 2 collision, 1 timeout.
- Headline: **No clear winner**: MPPI on the unknown-map A* path and Lazy Theta*, known map are within
  noise on this map (n=3).
- Ranking (synthetic, reached of 3, 95 % Wilson 44-100 % each, median time to B): MPPI + A* 14.62 s; Lazy
  Theta* known 19.74 s; Theta* known 19.92 s; Hybrid A* 20.14 s; A* + ESDF known 23.1 s; A* + ESDF unknown
  25.14 s; D* Lite 25.5 s; Informed RRT* 26.18 s. Lazy Theta* unknown 1/3 (6-79 %); the other 9 planners
  0/3. The earlier run of this page (look-where-you-go yaw, ungeofenced A* unknown) had 17 reached and 9
  collisions: holding yaw toward B and geofencing A* both helped here.
- 390 px phone viewport with the panel open on Custom: `scrollWidth` 390 = viewport width, no horizontal
  scroll. Screenshot (viewport only): [results/solver_drone_390.png](results/solver_drone_390.png) (390 x 844 at 2x).
- Share link round trip (no sweep after the reload): radius 0.25, v_max 1.5, Custom 24 beams 120 deg 4 m and
  yaw look_where_you_go were restored, and the panel opened.
- No console errors or warnings.

## Recommend (loop-80)

**Recommend** (Result section, next to Export JSON) downloads `recommend.md` and `recommend.json`: the
sweep turned into something to paste into the team repo and the pitch. Logic in
[recommend.js](recommend.js) (pure, unit tested), input = the same doc as Export JSON plus
[../playground/data/advisor.json](../playground/data/advisor.json).

| Part | What it says |
|---|---|
| Pick | Headline winner (or the only planner run) with the runner-up row; on "No clear winner" the tied set = every planner whose 95 % Wilson interval overlaps the best one's; on "No planner reached B" every row plus up to 5 "what to try next" items (time limit if runs timed out, Thorough, the benchmark's best for the map family and whether it was in the sweep, a map check when no route is wide enough). Rows: reached, interval, n, n distinct, median time to B, min clearance, collisions |
| Fly it | `make first-flight PLANNER=bench:<id> WORLD=<file.json> ARM=<F0\|F2>` for templates/flight-repo ([section "Fly what the Solver picks"](../../templates/flight-repo/README.md)). The id is the benchmark id (`advisor.json` planners, e.g. Solver `apf` => `bench:apf_escape`). On "none" the command flies the benchmark's best map-free planner for the family, marked untested on this map |
| ARM | F2 by default. F0, with a warning (no safety filter), when the narrowest passage is below 1.4 m: F2 holds the centre 0.7 m (eps) from every return ([flight-repo first_flight_bench.txt](../../templates/flight-repo/results/first_flight_bench.txt): narrow_gap_0, F2 stuck, F0 reached) |
| World file | A preset => `../../site/playground/presets/<name>.json` (relative to templates/flight-repo). A custom world => `my_world.json`, with a one-line python command that saves it from `recommend.json` (the world is inline there) |
| What flew | Vehicle, sensors, variations, yaw asked and reported, jitter, run time limit, seeds, run count; the synthetic caveat; and what the command flies instead (run.DEFAULTS vehicle and ideal sensor, truth pose, seed 0, exact A and B) |
| Benchmark | The pick's reached % / collision % per family, ideal and crazyflie, from advisor.json (matrix_0, 20 layouts per family, seed 0, true pose); on a tie also each tied planner on this map's family |

Narrowest passage: 2 x the bottleneck clearance of the best route A=>B on a 0.05 m ESDF grid of the world
(`narrowestPassage`: clearance at every cell centre, maximin Dijkstra, cells within 0.7 m of A count as
free, goal = any cell within 0.2 m of B). This is computed from the world, not from a run. The cheaper
proxy (2 x the winning runs' min clearance) was rejected: min clearance is the closest approach to any
surface, so a planner cutting a corner in open space reads narrow. In
[results/quick_random_0.json](results/quick_random_0.json) D* Lite's 0.583 m gives 1.17 m (=> F0) on a map
whose best route never narrows below 3.60 m. Measured on the presets (node, 46-289 ms each): narrow_gap_0
0.72 m (the gap from the two wall boxes is 0.764 m; the grid under-reads by 0.046 m), office_0 0.90 m,
glass_office_0 0.82 m => F0; random_0 3.60 m, u_trap_0 3.15 m, forest_0 1.78 m, maze_0 1.55 m,
warehouse_0 1.45 m => F2. warehouse_0 is 0.05 m above the threshold, inside the grid error.

### Result: Quick sweeps on narrow_gap_0 and random_0, then the flight

`node site/solver/results/measure_recommend.mjs` (copy of measure_solver.mjs, headless Chrome 140,
4 workers, 18 planners x 3 seeds = 54 runs per map, jitter 0.5 m, ideal, truth pose, load average about 23
on 16 cores; [results/recommend_check.json](results/recommend_check.json)). Synthetic.

| Map | Sweep | Headline | Pick | Narrowest passage | ARM | File |
|---|---|---|---|---|---|---|
| narrow_gap_0 | 38.5 s | No clear winner: MPPI on the unknown-map A* path and MPPI, goal only | tied set of 18 (14 at 3/3, 4 at 0/3), first `mppi_astar` 3/3, 44-100 %, median 21.22 s | 0.72 m | F0 + warning | [recommend_narrow_gap_0.md](results/recommend_narrow_gap_0.md), [.json](results/recommend_narrow_gap_0.json), sweep [quick_narrow_gap_0_loop80.json](results/quick_narrow_gap_0_loop80.json) |
| random_0 | 28.9 s | No clear winner: Theta* (any-angle), known map and Lazy Theta*, known map | tied set of 18 (17 at 3/3, `straight` 0/3), first `thetastar_known` 3/3, 44-100 %, median 16.82 s | 3.60 m | F2 | [recommend_random_0.md](results/recommend_random_0.md), [.json](results/recommend_random_0.json), sweep [quick_random_0_loop80.json](results/quick_random_0_loop80.json) |

With 3 seeds, 3/3 (44-100 %) overlaps 0/3 (0-56 %), so the tied set is every planner run: Quick cannot
separate them. Read the benchmark rows below the table (e.g. `mppi` is 25 % reached on narrow_gap in
the benchmark, ideal sensor, vs 95 % for `mppi_astar`).

The narrow_gap_0 command, run once in templates/flight-repo (its `./.venv`, built by this make, uv
CPython 3.11.15, numpy 2.4.6, scipy 1.17.1; `OUT=` pointed the log to /tmp so nothing was added under
templates/), from [results/recommend_narrow_gap_0_flight.txt](results/recommend_narrow_gap_0_flight.txt):

```
score input=synthetic adapter=world:../../site/playground/presets/narrow_gap_0.json fault=truth planner=bench:mppi_astar safety=arm:F0 reached=True final_dist_m=0.178 t_s=23.26 collided=False min_clearance_m=0.258 max_pose_error_m=0.000 ticks=466 intervened=0 keepalive=29 planner_errors=0 outcome=arrived modes=arrive_dwell:20,arrived:1,nominal:445 health=ok:466 log=/tmp/loop80_flight/first_flight_bench_mppi_astar_narrow_gap_0.jsonl
```

score_log.py: reached, 21.76 s to goal, min clearance 0.2579 m at (10.443, 7.182), in the gap. The
Solver's seed 0..2 runs gave a 21.22 s median and 0.261 m min clearance (10 Hz planner in the worker,
jittered A and B on seeds 1-2). keepalive=29: 29 ticks reused the previous setpoint under the 30 ms
planner budget on a loaded machine, so this run end is wall-clock dependent.

Not verified: the button itself was not clicked (the script calls `SOLVER.recommend()`, the function
behind it; two downloads from one click may make Chrome ask to allow multiple downloads); the "none"
and "winner" texts ran in unit tests only, not in a browser; the random_0 command and ARM=F2 on
narrow_gap_0 were not flown here; the custom-world `my_world.json` command was not run.

## Limits and not verified

- One map, 3 seeds, ideal sensor, truth pose: a small sample. On random_0 the Quick sweep cannot separate
  11 of the 12 planners.
- Jitter makes seeds sample start and goal positions within 0.25 to 1.0 m of the map's A and B, not other
  maps. A jittered map is a nearby variant of the same layout, so its runs are correlated with the others;
  the Wilson interval still treats distinct runs as independent.
- Duplicate detection only catches exact repeats (3 dp). Two runs that differ by 1 mm count as two trials.
  With jitter off, many planners repeat the identical run on every seed; those collapse to one trial.
- The duplicate marker and jitter-off path are unit tested in [test_sweep.mjs](test_sweep.mjs); the recorded
  browser run had jitter on and no duplicates, so the "deterministic" marker was not seen in a browser.
- Jittered A or B can change whether the world has a free path; the worker reports `free_path` per run, the
  Solver does not show it.
- Verified in headless Chrome 140 only. Firefox, Safari, real phones and touch were not tried.
  `CompressionStream` (share link) needs Chrome 80+, Firefox 113+, Safari 16.4+.
- Run time limit: only Auto on maze_0 ran in a browser. The fixed 60 / 120 / 180 s choices, the
  `tlim=` share link and the CSV / JSON fields are unit tested in [test_sweep.mjs](test_sweep.mjs) only;
  the scaled watchdog was not triggered.
- Not run by the script: Thorough, crazyflie preset, any VIO fault, import from a file, paste of a
  playground link (the codec is unit tested, the form was not clicked), CSV and JSON downloads through
  the buttons (the JSON comes from the same function), the 180 s watchdog and the worker-crash path
  (the error path is unit tested in sweep.js only).
- Your drone (loop-76): only the depth_cam_87 Quick sweep ran. No browser sweep used a custom vehicle, the
  Custom sensor, lidar_2d or `yaw=look_where_you_go`; `cfg.yaw` and planners honouring `vehicle.radius_m`
  depend on a worker change that was not in this checkout. Those paths are unit tested in sweep.js only.
- K workers each hold a Pyodide heap (the playground README measured 90 MB of wasm heap per runtime).
  4 workers on a small phone were not tried.
- Each worker is a separate Pyodide: per-run wall times are measured under the load of K parallel
  workers, so they are higher than in the playground.
- Not a flight result. Scored on truth by `scorer.score`.
