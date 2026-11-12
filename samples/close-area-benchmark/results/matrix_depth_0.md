`python bench.py --presets depth_cam_87 --planners astar_unknown,astar_unknown_f2,dstar_lite,dwa_mem,mppi_astar --layouts 6 --workers 10 --stem matrix_depth_0_regen` from samples/close-area-benchmark. Input: synthetic (simulated layouts, vehicle and sensors). Scored on truth. Seed 0, 6 layouts per cell, 10 worker processes, wall 58.9 s. Run time limit per family (s): random 60, u_trap 60, narrow_gap 60, office 60, warehouse 120, forest 60, maze 120, glass_office 60.

Regenerated 2026-11-12 with SKIP_DROPPED_BEAMS = True in close-area-arena/planners/astar_esdf.py (a beam the sensor flags dropped adds nothing to the map; docs/upstream-findings.md section 22). Written as matrix_depth_0_regen and renamed to matrix_depth_0. Same layouts and limits as the previous run of this file; the environment moved from Python 3.11.15 / numpy 2.4.6 / scipy 1.17.1 to the one below, and dwa_mem (no map, so untouched by the fix) reproduced 48/48 runs exactly.

### Preset `depth_cam_87`

Cell = reached % / collision % (20 layouts unless stated).

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| astar_unknown | 100 / 0 | 100 / 0 | 33.3 / 50 | 83.3 / 0 | 83.3 / 0 | 100 / 0 | 83.3 / 0 | 16.7 / 83.3 |
| astar_unknown_f2 | 100 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 16.7 / 16.7 | 100 / 0 | 50 / 0 | 0 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 | 33.3 / 33.3 | 83.3 / 0 | 66.7 / 0 | 100 / 0 | 83.3 / 0 | 16.7 / 83.3 |
| dwa_mem | 66.7 / 16.7 | 0 / 0 | 16.7 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 0 / 0 | 16.7 / 0 |
| mppi_astar | 100 / 0 | 100 / 0 | 83.3 / 0 | 100 / 0 | 83.3 / 0 | 100 / 0 | 100 / 0 | 16.7 / 83.3 |

Best planner per family (reached / collision %): random => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); narrow_gap => mppi_astar (83.3 / 0); office => mppi_astar (100 / 0); warehouse => astar_unknown/mppi_astar (83.3 / 0); forest => astar_unknown/astar_unknown_f2/dstar_lite/dwa_mem/mppi_astar (100 / 0); maze => mppi_astar (100 / 0); glass_office => dwa_mem (16.7 / 0)

Best without a prior map (astar_known, informed_rrt_star, astar_mpc, thetastar_known, lazy_thetastar_known excluded): random => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); narrow_gap => mppi_astar (83.3 / 0); office => mppi_astar (100 / 0); warehouse => astar_unknown/mppi_astar (83.3 / 0); forest => astar_unknown/astar_unknown_f2/dstar_lite/dwa_mem/mppi_astar (100 / 0); maze => mppi_astar (100 / 0); glass_office => dwa_mem (16.7 / 0)

### All fields

| preset | planner | family | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | collisions by material | sum of run wall s |
|---|---|---|---|---|---|---|---|---|---|---|
| depth_cam_87 | astar_unknown | random | 100 | 0 | 0 | 0 | 18.71 | 0.673 | - | 9.6 |
| depth_cam_87 | astar_unknown | u_trap | 100 | 0 | 0 | 0 | 21.92 | 0.626 | - | 13.4 |
| depth_cam_87 | astar_unknown | narrow_gap | 33.3 | 50 | 0 | 16.7 | 25.06 | 0.156 | matte 3 | 33.7 |
| depth_cam_87 | astar_unknown | office | 83.3 | 0 | 16.7 | 0 | 26.22 | 0.248 | - | 6.1 |
| depth_cam_87 | astar_unknown | warehouse | 83.3 | 0 | 16.7 | 0 | 52.88 | 0.297 | - | 28.6 |
| depth_cam_87 | astar_unknown | forest | 100 | 0 | 0 | 0 | 21.81 | 0.652 | - | 11.6 |
| depth_cam_87 | astar_unknown | maze | 83.3 | 0 | 16.7 | 0 | 46.64 | 0.556 | - | 30.5 |
| depth_cam_87 | astar_unknown | glass_office | 16.7 | 83.3 | 0 | 0 | 13.38 | 0.148 | glass 5 | 4.2 |
| depth_cam_87 | astar_unknown_f2 | random | 100 | 0 | 0 | 0 | 18.98 | 0.652 | - | 10.7 |
| depth_cam_87 | astar_unknown_f2 | u_trap | 100 | 0 | 0 | 0 | 22.87 | 0.669 | - | 14.6 |
| depth_cam_87 | astar_unknown_f2 | narrow_gap | 0 | 0 | 66.7 | 33.3 | - | 0.721 | - | 34.3 |
| depth_cam_87 | astar_unknown_f2 | office | 0 | 0 | 100 | 0 | - | 0.835 | - | 4.4 |
| depth_cam_87 | astar_unknown_f2 | warehouse | 16.7 | 16.7 | 50 | 16.7 | 90.3 | 0.368 | wall 1 | 33.3 |
| depth_cam_87 | astar_unknown_f2 | forest | 100 | 0 | 0 | 0 | 22.86 | 0.675 | - | 12.2 |
| depth_cam_87 | astar_unknown_f2 | maze | 50 | 0 | 50 | 0 | 56.2 | 0.577 | - | 36.1 |
| depth_cam_87 | astar_unknown_f2 | glass_office | 0 | 0 | 100 | 0 | - | 0.817 | - | 4.1 |
| depth_cam_87 | dstar_lite | random | 100 | 0 | 0 | 0 | 18.67 | 0.682 | - | 2.2 |
| depth_cam_87 | dstar_lite | u_trap | 100 | 0 | 0 | 0 | 21.92 | 0.624 | - | 2.7 |
| depth_cam_87 | dstar_lite | narrow_gap | 33.3 | 33.3 | 0 | 33.3 | 25.31 | 0.245 | matte 2 | 8.2 |
| depth_cam_87 | dstar_lite | office | 83.3 | 0 | 16.7 | 0 | 26.22 | 0.256 | - | 4 |
| depth_cam_87 | dstar_lite | warehouse | 66.7 | 0 | 33.3 | 0 | 52.65 | 0.304 | - | 12.5 |
| depth_cam_87 | dstar_lite | forest | 100 | 0 | 0 | 0 | 21.99 | 0.652 | - | 2.8 |
| depth_cam_87 | dstar_lite | maze | 83.3 | 0 | 16.7 | 0 | 45.76 | 0.574 | - | 9.2 |
| depth_cam_87 | dstar_lite | glass_office | 16.7 | 83.3 | 0 | 0 | 13.4 | 0.148 | glass 5 | 2.9 |
| depth_cam_87 | dwa_mem | random | 66.7 | 16.7 | 16.7 | 0 | 31.2 | 0.281 | matte 1 | 4.2 |
| depth_cam_87 | dwa_mem | u_trap | 0 | 0 | 100 | 0 | - | 0.341 | - | 4.3 |
| depth_cam_87 | dwa_mem | narrow_gap | 16.7 | 0 | 16.7 | 66.7 | 48.2 | 0.265 | - | 8.7 |
| depth_cam_87 | dwa_mem | office | 0 | 0 | 100 | 0 | - | 0.305 | - | 3.7 |
| depth_cam_87 | dwa_mem | warehouse | 0 | 0 | 100 | 0 | - | 0.274 | - | 10.4 |
| depth_cam_87 | dwa_mem | forest | 100 | 0 | 0 | 0 | 48.12 | 0.281 | - | 7.1 |
| depth_cam_87 | dwa_mem | maze | 0 | 0 | 100 | 0 | - | 0.277 | - | 9.5 |
| depth_cam_87 | dwa_mem | glass_office | 16.7 | 0 | 83.3 | 0 | 20.02 | 0.321 | - | 3.5 |
| depth_cam_87 | mppi_astar | random | 100 | 0 | 0 | 0 | 20.28 | 0.666 | - | 15.3 |
| depth_cam_87 | mppi_astar | u_trap | 100 | 0 | 0 | 0 | 22.73 | 0.495 | - | 19.9 |
| depth_cam_87 | mppi_astar | narrow_gap | 83.3 | 0 | 16.7 | 0 | 39.24 | 0.268 | - | 38.3 |
| depth_cam_87 | mppi_astar | office | 100 | 0 | 0 | 0 | 14.18 | 0.281 | - | 8 |
| depth_cam_87 | mppi_astar | warehouse | 83.3 | 0 | 16.7 | 0 | 34.36 | 0.272 | - | 26.2 |
| depth_cam_87 | mppi_astar | forest | 100 | 0 | 0 | 0 | 20.37 | 0.65 | - | 15.4 |
| depth_cam_87 | mppi_astar | maze | 100 | 0 | 0 | 0 | 36.07 | 0.352 | - | 45.5 |
| depth_cam_87 | mppi_astar | glass_office | 16.7 | 83.3 | 0 | 0 | 5.58 | 0.139 | glass 4, matte 1 | 3.7 |
