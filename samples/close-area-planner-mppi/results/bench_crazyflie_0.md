`python bench.py --preset crazyflie --families random,office --layouts 20 --seed 0 --workers 14` from samples/close-area-planner-mppi. Input: synthetic (simulated layouts, vehicle and sensor), scored on truth. Preset `crazyflie`, seed 0, 20 layouts per cell, 14 worker process(es), wall 15.2 s, Python 3.12.10, numpy 2.5.4, scipy 1.18.1, arm64 Darwin. Run time limit 60 s, 120 s for maze and warehouse. step ms = the whole planner.step() call (map update, ESDF, A* when due, MPPI) at 10 Hz; A* replan ms = the A* searches inside those steps. Timings were taken with 14 processes sharing the machine; see timing_0.md for one process.

Parity: astar_unknown runs identical to close-area-benchmark matrix_0.json (outcome, min clearance, path length): 40/40.

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | step ms median | step ms p95 | A* replan ms median | A* replan ms p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | random | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 22.51 | 24.63 | 0.59 | 0.33 | 84.6 | 41.14 | 112.74 |
| astar_unknown | office | 20 | 35.0 | 25.0 | 35.0 | 5.0 | 18.84 | 7.6 | 0.225 | 0.39 | 22.24 | 11.75 | 38.44 |
| mppi_none | random | 20 | 55.0 | 40.0 | 5.0 | 0.0 | 20.3 | 23.39 | 0.422 | 3.85 | 8.64 | - | - |
| mppi_none | office | 20 | 5.0 | 75.0 | 20.0 | 0.0 | 9.9 | 2.79 | 0.143 | 3.89 | 7.86 | - | - |
| mppi_astar | random | 20 | 80.0 | 20.0 | 0.0 | 0.0 | 20.37 | 23.95 | 0.535 | 4.98 | 86.36 | 42.75 | 101.22 |
| mppi_astar | office | 20 | 10.0 | 85.0 | 5.0 | 0.0 | 8.1 | 4.08 | 0.142 | 5.24 | 28.28 | 11.58 | 34.96 |

Per run (outcome, time to B s, min clearance m, path m):

| family | run | astar_unknown | mppi_none | mppi_astar |
|---|---|---|---|---|
| random | 0 | reached 22.5 0.7326 24.972 | collision - 0.1382 15.024 | collision - 0.1302 15.171 |
| random | 1 | reached 16.76 1.2564 23.974 | reached 20.32 1.2576 23.978 | reached 20.24 1.263 23.973 |
| random | 2 | reached 21.08 0.6147 24.058 | reached 20.44 0.7064 24.028 | reached 20.46 0.5957 24.091 |
| random | 3 | reached 27.62 0.2764 25.093 | stuck - 0.4346 8.918 | reached 25.48 0.1597 28.028 |
| random | 4 | reached 19.02 0.777 23.964 | reached 20.3 0.6242 23.796 | reached 20.18 0.9526 23.895 |
| random | 5 | reached 27.16 0.3717 24.764 | collision - 0.1452 10.782 | reached 22.56 0.4749 25.277 |
| random | 6 | reached 23.82 0.3121 25.551 | collision - 0.149 12.782 | reached 21.96 0.3667 25.532 |
| random | 7 | reached 23.64 0.5646 26.086 | reached 22.88 0.3941 25.718 | reached 21.6 0.6811 25.075 |
| random | 8 | reached 26.58 0.4762 26.113 | collision - 0.1373 5.706 | collision - 0.1276 7.024 |
| random | 9 | reached 16.48 0.7523 23.288 | reached 19.78 0.7793 23.295 | reached 19.7 0.7812 23.293 |
| random | 10 | reached 16.76 0.9314 23.92 | reached 20.26 0.928 23.918 | reached 20.2 0.9715 23.918 |
| random | 11 | reached 28.66 0.4572 27.192 | collision - 0.1474 6.277 | collision - 0.1451 15.21 |
| random | 12 | reached 23.72 0.5471 25.453 | collision - 0.1388 4.0 | reached 25.0 0.1979 26.769 |
| random | 13 | reached 31.6 0.2917 27.699 | collision - 0.1433 11.833 | collision - 0.1472 15.198 |
| random | 14 | reached 16.82 1.1604 24.063 | reached 20.38 1.1604 24.064 | reached 20.28 1.1604 24.06 |
| random | 15 | reached 18.76 0.9627 23.926 | reached 20.16 0.5386 23.786 | reached 20.16 0.9749 23.86 |
| random | 16 | reached 24.66 0.4371 25.762 | collision - 0.1408 8.481 | reached 23.4 0.1575 26.508 |
| random | 17 | reached 16.92 0.7177 23.578 | reached 20.0 0.762 23.579 | reached 19.92 0.743 23.58 |
| random | 18 | reached 16.44 1.1991 23.49 | reached 19.94 1.1991 23.491 | reached 19.86 1.1991 23.486 |
| random | 19 | reached 22.52 0.3885 24.505 | reached 20.6 0.4098 24.157 | reached 21.54 0.3609 24.747 |
| office | 0 | stuck - 0.2448 17.122 | stuck - 0.6379 2.923 | collision - 0.1406 10.027 |
| office | 1 | stuck - 0.2668 6.808 | stuck - 0.6326 3.868 | collision - 0.1398 11.129 |
| office | 2 | reached 18.5 0.3208 8.392 | collision - 0.1304 1.741 | collision - 0.1371 1.797 |
| office | 3 | collision - 0.1489 6.587 | stuck - 0.4239 2.814 | collision - 0.1349 4.651 |
| office | 4 | collision - 0.1472 2.414 | collision - 0.1359 3.46 | collision - 0.1381 3.556 |
| office | 5 | collision - 0.1473 4.265 | collision - 0.1496 2.776 | stuck - 0.3595 3.969 |
| office | 6 | stuck - 0.2857 17.857 | collision - 0.1402 1.637 | collision - 0.1469 2.418 |
| office | 7 | stuck - 0.1593 5.464 | collision - 0.1371 2.44 | collision - 0.1466 3.76 |
| office | 8 | timeout - 0.2092 20.917 | collision - 0.1453 7.706 | collision - 0.142 1.848 |
| office | 9 | reached 17.18 0.3596 6.526 | collision - 0.1443 6.328 | reached 7.44 0.3203 6.89 |
| office | 10 | collision - 0.147 5.163 | reached 9.9 0.3421 10.537 | collision - 0.1393 5.763 |
| office | 11 | stuck - 0.2038 3.434 | collision - 0.1401 1.587 | collision - 0.1414 4.062 |
| office | 12 | reached 32.34 0.1771 13.93 | collision - 0.1326 1.796 | collision - 0.1375 1.6 |
| office | 13 | reached 18.84 0.3414 11.325 | collision - 0.1282 1.138 | collision - 0.1392 8.754 |
| office | 14 | reached 11.3 0.2472 6.492 | collision - 0.1428 3.439 | reached 8.76 0.2321 7.945 |
| office | 15 | stuck - 0.2494 11.996 | collision - 0.1351 1.648 | collision - 0.1451 1.679 |
| office | 16 | stuck - 0.3032 13.914 | stuck - 0.4461 2.487 | collision - 0.1454 10.725 |
| office | 17 | reached 25.44 0.2416 12.695 | collision - 0.1481 3.908 | collision - 0.1483 13.463 |
| office | 18 | collision - 0.1488 2.995 | collision - 0.1433 4.524 | collision - 0.1377 4.1 |
| office | 19 | reached 25.16 0.1835 9.217 | collision - 0.142 2.209 | collision - 0.1498 1.766 |
