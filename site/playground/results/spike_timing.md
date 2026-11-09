# Spike timing: close-area arena under Pyodide in headless Chrome

Written by `node site/playground/results/measure.mjs` on 2026-11-09. Input: synthetic (simulated layouts, vehicle and range sensor from samples/close-area-arena). Raw data: [spike_cold.json](spike_cold.json), [spike_warm.json](spike_warm.json), [native_baseline.json](native_baseline.json).

## Environment

| | browser | native |
|---|---|---|
| runtime | Chrome/140.0.7339.208 headless=new, Pyodide 314.0.7 | CPython 3.12.10 |
| Python / numpy / scipy | 3.14.2 / 2.4.6 / 1.18.0 | 3.12.10 / 2.5.4 / 1.18.1 |
| machine | Apple M3 Max (16 cores), Darwin 25.6.0 arm64 | same machine |

Host load average (1 / 5 / 15 min): 109 / 106 / 94 before native, 115 / 107 / 95 after native, 147 / 118 / 100 after Chrome. The host was shared with other jobs, so absolute times are pessimistic and noisy; native and browser ran one after the other, not interleaved.

## Load (once per page)

| step | cold cache ms | warm cache ms |
|---|---|---|
| pyodide.js script | 609.9 | 6.9 |
| loadPyodide() (wasm + stdlib) | 1963.7 | 847.6 |
| loadPackage numpy + scipy | 1276.2 | 742.1 |
| fetch 11 arena .py files (parallel with packages) | 23.6 | 9.9 |
| load total (script start => files written) | 3851.2 | 1598 |
| arena import (DRIVER_PY incl. numpy, scipy.ndimage) | 938.2 | 885.8 |
| ready, since navigation start | 4915 | 2606 |
| of which numpy + scipy.ndimage import (Python perf_counter) | 915.4 | 864.1 |
| of which arena modules import | 19.1 | 18.9 |

Cold download from cdn.jsdelivr.net: 7 files, 22.0 MB transferred, 29.1 MB decoded (Resource Timing). Largest:

| file | transferred KB | decoded KB | ms |
|---|---|---|---|
| scipy-1.18.0-cp314-cp314-pyemscripten_2026_0_wasm32.whl | 13546 | 13701 | 638 |
| pyodide.asm.wasm | 3358 | 9373 | 1072 |
| numpy-2.4.6-cp314-cp314-pyemscripten_2026_0_wasm32.whl | 2862 | 2891 | 252 |
| python_stdlib.zip | 2447 | 2486 | 1091 |
| pyodide.asm.mjs | 256 | 1221 | 693 |

Arena source: 11 files, 58.4 KB, from the local server.

## Runs (cold page, 3 streamed runs + 1 without streaming per case)

Wall = `run_one` only (layout build excluded, listed separately). 30 s projection = median wall per simulated second x 30. Target: under 15 s.

| planner | layout | outcome | sim s | browser first run s | browser median s | browser wall per sim s | 30 s run => browser wall s | verdict | no-stream run s | native median wall per sim s | browser / native | layout build ms (browser) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| straight | random/0 | stuck | 20.4 | 0.092 | 0.079 | 0.0039 | 0.12 | PASS | 0.075 | 0.0028 | 1.39x | 78.2 |
| astar_esdf_known | random/0 | reached | 19.38 | 0.653 | 0.652 | 0.0337 | 1.01 | PASS | 0.651 | 0.0162 | 2.08x | 76.6 |
| astar_esdf_unknown | random/0 | reached | 18.68 | 2.869 | 2.875 | 0.1539 | 4.62 | PASS | 2.871 | 0.0727 | 2.12x | 77.8 |
| straight | u_trap/1 | stuck | 20.48 | 0.074 | 0.074 | 0.0036 | 0.11 | PASS | 0.073 | 0.002 | 1.8x | 77.6 |
| astar_esdf_known | u_trap/1 | reached | 20.06 | 0.596 | 0.596 | 0.0297 | 0.89 | PASS | 0.593 | 0.0142 | 2.09x | 78.1 |
| astar_esdf_unknown | u_trap/1 | reached | 22.16 | 4.384 | 4.38 | 0.1976 | 5.93 | PASS | 4.367 | 0.0917 | 2.15x | 78.1 |

## Same scores as native

Fields compared: outcome, time_to_goal_s, duration_s, min_clearance_m, path_length_m.

| planner | layout | browser = published results/astar_esdf_{family}_0.json | browser = native run today |
|---|---|---|---|
| straight | random/0 | yes | yes |
| astar_esdf_known | random/0 | yes | yes |
| astar_esdf_unknown | random/0 | yes | yes |
| straight | u_trap/1 | yes | yes |
| astar_esdf_known | u_trap/1 | yes | yes |
| astar_esdf_unknown | u_trap/1 | yes | yes |

## Memory (Chrome)

| point | wasm heap MB | JS heap used MB |
|---|---|---|
| after loadPyodide | 30 | 45 |
| after numpy + scipy | 62 | 189 |
| after arena import | 90 | 179 |
| after astar_esdf_unknown u_trap/1 run 4 | 90 | 179 |

## Interactive page (warm cache, 2 cases, 1 run each)

| planner | layout | outcome | sim s | wall s | positions streamed |
|---|---|---|---|---|---|
| straight | random/0 | stuck | 20.4 | 0.079 | 204 |
| astar_esdf_known | random/0 | reached | 19.38 | 0.646 | 194 |

Console errors / warnings: cold 0, warm 0. Page errors: cold 0, warm 0.

Screenshots (1280 x 900 viewport): [bench](spike_bench.png), [interactive](spike_interactive.png).
