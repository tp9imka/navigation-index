`python bench.py --layouts 20 --seed 0 --workers 14` from samples/close-area-planner-hybrid-astar. Input: synthetic (simulated layouts, vehicle and sensor). Seed 0, 20 layouts per cell, 14 processes, wall 207.5 s. Planner maps: unknown (log-odds from range hits), geofenced.

Parity: astar_unknown on the stock vehicle vs close-area-benchmark/results/matrix_0.json, same outcome, min clearance and path length: 200/200 runs.

Replan ms are pooled over every replan of the cell, measured with all processes busy (not a clean timing; see timing_jobs1_0.md). Flown max / p95 heading change per metre: median over runs that reached B, truth path resampled every 0.25 m. Stuck while moving = scorer outcome stuck (|p(t) - p(t - 10 s)| < 0.2 m) with truth speed above 0.3 m/s over the last 0.5 s: the vehicle was flying back over the point it passed 10 s earlier (a dead end turned back from), not hovering. The arena scorer ends those runs; they count as stuck here too.

| vehicle | preset | planner | family | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | flown max rad/m | flown p95 rad/m | replan ms median / p95 | grid fallback % of replans | stuck while moving % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| stock | ideal | astar_unknown | random | 100 | 0 | 0 | 0 | 19.01 | 23.962 | 0.615 | 1.138 | 0.199 | 25.29 / 81.23 | - | 0 |
| stock | ideal | astar_unknown | u_trap | 100 | 0 | 0 | 0 | 22.12 | 26.002 | 0.597 | 2.127 | 0.785 | 41.71 / 84.82 | - | 0 |
| stock | ideal | astar_unknown | narrow_gap | 90 | 0 | 5 | 5 | 37.51 | 37.698 | 0.254 | 6.678 | 0.655 | 46.67 / 86.07 | - | 5 |
| stock | ideal | astar_unknown | office | 95 | 0 | 5 | 0 | 22.8 | 10.637 | 0.261 | 2.77 | 1.697 | 7.56 / 21.74 | - | 5 |
| stock | ideal | astar_unknown | warehouse | 55 | 0 | 45 | 0 | 49.12 | 27.901 | 0.304 | 3.615 | 1.566 | 25.48 / 81.04 | - | 40 |
| stock | ideal | astar_unknown | forest | 100 | 0 | 0 | 0 | 23.31 | 24.17 | 0.603 | 1.777 | 0.816 | 29.52 / 86.21 | - | 0 |
| stock | ideal | astar_unknown | maze | 95 | 0 | 5 | 0 | 50.06 | 39.409 | 0.589 | 6.951 | 1.803 | 34.47 / 95.95 | - | 5 |
| stock | ideal | astar_unknown | glass_office | 95 | 0 | 5 | 0 | 30.34 | 14.416 | 0.273 | 2.936 | 1.856 | 7.61 / 30.55 | - | 0 |
| stock | ideal | astar_unknown_pp | random | 100 | 0 | 0 | 0 | 19.01 | 23.961 | 0.615 | 1.138 | 0.199 | 26.06 / 83.17 | - | 0 |
| stock | ideal | astar_unknown_pp | u_trap | 100 | 0 | 0 | 0 | 22.23 | 25.989 | 0.594 | 2.278 | 0.587 | 42.33 / 85.7 | - | 0 |
| stock | ideal | astar_unknown_pp | narrow_gap | 85 | 0 | 10 | 5 | 38.84 | 37.711 | 0.258 | 6.836 | 0.614 | 50.77 / 107.38 | - | 5 |
| stock | ideal | astar_unknown_pp | office | 95 | 0 | 5 | 0 | 22.8 | 10.637 | 0.263 | 2.77 | 1.697 | 8.15 / 22.6 | - | 5 |
| stock | ideal | astar_unknown_pp | warehouse | 55 | 0 | 45 | 0 | 49.66 | 27.901 | 0.299 | 3.753 | 1.567 | 24.6 / 81.95 | - | 45 |
| stock | ideal | astar_unknown_pp | forest | 100 | 0 | 0 | 0 | 23.71 | 24.218 | 0.603 | 1.606 | 0.747 | 32.31 / 106.7 | - | 0 |
| stock | ideal | astar_unknown_pp | maze | 95 | 0 | 5 | 0 | 50.62 | 39.316 | 0.591 | 7.831 | 1.803 | 36.28 / 98.26 | - | 5 |
| stock | ideal | astar_unknown_pp | glass_office | 95 | 0 | 5 | 0 | 30.1 | 14.497 | 0.272 | 2.945 | 1.856 | 7.56 / 32.81 | - | 0 |
| stock | ideal | hybrid_astar | random | 100 | 0 | 0 | 0 | 18.44 | 24.169 | 0.67 | 0.867 | 0.324 | 12.87 / 22.46 | 0 | 0 |
| stock | ideal | hybrid_astar | u_trap | 100 | 0 | 0 | 0 | 20.08 | 26.472 | 0.71 | 2.29 | 0.752 | 12.96 / 21.82 | 0 | 0 |
| stock | ideal | hybrid_astar | narrow_gap | 70 | 0 | 25 | 5 | 32.1 | 30.916 | 0.285 | 3.664 | 0.743 | 13.39 / 23.88 | 0 | 20 |
| stock | ideal | hybrid_astar | office | 90 | 0 | 5 | 5 | 20.19 | 11.057 | 0.264 | 2.337 | 1.445 | 13.73 / 24.05 | 0 | 5 |
| stock | ideal | hybrid_astar | warehouse | 55 | 0 | 45 | 0 | 48.28 | 27.405 | 0.259 | 2.168 | 1.161 | 13.27 / 26.6 | 0 | 40 |
| stock | ideal | hybrid_astar | forest | 100 | 0 | 0 | 0 | 22.47 | 24.334 | 0.552 | 1.683 | 0.674 | 13.03 / 20.87 | 0 | 0 |
| stock | ideal | hybrid_astar | maze | 90 | 0 | 5 | 5 | 46.46 | 42.498 | 0.46 | 5.548 | 1.186 | 13.7 / 26.97 | 0 | 5 |
| stock | ideal | hybrid_astar | glass_office | 85 | 0 | 15 | 0 | 29.2 | 13.239 | 0.26 | 2.037 | 1.137 | 13.64 / 25.63 | 0 | 5 |
| stock | crazyflie | astar_unknown | random | 100 | 0 | 0 | 0 | 22.51 | 24.634 | 0.59 | 2.355 | 1.143 | 35.69 / 95.6 | - | 0 |
| stock | crazyflie | astar_unknown | office | 35 | 25 | 35 | 5 | 18.84 | 7.6 | 0.225 | 7.333 | 3.018 | 9.91 / 29.53 | - | 15 |
| stock | crazyflie | astar_unknown_pp | random | 95 | 5 | 0 | 0 | 21.4 | 24.182 | 0.62 | 1.864 | 0.778 | 37.98 / 89.9 | - | 0 |
| stock | crazyflie | astar_unknown_pp | office | 45 | 40 | 15 | 0 | 20.18 | 7.296 | 0.196 | 8.599 | 3.3 | 9.95 / 30.22 | - | 5 |
| stock | crazyflie | hybrid_astar | random | 95 | 5 | 0 | 0 | 21.24 | 24.558 | 0.601 | 3.119 | 0.726 | 13.13 / 20.7 | 0 | 0 |
| stock | crazyflie | hybrid_astar | office | 40 | 45 | 15 | 0 | 28.32 | 9.944 | 0.19 | 6.365 | 2.094 | 13.45 / 26.83 | 0 | 10 |
| turn1 | ideal | astar_unknown | random | 100 | 0 | 0 | 0 | 18.99 | 23.979 | 0.615 | 0.855 | 0.214 | 29.27 / 82.29 | - | 0 |
| turn1 | ideal | astar_unknown | u_trap | 100 | 0 | 0 | 0 | 22.64 | 26.107 | 0.596 | 1.437 | 0.857 | 43.65 / 96.13 | - | 0 |
| turn1 | ideal | astar_unknown | narrow_gap | 90 | 0 | 0 | 10 | 37.62 | 39.037 | 0.267 | 7.529 | 0.709 | 45.84 / 86.85 | - | 0 |
| turn1 | ideal | astar_unknown | office | 90 | 0 | 5 | 5 | 21.89 | 10.782 | 0.265 | 2.583 | 1.817 | 7.82 / 21.41 | - | 5 |
| turn1 | ideal | astar_unknown | warehouse | 70 | 0 | 30 | 0 | 50.86 | 27.98 | 0.305 | 2.865 | 1.489 | 22.11 / 80.75 | - | 25 |
| turn1 | ideal | astar_unknown | forest | 100 | 0 | 0 | 0 | 23.37 | 24.154 | 0.588 | 1.204 | 0.644 | 29.85 / 86.2 | - | 0 |
| turn1 | ideal | astar_unknown | maze | 90 | 0 | 5 | 5 | 48.76 | 39.534 | 0.587 | 8.353 | 1.45 | 39.57 / 101.49 | - | 5 |
| turn1 | ideal | astar_unknown | glass_office | 90 | 0 | 10 | 0 | 30.92 | 14.164 | 0.273 | 2.74 | 1.657 | 8.22 / 36.76 | - | 0 |
| turn1 | ideal | astar_unknown_pp | random | 100 | 0 | 0 | 0 | 19 | 23.977 | 0.617 | 0.855 | 0.204 | 28.85 / 80.64 | - | 0 |
| turn1 | ideal | astar_unknown_pp | u_trap | 100 | 0 | 0 | 0 | 23.03 | 26.125 | 0.59 | 1.774 | 0.875 | 46.01 / 101.03 | - | 0 |
| turn1 | ideal | astar_unknown_pp | narrow_gap | 85 | 0 | 5 | 10 | 35.5 | 37.689 | 0.271 | 6.309 | 0.693 | 47.39 / 93.68 | - | 5 |
| turn1 | ideal | astar_unknown_pp | office | 90 | 0 | 5 | 5 | 21.89 | 10.782 | 0.265 | 2.669 | 1.825 | 7.7 / 19.5 | - | 5 |
| turn1 | ideal | astar_unknown_pp | warehouse | 55 | 0 | 45 | 0 | 50.52 | 28.156 | 0.302 | 2.636 | 1.455 | 22.15 / 81.63 | - | 30 |
| turn1 | ideal | astar_unknown_pp | forest | 100 | 0 | 0 | 0 | 23.32 | 24.145 | 0.588 | 1.192 | 0.658 | 30.05 / 86.78 | - | 0 |
| turn1 | ideal | astar_unknown_pp | maze | 90 | 0 | 10 | 0 | 49.14 | 38.95 | 0.593 | 5.329 | 1.442 | 37.84 / 97.91 | - | 10 |
| turn1 | ideal | astar_unknown_pp | glass_office | 85 | 0 | 15 | 0 | 31.32 | 14.165 | 0.273 | 2.872 | 1.572 | 8.18 / 34.54 | - | 5 |
| turn1 | ideal | hybrid_astar | random | 100 | 0 | 0 | 0 | 18.17 | 24.085 | 0.709 | 0.854 | 0.445 | 12.7 / 21.94 | 0 | 0 |
| turn1 | ideal | hybrid_astar | u_trap | 100 | 0 | 0 | 0 | 19.91 | 26.593 | 0.775 | 1.69 | 0.69 | 12.65 / 21.73 | 0 | 0 |
| turn1 | ideal | hybrid_astar | narrow_gap | 70 | 0 | 30 | 0 | 38.31 | 34.373 | 0.282 | 2.248 | 0.708 | 13.22 / 24.37 | 0 | 25 |
| turn1 | ideal | hybrid_astar | office | 85 | 0 | 10 | 5 | 20.72 | 12.335 | 0.264 | 2.245 | 1.321 | 13.77 / 23.61 | 0 | 0 |
| turn1 | ideal | hybrid_astar | warehouse | 45 | 0 | 55 | 0 | 49.96 | 27.328 | 0.258 | 2.554 | 1.206 | 13.18 / 25.01 | 0 | 55 |
| turn1 | ideal | hybrid_astar | forest | 100 | 0 | 0 | 0 | 22.09 | 24.426 | 0.547 | 1.244 | 0.692 | 12.95 / 20.08 | 0 | 0 |
| turn1 | ideal | hybrid_astar | maze | 80 | 0 | 15 | 5 | 44.35 | 41.986 | 0.466 | 4.819 | 1.123 | 13.58 / 24.18 | 0 | 15 |
| turn1 | ideal | hybrid_astar | glass_office | 75 | 0 | 25 | 0 | 30.16 | 14.138 | 0.27 | 1.919 | 1.227 | 13.67 / 23.94 | 0 | 20 |
| turn1 | crazyflie | astar_unknown | random | 100 | 0 | 0 | 0 | 22.17 | 24.833 | 0.628 | 2.603 | 0.974 | 35.75 / 87.68 | - | 0 |
| turn1 | crazyflie | astar_unknown | office | 35 | 35 | 25 | 5 | 19.46 | 8.007 | 0.214 | 6.391 | 3.012 | 10.39 / 35.2 | - | 10 |
| turn1 | crazyflie | astar_unknown_pp | random | 95 | 5 | 0 | 0 | 21.52 | 24.258 | 0.642 | 1.503 | 1.019 | 37.19 / 91.06 | - | 0 |
| turn1 | crazyflie | astar_unknown_pp | office | 35 | 30 | 30 | 5 | 19.5 | 7.363 | 0.192 | 4.225 | 2.545 | 9.82 / 36.88 | - | 5 |
| turn1 | crazyflie | hybrid_astar | random | 100 | 0 | 0 | 0 | 21.77 | 24.776 | 0.618 | 2.101 | 0.718 | 13.13 / 21.54 | 0 | 0 |
| turn1 | crazyflie | hybrid_astar | office | 30 | 35 | 35 | 0 | 23.44 | 9.551 | 0.184 | 7.536 | 2.167 | 13.72 / 33.02 | 0 | 20 |

Totals per vehicle and preset (all families of the preset pooled):

| vehicle | preset | planner | runs | reached % | collision % | stuck % | stuck while moving % | timeout % | replan ms median / p95 |
|---|---|---|---|---|---|---|---|---|---|
| stock | ideal | astar_unknown | 160 | 91.2 | 0 | 8.1 | 6.9 | 0.6 | 22.38 / 84.86 |
| stock | ideal | astar_unknown_pp | 160 | 90.6 | 0 | 8.8 | 7.5 | 0.6 | 22.85 / 89.81 |
| stock | ideal | hybrid_astar | 160 | 86.2 | 0 | 11.9 | 9.4 | 1.9 | 13.36 / 24.94 |
| stock | crazyflie | astar_unknown | 40 | 67.5 | 12.5 | 17.5 | 7.5 | 2.5 | 14.21 / 84.45 |
| stock | crazyflie | astar_unknown_pp | 40 | 70 | 22.5 | 7.5 | 2.5 | 0 | 14.19 / 83.18 |
| stock | crazyflie | hybrid_astar | 40 | 67.5 | 25 | 7.5 | 5 | 0 | 13.23 / 24.28 |
| turn1 | ideal | astar_unknown | 160 | 91.2 | 0 | 6.2 | 4.4 | 2.5 | 22.64 / 87.32 |
| turn1 | ideal | astar_unknown_pp | 160 | 88.1 | 0 | 10 | 6.9 | 1.9 | 22.35 / 87.71 |
| turn1 | ideal | hybrid_astar | 160 | 81.9 | 0 | 16.9 | 14.4 | 1.2 | 13.26 / 23.82 |
| turn1 | crazyflie | astar_unknown | 40 | 67.5 | 17.5 | 12.5 | 5 | 2.5 | 14.97 / 79.77 |
| turn1 | crazyflie | astar_unknown_pp | 40 | 65 | 17.5 | 15 | 2.5 | 2.5 | 14.4 / 81.44 |
| turn1 | crazyflie | hybrid_astar | 40 | 65 | 17.5 | 17.5 | 10 | 0 | 13.31 / 28.58 |

Replan wall time pooled over every replan of the file, per planner:

| planner | replans | median ms | p95 ms | p99 ms | max ms | replans > 200 ms |
|---|---|---|---|---|---|---|
| astar_unknown | 32003 | 20.67 | 85.55 | 105.76 | 199.63 | 0 |
| astar_unknown_pp | 31609 | 20.79 | 88.02 | 114.47 | 284.75 | 10 |
| hybrid_astar | 30451 | 13.30 | 24.75 | 33.58 | 142.18 | 0 |

Paired: median of (planner - astar_unknown) time to B on runs where both reached, per vehicle (both presets):

| vehicle | planner | median delta time to B s | paired runs | median delta path m |
|---|---|---|---|---|
| stock | astar_unknown_pp | 0 | 170 | 0 |
| stock | hybrid_astar | -1.21 | 160 | 0.37 |
| turn1 | astar_unknown_pp | 0 | 166 | 0 |
| turn1 | hybrid_astar | -0.94 | 152 | 0.37 |
