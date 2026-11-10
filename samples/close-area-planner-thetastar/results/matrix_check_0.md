`python bench.py check`. Input: synthetic. A* rows of results/flights_0.json against close-area-benchmark/results/matrix_0.json, run by run on outcome, min_clearance_m, path_length_m, time_to_goal_s.

| planner | preset | runs identical |
|---|---|---|
| astar_unknown | ideal | 160/160 |
| astar_known | ideal | 160/160 |
| astar_unknown | crazyflie | 40/40 |
