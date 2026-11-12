`python analyze.py` on results/bench_0.json (synthetic). Map coverage = known-free area of the planner's log-odds map at the end of the run / free area of the true 0.1 m grid.

| preset | arm | region | outcome group | runs | median coverage | min | max |
|---|---|---|---|---|---|---|---|
| ideal | frontier | unknown | found B | 25 | 0.68 | 0.16 | 0.99 |
| ideal | frontier | unknown | not found, stuck (hovering) | 11 | 0.98 | 0.98 | 0.99 |
| ideal | frontier | unknown | not found, timeout | 24 | 0.80 | 0.44 | 0.98 |
| ideal | nominal_frontier | 5 m | found B | 49 | 0.64 | 0.23 | 0.71 |
| ideal | nominal_frontier | 5 m | not found, stuck (hovering) | 3 | 0.98 | 0.98 | 0.98 |
| ideal | nominal_frontier | 5 m | not found, timeout | 8 | 0.76 | 0.61 | 0.88 |
| ideal | lawnmower | unknown | found B | 19 | 0.98 | 0.61 | 0.99 |
| ideal | lawnmower | unknown | not found, timeout | 38 | 0.54 | 0.19 | 0.99 |
| ideal | lawnmower | unknown | not found, collision | 3 | 0.69 | 0.68 | 0.77 |
| crazyflie | frontier | unknown | found B | 11 | 0.35 | 0.06 | 0.57 |
| crazyflie | frontier | unknown | not found, stuck (hovering) | 11 | 0.03 | 0.02 | 0.04 |
| crazyflie | frontier | unknown | not found, timeout | 38 | 0.56 | 0.17 | 0.70 |
| crazyflie | nominal_frontier | 5 m | found B | 33 | 0.29 | 0.10 | 0.49 |
| crazyflie | nominal_frontier | 5 m | not found, stuck (hovering) | 3 | 0.03 | 0.03 | 0.38 |
| crazyflie | nominal_frontier | 5 m | not found, timeout | 12 | 0.29 | 0.12 | 0.46 |
| crazyflie | nominal_frontier | 5 m | not found, collision | 12 | 0.08 | 0.02 | 0.14 |
| crazyflie | lawnmower | unknown | found B | 6 | 0.88 | 0.40 | 0.90 |
| crazyflie | lawnmower | unknown | not found, stuck (hovering) | 4 | 0.03 | 0.03 | 0.03 |
| crazyflie | lawnmower | unknown | not found, timeout | 19 | 0.32 | 0.19 | 0.88 |
| crazyflie | lawnmower | unknown | not found, collision | 31 | 0.07 | 0.02 | 0.60 |

Ideal `frontier` runs stuck without B, rerun: 11 of 11 ended with no frontier left (last selection returned none, same outcome as bench).

Highest-coverage ideal `frontier` runs, rerun with dropout 0 (everything else equal):

| family | layout | coverage, ideal (2 % dropout) | coverage, dropout 0 |
|---|---|---|---|
| random | 4 | 0.99 | 0.97 |
| random | 15 | 0.99 | 0.98 |
| random | 3 | 0.99 | 0.98 |

## Headline (pooled over random, office, warehouse; same numbers as bench_0.md)

| region | arm | ideal found % [95 % CI] | ideal collision % [95 % CI] | ideal median time to find s | ideal median time to B s | crazyflie found % [95 % CI] | crazyflie collision % [95 % CI] | crazyflie median time to B s |
|---|---|---|---|---|---|---|---|---|
| B given | oracle | 100.0 [94.0, 100.0] | 0.0 [0.0, 6.0] | 0.0 | 22.05 | 100.0 [94.0, 100.0] | 38.3 [27.1, 51.0] | 23.39 |
| 0 m | nominal_frontier | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 19.8 | 21.82 | 58.3 [45.7, 69.9] | 28.3 [18.5, 40.8] | 23.46 |
| 0 m | lawnmower | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 19.1 | 21.68 | 53.3 [40.9, 65.4] | 30.0 [19.9, 42.5] | 22.29 |
| 0 m | random_walk | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 20.1 | 22.18 | 60.0 [47.4, 71.4] | 35.0 [24.2, 47.6] | 23.69 |
| 2 m | nominal_frontier | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 21.1 | 23.0 | 50.0 [37.7, 62.3] | 40.0 [28.6, 52.6] | 24.13 |
| 2 m | lawnmower | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 30.4 | 32.84 | 51.7 [39.3, 63.8] | 35.0 [24.2, 47.6] | 23.2 |
| 2 m | random_walk | 86.7 [75.8, 93.1] | 0.0 [0.0, 6.0] | 20.3 | 23.92 | 63.3 [50.7, 74.4] | 30.0 [19.9, 42.5] | 24.92 |
| 5 m | nominal_frontier | 81.7 [70.1, 89.4] | 0.0 [0.0, 6.0] | 26.3 | 30.88 | 55.0 [42.5, 66.9] | 21.7 [13.1, 33.6] | 71.78 |
| 5 m | lawnmower | 83.3 [72.0, 90.7] | 1.7 [0.3, 8.9] | 47.8 | 49.72 | 40.0 [28.6, 52.6] | 43.3 [31.6, 55.9] | 36.8 |
| 5 m | random_walk | 85.0 [73.9, 91.9] | 0.0 [0.0, 6.0] | 41.4 | 43.38 | 46.7 [34.6, 59.1] | 38.3 [27.1, 51.0] | 28.52 |
| unknown | frontier | 41.7 [30.1, 54.3] | 0.0 [0.0, 6.0] | 78.4 | 81.28 | 18.3 [10.6, 29.9] | 0.0 [0.0, 6.0] | 140.48 |
| unknown | lawnmower | 31.7 [21.3, 44.2] | 5.0 [1.7, 13.7] | 152.5 | 152.81 | 10.0 [4.7, 20.1] | 51.7 [39.3, 63.8] | 160.06 |
| unknown | random_walk | 18.3 [10.6, 29.9] | 1.7 [0.3, 8.9] | 91.4 | 95.04 | 6.7 [2.6, 15.9] | 53.3 [40.9, 65.4] | 66.98 |
