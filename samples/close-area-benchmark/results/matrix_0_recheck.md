`python bench.py --add-to matrix_0 --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite --recheck vfh_plus,astar_unknown --workers 14` from samples/close-area-benchmark. Input: synthetic. Existing rows re-run on the same 20 layouts x 8 families x 2 presets, seed 0, and compared run by run with results/matrix_0.json on outcome, min_clearance_m, path_length_m, time_to_goal_s.

| planner | runs identical |
|---|---|
| vfh_plus | 320/320 |
| astar_unknown | 320/320 |

Differences: 0

