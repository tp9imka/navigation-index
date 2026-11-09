`python compare.py verify --layouts 50 --seed 0` (synthetic). At every replan of each D* Lite flight, A* from scratch ran on the same frozen blocked / cost arrays and the same start cell. Cost = sum of step length x cost of the entered cell.

| family | searches | both found a path | found / not found mismatch | invalid D* path | D* costlier than A* | (A* - D*) / D* max | median | abs(g(start) - D* path cost) max |
|---|---|---|---|---|---|---|---|---|
| random | 2391 | 2391 | 0 | 0 | 0 | 8.62e-16 | 0.00e+00 | 1.25e-12 |
| u_trap | 2822 | 2822 | 0 | 0 | 0 | 7.54e-16 | 0.00e+00 | 9.66e-13 |
| narrow_gap | 4804 | 4651 | 0 | 0 | 0 | 7.30e-16 | 0.00e+00 | 5.00e-12 |

A* pushes f = g + 1.0001 h (tie-break in astar_esdf.astar), so it may return a path up to 0.01 % costlier than optimal; D* Lite uses the plain octile h. A positive (A* - D*) gap below 1e-4 is that tie-break.
