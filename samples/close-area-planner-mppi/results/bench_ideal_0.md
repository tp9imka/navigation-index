`python bench.py --preset ideal --layouts 20 --seed 0 --workers 14` from samples/close-area-planner-mppi. Input: synthetic (simulated layouts, vehicle and sensor), scored on truth. Preset `ideal`, seed 0, 20 layouts per cell, 14 worker process(es), wall 99.1 s, Python 3.12.10, numpy 2.5.4, scipy 1.18.1, arm64 Darwin. Run time limit 60 s, 120 s for maze and warehouse. step ms = the whole planner.step() call (map update, ESDF, A* when due, MPPI) at 10 Hz; A* replan ms = the A* searches inside those steps. Timings were taken with 14 processes sharing the machine; see timing_0.md for one process.

Parity: astar_unknown runs identical to close-area-benchmark matrix_0.json (outcome, min clearance, path length): 160/160.

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | step ms median | step ms p95 | A* replan ms median | A* replan ms p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | random | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 19.01 | 23.96 | 0.615 | 0.65 | 63.58 | 24.99 | 77.41 |
| astar_unknown | u_trap | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 22.12 | 26.0 | 0.597 | 0.67 | 69.24 | 40.89 | 85.23 |
| astar_unknown | narrow_gap | 20 | 90.0 | 0.0 | 5.0 | 5.0 | 37.51 | 37.7 | 0.254 | 0.66 | 68.3 | 45.19 | 83.23 |
| astar_unknown | office | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 22.8 | 10.64 | 0.261 | 0.54 | 14.53 | 7.39 | 20.51 |
| astar_unknown | warehouse | 20 | 55.0 | 0.0 | 45.0 | 0.0 | 49.12 | 27.9 | 0.304 | 0.5 | 63.65 | 25.49 | 84.88 |
| astar_unknown | forest | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 23.31 | 24.17 | 0.603 | 0.7 | 68.94 | 29.98 | 85.28 |
| astar_unknown | maze | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 50.06 | 39.41 | 0.589 | 0.54 | 77.43 | 35.25 | 98.25 |
| astar_unknown | glass_office | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 30.34 | 14.42 | 0.273 | 0.58 | 17.14 | 7.83 | 32.69 |
| mppi_none | random | 20 | 90.0 | 0.0 | 10.0 | 0.0 | 20.35 | 23.94 | 0.45 | 4.11 | 8.16 | - | - |
| mppi_none | u_trap | 20 | 0.0 | 0.0 | 100.0 | 0.0 | - | 13.11 | 0.685 | 4.16 | 10.88 | - | - |
| mppi_none | narrow_gap | 20 | 25.0 | 0.0 | 75.0 | 0.0 | 22.76 | 20.42 | 0.561 | 3.96 | 8.85 | - | - |
| mppi_none | office | 20 | 25.0 | 0.0 | 75.0 | 0.0 | 8.4 | 2.65 | 0.579 | 3.8 | 8.7 | - | - |
| mppi_none | warehouse | 20 | 15.0 | 0.0 | 85.0 | 0.0 | 27.1 | 21.52 | 0.288 | 3.88 | 8.1 | - | - |
| mppi_none | forest | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 20.29 | 23.91 | 0.435 | 4.12 | 8.82 | - | - |
| mppi_none | maze | 20 | 0.0 | 0.0 | 100.0 | 0.0 | - | 8.67 | 0.382 | 3.91 | 16.55 | - | - |
| mppi_none | glass_office | 20 | 10.0 | 0.0 | 90.0 | 0.0 | 5.83 | 2.3 | 0.611 | 3.81 | 8.71 | - | - |
| mppi_astar | random | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 20.24 | 23.94 | 0.605 | 4.71 | 72.44 | 29.56 | 82.05 |
| mppi_astar | u_trap | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 21.93 | 25.82 | 0.471 | 4.78 | 80.06 | 39.8 | 94.59 |
| mppi_astar | narrow_gap | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 33.92 | 38.35 | 0.281 | 4.96 | 80.71 | 46.94 | 92.41 |
| mppi_astar | office | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 11.35 | 11.91 | 0.286 | 4.89 | 19.91 | 8.26 | 20.69 |
| mppi_astar | warehouse | 20 | 65.0 | 0.0 | 35.0 | 0.0 | 24.3 | 28.77 | 0.322 | 5.41 | 69.29 | 25.34 | 90.18 |
| mppi_astar | forest | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 20.4 | 24.08 | 0.563 | 4.98 | 78.88 | 30.95 | 100.94 |
| mppi_astar | maze | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 33.62 | 37.19 | 0.365 | 4.92 | 83.97 | 36.82 | 100.27 |
| mppi_astar | glass_office | 20 | 95.0 | 0.0 | 5.0 | 0.0 | 15.06 | 14.6 | 0.292 | 4.9 | 25.53 | 8.61 | 38.29 |

Per run (outcome, time to B s, min clearance m, path m):

| family | run | astar_unknown | mppi_none | mppi_astar |
|---|---|---|---|---|
| random | 0 | reached 18.7 0.6623 23.95 | reached 20.82 0.3409 24.051 | reached 20.24 0.5811 23.917 |
| random | 1 | reached 16.76 1.2564 23.974 | reached 20.32 1.2607 23.975 | reached 20.24 1.2634 23.973 |
| random | 2 | reached 18.38 0.6075 23.948 | reached 20.28 0.572 23.955 | reached 20.22 0.6379 23.954 |
| random | 3 | reached 21.62 0.6078 24.162 | stuck - 0.6351 7.886 | reached 20.44 0.5365 24.154 |
| random | 4 | reached 17.82 0.5875 23.673 | reached 20.12 0.4629 23.698 | reached 20.0 0.5917 23.681 |
| random | 5 | reached 20.56 0.636 23.983 | reached 20.46 0.383 24.007 | reached 20.28 0.6159 23.933 |
| random | 6 | reached 19.88 0.5865 24.743 | reached 21.24 0.3586 24.777 | reached 20.88 0.5864 24.745 |
| random | 7 | reached 19.84 0.5871 24.51 | reached 20.68 0.3589 24.36 | reached 20.6 0.5052 24.398 |
| random | 8 | reached 20.16 0.6162 23.538 | reached 20.98 0.3249 24.058 | reached 19.92 0.5781 23.523 |
| random | 9 | reached 16.72 0.7522 23.288 | reached 19.78 0.8437 23.299 | reached 19.7 0.7818 23.293 |
| random | 10 | reached 16.84 0.9321 23.919 | reached 20.26 1.0176 23.921 | reached 20.2 0.9718 23.918 |
| random | 11 | reached 20.08 0.5749 24.274 | reached 20.7 0.3874 24.227 | reached 20.52 0.5864 24.216 |
| random | 12 | reached 21.42 0.6132 24.055 | reached 20.24 0.2526 23.514 | reached 20.28 0.5565 23.992 |
| random | 13 | reached 21.88 0.4544 25.233 | reached 23.18 0.3125 25.609 | reached 21.26 0.4079 25.203 |
| random | 14 | reached 16.82 1.1604 24.063 | reached 20.38 1.1604 24.064 | reached 20.28 1.1604 24.06 |
| random | 15 | reached 17.9 0.6005 23.785 | reached 20.16 0.6874 23.798 | reached 20.08 0.6117 23.791 |
| random | 16 | reached 19.32 0.6056 24.556 | stuck - 0.4226 7.198 | reached 20.7 0.5987 24.558 |
| random | 17 | reached 17.06 0.7648 23.579 | reached 20.0 0.8342 23.583 | reached 19.92 0.7459 23.579 |
| random | 18 | reached 16.44 1.1991 23.49 | reached 19.94 1.1991 23.491 | reached 19.86 1.1991 23.486 |
| random | 19 | reached 20.08 0.655 23.909 | reached 20.42 0.4371 23.898 | reached 20.18 0.6245 23.856 |
| u_trap | 0 | reached 20.4 0.5485 25.225 | stuck - 0.6688 12.135 | reached 21.44 0.4473 25.281 |
| u_trap | 1 | reached 22.26 0.5963 27.437 | stuck - 0.6909 12.733 | reached 23.0 0.5121 27.069 |
| u_trap | 2 | reached 22.66 0.6004 27.649 | stuck - 0.6964 12.174 | reached 22.74 0.3714 26.572 |
| u_trap | 3 | reached 20.92 0.6044 26.331 | stuck - 0.6664 11.573 | reached 22.14 0.4655 25.89 |
| u_trap | 4 | reached 22.38 0.6292 26.731 | stuck - 0.6939 14.678 | reached 22.24 0.4417 26.106 |
| u_trap | 5 | reached 19.98 0.5671 25.341 | stuck - 0.6597 12.141 | reached 21.3 0.4995 25.165 |
| u_trap | 6 | reached 23.28 0.5972 26.778 | stuck - 0.6843 14.082 | reached 21.8 0.4395 25.759 |
| u_trap | 7 | reached 22.14 0.5959 25.909 | stuck - 0.3612 13.354 | reached 21.88 0.5811 25.801 |
| u_trap | 8 | reached 25.56 0.5983 27.312 | stuck - 0.6444 14.605 | reached 22.92 0.4589 26.847 |
| u_trap | 9 | reached 23.1 0.5764 25.921 | stuck - 0.5126 13.435 | reached 21.98 0.4709 25.845 |
| u_trap | 10 | reached 22.5 0.6061 27.811 | stuck - 0.6679 13.466 | reached 22.52 0.436 26.584 |
| u_trap | 11 | reached 22.1 0.6207 26.518 | stuck - 0.6903 12.546 | reached 22.5 0.4713 26.445 |
| u_trap | 12 | reached 23.5 0.5715 26.082 | stuck - 0.4477 14.346 | reached 21.98 0.4445 25.873 |
| u_trap | 13 | reached 22.14 0.5652 26.4 | stuck - 0.6983 13.037 | reached 22.36 0.4898 26.318 |
| u_trap | 14 | reached 20.52 0.6136 25.359 | stuck - 0.6923 12.976 | reached 21.74 0.5358 25.617 |
| u_trap | 15 | reached 20.66 0.6241 25.432 | stuck - 0.657 11.154 | reached 21.18 0.5062 24.975 |
| u_trap | 16 | reached 20.14 0.5173 24.94 | stuck - 0.7222 12.703 | reached 21.2 0.4762 25.031 |
| u_trap | 17 | reached 19.64 0.6074 24.604 | stuck - 0.6866 13.901 | reached 20.66 0.4924 24.423 |
| u_trap | 18 | reached 20.08 0.5898 24.842 | stuck - 0.6971 13.175 | reached 20.94 0.4687 24.725 |
| u_trap | 19 | reached 20.2 0.5803 25.311 | stuck - 0.6963 13.711 | reached 21.3 0.5419 25.111 |
| narrow_gap | 0 | reached 24.92 0.3286 25.19 | reached 21.96 0.2156 25.168 | reached 21.6 0.2651 25.194 |
| narrow_gap | 1 | reached 56.66 0.1882 66.29 | stuck - 0.3604 20.676 | reached 40.9 0.2602 44.321 |
| narrow_gap | 2 | reached 40.94 0.2805 46.448 | stuck - 0.432 21.711 | reached 41.04 0.2976 46.692 |
| narrow_gap | 3 | reached 24.9 0.2732 26.186 | reached 24.82 0.2319 26.501 | reached 22.24 0.2375 26.239 |
| narrow_gap | 4 | reached 50.42 0.2692 57.277 | stuck - 0.6604 20.329 | reached 41.82 0.2919 49.324 |
| narrow_gap | 5 | reached 40.6 0.2584 41.839 | stuck - 0.5447 19.954 | stuck - 0.6166 33.138 |
| narrow_gap | 6 | reached 40.82 0.2387 42.092 | stuck - 0.6152 20.074 | reached 37.14 0.3024 43.411 |
| narrow_gap | 7 | reached 33.64 0.2484 35.989 | stuck - 0.6069 19.866 | reached 35.32 0.27 39.098 |
| narrow_gap | 8 | reached 35.26 0.2504 35.21 | stuck - 0.629 20.978 | reached 30.04 0.2992 34.591 |
| narrow_gap | 9 | reached 44.58 0.2412 54.917 | stuck - 0.6057 19.853 | reached 42.78 0.298 49.773 |
| narrow_gap | 10 | reached 33.32 0.2249 36.092 | stuck - 0.6228 20.471 | reached 32.38 0.2937 37.593 |
| narrow_gap | 11 | stuck - 0.5824 23.606 | stuck - 0.2942 20.141 | reached 42.54 0.2708 50.353 |
| narrow_gap | 12 | reached 23.9 0.2414 23.636 | stuck - 0.5769 19.631 | reached 20.32 0.2698 23.661 |
| narrow_gap | 13 | reached 46.4 0.2935 51.6 | stuck - 0.6124 20.095 | reached 42.92 0.2947 50.253 |
| narrow_gap | 14 | reached 23.32 0.2712 25.156 | reached 22.76 0.2275 25.343 | reached 21.74 0.2534 25.144 |
| narrow_gap | 15 | reached 25.26 0.2745 27.15 | reached 27.48 0.217 27.55 | reached 23.78 0.2342 27.183 |
| narrow_gap | 16 | reached 39.76 0.2487 39.304 | stuck - 0.6512 19.74 | reached 33.92 0.295 39.741 |
| narrow_gap | 17 | timeout - 0.2333 42.466 | stuck - 0.4126 21.449 | reached 29.58 0.2176 31.897 |
| narrow_gap | 18 | reached 46.2 0.2672 52.393 | stuck - 0.6027 20.362 | reached 43.74 0.2993 51.362 |
| narrow_gap | 19 | reached 28.8 0.2252 24.678 | reached 21.64 0.2411 24.411 | reached 22.22 0.2704 24.369 |
| office | 0 | reached 22.0 0.2892 13.758 | stuck - 0.6477 2.813 | reached 12.78 0.313 13.881 |
| office | 1 | reached 18.2 0.2676 9.888 | stuck - 0.46 3.415 | reached 9.28 0.3277 10.065 |
| office | 2 | reached 24.56 0.2424 8.749 | reached 8.4 0.3007 6.999 | reached 9.04 0.2782 8.801 |
| office | 3 | reached 39.76 0.2314 16.99 | stuck - 0.6633 1.973 | reached 23.7 0.3079 15.973 |
| office | 4 | reached 30.22 0.2419 16.005 | stuck - 0.4344 3.369 | reached 14.78 0.259 16.067 |
| office | 5 | stuck - 0.2726 3.824 | stuck - 0.6526 1.833 | reached 20.14 0.2136 18.984 |
| office | 6 | reached 21.64 0.2757 13.295 | stuck - 0.6613 1.879 | reached 11.86 0.2718 13.242 |
| office | 7 | reached 29.88 0.2467 13.679 | stuck - 0.5521 2.489 | reached 12.86 0.2426 13.605 |
| office | 8 | reached 35.26 0.2281 12.751 | stuck - 0.6051 2.471 | reached 13.16 0.2717 13.271 |
| office | 9 | reached 14.92 0.2628 6.195 | reached 6.22 0.289 6.193 | reached 6.26 0.3313 6.211 |
| office | 10 | reached 25.92 0.2589 10.615 | reached 9.72 0.2949 10.162 | reached 9.42 0.2938 10.082 |
| office | 11 | reached 38.82 0.2446 15.24 | stuck - 0.6126 1.73 | reached 20.44 0.2447 20.023 |
| office | 12 | reached 20.72 0.2632 10.065 | stuck - 0.6745 1.701 | reached 10.1 0.3158 10.246 |
| office | 13 | reached 19.44 0.269 10.37 | stuck - 0.6775 2.317 | reached 9.8 0.3043 10.418 |
| office | 14 | reached 13.1 0.3132 5.783 | reached 5.74 0.3382 5.806 | reached 5.62 0.3425 5.785 |
| office | 15 | reached 22.8 0.25 10.659 | stuck - 0.6144 1.943 | reached 10.84 0.2754 11.081 |
| office | 16 | reached 27.9 0.2555 12.538 | stuck - 0.6295 2.279 | reached 15.18 0.2315 12.741 |
| office | 17 | reached 15.98 0.2659 6.993 | reached 8.78 0.2917 7.176 | reached 7.42 0.3107 7.1 |
| office | 18 | reached 25.18 0.2651 14.837 | stuck - 0.4777 3.203 | reached 14.66 0.3125 15.222 |
| office | 19 | reached 19.28 0.2537 7.428 | stuck - 0.4925 3.513 | reached 8.72 0.2619 7.975 |
| warehouse | 0 | reached 49.12 0.2939 27.268 | reached 27.1 0.2647 26.726 | reached 23.36 0.3255 26.966 |
| warehouse | 1 | reached 53.54 0.4536 35.37 | stuck - 0.5226 3.128 | reached 37.3 0.3269 40.732 |
| warehouse | 2 | stuck - 0.2401 31.92 | stuck - 0.3075 15.278 | stuck - 0.3358 28.708 |
| warehouse | 3 | reached 53.0 0.2782 27.984 | stuck - 0.3299 21.118 | reached 27.32 0.3373 27.416 |
| warehouse | 4 | reached 45.24 0.3035 27.763 | stuck - 0.3122 22.951 | reached 23.6 0.3157 26.88 |
| warehouse | 5 | reached 59.16 0.3419 36.833 | stuck - 0.281 23.006 | reached 30.54 0.2726 33.216 |
| warehouse | 6 | reached 39.5 0.2703 24.406 | stuck - 0.2979 22.167 | reached 21.68 0.2954 24.204 |
| warehouse | 7 | reached 36.88 0.4328 25.85 | stuck - 0.2789 19.393 | reached 22.1 0.3701 25.549 |
| warehouse | 8 | stuck - 0.2798 27.543 | stuck - 0.2835 19.233 | stuck - 0.3343 28.828 |
| warehouse | 9 | stuck - 0.356 29.092 | stuck - 0.2633 22.632 | reached 23.4 0.3289 26.643 |
| warehouse | 10 | reached 40.04 0.3957 25.874 | reached 25.96 0.2557 24.284 | reached 21.48 0.3204 24.417 |
| warehouse | 11 | stuck - 0.3036 27.819 | stuck - 0.2956 16.36 | stuck - 0.3449 32.647 |
| warehouse | 12 | stuck - 0.2809 28.009 | stuck - 0.2926 19.211 | stuck - 0.3059 33.246 |
| warehouse | 13 | reached 56.36 0.338 29.29 | reached 28.24 0.3073 27.64 | reached 27.48 0.2923 28.349 |
| warehouse | 14 | reached 66.48 0.2403 30.042 | stuck - 0.2838 7.999 | reached 51.92 0.2578 55.502 |
| warehouse | 15 | stuck - 0.3621 37.94 | stuck - 0.3125 21.932 | stuck - 0.3235 37.13 |
| warehouse | 16 | reached 45.18 0.2879 27.255 | stuck - 0.2814 22.935 | reached 24.3 0.3032 27.276 |
| warehouse | 17 | stuck - 0.246 27.292 | stuck - 0.2579 17.519 | stuck - 0.3123 32.17 |
| warehouse | 18 | stuck - 0.3482 44.053 | stuck - 0.262 27.254 | reached 43.7 0.3051 48.697 |
| warehouse | 19 | stuck - 0.3688 27.644 | stuck - 0.3213 15.894 | stuck - 0.3449 31.615 |
| forest | 0 | reached 23.8 0.6456 24.613 | reached 20.7 0.4102 24.5 | reached 20.76 0.5902 24.547 |
| forest | 1 | reached 22.3 0.6052 23.879 | reached 20.22 0.5186 23.915 | reached 20.16 0.5961 23.88 |
| forest | 2 | reached 21.22 0.6389 23.935 | reached 20.2 0.4789 23.808 | reached 20.26 0.5939 23.873 |
| forest | 3 | reached 26.78 0.5689 24.585 | reached 20.28 0.3975 23.847 | reached 20.7 0.5732 24.501 |
| forest | 4 | reached 22.28 0.6109 24.21 | reached 20.54 0.4768 24.138 | reached 20.44 0.5511 24.174 |
| forest | 5 | reached 20.48 0.6506 23.605 | reached 19.9 0.453 23.378 | reached 19.96 0.5969 23.501 |
| forest | 6 | reached 27.92 0.5657 25.44 | reached 20.56 0.368 24.308 | reached 21.16 0.5226 24.936 |
| forest | 7 | reached 22.16 0.5949 23.541 | reached 20.06 0.4313 23.494 | reached 19.92 0.6132 23.528 |
| forest | 8 | reached 23.46 0.6492 24.766 | reached 20.9 0.4392 24.624 | reached 20.9 0.6025 24.761 |
| forest | 9 | reached 25.36 0.5614 24.534 | reached 20.6 0.3761 24.269 | reached 20.74 0.5173 24.442 |
| forest | 10 | reached 29.68 0.5392 25.745 | reached 20.54 0.4168 24.225 | reached 20.7 0.446 24.27 |
| forest | 11 | reached 24.56 0.5649 24.179 | reached 20.4 0.4153 23.901 | reached 20.56 0.5521 24.226 |
| forest | 12 | reached 25.88 0.4671 23.442 | reached 19.9 0.4244 23.364 | reached 19.74 0.4824 23.31 |
| forest | 13 | reached 26.68 0.5767 25.173 | reached 20.26 0.388 23.903 | reached 20.94 0.48 24.586 |
| forest | 14 | reached 21.98 0.6316 24.687 | reached 21.0 0.4394 24.597 | reached 20.84 0.5979 24.639 |
| forest | 15 | reached 22.24 0.651 24.001 | reached 20.24 0.471 23.879 | reached 20.26 0.544 23.918 |
| forest | 16 | reached 20.0 0.6154 23.412 | reached 19.84 0.5589 23.399 | reached 19.78 0.6246 23.399 |
| forest | 17 | reached 19.58 0.6009 24.014 | reached 20.3 0.5656 23.983 | reached 20.22 0.5892 23.984 |
| forest | 18 | reached 23.16 0.5883 24.102 | reached 20.32 0.4274 23.939 | reached 20.36 0.536 23.986 |
| forest | 19 | reached 24.14 0.6159 24.161 | reached 19.9 0.4405 23.335 | reached 20.06 0.5379 23.541 |
| maze | 0 | reached 44.78 0.5911 37.733 | stuck - 0.6542 9.442 | reached 31.28 0.357 35.589 |
| maze | 1 | reached 33.76 0.6135 29.117 | stuck - 0.3732 22.425 | reached 24.4 0.4328 28.468 |
| maze | 2 | reached 51.2 0.5754 40.09 | stuck - 0.294 27.799 | reached 33.62 0.3497 37.266 |
| maze | 3 | reached 45.64 0.5802 36.057 | stuck - 0.3737 7.589 | reached 30.4 0.39 34.909 |
| maze | 4 | reached 49.08 0.582 39.391 | stuck - 0.4256 6.619 | reached 32.62 0.3719 37.123 |
| maze | 5 | reached 52.34 0.5948 41.59 | stuck - 0.4482 6.688 | reached 35.3 0.3744 39.003 |
| maze | 6 | stuck - 0.5763 35.303 | stuck - 0.3959 7.2 | stuck - 0.3888 36.312 |
| maze | 7 | reached 65.28 0.5682 52.224 | stuck - 0.4644 7.079 | reached 46.14 0.3519 52.45 |
| maze | 8 | reached 41.18 0.5828 33.058 | stuck - 0.3488 7.903 | reached 28.38 0.3836 32.18 |
| maze | 9 | reached 43.14 0.5844 36.155 | stuck - 0.6566 4.909 | reached 33.16 0.3561 36.925 |
| maze | 10 | reached 50.06 0.5883 39.428 | stuck - 0.3656 14.408 | reached 33.72 0.3627 37.336 |
| maze | 11 | reached 52.24 0.5861 45.043 | stuck - 0.3478 21.046 | reached 36.28 0.3754 41.909 |
| maze | 12 | reached 32.6 0.5944 29.897 | stuck - 0.369 13.512 | reached 25.0 0.4345 29.339 |
| maze | 13 | reached 62.56 0.5908 49.528 | stuck - 0.4552 4.156 | reached 42.34 0.3398 47.627 |
| maze | 14 | reached 38.44 0.6067 31.516 | stuck - 0.4097 12.382 | reached 26.48 0.4153 30.689 |
| maze | 15 | reached 54.76 0.5933 42.294 | stuck - 0.3873 11.35 | reached 35.28 0.3557 40.478 |
| maze | 16 | reached 99.58 0.5888 81.088 | stuck - 0.4866 3.675 | reached 90.56 0.3385 102.121 |
| maze | 17 | reached 56.46 0.5933 43.672 | stuck - 0.3388 18.033 | reached 39.7 0.3382 45.214 |
| maze | 18 | reached 39.42 0.5959 32.276 | stuck - 0.3281 24.095 | reached 30.48 0.3667 34.285 |
| maze | 19 | reached 56.3 0.5838 45.355 | stuck - 0.3767 6.699 | reached 38.38 0.3406 42.589 |
| glass_office | 0 | reached 38.86 0.307 25.679 | stuck - 0.3027 3.845 | reached 22.16 0.2578 24.394 |
| glass_office | 1 | reached 12.76 0.3462 5.744 | reached 5.62 0.4043 5.765 | reached 5.54 0.366 5.75 |
| glass_office | 2 | reached 17.9 0.274 5.989 | reached 6.04 0.3242 6.017 | reached 6.14 0.3258 6.001 |
| glass_office | 3 | reached 23.92 0.2716 13.433 | stuck - 0.6556 2.047 | reached 12.44 0.3404 13.208 |
| glass_office | 4 | reached 44.38 0.2388 30.508 | stuck - 0.6776 3.022 | reached 26.36 0.2828 29.782 |
| glass_office | 5 | reached 34.34 0.2475 12.033 | stuck - 0.6199 1.273 | reached 14.7 0.2329 13.036 |
| glass_office | 6 | reached 27.32 0.288 10.227 | stuck - 0.375 2.18 | reached 13.1 0.2567 11.681 |
| glass_office | 7 | reached 19.48 0.2719 7.683 | stuck - 0.6228 2.197 | reached 7.82 0.295 7.711 |
| glass_office | 8 | reached 27.44 0.3974 14.237 | stuck - 0.4623 2.553 | reached 13.12 0.3276 13.77 |
| glass_office | 9 | reached 34.56 0.2728 16.24 | stuck - 0.5139 2.646 | reached 15.98 0.3315 15.628 |
| glass_office | 10 | reached 30.34 0.2885 16.99 | stuck - 0.6531 2.575 | reached 15.06 0.3316 16.896 |
| glass_office | 11 | reached 47.64 0.2379 29.335 | stuck - 0.6433 1.379 | reached 28.24 0.2529 29.169 |
| glass_office | 12 | reached 40.02 0.2435 14.596 | stuck - 0.5269 2.334 | reached 23.04 0.2771 22.38 |
| glass_office | 13 | stuck - 0.275 4.242 | stuck - 0.6051 1.816 | stuck - 0.3152 7.939 |
| glass_office | 14 | reached 49.1 0.253 31.494 | stuck - 0.6174 2.684 | reached 22.6 0.2372 20.688 |
| glass_office | 15 | reached 45.64 0.2733 22.003 | stuck - 0.3876 3.983 | reached 20.64 0.3404 21.5 |
| glass_office | 16 | reached 20.64 0.2946 12.54 | stuck - 0.6281 1.961 | reached 11.1 0.3148 12.1 |
| glass_office | 17 | reached 20.48 0.2748 7.85 | stuck - 0.6519 1.96 | reached 7.98 0.2688 7.968 |
| glass_office | 18 | reached 39.88 0.2446 24.388 | stuck - 0.5966 2.258 | reached 21.32 0.2287 23.825 |
| glass_office | 19 | reached 28.9 0.252 15.353 | stuck - 0.666 1.305 | reached 15.34 0.29 15.438 |
