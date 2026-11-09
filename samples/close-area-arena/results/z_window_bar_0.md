`python run_z.py --layouts 50 --seed 0` from samples/close-area-arena (synthetic: simulated layouts, vehicle and sensor), wall 295 s

Layouts where the 1.0 +- 0.15 m band has a 2D path A => B: 7 of 50.

| planner | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | p95 time to goal s | median min clearance m | replans | plan median ms | plan p95 ms | setup median ms | fallback replans | no-path replans |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_esdf 2.5D | 50 | 14.0 | 0.0 | 86.0 | 0.0 | 28.16 | 36.42 | 1.0 | 4818 | 44.79 | 82.79 | - | 0 | 4300 |
| astar_esdf_3d | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 28.89 | 41.3 | 0.253 | 1075 | 26.04 | 162.61 | 185.89 | 0 | 0 |

Reached by layout class:

| class | layouts | astar_esdf 2.5D | astar_esdf_3d |
|---|---|---|---|
| band has a 2D path | 7 | 7 | 7 |
| band blocked (needs altitude) | 43 | 0 | 43 |

Per run (outcome, min clearance m, z range flown m):

| run | elements | band 2D path | astar_esdf 2.5D | astar_esdf_3d |
|---|---|---|---|---|
| 0 | bars z 1.304, window z 2.007 | no | stuck 1.0 [1.0, 1.0] | reached 0.2584 [1.0, 2.048] |
| 1 | window z 1.937, bars z 0.724/2.391 | no | stuck 1.0 [1.0, 1.0] | reached 0.2827 [0.95, 1.947] |
| 2 | bars z 0.633/2.037, window z 1.796 | no | stuck 1.0 [1.0, 1.0] | reached 0.2248 [0.97, 1.733] |
| 3 | bars z 1.025/1.882, window z 1.134 | no | stuck 1.0 [1.0, 1.0] | reached 0.2607 [1.0, 1.433] |
| 4 | bars z 2.218, window z 0.909 | yes | reached 0.2089 [1.0, 1.0] | reached 0.2283 [0.91, 1.0] |
| 5 | bars z 0.519, window z 1.445 | no | stuck 1.0 [1.0, 1.0] | reached 0.2486 [0.959, 1.434] |
| 6 | bars z 0.949, window z 1.078 | no | stuck 1.0 [1.0, 1.0] | reached 0.2813 [1.0, 1.527] |
| 7 | bars z 0.82/1.703, window z 1.395 | no | stuck 1.0 [1.0, 1.0] | reached 0.2479 [0.993, 1.346] |
| 8 | window z 0.605, bars z 0.55/2.268 | no | stuck 1.0 [1.0, 1.0] | reached 0.2489 [0.656, 1.35] |
| 9 | bars z 0.825/2.537, window z 0.605 | no | stuck 1.0 [1.0, 1.0] | reached 0.2446 [0.659, 1.503] |
| 10 | window z 0.501, window z 0.646 | no | stuck 1.0 [1.0, 1.0] | reached 0.2084 [0.553, 1.0] |
| 11 | bars z 0.576/1.945, window z 1.494 | no | stuck 1.0 [1.0, 1.0] | reached 0.2513 [0.989, 1.447] |
| 12 | bars z 1.024, window z 0.58 | no | stuck 1.0 [1.0, 1.0] | reached 0.2642 [0.557, 1.539] |
| 13 | window z 2.198, bars z 2.157 | no | stuck 1.0 [1.0, 1.0] | reached 0.2356 [0.962, 2.148] |
| 14 | window z 0.909, bars z 0.707 | yes | reached 0.2089 [1.0, 1.0] | reached 0.2542 [0.95, 1.32] |
| 15 | window z 1.732, window z 1.368 | no | stuck 1.0 [1.0, 1.0] | reached 0.2588 [0.963, 1.742] |
| 16 | bars z 1.119, window z 1.124 | no | stuck 1.0 [1.0, 1.0] | reached 0.2708 [0.95, 1.676] |
| 17 | bars z 0.767/1.966, window z 1.798 | no | stuck 1.0 [1.0, 1.0] | reached 0.2563 [0.998, 1.881] |
| 18 | bars z 2.246, window z 1.102 | yes | reached 0.1983 [1.0, 1.0] | reached 0.2526 [0.958, 1.149] |
| 19 | window z 2.144, bars z 1.626 | no | stuck 1.0 [1.0, 1.0] | reached 0.2682 [0.955, 2.135] |
| 20 | window z 2.227, bars z 0.7/1.574 | no | stuck 1.0 [1.0, 1.0] | reached 0.2813 [1.0, 2.25] |
| 21 | window z 1.873, window z 2.375 | no | stuck 1.0 [1.0, 1.0] | reached 0.2656 [1.0, 2.348] |
| 22 | window z 1.768, bars z 0.905/1.735 | no | stuck 1.0 [1.0, 1.0] | reached 0.2529 [1.0, 2.327] |
| 23 | window z 1.957, bars z 0.723/1.894 | no | stuck 1.0 [1.0, 1.0] | reached 0.2022 [0.959, 1.95] |
| 24 | bars z 1.072, window z 0.86 | no | stuck 1.0 [1.0, 1.0] | reached 0.2489 [0.851, 1.81] |
| 25 | window z 1.805, window z 2.139 | no | stuck 1.0 [1.0, 1.0] | reached 0.2236 [0.999, 2.147] |
| 26 | window z 2.278, bars z 0.567/1.528 | no | stuck 1.0 [1.0, 1.0] | reached 0.2216 [1.0, 2.249] |
| 27 | window z 2.33, window z 1.35 | no | stuck 1.0 [1.0, 1.0] | reached 0.2551 [1.0, 2.329] |
| 28 | window z 1.603, window z 2.379 | no | stuck 1.0 [1.0, 1.0] | reached 0.2322 [0.963, 2.325] |
| 29 | window z 2.466, window z 1.845 | no | stuck 1.0 [1.0, 1.0] | reached 0.2463 [1.0, 2.444] |
| 30 | bars z 1.911, window z 1.227 | no | stuck 1.0 [1.0, 1.0] | reached 0.2772 [0.961, 1.466] |
| 31 | window z 0.507, window z 0.588 | no | stuck 1.0 [1.0, 1.0] | reached 0.2533 [0.55, 1.0] |
| 32 | window z 2.091, window z 0.715 | no | stuck 1.0 [1.0, 1.0] | reached 0.225 [0.758, 2.046] |
| 33 | window z 1.818, window z 1.704 | no | stuck 1.0 [1.0, 1.0] | reached 0.2484 [1.0, 1.842] |
| 34 | window z 2.033, window z 2.156 | no | stuck 1.0 [1.0, 1.0] | reached 0.2664 [1.0, 2.15] |
| 35 | window z 1.458, bars z 1.064 | no | stuck 1.0 [1.0, 1.0] | reached 0.2874 [1.0, 1.72] |
| 36 | window z 1.495, bars z 0.87 | no | stuck 1.0 [1.0, 1.0] | reached 0.2267 [0.965, 1.71] |
| 37 | bars z 0.955, window z 2.273 | no | stuck 1.0 [1.0, 1.0] | reached 0.2379 [1.0, 2.246] |
| 38 | window z 2.441, window z 0.959 | no | stuck 1.0 [1.0, 1.0] | reached 0.2565 [0.95, 2.431] |
| 39 | window z 1.158, window z 0.965 | no | stuck 1.0 [1.0, 1.0] | reached 0.2378 [0.95, 1.143] |
| 40 | window z 2.189, bars z 0.631/1.891 | no | stuck 1.0 [1.0, 1.0] | reached 0.2559 [0.929, 2.149] |
| 41 | bars z 0.516/2.355, window z 1.214 | no | stuck 1.0 [1.0, 1.0] | reached 0.2652 [0.954, 1.33] |
| 42 | window z 1.987, window z 2.039 | no | stuck 1.0 [1.0, 1.0] | reached 0.2432 [1.0, 2.049] |
| 43 | window z 0.888, bars z 0.678/1.787 | yes | reached 0.1875 [1.0, 1.0] | reached 0.264 [0.852, 1.232] |
| 44 | window z 0.976, bars z 1.527 | yes | reached 0.246 [1.0, 1.0] | reached 0.2385 [0.87, 1.0] |
| 45 | window z 1.147, bars z 0.783 | yes | reached 0.1528 [1.0, 1.0] | reached 0.2592 [0.966, 1.518] |
| 46 | window z 1.331, bars z 1.157 | no | stuck 1.0 [1.0, 1.0] | reached 0.2808 [0.572, 1.35] |
| 47 | bars z 2.134, window z 2.317 | no | stuck 1.0 [1.0, 1.0] | reached 0.2427 [1.0, 2.332] |
| 48 | window z 0.929, bars z 0.483/1.969 | yes | reached 0.2289 [1.0, 1.0] | reached 0.2765 [0.95, 1.135] |
| 49 | window z 1.941, window z 1.178 | no | stuck 1.0 [1.0, 1.0] | reached 0.2237 [1.0, 1.948] |

Plot: [z_window_bar_0_run0.png](z_window_bar_0_run0.png), run 0 (first run where 2.5D did not reach B and 3D did). Top panel: side view, the true geometry under the 3D track (horizontal = distance along the track, vertical = height 0-3 m; dark = obstacle, grey = within 0.15 m, blue = 3D height, green = A, red = B). Bottom panel: top view (dark = blocks the 1.0 +- 0.15 m band, light grey = obstacle only above or below the band, orange = 2.5D track, blue = 3D track).
