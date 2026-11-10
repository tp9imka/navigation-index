`python bench.py plans --layouts 20 --seed 0 --repeats 3` from samples/close-area-planner-thetastar. Input: synthetic. One plan from A to B on the known prior grid per layout, seed 0, 20 layouts per family, 3 repeats per plan (ms = median of the repeats), single process, wall 121.5 s. Load average at start [255.1, 169.8, 108.5], at end [99.8, 142.3, 106.2] (shared machine). Plan ms = the planner's whole _plan (cost arrays, search, shortcut for A*), ESDF cached. Cost = thetastar.path_cost of the planned polyline in metres x cost (same scale for all three). Clearance = world.sdf every 2 cm along the planned polyline.

| family | planner | plan ms median | plan ms p95 | plan ms max | ms ratio median | length median m | length ratio median | shorter | cost median | cost ratio median | cheaper | clearance median m | clearance min m | fallback plans |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | astar_shortcut | 8.04 | 18.31 | 27.35 | - | 24.33 | - | - | 27.21 | - | - | 0.64 | 0.556 | 0 |
| random | thetastar | 55.4 | 192.91 | 204.34 | 8.23 | 24.38 | 1 | 5 | 24.58 | 0.925 | 17 | 0.96 | 0.814 | 0 |
| random | lazy_thetastar | 36.97 | 142.71 | 146.25 | 6.5 | 24.4 | 1.001 | 4 | 24.61 | 0.925 | 17 | 0.972 | 0.814 | 0 |
| u_trap | astar_shortcut | 15.35 | 22.05 | 22.08 | - | 25.41 | - | - | 27.79 | - | - | 0.619 | 0.589 | 0 |
| u_trap | thetastar | 114.95 | 165.06 | 167.54 | 7.31 | 25.43 | 1.001 | 6 | 25.41 | 0.916 | 20 | 0.978 | 0.936 | 0 |
| u_trap | lazy_thetastar | 81.66 | 109.91 | 112.94 | 4.86 | 25.43 | 1.001 | 6 | 25.41 | 0.918 | 20 | 0.972 | 0.923 | 0 |
| narrow_gap | astar_shortcut | 25.19 | 36.17 | 36.56 | - | 25.25 | - | - | 31 | - | - | 0.353 | 0.223 | 0 |
| narrow_gap | thetastar | 229.48 | 304.33 | 352.21 | 8.43 | 25.48 | 1.005 | 3 | 29.21 | 0.946 | 20 | 0.353 | 0.254 | 0 |
| narrow_gap | lazy_thetastar | 175.83 | 213.01 | 244.45 | 6.15 | 25.46 | 1.006 | 2 | 29.23 | 0.946 | 20 | 0.353 | 0.25 | 0 |
| office | astar_shortcut | 10.84 | 17.05 | 22.89 | - | 11.86 | - | - | 24.7 | - | - | 0.38 | 0.279 | 0 |
| office | thetastar | 52.52 | 163.61 | 173.99 | 4.61 | 12.21 | 1.029 | 1 | 20.87 | 0.837 | 20 | 0.377 | 0.26 | 0 |
| office | lazy_thetastar | 33.03 | 75.92 | 89.31 | 3.04 | 12.26 | 1.03 | 1 | 20.91 | 0.837 | 20 | 0.372 | 0.256 | 0 |
| warehouse | astar_shortcut | 32.01 | 39.75 | 44.01 | - | 35.99 | - | - | 70.12 | - | - | 0.574 | 0.45 | 0 |
| warehouse | thetastar | 137.05 | 213.17 | 231.92 | 4.78 | 36.41 | 1.012 | 0 | 43.63 | 0.665 | 20 | 0.657 | 0.45 | 0 |
| warehouse | lazy_thetastar | 92.22 | 147.95 | 149.21 | 2.98 | 36.43 | 1.013 | 0 | 43.64 | 0.665 | 20 | 0.657 | 0.45 | 0 |
| forest | astar_shortcut | 15.68 | 48.14 | 57.42 | - | 25.01 | - | - | 32.55 | - | - | 0.635 | 0.59 | 0 |
| forest | thetastar | 80.34 | 193.03 | 220.66 | 4.09 | 25.24 | 1.012 | 2 | 25.7 | 0.8 | 20 | 0.949 | 0.617 | 0 |
| forest | lazy_thetastar | 47.59 | 118.24 | 153.56 | 2.78 | 25.26 | 1.014 | 2 | 25.78 | 0.802 | 20 | 0.946 | 0.623 | 0 |
| maze | astar_shortcut | 57.18 | 85.87 | 96.58 | - | 38.56 | - | - | 65.7 | - | - | 0.593 | 0.572 | 0 |
| maze | thetastar | 152.87 | 234.45 | 237.94 | 2.64 | 39.96 | 1.045 | 0 | 43.71 | 0.697 | 20 | 0.671 | 0.572 | 0 |
| maze | lazy_thetastar | 90.91 | 131.55 | 132.03 | 1.5 | 40.01 | 1.045 | 0 | 43.74 | 0.698 | 20 | 0.671 | 0.572 | 0 |
| glass_office | astar_shortcut | 14.27 | 39.02 | 40.63 | - | 13.66 | - | - | 30.66 | - | - | 0.317 | 0.25 | 0 |
| glass_office | thetastar | 62.12 | 386.96 | 424.2 | 3.97 | 14.22 | 1.037 | 0 | 25.76 | 0.876 | 20 | 0.314 | 0.244 | 0 |
| glass_office | lazy_thetastar | 38.16 | 190.92 | 214.09 | 2.69 | 14.27 | 1.038 | 0 | 25.85 | 0.878 | 20 | 0.296 | 0.241 | 0 |
| all | astar_shortcut | 18.41 | 63.44 | 96.58 | - | 25.06 | - | - | 31.25 | - | - | 0.582 | 0.223 | 0 |
| all | thetastar | 118.38 | 265.7 | 424.2 | 5.51 | 25.17 | 1.012 | 17 | 26.24 | 0.855 | 157 | 0.655 | 0.244 | 0 |
| all | lazy_thetastar | 72.59 | 183.95 | 244.45 | 3.46 | 25.18 | 1.013 | 15 | 26.32 | 0.859 | 157 | 0.653 | 0.241 | 0 |

Ratios are medians of per-layout ratios Theta* / A* + shortcut (ms ratio: same layout, same process, a few ms apart, so less sensitive to machine load than the absolute ms); shorter / cheaper = layouts where the ratio is < 1.
