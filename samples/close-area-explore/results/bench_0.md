`python bench.py --layouts 20 --seed 0 --jobs 14` from samples/close-area-explore. Input: synthetic (simulated layouts, vehicle, range sensor; B detection by exact range + line of sight). Scored on truth. 1560 runs, wall 460.5 s on 14 processes.

Detection: within 2.0 m of B with a clear line of sight. Budget 180 s per run. Wilson 95 % intervals. Times are medians over runs that found / reached B, measured from take-off.

## Pooled over families

| preset | region | arm | n | found % [95 % CI] | reached % [95 % CI] | collision % [95 % CI] | stuck % | timeout % | median time to find s | median time to B s |
|---|---|---|---|---|---|---|---|---|---|---|
| ideal | B given | oracle | 60 | 100.0 [94.0, 100.0] | 98.3 [91.1, 99.7] | 0.0 [0.0, 6.0] | 0.0 | 1.7 | 0.0 | 22.8 |
| ideal | 0 m | frontier (region ignored) | 60 | 43.3 [31.6, 55.9] | 43.3 [31.6, 55.9] | 5.0 [1.7, 13.7] | 13.3 | 38.3 | 70.75 | 73.12 |
| ideal | 0 m | nominal_frontier | 60 | 95.0 [86.3, 98.3] | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 1.7 | 3.3 | 20.0 | 21.98 |
| ideal | 0 m | lawnmower | 60 | 91.7 [81.9, 96.4] | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 1.7 | 6.7 | 19.9 | 21.82 |
| ideal | 0 m | random_walk | 60 | 100.0 [94.0, 100.0] | 100.0 [94.0, 100.0] | 0.0 [0.0, 6.0] | 0.0 | 0.0 | 20.15 | 23.66 |
| ideal | 2 m | frontier (region ignored) | 60 | 43.3 [31.6, 55.9] | 43.3 [31.6, 55.9] | 5.0 [1.7, 13.7] | 13.3 | 38.3 | 70.75 | 73.12 |
| ideal | 2 m | nominal_frontier | 60 | 95.0 [86.3, 98.3] | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 0.0 | 5.0 | 22.7 | 24.9 |
| ideal | 2 m | lawnmower | 60 | 88.3 [77.8, 94.2] | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 0.0 | 11.7 | 25.5 | 28.96 |
| ideal | 2 m | random_walk | 60 | 95.0 [86.3, 98.3] | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 0.0 | 5.0 | 25.2 | 27.98 |
| ideal | 5 m | frontier (region ignored) | 60 | 43.3 [31.6, 55.9] | 43.3 [31.6, 55.9] | 5.0 [1.7, 13.7] | 13.3 | 38.3 | 70.75 | 73.12 |
| ideal | 5 m | nominal_frontier | 60 | 81.7 [70.1, 89.4] | 81.7 [70.1, 89.4] | 0.0 [0.0, 6.0] | 3.3 | 15.0 | 29.2 | 32.16 |
| ideal | 5 m | lawnmower | 60 | 86.7 [75.8, 93.1] | 86.7 [75.8, 93.1] | 0.0 [0.0, 6.0] | 0.0 | 13.3 | 55.25 | 58.41 |
| ideal | 5 m | random_walk | 60 | 91.7 [81.9, 96.4] | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 0.0 | 8.3 | 43.2 | 44.94 |
| ideal | unknown | frontier (region ignored) | 60 | 43.3 [31.6, 55.9] | 43.3 [31.6, 55.9] | 5.0 [1.7, 13.7] | 13.3 | 38.3 | 70.75 | 73.12 |
| ideal | unknown | nominal_frontier (= frontier) | 60 | 43.3 [31.6, 55.9] | 43.3 [31.6, 55.9] | 5.0 [1.7, 13.7] | 13.3 | 38.3 | 70.75 | 73.12 |
| ideal | unknown | lawnmower | 60 | 26.7 [17.1, 39.0] | 25.0 [15.8, 37.2] | 6.7 [2.6, 15.9] | 0.0 | 68.3 | 158.35 | 153.6 |
| ideal | unknown | random_walk | 60 | 13.3 [6.9, 24.2] | 13.3 [6.9, 24.2] | 1.7 [0.3, 8.9] | 0.0 | 85.0 | 66.0 | 69.46 |
| crazyflie | B given | oracle | 60 | 100.0 [94.0, 100.0] | 53.3 [40.9, 65.4] | 38.3 [27.1, 51.0] | 1.7 | 6.7 | 0.0 | 23.68 |
| crazyflie | 0 m | frontier (region ignored) | 60 | 3.3 [0.9, 11.4] | 3.3 [0.9, 11.4] | 16.7 [9.3, 28.0] | 15.0 | 65.0 | 131.05 | 132.97 |
| crazyflie | 0 m | nominal_frontier | 60 | 55.0 [42.5, 66.9] | 51.7 [39.3, 63.8] | 35.0 [24.2, 47.6] | 6.7 | 6.7 | 20.9 | 23.54 |
| crazyflie | 0 m | lawnmower | 60 | 55.0 [42.5, 66.9] | 51.7 [39.3, 63.8] | 33.3 [22.7, 45.9] | 6.7 | 8.3 | 20.9 | 23.54 |
| crazyflie | 0 m | random_walk | 60 | 58.3 [45.7, 69.9] | 56.7 [44.1, 68.4] | 36.7 [25.6, 49.3] | 5.0 | 1.7 | 21.2 | 23.77 |
| crazyflie | 2 m | frontier (region ignored) | 60 | 3.3 [0.9, 11.4] | 3.3 [0.9, 11.4] | 16.7 [9.3, 28.0] | 15.0 | 65.0 | 131.05 | 132.97 |
| crazyflie | 2 m | nominal_frontier | 60 | 50.0 [37.7, 62.3] | 50.0 [37.7, 62.3] | 35.0 [24.2, 47.6] | 1.7 | 13.3 | 22.95 | 24.67 |
| crazyflie | 2 m | lawnmower | 60 | 53.3 [40.9, 65.4] | 53.3 [40.9, 65.4] | 41.7 [30.1, 54.3] | 0.0 | 5.0 | 22.2 | 24.82 |
| crazyflie | 2 m | random_walk | 60 | 55.0 [42.5, 66.9] | 53.3 [40.9, 65.4] | 35.0 [24.2, 47.6] | 6.7 | 5.0 | 22.1 | 23.25 |
| crazyflie | 5 m | frontier (region ignored) | 60 | 3.3 [0.9, 11.4] | 3.3 [0.9, 11.4] | 16.7 [9.3, 28.0] | 15.0 | 65.0 | 131.05 | 132.97 |
| crazyflie | 5 m | nominal_frontier | 60 | 48.3 [36.2, 60.7] | 48.3 [36.2, 60.7] | 31.7 [21.3, 44.2] | 8.3 | 11.7 | 40.6 | 42.26 |
| crazyflie | 5 m | lawnmower | 60 | 38.3 [27.1, 51.0] | 38.3 [27.1, 51.0] | 50.0 [37.7, 62.3] | 1.7 | 10.0 | 32.8 | 34.44 |
| crazyflie | 5 m | random_walk | 60 | 41.7 [30.1, 54.3] | 40.0 [28.6, 52.6] | 43.3 [31.6, 55.9] | 6.7 | 10.0 | 26.0 | 28.18 |
| crazyflie | unknown | frontier (region ignored) | 60 | 3.3 [0.9, 11.4] | 3.3 [0.9, 11.4] | 16.7 [9.3, 28.0] | 15.0 | 65.0 | 131.05 | 132.97 |
| crazyflie | unknown | nominal_frontier (= frontier) | 60 | 3.3 [0.9, 11.4] | 3.3 [0.9, 11.4] | 16.7 [9.3, 28.0] | 15.0 | 65.0 | 131.05 | 132.97 |
| crazyflie | unknown | lawnmower | 60 | 8.3 [3.6, 18.1] | 8.3 [3.6, 18.1] | 75.0 [62.8, 84.2] | 1.7 | 15.0 | 151.7 | 153.3 |
| crazyflie | unknown | random_walk | 60 | 5.0 [1.7, 13.7] | 5.0 [1.7, 13.7] | 56.7 [44.1, 68.4] | 0.0 | 38.3 | 157.4 | 160.86 |

## Per family

| family / preset | region | arm | n | found % [95 % CI] | reached % [95 % CI] | collision % [95 % CI] | stuck % | timeout % | median time to find s | median time to B s |
|---|---|---|---|---|---|---|---|---|---|---|
| random / ideal | B given | oracle | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 0.0 | 19.01 |
| random / ideal | 0 m | frontier (region ignored) | 20 | 55.0 [34.2, 74.2] | 55.0 [34.2, 74.2] | 5.0 [0.9, 23.6] | 35.0 | 5.0 | 58.6 | 60.28 |
| random / ideal | 0 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.3 | 19.01 |
| random / ideal | 0 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.3 | 19.01 |
| random / ideal | 0 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.3 | 19.01 |
| random / ideal | 2 m | frontier (region ignored) | 20 | 55.0 [34.2, 74.2] | 55.0 [34.2, 74.2] | 5.0 [0.9, 23.6] | 35.0 | 5.0 | 58.6 | 60.28 |
| random / ideal | 2 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.2 | 18.92 |
| random / ideal | 2 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.7 | 19.37 |
| random / ideal | 2 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 17.5 | 19.24 |
| random / ideal | 5 m | frontier (region ignored) | 20 | 55.0 [34.2, 74.2] | 55.0 [34.2, 74.2] | 5.0 [0.9, 23.6] | 35.0 | 5.0 | 58.6 | 60.28 |
| random / ideal | 5 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 18.1 | 19.84 |
| random / ideal | 5 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 26.7 | 28.41 |
| random / ideal | 5 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 19.25 | 20.94 |
| random / ideal | unknown | frontier (region ignored) | 20 | 55.0 [34.2, 74.2] | 55.0 [34.2, 74.2] | 5.0 [0.9, 23.6] | 35.0 | 5.0 | 58.6 | 60.28 |
| random / ideal | unknown | nominal_frontier (= frontier) | 20 | 55.0 [34.2, 74.2] | 55.0 [34.2, 74.2] | 5.0 [0.9, 23.6] | 35.0 | 5.0 | 58.6 | 60.28 |
| random / ideal | unknown | lawnmower | 20 | 65.0 [43.3, 81.9] | 60.0 [38.7, 78.1] | 15.0 [5.2, 36.0] | 0.0 | 25.0 | 164.7 | 159.99 |
| random / ideal | unknown | random_walk | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 5.0 [0.9, 23.6] | 0.0 | 80.0 | 92.5 | 94.24 |
| random / crazyflie | B given | oracle | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 0.0 | 22.51 |
| random / crazyflie | 0 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 | 90.0 | 125.2 | 126.86 |
| random / crazyflie | 0 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.9 | 22.51 |
| random / crazyflie | 0 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.9 | 22.51 |
| random / crazyflie | 0 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 20.9 | 22.51 |
| random / crazyflie | 2 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 | 90.0 | 125.2 | 126.86 |
| random / crazyflie | 2 m | nominal_frontier | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 22.05 | 23.93 |
| random / crazyflie | 2 m | lawnmower | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 19.6 | 21.21 |
| random / crazyflie | 2 m | random_walk | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 5.0 [0.9, 23.6] | 0.0 | 0.0 | 20.2 | 22.5 |
| random / crazyflie | 5 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 | 90.0 | 125.2 | 126.86 |
| random / crazyflie | 5 m | nominal_frontier | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 10.0 [2.8, 30.1] | 0.0 | 0.0 | 27.05 | 29.4 |
| random / crazyflie | 5 m | lawnmower | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 5.0 [0.9, 23.6] | 0.0 | 0.0 | 27.5 | 31.7 |
| random / crazyflie | 5 m | random_walk | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 10.0 [2.8, 30.1] | 0.0 | 0.0 | 23.85 | 25.6 |
| random / crazyflie | unknown | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 | 90.0 | 125.2 | 126.86 |
| random / crazyflie | unknown | nominal_frontier (= frontier) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 0.0 | 90.0 | 125.2 | 126.86 |
| random / crazyflie | unknown | lawnmower | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 60.0 [38.7, 78.1] | 0.0 | 25.0 | 151.7 | 153.3 |
| random / crazyflie | unknown | random_walk | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 55.0 [34.2, 74.2] | 0.0 | 45.0 | - | - |
| office / ideal | B given | oracle | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 0.0 | 23.68 |
| office / ideal | 0 m | frontier (region ignored) | 20 | 65.0 [43.3, 81.9] | 65.0 [43.3, 81.9] | 5.0 [0.9, 23.6] | 5.0 | 25.0 | 76.3 | 79.5 |
| office / ideal | 0 m | nominal_frontier | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 0.0 [0.0, 16.1] | 5.0 | 5.0 | 19.8 | 22.39 |
| office / ideal | 0 m | lawnmower | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 0.0 [0.0, 16.1] | 5.0 | 5.0 | 19.8 | 22.39 |
| office / ideal | 0 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 19.95 | 23.66 |
| office / ideal | 2 m | frontier (region ignored) | 20 | 65.0 [43.3, 81.9] | 65.0 [43.3, 81.9] | 5.0 [0.9, 23.6] | 5.0 | 25.0 | 76.3 | 79.5 |
| office / ideal | 2 m | nominal_frontier | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 0.0 | 5.0 | 23.1 | 24.92 |
| office / ideal | 2 m | lawnmower | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 0.0 [0.0, 16.1] | 0.0 | 10.0 | 31.8 | 34.13 |
| office / ideal | 2 m | random_walk | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 0.0 | 5.0 | 25.6 | 28.66 |
| office / ideal | 5 m | frontier (region ignored) | 20 | 65.0 [43.3, 81.9] | 65.0 [43.3, 81.9] | 5.0 [0.9, 23.6] | 5.0 | 25.0 | 76.3 | 79.5 |
| office / ideal | 5 m | nominal_frontier | 20 | 70.0 [48.1, 85.5] | 70.0 [48.1, 85.5] | 0.0 [0.0, 16.1] | 10.0 | 20.0 | 45.0 | 47.18 |
| office / ideal | 5 m | lawnmower | 20 | 85.0 [64.0, 94.8] | 85.0 [64.0, 94.8] | 0.0 [0.0, 16.1] | 0.0 | 15.0 | 81.0 | 82.8 |
| office / ideal | 5 m | random_walk | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 0.0 | 5.0 | 63.5 | 67.34 |
| office / ideal | unknown | frontier (region ignored) | 20 | 65.0 [43.3, 81.9] | 65.0 [43.3, 81.9] | 5.0 [0.9, 23.6] | 5.0 | 25.0 | 76.3 | 79.5 |
| office / ideal | unknown | nominal_frontier (= frontier) | 20 | 65.0 [43.3, 81.9] | 65.0 [43.3, 81.9] | 5.0 [0.9, 23.6] | 5.0 | 25.0 | 76.3 | 79.5 |
| office / ideal | unknown | lawnmower | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 5.0 [0.9, 23.6] | 0.0 | 80.0 | 127.8 | 133.12 |
| office / ideal | unknown | random_walk | 20 | 25.0 [11.2, 46.9] | 25.0 [11.2, 46.9] | 0.0 [0.0, 16.1] | 0.0 | 75.0 | 58.4 | 61.06 |
| office / crazyflie | B given | oracle | 20 | 100.0 [83.9, 100.0] | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 0.0 | 0.0 | 0.0 | 25.3 |
| office / crazyflie | 0 m | frontier (region ignored) | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 10.0 [2.8, 30.1] | 30.0 | 60.0 | - | - |
| office / crazyflie | 0 m | nominal_frontier | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 40.0 [21.9, 61.3] | 5.0 | 5.0 | 20.65 | 25.59 |
| office / crazyflie | 0 m | lawnmower | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 35.0 [18.1, 56.7] | 5.0 | 10.0 | 20.65 | 25.59 |
| office / crazyflie | 0 m | random_walk | 20 | 55.0 [34.2, 74.2] | 55.0 [34.2, 74.2] | 45.0 [25.8, 65.8] | 0.0 | 0.0 | 20.8 | 25.82 |
| office / crazyflie | 2 m | frontier (region ignored) | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 10.0 [2.8, 30.1] | 30.0 | 60.0 | - | - |
| office / crazyflie | 2 m | nominal_frontier | 20 | 40.0 [21.9, 61.3] | 40.0 [21.9, 61.3] | 60.0 [38.7, 78.1] | 0.0 | 0.0 | 45.55 | 48.67 |
| office / crazyflie | 2 m | lawnmower | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 60.0 [38.7, 78.1] | 0.0 | 5.0 | 40.5 | 44.88 |
| office / crazyflie | 2 m | random_walk | 20 | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 50.0 [29.9, 70.1] | 0.0 | 0.0 | 26.45 | 29.97 |
| office / crazyflie | 5 m | frontier (region ignored) | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 10.0 [2.8, 30.1] | 30.0 | 60.0 | - | - |
| office / crazyflie | 5 m | nominal_frontier | 20 | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 35.0 [18.1, 56.7] | 25.0 | 5.0 | 107.6 | 112.24 |
| office / crazyflie | 5 m | lawnmower | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 70.0 [48.1, 85.5] | 5.0 | 10.0 | 38.2 | 42.66 |
| office / crazyflie | 5 m | random_walk | 20 | 20.0 [8.1, 41.6] | 15.0 [5.2, 36.0] | 70.0 [48.1, 85.5] | 5.0 | 10.0 | 55.35 | 97.98 |
| office / crazyflie | unknown | frontier (region ignored) | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 10.0 [2.8, 30.1] | 30.0 | 60.0 | - | - |
| office / crazyflie | unknown | nominal_frontier (= frontier) | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 10.0 [2.8, 30.1] | 30.0 | 60.0 | - | - |
| office / crazyflie | unknown | lawnmower | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 85.0 [64.0, 94.8] | 5.0 | 0.0 | 130.4 | 134.36 |
| office / crazyflie | unknown | random_walk | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 60.0 [38.7, 78.1] | 0.0 | 30.0 | 102.45 | 104.16 |
| warehouse / ideal | B given | oracle | 20 | 100.0 [83.9, 100.0] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 0.0 | 5.0 | 0.0 | 59.16 |
| warehouse / ideal | 0 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 5.0 [0.9, 23.6] | 0.0 | 85.0 | 86.55 | 90.35 |
| warehouse / ideal | 0 m | nominal_frontier | 20 | 95.0 [76.4, 99.1] | 95.0 [76.4, 99.1] | 0.0 [0.0, 16.1] | 0.0 | 5.0 | 56.6 | 59.08 |
| warehouse / ideal | 0 m | lawnmower | 20 | 85.0 [64.0, 94.8] | 85.0 [64.0, 94.8] | 0.0 [0.0, 16.1] | 0.0 | 15.0 | 52.8 | 55.16 |
| warehouse / ideal | 0 m | random_walk | 20 | 100.0 [83.9, 100.0] | 100.0 [83.9, 100.0] | 0.0 [0.0, 16.1] | 0.0 | 0.0 | 59.6 | 62.06 |
| warehouse / ideal | 2 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 5.0 [0.9, 23.6] | 0.0 | 85.0 | 86.55 | 90.35 |
| warehouse / ideal | 2 m | nominal_frontier | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 0.0 [0.0, 16.1] | 0.0 | 10.0 | 53.8 | 56.22 |
| warehouse / ideal | 2 m | lawnmower | 20 | 75.0 [53.1, 88.8] | 75.0 [53.1, 88.8] | 0.0 [0.0, 16.1] | 0.0 | 25.0 | 49.0 | 53.32 |
| warehouse / ideal | 2 m | random_walk | 20 | 90.0 [69.9, 97.2] | 90.0 [69.9, 97.2] | 0.0 [0.0, 16.1] | 0.0 | 10.0 | 49.65 | 52.38 |
| warehouse / ideal | 5 m | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 5.0 [0.9, 23.6] | 0.0 | 85.0 | 86.55 | 90.35 |
| warehouse / ideal | 5 m | nominal_frontier | 20 | 75.0 [53.1, 88.8] | 75.0 [53.1, 88.8] | 0.0 [0.0, 16.1] | 0.0 | 25.0 | 61.0 | 63.48 |
| warehouse / ideal | 5 m | lawnmower | 20 | 75.0 [53.1, 88.8] | 75.0 [53.1, 88.8] | 0.0 [0.0, 16.1] | 0.0 | 25.0 | 123.4 | 125.14 |
| warehouse / ideal | 5 m | random_walk | 20 | 80.0 [58.4, 91.9] | 80.0 [58.4, 91.9] | 0.0 [0.0, 16.1] | 0.0 | 20.0 | 57.85 | 59.94 |
| warehouse / ideal | unknown | frontier (region ignored) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 5.0 [0.9, 23.6] | 0.0 | 85.0 | 86.55 | 90.35 |
| warehouse / ideal | unknown | nominal_frontier (= frontier) | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 5.0 [0.9, 23.6] | 0.0 | 85.0 | 86.55 | 90.35 |
| warehouse / ideal | unknown | lawnmower | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 0.0 | 100.0 | - | - |
| warehouse / ideal | unknown | random_walk | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 0.0 | 100.0 | - | - |
| warehouse / crazyflie | B given | oracle | 20 | 100.0 [83.9, 100.0] | 10.0 [2.8, 30.1] | 65.0 [43.3, 81.9] | 5.0 | 20.0 | 0.0 | 108.63 |
| warehouse / crazyflie | 0 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 35.0 [18.1, 56.7] | 15.0 | 45.0 | 136.9 | 139.08 |
| warehouse / crazyflie | 0 m | nominal_frontier | 20 | 15.0 [5.2, 36.0] | 5.0 [0.9, 23.6] | 65.0 [43.3, 81.9] | 15.0 | 15.0 | 101.9 | 105.38 |
| warehouse / crazyflie | 0 m | lawnmower | 20 | 15.0 [5.2, 36.0] | 5.0 [0.9, 23.6] | 65.0 [43.3, 81.9] | 15.0 | 15.0 | 106.5 | 108.24 |
| warehouse / crazyflie | 0 m | random_walk | 20 | 20.0 [8.1, 41.6] | 15.0 [5.2, 36.0] | 65.0 [43.3, 81.9] | 15.0 | 5.0 | 104.3 | 110.74 |
| warehouse / crazyflie | 2 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 35.0 [18.1, 56.7] | 15.0 | 45.0 | 136.9 | 139.08 |
| warehouse / crazyflie | 2 m | nominal_frontier | 20 | 10.0 [2.8, 30.1] | 10.0 [2.8, 30.1] | 45.0 [25.8, 65.8] | 5.0 | 40.0 | 110.25 | 114.03 |
| warehouse / crazyflie | 2 m | lawnmower | 20 | 25.0 [11.2, 46.9] | 25.0 [11.2, 46.9] | 65.0 [43.3, 81.9] | 0.0 | 10.0 | 94.7 | 98.86 |
| warehouse / crazyflie | 2 m | random_walk | 20 | 20.0 [8.1, 41.6] | 15.0 [5.2, 36.0] | 50.0 [29.9, 70.1] | 20.0 | 15.0 | 106.35 | 116.08 |
| warehouse / crazyflie | 5 m | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 35.0 [18.1, 56.7] | 15.0 | 45.0 | 136.9 | 139.08 |
| warehouse / crazyflie | 5 m | nominal_frontier | 20 | 20.0 [8.1, 41.6] | 20.0 [8.1, 41.6] | 50.0 [29.9, 70.1] | 0.0 | 30.0 | 97.2 | 101.23 |
| warehouse / crazyflie | 5 m | lawnmower | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 75.0 [53.1, 88.8] | 0.0 | 20.0 | 151.1 | 153.02 |
| warehouse / crazyflie | 5 m | random_walk | 20 | 15.0 [5.2, 36.0] | 15.0 [5.2, 36.0] | 50.0 [29.9, 70.1] | 15.0 | 20.0 | 94.1 | 99.92 |
| warehouse / crazyflie | unknown | frontier (region ignored) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 35.0 [18.1, 56.7] | 15.0 | 45.0 | 136.9 | 139.08 |
| warehouse / crazyflie | unknown | nominal_frontier (= frontier) | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 35.0 [18.1, 56.7] | 15.0 | 45.0 | 136.9 | 139.08 |
| warehouse / crazyflie | unknown | lawnmower | 20 | 0.0 [0.0, 16.1] | 0.0 [0.0, 16.1] | 80.0 [58.4, 91.9] | 0.0 | 20.0 | - | - |
| warehouse / crazyflie | unknown | random_walk | 20 | 5.0 [0.9, 23.6] | 5.0 [0.9, 23.6] | 55.0 [34.2, 74.2] | 0.0 | 40.0 | 157.4 | 160.86 |

## Collisions (325 runs)

- random ideal layout 3 lawnmower region unknown: t 114.4 s, found False, min clearance 0.1489 m
- random ideal layout 6 lawnmower region unknown: t 127.26 s, found False, min clearance 0.1466 m
- random ideal layout 6 random_walk region unknown: t 178.74 s, found False, min clearance 0.149 m
- random ideal layout 7 lawnmower region unknown: t 16.88 s, found False, min clearance 0.1494 m
- random ideal layout 16 frontier region unknown: t 41.04 s, found False, min clearance 0.1498 m
- random crazyflie layout 0 nominal_frontier region 5 m: t 16.68 s, found False, min clearance 0.1474 m
- random crazyflie layout 0 random_walk region unknown: t 149.22 s, found False, min clearance 0.1461 m
- random crazyflie layout 1 lawnmower region 5 m: t 23.32 s, found False, min clearance 0.1474 m
- random crazyflie layout 1 random_walk region 5 m: t 36.26 s, found False, min clearance 0.1494 m
- random crazyflie layout 1 lawnmower region unknown: t 51.4 s, found False, min clearance 0.1497 m
- random crazyflie layout 2 lawnmower region unknown: t 11.0 s, found False, min clearance 0.1476 m
- random crazyflie layout 3 lawnmower region unknown: t 127.5 s, found False, min clearance 0.1458 m
- random crazyflie layout 4 lawnmower region unknown: t 66.74 s, found False, min clearance 0.1485 m
- random crazyflie layout 6 random_walk region unknown: t 59.5 s, found False, min clearance 0.1494 m
- random crazyflie layout 7 random_walk region 5 m: t 23.66 s, found False, min clearance 0.1471 m
- random crazyflie layout 7 lawnmower region unknown: t 13.26 s, found False, min clearance 0.1491 m
- random crazyflie layout 7 random_walk region unknown: t 60.48 s, found False, min clearance 0.1498 m
- random crazyflie layout 8 random_walk region 2 m: t 8.9 s, found False, min clearance 0.1474 m
- random crazyflie layout 8 lawnmower region unknown: t 113.8 s, found False, min clearance 0.1478 m
- random crazyflie layout 8 random_walk region unknown: t 149.84 s, found False, min clearance 0.1498 m
- random crazyflie layout 9 lawnmower region unknown: t 122.92 s, found False, min clearance 0.1495 m
- random crazyflie layout 9 random_walk region unknown: t 57.66 s, found False, min clearance 0.1495 m
- random crazyflie layout 10 lawnmower region unknown: t 29.38 s, found False, min clearance 0.1487 m
- random crazyflie layout 10 random_walk region unknown: t 25.7 s, found False, min clearance 0.1487 m
- random crazyflie layout 11 nominal_frontier region 5 m: t 20.46 s, found False, min clearance 0.149 m
- random crazyflie layout 11 lawnmower region unknown: t 60.46 s, found False, min clearance 0.1476 m
- random crazyflie layout 14 random_walk region unknown: t 52.7 s, found False, min clearance 0.1493 m
- random crazyflie layout 15 random_walk region unknown: t 11.36 s, found False, min clearance 0.1489 m
- random crazyflie layout 16 lawnmower region unknown: t 105.86 s, found False, min clearance 0.1495 m
- random crazyflie layout 16 random_walk region unknown: t 69.32 s, found False, min clearance 0.1497 m
- random crazyflie layout 17 random_walk region unknown: t 7.3 s, found False, min clearance 0.1487 m
- random crazyflie layout 18 lawnmower region unknown: t 17.7 s, found False, min clearance 0.1492 m
- random crazyflie layout 19 frontier region unknown: t 176.0 s, found False, min clearance 0.146 m
- random crazyflie layout 19 lawnmower region unknown: t 9.88 s, found False, min clearance 0.1492 m
- random crazyflie layout 19 random_walk region unknown: t 57.14 s, found False, min clearance 0.1476 m
- office ideal layout 2 lawnmower region unknown: t 143.6 s, found False, min clearance 0.1481 m
- office ideal layout 16 frontier region unknown: t 25.5 s, found False, min clearance 0.1493 m
- office crazyflie layout 0 nominal_frontier region 0 m: t 58.52 s, found False, min clearance 0.1488 m
- office crazyflie layout 0 lawnmower region 2 m: t 38.68 s, found False, min clearance 0.1487 m
- office crazyflie layout 0 lawnmower region 5 m: t 19.18 s, found False, min clearance 0.1471 m
- office crazyflie layout 0 lawnmower region unknown: t 7.12 s, found False, min clearance 0.1471 m
- office crazyflie layout 0 random_walk region unknown: t 30.2 s, found False, min clearance 0.1495 m
- office crazyflie layout 1 lawnmower region 2 m: t 49.8 s, found False, min clearance 0.1493 m
- office crazyflie layout 1 random_walk region 5 m: t 12.96 s, found False, min clearance 0.1491 m
- office crazyflie layout 1 lawnmower region unknown: t 12.8 s, found False, min clearance 0.1468 m
- office crazyflie layout 2 lawnmower region 5 m: t 18.14 s, found False, min clearance 0.1468 m
- office crazyflie layout 2 random_walk region 5 m: t 15.18 s, found True, min clearance 0.1479 m
- office crazyflie layout 2 lawnmower region unknown: t 18.22 s, found False, min clearance 0.1477 m
- office crazyflie layout 3 oracle region unknown: t 19.04 s, found True, min clearance 0.1489 m
- office crazyflie layout 3 nominal_frontier region 0 m: t 24.86 s, found False, min clearance 0.15 m
- office crazyflie layout 3 lawnmower region 0 m: t 24.94 s, found False, min clearance 0.148 m
- office crazyflie layout 3 random_walk region 0 m: t 19.04 s, found False, min clearance 0.1483 m
- office crazyflie layout 3 nominal_frontier region 2 m: t 5.78 s, found False, min clearance 0.1451 m
- office crazyflie layout 3 lawnmower region 2 m: t 104.88 s, found False, min clearance 0.1499 m
- office crazyflie layout 3 random_walk region 2 m: t 11.5 s, found False, min clearance 0.1479 m
- office crazyflie layout 3 lawnmower region 5 m: t 25.22 s, found False, min clearance 0.1458 m
- office crazyflie layout 3 random_walk region 5 m: t 117.3 s, found False, min clearance 0.1481 m
- office crazyflie layout 3 lawnmower region unknown: t 12.58 s, found False, min clearance 0.1478 m
- office crazyflie layout 3 random_walk region unknown: t 176.72 s, found False, min clearance 0.1498 m
- office crazyflie layout 4 oracle region unknown: t 6.94 s, found True, min clearance 0.1472 m
- office crazyflie layout 4 nominal_frontier region 0 m: t 6.94 s, found False, min clearance 0.1468 m
- office crazyflie layout 4 lawnmower region 0 m: t 6.94 s, found False, min clearance 0.1468 m
- office crazyflie layout 4 random_walk region 0 m: t 6.94 s, found False, min clearance 0.1468 m
- office crazyflie layout 4 nominal_frontier region 2 m: t 6.88 s, found False, min clearance 0.1481 m
- office crazyflie layout 4 lawnmower region 2 m: t 6.88 s, found False, min clearance 0.1466 m
- office crazyflie layout 4 random_walk region 2 m: t 6.9 s, found False, min clearance 0.1469 m
- office crazyflie layout 4 nominal_frontier region 5 m: t 6.82 s, found False, min clearance 0.1492 m
- office crazyflie layout 4 lawnmower region 5 m: t 14.14 s, found False, min clearance 0.1487 m
- office crazyflie layout 4 random_walk region 5 m: t 19.92 s, found False, min clearance 0.1481 m
- office crazyflie layout 4 lawnmower region unknown: t 85.42 s, found False, min clearance 0.1459 m
- office crazyflie layout 4 random_walk region unknown: t 13.76 s, found False, min clearance 0.1483 m
- office crazyflie layout 5 oracle region unknown: t 10.44 s, found True, min clearance 0.1473 m
- office crazyflie layout 5 nominal_frontier region 0 m: t 10.44 s, found False, min clearance 0.1473 m
- office crazyflie layout 5 lawnmower region 0 m: t 10.44 s, found False, min clearance 0.1473 m
- office crazyflie layout 5 random_walk region 0 m: t 10.44 s, found False, min clearance 0.1473 m
- office crazyflie layout 5 nominal_frontier region 2 m: t 9.7 s, found False, min clearance 0.1469 m
- office crazyflie layout 5 lawnmower region 2 m: t 7.58 s, found False, min clearance 0.1443 m
- office crazyflie layout 5 random_walk region 2 m: t 10.98 s, found False, min clearance 0.1485 m
- office crazyflie layout 5 lawnmower region 5 m: t 9.06 s, found False, min clearance 0.1455 m
- office crazyflie layout 5 random_walk region 5 m: t 13.58 s, found False, min clearance 0.1462 m
- office crazyflie layout 5 lawnmower region unknown: t 15.94 s, found False, min clearance 0.1477 m
- office crazyflie layout 5 random_walk region unknown: t 95.22 s, found False, min clearance 0.1498 m
- office crazyflie layout 6 oracle region unknown: t 48.58 s, found True, min clearance 0.1467 m
- office crazyflie layout 6 random_walk region 0 m: t 55.46 s, found False, min clearance 0.1479 m
- office crazyflie layout 6 nominal_frontier region 2 m: t 17.2 s, found False, min clearance 0.146 m
- office crazyflie layout 6 lawnmower region 2 m: t 13.16 s, found False, min clearance 0.1479 m
- office crazyflie layout 6 lawnmower region 5 m: t 61.94 s, found False, min clearance 0.1471 m
- office crazyflie layout 6 random_walk region 5 m: t 19.6 s, found False, min clearance 0.1477 m
- office crazyflie layout 7 oracle region unknown: t 25.82 s, found True, min clearance 0.1467 m
- office crazyflie layout 7 nominal_frontier region 0 m: t 25.82 s, found False, min clearance 0.1467 m
- office crazyflie layout 7 lawnmower region 0 m: t 25.82 s, found False, min clearance 0.1467 m
- office crazyflie layout 7 random_walk region 0 m: t 25.82 s, found False, min clearance 0.1467 m
- office crazyflie layout 7 nominal_frontier region 2 m: t 23.44 s, found False, min clearance 0.1449 m
- office crazyflie layout 7 lawnmower region 2 m: t 11.62 s, found False, min clearance 0.1472 m
- office crazyflie layout 7 random_walk region 2 m: t 2.0 s, found False, min clearance 0.1447 m
- office crazyflie layout 7 nominal_frontier region 5 m: t 106.0 s, found False, min clearance 0.1495 m
- office crazyflie layout 7 lawnmower region 5 m: t 58.66 s, found False, min clearance 0.1456 m
- office crazyflie layout 7 random_walk region 5 m: t 10.5 s, found False, min clearance 0.1476 m
- office crazyflie layout 7 lawnmower region unknown: t 6.2 s, found False, min clearance 0.1475 m
- office crazyflie layout 7 random_walk region unknown: t 7.04 s, found False, min clearance 0.1464 m
- office crazyflie layout 8 oracle region unknown: t 87.12 s, found True, min clearance 0.146 m
- office crazyflie layout 8 nominal_frontier region 2 m: t 18.86 s, found False, min clearance 0.1477 m
- office crazyflie layout 8 lawnmower region 2 m: t 2.52 s, found False, min clearance 0.1485 m
- office crazyflie layout 8 random_walk region 2 m: t 18.86 s, found False, min clearance 0.1477 m
- office crazyflie layout 8 nominal_frontier region 5 m: t 31.4 s, found False, min clearance 0.1477 m
- office crazyflie layout 8 random_walk region 5 m: t 13.38 s, found False, min clearance 0.1478 m
- office crazyflie layout 8 lawnmower region unknown: t 19.48 s, found False, min clearance 0.1476 m
- office crazyflie layout 9 nominal_frontier region 2 m: t 104.8 s, found False, min clearance 0.1473 m
- office crazyflie layout 9 lawnmower region 2 m: t 24.58 s, found False, min clearance 0.1466 m
- office crazyflie layout 9 lawnmower region 5 m: t 12.04 s, found False, min clearance 0.1476 m
- office crazyflie layout 9 lawnmower region unknown: t 8.28 s, found False, min clearance 0.1471 m
- office crazyflie layout 9 random_walk region unknown: t 14.34 s, found False, min clearance 0.1473 m
- office crazyflie layout 10 oracle region unknown: t 9.3 s, found True, min clearance 0.147 m
- office crazyflie layout 10 frontier region unknown: t 114.4 s, found False, min clearance 0.1498 m
- office crazyflie layout 10 nominal_frontier region 0 m: t 9.3 s, found False, min clearance 0.147 m
- office crazyflie layout 10 lawnmower region 0 m: t 9.3 s, found False, min clearance 0.147 m
- office crazyflie layout 10 random_walk region 0 m: t 9.3 s, found False, min clearance 0.147 m
- office crazyflie layout 10 random_walk region 2 m: t 39.2 s, found False, min clearance 0.1485 m
- office crazyflie layout 10 nominal_frontier region 5 m: t 26.6 s, found False, min clearance 0.1497 m
- office crazyflie layout 10 lawnmower region 5 m: t 40.8 s, found False, min clearance 0.147 m
- office crazyflie layout 10 random_walk region 5 m: t 52.64 s, found False, min clearance 0.1498 m
- office crazyflie layout 10 lawnmower region unknown: t 10.86 s, found False, min clearance 0.1499 m
- office crazyflie layout 10 random_walk region unknown: t 15.08 s, found False, min clearance 0.1498 m
- office crazyflie layout 11 oracle region unknown: t 15.82 s, found True, min clearance 0.1454 m
- office crazyflie layout 11 nominal_frontier region 0 m: t 15.82 s, found False, min clearance 0.1454 m
- office crazyflie layout 11 lawnmower region 0 m: t 15.82 s, found False, min clearance 0.1454 m
- office crazyflie layout 11 random_walk region 0 m: t 15.82 s, found False, min clearance 0.1454 m
- office crazyflie layout 11 nominal_frontier region 2 m: t 17.8 s, found False, min clearance 0.1495 m
- office crazyflie layout 11 random_walk region 2 m: t 18.8 s, found False, min clearance 0.1477 m
- office crazyflie layout 11 nominal_frontier region 5 m: t 22.26 s, found False, min clearance 0.1491 m
- office crazyflie layout 11 random_walk region unknown: t 8.14 s, found False, min clearance 0.1498 m
- office crazyflie layout 12 lawnmower region 5 m: t 5.28 s, found False, min clearance 0.1497 m
- office crazyflie layout 12 random_walk region 5 m: t 25.72 s, found False, min clearance 0.1492 m
- office crazyflie layout 12 lawnmower region unknown: t 6.58 s, found False, min clearance 0.149 m
- office crazyflie layout 12 random_walk region unknown: t 23.32 s, found False, min clearance 0.1493 m
- office crazyflie layout 13 nominal_frontier region 2 m: t 16.22 s, found False, min clearance 0.1494 m
- office crazyflie layout 13 lawnmower region 2 m: t 18.7 s, found False, min clearance 0.1447 m
- office crazyflie layout 13 lawnmower region 5 m: t 13.48 s, found False, min clearance 0.1483 m
- office crazyflie layout 13 lawnmower region unknown: t 38.02 s, found False, min clearance 0.1484 m
- office crazyflie layout 14 frontier region unknown: t 165.06 s, found False, min clearance 0.1469 m
- office crazyflie layout 14 random_walk region 5 m: t 132.28 s, found False, min clearance 0.1484 m
- office crazyflie layout 14 lawnmower region unknown: t 37.0 s, found False, min clearance 0.1499 m
- office crazyflie layout 15 lawnmower region 5 m: t 8.7 s, found False, min clearance 0.1473 m
- office crazyflie layout 15 random_walk region 5 m: t 30.34 s, found False, min clearance 0.1489 m
- office crazyflie layout 15 lawnmower region unknown: t 8.08 s, found False, min clearance 0.1472 m
- office crazyflie layout 15 random_walk region unknown: t 7.34 s, found False, min clearance 0.1472 m
- office crazyflie layout 16 oracle region unknown: t 38.68 s, found True, min clearance 0.1494 m
- office crazyflie layout 16 random_walk region 0 m: t 38.34 s, found False, min clearance 0.1484 m
- office crazyflie layout 16 nominal_frontier region 2 m: t 28.32 s, found False, min clearance 0.1487 m
- office crazyflie layout 16 lawnmower region 2 m: t 65.84 s, found False, min clearance 0.1468 m
- office crazyflie layout 16 random_walk region 2 m: t 51.98 s, found False, min clearance 0.1461 m
- office crazyflie layout 16 nominal_frontier region 5 m: t 60.94 s, found False, min clearance 0.1485 m
- office crazyflie layout 16 random_walk region 5 m: t 27.2 s, found False, min clearance 0.1469 m
- office crazyflie layout 16 lawnmower region unknown: t 11.52 s, found False, min clearance 0.1481 m
- office crazyflie layout 17 lawnmower region 5 m: t 19.56 s, found False, min clearance 0.1487 m
- office crazyflie layout 17 lawnmower region unknown: t 169.08 s, found False, min clearance 0.1491 m
- office crazyflie layout 17 random_walk region unknown: t 80.02 s, found False, min clearance 0.1472 m
- office crazyflie layout 18 oracle region unknown: t 7.68 s, found True, min clearance 0.1488 m
- office crazyflie layout 18 nominal_frontier region 0 m: t 7.68 s, found False, min clearance 0.149 m
- office crazyflie layout 18 lawnmower region 0 m: t 7.68 s, found False, min clearance 0.149 m
- office crazyflie layout 18 random_walk region 0 m: t 7.68 s, found False, min clearance 0.149 m
- office crazyflie layout 18 nominal_frontier region 2 m: t 8.44 s, found False, min clearance 0.1485 m
- office crazyflie layout 18 lawnmower region 2 m: t 7.58 s, found False, min clearance 0.1497 m
- office crazyflie layout 18 random_walk region 2 m: t 41.1 s, found False, min clearance 0.1492 m
- office crazyflie layout 18 nominal_frontier region 5 m: t 7.76 s, found False, min clearance 0.1473 m
- office crazyflie layout 18 lawnmower region 5 m: t 7.72 s, found False, min clearance 0.1487 m
- office crazyflie layout 18 random_walk region 5 m: t 7.52 s, found False, min clearance 0.1463 m
- office crazyflie layout 18 lawnmower region unknown: t 45.0 s, found False, min clearance 0.1493 m
- office crazyflie layout 18 random_walk region unknown: t 13.74 s, found False, min clearance 0.1498 m
- office crazyflie layout 19 nominal_frontier region 2 m: t 121.7 s, found False, min clearance 0.1497 m
- office crazyflie layout 19 random_walk region 2 m: t 60.36 s, found False, min clearance 0.1494 m
- warehouse ideal layout 16 frontier region unknown: t 83.74 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 0 nominal_frontier region 0 m: t 114.42 s, found True, min clearance 0.1477 m
- warehouse crazyflie layout 0 lawnmower region 0 m: t 146.64 s, found True, min clearance 0.1488 m
- warehouse crazyflie layout 0 random_walk region 2 m: t 18.64 s, found False, min clearance 0.1469 m
- warehouse crazyflie layout 0 lawnmower region 5 m: t 28.92 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 0 random_walk region 5 m: t 96.18 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 1 oracle region unknown: t 139.46 s, found True, min clearance 0.1486 m
- warehouse crazyflie layout 1 nominal_frontier region 0 m: t 76.98 s, found False, min clearance 0.1472 m
- warehouse crazyflie layout 1 lawnmower region 0 m: t 76.98 s, found False, min clearance 0.1472 m
- warehouse crazyflie layout 1 random_walk region 0 m: t 76.98 s, found False, min clearance 0.1472 m
- warehouse crazyflie layout 1 nominal_frontier region 2 m: t 65.22 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 1 lawnmower region 2 m: t 117.36 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 1 nominal_frontier region 5 m: t 16.7 s, found False, min clearance 0.1487 m
- warehouse crazyflie layout 1 lawnmower region 5 m: t 97.22 s, found False, min clearance 0.145 m
- warehouse crazyflie layout 1 random_walk region 5 m: t 120.24 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 1 lawnmower region unknown: t 68.48 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 2 oracle region unknown: t 35.76 s, found True, min clearance 0.1468 m
- warehouse crazyflie layout 2 nominal_frontier region 0 m: t 35.76 s, found False, min clearance 0.1467 m
- warehouse crazyflie layout 2 lawnmower region 0 m: t 35.76 s, found False, min clearance 0.1467 m
- warehouse crazyflie layout 2 random_walk region 0 m: t 35.76 s, found False, min clearance 0.1467 m
- warehouse crazyflie layout 2 lawnmower region 2 m: t 77.86 s, found False, min clearance 0.1459 m
- warehouse crazyflie layout 2 lawnmower region unknown: t 151.82 s, found False, min clearance 0.1499 m
- warehouse crazyflie layout 3 oracle region unknown: t 112.4 s, found True, min clearance 0.145 m
- warehouse crazyflie layout 3 frontier region unknown: t 87.58 s, found False, min clearance 0.1493 m
- warehouse crazyflie layout 3 nominal_frontier region 0 m: t 30.38 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 3 lawnmower region 0 m: t 30.38 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 3 random_walk region 0 m: t 30.38 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 3 nominal_frontier region 2 m: t 41.14 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 3 lawnmower region 2 m: t 22.66 s, found False, min clearance 0.1494 m
- warehouse crazyflie layout 3 nominal_frontier region 5 m: t 44.48 s, found False, min clearance 0.1485 m
- warehouse crazyflie layout 3 lawnmower region 5 m: t 140.62 s, found False, min clearance 0.1466 m
- warehouse crazyflie layout 3 random_walk region unknown: t 114.64 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 4 oracle region unknown: t 85.46 s, found True, min clearance 0.1493 m
- warehouse crazyflie layout 4 frontier region unknown: t 50.94 s, found False, min clearance 0.1461 m
- warehouse crazyflie layout 4 nominal_frontier region 2 m: t 55.64 s, found False, min clearance 0.1494 m
- warehouse crazyflie layout 4 random_walk region 2 m: t 49.16 s, found False, min clearance 0.1473 m
- warehouse crazyflie layout 4 nominal_frontier region 5 m: t 27.62 s, found False, min clearance 0.1498 m
- warehouse crazyflie layout 4 lawnmower region 5 m: t 44.32 s, found False, min clearance 0.1499 m
- warehouse crazyflie layout 4 random_walk region 5 m: t 46.68 s, found False, min clearance 0.1487 m
- warehouse crazyflie layout 4 lawnmower region unknown: t 115.68 s, found False, min clearance 0.148 m
- warehouse crazyflie layout 4 random_walk region unknown: t 15.72 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 5 oracle region unknown: t 132.06 s, found True, min clearance 0.1474 m
- warehouse crazyflie layout 5 frontier region unknown: t 72.72 s, found False, min clearance 0.1499 m
- warehouse crazyflie layout 5 nominal_frontier region 0 m: t 79.02 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 5 lawnmower region 0 m: t 79.02 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 5 random_walk region 0 m: t 79.02 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 5 nominal_frontier region 5 m: t 37.58 s, found False, min clearance 0.1494 m
- warehouse crazyflie layout 5 lawnmower region 5 m: t 73.66 s, found False, min clearance 0.1389 m
- warehouse crazyflie layout 5 lawnmower region unknown: t 55.76 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 5 random_walk region unknown: t 37.6 s, found False, min clearance 0.1487 m
- warehouse crazyflie layout 6 oracle region unknown: t 26.12 s, found True, min clearance 0.1496 m
- warehouse crazyflie layout 6 nominal_frontier region 0 m: t 21.1 s, found False, min clearance 0.148 m
- warehouse crazyflie layout 6 lawnmower region 0 m: t 21.1 s, found False, min clearance 0.148 m
- warehouse crazyflie layout 6 random_walk region 0 m: t 21.1 s, found False, min clearance 0.148 m
- warehouse crazyflie layout 6 nominal_frontier region 2 m: t 26.58 s, found False, min clearance 0.1482 m
- warehouse crazyflie layout 6 lawnmower region 5 m: t 44.04 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 6 random_walk region 5 m: t 43.1 s, found False, min clearance 0.1483 m
- warehouse crazyflie layout 6 lawnmower region unknown: t 106.94 s, found False, min clearance 0.1492 m
- warehouse crazyflie layout 7 nominal_frontier region 2 m: t 56.32 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 7 nominal_frontier region 5 m: t 60.54 s, found False, min clearance 0.1485 m
- warehouse crazyflie layout 7 lawnmower region unknown: t 34.12 s, found False, min clearance 0.1467 m
- warehouse crazyflie layout 7 random_walk region unknown: t 123.72 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 8 oracle region unknown: t 142.0 s, found True, min clearance 0.1496 m
- warehouse crazyflie layout 8 nominal_frontier region 2 m: t 24.9 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 8 random_walk region 2 m: t 33.76 s, found False, min clearance 0.1473 m
- warehouse crazyflie layout 8 lawnmower region 5 m: t 39.06 s, found False, min clearance 0.1455 m
- warehouse crazyflie layout 8 random_walk region 5 m: t 148.88 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 8 lawnmower region unknown: t 84.08 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 8 random_walk region unknown: t 13.76 s, found False, min clearance 0.1465 m
- warehouse crazyflie layout 9 oracle region unknown: t 65.4 s, found True, min clearance 0.1483 m
- warehouse crazyflie layout 9 nominal_frontier region 0 m: t 65.36 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 9 lawnmower region 0 m: t 65.36 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 9 random_walk region 0 m: t 65.36 s, found False, min clearance 0.1478 m
- warehouse crazyflie layout 9 lawnmower region 2 m: t 21.5 s, found False, min clearance 0.1499 m
- warehouse crazyflie layout 9 random_walk region 2 m: t 156.34 s, found False, min clearance 0.1476 m
- warehouse crazyflie layout 9 nominal_frontier region 5 m: t 58.8 s, found False, min clearance 0.146 m
- warehouse crazyflie layout 9 lawnmower region 5 m: t 56.0 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 9 random_walk region 5 m: t 23.12 s, found False, min clearance 0.1494 m
- warehouse crazyflie layout 9 lawnmower region unknown: t 35.94 s, found False, min clearance 0.1467 m
- warehouse crazyflie layout 9 random_walk region unknown: t 24.36 s, found False, min clearance 0.1479 m
- warehouse crazyflie layout 10 oracle region unknown: t 66.42 s, found True, min clearance 0.1498 m
- warehouse crazyflie layout 10 frontier region unknown: t 45.28 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 10 nominal_frontier region 0 m: t 66.8 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 10 lawnmower region 0 m: t 66.8 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 10 random_walk region 0 m: t 66.8 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 10 lawnmower region 2 m: t 47.56 s, found False, min clearance 0.1473 m
- warehouse crazyflie layout 10 random_walk region 2 m: t 80.08 s, found False, min clearance 0.1471 m
- warehouse crazyflie layout 10 nominal_frontier region 5 m: t 49.1 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 10 lawnmower region 5 m: t 100.62 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 10 random_walk region 5 m: t 10.18 s, found False, min clearance 0.1446 m
- warehouse crazyflie layout 10 lawnmower region unknown: t 133.64 s, found False, min clearance 0.1467 m
- warehouse crazyflie layout 10 random_walk region unknown: t 74.52 s, found False, min clearance 0.1482 m
- warehouse crazyflie layout 11 lawnmower region 2 m: t 120.88 s, found False, min clearance 0.1468 m
- warehouse crazyflie layout 11 random_walk region 2 m: t 34.06 s, found False, min clearance 0.1473 m
- warehouse crazyflie layout 11 lawnmower region unknown: t 22.42 s, found False, min clearance 0.148 m
- warehouse crazyflie layout 12 frontier region unknown: t 113.48 s, found False, min clearance 0.1469 m
- warehouse crazyflie layout 12 lawnmower region 2 m: t 31.98 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 12 random_walk region 2 m: t 30.64 s, found False, min clearance 0.1475 m
- warehouse crazyflie layout 12 nominal_frontier region 5 m: t 84.18 s, found False, min clearance 0.1467 m
- warehouse crazyflie layout 12 lawnmower region 5 m: t 30.66 s, found False, min clearance 0.1486 m
- warehouse crazyflie layout 12 random_walk region 5 m: t 105.94 s, found False, min clearance 0.1452 m
- warehouse crazyflie layout 12 lawnmower region unknown: t 34.32 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 13 oracle region unknown: t 48.32 s, found True, min clearance 0.1468 m
- warehouse crazyflie layout 13 frontier region unknown: t 49.74 s, found False, min clearance 0.149 m
- warehouse crazyflie layout 13 nominal_frontier region 0 m: t 71.82 s, found True, min clearance 0.1487 m
- warehouse crazyflie layout 13 lawnmower region 0 m: t 71.82 s, found True, min clearance 0.1487 m
- warehouse crazyflie layout 13 random_walk region 0 m: t 71.82 s, found True, min clearance 0.1487 m
- warehouse crazyflie layout 13 nominal_frontier region 2 m: t 46.66 s, found False, min clearance 0.1486 m
- warehouse crazyflie layout 13 random_walk region 2 m: t 75.34 s, found True, min clearance 0.1498 m
- warehouse crazyflie layout 13 lawnmower region 5 m: t 65.96 s, found False, min clearance 0.1484 m
- warehouse crazyflie layout 13 random_walk region unknown: t 98.28 s, found False, min clearance 0.1475 m
- warehouse crazyflie layout 14 random_walk region 0 m: t 163.76 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 14 lawnmower region 2 m: t 29.1 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 14 random_walk region 2 m: t 29.06 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 14 lawnmower region 5 m: t 117.08 s, found False, min clearance 0.1495 m
- warehouse crazyflie layout 14 random_walk region 5 m: t 105.1 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 14 lawnmower region unknown: t 12.16 s, found False, min clearance 0.1459 m
- warehouse crazyflie layout 14 random_walk region unknown: t 12.46 s, found False, min clearance 0.1497 m
- warehouse crazyflie layout 15 oracle region unknown: t 46.4 s, found True, min clearance 0.1488 m
- warehouse crazyflie layout 15 nominal_frontier region 0 m: t 46.4 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 15 lawnmower region 0 m: t 46.4 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 15 random_walk region 0 m: t 46.4 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 15 lawnmower region 2 m: t 74.52 s, found False, min clearance 0.1486 m
- warehouse crazyflie layout 15 lawnmower region 5 m: t 39.06 s, found False, min clearance 0.1496 m
- warehouse crazyflie layout 15 random_walk region 5 m: t 65.26 s, found False, min clearance 0.1487 m
- warehouse crazyflie layout 15 lawnmower region unknown: t 13.12 s, found False, min clearance 0.1491 m
- warehouse crazyflie layout 15 random_walk region unknown: t 52.2 s, found False, min clearance 0.1483 m
- warehouse crazyflie layout 16 frontier region unknown: t 171.6 s, found False, min clearance 0.1496 m
- warehouse crazyflie layout 16 nominal_frontier region 0 m: t 64.22 s, found False, min clearance 0.1483 m
- warehouse crazyflie layout 16 lawnmower region 0 m: t 64.22 s, found False, min clearance 0.1483 m
- warehouse crazyflie layout 16 random_walk region 0 m: t 64.22 s, found False, min clearance 0.1483 m
- warehouse crazyflie layout 16 nominal_frontier region 2 m: t 51.5 s, found False, min clearance 0.1486 m
- warehouse crazyflie layout 16 lawnmower region 2 m: t 73.64 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 16 nominal_frontier region 5 m: t 27.12 s, found False, min clearance 0.1462 m
- warehouse crazyflie layout 16 lawnmower region unknown: t 53.74 s, found False, min clearance 0.1464 m
- warehouse crazyflie layout 17 oracle region unknown: t 26.92 s, found True, min clearance 0.1477 m
- warehouse crazyflie layout 17 nominal_frontier region 0 m: t 26.92 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 17 lawnmower region 0 m: t 26.92 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 17 random_walk region 0 m: t 26.92 s, found False, min clearance 0.1477 m
- warehouse crazyflie layout 17 lawnmower region 2 m: t 120.44 s, found False, min clearance 0.1483 m
- warehouse crazyflie layout 17 lawnmower region 5 m: t 33.08 s, found False, min clearance 0.1487 m
- warehouse crazyflie layout 17 lawnmower region unknown: t 37.92 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 18 oracle region unknown: t 35.32 s, found True, min clearance 0.1487 m
- warehouse crazyflie layout 18 nominal_frontier region 0 m: t 35.32 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 18 lawnmower region 0 m: t 35.32 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 18 random_walk region 0 m: t 35.32 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 18 lawnmower region 2 m: t 40.08 s, found False, min clearance 0.1472 m
- warehouse crazyflie layout 18 random_walk region 2 m: t 15.7 s, found False, min clearance 0.1485 m
- warehouse crazyflie layout 18 nominal_frontier region 5 m: t 34.02 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 18 lawnmower region 5 m: t 49.2 s, found False, min clearance 0.1494 m
- warehouse crazyflie layout 18 lawnmower region unknown: t 108.9 s, found False, min clearance 0.1486 m
- warehouse crazyflie layout 18 random_walk region unknown: t 17.48 s, found False, min clearance 0.1489 m
- warehouse crazyflie layout 19 nominal_frontier region 2 m: t 92.2 s, found False, min clearance 0.1488 m
- warehouse crazyflie layout 19 lawnmower region 2 m: t 30.02 s, found False, min clearance 0.1479 m
