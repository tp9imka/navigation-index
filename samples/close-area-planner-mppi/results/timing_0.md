`python bench.py --timing --workers 1` from samples/close-area-planner-mppi. Input: synthetic (simulated layouts, vehicle and sensor), scored on truth. Preset `ideal`, seed 0, 5 layouts per cell, 1 worker process(es), wall 65.8 s, Python 3.12.10, numpy 2.5.4, scipy 1.18.1, arm64 Darwin. Run time limit 60 s, 120 s for maze and warehouse. step ms = the whole planner.step() call (map update, ESDF, A* when due, MPPI) at 10 Hz; A* replan ms = the A* searches inside those steps.

Parity: astar_unknown runs identical to close-area-benchmark matrix_0.json (outcome, min clearance, path length): 10/10.

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | step ms median | step ms p95 | A* replan ms median | A* replan ms p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | random | 5 | 100.0 | 0.0 | 0.0 | 0.0 | 18.38 | 23.95 | 0.608 | 0.65 | 51.88 | 22.42 | 59.86 |
| astar_unknown | maze | 5 | 100.0 | 0.0 | 0.0 | 0.0 | 45.64 | 37.73 | 0.582 | 0.48 | 59.13 | 22.01 | 72.35 |
| mppi_none | random | 5 | 80.0 | 0.0 | 20.0 | 0.0 | 20.3 | 23.95 | 0.572 | 3.77 | 4.03 | - | - |
| mppi_none | maze | 5 | 0.0 | 0.0 | 100.0 | 0.0 | - | 9.44 | 0.374 | 3.63 | 3.91 | - | - |
| mppi_astar | random | 5 | 100.0 | 0.0 | 0.0 | 0.0 | 20.24 | 23.95 | 0.592 | 4.18 | 57.09 | 22.64 | 60.69 |
| mppi_astar | maze | 5 | 100.0 | 0.0 | 0.0 | 0.0 | 31.28 | 35.59 | 0.372 | 4.33 | 64.3 | 23.01 | 72.77 |

Per run (outcome, time to B s, min clearance m, path m):

| family | run | astar_unknown | mppi_none | mppi_astar |
|---|---|---|---|---|
| random | 0 | reached 18.7 0.6623 23.95 | reached 20.82 0.3409 24.051 | reached 20.24 0.5811 23.917 |
| random | 1 | reached 16.76 1.2564 23.974 | reached 20.32 1.2607 23.975 | reached 20.24 1.2634 23.973 |
| random | 2 | reached 18.38 0.6075 23.948 | reached 20.28 0.572 23.955 | reached 20.22 0.6379 23.954 |
| random | 3 | reached 21.62 0.6078 24.162 | stuck - 0.6351 7.886 | reached 20.44 0.5365 24.154 |
| random | 4 | reached 17.82 0.5875 23.673 | reached 20.12 0.4629 23.698 | reached 20.0 0.5917 23.681 |
| maze | 0 | reached 44.78 0.5911 37.733 | stuck - 0.6542 9.442 | reached 31.28 0.357 35.589 |
| maze | 1 | reached 33.76 0.6135 29.117 | stuck - 0.3732 22.425 | reached 24.4 0.4328 28.468 |
| maze | 2 | reached 51.2 0.5754 40.09 | stuck - 0.294 27.799 | reached 33.62 0.3497 37.266 |
| maze | 3 | reached 45.64 0.5802 36.057 | stuck - 0.3737 7.589 | reached 30.4 0.39 34.909 |
| maze | 4 | reached 49.08 0.582 39.391 | stuck - 0.4256 6.619 | reached 32.62 0.3719 37.123 |
