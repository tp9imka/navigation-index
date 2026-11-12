`python3 results/matrix_depth_0.compare.py`. Input: synthetic. depth_cam_87 rows from matrix_depth_0.json; ideal and crazyflie rows from matrix_0.json restricted to the same layouts (index 0-5, seed 0), so every cell is paired on identical worlds. n = 6 per cell, 48 per pooled row. Intervals: 95 % Wilson.

## Preset `depth_cam_87` (layouts 0-5)

Cell = reached % / collision %, n = 6.

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office | pooled reached % [95 % CI] | pooled collision % [95 % CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | 100 / 0 | 100 / 0 | 33 / 50 | 83 / 0 | 83 / 0 | 100 / 0 | 83 / 0 | 17 / 83 | 75 [61, 85] (36/48) | 17 [9, 30] (8/48) |
| astar_unknown_f2 | 100 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 17 / 17 | 100 / 0 | 50 / 0 | 0 / 0 | 46 [33, 60] (22/48) | 2 [0, 11] (1/48) |
| dstar_lite | 100 / 0 | 100 / 0 | 33 / 33 | 83 / 0 | 67 / 0 | 100 / 0 | 83 / 0 | 17 / 83 | 73 [59, 83] (35/48) | 15 [7, 27] (7/48) |
| dwa_mem | 67 / 17 | 0 / 0 | 17 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 0 / 0 | 17 / 0 | 25 [15, 39] (12/48) | 2 [0, 11] (1/48) |
| mppi_astar | 100 / 0 | 100 / 0 | 83 / 0 | 100 / 0 | 83 / 0 | 100 / 0 | 100 / 0 | 17 / 83 | 85 [73, 93] (41/48) | 10 [5, 22] (5/48) |

Best per family (highest reached, then lowest collision; ties listed): random => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); narrow_gap => mppi_astar (83 / 0); office => mppi_astar (100 / 0); warehouse => astar_unknown/mppi_astar (83 / 0); forest => astar_unknown/astar_unknown_f2/dstar_lite/dwa_mem/mppi_astar (100 / 0); maze => mppi_astar (100 / 0); glass_office => dwa_mem (17 / 0).

## Preset `ideal` (layouts 0-5)

Cell = reached % / collision %, n = 6.

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office | pooled reached % [95 % CI] | pooled collision % [95 % CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | 100 / 0 | 100 / 0 | 83 / 0 | 67 / 0 | 50 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 88 [75, 94] (42/48) | 0 [0, 7] (0/48) |
| astar_unknown_f2 | 67 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 83 / 0 | 0 / 0 | 0 / 0 | 31 [20, 45] (15/48) | 0 [0, 7] (0/48) |
| dstar_lite | 100 / 0 | 100 / 0 | 83 / 0 | 67 / 0 | 83 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 92 [80, 97] (44/48) | 0 [0, 7] (0/48) |
| dwa_mem | 83 / 0 | 0 / 0 | 33 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 0 / 0 | 17 / 0 | 29 [18, 43] (14/48) | 0 [0, 7] (0/48) |
| mppi_astar | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 50 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 94 [83, 98] (45/48) | 0 [0, 7] (0/48) |

Best per family (highest reached, then lowest collision; ties listed): random => astar_unknown/dstar_lite/mppi_astar (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); narrow_gap => mppi_astar (100 / 0); office => mppi_astar (100 / 0); warehouse => dstar_lite (83 / 0); forest => astar_unknown/dstar_lite/dwa_mem/mppi_astar (100 / 0); maze => astar_unknown/dstar_lite/mppi_astar (100 / 0); glass_office => astar_unknown/dstar_lite/mppi_astar (100 / 0).

## Preset `crazyflie` (layouts 0-5)

Cell = reached % / collision %, n = 6.

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office | pooled reached % [95 % CI] | pooled collision % [95 % CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | 100 / 0 | 100 / 0 | 33 / 0 | 17 / 17 | 0 / 50 | 100 / 0 | 50 / 0 | 17 / 67 | 52 [38, 66] (25/48) | 17 [9, 30] (8/48) |
| astar_unknown_f2 | 100 / 0 | 100 / 0 | 17 / 0 | 17 / 17 | 33 / 0 | 100 / 0 | 50 / 0 | 0 / 83 | 52 [38, 66] (25/48) | 12 [6, 25] (6/48) |
| dstar_lite | 100 / 0 | 100 / 0 | 17 / 0 | 0 / 33 | 17 / 67 | 83 / 17 | 50 / 0 | 17 / 67 | 48 [34, 62] (23/48) | 23 [13, 37] (11/48) |
| dwa_mem | 83 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 33 | 33 / 17 | 0 / 0 | 17 / 0 | 17 [9, 30] (8/48) | 6 [2, 17] (3/48) |
| mppi_astar | 83 / 17 | 100 / 0 | 17 / 83 | 0 / 83 | 0 / 100 | 100 / 0 | 0 / 100 | 0 / 83 | 38 [25, 52] (18/48) | 58 [44, 71] (28/48) |

Best per family (highest reached, then lowest collision; ties listed): random => astar_unknown/astar_unknown_f2/dstar_lite (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); narrow_gap => astar_unknown (33 / 0); office => astar_unknown/astar_unknown_f2 (17 / 17); warehouse => astar_unknown_f2 (33 / 0); forest => astar_unknown/astar_unknown_f2/mppi_astar (100 / 0); maze => astar_unknown/astar_unknown_f2/dstar_lite (50 / 0); glass_office => dwa_mem (17 / 0).

## depth_cam_87 outcome mix and collision material

| planner | reached | collision | stuck | timeout | hits on glass | hits on other |
|---|---|---|---|---|---|---|
| astar_unknown | 36 | 8 | 3 | 1 | 5 | 3 |
| astar_unknown_f2 | 22 | 1 | 22 | 3 | 0 | 1 |
| dstar_lite | 35 | 7 | 4 | 2 | 5 | 2 |
| dwa_mem | 12 | 1 | 31 | 4 | 0 | 1 |
| mppi_astar | 41 | 5 | 2 | 0 | 4 | 1 |

## Same outcome as depth_cam_87, run by run (layouts 0-5)

| planner | vs ideal | vs crazyflie |
|---|---|---|
| astar_unknown | 35/48 | 30/48 |
| astar_unknown_f2 | 37/48 | 28/48 |
| dstar_lite | 36/48 | 30/48 |
| dwa_mem | 43/48 | 37/48 |
| mppi_astar | 40/48 | 23/48 |

## Prior-map rows of matrix_0.json: ideal vs crazyflie, run by run (all layouts)

Same outcome and same min clearance on both presets. These planners never read the scan, so they were not re-run on depth_cam_87; their depth column equals ideal.

| planner | identical runs |
|---|---|
| astar_known | 160/160 |
| informed_rrt_star | 160/160 |
| astar_mpc | 160/160 |
| thetastar_known | 160/160 |
| lazy_thetastar_known | 160/160 |
