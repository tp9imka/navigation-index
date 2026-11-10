`python bench.py --presets depth_cam_87 --planners astar_unknown,astar_unknown_f2,dstar_lite,dwa_mem,mppi_astar --layouts 6 --workers 4 --stem matrix_depth_0` from samples/close-area-benchmark. Input: synthetic (simulated layouts, vehicle and sensors). Scored on truth. Seed 0, 6 layouts per cell, 4 worker processes, wall 121.4 s. Run time limit per family (s): random 60, u_trap 60, narrow_gap 60, office 60, warehouse 120, forest 60, maze 120, glass_office 60.

### Preset `depth_cam_87`

Cell = reached % / collision % (20 layouts unless stated).

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| astar_unknown | 100 / 0 | 100 / 0 | 33.3 / 33.3 | 66.7 / 0 | 83.3 / 16.7 | 100 / 0 | 100 / 0 | 16.7 / 83.3 |
| astar_unknown_f2 | 100 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 16.7 / 16.7 | 100 / 0 | 16.7 / 0 | 0 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 | 66.7 / 16.7 | 66.7 / 0 | 83.3 / 0 | 100 / 0 | 83.3 / 0 | 33.3 / 66.7 |
| dwa_mem | 66.7 / 16.7 | 0 / 0 | 16.7 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 0 / 0 | 16.7 / 0 |
| mppi_astar | 100 / 0 | 100 / 0 | 83.3 / 0 | 50 / 50 | 50 / 50 | 100 / 0 | 83.3 / 16.7 | 16.7 / 83.3 |

Best planner per family (reached / collision %): random => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); narrow_gap => mppi_astar (83.3 / 0); office => astar_unknown/dstar_lite (66.7 / 0); warehouse => dstar_lite (83.3 / 0); forest => astar_unknown/astar_unknown_f2/dstar_lite/dwa_mem/mppi_astar (100 / 0); maze => astar_unknown (100 / 0); glass_office => dstar_lite (33.3 / 66.7)

Best without a prior map (astar_known, informed_rrt_star, astar_mpc, thetastar_known, lazy_thetastar_known excluded): random => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); u_trap => astar_unknown/astar_unknown_f2/dstar_lite/mppi_astar (100 / 0); narrow_gap => mppi_astar (83.3 / 0); office => astar_unknown/dstar_lite (66.7 / 0); warehouse => dstar_lite (83.3 / 0); forest => astar_unknown/astar_unknown_f2/dstar_lite/dwa_mem/mppi_astar (100 / 0); maze => astar_unknown (100 / 0); glass_office => dstar_lite (33.3 / 66.7)

### All fields

| preset | planner | family | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | collisions by material | sum of run wall s |
|---|---|---|---|---|---|---|---|---|---|---|
| depth_cam_87 | astar_unknown | random | 100 | 0 | 0 | 0 | 18.71 | 0.651 | - | 8.7 |
| depth_cam_87 | astar_unknown | u_trap | 100 | 0 | 0 | 0 | 21.94 | 0.615 | - | 12 |
| depth_cam_87 | astar_unknown | narrow_gap | 33.3 | 33.3 | 0 | 33.3 | 25 | 0.245 | matte 2 | 32.7 |
| depth_cam_87 | astar_unknown | office | 66.7 | 0 | 33.3 | 0 | 25.02 | 0.25 | - | 4 |
| depth_cam_87 | astar_unknown | warehouse | 83.3 | 16.7 | 0 | 0 | 57.8 | 0.27 | matte 1 | 28.8 |
| depth_cam_87 | astar_unknown | forest | 100 | 0 | 0 | 0 | 21.84 | 0.648 | - | 10 |
| depth_cam_87 | astar_unknown | maze | 100 | 0 | 0 | 0 | 50.68 | 0.554 | - | 27.8 |
| depth_cam_87 | astar_unknown | glass_office | 16.7 | 83.3 | 0 | 0 | 13.2 | 0.146 | glass 5 | 2.6 |
| depth_cam_87 | astar_unknown_f2 | random | 100 | 0 | 0 | 0 | 19 | 0.64 | - | 9.1 |
| depth_cam_87 | astar_unknown_f2 | u_trap | 100 | 0 | 0 | 0 | 23.08 | 0.653 | - | 12.9 |
| depth_cam_87 | astar_unknown_f2 | narrow_gap | 0 | 0 | 100 | 0 | - | 0.724 | - | 30.7 |
| depth_cam_87 | astar_unknown_f2 | office | 0 | 0 | 100 | 0 | - | 0.796 | - | 3.1 |
| depth_cam_87 | astar_unknown_f2 | warehouse | 16.7 | 16.7 | 66.7 | 0 | 74.84 | 0.378 | wall 1 | 25.2 |
| depth_cam_87 | astar_unknown_f2 | forest | 100 | 0 | 0 | 0 | 22.65 | 0.667 | - | 10.7 |
| depth_cam_87 | astar_unknown_f2 | maze | 16.7 | 0 | 83.3 | 0 | 55 | 0.563 | - | 32.5 |
| depth_cam_87 | astar_unknown_f2 | glass_office | 0 | 0 | 100 | 0 | - | 0.83 | - | 3.2 |
| depth_cam_87 | dstar_lite | random | 100 | 0 | 0 | 0 | 18.67 | 0.682 | - | 2 |
| depth_cam_87 | dstar_lite | u_trap | 100 | 0 | 0 | 0 | 21.85 | 0.607 | - | 2.6 |
| depth_cam_87 | dstar_lite | narrow_gap | 66.7 | 16.7 | 0 | 16.7 | 33.17 | 0.234 | matte 1 | 7.1 |
| depth_cam_87 | dstar_lite | office | 66.7 | 0 | 33.3 | 0 | 25.2 | 0.251 | - | 3.7 |
| depth_cam_87 | dstar_lite | warehouse | 83.3 | 0 | 16.7 | 0 | 58.1 | 0.257 | - | 10.4 |
| depth_cam_87 | dstar_lite | forest | 100 | 0 | 0 | 0 | 21.76 | 0.653 | - | 2.5 |
| depth_cam_87 | dstar_lite | maze | 83.3 | 0 | 16.7 | 0 | 50.56 | 0.559 | - | 8.7 |
| depth_cam_87 | dstar_lite | glass_office | 33.3 | 66.7 | 0 | 0 | 30.78 | 0.146 | glass 4 | 3.2 |
| depth_cam_87 | dwa_mem | random | 66.7 | 16.7 | 16.7 | 0 | 31.2 | 0.281 | matte 1 | 3.7 |
| depth_cam_87 | dwa_mem | u_trap | 0 | 0 | 100 | 0 | - | 0.341 | - | 3.5 |
| depth_cam_87 | dwa_mem | narrow_gap | 16.7 | 0 | 16.7 | 66.7 | 48.2 | 0.265 | - | 7.7 |
| depth_cam_87 | dwa_mem | office | 0 | 0 | 100 | 0 | - | 0.305 | - | 3.3 |
| depth_cam_87 | dwa_mem | warehouse | 0 | 0 | 100 | 0 | - | 0.274 | - | 9.6 |
| depth_cam_87 | dwa_mem | forest | 100 | 0 | 0 | 0 | 48.12 | 0.281 | - | 6.3 |
| depth_cam_87 | dwa_mem | maze | 0 | 0 | 100 | 0 | - | 0.277 | - | 8.5 |
| depth_cam_87 | dwa_mem | glass_office | 16.7 | 0 | 83.3 | 0 | 20.02 | 0.321 | - | 3.1 |
| depth_cam_87 | mppi_astar | random | 100 | 0 | 0 | 0 | 20.28 | 0.659 | - | 13.5 |
| depth_cam_87 | mppi_astar | u_trap | 100 | 0 | 0 | 0 | 22.68 | 0.478 | - | 16.5 |
| depth_cam_87 | mppi_astar | narrow_gap | 83.3 | 0 | 0 | 16.7 | 40.84 | 0.26 | - | 39.5 |
| depth_cam_87 | mppi_astar | office | 50 | 50 | 0 | 0 | 12.64 | 0.196 | matte 3 | 4.1 |
| depth_cam_87 | mppi_astar | warehouse | 50 | 50 | 0 | 0 | 24.94 | 0.183 | matte 3 | 13.1 |
| depth_cam_87 | mppi_astar | forest | 100 | 0 | 0 | 0 | 20.35 | 0.617 | - | 13.5 |
| depth_cam_87 | mppi_astar | maze | 83.3 | 16.7 | 0 | 0 | 33.62 | 0.346 | matte 1 | 24.7 |
| depth_cam_87 | mppi_astar | glass_office | 16.7 | 83.3 | 0 | 0 | 5.58 | 0.145 | glass 4, matte 1 | 3.1 |
