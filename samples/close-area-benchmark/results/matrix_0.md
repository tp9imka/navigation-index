`python bench.py --layouts 20 --seed 0 --workers 10 --parity --stem matrix_0_regen` from samples/close-area-benchmark. Input: synthetic (simulated layouts, vehicle and sensors). Scored on truth. Seed 0, 20 layouts per cell, 10 worker processes, wall 2963.7 s. Run time limit per family (s): random 60, u_trap 60, narrow_gap 60, office 60, warehouse 120, forest 60, maze 120, glass_office 60.

Regenerated 2026-11-12 with SKIP_DROPPED_BEAMS = True in close-area-arena/planners/astar_esdf.py (a beam the sensor flags dropped adds nothing to the map; docs/upstream-findings.md section 22). Written as matrix_0_regen and renamed to matrix_0; every other input matches the previous run of this file.

Parity with run.evaluate (ideal x random, runs with identical outcome and min clearance): straight 10/10, astar_known 10/10

### Preset `ideal`

Cell = reached % / collision % (20 layouts unless stated).

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| straight | 40 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 15 / 0 | 0 / 5 | 0 / 0 |
| freest_beam | 80 / 0 | 0 / 0 | 0 / 0 | 15 / 5 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 5 |
| apf_escape | 100 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 10 / 0 | 0 / 0 |
| vfh_plus | 100 / 0 | 0 / 0 | 50 / 0 | 40 / 0 | 20 / 0 | 100 / 0 | 10 / 0 | 50 / 0 |
| astar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown | 100 / 0 | 100 / 0 | 80 / 0 | 90 / 0 | 50 / 0 | 100 / 0 | 90 / 0 | 90 / 0 |
| informed_rrt_star | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_mpc | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown_f2 | 80 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 65 / 0 | 0 / 0 | 0 / 0 |
| dwa | 80 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 90 / 0 | 0 / 0 | 5 / 0 |
| dwa_mem | 75 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 75 / 0 | 0 / 0 | 5 / 0 |
| bug2 | 90 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 20 / 0 | 0 / 0 |
| tangent_bug | 95 / 0 | 90 / 0 | 45 / 0 | 25 / 0 | 20 / 0 | 100 / 0 | 15 / 0 | 25 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 | 85 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 90 / 0 |
| thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| thetastar_unknown | 100 / 0 | 100 / 0 | 80 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 95 / 0 |
| lazy_thetastar_unknown | 100 / 0 | 100 / 0 | 100 / 0 | 85 / 0 | 55 / 0 | 100 / 0 | 85 / 0 | 90 / 0 |
| mppi | 90 / 0 | 0 / 0 | 25 / 0 | 25 / 0 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 0 |
| mppi_astar | 100 / 0 | 100 / 0 | 95 / 0 | 95 / 0 | 55 / 0 | 100 / 0 | 95 / 0 | 95 / 0 |
| hybrid_astar | 100 / 0 | 100 / 0 | 85 / 0 | 90 / 0 | 50 / 0 | 100 / 0 | 90 / 0 | 85 / 0 |

Best planner per family (reached / collision %): random => apf_escape/vfh_plus/astar_known/astar_unknown/informed_rrt_star/astar_mpc/dstar_lite/thetastar_known/lazy_thetastar_known/thetastar_unknown/lazy_thetastar_unknown/mppi_astar/hybrid_astar (100 / 0); u_trap => astar_known/astar_unknown/informed_rrt_star/astar_mpc/astar_unknown_f2/dstar_lite/thetastar_known/lazy_thetastar_known/thetastar_unknown/lazy_thetastar_unknown/mppi_astar/hybrid_astar (100 / 0); narrow_gap => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known/lazy_thetastar_unknown (100 / 0); office => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0); warehouse => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0); forest => freest_beam/apf_escape/vfh_plus/astar_known/astar_unknown/informed_rrt_star/astar_mpc/bug2/tangent_bug/dstar_lite/thetastar_known/lazy_thetastar_known/thetastar_unknown/lazy_thetastar_unknown/mppi/mppi_astar/hybrid_astar (100 / 0); maze => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0); glass_office => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0)

Best without a prior map (astar_known, informed_rrt_star, astar_mpc, thetastar_known, lazy_thetastar_known excluded): random => apf_escape/vfh_plus/astar_unknown/dstar_lite/thetastar_unknown/lazy_thetastar_unknown/mppi_astar/hybrid_astar (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/thetastar_unknown/lazy_thetastar_unknown/mppi_astar/hybrid_astar (100 / 0); narrow_gap => lazy_thetastar_unknown (100 / 0); office => mppi_astar (95 / 0); warehouse => dstar_lite/thetastar_unknown/lazy_thetastar_unknown/mppi_astar (55 / 0); forest => freest_beam/apf_escape/vfh_plus/astar_unknown/bug2/tangent_bug/dstar_lite/thetastar_unknown/lazy_thetastar_unknown/mppi/mppi_astar/hybrid_astar (100 / 0); maze => mppi_astar (95 / 0); glass_office => thetastar_unknown/mppi_astar (95 / 0)

### Preset `crazyflie`

Cell = reached % / collision % (20 layouts unless stated).

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| straight | 40 / 40 | 0 / 65 | 0 / 70 | 0 / 65 | 0 / 65 | 15 / 60 | 0 / 80 | 5 / 70 |
| freest_beam | 50 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 35 / 15 | 0 / 10 | 5 / 5 |
| apf_escape | 85 / 0 | 35 / 20 | 0 / 5 | 0 / 10 | 0 / 0 | 60 / 25 | 0 / 15 | 5 / 20 |
| vfh_plus | 45 / 55 | 0 / 100 | 5 / 95 | 5 / 90 | 0 / 95 | 35 / 65 | 0 / 100 | 0 / 90 |
| astar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown | 100 / 0 | 100 / 0 | 20 / 5 | 30 / 35 | 5 / 55 | 100 / 0 | 45 / 0 | 15 / 60 |
| informed_rrt_star | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_mpc | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown_f2 | 100 / 0 | 100 / 0 | 15 / 0 | 40 / 5 | 30 / 0 | 100 / 0 | 50 / 0 | 5 / 65 |
| dwa | 40 / 35 | 0 / 15 | 0 / 40 | 0 / 55 | 0 / 50 | 10 / 90 | 0 / 65 | 5 / 60 |
| dwa_mem | 55 / 5 | 0 / 0 | 5 / 0 | 5 / 0 | 0 / 20 | 45 / 15 | 0 / 15 | 5 / 5 |
| bug2 | 90 / 10 | 20 / 30 | 0 / 0 | 0 / 35 | 15 / 20 | 50 / 40 | 0 / 20 | 5 / 40 |
| tangent_bug | 55 / 45 | 35 / 15 | 5 / 10 | 10 / 45 | 0 / 35 | 25 / 75 | 0 / 50 | 5 / 50 |
| dstar_lite | 100 / 0 | 100 / 0 | 20 / 0 | 35 / 25 | 10 / 55 | 95 / 5 | 55 / 0 | 15 / 60 |
| thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| thetastar_unknown | 95 / 5 | 100 / 0 | 10 / 25 | 35 / 40 | 20 / 40 | 95 / 5 | 50 / 5 | 20 / 65 |
| lazy_thetastar_unknown | 100 / 0 | 100 / 0 | 20 / 10 | 35 / 45 | 15 / 25 | 95 / 5 | 40 / 5 | 15 / 65 |
| mppi | 60 / 35 | 0 / 95 | 5 / 95 | 10 / 80 | 0 / 100 | 100 / 0 | 0 / 95 | 10 / 70 |
| mppi_astar | 80 / 20 | 80 / 20 | 10 / 90 | 15 / 80 | 0 / 100 | 100 / 0 | 5 / 95 | 5 / 80 |
| hybrid_astar | 100 / 0 | 95 / 5 | 0 / 0 | 25 / 35 | 0 / 20 | 95 / 5 | 40 / 5 | 5 / 70 |

Best planner per family (reached / collision %): random => astar_known/astar_unknown/informed_rrt_star/astar_mpc/astar_unknown_f2/dstar_lite/thetastar_known/lazy_thetastar_known/lazy_thetastar_unknown/hybrid_astar (100 / 0); u_trap => astar_known/astar_unknown/informed_rrt_star/astar_mpc/astar_unknown_f2/dstar_lite/thetastar_known/lazy_thetastar_known/thetastar_unknown/lazy_thetastar_unknown (100 / 0); narrow_gap => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0); office => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0); warehouse => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0); forest => astar_known/astar_unknown/informed_rrt_star/astar_mpc/astar_unknown_f2/thetastar_known/lazy_thetastar_known/mppi/mppi_astar (100 / 0); maze => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0); glass_office => astar_known/informed_rrt_star/astar_mpc/thetastar_known/lazy_thetastar_known (100 / 0)

Best without a prior map (astar_known, informed_rrt_star, astar_mpc, thetastar_known, lazy_thetastar_known excluded): random => astar_unknown/astar_unknown_f2/dstar_lite/lazy_thetastar_unknown/hybrid_astar (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/thetastar_unknown/lazy_thetastar_unknown (100 / 0); narrow_gap => dstar_lite (20 / 0); office => astar_unknown_f2 (40 / 5); warehouse => astar_unknown_f2 (30 / 0); forest => astar_unknown/astar_unknown_f2/mppi/mppi_astar (100 / 0); maze => dstar_lite (55 / 0); glass_office => thetastar_unknown (20 / 65)

### All fields

| preset | planner | family | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | collisions by material | sum of run wall s |
|---|---|---|---|---|---|---|---|---|---|---|
| ideal | straight | random | 40 | 0 | 60 | 0 | 16.94 | 0.383 | - | 0.8 |
| ideal | straight | u_trap | 0 | 0 | 100 | 0 | - | 0.383 | - | 0.8 |
| ideal | straight | narrow_gap | 0 | 0 | 100 | 0 | - | 0.37 | - | 0.8 |
| ideal | straight | office | 0 | 0 | 100 | 0 | - | 0.37 | - | 0.6 |
| ideal | straight | warehouse | 0 | 0 | 100 | 0 | - | 0.392 | - | 0.4 |
| ideal | straight | forest | 15 | 0 | 85 | 0 | 26.02 | 0.39 | - | 0.7 |
| ideal | straight | maze | 0 | 5 | 95 | 0 | - | 0.38 | matte 1 | 0.6 |
| ideal | straight | glass_office | 0 | 0 | 100 | 0 | - | 0.401 | - | 0.6 |
| ideal | freest_beam | random | 80 | 0 | 20 | 0 | 24.64 | 0.47 | - | 1.1 |
| ideal | freest_beam | u_trap | 0 | 0 | 100 | 0 | - | 0.434 | - | 1 |
| ideal | freest_beam | narrow_gap | 0 | 0 | 100 | 0 | - | 0.441 | - | 1.4 |
| ideal | freest_beam | office | 15 | 5 | 80 | 0 | 11.1 | 0.412 | matte 1 | 0.5 |
| ideal | freest_beam | warehouse | 15 | 0 | 85 | 0 | 37.72 | 0.343 | - | 1.5 |
| ideal | freest_beam | forest | 100 | 0 | 0 | 0 | 26.64 | 0.353 | - | 1 |
| ideal | freest_beam | maze | 0 | 0 | 100 | 0 | - | 0.398 | - | 1 |
| ideal | freest_beam | glass_office | 10 | 5 | 85 | 0 | 12.4 | 0.411 | matte 1 | 0.5 |
| ideal | apf_escape | random | 100 | 0 | 0 | 0 | 27.52 | 0.754 | - | 1.2 |
| ideal | apf_escape | u_trap | 90 | 0 | 5 | 5 | 43.03 | 0.658 | - | 2 |
| ideal | apf_escape | narrow_gap | 0 | 0 | 90 | 10 | - | 0.665 | - | 2.1 |
| ideal | apf_escape | office | 0 | 0 | 100 | 0 | - | 0.581 | - | 1.4 |
| ideal | apf_escape | warehouse | 0 | 0 | 100 | 0 | - | 0.565 | - | 1.2 |
| ideal | apf_escape | forest | 100 | 0 | 0 | 0 | 30.13 | 0.546 | - | 1.2 |
| ideal | apf_escape | maze | 10 | 0 | 90 | 0 | 93.67 | 0.572 | - | 2.6 |
| ideal | apf_escape | glass_office | 0 | 0 | 100 | 0 | - | 0.594 | - | 1.5 |
| ideal | vfh_plus | random | 100 | 0 | 0 | 0 | 25.59 | 0.288 | - | 1.6 |
| ideal | vfh_plus | u_trap | 0 | 0 | 95 | 5 | - | 0.954 | - | 1.6 |
| ideal | vfh_plus | narrow_gap | 50 | 0 | 50 | 0 | 27.58 | 0.288 | - | 1.6 |
| ideal | vfh_plus | office | 40 | 0 | 60 | 0 | 10.8 | 0.287 | - | 1.4 |
| ideal | vfh_plus | warehouse | 20 | 0 | 80 | 0 | 30.2 | 0.278 | - | 2.6 |
| ideal | vfh_plus | forest | 100 | 0 | 0 | 0 | 26.14 | 0.311 | - | 1.3 |
| ideal | vfh_plus | maze | 10 | 0 | 85 | 5 | 45.4 | 0.255 | - | 3 |
| ideal | vfh_plus | glass_office | 50 | 0 | 45 | 5 | 23.71 | 0.265 | - | 1.8 |
| ideal | astar_known | random | 100 | 0 | 0 | 0 | 18.46 | 0.633 | - | 4.4 |
| ideal | astar_known | u_trap | 100 | 0 | 0 | 0 | 19.24 | 0.617 | - | 5.8 |
| ideal | astar_known | narrow_gap | 100 | 0 | 0 | 0 | 24.48 | 0.277 | - | 12.5 |
| ideal | astar_known | office | 100 | 0 | 0 | 0 | 21.01 | 0.265 | - | 8.7 |
| ideal | astar_known | warehouse | 100 | 0 | 0 | 0 | 43.74 | 0.539 | - | 27.9 |
| ideal | astar_known | forest | 100 | 0 | 0 | 0 | 22.72 | 0.616 | - | 8.7 |
| ideal | astar_known | maze | 100 | 0 | 0 | 0 | 41.03 | 0.594 | - | 46 |
| ideal | astar_known | glass_office | 100 | 0 | 0 | 0 | 25.12 | 0.265 | - | 15.7 |
| ideal | astar_unknown | random | 100 | 0 | 0 | 0 | 18.93 | 0.636 | - | 31.2 |
| ideal | astar_unknown | u_trap | 100 | 0 | 0 | 0 | 21.88 | 0.589 | - | 42.9 |
| ideal | astar_unknown | narrow_gap | 80 | 0 | 20 | 0 | 35.09 | 0.271 | - | 76.1 |
| ideal | astar_unknown | office | 90 | 0 | 10 | 0 | 22.46 | 0.259 | - | 12.5 |
| ideal | astar_unknown | warehouse | 50 | 0 | 50 | 0 | 44.92 | 0.313 | - | 71.2 |
| ideal | astar_unknown | forest | 100 | 0 | 0 | 0 | 23.29 | 0.602 | - | 41.3 |
| ideal | astar_unknown | maze | 90 | 0 | 10 | 0 | 48.55 | 0.59 | - | 96.8 |
| ideal | astar_unknown | glass_office | 90 | 0 | 10 | 0 | 30.58 | 0.266 | - | 21.9 |
| ideal | informed_rrt_star | random | 100 | 0 | 0 | 0 | 23.92 | 0.288 | - | 12.4 |
| ideal | informed_rrt_star | u_trap | 100 | 0 | 0 | 0 | 23.36 | 0.257 | - | 8.9 |
| ideal | informed_rrt_star | narrow_gap | 100 | 0 | 0 | 0 | 28.13 | 0.256 | - | 8.8 |
| ideal | informed_rrt_star | office | 100 | 0 | 0 | 0 | 25.73 | 0.249 | - | 10.3 |
| ideal | informed_rrt_star | warehouse | 100 | 0 | 0 | 0 | 62.5 | 0.248 | - | 6.1 |
| ideal | informed_rrt_star | forest | 100 | 0 | 0 | 0 | 33.8 | 0.263 | - | 14.3 |
| ideal | informed_rrt_star | maze | 100 | 0 | 0 | 0 | 74.63 | 0.264 | - | 8.5 |
| ideal | informed_rrt_star | glass_office | 100 | 0 | 0 | 0 | 31.9 | 0.249 | - | 8.4 |
| ideal | astar_mpc | random | 100 | 0 | 0 | 0 | 18.03 | 0.632 | - | 8.1 |
| ideal | astar_mpc | u_trap | 100 | 0 | 0 | 0 | 18.65 | 0.62 | - | 9.6 |
| ideal | astar_mpc | narrow_gap | 100 | 0 | 0 | 0 | 22.02 | 0.338 | - | 15.6 |
| ideal | astar_mpc | office | 100 | 0 | 0 | 0 | 16.37 | 0.37 | - | 11.8 |
| ideal | astar_mpc | warehouse | 100 | 0 | 0 | 0 | 38.03 | 0.577 | - | 34.6 |
| ideal | astar_mpc | forest | 100 | 0 | 0 | 0 | 20.33 | 0.62 | - | 13.2 |
| ideal | astar_mpc | maze | 100 | 0 | 0 | 0 | 37.26 | 0.601 | - | 53.1 |
| ideal | astar_mpc | glass_office | 100 | 0 | 0 | 0 | 19.16 | 0.29 | - | 18.5 |
| ideal | astar_unknown_f2 | random | 80 | 0 | 20 | 0 | 18.27 | 0.867 | - | 34.4 |
| ideal | astar_unknown_f2 | u_trap | 100 | 0 | 0 | 0 | 22.46 | 0.827 | - | 45.5 |
| ideal | astar_unknown_f2 | narrow_gap | 0 | 0 | 100 | 0 | - | 0.889 | - | 84.5 |
| ideal | astar_unknown_f2 | office | 0 | 0 | 100 | 0 | - | 0.875 | - | 9.7 |
| ideal | astar_unknown_f2 | warehouse | 0 | 0 | 90 | 10 | - | 0.702 | - | 112.3 |
| ideal | astar_unknown_f2 | forest | 65 | 0 | 35 | 0 | 22.28 | 0.797 | - | 44.9 |
| ideal | astar_unknown_f2 | maze | 0 | 0 | 100 | 0 | - | 0.752 | - | 64.7 |
| ideal | astar_unknown_f2 | glass_office | 0 | 0 | 100 | 0 | - | 0.853 | - | 13.3 |
| ideal | dwa | random | 80 | 0 | 15 | 5 | 31.06 | 0.272 | - | 10.9 |
| ideal | dwa | u_trap | 0 | 0 | 100 | 0 | - | 0.289 | - | 11.5 |
| ideal | dwa | narrow_gap | 10 | 0 | 45 | 45 | 51.96 | 0.279 | - | 16.9 |
| ideal | dwa | office | 5 | 0 | 95 | 0 | 25.84 | 0.295 | - | 10.5 |
| ideal | dwa | warehouse | 10 | 0 | 90 | 0 | 66.74 | 0.256 | - | 27.6 |
| ideal | dwa | forest | 90 | 0 | 0 | 10 | 50.67 | 0.276 | - | 12.8 |
| ideal | dwa | maze | 0 | 0 | 100 | 0 | - | 0.26 | - | 23 |
| ideal | dwa | glass_office | 5 | 0 | 95 | 0 | 16.18 | 0.299 | - | 10.3 |
| ideal | dwa_mem | random | 75 | 0 | 15 | 10 | 27.68 | 0.264 | - | 45.3 |
| ideal | dwa_mem | u_trap | 0 | 0 | 100 | 0 | - | 0.292 | - | 35.6 |
| ideal | dwa_mem | narrow_gap | 10 | 0 | 80 | 10 | 52.86 | 0.289 | - | 54 |
| ideal | dwa_mem | office | 5 | 0 | 95 | 0 | 23.58 | 0.292 | - | 31.1 |
| ideal | dwa_mem | warehouse | 10 | 0 | 90 | 0 | 78.94 | 0.251 | - | 112.8 |
| ideal | dwa_mem | forest | 75 | 0 | 0 | 25 | 47 | 0.265 | - | 53.2 |
| ideal | dwa_mem | maze | 0 | 0 | 100 | 0 | - | 0.256 | - | 81 |
| ideal | dwa_mem | glass_office | 5 | 0 | 95 | 0 | 15.54 | 0.299 | - | 32 |
| ideal | bug2 | random | 90 | 0 | 0 | 10 | 27.48 | 0.53 | - | 1.6 |
| ideal | bug2 | u_trap | 90 | 0 | 5 | 5 | 42.71 | 0.481 | - | 2.1 |
| ideal | bug2 | narrow_gap | 0 | 0 | 0 | 100 | - | 0.481 | - | 2.9 |
| ideal | bug2 | office | 0 | 0 | 100 | 0 | - | 0.454 | - | 1.3 |
| ideal | bug2 | warehouse | 0 | 0 | 65 | 35 | - | 0.471 | - | 3.2 |
| ideal | bug2 | forest | 100 | 0 | 0 | 0 | 36.08 | 0.458 | - | 1.4 |
| ideal | bug2 | maze | 20 | 0 | 0 | 80 | 102.81 | 0.471 | - | 5.3 |
| ideal | bug2 | glass_office | 0 | 0 | 100 | 0 | - | 0.458 | - | 1.2 |
| ideal | tangent_bug | random | 95 | 0 | 5 | 0 | 24.6 | 0.435 | - | 1.3 |
| ideal | tangent_bug | u_trap | 90 | 0 | 10 | 0 | 29.82 | 0.422 | - | 1.5 |
| ideal | tangent_bug | narrow_gap | 45 | 0 | 45 | 10 | 27.34 | 0.378 | - | 1.4 |
| ideal | tangent_bug | office | 25 | 0 | 35 | 40 | 19.74 | 0.349 | - | 1.8 |
| ideal | tangent_bug | warehouse | 20 | 0 | 75 | 5 | 34.41 | 0.315 | - | 2.2 |
| ideal | tangent_bug | forest | 100 | 0 | 0 | 0 | 25.19 | 0.407 | - | 1 |
| ideal | tangent_bug | maze | 15 | 0 | 55 | 30 | 48.66 | 0.345 | - | 3.6 |
| ideal | tangent_bug | glass_office | 25 | 0 | 45 | 30 | 8.42 | 0.354 | - | 1.7 |
| ideal | dstar_lite | random | 100 | 0 | 0 | 0 | 18.78 | 0.617 | - | 9.3 |
| ideal | dstar_lite | u_trap | 100 | 0 | 0 | 0 | 21.79 | 0.598 | - | 11.2 |
| ideal | dstar_lite | narrow_gap | 85 | 0 | 10 | 5 | 33.9 | 0.263 | - | 21 |
| ideal | dstar_lite | office | 90 | 0 | 10 | 0 | 22.48 | 0.258 | - | 13.5 |
| ideal | dstar_lite | warehouse | 55 | 0 | 45 | 0 | 44.92 | 0.304 | - | 41.1 |
| ideal | dstar_lite | forest | 100 | 0 | 0 | 0 | 23.24 | 0.597 | - | 13.5 |
| ideal | dstar_lite | maze | 90 | 0 | 10 | 0 | 48.75 | 0.587 | - | 33.2 |
| ideal | dstar_lite | glass_office | 90 | 0 | 10 | 0 | 30.61 | 0.267 | - | 21.4 |
| ideal | thetastar_known | random | 100 | 0 | 0 | 0 | 17.09 | 0.943 | - | 21.8 |
| ideal | thetastar_known | u_trap | 100 | 0 | 0 | 0 | 17.66 | 0.931 | - | 31.7 |
| ideal | thetastar_known | narrow_gap | 100 | 0 | 0 | 0 | 22.36 | 0.34 | - | 74 |
| ideal | thetastar_known | office | 100 | 0 | 0 | 0 | 18.05 | 0.283 | - | 36.2 |
| ideal | thetastar_known | warehouse | 100 | 0 | 0 | 0 | 27.46 | 0.603 | - | 80.4 |
| ideal | thetastar_known | forest | 100 | 0 | 0 | 0 | 18.12 | 0.891 | - | 29.3 |
| ideal | thetastar_known | maze | 100 | 0 | 0 | 0 | 30.07 | 0.797 | - | 93.6 |
| ideal | thetastar_known | glass_office | 100 | 0 | 0 | 0 | 21.17 | 0.266 | - | 70.2 |
| ideal | lazy_thetastar_known | random | 100 | 0 | 0 | 0 | 17.11 | 0.933 | - | 17.6 |
| ideal | lazy_thetastar_known | u_trap | 100 | 0 | 0 | 0 | 17.68 | 0.921 | - | 20 |
| ideal | lazy_thetastar_known | narrow_gap | 100 | 0 | 0 | 0 | 22.36 | 0.347 | - | 53.3 |
| ideal | lazy_thetastar_known | office | 100 | 0 | 0 | 0 | 18.03 | 0.288 | - | 22.5 |
| ideal | lazy_thetastar_known | warehouse | 100 | 0 | 0 | 0 | 27.53 | 0.597 | - | 56.8 |
| ideal | lazy_thetastar_known | forest | 100 | 0 | 0 | 0 | 18.17 | 0.895 | - | 20.7 |
| ideal | lazy_thetastar_known | maze | 100 | 0 | 0 | 0 | 29.96 | 0.797 | - | 56.2 |
| ideal | lazy_thetastar_known | glass_office | 100 | 0 | 0 | 0 | 20.94 | 0.264 | - | 44.3 |
| ideal | thetastar_unknown | random | 100 | 0 | 0 | 0 | 17.21 | 0.93 | - | 407.1 |
| ideal | thetastar_unknown | u_trap | 100 | 0 | 0 | 0 | 18.72 | 0.876 | - | 519 |
| ideal | thetastar_unknown | narrow_gap | 80 | 0 | 15 | 5 | 30.06 | 0.306 | - | 912.5 |
| ideal | thetastar_unknown | office | 90 | 0 | 10 | 0 | 18.37 | 0.278 | - | 51.6 |
| ideal | thetastar_unknown | warehouse | 55 | 0 | 40 | 5 | 39.84 | 0.356 | - | 1106.4 |
| ideal | thetastar_unknown | forest | 100 | 0 | 0 | 0 | 18.17 | 0.809 | - | 455.8 |
| ideal | thetastar_unknown | maze | 90 | 0 | 10 | 0 | 37.45 | 0.78 | - | 1342.1 |
| ideal | thetastar_unknown | glass_office | 95 | 0 | 5 | 0 | 25.6 | 0.274 | - | 145.3 |
| ideal | lazy_thetastar_unknown | random | 100 | 0 | 0 | 0 | 17.39 | 0.911 | - | 105.9 |
| ideal | lazy_thetastar_unknown | u_trap | 100 | 0 | 0 | 0 | 18.83 | 0.869 | - | 125.9 |
| ideal | lazy_thetastar_unknown | narrow_gap | 100 | 0 | 0 | 0 | 31.47 | 0.279 | - | 279.4 |
| ideal | lazy_thetastar_unknown | office | 85 | 0 | 15 | 0 | 17.78 | 0.275 | - | 28.1 |
| ideal | lazy_thetastar_unknown | warehouse | 55 | 0 | 45 | 0 | 40.78 | 0.394 | - | 334 |
| ideal | lazy_thetastar_unknown | forest | 100 | 0 | 0 | 0 | 18.39 | 0.856 | - | 111.7 |
| ideal | lazy_thetastar_unknown | maze | 85 | 0 | 15 | 0 | 36.24 | 0.772 | - | 400.2 |
| ideal | lazy_thetastar_unknown | glass_office | 90 | 0 | 10 | 0 | 25.2 | 0.274 | - | 57.5 |
| ideal | mppi | random | 90 | 0 | 10 | 0 | 20.35 | 0.45 | - | 16.9 |
| ideal | mppi | u_trap | 0 | 0 | 100 | 0 | - | 0.682 | - | 17.5 |
| ideal | mppi | narrow_gap | 25 | 0 | 75 | 0 | 22.76 | 0.561 | - | 30.3 |
| ideal | mppi | office | 25 | 0 | 75 | 0 | 8.4 | 0.578 | - | 9 |
| ideal | mppi | warehouse | 15 | 0 | 85 | 0 | 27.44 | 0.294 | - | 30.8 |
| ideal | mppi | forest | 100 | 0 | 0 | 0 | 20.34 | 0.432 | - | 16.8 |
| ideal | mppi | maze | 0 | 0 | 100 | 0 | - | 0.382 | - | 17.8 |
| ideal | mppi | glass_office | 10 | 0 | 90 | 0 | 5.88 | 0.604 | - | 9.9 |
| ideal | mppi_astar | random | 100 | 0 | 0 | 0 | 20.24 | 0.605 | - | 47.7 |
| ideal | mppi_astar | u_trap | 100 | 0 | 0 | 0 | 21.93 | 0.466 | - | 59.2 |
| ideal | mppi_astar | narrow_gap | 95 | 0 | 5 | 0 | 34.68 | 0.279 | - | 99.4 |
| ideal | mppi_astar | office | 95 | 0 | 5 | 0 | 11.04 | 0.298 | - | 16.5 |
| ideal | mppi_astar | warehouse | 55 | 0 | 45 | 0 | 23.56 | 0.316 | - | 67.4 |
| ideal | mppi_astar | forest | 100 | 0 | 0 | 0 | 20.38 | 0.581 | - | 50.3 |
| ideal | mppi_astar | maze | 95 | 0 | 5 | 0 | 33 | 0.372 | - | 94 |
| ideal | mppi_astar | glass_office | 95 | 0 | 5 | 0 | 14.78 | 0.297 | - | 24.3 |
| ideal | hybrid_astar | random | 100 | 0 | 0 | 0 | 18.48 | 0.67 | - | 14.3 |
| ideal | hybrid_astar | u_trap | 100 | 0 | 0 | 0 | 20 | 0.703 | - | 16 |
| ideal | hybrid_astar | narrow_gap | 85 | 0 | 10 | 5 | 32.54 | 0.289 | - | 28.1 |
| ideal | hybrid_astar | office | 90 | 0 | 10 | 0 | 20.12 | 0.258 | - | 18.4 |
| ideal | hybrid_astar | warehouse | 50 | 0 | 50 | 0 | 44.32 | 0.265 | - | 35.2 |
| ideal | hybrid_astar | forest | 100 | 0 | 0 | 0 | 22.59 | 0.55 | - | 17.6 |
| ideal | hybrid_astar | maze | 90 | 0 | 10 | 0 | 45.45 | 0.423 | - | 37.1 |
| ideal | hybrid_astar | glass_office | 85 | 0 | 15 | 0 | 29.2 | 0.264 | - | 21 |
| crazyflie | straight | random | 40 | 40 | 20 | 0 | 16.69 | 0.254 | matte 8 | 0.7 |
| crazyflie | straight | u_trap | 0 | 65 | 35 | 0 | - | 0.15 | matte 13 | 0.7 |
| crazyflie | straight | narrow_gap | 0 | 70 | 30 | 0 | - | 0.149 | matte 14 | 0.7 |
| crazyflie | straight | office | 0 | 65 | 35 | 0 | - | 0.149 | matte 13 | 0.4 |
| crazyflie | straight | warehouse | 0 | 65 | 35 | 0 | - | 0.149 | matte 13 | 0.3 |
| crazyflie | straight | forest | 15 | 60 | 25 | 0 | 16.82 | 0.149 | matte 12 | 0.5 |
| crazyflie | straight | maze | 0 | 80 | 20 | 0 | - | 0.149 | matte 16 | 0.3 |
| crazyflie | straight | glass_office | 5 | 70 | 25 | 0 | 5.18 | 0.149 | matte 14 | 0.3 |
| crazyflie | freest_beam | random | 50 | 5 | 45 | 0 | 24.41 | 0.456 | matte 1 | 0.9 |
| crazyflie | freest_beam | u_trap | 0 | 0 | 100 | 0 | - | 0.598 | - | 0.8 |
| crazyflie | freest_beam | narrow_gap | 0 | 0 | 80 | 20 | - | 0.44 | - | 1.4 |
| crazyflie | freest_beam | office | 0 | 0 | 95 | 5 | - | 0.406 | - | 0.4 |
| crazyflie | freest_beam | warehouse | 0 | 0 | 95 | 5 | - | 0.384 | - | 0.6 |
| crazyflie | freest_beam | forest | 35 | 15 | 50 | 0 | 25.14 | 0.226 | matte 3 | 0.6 |
| crazyflie | freest_beam | maze | 0 | 10 | 90 | 0 | - | 0.355 | matte 2 | 0.5 |
| crazyflie | freest_beam | glass_office | 5 | 5 | 90 | 0 | 6.44 | 0.454 | matte 1 | 0.4 |
| crazyflie | apf_escape | random | 85 | 0 | 10 | 5 | 26.68 | 0.58 | - | 1.2 |
| crazyflie | apf_escape | u_trap | 35 | 20 | 40 | 5 | 43.1 | 0.237 | matte 4 | 1.6 |
| crazyflie | apf_escape | narrow_gap | 0 | 5 | 40 | 55 | - | 0.422 | matte 1 | 1.9 |
| crazyflie | apf_escape | office | 0 | 10 | 65 | 25 | - | 0.246 | matte 2 | 1.4 |
| crazyflie | apf_escape | warehouse | 0 | 0 | 100 | 0 | - | 0.439 | - | 0.8 |
| crazyflie | apf_escape | forest | 60 | 25 | 10 | 5 | 32.84 | 0.192 | matte 5 | 1 |
| crazyflie | apf_escape | maze | 0 | 15 | 80 | 5 | - | 0.341 | matte 3 | 1.9 |
| crazyflie | apf_escape | glass_office | 5 | 20 | 60 | 15 | 11.82 | 0.278 | glass 3, matte 1 | 1.1 |
| crazyflie | vfh_plus | random | 45 | 55 | 0 | 0 | 24.88 | 0.15 | matte 11 | 0.7 |
| crazyflie | vfh_plus | u_trap | 0 | 100 | 0 | 0 | - | 0.147 | matte 20 | 0.6 |
| crazyflie | vfh_plus | narrow_gap | 5 | 95 | 0 | 0 | 29.24 | 0.146 | matte 19 | 0.6 |
| crazyflie | vfh_plus | office | 5 | 90 | 0 | 5 | 9.02 | 0.146 | matte 18 | 0.2 |
| crazyflie | vfh_plus | warehouse | 0 | 95 | 5 | 0 | - | 0.147 | matte 19 | 0.3 |
| crazyflie | vfh_plus | forest | 35 | 65 | 0 | 0 | 25.16 | 0.145 | matte 13 | 0.6 |
| crazyflie | vfh_plus | maze | 0 | 100 | 0 | 0 | - | 0.147 | matte 20 | 0.2 |
| crazyflie | vfh_plus | glass_office | 0 | 90 | 10 | 0 | - | 0.147 | matte 18 | 0.3 |
| crazyflie | astar_known | random | 100 | 0 | 0 | 0 | 18.46 | 0.633 | - | 4.3 |
| crazyflie | astar_known | u_trap | 100 | 0 | 0 | 0 | 19.24 | 0.617 | - | 5.5 |
| crazyflie | astar_known | narrow_gap | 100 | 0 | 0 | 0 | 24.48 | 0.277 | - | 12.2 |
| crazyflie | astar_known | office | 100 | 0 | 0 | 0 | 21.01 | 0.265 | - | 8.6 |
| crazyflie | astar_known | warehouse | 100 | 0 | 0 | 0 | 43.74 | 0.539 | - | 26.2 |
| crazyflie | astar_known | forest | 100 | 0 | 0 | 0 | 22.72 | 0.616 | - | 8.5 |
| crazyflie | astar_known | maze | 100 | 0 | 0 | 0 | 41.03 | 0.594 | - | 46.3 |
| crazyflie | astar_known | glass_office | 100 | 0 | 0 | 0 | 25.12 | 0.265 | - | 15.8 |
| crazyflie | astar_unknown | random | 100 | 0 | 0 | 0 | 21.8 | 0.634 | - | 38.5 |
| crazyflie | astar_unknown | u_trap | 100 | 0 | 0 | 0 | 29.46 | 0.41 | - | 68.3 |
| crazyflie | astar_unknown | narrow_gap | 20 | 5 | 0 | 75 | 27.85 | 0.274 | matte 1 | 130.8 |
| crazyflie | astar_unknown | office | 30 | 35 | 25 | 10 | 18.9 | 0.199 | matte 7 | 18.7 |
| crazyflie | astar_unknown | warehouse | 5 | 55 | 40 | 0 | 56.84 | 0.149 | matte 11 | 114.3 |
| crazyflie | astar_unknown | forest | 100 | 0 | 0 | 0 | 24.58 | 0.497 | - | 45.9 |
| crazyflie | astar_unknown | maze | 45 | 0 | 45 | 10 | 81.8 | 0.257 | - | 172.8 |
| crazyflie | astar_unknown | glass_office | 15 | 60 | 25 | 0 | 21.16 | 0.148 | glass 8, matte 4 | 20.1 |
| crazyflie | informed_rrt_star | random | 100 | 0 | 0 | 0 | 23.92 | 0.288 | - | 12.3 |
| crazyflie | informed_rrt_star | u_trap | 100 | 0 | 0 | 0 | 23.36 | 0.257 | - | 8.5 |
| crazyflie | informed_rrt_star | narrow_gap | 100 | 0 | 0 | 0 | 28.13 | 0.256 | - | 8.7 |
| crazyflie | informed_rrt_star | office | 100 | 0 | 0 | 0 | 25.73 | 0.249 | - | 10.1 |
| crazyflie | informed_rrt_star | warehouse | 100 | 0 | 0 | 0 | 62.5 | 0.248 | - | 5.8 |
| crazyflie | informed_rrt_star | forest | 100 | 0 | 0 | 0 | 33.8 | 0.263 | - | 13.6 |
| crazyflie | informed_rrt_star | maze | 100 | 0 | 0 | 0 | 74.63 | 0.264 | - | 8.3 |
| crazyflie | informed_rrt_star | glass_office | 100 | 0 | 0 | 0 | 31.9 | 0.249 | - | 8.6 |
| crazyflie | astar_mpc | random | 100 | 0 | 0 | 0 | 18.03 | 0.632 | - | 7.9 |
| crazyflie | astar_mpc | u_trap | 100 | 0 | 0 | 0 | 18.65 | 0.62 | - | 9.6 |
| crazyflie | astar_mpc | narrow_gap | 100 | 0 | 0 | 0 | 22.02 | 0.338 | - | 15.7 |
| crazyflie | astar_mpc | office | 100 | 0 | 0 | 0 | 16.37 | 0.37 | - | 11.9 |
| crazyflie | astar_mpc | warehouse | 100 | 0 | 0 | 0 | 38.03 | 0.577 | - | 34.8 |
| crazyflie | astar_mpc | forest | 100 | 0 | 0 | 0 | 20.33 | 0.62 | - | 12.5 |
| crazyflie | astar_mpc | maze | 100 | 0 | 0 | 0 | 37.26 | 0.601 | - | 53.4 |
| crazyflie | astar_mpc | glass_office | 100 | 0 | 0 | 0 | 19.16 | 0.29 | - | 18.8 |
| crazyflie | astar_unknown_f2 | random | 100 | 0 | 0 | 0 | 22.56 | 0.695 | - | 42.4 |
| crazyflie | astar_unknown_f2 | u_trap | 100 | 0 | 0 | 0 | 28.84 | 0.5 | - | 64.7 |
| crazyflie | astar_unknown_f2 | narrow_gap | 15 | 0 | 0 | 85 | 29.16 | 0.439 | - | 165.7 |
| crazyflie | astar_unknown_f2 | office | 40 | 5 | 50 | 5 | 22.61 | 0.287 | matte 1 | 21 |
| crazyflie | astar_unknown_f2 | warehouse | 30 | 0 | 70 | 0 | 82.34 | 0.348 | - | 132.2 |
| crazyflie | astar_unknown_f2 | forest | 100 | 0 | 0 | 0 | 25.54 | 0.506 | - | 48.5 |
| crazyflie | astar_unknown_f2 | maze | 50 | 0 | 40 | 10 | 81.32 | 0.46 | - | 169.7 |
| crazyflie | astar_unknown_f2 | glass_office | 5 | 65 | 25 | 5 | 50.78 | 0.149 | glass 13 | 23.2 |
| crazyflie | dwa | random | 40 | 35 | 25 | 0 | 25.69 | 0.166 | matte 7 | 2.8 |
| crazyflie | dwa | u_trap | 0 | 15 | 85 | 0 | - | 0.22 | matte 3 | 3 |
| crazyflie | dwa | narrow_gap | 0 | 40 | 55 | 5 | - | 0.154 | matte 8 | 3.6 |
| crazyflie | dwa | office | 0 | 55 | 45 | 0 | - | 0.15 | matte 11 | 1.7 |
| crazyflie | dwa | warehouse | 0 | 50 | 50 | 0 | - | 0.151 | matte 10 | 1.9 |
| crazyflie | dwa | forest | 10 | 90 | 0 | 0 | 27.91 | 0.148 | matte 18 | 1.8 |
| crazyflie | dwa | maze | 0 | 65 | 35 | 0 | - | 0.149 | matte 13 | 2.1 |
| crazyflie | dwa | glass_office | 5 | 60 | 35 | 0 | 11.98 | 0.15 | matte 12 | 1.6 |
| crazyflie | dwa_mem | random | 55 | 5 | 40 | 0 | 26.28 | 0.273 | matte 1 | 6.2 |
| crazyflie | dwa_mem | u_trap | 0 | 0 | 100 | 0 | - | 0.262 | - | 7.3 |
| crazyflie | dwa_mem | narrow_gap | 5 | 0 | 15 | 80 | 46.54 | 0.24 | - | 12.7 |
| crazyflie | dwa_mem | office | 5 | 0 | 95 | 0 | 17.16 | 0.272 | - | 7 |
| crazyflie | dwa_mem | warehouse | 0 | 20 | 75 | 5 | - | 0.207 | matte 4 | 19.4 |
| crazyflie | dwa_mem | forest | 45 | 15 | 20 | 20 | 41.74 | 0.223 | matte 3 | 8.4 |
| crazyflie | dwa_mem | maze | 0 | 15 | 80 | 5 | - | 0.23 | matte 3 | 18.6 |
| crazyflie | dwa_mem | glass_office | 5 | 5 | 90 | 0 | 17.98 | 0.255 | matte 1 | 6.2 |
| crazyflie | bug2 | random | 90 | 10 | 0 | 0 | 27.86 | 0.402 | matte 2 | 1.1 |
| crazyflie | bug2 | u_trap | 20 | 30 | 0 | 50 | 45.16 | 0.206 | matte 6 | 1.8 |
| crazyflie | bug2 | narrow_gap | 0 | 0 | 0 | 100 | - | 0.34 | - | 2.4 |
| crazyflie | bug2 | office | 0 | 35 | 50 | 15 | - | 0.21 | matte 7 | 0.8 |
| crazyflie | bug2 | warehouse | 15 | 20 | 60 | 5 | 77.84 | 0.229 | matte 4 | 1.6 |
| crazyflie | bug2 | forest | 50 | 40 | 5 | 5 | 30.03 | 0.194 | matte 8 | 1.2 |
| crazyflie | bug2 | maze | 0 | 20 | 80 | 0 | - | 0.335 | matte 4 | 1.1 |
| crazyflie | bug2 | glass_office | 5 | 40 | 55 | 0 | 6.2 | 0.2 | glass 1, matte 7 | 0.7 |
| crazyflie | tangent_bug | random | 55 | 45 | 0 | 0 | 24.44 | 0.216 | matte 9 | 0.9 |
| crazyflie | tangent_bug | u_trap | 35 | 15 | 10 | 40 | 31.66 | 0.302 | matte 3 | 1.7 |
| crazyflie | tangent_bug | narrow_gap | 5 | 10 | 25 | 60 | 26.9 | 0.234 | matte 2 | 1.7 |
| crazyflie | tangent_bug | office | 10 | 45 | 35 | 10 | 12.4 | 0.154 | matte 9 | 0.8 |
| crazyflie | tangent_bug | warehouse | 0 | 35 | 55 | 10 | - | 0.203 | matte 7 | 1 |
| crazyflie | tangent_bug | forest | 25 | 75 | 0 | 0 | 24.36 | 0.149 | matte 15 | 0.5 |
| crazyflie | tangent_bug | maze | 0 | 50 | 45 | 5 | - | 0.151 | matte 10 | 1.2 |
| crazyflie | tangent_bug | glass_office | 5 | 50 | 35 | 10 | 17.36 | 0.153 | glass 1, matte 9 | 0.9 |
| crazyflie | dstar_lite | random | 100 | 0 | 0 | 0 | 22.23 | 0.63 | - | 7.3 |
| crazyflie | dstar_lite | u_trap | 100 | 0 | 0 | 0 | 29.51 | 0.426 | - | 11.7 |
| crazyflie | dstar_lite | narrow_gap | 20 | 0 | 0 | 80 | 27.76 | 0.263 | - | 27.8 |
| crazyflie | dstar_lite | office | 35 | 25 | 40 | 0 | 21 | 0.235 | matte 5 | 9.8 |
| crazyflie | dstar_lite | warehouse | 10 | 55 | 25 | 10 | 87.44 | 0.149 | matte 11 | 28.7 |
| crazyflie | dstar_lite | forest | 95 | 5 | 0 | 0 | 24.36 | 0.48 | matte 1 | 8.5 |
| crazyflie | dstar_lite | maze | 55 | 0 | 40 | 5 | 86.52 | 0.257 | - | 36.7 |
| crazyflie | dstar_lite | glass_office | 15 | 60 | 20 | 5 | 21.26 | 0.148 | glass 6, matte 6 | 10.3 |
| crazyflie | thetastar_known | random | 100 | 0 | 0 | 0 | 17.09 | 0.943 | - | 22.2 |
| crazyflie | thetastar_known | u_trap | 100 | 0 | 0 | 0 | 17.66 | 0.931 | - | 31.5 |
| crazyflie | thetastar_known | narrow_gap | 100 | 0 | 0 | 0 | 22.36 | 0.34 | - | 74.1 |
| crazyflie | thetastar_known | office | 100 | 0 | 0 | 0 | 18.05 | 0.283 | - | 35.4 |
| crazyflie | thetastar_known | warehouse | 100 | 0 | 0 | 0 | 27.46 | 0.603 | - | 79.6 |
| crazyflie | thetastar_known | forest | 100 | 0 | 0 | 0 | 18.12 | 0.891 | - | 28.9 |
| crazyflie | thetastar_known | maze | 100 | 0 | 0 | 0 | 30.07 | 0.797 | - | 93.6 |
| crazyflie | thetastar_known | glass_office | 100 | 0 | 0 | 0 | 21.17 | 0.266 | - | 71.7 |
| crazyflie | lazy_thetastar_known | random | 100 | 0 | 0 | 0 | 17.11 | 0.933 | - | 16.9 |
| crazyflie | lazy_thetastar_known | u_trap | 100 | 0 | 0 | 0 | 17.68 | 0.921 | - | 19.4 |
| crazyflie | lazy_thetastar_known | narrow_gap | 100 | 0 | 0 | 0 | 22.36 | 0.347 | - | 53.8 |
| crazyflie | lazy_thetastar_known | office | 100 | 0 | 0 | 0 | 18.03 | 0.288 | - | 22.7 |
| crazyflie | lazy_thetastar_known | warehouse | 100 | 0 | 0 | 0 | 27.53 | 0.597 | - | 57.2 |
| crazyflie | lazy_thetastar_known | forest | 100 | 0 | 0 | 0 | 18.17 | 0.895 | - | 20.3 |
| crazyflie | lazy_thetastar_known | maze | 100 | 0 | 0 | 0 | 29.96 | 0.797 | - | 56.7 |
| crazyflie | lazy_thetastar_known | glass_office | 100 | 0 | 0 | 0 | 20.94 | 0.264 | - | 44.1 |
| crazyflie | thetastar_unknown | random | 95 | 5 | 0 | 0 | 19.38 | 0.735 | matte 1 | 748.7 |
| crazyflie | thetastar_unknown | u_trap | 100 | 0 | 0 | 0 | 25.21 | 0.464 | - | 1094.4 |
| crazyflie | thetastar_unknown | narrow_gap | 10 | 25 | 5 | 60 | 52.95 | 0.207 | matte 5 | 2559.7 |
| crazyflie | thetastar_unknown | office | 35 | 40 | 25 | 0 | 24.9 | 0.198 | matte 8 | 95 |
| crazyflie | thetastar_unknown | warehouse | 20 | 40 | 40 | 0 | 87.8 | 0.195 | matte 8 | 2981.5 |
| crazyflie | thetastar_unknown | forest | 95 | 5 | 0 | 0 | 23 | 0.475 | matte 1 | 973.5 |
| crazyflie | thetastar_unknown | maze | 50 | 5 | 40 | 5 | 76.66 | 0.283 | matte 1 | 3757 |
| crazyflie | thetastar_unknown | glass_office | 20 | 65 | 15 | 0 | 45.61 | 0.148 | glass 12, matte 1 | 301.2 |
| crazyflie | lazy_thetastar_unknown | random | 100 | 0 | 0 | 0 | 19.6 | 0.811 | - | 180.2 |
| crazyflie | lazy_thetastar_unknown | u_trap | 100 | 0 | 0 | 0 | 25.23 | 0.47 | - | 285.5 |
| crazyflie | lazy_thetastar_unknown | narrow_gap | 20 | 10 | 0 | 70 | 55.16 | 0.209 | matte 2 | 813.7 |
| crazyflie | lazy_thetastar_unknown | office | 35 | 45 | 15 | 5 | 20.72 | 0.165 | matte 9 | 42.7 |
| crazyflie | lazy_thetastar_unknown | warehouse | 15 | 25 | 40 | 20 | 86.86 | 0.214 | matte 5 | 890.7 |
| crazyflie | lazy_thetastar_unknown | forest | 95 | 5 | 0 | 0 | 23.6 | 0.421 | matte 1 | 241.5 |
| crazyflie | lazy_thetastar_unknown | maze | 40 | 5 | 45 | 10 | 77.03 | 0.289 | matte 1 | 1022.8 |
| crazyflie | lazy_thetastar_unknown | glass_office | 15 | 65 | 20 | 0 | 16.46 | 0.148 | glass 9, matte 4 | 86.5 |
| crazyflie | mppi | random | 60 | 35 | 5 | 0 | 20.31 | 0.487 | matte 7 | 12.7 |
| crazyflie | mppi | u_trap | 0 | 95 | 5 | 0 | - | 0.141 | matte 19 | 8.2 |
| crazyflie | mppi | narrow_gap | 5 | 95 | 0 | 0 | 21.6 | 0.137 | matte 19 | 8.3 |
| crazyflie | mppi | office | 10 | 80 | 10 | 0 | 16.64 | 0.142 | matte 16 | 4.3 |
| crazyflie | mppi | warehouse | 0 | 100 | 0 | 0 | - | 0.142 | matte 20 | 0.8 |
| crazyflie | mppi | forest | 100 | 0 | 0 | 0 | 20.88 | 0.407 | - | 15.6 |
| crazyflie | mppi | maze | 0 | 95 | 5 | 0 | - | 0.141 | matte 19 | 3.7 |
| crazyflie | mppi | glass_office | 10 | 70 | 20 | 0 | 7.59 | 0.149 | glass 1, matte 13 | 3.8 |
| crazyflie | mppi_astar | random | 80 | 20 | 0 | 0 | 20.37 | 0.624 | matte 4 | 51.1 |
| crazyflie | mppi_astar | u_trap | 80 | 20 | 0 | 0 | 27.1 | 0.193 | matte 4 | 72.6 |
| crazyflie | mppi_astar | narrow_gap | 10 | 90 | 0 | 0 | 21.48 | 0.14 | matte 18 | 45.1 |
| crazyflie | mppi_astar | office | 15 | 80 | 5 | 0 | 7.94 | 0.146 | matte 16 | 9.7 |
| crazyflie | mppi_astar | warehouse | 0 | 100 | 0 | 0 | - | 0.143 | matte 20 | 23.4 |
| crazyflie | mppi_astar | forest | 100 | 0 | 0 | 0 | 21.29 | 0.421 | - | 54.8 |
| crazyflie | mppi_astar | maze | 5 | 95 | 0 | 0 | 41.24 | 0.143 | matte 19 | 52.8 |
| crazyflie | mppi_astar | glass_office | 5 | 80 | 15 | 0 | 8.34 | 0.144 | glass 4, matte 12 | 15.4 |
| crazyflie | hybrid_astar | random | 100 | 0 | 0 | 0 | 22.29 | 0.587 | - | 16.2 |
| crazyflie | hybrid_astar | u_trap | 95 | 5 | 0 | 0 | 28.16 | 0.42 | matte 1 | 21.9 |
| crazyflie | hybrid_astar | narrow_gap | 0 | 0 | 5 | 95 | - | 0.257 | - | 49 |
| crazyflie | hybrid_astar | office | 25 | 35 | 30 | 10 | 19.8 | 0.176 | matte 7 | 21 |
| crazyflie | hybrid_astar | warehouse | 0 | 20 | 65 | 15 | - | 0.267 | matte 4 | 50.8 |
| crazyflie | hybrid_astar | forest | 95 | 5 | 0 | 0 | 26.02 | 0.372 | matte 1 | 20.5 |
| crazyflie | hybrid_astar | maze | 40 | 5 | 25 | 30 | 87.15 | 0.299 | matte 1 | 62.5 |
| crazyflie | hybrid_astar | glass_office | 5 | 70 | 20 | 5 | 16.6 | 0.148 | glass 10, matte 4 | 20.6 |
