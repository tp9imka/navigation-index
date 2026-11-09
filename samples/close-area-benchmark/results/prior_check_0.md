`python bench.py --planners astar_unknown_prior,astar_unknown --families office,warehouse,glass_office --presets ideal --stem prior_check_0` from samples/close-area-benchmark. Input: synthetic (simulated layouts, vehicle and sensors). Scored on truth. Seed 0, 20 layouts per cell, 14 worker processes, wall 28.6 s. Run time limit per family (s): office 60, warehouse 120, glass_office 60.

Not in this checkout, to add: close-area-planner-dwa-bug (DWA, Bug2); close-area-planner-dstar (D* Lite)

### Preset `ideal`

Cell = reached % / collision % (20 layouts unless stated).

| planner | office | warehouse | glass_office |
|---|---|---|---|
| astar_unknown_prior | 15 / 0 | 70 / 0 | 25 / 0 |
| astar_unknown | 95 / 0 | 55 / 0 | 95 / 0 |

Best planner per family (reached / collision %): office => astar_unknown (95 / 0); warehouse => astar_unknown_prior (70 / 0); glass_office => astar_unknown (95 / 0)

Best without a prior map (astar_known, informed_rrt_star, astar_mpc excluded): office => astar_unknown (95 / 0); warehouse => astar_unknown_prior (70 / 0); glass_office => astar_unknown (95 / 0)

### All fields

| preset | planner | family | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | collisions by material | sum of run wall s |
|---|---|---|---|---|---|---|---|---|---|---|
| ideal | astar_unknown_prior | office | 15 | 0 | 85 | 0 | 30.76 | 0.913 | - | 11.7 |
| ideal | astar_unknown_prior | warehouse | 70 | 0 | 30 | 0 | 48.33 | 0.285 | - | 120.8 |
| ideal | astar_unknown_prior | glass_office | 25 | 0 | 75 | 0 | 25.82 | 0.824 | - | 14.1 |
| ideal | astar_unknown | office | 95 | 0 | 5 | 0 | 22.8 | 0.261 | - | 15.6 |
| ideal | astar_unknown | warehouse | 55 | 0 | 45 | 0 | 49.12 | 0.304 | - | 102 |
| ideal | astar_unknown | glass_office | 95 | 0 | 5 | 0 | 30.34 | 0.273 | - | 24.6 |
