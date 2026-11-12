`python bench.py --layouts 20 --seed 0 --jobs 10 --name bench_0_regen` from samples/close-area-explore. Input: synthetic (simulated layouts, vehicle, range sensor; B detection by exact range + line of sight). Scored on truth. 1560 runs, wall 556.2 s on 10 processes.

Regenerated 2026-11-12 with SKIP_DROPPED_BEAMS = True in close-area-arena/planners/astar_esdf.py (a beam the sensor flags dropped adds nothing to the map; docs/upstream-findings.md section 22). Written as bench_0_regen and renamed to bench_0; every other input matches the previous run of this file.

Detection: within 2.0 m of B with a clear line of sight. Budget 180 s per run. Wilson 95 % intervals. Times are medians over runs that found / reached B, measured from take-off.

## Pooled over families

| preset | region | arm | n | found % [95 % CI] | reached % [95 % CI] | collision % [95 % CI] | stuck % | timeout % | median time to find s | median time to B s |
|---|---|---|---|---|---|---|---|---|---|---|
| ideal | B given | oracle | 60 | 100.0 [94.0, 100.0] | 93.3 [84.1, 97.4] | 0.0 [0.0, 6.0] | 0.0 | 6.7 | 0.0 | 22.05 |
| ideal | 0 m | frontier (region ignored) | 60 | 41.7 [30.1, 54.3] | 41.7 [30.1, 54.3] | 0.0 [0.0, 6.0] | 18.3 | 40.0 | 78.4 | 81.28 |
| ideal | 0 m | nominal_frontier | 60 | 91.7 [81.9, 96.4] | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 0.0 | 8.3 | 19.8 | 21.82 |
| ideal | 0 m | lawnmower | 60 | 88.3 [77.8, 94.2] | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 0.0 | 11.7 | 19.1 | 21.68 |
| ideal | 0 m | random_walk | 60 | 95.0 [86.3, 98.3] | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 0.0 | 5.0 | 20.1 | 22.18 |
| ideal | 2 m | frontier (region ignored) | 60 | 41.7 [30.1, 54.3] | 41.7 [30.1, 54.3] | 0.0 [0.0, 6.0] | 18.3 | 40.0 | 78.4 | 81.28 |
| ideal | 2 m | nominal_frontier | 60 | 88.3 [77.8, 94.2] | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 0.0 | 11.7 | 21.1 | 23.0 |
| ideal | 2 m | lawnmower | 60 | 91.7 [81.9, 96.4] | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 0.0 | 8.3 | 30.4 | 32.84 |
| ideal | 2 m | random_walk | 60 | 86.7 [75.8, 93.1] | 86.7 [75.8, 93.1] | 0.0 [0.0, 6.0] | 0.0 | 13.3 | 20.3 | 23.92 |
| ideal | 5 m | frontier (region ignored) | 60 | 41.7 [30.1, 54.3] | 41.7 [30.1, 54.3] | 0.0 [0.0, 6.0] | 18.3 | 40.0 | 78.4 | 81.28 |
| ideal | 5 m | nominal_frontier | 60 | 81.7 [70.1, 89.4] | 81.7 [70.1, 89.4] | 0.0 [0.0, 6.0] | 5.0 | 13.3 | 26.3 | 30.88 |
| ideal | 5 m | lawnmower | 60 | 83.3 [72.0, 90.7] | 81.7 [70.1, 89.4] | 1.7 [0.3, 8.9] | 0.0 | 16.7 | 47.8 | 49.72 |
| ideal | 5 m | random_walk | 60 | 85.0 [73.9, 91.9] | 85.0 [73.9, 91.9] | 0.0 [0.0, 6.0] | 0.0 | 15.0 | 41.4 | 43.38 |
| ideal | unknown | frontier (region ignored) | 60 | 41.7 [30.1, 54.3] | 41.7 [30.1, 54.3] | 0.0 [0.0, 6.0] | 18.3 | 40.0 | 78.4 | 81.28 |
| ideal | unknown | nominal_frontier (= frontier) | 60 | 41.7 [30.1, 54.3] | 41.7 [30.1, 54.3] | 0.0 [0.0, 6.0] | 18.3 | 40.0 | 78.4 | 81.28 |
| ideal | unknown | lawnmower | 60 | 31.7 [21.3, 44.2] | 30.0 [19.9, 42.5] | 5.0 [1.7, 13.7] | 0.0 | 65.0 | 152.5 | 152.81 |
| ideal | unknown | random_walk | 60 | 18.3 [10.6, 29.9] | 18.3 [10.6, 29.9] | 1.7 [0.3, 8.9] | 0.0 | 80.0 | 91.4 | 95.04 |
| crazyflie | B given | oracle | 60 | 100.0 [94.0, 100.0] | 56.7 [44.1, 68.4] | 38.3 [27.1, 51.0] | 3.3 | 1.7 | 0.0 | 23.39 |
| crazyflie | 0 m | frontier (region ignored) | 60 | 18.3 [10.6, 29.9] | 18.3 [10.6, 29.9] | 0.0 [0.0, 6.0] | 18.3 | 63.3 | 135.4 | 140.48 |
| crazyflie | 0 m | nominal_frontier | 60 | 58.3 [45.7, 69.9] | 58.3 [45.7, 69.9] | 28.3 [18.5, 40.8] | 1.7 | 11.7 | 21.3 | 23.46 |
| crazyflie | 0 m | lawnmower | 60 | 53.3 [40.9, 65.4] | 53.3 [40.9, 65.4] | 30.0 [19.9, 42.5] | 1.7 | 15.0 | 20.7 | 22.29 |
| crazyflie | 0 m | random_walk | 60 | 60.0 [47.4, 71.4] | 60.0 [47.4, 71.4] | 35.0 [24.2, 47.6] | 3.3 | 1.7 | 21.5 | 23.69 |
| crazyflie | 2 m | frontier (region ignored) | 60 | 18.3 [10.6, 29.9] | 18.3 [10.6, 29.9] | 0.0 [0.0, 6.0] | 18.3 | 63.3 | 135.4 | 140.48 |
| crazyflie | 2 m | nominal_frontier | 60 | 50.0 [37.7, 62.3] | 50.0 [37.7, 62.3] | 40.0 [28.6, 52.6] | 3.3 | 6.7 | 22.2 | 24.13 |
| crazyflie | 2 m | lawnmower | 60 | 51.7 [39.3, 63.8] | 50.0 [37.7, 62.3] | 35.0 [24.2, 47.6] | 5.0 | 10.0 | 21.5 | 23.2 |
| crazyflie | 2 m | random_walk | 60 | 63.3 [50.7, 74.4] | 61.7 [49.0, 72.9] | 30.0 [19.9, 42.5] | 3.3 | 5.0 | 23.4 | 24.92 |
| crazyflie | 5 m | frontier (region ignored) | 60 | 18.3 [10.6, 29.9] | 18.3 [10.6, 29.9] | 0.0 [0.0, 6.0] | 18.3 | 63.3 | 135.4 | 140.48 |
| crazyflie | 5 m | nominal_frontier | 60 | 55.0 [42.5, 66.9] | 53.3 [40.9, 65.4] | 21.7 [13.1, 33.6] | 5.0 | 20.0 | 70.8 | 71.78 |
| crazyflie | 5 m | lawnmower | 60 | 40.0 [28.6, 52.6] | 40.0 [28.6, 52.6] | 43.3 [31.6, 55.9] | 0.0 | 16.7 | 35.15 | 36.8 |
| crazyflie | 5 m | random_walk | 60 | 46.7 [34.6, 59.1] | 46.7 [34.6, 59.1] | 38.3 [27.1, 51.0] | 6.7 | 8.3 | 26.8 | 28.52 |
| crazyflie | unknown | frontier (region ignored) | 60 | 18.3 [10.6, 29.9] | 18.3 [10.6, 29.9] | 0.0 [0.0, 6.0] | 18.3 | 63.3 | 135.4 | 140.48 |
| crazyflie | unknown | nominal_frontier (= frontier) | 60 | 18.3 [10.6, 29.9] | 18.3 [10.6, 29.9] | 0.0 [0.0, 6.0] | 18.3 | 63.3 | 135.4 | 140.48 |
| crazyflie | unknown | lawnmower | 60 | 10.0 [4.7, 20.1] | 10.0 [4.7, 20.1] | 51.7 [39.3, 63.8] | 6.7 | 31.7 | 158.45 | 160.06 |
| crazyflie | unknown | random_walk | 60 | 6.7 [2.6, 15.9] | 6.7 [2.6, 15.9] | 53.3 [40.9, 65.4] | 0.0 | 40.0 | 63.8 | 66.98 |

## Per family

| family / preset | region | arm | n | found % [95 % CI] | reached % [95 % CI] | collision % [95 % CI] | stuck % | timeout % | median time to find s | median time to B s |
|---|---|---|---|---|---|---|---|---|---|---|
| random / ideal | B given | oracle | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 0.0 | 18.93 |
| random / ideal | 0 m | frontier (region ignored) | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 0.0 [0.0, 16.1] | 50.0 | 0.0 | 61.95 | 64.28 |
| random / ideal | 0 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.35 | 18.93 |
| random / ideal | 0 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.35 | 18.93 |
| random / ideal | 0 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.35 | 18.93 |
| random / ideal | 2 m | frontier (region ignored) | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 0.0 [0.0, 16.1] | 50.0 | 0.0 | 61.95 | 64.28 |
| random / ideal | 2 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.3 | 18.97 |
| random / ideal | 2 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.6 | 19.28 |
| random / ideal | 2 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.3 | 18.92 |
| random / ideal | 5 m | frontier (region ignored) | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 0.0 [0.0, 16.1] | 50.0 | 0.0 | 61.95 | 64.28 |
| random / ideal | 5 m | nominal_frontier | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 5.0 | 0.0 | 17.3 | 19.3 |
| random / ideal | 5 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 26.8 | 28.51 |
| random / ideal | 5 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 19.3 | 20.99 |
| random / ideal | unknown | frontier (region ignored) | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 0.0 [0.0, 16.1] | 50.0 | 0.0 | 61.95 | 64.28 |
| random / ideal | unknown | nominal_frontier (= frontier) | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 0.0 [0.0, 16.1] | 50.0 | 0.0 | 61.95 | 64.28 |
| random / ideal | unknown | lawnmower | 20 | 80.0 [58.4, 91.9] | 75.0 [53.1, 88.8] | 10.0 [2.8, 30.1] | 0.0 | 15.0 | 158.0 | 154.1 |
| random / ideal | unknown | random_walk | 20 | 20.0 [8.1, 41.6] | 20.0 [8.1, 41.6] | 0.0 [0.0, 16.1] | 0.0 | 80.0 | 109.55 | 111.46 |
| random / crazyflie | B given | oracle | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 0.0 | 21.8 |
| random / crazyflie | 0 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 0.0 | 90.0 | 152.1 | 154.06 |
| random / crazyflie | 0 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.2 | 21.8 |
| random / crazyflie | 0 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.2 | 21.8 |
| random / crazyflie | 0 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.2 | 21.8 |
| random / crazyflie | 2 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 0.0 | 90.0 | 152.1 | 154.06 |
| random / crazyflie | 2 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 22.15 | 23.82 |
| random / crazyflie | 2 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.0 | 21.63 |
| random / crazyflie | 2 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.2 | 22.19 |
| random / crazyflie | 5 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 0.0 | 90.0 | 152.1 | 154.06 |
| random / crazyflie | 5 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 32.2 | 33.86 |
| random / crazyflie | 5 m | lawnmower | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 10.0 [2.8, 30.1] | 0.0 | 0.0 | 26.15 | 29.54 |
| random / crazyflie | 5 m | random_walk | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 5.0 [0.9, 23.6] | 0.0 | 0.0 | 23.2 | 25.04 |
| random / crazyflie | unknown | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 0.0 | 90.0 | 152.1 | 154.06 |
| random / crazyflie | unknown | nominal_frontier (= frontier) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 0.0 | 90.0 | 152.1 | 154.06 |
| random / crazyflie | unknown | lawnmower | 20 | 20.0 [8.1, 41.6] | 20.0 [8.1, 41.6] | 45.0 [25.8, 65.8] | 0.0 | 35.0 | 162.65 | 164.27 |
| random / crazyflie | unknown | random_walk | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 30.0 [14.5, 51.9] | 0.0 | 65.0 | 87.2 | 89.06 |
| office / ideal | B given | oracle | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 0.0 | 22.82 |
| office / ideal | 0 m | frontier (region ignored) | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 5.0 | 25.0 | 100.25 | 103.43 |
| office / ideal | 0 m | nominal_frontier | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 0.0 | 5.0 | 19.8 | 22.76 |
| office / ideal | 0 m | lawnmower | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 0.0 | 5.0 | 19.8 | 22.76 |
| office / ideal | 0 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.1 | 22.83 |
| office / ideal | 2 m | frontier (region ignored) | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 5.0 | 25.0 | 100.25 | 103.43 |
| office / ideal | 2 m | nominal_frontier | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 0.0 [0.0, 16.1] | 0.0 | 10.0 | 23.05 | 25.18 |
| office / ideal | 2 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 31.4 | 33.92 |
| office / ideal | 2 m | random_walk | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 0.0 | 5.0 | 24.6 | 29.14 |
| office / ideal | 5 m | frontier (region ignored) | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 5.0 | 25.0 | 100.25 | 103.43 |
| office / ideal | 5 m | nominal_frontier | 20 | 80.0 [58.4, 91.9] | 80.0 [58.4, 91.9] | 0.0 [0.0, 16.1] | 10.0 | 10.0 | 59.35 | 62.92 |
| office / ideal | 5 m | lawnmower | 20 | 75.0 [53.1, 88.8] | 75.0 [53.1, 88.8] | 5.0 [0.9, 23.6] | 0.0 | 20.0 | 70.4 | 74.86 |
| office / ideal | 5 m | random_walk | 20 | 85.0 [64.0, 94.8] | 85.0 [64.0, 94.8] | 0.0 [0.0, 16.1] | 0.0 | 15.0 | 66.1 | 70.72 |
| office / ideal | unknown | frontier (region ignored) | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 5.0 | 25.0 | 100.25 | 103.43 |
| office / ideal | unknown | nominal_frontier (= frontier) | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 5.0 | 25.0 | 100.25 | 103.43 |
| office / ideal | unknown | lawnmower | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 5.0 [0.9, 23.6] | 0.0 | 80.0 | 94.9 | 99.7 |
| office / ideal | unknown | random_walk | 20 | 25.0 [11.2, 46.9] | 25.0 [11.2, 46.9] | 5.0 [0.9, 23.6] | 0.0 | 70.0 | 38.2 | 42.44 |
| office / crazyflie | B given | oracle | 20 | 100.0 [83.9, 100.0] | 40.0 [21.9, 61.3] | 50.0 [29.9, 70.1] | 5.0 | 5.0 | 0.0 | 20.85 |
| office / crazyflie | 0 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 45.0 | 45.0 | 32.9 | 35.51 |
| office / crazyflie | 0 m | nominal_frontier | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 40.0 [21.9, 61.3] | 0.0 | 10.0 | 23.3 | 25.71 |
| office / crazyflie | 0 m | lawnmower | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 40.0 [21.9, 61.3] | 0.0 | 10.0 | 23.1 | 25.71 |
| office / crazyflie | 0 m | random_walk | 20 | 45.0 [25.8, 65.8] | 45.0 [25.8, 65.8] | 50.0 [29.9, 70.1] | 5.0 | 0.0 | 20.4 | 22.0 |
| office / crazyflie | 2 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 45.0 | 45.0 | 32.9 | 35.51 |
| office / crazyflie | 2 m | nominal_frontier | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 45.0 [25.8, 65.8] | 5.0 | 0.0 | 33.25 | 36.5 |
| office / crazyflie | 2 m | lawnmower | 20 | 40.0 [21.9, 61.3] | 35.0 [18.1, 56.7] | 55.0 [34.2, 74.2] | 10.0 | 0.0 | 22.35 | 25.3 |
| office / crazyflie | 2 m | random_walk | 20 | 55.0 [34.2, 74.2] | 50.0 [29.9, 70.1] | 45.0 [25.8, 65.8] | 0.0 | 5.0 | 27.3 | 31.42 |
| office / crazyflie | 5 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 45.0 | 45.0 | 32.9 | 35.51 |
| office / crazyflie | 5 m | nominal_frontier | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 20.0 [8.1, 41.6] | 15.0 | 30.0 | 82.3 | 84.34 |
| office / crazyflie | 5 m | lawnmower | 20 | 25.0 [11.2, 46.9] | 25.0 [11.2, 46.9] | 55.0 [34.2, 74.2] | 0.0 | 20.0 | 53.3 | 56.06 |
| office / crazyflie | 5 m | random_walk | 20 | 30.0 [14.5, 51.9] | 30.0 [14.5, 51.9] | 45.0 [25.8, 65.8] | 10.0 | 15.0 | 117.5 | 119.89 |
| office / crazyflie | unknown | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 45.0 | 45.0 | 32.9 | 35.51 |
| office / crazyflie | unknown | nominal_frontier (= frontier) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 45.0 | 45.0 | 32.9 | 35.51 |
| office / crazyflie | unknown | lawnmower | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 60.0 [38.7, 78.1] | 20.0 | 10.0 | 82.65 | 86.27 |
| office / crazyflie | unknown | random_walk | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 65.0 [43.3, 81.9] | 0.0 | 20.0 | 40.4 | 44.9 |
| warehouse / ideal | B given | oracle | 20 | 100.0 [83.9, 100.0] | 80.0 [58.4, 91.9] | 0.0 [0.0, 16.1] | 0.0 | 20.0 | 0.0 | 51.9 |
| warehouse / ideal | 0 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 [0.0, 16.1] | 0.0 | 95.0 | 75.0 | 77.54 |
| warehouse / ideal | 0 m | nominal_frontier | 20 | 80.0 [58.4, 91.9] | 80.0 [58.4, 91.9] | 0.0 [0.0, 16.1] | 0.0 | 20.0 | 49.65 | 52.54 |
| warehouse / ideal | 0 m | lawnmower | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 0.0 | 30.0 | 42.7 | 45.28 |
| warehouse / ideal | 0 m | random_walk | 20 | 85.0 [64.0, 94.8] | 85.0 [64.0, 94.8] | 0.0 [0.0, 16.1] | 0.0 | 15.0 | 56.6 | 59.6 |
| warehouse / ideal | 2 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 [0.0, 16.1] | 0.0 | 95.0 | 75.0 | 77.54 |
| warehouse / ideal | 2 m | nominal_frontier | 20 | 75.0 [53.1, 88.8] | 75.0 [53.1, 88.8] | 0.0 [0.0, 16.1] | 0.0 | 25.0 | 43.9 | 46.44 |
| warehouse / ideal | 2 m | lawnmower | 20 | 75.0 [53.1, 88.8] | 75.0 [53.1, 88.8] | 0.0 [0.0, 16.1] | 0.0 | 25.0 | 47.7 | 50.64 |
| warehouse / ideal | 2 m | random_walk | 20 | 65.0 [43.3, 81.9] | 65.0 [43.3, 81.9] | 0.0 [0.0, 16.1] | 0.0 | 35.0 | 43.8 | 46.36 |
| warehouse / ideal | 5 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 [0.0, 16.1] | 0.0 | 95.0 | 75.0 | 77.54 |
| warehouse / ideal | 5 m | nominal_frontier | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 0.0 | 30.0 | 65.3 | 67.64 |
| warehouse / ideal | 5 m | lawnmower | 20 | 75.0 [53.1, 88.8] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 0.0 | 30.0 | 128.1 | 126.88 |
| warehouse / ideal | 5 m | random_walk | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 0.0 | 30.0 | 63.15 | 65.47 |
| warehouse / ideal | unknown | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 [0.0, 16.1] | 0.0 | 95.0 | 75.0 | 77.54 |
| warehouse / ideal | unknown | nominal_frontier (= frontier) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 [0.0, 16.1] | 0.0 | 95.0 | 75.0 | 77.54 |
| warehouse / ideal | unknown | lawnmower | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 0.0 | 100.0 | - | - |
| warehouse / ideal | unknown | random_walk | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 0.0 [0.0, 16.1] | 0.0 | 90.0 | 102.2 | 104.02 |
| warehouse / crazyflie | B given | oracle | 20 | 100.0 [83.9, 100.0] | 30.0 [14.5, 51.9] | 65.0 [43.3, 81.9] | 5.0 | 0.0 | 0.0 | 137.04 |
| warehouse / crazyflie | 0 m | frontier (region ignored) | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 0.0 [0.0, 16.1] | 10.0 | 55.0 | 135.4 | 140.48 |
| warehouse / crazyflie | 0 m | nominal_frontier | 20 | 25.0 [11.2, 46.9] | 25.0 [11.2, 46.9] | 45.0 [25.8, 65.8] | 5.0 | 25.0 | 100.7 | 105.76 |
| warehouse / crazyflie | 0 m | lawnmower | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 50.0 [29.9, 70.1] | 5.0 | 35.0 | 70.05 | 73.78 |
| warehouse / crazyflie | 0 m | random_walk | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 55.0 [34.2, 74.2] | 5.0 | 5.0 | 129.8 | 132.4 |
| warehouse / crazyflie | 2 m | frontier (region ignored) | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 0.0 [0.0, 16.1] | 10.0 | 55.0 | 135.4 | 140.48 |
| warehouse / crazyflie | 2 m | nominal_frontier | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 75.0 [53.1, 88.8] | 5.0 | 20.0 | - | - |
| warehouse / crazyflie | 2 m | lawnmower | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 50.0 [29.9, 70.1] | 5.0 | 30.0 | 80.4 | 86.52 |
| warehouse / crazyflie | 2 m | random_walk | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 45.0 [25.8, 65.8] | 10.0 | 10.0 | 84.0 | 87.68 |
| warehouse / crazyflie | 5 m | frontier (region ignored) | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 0.0 [0.0, 16.1] | 10.0 | 55.0 | 135.4 | 140.48 |
| warehouse / crazyflie | 5 m | nominal_frontier | 20 | 30.0 [14.5, 51.9] | 25.0 [11.2, 46.9] | 45.0 [25.8, 65.8] | 0.0 | 30.0 | 100.7 | 113.76 |
| warehouse / crazyflie | 5 m | lawnmower | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 65.0 [43.3, 81.9] | 0.0 | 30.0 | 175.3 | 177.82 |
| warehouse / crazyflie | 5 m | random_walk | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 65.0 [43.3, 81.9] | 10.0 | 10.0 | 128.6 | 132.86 |
| warehouse / crazyflie | unknown | frontier (region ignored) | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 0.0 [0.0, 16.1] | 10.0 | 55.0 | 135.4 | 140.48 |
| warehouse / crazyflie | unknown | nominal_frontier (= frontier) | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 0.0 [0.0, 16.1] | 10.0 | 55.0 | 135.4 | 140.48 |
| warehouse / crazyflie | unknown | lawnmower | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 50.0 [29.9, 70.1] | 0.0 | 50.0 | - | - |
| warehouse / crazyflie | unknown | random_walk | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 65.0 [43.3, 81.9] | 0.0 | 35.0 | - | - |

## Collisions (272 runs)

- random ideal layout 3 lawnmower region unknown: t 100.92 s, found False, min clearance 0.1489 m
- random ideal layout 7 lawnmower region unknown: t 99.18 s, found False, min clearance 0.1491 m
- random crazyflie layout 1 lawnmower region 5 m: t 23.32 s, found False, min clearance 0.1474 m
- random crazyflie layout 1 random_walk region unknown: t 107.72 s, found False, min clearance 0.1496 m
- random crazyflie layout 2 lawnmower region unknown: t 83.46 s, found False, min clearance 0.1492 m
- random crazyflie layout 6 lawnmower region unknown: t 115.62 s, found False, min clearance 0.1492 m
- random crazyflie layout 6 random_walk region unknown: t 161.34 s, found False, min clearance 0.1487 m
- random crazyflie layout 7 lawnmower region unknown: t 144.76 s, found False, min clearance 0.1481 m
- random crazyflie layout 9 lawnmower region unknown: t 70.66 s, found False, min clearance 0.1487 m
- random crazyflie layout 11 lawnmower region unknown: t 63.24 s, found False, min clearance 0.1488 m
- random crazyflie layout 13 lawnmower region 5 m: t 35.04 s, found False, min clearance 0.1476 m
- random crazyflie layout 14 random_walk region 5 m: t 32.98 s, found False, min clearance 0.1476 m
- random crazyflie layout 14 random_walk region unknown: t 53.16 s, found False, min clearance 0.1484 m
- random crazyflie layout 15 lawnmower region unknown: t 34.18 s, found False, min clearance 0.1486 m
- random crazyflie layout 15 random_walk region unknown: t 9.34 s, found False, min clearance 0.1496 m
- random crazyflie layout 16 lawnmower region unknown: t 108.06 s, found False, min clearance 0.1486 m
- random crazyflie layout 16 random_walk region unknown: t 166.92 s, found False, min clearance 0.1484 m
- random crazyflie layout 17 lawnmower region unknown: t 9.88 s, found False, min clearance 0.15 m
- random crazyflie layout 18 lawnmower region unknown: t 16.82 s, found False, min clearance 0.1491 m
- random crazyflie layout 19 random_walk region unknown: t 34.38 s, found False, min clearance 0.1499 m
- office ideal layout 2 lawnmower region unknown: t 150.16 s, found False, min clearance 0.1483 m
- office ideal layout 6 lawnmower region 5 m: t 47.36 s, found False, min clearance 0.1489 m
- office ideal layout 10 random_walk region unknown: t 136.8 s, found False, min clearance 0.1493 m
- office crazyflie layout 0 lawnmower region 2 m: t 39.24 s, found False, min clearance 0.1486 m
- office crazyflie layout 0 lawnmower region unknown: t 7.12 s, found False, min clearance 0.1471 m
- office crazyflie layout 1 oracle region unknown: t 39.48 s, found True, min clearance 0.1461 m
- office crazyflie layout 1 random_walk region 0 m: t 39.48 s, found False, min clearance 0.1458 m
- office crazyflie layout 1 random_walk region 2 m: t 53.94 s, found False, min clearance 0.1496 m
- office crazyflie layout 2 lawnmower region 2 m: t 55.5 s, found True, min clearance 0.1461 m
- office crazyflie layout 2 lawnmower region 5 m: t 7.64 s, found False, min clearance 0.1496 m
- office crazyflie layout 2 lawnmower region unknown: t 15.72 s, found False, min clearance 0.1491 m
- office crazyflie layout 2 random_walk region unknown: t 14.42 s, found False, min clearance 0.1499 m
- office crazyflie layout 3 nominal_frontier region 2 m: t 5.34 s, found False, min clearance 0.1499 m
- office crazyflie layout 3 lawnmower region 2 m: t 6.38 s, found False, min clearance 0.1494 m
- office crazyflie layout 3 random_walk region 2 m: t 10.78 s, found False, min clearance 0.149 m
- office crazyflie layout 3 random_walk region unknown: t 17.8 s, found False, min clearance 0.1486 m
- office crazyflie layout 4 oracle region unknown: t 6.94 s, found True, min clearance 0.1473 m
- office crazyflie layout 4 nominal_frontier region 0 m: t 6.86 s, found False, min clearance 0.1477 m
- office crazyflie layout 4 lawnmower region 0 m: t 6.86 s, found False, min clearance 0.1477 m
- office crazyflie layout 4 random_walk region 0 m: t 6.86 s, found False, min clearance 0.1477 m
- office crazyflie layout 4 nominal_frontier region 2 m: t 6.8 s, found False, min clearance 0.1498 m
- office crazyflie layout 4 lawnmower region 2 m: t 6.78 s, found False, min clearance 0.148 m
- office crazyflie layout 4 random_walk region 2 m: t 62.2 s, found True, min clearance 0.1498 m
- office crazyflie layout 4 nominal_frontier region 5 m: t 10.9 s, found False, min clearance 0.1499 m
- office crazyflie layout 4 lawnmower region 5 m: t 11.02 s, found False, min clearance 0.1443 m
- office crazyflie layout 4 random_walk region 5 m: t 7.74 s, found False, min clearance 0.1476 m
- office crazyflie layout 4 random_walk region unknown: t 9.66 s, found False, min clearance 0.1463 m
- office crazyflie layout 5 oracle region unknown: t 90.84 s, found True, min clearance 0.1496 m
- office crazyflie layout 5 nominal_frontier region 2 m: t 9.94 s, found False, min clearance 0.1473 m
- office crazyflie layout 5 random_walk region 2 m: t 11.0 s, found False, min clearance 0.1472 m
- office crazyflie layout 5 lawnmower region 5 m: t 55.8 s, found False, min clearance 0.1469 m
- office crazyflie layout 5 random_walk region 5 m: t 13.58 s, found False, min clearance 0.1487 m
- office crazyflie layout 5 lawnmower region unknown: t 16.7 s, found False, min clearance 0.1478 m
- office crazyflie layout 5 random_walk region unknown: t 13.34 s, found False, min clearance 0.147 m
- office crazyflie layout 6 oracle region unknown: t 23.98 s, found True, min clearance 0.1495 m
- office crazyflie layout 6 nominal_frontier region 0 m: t 23.92 s, found False, min clearance 0.1471 m
- office crazyflie layout 6 lawnmower region 0 m: t 23.92 s, found False, min clearance 0.1471 m
- office crazyflie layout 6 random_walk region 0 m: t 23.92 s, found False, min clearance 0.1471 m
- office crazyflie layout 6 nominal_frontier region 2 m: t 15.02 s, found False, min clearance 0.1494 m
- office crazyflie layout 6 lawnmower region 2 m: t 15.66 s, found False, min clearance 0.1489 m
- office crazyflie layout 6 lawnmower region 5 m: t 21.92 s, found False, min clearance 0.147 m
- office crazyflie layout 6 random_walk region 5 m: t 46.14 s, found False, min clearance 0.1475 m
- office crazyflie layout 6 lawnmower region unknown: t 17.52 s, found False, min clearance 0.1473 m
- office crazyflie layout 7 oracle region unknown: t 27.76 s, found True, min clearance 0.1484 m
- office crazyflie layout 7 nominal_frontier region 0 m: t 27.76 s, found False, min clearance 0.1484 m
- office crazyflie layout 7 lawnmower region 0 m: t 27.76 s, found False, min clearance 0.1484 m
- office crazyflie layout 7 random_walk region 0 m: t 27.76 s, found False, min clearance 0.1484 m
- office crazyflie layout 7 nominal_frontier region 2 m: t 10.66 s, found False, min clearance 0.1499 m
- office crazyflie layout 7 random_walk region 2 m: t 2.0 s, found False, min clearance 0.1447 m
- office crazyflie layout 7 random_walk region 5 m: t 10.54 s, found False, min clearance 0.15 m
- office crazyflie layout 7 lawnmower region unknown: t 6.18 s, found False, min clearance 0.146 m
- office crazyflie layout 7 random_walk region unknown: t 7.02 s, found False, min clearance 0.1497 m
- office crazyflie layout 8 nominal_frontier region 2 m: t 33.2 s, found False, min clearance 0.1478 m
- office crazyflie layout 8 lawnmower region 2 m: t 2.52 s, found False, min clearance 0.1485 m
- office crazyflie layout 8 lawnmower region 5 m: t 14.1 s, found False, min clearance 0.15 m
- office crazyflie layout 8 random_walk region 5 m: t 11.84 s, found False, min clearance 0.1485 m
- office crazyflie layout 8 lawnmower region unknown: t 35.56 s, found False, min clearance 0.1499 m
- office crazyflie layout 8 random_walk region unknown: t 51.36 s, found False, min clearance 0.1483 m
- office crazyflie layout 9 lawnmower region 2 m: t 13.58 s, found False, min clearance 0.1498 m
- office crazyflie layout 9 random_walk region 5 m: t 18.88 s, found False, min clearance 0.1498 m
- office crazyflie layout 9 lawnmower region unknown: t 8.14 s, found False, min clearance 0.1477 m
- office crazyflie layout 9 random_walk region unknown: t 16.0 s, found False, min clearance 0.1461 m
- office crazyflie layout 10 oracle region unknown: t 9.3 s, found True, min clearance 0.1487 m
- office crazyflie layout 10 nominal_frontier region 0 m: t 9.3 s, found False, min clearance 0.1487 m
- office crazyflie layout 10 lawnmower region 0 m: t 9.3 s, found False, min clearance 0.1487 m
- office crazyflie layout 10 random_walk region 0 m: t 9.3 s, found False, min clearance 0.1487 m
- office crazyflie layout 10 lawnmower region 2 m: t 75.0 s, found False, min clearance 0.1466 m
- office crazyflie layout 10 random_walk region 5 m: t 90.62 s, found False, min clearance 0.1482 m
- office crazyflie layout 10 random_walk region unknown: t 127.36 s, found False, min clearance 0.1484 m
- office crazyflie layout 11 oracle region unknown: t 15.84 s, found True, min clearance 0.1464 m
- office crazyflie layout 11 nominal_frontier region 0 m: t 15.84 s, found False, min clearance 0.1464 m
- office crazyflie layout 11 lawnmower region 0 m: t 15.84 s, found False, min clearance 0.1464 m
- office crazyflie layout 11 random_walk region 0 m: t 15.84 s, found False, min clearance 0.1464 m
- office crazyflie layout 11 nominal_frontier region 2 m: t 6.06 s, found False, min clearance 0.1487 m
- office crazyflie layout 11 random_walk region 2 m: t 25.3 s, found False, min clearance 0.1488 m
- office crazyflie layout 11 nominal_frontier region 5 m: t 6.18 s, found False, min clearance 0.1468 m
- office crazyflie layout 11 lawnmower region 5 m: t 15.54 s, found False, min clearance 0.1466 m
- office crazyflie layout 11 random_walk region 5 m: t 11.82 s, found False, min clearance 0.1489 m
- office crazyflie layout 11 random_walk region unknown: t 8.28 s, found False, min clearance 0.1481 m
- office crazyflie layout 12 oracle region unknown: t 24.76 s, found True, min clearance 0.1451 m
- office crazyflie layout 12 nominal_frontier region 0 m: t 24.76 s, found False, min clearance 0.1447 m
- office crazyflie layout 12 lawnmower region 0 m: t 24.76 s, found False, min clearance 0.1447 m
- office crazyflie layout 12 random_walk region 0 m: t 24.76 s, found False, min clearance 0.1447 m
- office crazyflie layout 12 lawnmower region 2 m: t 19.08 s, found False, min clearance 0.1497 m
- office crazyflie layout 12 lawnmower region 5 m: t 21.0 s, found False, min clearance 0.1473 m
- office crazyflie layout 12 lawnmower region unknown: t 6.58 s, found False, min clearance 0.1478 m
- office crazyflie layout 12 random_walk region unknown: t 6.22 s, found False, min clearance 0.1486 m
- office crazyflie layout 13 random_walk region 2 m: t 26.1 s, found False, min clearance 0.1488 m
- office crazyflie layout 13 lawnmower region 5 m: t 12.82 s, found False, min clearance 0.1482 m
- office crazyflie layout 13 lawnmower region unknown: t 36.06 s, found False, min clearance 0.1497 m
- office crazyflie layout 13 random_walk region unknown: t 20.18 s, found False, min clearance 0.1464 m
- office crazyflie layout 14 lawnmower region unknown: t 20.98 s, found False, min clearance 0.1483 m
- office crazyflie layout 15 random_walk region 2 m: t 63.94 s, found False, min clearance 0.1471 m
- office crazyflie layout 15 lawnmower region 5 m: t 8.84 s, found False, min clearance 0.145 m
- office crazyflie layout 15 lawnmower region unknown: t 7.32 s, found False, min clearance 0.1499 m
- office crazyflie layout 15 random_walk region unknown: t 6.1 s, found False, min clearance 0.15 m
- office crazyflie layout 16 nominal_frontier region 0 m: t 19.94 s, found False, min clearance 0.146 m
- office crazyflie layout 16 lawnmower region 0 m: t 19.94 s, found False, min clearance 0.146 m
- office crazyflie layout 16 random_walk region 0 m: t 19.94 s, found False, min clearance 0.146 m
- office crazyflie layout 16 nominal_frontier region 2 m: t 28.46 s, found False, min clearance 0.1492 m
- office crazyflie layout 16 lawnmower region 2 m: t 74.46 s, found False, min clearance 0.1497 m
- office crazyflie layout 16 nominal_frontier region 5 m: t 27.42 s, found False, min clearance 0.1495 m
- office crazyflie layout 16 lawnmower region 5 m: t 83.62 s, found False, min clearance 0.1455 m
- office crazyflie layout 16 lawnmower region unknown: t 11.6 s, found False, min clearance 0.1491 m
- office crazyflie layout 18 oracle region unknown: t 7.68 s, found True, min clearance 0.1468 m
- office crazyflie layout 18 nominal_frontier region 0 m: t 7.68 s, found False, min clearance 0.147 m
- office crazyflie layout 18 lawnmower region 0 m: t 7.68 s, found False, min clearance 0.147 m
- office crazyflie layout 18 random_walk region 0 m: t 7.68 s, found False, min clearance 0.147 m
- office crazyflie layout 18 nominal_frontier region 2 m: t 21.44 s, found False, min clearance 0.1463 m
- office crazyflie layout 18 lawnmower region 2 m: t 7.5 s, found False, min clearance 0.1467 m
- office crazyflie layout 18 random_walk region 2 m: t 7.5 s, found False, min clearance 0.1479 m
- office crazyflie layout 18 nominal_frontier region 5 m: t 7.82 s, found False, min clearance 0.1484 m
- office crazyflie layout 18 lawnmower region 5 m: t 21.3 s, found False, min clearance 0.1486 m
- office crazyflie layout 18 random_walk region 5 m: t 22.02 s, found False, min clearance 0.1467 m
- office crazyflie layout 18 random_walk region unknown: t 18.96 s, found False, min clearance 0.1491 m
- office crazyflie layout 19 oracle region unknown: t 24.7 s, found True, min clearance 0.1495 m
- office crazyflie layout 19 random_walk region 0 m: t 24.68 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 0 lawnmower region 0 m: t 126.86 s, found False, min clearance 0.1494 m
- warehouse crazyflie layout 0 lawnmower region 2 m: t 15.3 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 0 nominal_frontier region 5 m: t 86.68 s, found True, min clearance 0.149 m
- warehouse crazyflie layout 0 lawnmower region 5 m: t 102.22 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 0 lawnmower region unknown: t 71.52 s, found False, min clearance 0.1474 m
- warehouse crazyflie layout 1 nominal_frontier region 2 m: t 65.76 s, found False, min clearance 0.1482 m
- warehouse crazyflie layout 1 lawnmower region 5 m: t 25.86 s, found False, min clearance 0.1494 m
- warehouse crazyflie layout 2 random_walk region 0 m: t 120.62 s, found False, min clearance 0.1498 m
- warehouse crazyflie layout 2 random_walk region 5 m: t 55.3 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 2 random_walk region unknown: t 178.42 s, found False, min clearance 0.1463 m
- warehouse crazyflie layout 3 oracle region unknown: t 72.38 s, found True, min clearance 0.1491 m
- warehouse crazyflie layout 3 random_walk region 0 m: t 106.74 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 3 nominal_frontier region 2 m: t 45.62 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 3 lawnmower region 2 m: t 50.62 s, found False, min clearance 0.147 m
- warehouse crazyflie layout 3 random_walk region 2 m: t 143.26 s, found False, min clearance 0.1465 m
- warehouse crazyflie layout 3 lawnmower region 5 m: t 21.52 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 3 random_walk region 5 m: t 22.42 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 3 lawnmower region unknown: t 152.92 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 4 oracle region unknown: t 42.66 s, found True, min clearance 0.1483 m
- warehouse crazyflie layout 4 nominal_frontier region 0 m: t 42.68 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 4 lawnmower region 0 m: t 42.68 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 4 random_walk region 0 m: t 42.68 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 4 nominal_frontier region 2 m: t 82.94 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 4 random_walk region 5 m: t 49.12 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 4 random_walk region unknown: t 119.56 s, found False, min clearance 0.1459 m
- warehouse crazyflie layout 5 oracle region unknown: t 73.6 s, found True, min clearance 0.1479 m
- warehouse crazyflie layout 5 nominal_frontier region 0 m: t 73.82 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 5 lawnmower region 0 m: t 73.82 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 5 random_walk region 0 m: t 73.82 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 5 nominal_frontier region 2 m: t 10.14 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 5 lawnmower region 2 m: t 10.14 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 5 random_walk region 2 m: t 10.14 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 5 lawnmower region 5 m: t 13.8 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 5 random_walk region 5 m: t 14.76 s, found False, min clearance 0.1496 m
- warehouse crazyflie layout 6 nominal_frontier region 2 m: t 21.58 s, found False, min clearance 0.1479 m
- warehouse crazyflie layout 6 nominal_frontier region 5 m: t 22.24 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 6 lawnmower region 5 m: t 21.84 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 6 random_walk region 5 m: t 23.84 s, found False, min clearance 0.1498 m
- warehouse crazyflie layout 6 lawnmower region unknown: t 27.4 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 6 random_walk region unknown: t 93.16 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 7 nominal_frontier region 2 m: t 45.82 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 7 lawnmower region 2 m: t 66.7 s, found False, min clearance 0.1486 m
- warehouse crazyflie layout 7 lawnmower region unknown: t 29.86 s, found False, min clearance 0.1449 m
- warehouse crazyflie layout 8 oracle region unknown: t 132.96 s, found True, min clearance 0.1487 m
- warehouse crazyflie layout 8 random_walk region 2 m: t 25.12 s, found False, min clearance 0.1481 m
- warehouse crazyflie layout 8 lawnmower region 5 m: t 43.7 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 8 random_walk region 5 m: t 24.8 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 8 lawnmower region unknown: t 18.06 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 8 random_walk region unknown: t 101.84 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 9 nominal_frontier region 2 m: t 36.46 s, found False, min clearance 0.1469 m
- warehouse crazyflie layout 9 lawnmower region 2 m: t 62.06 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 9 nominal_frontier region 5 m: t 32.88 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 9 lawnmower region 5 m: t 42.04 s, found False, min clearance 0.1499 m
- warehouse crazyflie layout 9 random_walk region 5 m: t 22.42 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 9 lawnmower region unknown: t 71.64 s, found False, min clearance 0.1496 m
- warehouse crazyflie layout 9 random_walk region unknown: t 30.64 s, found False, min clearance 0.146 m
- warehouse crazyflie layout 10 oracle region unknown: t 38.18 s, found True, min clearance 0.1488 m
- warehouse crazyflie layout 10 nominal_frontier region 0 m: t 67.22 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 10 lawnmower region 0 m: t 67.22 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 10 random_walk region 0 m: t 67.22 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 10 nominal_frontier region 2 m: t 9.6 s, found False, min clearance 0.1484 m
- warehouse crazyflie layout 10 random_walk region 2 m: t 9.64 s, found False, min clearance 0.1496 m
- warehouse crazyflie layout 10 nominal_frontier region 5 m: t 45.84 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 10 lawnmower region 5 m: t 43.52 s, found False, min clearance 0.1473 m
- warehouse crazyflie layout 10 random_walk region 5 m: t 27.48 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 10 random_walk region unknown: t 73.04 s, found False, min clearance 0.1486 m
- warehouse crazyflie layout 11 oracle region unknown: t 37.86 s, found True, min clearance 0.1493 m
- warehouse crazyflie layout 11 nominal_frontier region 0 m: t 37.86 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 11 lawnmower region 0 m: t 37.86 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 11 random_walk region 0 m: t 37.86 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 11 nominal_frontier region 2 m: t 38.86 s, found False, min clearance 0.1467 m
- warehouse crazyflie layout 11 lawnmower region 2 m: t 122.0 s, found False, min clearance 0.1499 m
- warehouse crazyflie layout 11 random_walk region unknown: t 49.34 s, found False, min clearance 0.1453 m
- warehouse crazyflie layout 12 oracle region unknown: t 61.0 s, found True, min clearance 0.1486 m
- warehouse crazyflie layout 12 nominal_frontier region 2 m: t 75.66 s, found False, min clearance 0.148 m
- warehouse crazyflie layout 12 nominal_frontier region 5 m: t 28.8 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 12 lawnmower region 5 m: t 75.44 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 13 oracle region unknown: t 44.4 s, found True, min clearance 0.1477 m
- warehouse crazyflie layout 13 nominal_frontier region 2 m: t 64.08 s, found False, min clearance 0.1461 m
- warehouse crazyflie layout 13 lawnmower region 5 m: t 108.92 s, found False, min clearance 0.15 m
- warehouse crazyflie layout 13 random_walk region 5 m: t 44.6 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 13 lawnmower region unknown: t 35.94 s, found False, min clearance 0.1496 m
- warehouse crazyflie layout 13 random_walk region unknown: t 7.5 s, found False, min clearance 0.1485 m
- warehouse crazyflie layout 14 oracle region unknown: t 32.12 s, found True, min clearance 0.1494 m
- warehouse crazyflie layout 14 nominal_frontier region 0 m: t 32.12 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 14 lawnmower region 0 m: t 32.12 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 14 random_walk region 0 m: t 32.12 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 14 nominal_frontier region 2 m: t 83.3 s, found False, min clearance 0.1448 m
- warehouse crazyflie layout 14 lawnmower region 2 m: t 170.1 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 14 random_walk region 2 m: t 30.08 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 14 nominal_frontier region 5 m: t 28.9 s, found False, min clearance 0.1494 m
- warehouse crazyflie layout 14 lawnmower region 5 m: t 88.04 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 14 random_walk region 5 m: t 96.32 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 14 lawnmower region unknown: t 12.1 s, found False, min clearance 0.1468 m
- warehouse crazyflie layout 15 oracle region unknown: t 50.78 s, found True, min clearance 0.1478 m
- warehouse crazyflie layout 15 nominal_frontier region 0 m: t 50.78 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 15 lawnmower region 0 m: t 50.78 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 15 random_walk region 0 m: t 50.78 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 15 lawnmower region 2 m: t 44.2 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 15 random_walk region 2 m: t 135.82 s, found False, min clearance 0.1474 m
- warehouse crazyflie layout 15 nominal_frontier region 5 m: t 26.12 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 15 lawnmower region 5 m: t 26.02 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 15 random_walk region 5 m: t 26.1 s, found False, min clearance 0.1498 m
- warehouse crazyflie layout 15 random_walk region unknown: t 109.58 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 16 oracle region unknown: t 16.26 s, found True, min clearance 0.1476 m
- warehouse crazyflie layout 16 nominal_frontier region 0 m: t 16.26 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 16 lawnmower region 0 m: t 16.26 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 16 random_walk region 0 m: t 16.26 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 16 nominal_frontier region 2 m: t 52.46 s, found False, min clearance 0.1481 m
- warehouse crazyflie layout 16 lawnmower region 2 m: t 56.06 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 16 random_walk region 2 m: t 63.6 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 16 lawnmower region 5 m: t 51.34 s, found False, min clearance 0.1479 m
- warehouse crazyflie layout 16 lawnmower region unknown: t 47.06 s, found False, min clearance 0.1463 m
- warehouse crazyflie layout 16 random_walk region unknown: t 26.8 s, found False, min clearance 0.1486 m
- warehouse crazyflie layout 17 oracle region unknown: t 109.56 s, found True, min clearance 0.1473 m
- warehouse crazyflie layout 17 nominal_frontier region 2 m: t 29.18 s, found False, min clearance 0.1483 m
- warehouse crazyflie layout 17 lawnmower region 2 m: t 130.6 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 17 random_walk region unknown: t 18.66 s, found False, min clearance 0.1485 m
- warehouse crazyflie layout 18 nominal_frontier region 0 m: t 75.82 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 18 lawnmower region 0 m: t 75.82 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 18 random_walk region 0 m: t 75.82 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 18 random_walk region 2 m: t 31.84 s, found False, min clearance 0.1485 m
- warehouse crazyflie layout 18 nominal_frontier region 5 m: t 43.46 s, found False, min clearance 0.1461 m
- warehouse crazyflie layout 18 random_walk region 5 m: t 40.82 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 18 lawnmower region unknown: t 49.82 s, found False, min clearance 0.1499 m
- warehouse crazyflie layout 18 random_walk region unknown: t 17.9 s, found False, min clearance 0.1485 m
- warehouse crazyflie layout 19 oracle region unknown: t 21.82 s, found True, min clearance 0.1477 m
- warehouse crazyflie layout 19 nominal_frontier region 0 m: t 21.78 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 19 lawnmower region 0 m: t 21.78 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 19 random_walk region 0 m: t 21.78 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 19 nominal_frontier region 2 m: t 72.3 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 19 random_walk region 2 m: t 136.58 s, found False, min clearance 0.1487 m
- warehouse crazyflie layout 19 nominal_frontier region 5 m: t 21.2 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 19 random_walk region 5 m: t 22.44 s, found False, min clearance 0.1473 m
- warehouse crazyflie layout 19 random_walk region unknown: t 48.02 s, found False, min clearance 0.1487 m
