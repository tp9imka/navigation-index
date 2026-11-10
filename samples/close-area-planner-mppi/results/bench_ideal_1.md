`python bench.py --seed 1 --layouts 10 --workers 14` from samples/close-area-planner-mppi. Input: synthetic (simulated layouts, vehicle and sensor), scored on truth. Preset `ideal`, seed 1, 10 layouts per cell, 14 worker process(es), wall 63.3 s, Python 3.12.10, numpy 2.5.4, scipy 1.18.1, arm64 Darwin. Run time limit 60 s, 120 s for maze and warehouse. step ms = the whole planner.step() call (map update, ESDF, A* when due, MPPI) at 10 Hz; A* replan ms = the A* searches inside those steps. Timings were taken with 14 processes sharing the machine; see timing_0.md for one process.

Parity: astar_unknown runs identical to close-area-benchmark matrix_0.json (outcome, min clearance, path length): 0/0.

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | step ms median | step ms p95 | A* replan ms median | A* replan ms p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | random | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 19.62 | 24.24 | 0.603 | 0.68 | 72.62 | 30.41 | 94.42 |
| astar_unknown | u_trap | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 22.3 | 26.52 | 0.591 | 0.7 | 73.37 | 44.93 | 93.77 |
| astar_unknown | narrow_gap | 10 | 50.0 | 10.0 | 40.0 | 0.0 | 25.58 | 25.14 | 0.257 | 0.7 | 72.75 | 45.23 | 90.48 |
| astar_unknown | office | 10 | 80.0 | 0.0 | 20.0 | 0.0 | 27.16 | 14.14 | 0.266 | 0.58 | 26.13 | 8.82 | 41.69 |
| astar_unknown | warehouse | 10 | 90.0 | 0.0 | 10.0 | 0.0 | 50.82 | 28.87 | 0.272 | 0.52 | 70.66 | 28.74 | 88.75 |
| astar_unknown | forest | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 25.74 | 24.48 | 0.6 | 0.72 | 71.71 | 31.05 | 89.0 |
| astar_unknown | maze | 10 | 50.0 | 0.0 | 50.0 | 0.0 | 71.24 | 39.08 | 0.586 | 0.56 | 85.39 | 47.3 | 103.07 |
| astar_unknown | glass_office | 10 | 90.0 | 0.0 | 10.0 | 0.0 | 25.02 | 13.08 | 0.248 | 0.6 | 15.71 | 8.1 | 22.98 |
| mppi_none | random | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 20.59 | 24.14 | 0.47 | 4.23 | 8.81 | - | - |
| mppi_none | u_trap | 10 | 0.0 | 0.0 | 100.0 | 0.0 | - | 13.32 | 0.691 | 4.0 | 9.58 | - | - |
| mppi_none | narrow_gap | 10 | 20.0 | 0.0 | 80.0 | 0.0 | 24.16 | 20.31 | 0.598 | 3.95 | 8.83 | - | - |
| mppi_none | office | 10 | 10.0 | 0.0 | 90.0 | 0.0 | 11.84 | 3.07 | 0.567 | 3.77 | 8.78 | - | - |
| mppi_none | warehouse | 10 | 10.0 | 0.0 | 90.0 | 0.0 | 33.92 | 24.8 | 0.291 | 3.8 | 8.06 | - | - |
| mppi_none | forest | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 20.32 | 23.88 | 0.399 | 4.08 | 8.35 | - | - |
| mppi_none | maze | 10 | 0.0 | 0.0 | 100.0 | 0.0 | - | 5.55 | 0.41 | 3.93 | 8.3 | - | - |
| mppi_none | glass_office | 10 | 0.0 | 0.0 | 100.0 | 0.0 | - | 1.94 | 0.627 | 3.96 | 8.8 | - | - |
| mppi_astar | random | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 20.43 | 24.18 | 0.583 | 4.8 | 77.75 | 29.31 | 99.94 |
| mppi_astar | u_trap | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 22.23 | 26.14 | 0.446 | 4.77 | 78.71 | 43.48 | 88.74 |
| mppi_astar | narrow_gap | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 34.1 | 33.74 | 0.255 | 5.0 | 76.72 | 45.3 | 87.88 |
| mppi_astar | office | 10 | 90.0 | 0.0 | 10.0 | 0.0 | 15.56 | 16.54 | 0.295 | 5.03 | 34.8 | 9.95 | 41.24 |
| mppi_astar | warehouse | 10 | 90.0 | 0.0 | 10.0 | 0.0 | 25.06 | 27.45 | 0.297 | 5.0 | 77.99 | 29.1 | 95.56 |
| mppi_astar | forest | 10 | 100.0 | 0.0 | 0.0 | 0.0 | 20.69 | 24.38 | 0.565 | 5.07 | 80.12 | 29.88 | 93.75 |
| mppi_astar | maze | 10 | 50.0 | 0.0 | 40.0 | 10.0 | 33.94 | 36.03 | 0.367 | 4.92 | 87.01 | 46.58 | 99.84 |
| mppi_astar | glass_office | 10 | 80.0 | 0.0 | 20.0 | 0.0 | 17.56 | 14.55 | 0.284 | 5.0 | 21.86 | 8.44 | 24.6 |

Per run (outcome, time to B s, min clearance m, path m):

| family | run | astar_unknown | mppi_none | mppi_astar |
|---|---|---|---|---|
| random | 0 | reached 16.44 1.26 23.493 | reached 19.94 1.2724 23.492 | reached 19.86 1.2688 23.491 |
| random | 1 | reached 24.92 0.4607 24.266 | reached 20.74 0.357 24.194 | reached 20.44 0.393 24.191 |
| random | 2 | reached 19.46 0.5817 23.629 | reached 20.02 0.7044 23.65 | reached 19.94 0.6053 23.63 |
| random | 3 | reached 19.26 0.6038 24.647 | reached 20.84 0.6119 24.652 | reached 20.76 0.6722 24.654 |
| random | 4 | reached 21.5 0.6016 24.216 | reached 20.44 0.4595 24.091 | reached 20.42 0.5693 24.169 |
| random | 5 | reached 19.78 0.605 24.383 | reached 20.78 0.3918 24.316 | reached 20.6 0.5877 24.384 |
| random | 6 | reached 21.28 0.5995 24.66 | reached 21.04 0.4299 24.619 | reached 20.8 0.578 24.638 |
| random | 7 | reached 21.0 0.6081 24.491 | reached 21.08 0.3875 24.486 | reached 20.66 0.54 24.447 |
| random | 8 | reached 18.3 0.6855 23.52 | reached 19.92 0.481 23.488 | reached 19.84 0.6026 23.49 |
| random | 9 | reached 17.76 0.5998 23.495 | reached 19.94 0.5485 23.501 | reached 19.9 0.5633 23.497 |
| u_trap | 0 | reached 21.9 0.5658 26.947 | stuck - 0.6549 12.706 | reached 22.38 0.4407 26.258 |
| u_trap | 1 | reached 22.24 0.6083 27.45 | stuck - 0.6606 13.375 | reached 22.34 0.4284 26.363 |
| u_trap | 2 | reached 20.62 0.6046 24.959 | stuck - 0.6993 12.873 | reached 21.02 0.5082 24.836 |
| u_trap | 3 | reached 22.6 0.6145 27.889 | stuck - 0.6779 13.81 | reached 23.46 0.4343 27.543 |
| u_trap | 4 | reached 22.38 0.5773 27.054 | stuck - 0.6572 13.799 | reached 22.62 0.4118 26.631 |
| u_trap | 5 | reached 22.36 0.6082 26.43 | stuck - 0.7256 14.373 | reached 22.2 0.4314 26.181 |
| u_trap | 6 | reached 23.98 0.5578 26.183 | stuck - 0.7295 13.272 | reached 22.26 0.4543 26.103 |
| u_trap | 7 | reached 22.54 0.6038 26.156 | stuck - 0.7051 13.216 | reached 22.08 0.4507 25.853 |
| u_trap | 8 | reached 22.18 0.5725 25.937 | stuck - 0.6819 14.733 | reached 22.02 0.4892 25.883 |
| u_trap | 9 | reached 21.42 0.5749 26.616 | stuck - 0.7095 12.02 | reached 22.08 0.4676 25.884 |
| narrow_gap | 0 | reached 31.1 0.2651 33.535 | stuck - 0.6047 20.643 | reached 33.2 0.2513 32.608 |
| narrow_gap | 1 | reached 24.68 0.2839 24.26 | reached 20.52 0.2826 24.068 | reached 20.58 0.2723 24.14 |
| narrow_gap | 2 | collision - 0.1486 17.215 | stuck - 0.6258 20.417 | reached 21.12 0.2517 24.184 |
| narrow_gap | 3 | stuck - 0.9718 26.01 | stuck - 0.6382 20.478 | reached 41.96 0.3306 49.079 |
| narrow_gap | 4 | reached 36.38 0.2397 40.591 | stuck - 0.6232 20.212 | reached 37.86 0.2374 41.611 |
| narrow_gap | 5 | reached 25.58 0.3013 27.509 | reached 27.8 0.2429 27.954 | reached 23.36 0.2285 27.425 |
| narrow_gap | 6 | stuck - 0.2481 23.291 | stuck - 0.5111 15.674 | reached 44.66 0.2676 51.965 |
| narrow_gap | 7 | stuck - 0.1997 35.367 | stuck - 0.6258 19.672 | reached 47.06 0.2577 43.962 |
| narrow_gap | 8 | stuck - 0.2252 16.829 | stuck - 0.5917 19.901 | reached 35.0 0.1975 34.871 |
| narrow_gap | 9 | reached 25.46 0.3102 24.211 | stuck - 0.4699 20.106 | reached 20.78 0.2647 24.247 |
| office | 0 | reached 26.86 0.248 16.908 | stuck - 0.6228 1.624 | reached 15.56 0.2949 17.104 |
| office | 1 | reached 27.46 0.2905 18.76 | stuck - 0.6717 3.487 | reached 16.58 0.2633 18.713 |
| office | 2 | reached 40.42 0.2658 29.61 | stuck - 0.6545 2.305 | reached 25.84 0.2733 28.941 |
| office | 3 | reached 16.48 0.2612 7.089 | stuck - 0.423 4.855 | reached 6.9 0.3255 7.163 |
| office | 4 | reached 18.08 0.3219 9.732 | stuck - 0.6504 1.978 | reached 8.86 0.3072 9.298 |
| office | 5 | reached 26.2 0.2667 11.716 | reached 11.84 0.2893 10.93 | reached 11.86 0.2959 12.33 |
| office | 6 | stuck - 0.2651 5.379 | stuck - 0.5318 2.151 | stuck - 0.2489 6.844 |
| office | 7 | reached 39.8 0.3145 23.136 | stuck - 0.4035 6.19 | reached 20.44 0.3008 22.369 |
| office | 8 | stuck - 0.2526 4.629 | stuck - 0.3333 4.404 | reached 15.8 0.2451 16.528 |
| office | 9 | reached 29.48 0.2772 16.557 | stuck - 0.6013 2.651 | reached 14.9 0.3183 16.543 |
| warehouse | 0 | reached 52.88 0.2275 26.688 | stuck - 0.3363 14.535 | reached 23.66 0.326 26.37 |
| warehouse | 1 | reached 61.68 0.2676 29.434 | stuck - 0.2599 26.008 | reached 24.56 0.2693 27.793 |
| warehouse | 2 | reached 60.86 0.2495 33.665 | stuck - 0.2954 24.794 | reached 31.3 0.2445 34.326 |
| warehouse | 3 | reached 48.8 0.276 24.786 | stuck - 0.2866 22.701 | reached 21.78 0.3083 24.675 |
| warehouse | 4 | reached 49.48 0.3618 32.87 | stuck - 0.3152 21.641 | reached 30.02 0.3106 32.453 |
| warehouse | 5 | reached 50.32 0.2905 27.115 | stuck - 0.2595 25.061 | reached 25.06 0.3136 27.116 |
| warehouse | 6 | reached 37.34 0.3764 28.299 | stuck - 0.2744 24.802 | reached 23.0 0.2852 26.346 |
| warehouse | 7 | reached 93.5 0.261 58.388 | reached 33.92 0.2127 29.363 | reached 27.06 0.275 31.229 |
| warehouse | 8 | reached 50.82 0.3126 33.676 | stuck - 0.3188 27.694 | reached 30.22 0.3341 33.359 |
| warehouse | 9 | stuck - 0.2461 25.333 | stuck - 0.3088 15.933 | stuck - 0.2417 24.548 |
| forest | 0 | reached 21.94 0.6095 23.478 | reached 20.06 0.3864 23.457 | reached 19.9 0.5952 23.446 |
| forest | 1 | reached 25.52 0.5536 25.311 | reached 20.46 0.4724 24.23 | reached 21.34 0.5391 25.122 |
| forest | 2 | reached 28.26 0.5684 24.752 | reached 21.04 0.428 24.68 | reached 20.94 0.5101 24.7 |
| forest | 3 | reached 25.96 0.587 24.751 | reached 20.4 0.469 24.275 | reached 20.92 0.6027 24.764 |
| forest | 4 | reached 26.56 0.6292 24.676 | reached 20.78 0.3226 24.305 | reached 20.8 0.5862 24.573 |
| forest | 5 | reached 27.28 0.5968 25.521 | reached 20.24 0.3744 23.841 | reached 21.6 0.531 25.217 |
| forest | 6 | reached 21.68 0.6205 23.236 | reached 19.76 0.3883 23.185 | reached 19.76 0.5922 23.271 |
| forest | 7 | reached 22.48 0.6189 23.419 | reached 19.8 0.3822 23.199 | reached 19.82 0.4844 23.38 |
| forest | 8 | reached 26.28 0.6027 24.287 | reached 20.4 0.4102 23.911 | reached 20.58 0.6094 24.197 |
| forest | 9 | reached 24.0 0.5893 23.702 | reached 20.1 0.4883 23.609 | reached 19.98 0.5431 23.625 |
| maze | 0 | reached 71.24 0.5845 56.515 | stuck - 0.3907 3.867 | reached 47.86 0.357 54.454 |
| maze | 1 | stuck - 0.5874 49.397 | stuck - 0.4522 8.3 | timeout - 0.3561 136.48 |
| maze | 2 | stuck - 0.5886 34.586 | stuck - 0.4119 3.834 | stuck - 0.3302 36.411 |
| maze | 3 | reached 73.22 0.5911 61.757 | stuck - 0.4021 5.494 | stuck - 0.3529 25.769 |
| maze | 4 | reached 43.78 0.5938 34.947 | stuck - 0.4081 5.934 | reached 31.1 0.3905 35.493 |
| maze | 5 | stuck - 0.5716 31.476 | stuck - 0.3916 3.94 | stuck - 0.3544 31.676 |
| maze | 6 | reached 55.32 0.5591 43.214 | stuck - 0.6309 5.602 | reached 31.46 0.3764 35.659 |
| maze | 7 | stuck - 0.5634 34.754 | stuck - 0.3825 6.31 | stuck - 0.431 24.846 |
| maze | 8 | stuck - 0.5983 25.604 | stuck - 0.4336 3.664 | reached 33.94 0.3887 39.054 |
| maze | 9 | reached 80.02 0.5504 62.943 | stuck - 0.4366 8.213 | reached 56.62 0.3813 63.195 |
| glass_office | 0 | reached 25.02 0.2414 17.205 | stuck - 0.6624 1.57 | reached 16.16 0.2711 17.209 |
| glass_office | 1 | reached 39.92 0.2477 13.859 | stuck - 0.3008 3.786 | reached 18.96 0.2827 14.391 |
| glass_office | 2 | reached 18.92 0.2265 9.707 | stuck - 0.6684 1.268 | reached 9.46 0.3128 9.507 |
| glass_office | 3 | stuck - 0.2877 6.377 | stuck - 0.5369 2.108 | stuck - 0.2697 7.015 |
| glass_office | 4 | reached 24.86 0.2715 8.638 | stuck - 0.324 5.841 | reached 8.56 0.2854 8.577 |
| glass_office | 5 | reached 25.0 0.2586 14.748 | stuck - 0.6306 1.495 | reached 13.48 0.2555 14.712 |
| glass_office | 6 | reached 33.0 0.2229 12.297 | stuck - 0.6226 1.308 | reached 21.42 0.2612 20.463 |
| glass_office | 7 | reached 21.1 0.2333 6.931 | stuck - 0.6358 2.315 | stuck - 0.3173 3.444 |
| glass_office | 8 | reached 51.38 0.2783 32.302 | stuck - 0.3039 6.698 | reached 27.8 0.2967 31.312 |
| glass_office | 9 | reached 35.58 0.249 26.0 | stuck - 0.664 1.773 | reached 25.5 0.2877 26.737 |
