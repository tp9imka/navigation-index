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
| Sweep | [sweep.js](sweep.js) | Planners (from the worker's `ready` env.planners, all checked, playground labels), sensor presets ideal and crazyflie, VIO fault (truth only, or truth + one of none / jump / bias / dropout), seeds 0..N-1 (default 5), **Jitter A and B per seed** (default on, radius 0.25 / 0.5 / 1.0 m, default 0.5 m), **Run time limit** (Auto by map family, 60, 120 or 180 s). Shows the run count, a time estimate and the limit the map gets |
| Engine | [pool.js](pool.js) | K = min(4, `navigator.hardwareConcurrency` - 1), at least 1, ES-module workers of [../playground/worker.js](../playground/worker.js), unchanged. Each loads Pyodide once. One FIFO queue. Cancel terminates the pool |
| Race | [solver.js](solver.js) | All finished trajectories on one canvas, one colour per planner, legend with live counters. **Animate race** replays one variation + seed in sim time, with a timeline slider |
| Result | [sweep.js](sweep.js), [solver.js](solver.js) | Ranking, headline, planner x variation matrix, cell details, CSV / JSON export, share link |

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
- K workers each hold a Pyodide heap (the playground README measured 90 MB of wasm heap per runtime).
  4 workers on a small phone were not tried.
- Each worker is a separate Pyodide: per-run wall times are measured under the load of K parallel
  workers, so they are higher than in the playground.
- Not a flight result. Scored on truth by `scorer.score`.
