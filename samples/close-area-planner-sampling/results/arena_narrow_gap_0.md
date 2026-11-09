`python bench.py --layouts 50 --seed 0 --iters 5000 --informed 1` from samples/close-area-planner-sampling (synthetic: simulated layouts, vehicle and sensor)

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | replans | plan median ms | plan p95 ms | fallback replans | no-path replans | wall s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_esdf known_map | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 24.23 | 0.276 | 3115 | 3.91 | 40.31 | 272 | 0 | 38.8 |
| informed_rrt_star iters=5000 | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 27.56 | 0.251 | 50 | 330.27 | 615.54 | 12 | 0 | 24.2 |

Per run (outcome, min clearance m, path m):

| run | astar_esdf known_map | informed_rrt_star iters=5000 |
|---|---|---|
| 0 | reached 0.3252 24.814 | reached 0.2697 24.697 |
| 1 | reached 0.2388 24.343 | reached 0.2373 24.227 |
| 2 | reached 0.2404 25.763 | reached 0.2443 25.717 |
| 3 | reached 0.2691 25.71 | reached 0.2378 25.635 |
| 4 | reached 0.3522 25.756 | reached 0.2752 25.406 |
| 5 | reached 0.3857 24.526 | reached 0.2685 24.294 |
| 6 | reached 0.2923 24.405 | reached 0.2455 24.293 |
| 7 | reached 0.2752 23.467 | reached 0.2709 23.433 |
| 8 | reached 0.2752 24.516 | reached 0.2204 24.148 |
| 9 | reached 0.3049 24.916 | reached 0.269 24.815 |
| 10 | reached 0.3001 23.843 | reached 0.2706 23.709 |
| 11 | reached 0.3432 24.54 | reached 0.2311 24.393 |
| 12 | reached 0.2392 23.523 | reached 0.2284 23.357 |
| 13 | reached 0.3292 24.605 | reached 0.309 24.512 |
| 14 | reached 0.2687 24.742 | reached 0.2542 24.711 |
| 15 | reached 0.2764 26.709 | reached 0.2547 26.644 |
| 16 | reached 0.2781 24.363 | reached 0.2536 24.111 |
| 17 | reached 0.2469 25.969 | reached 0.2492 24.049 |
| 18 | reached 0.3108 25.721 | reached 0.2957 25.531 |
| 19 | reached 0.231 24.036 | reached 0.2417 23.891 |
| 20 | reached 0.3999 25.455 | reached 0.2754 24.979 |
| 21 | reached 0.212 24.07 | reached 0.1959 23.953 |
| 22 | reached 0.2859 24.151 | reached 0.2114 24.053 |
| 23 | reached 0.279 26.585 | reached 0.2811 26.323 |
| 24 | reached 0.2844 24.462 | reached 0.2492 24.295 |
| 25 | reached 0.2538 24.5 | reached 0.2551 24.467 |
| 26 | reached 0.3262 24.582 | reached 0.2764 24.429 |
| 27 | reached 0.2328 25.682 | reached 0.2129 25.649 |
| 28 | reached 0.2965 24.358 | reached 0.2924 24.175 |
| 29 | reached 0.3137 26.258 | reached 0.2733 25.868 |
| 30 | reached 0.2536 26.009 | reached 0.1631 25.62 |
| 31 | reached 0.2695 23.841 | reached 0.1672 23.739 |
| 32 | reached 0.1839 24.838 | reached 0.1888 24.857 |
| 33 | reached 0.221 23.021 | reached 0.2225 23.014 |
| 34 | reached 0.1992 23.996 | reached 0.1941 23.99 |
| 35 | reached 0.2843 24.321 | reached 0.2648 24.143 |
| 36 | reached 0.2223 27.206 | reached 0.2225 27.068 |
| 37 | reached 0.2836 25.138 | reached 0.2894 26.357 |
| 38 | reached 0.2532 24.544 | reached 0.2612 24.519 |
| 39 | reached 0.3058 25.085 | reached 0.26 24.944 |
| 40 | reached 0.2042 24.537 | reached 0.2069 24.529 |
| 41 | reached 0.2342 25.345 | reached 0.235 25.336 |
| 42 | reached 0.3232 23.654 | reached 0.2713 23.445 |
| 43 | reached 0.2599 24.928 | reached 0.2522 24.831 |
| 44 | reached 0.1911 26.532 | reached 0.2197 26.583 |
| 45 | reached 0.2891 26.308 | reached 0.279 26.097 |
| 46 | reached 0.2371 24.781 | reached 0.2384 24.767 |
| 47 | reached 0.2803 24.427 | reached 0.2776 24.411 |
| 48 | reached 0.2757 26.562 | reached 0.1915 26.525 |
| 49 | reached 0.3044 23.506 | reached 0.2494 23.305 |
