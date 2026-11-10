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
| Sweep | [sweep.js](sweep.js) | Planners (from the worker's `ready` env.planners, all checked, playground labels), sensor presets ideal and crazyflie, VIO fault (truth only, or truth + one of none / jump / bias / dropout), seeds 0..N-1 (default 5). Shows the run count and a time estimate |
| Engine | [pool.js](pool.js) | K = min(4, `navigator.hardwareConcurrency` - 1), at least 1, ES-module workers of [../playground/worker.js](../playground/worker.js), unchanged. Each loads Pyodide once. One FIFO queue. Cancel terminates the pool |
| Race | [solver.js](solver.js) | All finished trajectories on one canvas, one colour per planner, legend with live counters. **Animate race** replays one variation + seed in sim time, with a timeline slider |
| Result | [sweep.js](sweep.js), [solver.js](solver.js) | Ranking, headline, planner x variation matrix, cell details, CSV / JSON export, share link |

Details:

- **Run order.** `buildRuns` puts the seed outermost and the planner innermost, so all planners advance
  at the same pace and the race fills evenly.
- **Pool start.** The first worker starts alone; the other K-1 start when it is ready, so a cold load
  downloads the 22 MB once and the others read the browser cache. Runs start as soon as one worker is ready.
- **Errors.** A worker `error` message, a worker crash (`onerror`), a fatal load error with a run on it
  or no result within 180 s (watchdog, the worker is replaced) all end the run with outcome `error`.
  An error counts in n as not reached. The legend and the cell details show error counts and messages.
  Cancelled runs are not results: the progress line says how many were not run.
- **Cell.** Success rate = reached B / n, with its 95 % Wilson score interval (z = 1.96), n, and the
  median time to B over the runs that reached it. Click => median path length, lowest min clearance,
  collision rate, mean wall time per run, and the race view switches to that variation.
- **Ranking.** Pooled over all variations of the sweep. Order: success rate, then median time to B,
  then planner id.
- **Headline.** If the best planner's Wilson interval overlaps the runner-up's, it says
  "No clear winner: A and B are within noise on this map (n=..)". Otherwise it names the winner with both
  intervals. If no planner reached B, it says so.
- **Estimate.** Before the first results it uses a prior per planner (browser Python seconds from the
  [playground README](../playground/README.md)). After that it uses the mean worker time per planner
  measured in this browser, summed over the remaining runs and divided by K. The pool's load time is not included.
- **Quick** = 3 seeds, ideal only, truth pose only, then runs. **Thorough** = 10 seeds, ideal + crazyflie,
  keeps the fault choice, then runs. Neither changes the planner selection.
- **Share link.** `index.html?planners=..&presets=..&fault=..&seeds=..&src=<preset>#w=<world>`. The world
  is coded the playground way (deflate + base64url, code copied into sweep.js, playground.js is not
  imported). Results are not in the link. `?map=<preset>` opens a preset directly; `?pyodide=cdn|local|auto`
  is passed to the worker.
- **Exports.** CSV: one row per run. JSON (`navidx-solver-sweep/1`): spec, records, ranking, matrix,
  headline, world, worker env, pool size and timings. Trajectories are not exported.
- Safety filter is always `none`, VIO loss recovery `none` (the playground covers those).

## How to add a planner

Add it to `PLANNERS` in `DRIVER_PY` in [../playground/worker.js](../playground/worker.js) (and its files
to [../playground/manifest.json](../playground/manifest.json)). The worker lists it in `env.planners`, and
the Solver shows it automatically. Add a label to `PLANNER_LABELS` in [sweep.js](sweep.js) to get a
readable name instead of the id, and a time to `PRIOR_WALL_S` for the first estimate. Colours are taken by
position in `env.planners` (12 colours, then they repeat).

## Result: one real Quick sweep on random_0

Source: [results/quick_random_0.json](results/quick_random_0.json) (exported by the page with
`SOLVER.exportJSON()`, the function behind **Export JSON**) and
[results/solver_check.json](results/solver_check.json), both written by
[results/measure_solver.mjs](results/measure_solver.mjs) in headless Chrome 140 on an Apple M3 Max
(16 cores, shared host, load average 83 / 70 / 51). Input type: synthetic.

- Quick = 12 planners x ideal x truth pose x 3 seeds = **36 runs, 36 done, 0 errors, 12.0 s** on K = 4
  workers. Python ready 6.4 s after navigation (fresh profile).
- 33 reached B, 3 stuck (all 3 are `straight`).
- Headline: **No clear winner**: A* + ESDF, unknown map and D* Lite, unknown map (geofenced) are within
  noise on this map (n=3). 11 planners reached B 3/3 (95 % Wilson 44-100 %); straight 0/3 (0-56 %).
  With 3 seeds per planner, no ranking among the 11 is significant.
- Ranking by median time to B: A* unknown map 18.68 s, D* Lite 18.72 s, A* known map 19.38 s, TangentBug
  25.36 s, ..., DWA + 3 s memory 47.3 s.
- Cross-check: A* + ESDF known map gives 19.38 s to B and 0.5647 m min clearance here, the same as the
  browser = native case in [the playground README](../playground/README.md) (random_0, seed 0).
- Time estimate: before the sweep, the prior said about 13 s for the default 60 runs; after it, the measured
  per-planner times gave about 10 s for the 36 runs, against 12.0 s measured. In two earlier runs of
  the same script (not kept, host load around 60), the same sweep took 23.8 s and 25.0 s. Treat the estimate as rough.
- 390 px phone viewport (dark theme): `scrollWidth` 390 = viewport width, no horizontal scroll. The matrix
  scrolls inside its own box if it gets wider than the screen.
- Share link: 737 characters; reopening it restored the identical world (`random_0`), the 12 planners,
  3 seeds and the ideal preset.
- Cancel: started a 36-run sweep, cancelled after the first result: progress showed "1/36, cancelled: 35
  runs not run", and a new pool started.
- No console errors or warnings.

Screenshots (viewport only): [desktop result matrix](results/solver_matrix_desktop.png) (1280 x 900,
light), [race mid-animation](results/solver_race_mid.png) (random_0, ideal, seed 0, at 23.6 s of
47.3 s, 12 runs), [phone 390 px](results/solver_phone_390.png) (390 x 844 at 2x, dark).

Re-run (Chrome at the macOS default path or `CHROME=...`, network for cdn.jsdelivr.net):

```sh
node site/solver/results/measure_solver.mjs     # about 1 minute
node --test site/solver/test_sweep.mjs          # sweep.js unit tests, plain node
```

## Limits and not verified

- One map, 3 seeds, ideal sensor, truth pose: a small sample. On random_0 the Quick sweep cannot separate
  11 of the 12 planners.
- With truth pose, the seed only changes the sensor noise. Many planners give the same result on every seed,
  so the n seeds are not fully independent trials. The Wilson interval assumes they are.
- Verified in headless Chrome 140 only. Firefox, Safari, real phones and touch were not tried.
  `CompressionStream` (share link) needs Chrome 80+, Firefox 113+, Safari 16.4+.
- Not run by the script: Thorough, crazyflie preset, any VIO fault, import from a file, paste of a
  playground link (the codec is unit tested, the form was not clicked), CSV and JSON downloads through
  the buttons (the JSON comes from the same function), the 180 s watchdog and the worker-crash path
  (the error path is unit tested in sweep.js only).
- K workers each hold a Pyodide heap (the playground README measured 90 MB of wasm heap per runtime).
  4 workers on a small phone were not tried.
- Each worker is a separate Pyodide: per-run wall times are measured under the load of K parallel
  workers, so they are higher than in the playground.
- Not a flight result. Scored on truth by `scorer.score`.
