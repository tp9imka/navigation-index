`python bench.py --layouts 20 --seed 0 --workers 14 --parity` from samples/close-area-benchmark. Input: synthetic (simulated layouts, vehicle and sensors). Scored on truth. Seed 0, 20 layouts per cell, 14 worker processes, wall 323.4 s. Run time limit per family (s): random 60, u_trap 60, narrow_gap 60, office 60, warehouse 120, forest 60, maze 120, glass_office 60.

Parity with run.evaluate (ideal x random, runs with identical outcome and min clearance): straight 10/10, astar_known 10/10

Rows dwa, dwa_mem, bug2, tangent_bug, dstar_lite added later by `python bench.py --add-to matrix_0 --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite --recheck vfh_plus,astar_unknown --workers 14` (2026-11-09, same layouts and limits, 14 worker processes, wall 216.2 s for 2240 runs, Python 3.12.10, numpy 2.5.4). All other rows are kept from the first run. Existing rows re-run as a check, runs identical in outcome, min clearance, path length and time to goal: vfh_plus 320/320, astar_unknown 320/320.

### Preset `ideal`

Cell = reached % / collision % (20 layouts unless stated).

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| straight | 40 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 15 / 0 | 0 / 5 | 0 / 0 |
| freest_beam | 80 / 0 | 0 / 0 | 0 / 0 | 15 / 5 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 5 |
| apf_escape | 100 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 10 / 0 | 0 / 0 |
| vfh_plus | 100 / 0 | 0 / 0 | 50 / 0 | 40 / 0 | 20 / 0 | 100 / 0 | 10 / 0 | 50 / 0 |
| astar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown | 100 / 0 | 100 / 0 | 90 / 0 | 95 / 0 | 55 / 0 | 100 / 0 | 95 / 0 | 95 / 0 |
| informed_rrt_star | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_mpc | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown_f2 | 75 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 65 / 0 | 0 / 0 | 0 / 0 |
| dwa | 80 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 90 / 0 | 0 / 0 | 5 / 0 |
| dwa_mem | 75 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 75 / 0 | 0 / 0 | 5 / 0 |
| bug2 | 90 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 20 / 0 | 0 / 0 |
| tangent_bug | 95 / 0 | 90 / 0 | 45 / 0 | 25 / 0 | 20 / 0 | 100 / 0 | 15 / 0 | 25 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 | 85 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 95 / 0 |

Best planner per family (reached / collision %): random => apf_escape/vfh_plus/astar_known/astar_unknown/informed_rrt_star/astar_mpc/dstar_lite (100 / 0); u_trap => astar_known/astar_unknown/informed_rrt_star/astar_mpc/astar_unknown_f2/dstar_lite (100 / 0); narrow_gap => astar_known/informed_rrt_star/astar_mpc (100 / 0); office => astar_known/informed_rrt_star/astar_mpc (100 / 0); warehouse => astar_known/informed_rrt_star/astar_mpc (100 / 0); forest => freest_beam/apf_escape/vfh_plus/astar_known/astar_unknown/informed_rrt_star/astar_mpc/bug2/tangent_bug/dstar_lite (100 / 0); maze => astar_known/informed_rrt_star/astar_mpc (100 / 0); glass_office => astar_known/informed_rrt_star/astar_mpc (100 / 0)

Best without a prior map (astar_known, informed_rrt_star, astar_mpc excluded): random => apf_escape/vfh_plus/astar_unknown/dstar_lite (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite (100 / 0); narrow_gap => astar_unknown (90 / 0); office => astar_unknown (95 / 0); warehouse => astar_unknown/dstar_lite (55 / 0); forest => freest_beam/apf_escape/vfh_plus/astar_unknown/bug2/tangent_bug/dstar_lite (100 / 0); maze => astar_unknown (95 / 0); glass_office => astar_unknown/dstar_lite (95 / 0)

### Preset `crazyflie`

Cell = reached % / collision % (20 layouts unless stated).

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| straight | 40 / 40 | 0 / 65 | 0 / 70 | 0 / 65 | 0 / 65 | 15 / 60 | 0 / 80 | 5 / 70 |
| freest_beam | 50 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 35 / 15 | 0 / 10 | 5 / 5 |
| apf_escape | 85 / 0 | 35 / 20 | 0 / 5 | 0 / 10 | 0 / 0 | 60 / 25 | 0 / 15 | 5 / 20 |
| vfh_plus | 45 / 55 | 0 / 100 | 5 / 95 | 5 / 90 | 0 / 95 | 35 / 65 | 0 / 100 | 0 / 90 |
| astar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown | 100 / 0 | 95 / 5 | 25 / 5 | 35 / 25 | 0 / 50 | 95 / 5 | 35 / 15 | 5 / 65 |
| informed_rrt_star | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_mpc | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown_f2 | 100 / 0 | 100 / 0 | 15 / 5 | 50 / 5 | 0 / 0 | 95 / 5 | 55 / 0 | 5 / 45 |
| dwa | 40 / 35 | 0 / 15 | 0 / 40 | 0 / 55 | 0 / 50 | 10 / 90 | 0 / 65 | 5 / 60 |
| dwa_mem | 55 / 5 | 0 / 0 | 5 / 0 | 5 / 0 | 0 / 20 | 45 / 15 | 0 / 15 | 5 / 5 |
| bug2 | 90 / 10 | 20 / 30 | 0 / 0 | 0 / 35 | 15 / 20 | 50 / 40 | 0 / 20 | 5 / 40 |
| tangent_bug | 55 / 45 | 35 / 15 | 5 / 10 | 10 / 45 | 0 / 35 | 25 / 75 | 0 / 50 | 5 / 50 |
| dstar_lite | 100 / 0 | 100 / 0 | 15 / 10 | 20 / 40 | 5 / 45 | 100 / 0 | 40 / 25 | 10 / 65 |

Best planner per family (reached / collision %): random => astar_known/astar_unknown/informed_rrt_star/astar_mpc/astar_unknown_f2/dstar_lite (100 / 0); u_trap => astar_known/informed_rrt_star/astar_mpc/astar_unknown_f2/dstar_lite (100 / 0); narrow_gap => astar_known/informed_rrt_star/astar_mpc (100 / 0); office => astar_known/informed_rrt_star/astar_mpc (100 / 0); warehouse => astar_known/informed_rrt_star/astar_mpc (100 / 0); forest => astar_known/informed_rrt_star/astar_mpc/dstar_lite (100 / 0); maze => astar_known/informed_rrt_star/astar_mpc (100 / 0); glass_office => astar_known/informed_rrt_star/astar_mpc (100 / 0)

Best without a prior map (astar_known, informed_rrt_star, astar_mpc excluded): random => astar_unknown/astar_unknown_f2/dstar_lite (100 / 0); u_trap => astar_unknown_f2/dstar_lite (100 / 0); narrow_gap => astar_unknown (25 / 5); office => astar_unknown_f2 (50 / 5); warehouse => bug2 (15 / 20); forest => dstar_lite (100 / 0); maze => astar_unknown_f2 (55 / 0); glass_office => dstar_lite (10 / 65)

### All fields

| preset | planner | family | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | collisions by material | sum of run wall s |
|---|---|---|---|---|---|---|---|---|---|---|
| ideal | straight | random | 40 | 0 | 60 | 0 | 16.94 | 0.383 | - | 1 |
| ideal | straight | u_trap | 0 | 0 | 100 | 0 | - | 0.383 | - | 1.2 |
| ideal | straight | narrow_gap | 0 | 0 | 100 | 0 | - | 0.37 | - | 1 |
| ideal | straight | office | 0 | 0 | 100 | 0 | - | 0.37 | - | 0.7 |
| ideal | straight | warehouse | 0 | 0 | 100 | 0 | - | 0.392 | - | 1 |
| ideal | straight | forest | 15 | 0 | 85 | 0 | 26.02 | 0.39 | - | 0.9 |
| ideal | straight | maze | 0 | 5 | 95 | 0 | - | 0.38 | matte 1 | 0.7 |
| ideal | straight | glass_office | 0 | 0 | 100 | 0 | - | 0.401 | - | 0.7 |
| ideal | freest_beam | random | 80 | 0 | 20 | 0 | 24.64 | 0.47 | - | 1.4 |
| ideal | freest_beam | u_trap | 0 | 0 | 100 | 0 | - | 0.434 | - | 1.3 |
| ideal | freest_beam | narrow_gap | 0 | 0 | 100 | 0 | - | 0.441 | - | 1.7 |
| ideal | freest_beam | office | 15 | 5 | 80 | 0 | 11.1 | 0.412 | matte 1 | 0.6 |
| ideal | freest_beam | warehouse | 15 | 0 | 85 | 0 | 37.72 | 0.343 | - | 1.9 |
| ideal | freest_beam | forest | 100 | 0 | 0 | 0 | 26.64 | 0.353 | - | 1.4 |
| ideal | freest_beam | maze | 0 | 0 | 100 | 0 | - | 0.398 | - | 1.4 |
| ideal | freest_beam | glass_office | 10 | 5 | 85 | 0 | 12.4 | 0.411 | matte 1 | 0.7 |
| ideal | apf_escape | random | 100 | 0 | 0 | 0 | 27.52 | 0.754 | - | 1.7 |
| ideal | apf_escape | u_trap | 90 | 0 | 5 | 5 | 43.03 | 0.658 | - | 2.7 |
| ideal | apf_escape | narrow_gap | 0 | 0 | 90 | 10 | - | 0.665 | - | 2.6 |
| ideal | apf_escape | office | 0 | 0 | 100 | 0 | - | 0.581 | - | 1.6 |
| ideal | apf_escape | warehouse | 0 | 0 | 100 | 0 | - | 0.565 | - | 1.8 |
| ideal | apf_escape | forest | 100 | 0 | 0 | 0 | 30.13 | 0.546 | - | 1.7 |
| ideal | apf_escape | maze | 10 | 0 | 90 | 0 | 93.67 | 0.572 | - | 4.6 |
| ideal | apf_escape | glass_office | 0 | 0 | 100 | 0 | - | 0.594 | - | 2 |
| ideal | vfh_plus | random | 100 | 0 | 0 | 0 | 25.59 | 0.288 | - | 1.8 |
| ideal | vfh_plus | u_trap | 0 | 0 | 95 | 5 | - | 0.954 | - | 2.2 |
| ideal | vfh_plus | narrow_gap | 50 | 0 | 50 | 0 | 27.58 | 0.288 | - | 2.3 |
| ideal | vfh_plus | office | 40 | 0 | 60 | 0 | 10.8 | 0.287 | - | 2.1 |
| ideal | vfh_plus | warehouse | 20 | 0 | 80 | 0 | 30.2 | 0.278 | - | 3.5 |
| ideal | vfh_plus | forest | 100 | 0 | 0 | 0 | 26.14 | 0.311 | - | 2 |
| ideal | vfh_plus | maze | 10 | 0 | 85 | 5 | 45.4 | 0.255 | - | 4.5 |
| ideal | vfh_plus | glass_office | 50 | 0 | 45 | 5 | 23.71 | 0.265 | - | 2.7 |
| ideal | astar_known | random | 100 | 0 | 0 | 0 | 18.46 | 0.633 | - | 7.1 |
| ideal | astar_known | u_trap | 100 | 0 | 0 | 0 | 19.24 | 0.617 | - | 8.1 |
| ideal | astar_known | narrow_gap | 100 | 0 | 0 | 0 | 24.48 | 0.277 | - | 21.2 |
| ideal | astar_known | office | 100 | 0 | 0 | 0 | 21.01 | 0.265 | - | 15.2 |
| ideal | astar_known | warehouse | 100 | 0 | 0 | 0 | 43.74 | 0.539 | - | 38 |
| ideal | astar_known | forest | 100 | 0 | 0 | 0 | 22.72 | 0.616 | - | 12.6 |
| ideal | astar_known | maze | 100 | 0 | 0 | 0 | 41.03 | 0.594 | - | 64.3 |
| ideal | astar_known | glass_office | 100 | 0 | 0 | 0 | 25.12 | 0.265 | - | 20.7 |
| ideal | astar_unknown | random | 100 | 0 | 0 | 0 | 19.01 | 0.615 | - | 41.9 |
| ideal | astar_unknown | u_trap | 100 | 0 | 0 | 0 | 22.12 | 0.597 | - | 57.9 |
| ideal | astar_unknown | narrow_gap | 90 | 0 | 5 | 5 | 37.51 | 0.254 | - | 120.5 |
| ideal | astar_unknown | office | 95 | 0 | 5 | 0 | 22.8 | 0.261 | - | 19.7 |
| ideal | astar_unknown | warehouse | 55 | 0 | 45 | 0 | 49.12 | 0.304 | - | 112.1 |
| ideal | astar_unknown | forest | 100 | 0 | 0 | 0 | 23.31 | 0.603 | - | 60.1 |
| ideal | astar_unknown | maze | 95 | 0 | 5 | 0 | 50.06 | 0.589 | - | 135.4 |
| ideal | astar_unknown | glass_office | 95 | 0 | 5 | 0 | 30.34 | 0.273 | - | 33.2 |
| ideal | informed_rrt_star | random | 100 | 0 | 0 | 0 | 23.92 | 0.288 | - | 17 |
| ideal | informed_rrt_star | u_trap | 100 | 0 | 0 | 0 | 23.36 | 0.257 | - | 12.8 |
| ideal | informed_rrt_star | narrow_gap | 100 | 0 | 0 | 0 | 28.13 | 0.256 | - | 12.3 |
| ideal | informed_rrt_star | office | 100 | 0 | 0 | 0 | 25.73 | 0.249 | - | 13.7 |
| ideal | informed_rrt_star | warehouse | 100 | 0 | 0 | 0 | 62.5 | 0.248 | - | 8.8 |
| ideal | informed_rrt_star | forest | 100 | 0 | 0 | 0 | 33.8 | 0.263 | - | 19.6 |
| ideal | informed_rrt_star | maze | 100 | 0 | 0 | 0 | 74.63 | 0.264 | - | 13.1 |
| ideal | informed_rrt_star | glass_office | 100 | 0 | 0 | 0 | 31.9 | 0.249 | - | 12.1 |
| ideal | astar_mpc | random | 100 | 0 | 0 | 0 | 18.03 | 0.632 | - | 11.3 |
| ideal | astar_mpc | u_trap | 100 | 0 | 0 | 0 | 18.65 | 0.62 | - | 13.5 |
| ideal | astar_mpc | narrow_gap | 100 | 0 | 0 | 0 | 22.02 | 0.338 | - | 21.2 |
| ideal | astar_mpc | office | 100 | 0 | 0 | 0 | 16.37 | 0.37 | - | 15.1 |
| ideal | astar_mpc | warehouse | 100 | 0 | 0 | 0 | 38.03 | 0.577 | - | 52.2 |
| ideal | astar_mpc | forest | 100 | 0 | 0 | 0 | 20.33 | 0.62 | - | 20.2 |
| ideal | astar_mpc | maze | 100 | 0 | 0 | 0 | 37.26 | 0.601 | - | 79.9 |
| ideal | astar_mpc | glass_office | 100 | 0 | 0 | 0 | 19.16 | 0.29 | - | 29.6 |
| ideal | astar_unknown_f2 | random | 75 | 0 | 25 | 0 | 17.76 | 0.891 | - | 59.7 |
| ideal | astar_unknown_f2 | u_trap | 100 | 0 | 0 | 0 | 22.93 | 0.827 | - | 75.9 |
| ideal | astar_unknown_f2 | narrow_gap | 0 | 0 | 100 | 0 | - | 0.889 | - | 115.8 |
| ideal | astar_unknown_f2 | office | 0 | 0 | 100 | 0 | - | 0.873 | - | 13.5 |
| ideal | astar_unknown_f2 | warehouse | 0 | 0 | 95 | 5 | - | 0.692 | - | 131.2 |
| ideal | astar_unknown_f2 | forest | 65 | 0 | 35 | 0 | 22.18 | 0.801 | - | 57.6 |
| ideal | astar_unknown_f2 | maze | 0 | 0 | 100 | 0 | - | 0.757 | - | 103.4 |
| ideal | astar_unknown_f2 | glass_office | 0 | 0 | 100 | 0 | - | 0.852 | - | 19.9 |
| ideal | dwa | random | 80 | 0 | 15 | 5 | 31.06 | 0.272 | - | 13.3 |
| ideal | dwa | u_trap | 0 | 0 | 100 | 0 | - | 0.289 | - | 15.6 |
| ideal | dwa | narrow_gap | 10 | 0 | 45 | 45 | 51.96 | 0.279 | - | 23.7 |
| ideal | dwa | office | 5 | 0 | 95 | 0 | 25.84 | 0.295 | - | 12.8 |
| ideal | dwa | warehouse | 10 | 0 | 90 | 0 | 66.74 | 0.256 | - | 36.9 |
| ideal | dwa | forest | 90 | 0 | 0 | 10 | 50.67 | 0.276 | - | 14.8 |
| ideal | dwa | maze | 0 | 0 | 100 | 0 | - | 0.26 | - | 31.2 |
| ideal | dwa | glass_office | 5 | 0 | 95 | 0 | 16.18 | 0.299 | - | 12.6 |
| ideal | dwa_mem | random | 75 | 0 | 15 | 10 | 27.68 | 0.264 | - | 58.1 |
| ideal | dwa_mem | u_trap | 0 | 0 | 100 | 0 | - | 0.292 | - | 42.4 |
| ideal | dwa_mem | narrow_gap | 10 | 0 | 80 | 10 | 52.86 | 0.289 | - | 64.7 |
| ideal | dwa_mem | office | 5 | 0 | 95 | 0 | 23.58 | 0.292 | - | 38.5 |
| ideal | dwa_mem | warehouse | 10 | 0 | 90 | 0 | 78.94 | 0.251 | - | 142.9 |
| ideal | dwa_mem | forest | 75 | 0 | 0 | 25 | 47 | 0.265 | - | 66.3 |
| ideal | dwa_mem | maze | 0 | 0 | 100 | 0 | - | 0.256 | - | 95.5 |
| ideal | dwa_mem | glass_office | 5 | 0 | 95 | 0 | 15.54 | 0.299 | - | 37.9 |
| ideal | bug2 | random | 90 | 0 | 0 | 10 | 27.48 | 0.53 | - | 1.7 |
| ideal | bug2 | u_trap | 90 | 0 | 5 | 5 | 42.71 | 0.481 | - | 2.4 |
| ideal | bug2 | narrow_gap | 0 | 0 | 0 | 100 | - | 0.481 | - | 3.6 |
| ideal | bug2 | office | 0 | 0 | 100 | 0 | - | 0.454 | - | 1.7 |
| ideal | bug2 | warehouse | 0 | 0 | 65 | 35 | - | 0.471 | - | 4.2 |
| ideal | bug2 | forest | 100 | 0 | 0 | 0 | 36.08 | 0.458 | - | 1.7 |
| ideal | bug2 | maze | 20 | 0 | 0 | 80 | 102.81 | 0.471 | - | 6.5 |
| ideal | bug2 | glass_office | 0 | 0 | 100 | 0 | - | 0.458 | - | 1.8 |
| ideal | tangent_bug | random | 95 | 0 | 5 | 0 | 24.6 | 0.435 | - | 1.5 |
| ideal | tangent_bug | u_trap | 90 | 0 | 10 | 0 | 29.82 | 0.422 | - | 1.9 |
| ideal | tangent_bug | narrow_gap | 45 | 0 | 45 | 10 | 27.34 | 0.378 | - | 1.8 |
| ideal | tangent_bug | office | 25 | 0 | 35 | 40 | 19.74 | 0.349 | - | 2.2 |
| ideal | tangent_bug | warehouse | 20 | 0 | 75 | 5 | 34.41 | 0.315 | - | 2.7 |
| ideal | tangent_bug | forest | 100 | 0 | 0 | 0 | 25.19 | 0.407 | - | 1.4 |
| ideal | tangent_bug | maze | 15 | 0 | 55 | 30 | 48.66 | 0.345 | - | 4.6 |
| ideal | tangent_bug | glass_office | 25 | 0 | 45 | 30 | 8.42 | 0.354 | - | 2.3 |
| ideal | dstar_lite | random | 100 | 0 | 0 | 0 | 18.78 | 0.616 | - | 11.9 |
| ideal | dstar_lite | u_trap | 100 | 0 | 0 | 0 | 22.12 | 0.598 | - | 14.3 |
| ideal | dstar_lite | narrow_gap | 85 | 0 | 5 | 10 | 39.72 | 0.262 | - | 31.8 |
| ideal | dstar_lite | office | 90 | 0 | 10 | 0 | 22.39 | 0.261 | - | 21.6 |
| ideal | dstar_lite | warehouse | 55 | 0 | 45 | 0 | 47.7 | 0.293 | - | 61.8 |
| ideal | dstar_lite | forest | 100 | 0 | 0 | 0 | 23.24 | 0.595 | - | 17.1 |
| ideal | dstar_lite | maze | 90 | 0 | 10 | 0 | 49.7 | 0.586 | - | 51.6 |
| ideal | dstar_lite | glass_office | 95 | 0 | 5 | 0 | 29.16 | 0.272 | - | 26.6 |
| crazyflie | straight | random | 40 | 40 | 20 | 0 | 16.69 | 0.254 | matte 8 | 1 |
| crazyflie | straight | u_trap | 0 | 65 | 35 | 0 | - | 0.15 | matte 13 | 1 |
| crazyflie | straight | narrow_gap | 0 | 70 | 30 | 0 | - | 0.149 | matte 14 | 0.8 |
| crazyflie | straight | office | 0 | 65 | 35 | 0 | - | 0.149 | matte 13 | 0.5 |
| crazyflie | straight | warehouse | 0 | 65 | 35 | 0 | - | 0.149 | matte 13 | 0.7 |
| crazyflie | straight | forest | 15 | 60 | 25 | 0 | 16.82 | 0.149 | matte 12 | 0.8 |
| crazyflie | straight | maze | 0 | 80 | 20 | 0 | - | 0.149 | matte 16 | 0.6 |
| crazyflie | straight | glass_office | 5 | 70 | 25 | 0 | 5.18 | 0.149 | matte 14 | 0.7 |
| crazyflie | freest_beam | random | 50 | 5 | 45 | 0 | 24.41 | 0.456 | matte 1 | 1.3 |
| crazyflie | freest_beam | u_trap | 0 | 0 | 100 | 0 | - | 0.598 | - | 1.2 |
| crazyflie | freest_beam | narrow_gap | 0 | 0 | 80 | 20 | - | 0.44 | - | 1.6 |
| crazyflie | freest_beam | office | 0 | 0 | 95 | 5 | - | 0.406 | - | 0.6 |
| crazyflie | freest_beam | warehouse | 0 | 0 | 95 | 5 | - | 0.384 | - | 1 |
| crazyflie | freest_beam | forest | 35 | 15 | 50 | 0 | 25.14 | 0.226 | matte 3 | 0.9 |
| crazyflie | freest_beam | maze | 0 | 10 | 90 | 0 | - | 0.355 | matte 2 | 0.7 |
| crazyflie | freest_beam | glass_office | 5 | 5 | 90 | 0 | 6.44 | 0.454 | matte 1 | 0.4 |
| crazyflie | apf_escape | random | 85 | 0 | 10 | 5 | 26.68 | 0.58 | - | 1.7 |
| crazyflie | apf_escape | u_trap | 35 | 20 | 40 | 5 | 43.1 | 0.237 | matte 4 | 2 |
| crazyflie | apf_escape | narrow_gap | 0 | 5 | 40 | 55 | - | 0.422 | matte 1 | 2.6 |
| crazyflie | apf_escape | office | 0 | 10 | 65 | 25 | - | 0.246 | matte 2 | 1.9 |
| crazyflie | apf_escape | warehouse | 0 | 0 | 100 | 0 | - | 0.439 | - | 1.4 |
| crazyflie | apf_escape | forest | 60 | 25 | 10 | 5 | 32.84 | 0.192 | matte 5 | 1.2 |
| crazyflie | apf_escape | maze | 0 | 15 | 80 | 5 | - | 0.341 | matte 3 | 2.8 |
| crazyflie | apf_escape | glass_office | 5 | 20 | 60 | 15 | 11.82 | 0.278 | glass 3, matte 1 | 1.4 |
| crazyflie | vfh_plus | random | 45 | 55 | 0 | 0 | 24.88 | 0.15 | matte 11 | 0.9 |
| crazyflie | vfh_plus | u_trap | 0 | 100 | 0 | 0 | - | 0.147 | matte 20 | 1 |
| crazyflie | vfh_plus | narrow_gap | 5 | 95 | 0 | 0 | 29.24 | 0.146 | matte 19 | 0.7 |
| crazyflie | vfh_plus | office | 5 | 90 | 0 | 5 | 9.02 | 0.146 | matte 18 | 0.4 |
| crazyflie | vfh_plus | warehouse | 0 | 95 | 5 | 0 | - | 0.147 | matte 19 | 0.5 |
| crazyflie | vfh_plus | forest | 35 | 65 | 0 | 0 | 25.16 | 0.145 | matte 13 | 1 |
| crazyflie | vfh_plus | maze | 0 | 100 | 0 | 0 | - | 0.147 | matte 20 | 0.3 |
| crazyflie | vfh_plus | glass_office | 0 | 90 | 10 | 0 | - | 0.147 | matte 18 | 0.4 |
| crazyflie | astar_known | random | 100 | 0 | 0 | 0 | 18.46 | 0.633 | - | 6.1 |
| crazyflie | astar_known | u_trap | 100 | 0 | 0 | 0 | 19.24 | 0.617 | - | 9.4 |
| crazyflie | astar_known | narrow_gap | 100 | 0 | 0 | 0 | 24.48 | 0.277 | - | 20.1 |
| crazyflie | astar_known | office | 100 | 0 | 0 | 0 | 21.01 | 0.265 | - | 12.8 |
| crazyflie | astar_known | warehouse | 100 | 0 | 0 | 0 | 43.74 | 0.539 | - | 37.1 |
| crazyflie | astar_known | forest | 100 | 0 | 0 | 0 | 22.72 | 0.616 | - | 11.9 |
| crazyflie | astar_known | maze | 100 | 0 | 0 | 0 | 41.03 | 0.594 | - | 64.2 |
| crazyflie | astar_known | glass_office | 100 | 0 | 0 | 0 | 25.12 | 0.265 | - | 19.2 |
| crazyflie | astar_unknown | random | 100 | 0 | 0 | 0 | 22.51 | 0.59 | - | 54.1 |
| crazyflie | astar_unknown | u_trap | 95 | 5 | 0 | 0 | 28.96 | 0.402 | matte 1 | 95.5 |
| crazyflie | astar_unknown | narrow_gap | 25 | 5 | 0 | 70 | 29.6 | 0.25 | matte 1 | 179.8 |
| crazyflie | astar_unknown | office | 35 | 25 | 35 | 5 | 18.84 | 0.225 | matte 5 | 20.4 |
| crazyflie | astar_unknown | warehouse | 0 | 50 | 40 | 10 | - | 0.155 | matte 10 | 198.6 |
| crazyflie | astar_unknown | forest | 95 | 5 | 0 | 0 | 25.28 | 0.508 | matte 1 | 64.3 |
| crazyflie | astar_unknown | maze | 35 | 15 | 35 | 15 | 91.6 | 0.242 | matte 3 | 243.5 |
| crazyflie | astar_unknown | glass_office | 5 | 65 | 30 | 0 | 56.96 | 0.149 | glass 7, matte 6 | 38.4 |
| crazyflie | informed_rrt_star | random | 100 | 0 | 0 | 0 | 23.92 | 0.288 | - | 16 |
| crazyflie | informed_rrt_star | u_trap | 100 | 0 | 0 | 0 | 23.36 | 0.257 | - | 11.5 |
| crazyflie | informed_rrt_star | narrow_gap | 100 | 0 | 0 | 0 | 28.13 | 0.256 | - | 11.5 |
| crazyflie | informed_rrt_star | office | 100 | 0 | 0 | 0 | 25.73 | 0.249 | - | 13.4 |
| crazyflie | informed_rrt_star | warehouse | 100 | 0 | 0 | 0 | 62.5 | 0.248 | - | 9.4 |
| crazyflie | informed_rrt_star | forest | 100 | 0 | 0 | 0 | 33.8 | 0.263 | - | 19 |
| crazyflie | informed_rrt_star | maze | 100 | 0 | 0 | 0 | 74.63 | 0.264 | - | 11.8 |
| crazyflie | informed_rrt_star | glass_office | 100 | 0 | 0 | 0 | 31.9 | 0.249 | - | 14.8 |
| crazyflie | astar_mpc | random | 100 | 0 | 0 | 0 | 18.03 | 0.632 | - | 13.4 |
| crazyflie | astar_mpc | u_trap | 100 | 0 | 0 | 0 | 18.65 | 0.62 | - | 13.2 |
| crazyflie | astar_mpc | narrow_gap | 100 | 0 | 0 | 0 | 22.02 | 0.338 | - | 21.4 |
| crazyflie | astar_mpc | office | 100 | 0 | 0 | 0 | 16.37 | 0.37 | - | 16.4 |
| crazyflie | astar_mpc | warehouse | 100 | 0 | 0 | 0 | 38.03 | 0.577 | - | 53.2 |
| crazyflie | astar_mpc | forest | 100 | 0 | 0 | 0 | 20.33 | 0.62 | - | 18.5 |
| crazyflie | astar_mpc | maze | 100 | 0 | 0 | 0 | 37.26 | 0.601 | - | 79.5 |
| crazyflie | astar_mpc | glass_office | 100 | 0 | 0 | 0 | 19.16 | 0.29 | - | 26.5 |
| crazyflie | astar_unknown_f2 | random | 100 | 0 | 0 | 0 | 21.71 | 0.649 | - | 68.6 |
| crazyflie | astar_unknown_f2 | u_trap | 100 | 0 | 0 | 0 | 28.98 | 0.426 | - | 103.6 |
| crazyflie | astar_unknown_f2 | narrow_gap | 15 | 5 | 10 | 70 | 29.3 | 0.582 | matte 1 | 206.2 |
| crazyflie | astar_unknown_f2 | office | 50 | 5 | 45 | 0 | 22.67 | 0.283 | matte 1 | 27.6 |
| crazyflie | astar_unknown_f2 | warehouse | 0 | 0 | 100 | 0 | - | 0.335 | - | 202.7 |
| crazyflie | astar_unknown_f2 | forest | 95 | 5 | 0 | 0 | 25.56 | 0.491 | matte 1 | 63.6 |
| crazyflie | astar_unknown_f2 | maze | 55 | 0 | 35 | 10 | 84.46 | 0.4 | - | 257.8 |
| crazyflie | astar_unknown_f2 | glass_office | 5 | 45 | 45 | 5 | 52.46 | 0.179 | glass 9 | 30.9 |
| crazyflie | dwa | random | 40 | 35 | 25 | 0 | 25.69 | 0.166 | matte 7 | 3.8 |
| crazyflie | dwa | u_trap | 0 | 15 | 85 | 0 | - | 0.22 | matte 3 | 3.8 |
| crazyflie | dwa | narrow_gap | 0 | 40 | 55 | 5 | - | 0.154 | matte 8 | 4.9 |
| crazyflie | dwa | office | 0 | 55 | 45 | 0 | - | 0.15 | matte 11 | 1.9 |
| crazyflie | dwa | warehouse | 0 | 50 | 50 | 0 | - | 0.151 | matte 10 | 2.4 |
| crazyflie | dwa | forest | 10 | 90 | 0 | 0 | 27.91 | 0.148 | matte 18 | 2.2 |
| crazyflie | dwa | maze | 0 | 65 | 35 | 0 | - | 0.149 | matte 13 | 2.8 |
| crazyflie | dwa | glass_office | 5 | 60 | 35 | 0 | 11.98 | 0.15 | matte 12 | 1.9 |
| crazyflie | dwa_mem | random | 55 | 5 | 40 | 0 | 26.28 | 0.273 | matte 1 | 8.7 |
| crazyflie | dwa_mem | u_trap | 0 | 0 | 100 | 0 | - | 0.262 | - | 8.8 |
| crazyflie | dwa_mem | narrow_gap | 5 | 0 | 15 | 80 | 46.54 | 0.24 | - | 15.8 |
| crazyflie | dwa_mem | office | 5 | 0 | 95 | 0 | 17.16 | 0.272 | - | 8.6 |
| crazyflie | dwa_mem | warehouse | 0 | 20 | 75 | 5 | - | 0.207 | matte 4 | 23 |
| crazyflie | dwa_mem | forest | 45 | 15 | 20 | 20 | 41.74 | 0.223 | matte 3 | 10.7 |
| crazyflie | dwa_mem | maze | 0 | 15 | 80 | 5 | - | 0.23 | matte 3 | 22.7 |
| crazyflie | dwa_mem | glass_office | 5 | 5 | 90 | 0 | 17.98 | 0.255 | matte 1 | 7.6 |
| crazyflie | bug2 | random | 90 | 10 | 0 | 0 | 27.86 | 0.402 | matte 2 | 1.2 |
| crazyflie | bug2 | u_trap | 20 | 30 | 0 | 50 | 45.16 | 0.206 | matte 6 | 2.2 |
| crazyflie | bug2 | narrow_gap | 0 | 0 | 0 | 100 | - | 0.34 | - | 3.1 |
| crazyflie | bug2 | office | 0 | 35 | 50 | 15 | - | 0.21 | matte 7 | 1.1 |
| crazyflie | bug2 | warehouse | 15 | 20 | 60 | 5 | 77.84 | 0.229 | matte 4 | 2 |
| crazyflie | bug2 | forest | 50 | 40 | 5 | 5 | 30.03 | 0.194 | matte 8 | 1.6 |
| crazyflie | bug2 | maze | 0 | 20 | 80 | 0 | - | 0.335 | matte 4 | 1.5 |
| crazyflie | bug2 | glass_office | 5 | 40 | 55 | 0 | 6.2 | 0.2 | glass 1, matte 7 | 0.8 |
| crazyflie | tangent_bug | random | 55 | 45 | 0 | 0 | 24.44 | 0.216 | matte 9 | 1.1 |
| crazyflie | tangent_bug | u_trap | 35 | 15 | 10 | 40 | 31.66 | 0.302 | matte 3 | 2.2 |
| crazyflie | tangent_bug | narrow_gap | 5 | 10 | 25 | 60 | 26.9 | 0.234 | matte 2 | 2.4 |
| crazyflie | tangent_bug | office | 10 | 45 | 35 | 10 | 12.4 | 0.154 | matte 9 | 1 |
| crazyflie | tangent_bug | warehouse | 0 | 35 | 55 | 10 | - | 0.203 | matte 7 | 1.2 |
| crazyflie | tangent_bug | forest | 25 | 75 | 0 | 0 | 24.36 | 0.149 | matte 15 | 0.6 |
| crazyflie | tangent_bug | maze | 0 | 50 | 45 | 5 | - | 0.151 | matte 10 | 1.6 |
| crazyflie | tangent_bug | glass_office | 5 | 50 | 35 | 10 | 17.36 | 0.153 | glass 1, matte 9 | 1.1 |
| crazyflie | dstar_lite | random | 100 | 0 | 0 | 0 | 21.41 | 0.576 | - | 10.1 |
| crazyflie | dstar_lite | u_trap | 100 | 0 | 0 | 0 | 29.73 | 0.407 | - | 15.1 |
| crazyflie | dstar_lite | narrow_gap | 15 | 10 | 0 | 75 | 26.92 | 0.266 | matte 2 | 32.8 |
| crazyflie | dstar_lite | office | 20 | 40 | 40 | 0 | 24.85 | 0.158 | matte 8 | 16.4 |
| crazyflie | dstar_lite | warehouse | 5 | 45 | 50 | 0 | 105.68 | 0.17 | matte 9 | 45.5 |
| crazyflie | dstar_lite | forest | 100 | 0 | 0 | 0 | 24.58 | 0.493 | - | 10.9 |
| crazyflie | dstar_lite | maze | 40 | 25 | 30 | 5 | 83.36 | 0.234 | matte 5 | 46.2 |
| crazyflie | dstar_lite | glass_office | 10 | 65 | 25 | 0 | 36.03 | 0.15 | glass 7, matte 6 | 17.2 |
