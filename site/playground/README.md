# Playground spike: the close-area arena in the browser (Pyodide)

Feasibility spike for a browser playground (draw an arena, place A and B, pick a planner, watch
it fly). Question: can the hub's real Python arena and planners
([samples/close-area-arena](../../samples/close-area-arena/README.md)) run in the browser fast
enough, so the playground and the benchmarks share one implementation?

## Verdict

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

## Numbers (headless Chrome, Pyodide 314.0.7, synthetic input)

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

## What the playground has to deal with

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

## Files

| File | What |
|---|---|
| [spike.html](spike.html) | The page. `?bench=1` runs the full 6-case matrix; `?reps=N` sets the repetitions |
| [spike.js](spike.js) | Loads Pyodide from the URL in the manifest, `loadPackage` numpy + scipy, writes the arena files into `/home/pyodide/close_area_arena/`, runs `DRIVER_PY` (imports + `bench_case`), streams positions, draws canvases. `window.SPIKE_RESULT` holds every measurement |
| [manifest.json](manifest.json) | Pyodide version and base URL, packages, and the 11 arena files (`src` is relative to the manifest, so `../../` is the repo root) |
| [results/measure.mjs](results/measure.mjs) | Runs `DRIVER_PY` under native CPython from the arena venv, then the page in headless Chrome over the DevTools protocol: cold profile with `?bench=1`, then warm with the default page. Writes everything below |
| [results/spike_timing.md](results/spike_timing.md) | Generated report: environment, load, runs, score parity, memory, downloads |
| `results/spike_cold.json`, `spike_warm.json`, `native_baseline.json` | Raw measurements |
| [results/spike_bench.png](results/spike_bench.png), [results/spike_interactive.png](results/spike_interactive.png) | 1280 x 900 viewport screenshots |

## Run

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

## Not verified

- GitHub Pages hosting (only `python3 -m http.server` locally). Pages serves `.py` files as static
  files, but that was not tried.
- Firefox, Safari, phones, and slower laptops. Only headless Chrome 140 on one M3 Max, under heavy
  host load.
- The Web Worker variant and the JS-port estimates: these are estimates, not measurements.
- Runs of exactly 30 s: the measured runs end at 18.7-22.2 s simulated (reached or stuck). The 30 s
  figures are wall per simulated second x 30.
- Narrow-gap layouts, the estimator and fault hooks, and user-drawn arenas.
- Real or SITL flight: everything here is the synthetic arena.
