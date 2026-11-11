# Playground: new planners, browser vs native

`node site/playground/results/measure_loop73.mjs`, 2026-11-10T06:09:04.462Z. Input: **synthetic** (2.5D point-mass arena, preset worlds, seed 0, sensor ideal, truth pose, no filter).
Browser: Chrome/140.0.7339.208, Pyodide 314.0.7 (Python 3.14.2, numpy 2.4.6, scipy 1.18.0). Native: 3.12.10, numpy 2.5.4, scipy 1.18.1 ([native_parity_loop73.json](native_parity_loop73.json)).
Host: 16 CPUs, load average 45.8 / 38.9 / 39.5 at start. Load errors in the worker: {}.

**12/12 cases identical (browser = native).** Runs over 60 s of browser Python: none.

| world | planner | browser outcome / time to goal s / min clearance m / path m | native | same | browser Python s | native Python s |
|---|---|---|---|---|---|---|
| random_0 | thetastar_known | reached / 17.08 / 0.8833 / 24.123 | reached / 17.08 / 0.8833 / 24.123 | yes | 3.28 | 2.059 |
| maze_0 | thetastar_known | reached / 31.88 / 0.8223 / 39.463 | reached / 31.88 / 0.8223 / 39.463 | yes | 9.873 | 6.214 |
| random_0 | lazy_thetastar_known | reached / 17.12 / 0.8494 / 24.098 | reached / 17.12 / 0.8494 / 24.098 | yes | 2.268 | 1.401 |
| maze_0 | lazy_thetastar_known | reached / 31.88 / 0.8208 / 39.448 | reached / 31.88 / 0.8208 / 39.448 | yes | 6.253 | 3.616 |
| random_0 | lazy_thetastar_unknown | reached / 17.6 / 0.8919 / 24.653 | reached / 17.6 / 0.8919 / 24.653 | yes | 10.179 | 6.44 |
| maze_0 | lazy_thetastar_unknown | reached / 33.78 / 0.7908 / 40.487 | reached / 33.78 / 0.7908 / 40.487 | yes | 30.727 | 19.599 |
| random_0 | mppi | reached / 20.82 / 0.341 / 24.051 | reached / 20.82 / 0.341 / 24.051 | yes | 1.673 | 1.112 |
| maze_0 | mppi | stuck / - / 0.6542 / 9.441 | stuck / - / 0.6542 / 9.441 | yes | 1.673 | 1.083 |
| random_0 | mppi_astar | reached / 20.24 / 0.5812 / 23.917 | reached / 20.24 / 0.5812 / 23.917 | yes | 5.321 | 3.122 |
| maze_0 | mppi_astar | reached / 31.28 / 0.357 / 35.589 | reached / 31.28 / 0.357 / 35.589 | yes | 10.177 | 5.684 |
| random_0 | hybrid_astar | reached / 18.74 / 0.6417 / 24.371 | reached / 18.74 / 0.6417 / 24.371 | yes | 1.084 | 0.868 |
| maze_0 | hybrid_astar | reached / 39.26 / 0.2553 / 38.439 | reached / 39.26 / 0.2553 / 38.439 | yes | 2.262 | 1.932 |

Console errors / warnings: 1
- exception: {"exceptionId":1,"text":"Uncaught (in promise)","lineNumber":1020,"columnNumber":9,"scriptId":"7","url":"http://127.0.0.1:8776/site/playground/playground.js?v=20261110","stackTrace":{"callFrames":[{"functionName":"parityNote","scriptId":"7","url":"http://127.0.0.1:8776/site/playground/playground.js?v=20261110","lineNumber":1020,"columnNumber":9}]},"exception":{"type":"object","subtype":"error","className":"TypeError","description":"TypeError: Cannot read properties of null (reading 'forEach')\n    at parityNote (http://127.0.0.1:8776/site/playground/playground.js?v=20261110:1021:10)","objectId
