# Arena playground: the close-area arena in the browser (Pyodide)

Open [index.html](index.html) (served from the repo root: `python3 -m http.server 8000`, then
`http://localhost:8000/site/playground/`). Draw or load an arena, drag A and B, pick a planner,
sensor preset, VIO fault and safety filter, press Run, and watch the replay with a score panel.
Press **Copy link** to share the world and config: opening the link restores both and runs.

The page runs the hub's real Python code with Pyodide in a Web Worker: the arena
([samples/close-area-arena](../../samples/close-area-arena/README.md)), APF and VFH+
([close-area-planner-reactive](../../samples/close-area-planner-reactive/README.md)), DWA, Bug2 and
TangentBug ([close-area-planner-dwa-bug](../../samples/close-area-planner-dwa-bug/README.md)), D* Lite
([close-area-planner-dstar](../../samples/close-area-planner-dstar/README.md)), Informed RRT*
([close-area-planner-sampling](../../samples/close-area-planner-sampling/README.md)) and the F2 filter
([close-area-safety-filter](../../samples/close-area-safety-filter/README.md)). Nothing is re-implemented
in JS. Everything is **synthetic**: a simulated 2.5D point-mass vehicle, simulated range sensors and
a simulated VIO. No number here is a flight result.

## Result

Source: [results/playground_check.md](results/playground_check.md), written by
`results/measure_playground.mjs` in headless Chrome 140 on an Apple M3 Max, against
[results/native_parity.json](results/native_parity.json) from `results/native_parity.py` (CPython 3.12.10).
Input type: synthetic.

- **12 planners in the browser: 12 of the 14 benchmarked rows** of
  [close-area-benchmark](../../samples/close-area-benchmark/README.md). Added in loop-62: DWA, DWA + 3 s
  memory, Bug2, TangentBug, D* Lite (unknown map) and Informed RRT* (known map). The 2 rows left out:
  `astar_mpc` needs osqp, and the Pyodide 314.0.7 `pyodide-lock.json` lists 357 packages but no osqp
  (only clarabel and cvxpy-base, checked 2026-11-09); `astar_unknown_f2` is not a separate planner
  here. A* unknown map + filter F2 is close to it, but differs: the benchmark's A* unknown map is
  geofenced, the playground's keeps the shipped map corner (see "What a run does").
- **Browser = native on 21/21 preset cases** (outcome, time to goal, duration, min clearance, path
  length; seed 0). Example: random_0, A* known map => reached in 19.38 s, min clearance 0.5647 m,
  path 23.838 m in both. The cases cover all 12 planners, all 3 sensor presets, faults none / jump /
  bias / dropout and F2. The 6 new planners, one preset each:

  | world | planner | outcome / time to goal s / min clearance m / path m (browser = native) | browser Python s | native Python s |
  |---|---|---|---|---|
  | random_0 | dwa | reached / 43.68 / 0.2682 / 24.261 | 1.018 | 0.601 |
  | u_trap_0 | dwa_mem | stuck (28.94 s) / - / 0.2757 / 12.447 | 2.383 | 1.5 |
  | office_0 | bug2 | stuck (28.94 s) / - / 0.4578 / 11.281 | 0.196 | 0.109 |
  | forest_0 | tangent_bug | reached / 25.68 / 0.3731 / 24.519 | 0.235 | 0.133 |
  | narrow_gap_0 | dstar_lite | reached / 24.52 / 0.3288 / 25.187 | 1.28 | 0.824 |
  | office_0 | informed_rrt_star | reached / 25.88 / 0.2762 / 13.578 | 0.82 | 0.434 |

- **Shareable link works in a fresh profile.** A hand-drawn world with compare mode (TangentBug vs
  D* Lite + F2, Crazyflie sensor, VIO on, seed 7) gave a 461-character link. A second headless Chrome
  with a new profile and cold cache opened it, restored the identical world and config, ran by
  itself, and got both scores identical to the source tab (A collision at 8.5 s, B reached in 28.4 s).
  The `w=` value is 426-1610 characters for the 8 presets (forest_0 is the longest, 6966 characters
  of JSON). The Copy link button put the link in the clipboard and the address bar. A broken `w=`
  shows a message and loads random_0.
- A box drawn with real pointer events on an empty world: A* known map and freest_beam give the same
  score in the browser and in native CPython on the saved [custom_world.json](results/custom_world.json).
- The page stays responsive: during a 2.9 s A* unknown-map run in the worker, the longest gap
  between animation frames was 10 ms.
- Cold load in a fresh profile: Python ready 5.7 s after the page script starts, 22.2 MB
  downloaded from cdn.jsdelivr.net. The load starts when the page opens, so it overlaps with drawing.
- 390 px wide phone viewport: no horizontal scroll, runs work.
- Screenshots (viewport only): [loading](results/pg_loading.png),
  [compare A* vs freest_beam](results/pg_compare_random0.png),
  [hand-drawn box](results/pg_custom_drawn.png), [shared link in a fresh profile](results/pg_shared_link.png), [VIO jump, no filter vs F2, dark theme](results/pg_jump_f2_dark.png),
  [phone 390 px](results/pg_phone_390.png).

The driver loop matches the arena's own loops, checked natively in `native_parity.py`
([native_parity.json](results/native_parity.json), 21/26 checks identical):

| check | identical |
|---|---|
| A: driver == `run.run_one` on the same JSON world (truth pose, ideal sensor), 8 cases of the first 6 planners | 8/8 |
| E: driver == `run.run_one` with the planner built by `close-area-benchmark/bench.py` `PLANNERS[name][0]` called with the world, same JSON world, 6 new planners | 6/6 |
| C: driver == `run.run_one` + `estimator.make_pose_source_factory(fault)` (the `run.evaluate` path) | 2/2 |
| D: driver with F2 == `close-area-safety-filter/run_kill.run_one("F2", case, unsensed off)` | 2/2 |
| B: driver on the preset JSON == `run.run_one` on `world.make_world` (no JSON) | 3/8 |

Information only: the 6 new cases against the benchmark's own rows in
`samples/close-area-benchmark/results/matrix_0.json` (generated worlds, preset ideal, layout 0):
5/6 identical, 6/6 same outcome. Informed RRT* on office_0 differs in min clearance only (0.2762 m
here, 0.2761 m in the matrix), the same 4-decimal JSON rounding as check B.

Check B is a real difference, not a bug in the playground: `world_json` rounds every number to 4
decimals (0.1 mm), and that is enough to move some runs a little. Example: straight on random_0
gives duration 20.3 s on the JSON world and 20.38 s on the generated world. So a playground score
equals the native score **on the same JSON world**, and can differ slightly from the published
`results/*.json` of the arena, which were run on generated worlds.

## What a run does

`worker.js` holds `DRIVER_PY`, about 260 lines of Python glue. It calls `world_json.from_json`,
`worlds_complex.has_free_path`, `presets.make_sensor`, `estimator.make_pose_source_factory`,
the planner `make()` functions, `filters.make("F2")` and `scorer.score`. Each planner is built the
way `close-area-benchmark/bench.py` builds it: the DWA / Bug, D* Lite and RRT* samples each import
their own `arena.py`, so they load with bench.py's recipe (folder on `sys.path` only while importing).
D* Lite gets the benchmark's geofence (log-odds map corner = area corner - 2 m). A* unknown map keeps
the shipped fixed map corner at (-2.5, -2.5), as before, so on a user-drawn world with B at negative
x or y it is clamped to the map edge and D* Lite is not. The loop is `run.run_one`
when the filter is off (pose at the 10 Hz planner rate), and `run_kill.run_one` when F2 is on (pose
and filter every 50 Hz step, a second sensor copy for the filter at 16.7 Hz, rng `[seed, index, 8]`).
The only additions are a sensor-preset argument and trace recording.

| Control | Options | Source |
|---|---|---|
| Planner | straight, freest_beam, A* + ESDF known map, A* + ESDF unknown map, APF, VFH+, DWA, DWA + 3 s scan memory, Bug2, TangentBug, D* Lite unknown map, Informed RRT* 5000 known map | `planners/`, `run_faults.FreestBeam`, `close-area-planner-reactive`, `close-area-planner-dwa-bug`, `close-area-planner-dstar`, `close-area-planner-sampling` |
| Sensor | ideal (72 rays, 6 m), crazyflie (4 cone beams, 3 m), crazyflie_bright (0.73 m) | `presets.py` |
| VIO fault | off (planner sees truth), VIO no fault, jump, bias, dropout | `estimator.py`, `faults.py`; the VIO options add 2 seeded dark zones |
| Filter | none, F2 (PX4-CBF as shipped, on ranges) | `close-area-safety-filter/filters.py` |
| Seed | 0-9999 | sensor noise, dark zones, fault timing |

Each run returns the 10 Hz trace (truth, estimate, sigma, quality, yaw, range scan), the planned
path snapshots, truth clearance, dark zones, the fault log and the scorer row. The replay draws
truth and estimate paths, the range beams, the planned path (A*, D* Lite, RRT*) and the vehicle at
its true 0.15 m size.
Compare mode runs config B on the same world and overlays it, with both columns in the score table.

## Editor

Tools: Move (drag obstacles, A or B), Box, Wall (axis-aligned, 0.1 m thick), Cylinder (drag the
radius), Glass (0.04 m wall, material glass: cone sensors do not see it, truth and the A* prior map
do). Snap 0.1 m, Undo (Ctrl+Z), Delete, material per obstacle. Presets: 8 worlds in
[presets/](presets/index.json) (office, warehouse, forest, maze, glass_office, random, u_trap,
narrow_gap; seed 0, layout 0), exported with `world_json.to_json` by `results/export_presets.py`.
Download / open `close-area-world/1` JSON, or keep one world in localStorage. Any edit clears the
replay, because the trace no longer matches the world. The area bounds of a preset cannot be
resized in the editor; "New empty" gives a 20 x 20 m area.

## Shareable link

**Copy link** builds `index.html?CONFIG#w=WORLD`, copies it and puts it in the address bar.

- `w=`: the `close-area-world/1` JSON, compressed with `CompressionStream("deflate")` (zlib) and
  base64url coded without padding.
- Query params: `planner`, `preset`, `fault`, `filter` for config A; the same with `_b` for config B
  and `compare=1` when compare is on; `seed`; `src=<preset>` when the world is an unedited preset
  (used only to show the native parity note, after checking the decoded world equals the preset file).
- Opening the link restores world and config and runs once Python is ready. Unknown param values
  are ignored with a message. Editing the world or loading another one removes the link from the
  address bar, so a reload does not bring back an old world.

## Files

| File | What |
|---|---|
| [index.html](index.html), [playground.css](playground.css), [playground.js](playground.js) | The page. Uses `../showcase.css` for the palette and light / dark theme. `window.PG` is a small API for scripted checks |
| [worker.js](worker.js) | ES module worker: loads Pyodide 314.0.7 (`pyodide.mjs`), numpy, scipy and the 30 files in the manifest once, then serves `run` messages |
| [manifest.json](manifest.json) | Pyodide pin, packages, files (shared with the spike) |
| [presets/](presets/index.json) | Preset world JSON |
| `results/export_presets.py`, `native_parity.py`, `measure_playground.mjs` | Export presets; native reference + loop parity; headless Chrome check, link check in a second fresh profile, and screenshots ([pg_shared_link.png](results/pg_shared_link.png)) |

Re-run (needs the arena venv, Chrome at the macOS default path, network for the CDN):

```sh
uv venv --python 3.12 samples/close-area-arena/.venv
uv pip install --python samples/close-area-arena/.venv -r samples/close-area-arena/requirements.txt
samples/close-area-arena/.venv/bin/python site/playground/results/export_presets.py
samples/close-area-arena/.venv/bin/python site/playground/results/native_parity.py   # about 1 minute
node site/playground/results/measure_playground.mjs                                  # about 3 minutes
```

Finding: `importScripts` of the CDN `pyodide.js` failed in a classic worker in Chrome 140
(NetworkError, while `fetch` of the same URL returned 200), and `pyodide.mjs` refuses classic
workers. The worker is therefore started with `{type: "module"}` and uses `import()`.

## Not verified (playground)

- GitHub Pages hosting. Only `python3 -m http.server` locally.
- Firefox and Safari, real phones and touch input. Only headless Chrome 140 with mouse events and
  a 390 x 844 emulated viewport.
- The shareable link was checked in Chrome only: `CompressionStream` needs Chrome 80+, Firefox 113+,
  Safari 16.4+ (not tried). Very long links (over about 8000 characters, for example a world with
  hundreds of obstacles) were not tried; some chat tools and servers cut long URLs.
- The 6 new planners have a native reference on one preset each, with the ideal sensor and truth
  pose. Other sensors, faults and F2 run through the same driver code but are not compared with
  native for them; the link check (TangentBug, D* Lite + F2) is browser vs browser only.
- Pointer drawing was checked for the Box tool only. Wall, Cylinder, Glass, Move, Undo, Delete,
  material change and file open / save / localStorage were not exercised by the scripted check.
- `spike.html` with the extended manifest (it now also writes the 19 extra files) was not re-run.
- Worlds much larger than 20 x 20 m, and runs near the 60 s limit with A* unknown map. Estimate,
  not measured: browser Python ran about 2x slower than native in the check, so such a run would
  take about 10 s.
- Real or SITL flight: everything is the synthetic arena.

# Spike (loop-48a): can the arena run in the browser?

Feasibility spike for a browser playground (draw an arena, place A and B, pick a planner, watch
it fly). Question: can the hub's real Python arena and planners
([samples/close-area-arena](../../samples/close-area-arena/README.md)) run in the browser fast
enough, so the playground and the benchmarks share one implementation?

### Verdict

**Yes, PASS.** A projected 30 s run takes 0.1-1.0 s of wall time for `straight` and
`astar_esdf` (known map), and 4.6-5.9 s for `astar_esdf` with an unknown map. The target was
under 15 s. The browser gives the same scores as native CPython on all 6 measured cases. Source:
[results/spike_timing.md](results/spike_timing.md). Input type: synthetic (simulated layouts,
vehicle and range sensor), measured in headless Chrome 140 on an Apple M3 Max.

The real cost is page load. Cold cache, the page is ready 4.9 s after navigation and downloads
22.0 MB from cdn.jsdelivr.net. The scipy wheel alone is 13.5 MB. With a warm cache, ready takes
2.6 s.

The host was shared with other jobs (load average 109-147 on 16 cores during the measurement), so
every absolute time here is pessimistic.

### Numbers (headless Chrome, Pyodide 314.0.7, synthetic input)

| What | Cold cache | Warm cache |
|---|---|---|
| Pyodide + numpy + scipy load (script start => arena files written) | 3851 ms | 1598 ms |
| of which `loadPackage(["numpy", "scipy"])` | 1276 ms | 742 ms |
| Arena import (numpy + scipy.ndimage import 915 ms, arena modules 19 ms) | 938 ms | 886 ms |
| Ready, since navigation start | 4915 ms | 2606 ms |

| Planner | Layout | Simulated s | Browser wall s (median of 3) | Wall per simulated s | 30 s run => wall s | Native wall per simulated s | Browser / native |
|---|---|---|---|---|---|---|---|
| straight | random/0 | 20.4 | 0.079 | 0.0039 | 0.12 | 0.0028 | 1.39x |
| astar_esdf known map | random/0 | 19.38 | 0.652 | 0.0337 | 1.01 | 0.0162 | 2.08x |
| astar_esdf unknown map | random/0 | 18.68 | 2.875 | 0.1539 | 4.62 | 0.0727 | 2.12x |
| straight | u_trap/1 | 20.48 | 0.074 | 0.0036 | 0.11 | 0.002 | 1.8x |
| astar_esdf known map | u_trap/1 | 20.06 | 0.596 | 0.0297 | 0.89 | 0.0142 | 2.09x |
| astar_esdf unknown map | u_trap/1 | 22.16 | 4.38 | 0.1976 | 5.93 | 0.0917 | 2.15x |

- Total for one 20 s run, cold page: 4.9 s to ready, then 0.65 s for astar_esdf known map on
  random/0 (19.38 s simulated).
- The first run takes the same time as later runs (astar known random/0: 0.653 s first, 0.652 s
  median). There is no warm-up penalty after import.
- Layout build (`world.make_world`, raster + BFS free-path check): 77-78 ms per layout.
- Streaming cost: positions go to JS through the `pose_source` hook at 10 Hz (194-204 calls per
  run). A run with streaming takes the same time as one without (astar known random/0: 0.652 s
  vs 0.651 s).
- Memory: the wasm heap is 90 MB after import and does not grow over 24 runs. The Chrome JS heap is
  179-182 MB after import (`performance.memory`, Chrome only).
- Scores (outcome, time to goal, duration, min clearance, path length) are identical to
  `samples/close-area-arena/results/astar_esdf_{family}_0.json`, which was run with CPython 3.11 /
  numpy 2.4.6. They also match today's native run (CPython 3.12.10 / numpy 2.5.4). Pyodide uses
  Python 3.14.2 / numpy 2.4.6 / scipy 1.18.0.

### What the playground has to deal with

The main thread freezes while Python runs, because `run_one` is one synchronous call. The freeze
lasts 0.08 s for straight, 0.6-0.65 s for astar known map, and 2.9-4.4 s for astar unknown map
(table above). Positions cannot be drawn while the run is computing. This spike computes the whole
run first, then replays the streamed positions at 4x speed. Ranked options:

1. **Run Pyodide in a Web Worker, keep compute-then-replay (recommended).** The UI stays
   responsive and the arena code does not change. The worker posts positions with `postMessage`,
   in chunks or at the end. Estimate: about half a day, roughly 100-150 lines of JS moved into
   `worker.js` plus a message protocol. Not built or measured here.
2. **Ship as measured, on the main thread.** No extra cost. A 0.6 s freeze for astar known map is
   tolerable. The 4-6 s freeze for unknown map is not, so hide that planner or show a "computing"
   state.
3. **Lower the planner or physics rate.** Not needed: the slowest case is already 5x faster than
   real time. Changing `plan_hz` or `HZ` would also make playground results differ from the
   benchmarks.
4. **Precompute runs offline.** This already exists for the showcase
   (`export_replay.py`). It does not cover user-drawn arenas, so it does not answer the brief.
5. **Port a subset to JS.** Estimate: 2-4 days for vehicle, range fan, scorer, straight and A* +
   ESDF (an EDT would also be needed). It saves the 22 MB download and about 4 s of cold load. The
   cost is a second implementation that drifts from the benchmarks. Only worth it if cold load on
   the Pages site turns out to be unacceptable.

To cut cold load without porting, the playground can start loading Pyodide when the page opens,
while the user is still drawing. The service-worker or HTTP cache then makes repeat visits about
2.6 s (warm column).

Custom arenas: the playground will need a few lines of Python that build a `World` from the drawn
boxes and cylinders, then call `rasterize()` and the BFS check, the way `make_world` does. No
arena file needs to change for that. Not written or tested here.

### Files

| File | What |
|---|---|
| [spike.html](spike.html) | The page. `?bench=1` runs the full 6-case matrix; `?reps=N` sets the repetitions |
| [spike.js](spike.js) | Loads Pyodide from the URL in the manifest, `loadPackage` numpy + scipy, writes the arena files into `/home/pyodide/close_area_arena/`, runs `DRIVER_PY` (imports + `bench_case`), streams positions, draws canvases. `window.SPIKE_RESULT` holds every measurement |
| [manifest.json](manifest.json) | Pyodide version and base URL, packages, and the arena files (11 for the spike, 23 now that the playground also loads estimator, faults, presets, sensors_cone, world_json, worlds_complex, world_glass, run_faults, APF, VFH+ and filters.py; `src` is relative to the manifest, so `../../` is the repo root) |
| [results/measure.mjs](results/measure.mjs) | Runs `DRIVER_PY` under native CPython from the arena venv, then the page in headless Chrome over the DevTools protocol: cold profile with `?bench=1`, then warm with the default page. Writes everything below |
| [results/spike_timing.md](results/spike_timing.md) | Generated report: environment, load, runs, score parity, memory, downloads |
| `results/spike_cold.json`, `spike_warm.json`, `native_baseline.json` | Raw measurements |
| [results/spike_bench.png](results/spike_bench.png), [results/spike_interactive.png](results/spike_interactive.png) | 1280 x 900 viewport screenshots |

### Run

```sh
python3 -m http.server 8000            # from the repo root
# open http://localhost:8000/site/playground/spike.html  (add ?bench=1 for the matrix)
```

Re-measure (needs the arena venv for the native baseline, Chrome, and network for the CDN):

```sh
uv venv --python 3.12 samples/close-area-arena/.venv
uv pip install --python samples/close-area-arena/.venv -r samples/close-area-arena/requirements.txt
node site/playground/results/measure.mjs        # about 4 minutes on the loaded host
```

Version notes: Pyodide moved to Python-version numbering. `314.0.7` was the jsdelivr `latest`
tag on 2026-11-09, and its `pyodide-lock.json` lists numpy 2.4.6 and scipy 1.18.0. The older line,
`0.29.5`, ships scipy 1.14.1. Pyodide 314 converts JS `null` to `JsNull`, which is not Python
`None`, so `spike.js` passes `undefined` for "no callback".

### Not verified

- GitHub Pages hosting (only `python3 -m http.server` locally). Pages serves `.py` files as static
  files, but that was not tried.
- Firefox, Safari, phones, and slower laptops. Only headless Chrome 140 on one M3 Max, under heavy
  host load.
- The JS-port estimates: these are estimates, not measurements. (The Web Worker variant was built and measured later: see the playground section above.)
- Runs of exactly 30 s: the measured runs end at 18.7-22.2 s simulated (reached or stuck). The 30 s
  figures are wall per simulated second x 30.
- Narrow-gap layouts, the estimator and fault hooks, and user-drawn arenas.
- Real or SITL flight: everything here is the synthetic arena.
