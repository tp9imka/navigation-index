`python analyze.py` on results/bench_0.json (synthetic). Map coverage = known-free area of the planner's log-odds map at the end of the run / free area of the true 0.1 m grid.

| preset | arm | region | outcome group | runs | median coverage | min | max |
|---|---|---|---|---|---|---|---|
| ideal | frontier | unknown | found B | 26 | 0.72 | 0.28 | 1.03 |
| ideal | frontier | unknown | not found, stuck (hovering) | 8 | 1.03 | 0.99 | 1.06 |
| ideal | frontier | unknown | not found, timeout | 23 | 1.02 | 0.52 | 1.25 |
| ideal | frontier | unknown | not found, collision | 3 | 0.36 | 0.33 | 0.83 |
| ideal | nominal_frontier | 5 m | found B | 49 | 0.67 | 0.32 | 0.99 |
| ideal | nominal_frontier | 5 m | not found, stuck (hovering) | 2 | 0.99 | 0.99 | 0.99 |
| ideal | nominal_frontier | 5 m | not found, timeout | 9 | 0.98 | 0.82 | 1.11 |
| ideal | lawnmower | unknown | found B | 16 | 1.01 | 0.62 | 1.04 |
| ideal | lawnmower | unknown | not found, timeout | 40 | 0.73 | 0.51 | 1.04 |
| ideal | lawnmower | unknown | not found, collision | 4 | 0.78 | 0.25 | 0.92 |
| crazyflie | frontier | unknown | found B | 2 | 0.44 | 0.40 | 0.48 |
| crazyflie | frontier | unknown | not found, stuck (hovering) | 9 | 0.05 | 0.03 | 0.18 |
| crazyflie | frontier | unknown | not found, timeout | 39 | 0.58 | 0.17 | 0.74 |
| crazyflie | frontier | unknown | not found, collision | 10 | 0.18 | 0.09 | 0.67 |
| crazyflie | nominal_frontier | 5 m | found B | 29 | 0.30 | 0.13 | 0.48 |
| crazyflie | nominal_frontier | 5 m | not found, stuck (hovering) | 5 | 0.10 | 0.04 | 0.47 |
| crazyflie | nominal_frontier | 5 m | not found, timeout | 7 | 0.37 | 0.16 | 0.39 |
| crazyflie | nominal_frontier | 5 m | not found, collision | 19 | 0.12 | 0.02 | 0.28 |
| crazyflie | lawnmower | unknown | found B | 5 | 0.72 | 0.43 | 0.91 |
| crazyflie | lawnmower | unknown | not found, stuck (hovering) | 1 | 0.04 | 0.04 | 0.04 |
| crazyflie | lawnmower | unknown | not found, timeout | 9 | 0.74 | 0.27 | 0.89 |
| crazyflie | lawnmower | unknown | not found, collision | 45 | 0.11 | 0.02 | 0.68 |

Ideal `frontier` runs stuck without B, rerun: 8 of 8 ended with no frontier left (last selection returned none, same outcome as bench).

Highest-coverage ideal `frontier` runs, rerun with dropout 0 (everything else equal):

| family | layout | coverage, ideal (2 % dropout) | coverage, dropout 0 |
|---|---|---|---|
| warehouse | 1 | 1.19 | 0.85 |
| warehouse | 2 | 1.20 | 0.79 |
| warehouse | 4 | 1.25 | 0.98 |

## Headline (pooled over random, office, warehouse; same numbers as bench_0.md)

| region | arm | ideal found % [95 % CI] | ideal collision % [95 % CI] | ideal median time to find s | ideal median time to B s | crazyflie found % [95 % CI] | crazyflie collision % [95 % CI] | crazyflie median time to B s |
|---|---|---|---|---|---|---|---|---|
| B given | oracle | 100.0 [94.0, 100.0] | 0.0 [0.0, 6.0] | 0.0 | 22.8 | 100.0 [94.0, 100.0] | 38.3 [27.1, 51.0] | 23.68 |
| 0 m | nominal_frontier | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 20.0 | 21.98 | 55.0 [42.5, 66.9] | 35.0 [24.2, 47.6] | 23.54 |
| 0 m | lawnmower | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 19.9 | 21.82 | 55.0 [42.5, 66.9] | 33.3 [22.7, 45.9] | 23.54 |
| 0 m | random_walk | 100.0 [94.0, 100.0] | 0.0 [0.0, 6.0] | 20.15 | 23.66 | 58.3 [45.7, 69.9] | 36.7 [25.6, 49.3] | 23.77 |
| 2 m | nominal_frontier | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 22.7 | 24.9 | 50.0 [37.7, 62.3] | 35.0 [24.2, 47.6] | 24.67 |
| 2 m | lawnmower | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 25.5 | 28.96 | 53.3 [40.9, 65.4] | 41.7 [30.1, 54.3] | 24.82 |
| 2 m | random_walk | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 25.2 | 27.98 | 55.0 [42.5, 66.9] | 35.0 [24.2, 47.6] | 23.25 |
| 5 m | nominal_frontier | 81.7 [70.1, 89.4] | 0.0 [0.0, 6.0] | 29.2 | 32.16 | 48.3 [36.2, 60.7] | 31.7 [21.3, 44.2] | 42.26 |
| 5 m | lawnmower | 86.7 [75.8, 93.1] | 0.0 [0.0, 6.0] | 55.25 | 58.41 | 38.3 [27.1, 51.0] | 50.0 [37.7, 62.3] | 34.44 |
| 5 m | random_walk | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 43.2 | 44.94 | 41.7 [30.1, 54.3] | 43.3 [31.6, 55.9] | 28.18 |
| unknown | frontier | 43.3 [31.6, 55.9] | 5.0 [1.7, 13.7] | 70.75 | 73.12 | 3.3 [0.9, 11.4] | 16.7 [9.3, 28.0] | 132.97 |
| unknown | lawnmower | 26.7 [17.1, 39.0] | 6.7 [2.6, 15.9] | 158.35 | 153.6 | 8.3 [3.6, 18.1] | 75.0 [62.8, 84.2] | 153.3 |
| unknown | random_walk | 13.3 [6.9, 24.2] | 1.7 [0.3, 8.9] | 66.0 | 69.46 | 5.0 [1.7, 13.7] | 56.7 [44.1, 68.4] | 160.86 |
