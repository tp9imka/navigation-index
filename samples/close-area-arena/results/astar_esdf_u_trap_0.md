`python -m planners.astar_esdf --layouts 50 --seed 0` from samples/close-area-arena (synthetic: simulated layouts, vehicle and sensor)

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | replans | plan median ms | plan p95 ms | fallback replans | no-path replans | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| straight | u_trap | 50 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.383 | 0 | - | - | 0 | 0 | 3.5 |
| astar_esdf known_map | u_trap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 19.04 | 0.621 | 2451 | 1.47 | 15.08 | 0 | 0 | 14.9 |
| astar_esdf unknown_map | u_trap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 22.11 | 0.595 | 2826 | 32.94 | 60.2 | 0 | 0 | 97.3 |

Per run (outcome, min clearance m):

| run | straight | astar_esdf known_map | astar_esdf unknown_map |
|---|---|---|---|
| 0 | stuck 0.383 | reached 0.601 | reached 0.6123 |
| 1 | stuck 0.3754 | reached 0.6399 | reached 0.6093 |
| 2 | stuck 0.3795 | reached 0.6227 | reached 0.5795 |
| 3 | stuck 0.3854 | reached 0.6225 | reached 0.5896 |
| 4 | stuck 0.3829 | reached 0.6729 | reached 0.6271 |
| 5 | stuck 0.3859 | reached 0.6301 | reached 0.6233 |
| 6 | stuck 0.3849 | reached 0.6382 | reached 0.573 |
| 7 | stuck 0.4067 | reached 0.674 | reached 0.5967 |
| 8 | stuck 0.3704 | reached 0.573 | reached 0.6006 |
| 9 | stuck 0.3906 | reached 0.5862 | reached 0.6318 |
| 10 | stuck 0.3827 | reached 0.6164 | reached 0.5965 |
| 11 | stuck 0.379 | reached 0.5967 | reached 0.6099 |
| 12 | stuck 0.3829 | reached 0.6107 | reached 0.5689 |
| 13 | stuck 0.3749 | reached 0.6169 | reached 0.576 |
| 14 | stuck 0.3746 | reached 0.6664 | reached 0.5829 |
| 15 | stuck 0.3862 | reached 0.6069 | reached 0.5435 |
| 16 | stuck 0.3775 | reached 0.5874 | reached 0.5713 |
| 17 | stuck 0.3836 | reached 0.6203 | reached 0.5945 |
| 18 | stuck 0.3838 | reached 0.5935 | reached 0.6288 |
| 19 | stuck 0.3802 | reached 0.5801 | reached 0.5994 |
| 20 | stuck 0.3825 | reached 0.6297 | reached 0.6268 |
| 21 | stuck 0.3846 | reached 0.6414 | reached 0.6066 |
| 22 | stuck 0.3839 | reached 0.6103 | reached 0.5665 |
| 23 | stuck 0.3852 | reached 0.6309 | reached 0.5843 |
| 24 | stuck 0.4056 | reached 0.6244 | reached 0.5921 |
| 25 | stuck 0.3844 | reached 0.623 | reached 0.5962 |
| 26 | stuck 0.3883 | reached 0.6288 | reached 0.6066 |
| 27 | stuck 0.4038 | reached 0.604 | reached 0.5842 |
| 28 | stuck 0.3819 | reached 0.6136 | reached 0.5933 |
| 29 | stuck 0.3708 | reached 0.6449 | reached 0.5961 |
| 30 | stuck 0.3731 | reached 0.6132 | reached 0.5882 |
| 31 | stuck 0.3751 | reached 0.5999 | reached 0.5778 |
| 32 | stuck 0.381 | reached 0.5861 | reached 0.5872 |
| 33 | stuck 0.3845 | reached 0.6305 | reached 0.6227 |
| 34 | stuck 0.3857 | reached 0.6098 | reached 0.6332 |
| 35 | stuck 0.3794 | reached 0.5811 | reached 0.6246 |
| 36 | stuck 0.3866 | reached 0.625 | reached 0.5529 |
| 37 | stuck 0.3885 | reached 0.6515 | reached 0.6163 |
| 38 | stuck 0.386 | reached 0.5848 | reached 0.5932 |
| 39 | stuck 0.3784 | reached 0.6421 | reached 0.5379 |
| 40 | stuck 0.3821 | reached 0.6296 | reached 0.6037 |
| 41 | stuck 0.3825 | reached 0.609 | reached 0.6287 |
| 42 | stuck 0.3809 | reached 0.6199 | reached 0.584 |
| 43 | stuck 0.3801 | reached 0.609 | reached 0.6074 |
| 44 | stuck 0.3829 | reached 0.6869 | reached 0.5691 |
| 45 | stuck 0.3862 | reached 0.6345 | reached 0.5818 |
| 46 | stuck 0.385 | reached 0.6748 | reached 0.5523 |
| 47 | stuck 0.3826 | reached 0.619 | reached 0.4429 |
| 48 | stuck 0.385 | reached 0.6813 | reached 0.6116 |
| 49 | stuck 0.3776 | reached 0.6374 | reached 0.6025 |

Plot: [astar_esdf_u_trap_0_run0.png](astar_esdf_u_trap_0_run0.png), run 0 (first run the unknown-map mode did not reach B, else run 0). Panels left to right: straight, astar_esdf known_map, astar_esdf unknown_map. Blue = truth path, green = last planned path, grey band = 0.15 m inflation, orange = stuck, magenta = collision, purple = timeout.


Notes (written by hand after the run, synthetic): both modes reach B in all 50 layouts; the unknown-map mode enters the cup, sees its walls and replans out, which costs about 3 s of median time to goal (22.11 s vs 19.04 s). Planner constants were tuned on seed-0 layouts 0-9 of random and narrow_gap, so the numbers are not held-out.
