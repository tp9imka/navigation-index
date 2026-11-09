`python bench.py --layouts 50 --seed 0 --iters 5000 --informed 1` from samples/close-area-planner-sampling (synthetic: simulated layouts, vehicle and sensor)

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | replans | plan median ms | plan p95 ms | fallback replans | no-path replans | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_esdf known_map | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 18.81 | 0.635 | 2379 | 1.26 | 10.98 | 0 | 0 | 11.8 |
| informed_rrt_star iters=5000 | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 23.58 | 0.269 | 50 | 466.94 | 612.76 | 0 | 0 | 29.4 |

Per run (outcome, min clearance m, path m):

| run | astar_esdf known_map | informed_rrt_star iters=5000 |
|---|---|---|
| 0 | reached 0.5647 23.838 | reached 0.2211 23.551 |
| 1 | reached 1.2564 23.974 | reached 1.2535 23.971 |
| 2 | reached 0.6739 23.951 | reached 0.3787 23.94 |
| 3 | reached 0.6144 23.975 | reached 0.2677 23.728 |
| 4 | reached 0.5976 23.642 | reached 0.2242 23.592 |
| 5 | reached 0.6517 23.921 | reached 0.286 23.749 |
| 6 | reached 0.6146 24.655 | reached 0.2529 24.426 |
| 7 | reached 0.6847 24.456 | reached 0.3027 24.241 |
| 8 | reached 0.6308 23.542 | reached 0.286 23.25 |
| 9 | reached 0.7522 23.288 | reached 0.7688 23.291 |
| 10 | reached 0.9321 23.919 | reached 0.9253 23.915 |
| 11 | reached 0.5861 24.127 | reached 0.2496 23.94 |
| 12 | reached 0.622 24.045 | reached 0.2808 23.759 |
| 13 | reached 0.6261 25.8 | reached 0.2595 24.716 |
| 14 | reached 1.1604 24.063 | reached 1.1604 24.053 |
| 15 | reached 0.6046 23.785 | reached 0.4705 23.777 |
| 16 | reached 0.6347 24.56 | reached 0.2673 24.39 |
| 17 | reached 0.7632 23.577 | reached 0.7312 23.57 |
| 18 | reached 1.1991 23.49 | reached 1.1991 23.478 |
| 19 | reached 0.6074 23.718 | reached 0.2697 23.619 |
| 20 | reached 0.6222 24.44 | reached 0.2734 23.78 |
| 21 | reached 0.6462 23.436 | reached 0.3048 23.366 |
| 22 | reached 0.628 24.389 | reached 0.2854 24.099 |
| 23 | reached 0.6163 23.767 | reached 0.266 23.705 |
| 24 | reached 1.1526 23.73 | reached 1.1526 23.721 |
| 25 | reached 0.6051 24.474 | reached 0.2654 24.04 |
| 26 | reached 0.6376 25.279 | reached 0.251 24.383 |
| 27 | reached 0.5997 23.716 | reached 0.2808 23.65 |
| 28 | reached 0.6403 23.269 | reached 0.2591 23.159 |
| 29 | reached 0.8434 24.087 | reached 0.8428 24.084 |
| 30 | reached 0.6407 24.323 | reached 0.2298 23.961 |
| 31 | reached 0.8186 24.026 | reached 0.789 24.016 |
| 32 | reached 0.595 24.372 | reached 0.2828 24.353 |
| 33 | reached 0.6303 23.983 | reached 0.2436 23.881 |
| 34 | reached 0.6757 23.402 | reached 0.2698 23.313 |
| 35 | reached 0.5757 25.174 | reached 0.2542 24.891 |
| 36 | reached 0.6667 23.818 | reached 0.2815 23.723 |
| 37 | reached 0.6005 23.903 | reached 0.2556 23.874 |
| 38 | reached 0.6402 24.802 | reached 0.2835 24.713 |
| 39 | reached 0.6387 24.044 | reached 0.2687 23.987 |
| 40 | reached 0.6176 23.771 | reached 0.2535 23.604 |
| 41 | reached 0.6235 23.918 | reached 0.2513 23.756 |
| 42 | reached 0.6662 24.937 | reached 0.2495 24.448 |
| 43 | reached 0.5447 23.993 | reached 0.2049 23.859 |
| 44 | reached 0.6173 23.338 | reached 0.383 23.332 |
| 45 | reached 0.6361 23.916 | reached 0.2268 23.858 |
| 46 | reached 0.6522 23.913 | reached 0.248 23.572 |
| 47 | reached 0.6478 24.485 | reached 0.2468 24.27 |
| 48 | reached 0.5968 22.989 | reached 0.2575 22.921 |
| 49 | reached 0.6606 24.009 | reached 0.2638 23.931 |
