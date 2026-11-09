`python clearance.py` over results/sweep_0.json (synthetic, planning only). Level 0.25 = planned at ESDF > 0.25 m; level 0.15 = the RADIUS-only fallback.

| planner | budget | inflation level m | ok plans | exact clearance < 0.15 m | % | min exact clearance m |
|---|---|---|---|---|---|---|
| astar | - | 0.25 | 150 | 0 | 0.0 | 0.220 |
| astar | - | 0.15 | 60 | 17 | 28.3 | 0.119 |
| informed_rrt_star | 1000 | 0.25 | 1066 | 0 | 0.0 | 0.211 |
| informed_rrt_star | 1000 | 0.15 | 616 | 57 | 9.3 | 0.110 |
| informed_rrt_star | 5000 | 0.25 | 1467 | 0 | 0.0 | 0.211 |
| informed_rrt_star | 5000 | 0.15 | 588 | 35 | 6.0 | 0.113 |
| rrt_star | 1000 | 0.25 | 1066 | 0 | 0.0 | 0.213 |
| rrt_star | 1000 | 0.15 | 616 | 69 | 11.2 | 0.116 |
| rrt_star | 5000 | 0.25 | 1467 | 0 | 0.0 | 0.211 |
| rrt_star | 5000 | 0.15 | 588 | 57 | 9.7 | 0.113 |
