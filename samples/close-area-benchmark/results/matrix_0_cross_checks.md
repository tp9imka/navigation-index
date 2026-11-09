`python bench.py --cross-check matrix_0`. Input: synthetic. Rows of results/matrix_0.json (preset ideal) vs close-area-planner-dwa-bug/results/dwa_bug_0.json (fan default, run.evaluate, seed 0) on random, u_trap and narrow_gap, same layout indices. Same = identical outcome and min clearance.

| planner | runs same |
|---|---|
| dwa | 60/60 |
| dwa_mem | 60/60 |
| bug2 | 60/60 |
| tangent_bug | 60/60 |

Differences: 0

dstar_lite vs astar_unknown (same geofence, same map and cost model, incremental search), runs with the same outcome, and mean planner step time over all runs of the preset (ms; 14 processes in parallel, not a clean timing):

| preset | same outcome | astar_unknown mean step ms | dstar_lite mean step ms |
|---|---|---|---|
| ideal | 153/160 | 10.7 | 4.2 |
| crazyflie | 115/160 | 13.42 | 2.92 |
