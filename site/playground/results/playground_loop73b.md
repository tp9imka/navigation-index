# Playground: maze_0 and warehouse_0 with the benchmark run time limit, browser vs native

`node site/playground/results/measure_loop73b.mjs`, 2026-11-10T07:07:26.126Z. Input: **synthetic** (2.5D point-mass arena, preset worlds, seed 0, sensor ideal, truth pose, no filter).
Browser: Chrome/140.0.7339.208, Pyodide 314.0.7 (Python 3.14.2, numpy 2.4.6, scipy 1.18.0). Native: 3.12.10, numpy 2.5.4, scipy 1.18.1 ([native_parity.json](native_parity.json), [native_parity_loop73.json](native_parity_loop73.json)).
Host: 16 CPUs, load average 29.1 / 17.6 / 18.4 at start. Load errors in the worker: {}.

**11/11 cases identical (browser = native).** Run time limit reported by the worker = native and shown in the score table: yes, every case. Runs over 60 s of browser Python: none.

| world | planner | limit s (browser / native / table) | browser outcome / time to goal s / min clearance m / path m | native | same | browser Python s | native Python s |
|---|---|---|---|---|---|---|---|
| maze_0 | astar_known | 120 / 120 / 120 | reached / 41.26 / 0.5937 / 36.981 | reached / 41.26 / 0.5937 / 36.981 | yes | 5.076 | 1.974 |
| warehouse_0 | astar_known | 120 / 120 / 120 | reached / 49.26 / 0.5151 / 34.978 | reached / 49.26 / 0.5151 / 34.978 | yes | 4.237 | 1.649 |
| maze_0 | bug2 | 120 / 120 / 120 | reached / 105.22 / 0.4043 / 65.49 | reached / 105.22 / 0.4043 / 65.49 | yes | 0.662 | 0.313 |
| warehouse_0 | bug2 | 120 / 120 / 120 | timeout / - / 0.4254 / 70.725 | timeout / - / 0.4254 / 70.725 | yes | 0.714 | 0.321 |
| maze_0 | informed_rrt_star | 120 / 120 / 120 | reached / 69.7 / 0.2754 / 33.637 | reached / 69.7 / 0.2754 / 33.637 | yes | 0.932 | 0.415 |
| maze_0 | thetastar_known | 120 / 120 / 120 | reached / 31.88 / 0.8223 / 39.463 | reached / 31.88 / 0.8223 / 39.463 | yes | 9.844 | 4.509 |
| maze_0 | lazy_thetastar_known | 120 / 120 / 120 | reached / 31.88 / 0.8208 / 39.448 | reached / 31.88 / 0.8208 / 39.448 | yes | 6.203 | 2.736 |
| maze_0 | lazy_thetastar_unknown | 120 / 120 / 120 | reached / 33.78 / 0.7908 / 40.487 | reached / 33.78 / 0.7908 / 40.487 | yes | 31.816 | 14.253 |
| maze_0 | mppi | 120 / 120 / 120 | stuck / - / 0.6542 / 9.441 | stuck / - / 0.6542 / 9.441 | yes | 1.721 | 0.825 |
| maze_0 | mppi_astar | 120 / 120 / 120 | reached / 31.28 / 0.357 / 35.589 | reached / 31.28 / 0.357 / 35.589 | yes | 10.109 | 4.314 |
| maze_0 | hybrid_astar | 120 / 120 / 120 | reached / 39.26 / 0.2553 / 38.439 | reached / 39.26 / 0.2553 / 38.439 | yes | 2.466 | 1.516 |

Console errors / warnings: 0
