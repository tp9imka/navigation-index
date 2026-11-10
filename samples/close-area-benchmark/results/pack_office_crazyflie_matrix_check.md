`python pack.py check-matrix results/pack_office_crazyflie.json`. Input: synthetic. Seed-0 runs of the pack (no jitter) on family layouts, against results/matrix_0.json (preset crazyflie, same layout index).

Pack runs vs matrix: 15/15 same outcome with min clearance within 0.2 mm (the world JSON rounds coordinates to 0.1 mm). fly() on the unrounded layouts: 15/15 identical outcome and min clearance.

| planner | world | matrix outcome, min clearance m | pack run (world JSON, 0.1 mm) | fly() on the unrounded layout |
|---|---|---|---|---|
| astar_known | office #0 | reached, 0.2996 | reached, 0.2997 ok | reached, 0.2996 identical |
| astar_known | office #1 | reached, 0.2805 | reached, 0.2805 ok | reached, 0.2805 identical |
| astar_known | office #2 | reached, 0.25 | reached, 0.25 ok | reached, 0.25 identical |
| astar_unknown | office #0 | stuck, 0.2448 | stuck, 0.2447 ok | stuck, 0.2448 identical |
| astar_unknown | office #1 | stuck, 0.2668 | stuck, 0.2667 ok | stuck, 0.2668 identical |
| astar_unknown | office #2 | reached, 0.3208 | reached, 0.3208 ok | reached, 0.3208 identical |
| astar_unknown_f2 | office #0 | reached, 0.3321 | reached, 0.3321 ok | reached, 0.3321 identical |
| astar_unknown_f2 | office #1 | stuck, 0.3228 | stuck, 0.3228 ok | stuck, 0.3228 identical |
| astar_unknown_f2 | office #2 | reached, 0.3521 | reached, 0.3522 ok | reached, 0.3521 identical |
| lazy_thetastar_unknown | office #0 | collision, 0.1428 | collision, 0.1428 ok | collision, 0.1428 identical |
| lazy_thetastar_unknown | office #1 | collision, 0.1425 | collision, 0.1425 ok | collision, 0.1425 identical |
| lazy_thetastar_unknown | office #2 | reached, 0.3151 | reached, 0.3151 ok | reached, 0.3151 identical |
| dwa_mem | office #0 | stuck, 0.2328 | stuck, 0.2328 ok | stuck, 0.2328 identical |
| dwa_mem | office #1 | stuck, 0.2895 | stuck, 0.2895 ok | stuck, 0.2895 identical |
| dwa_mem | office #2 | stuck, 0.2736 | stuck, 0.2736 ok | stuck, 0.2736 identical |
