`python bench.py --layouts 50 --seed 0` in samples/close-area-planner-mpc (synthetic: simulated layouts, vehicle and sensor), wall 381.9 s, arm64 Darwin, Python 3.11.15, numpy 2.4.6, osqp 1.1.3

| follower | family | layouts | reached % | collision % | stuck % | timeout % | median min clearance m | worst min clearance m | tracking err median / p95 m | vs t=0 path median / p95 m | step ms median / p95 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| astar_carrot | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.635 | 0.5447 | 0.018 / 0.053 | 0.041 / 0.457 | 0.059 / 5.157 |
| astar_mpc | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.637 | 0.5506 | 0.017 / 0.054 | 0.052 / 0.484 | 1.001 / 5.896 |
| astar_mpc_cold | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.637 | 0.5504 | 0.017 / 0.055 | 0.052 / 0.474 | 1.479 / 6.39 |
| astar_mpc_nocorridor | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.637 | 0.5506 | 0.017 / 0.054 | 0.052 / 0.484 | 1.027 / 6.143 |
| astar_mpc_fast | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.63 | 0.5441 | 0.02 / 0.053 | 0.057 / 0.466 | 1.013 / 6.249 |
| astar_mpc_fast_nocorridor | random | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.63 | 0.5441 | 0.02 / 0.053 | 0.057 / 0.466 | 1.019 / 6.397 |
| astar_carrot | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.276 | 0.1839 | 0.021 / 0.053 | 0.057 / 0.393 | 0.06 / 20.569 |
| astar_mpc | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.304 | 0.1794 | 0.019 / 0.053 | 0.063 / 0.386 | 1.106 / 22.712 |
| astar_mpc_cold | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.303 | 0.1798 | 0.019 / 0.053 | 0.063 / 0.379 | 1.596 / 23.651 |
| astar_mpc_nocorridor | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.304 | 0.1794 | 0.019 / 0.053 | 0.063 / 0.382 | 1.106 / 23.109 |
| astar_mpc_fast | narrow_gap | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0.284 | 0.1727 | 0.021 / 0.055 | 0.049 / 0.295 | 1.052 / 23.492 |
| astar_mpc_fast_nocorridor | narrow_gap | 50 | 98.0 | 2.0 | 0.0 | 0.0 | 0.284 | 0.149 | 0.021 / 0.054 | 0.049 / 0.304 | 1.055 / 23.68 |

MPC solver (per planner step; QP = wall time of OSQP update + solve; step = replan + reference + corridor + QP):

| follower | family | steps | QP ms median / p95 / max | OSQP solve_time ms median / p95 | corridor ms median / p95 | iterations median / p95 | not solved | slack > 1 cm at k=1 | steps with an active obstacle plane | truncated corridors |
|---|---|---|---|---|---|---|---|---|---|---|
| astar_mpc | random | 9113 | 0.213 / 0.448 / 7.981 | 0.13 / 0.363 | 0.454 / 0.856 | 25.0 / 75.0 | 0 | 0 | 0 | 0 |
| astar_mpc_cold | random | 9103 | 0.717 / 0.865 / 5.453 | 0.643 / 0.779 | 0.456 / 0.863 | 125.0 / 150.0 | 0 | 0 | 0 | 0 |
| astar_mpc_nocorridor | random | 9113 | 0.22 / 0.456 / 8.445 | 0.132 / 0.373 | 0.464 / 0.88 | 25.0 / 75.0 | 0 | 0 | 0 | 0 |
| astar_mpc_fast | random | 9079 | 0.222 / 0.464 / 4.28 | 0.133 / 0.377 | 0.426 / 0.869 | 25.0 / 75.0 | 0 | 0 | 0 | 0 |
| astar_mpc_fast_nocorridor | random | 9079 | 0.223 / 0.463 / 4.273 | 0.133 / 0.377 | 0.425 / 0.876 | 25.0 / 75.0 | 0 | 0 | 0 | 0 |
| astar_mpc | narrow_gap | 11161 | 0.222 / 0.464 / 9.311 | 0.132 / 0.358 | 0.587 / 0.888 | 25.0 / 50.0 | 0 | 14 | 163 | 0 |
| astar_mpc_cold | narrow_gap | 11163 | 0.733 / 1.036 / 29.237 | 0.649 / 0.914 | 0.597 / 0.901 | 125.0 / 175.0 | 0 | 15 | 159 | 0 |
| astar_mpc_nocorridor | narrow_gap | 11153 | 0.224 / 0.473 / 13.877 | 0.132 / 0.359 | 0.588 / 0.892 | 25.0 / 50.0 | 0 | 0 | 0 | 0 |
| astar_mpc_fast | narrow_gap | 9454 | 0.22 / 0.482 / 10.007 | 0.131 / 0.381 | 0.437 / 0.856 | 25.0 / 75.0 | 0 | 2 | 135 | 0 |
| astar_mpc_fast_nocorridor | narrow_gap | 9378 | 0.22 / 0.477 / 5.75 | 0.132 / 0.38 | 0.439 / 0.854 | 25.0 / 75.0 | 0 | 0 | 0 | 0 |

Per run, random (outcome, min clearance m):

| run | astar_carrot | astar_mpc | astar_mpc_cold | astar_mpc_nocorridor | astar_mpc_fast | astar_mpc_fast_nocorridor |
|---|---|---|---|---|---|---|
| 0 | reached 0.5647 | reached 0.5985 | reached 0.595 | reached 0.5985 | reached 0.5815 | reached 0.5815 |
| 1 | reached 1.2564 | reached 1.2447 | reached 1.2447 | reached 1.2447 | reached 1.2093 | reached 1.2093 |
| 2 | reached 0.6739 | reached 0.6863 | reached 0.6863 | reached 0.6863 | reached 0.6741 | reached 0.6741 |
| 3 | reached 0.6144 | reached 0.6218 | reached 0.6219 | reached 0.6218 | reached 0.6261 | reached 0.6261 |
| 4 | reached 0.5976 | reached 0.5852 | reached 0.5849 | reached 0.5852 | reached 0.5759 | reached 0.5759 |
| 5 | reached 0.6517 | reached 0.6537 | reached 0.6377 | reached 0.6537 | reached 0.6711 | reached 0.6711 |
| 6 | reached 0.6146 | reached 0.6282 | reached 0.6282 | reached 0.6282 | reached 0.626 | reached 0.626 |
| 7 | reached 0.6847 | reached 0.6621 | reached 0.6619 | reached 0.6621 | reached 0.6096 | reached 0.6096 |
| 8 | reached 0.6308 | reached 0.6272 | reached 0.627 | reached 0.6272 | reached 0.6245 | reached 0.6245 |
| 9 | reached 0.7522 | reached 0.7782 | reached 0.7782 | reached 0.7782 | reached 0.7518 | reached 0.7518 |
| 10 | reached 0.9321 | reached 0.9209 | reached 0.9209 | reached 0.9209 | reached 0.9881 | reached 0.9881 |
| 11 | reached 0.5861 | reached 0.5714 | reached 0.5714 | reached 0.5714 | reached 0.5778 | reached 0.5778 |
| 12 | reached 0.622 | reached 0.6059 | reached 0.6059 | reached 0.6059 | reached 0.6255 | reached 0.6254 |
| 13 | reached 0.6261 | reached 0.6124 | reached 0.6337 | reached 0.6124 | reached 0.6442 | reached 0.6442 |
| 14 | reached 1.1604 | reached 1.1604 | reached 1.1604 | reached 1.1604 | reached 1.1604 | reached 1.1604 |
| 15 | reached 0.6046 | reached 0.6022 | reached 0.6022 | reached 0.6022 | reached 0.5978 | reached 0.5978 |
| 16 | reached 0.6347 | reached 0.6356 | reached 0.6353 | reached 0.6356 | reached 0.665 | reached 0.665 |
| 17 | reached 0.7632 | reached 0.7049 | reached 0.7049 | reached 0.7049 | reached 0.7075 | reached 0.7076 |
| 18 | reached 1.1991 | reached 1.1991 | reached 1.1991 | reached 1.1991 | reached 1.1991 | reached 1.1991 |
| 19 | reached 0.6074 | reached 0.6282 | reached 0.6281 | reached 0.6282 | reached 0.6405 | reached 0.6405 |
| 20 | reached 0.6222 | reached 0.6373 | reached 0.6373 | reached 0.6373 | reached 0.6221 | reached 0.6221 |
| 21 | reached 0.6462 | reached 0.6471 | reached 0.6468 | reached 0.6471 | reached 0.7102 | reached 0.7102 |
| 22 | reached 0.628 | reached 0.6364 | reached 0.633 | reached 0.6364 | reached 0.6569 | reached 0.6569 |
| 23 | reached 0.6163 | reached 0.6523 | reached 0.6523 | reached 0.6523 | reached 0.605 | reached 0.605 |
| 24 | reached 1.1526 | reached 1.1526 | reached 1.1526 | reached 1.1526 | reached 1.1526 | reached 1.1526 |
| 25 | reached 0.6051 | reached 0.6012 | reached 0.6011 | reached 0.6012 | reached 0.5965 | reached 0.5965 |
| 26 | reached 0.6376 | reached 0.6448 | reached 0.6447 | reached 0.6448 | reached 0.6403 | reached 0.6403 |
| 27 | reached 0.5997 | reached 0.6014 | reached 0.6014 | reached 0.6014 | reached 0.5984 | reached 0.5984 |
| 28 | reached 0.6403 | reached 0.6448 | reached 0.6447 | reached 0.6448 | reached 0.6671 | reached 0.6671 |
| 29 | reached 0.8434 | reached 0.8431 | reached 0.8431 | reached 0.8431 | reached 0.8433 | reached 0.8433 |
| 30 | reached 0.6407 | reached 0.6471 | reached 0.647 | reached 0.6471 | reached 0.6272 | reached 0.6272 |
| 31 | reached 0.8186 | reached 0.8692 | reached 0.8692 | reached 0.8692 | reached 0.5977 | reached 0.5977 |
| 32 | reached 0.595 | reached 0.5578 | reached 0.5578 | reached 0.5578 | reached 0.6074 | reached 0.6074 |
| 33 | reached 0.6303 | reached 0.6221 | reached 0.5951 | reached 0.6221 | reached 0.6307 | reached 0.6307 |
| 34 | reached 0.6757 | reached 0.6722 | reached 0.6722 | reached 0.6722 | reached 0.6294 | reached 0.6294 |
| 35 | reached 0.5757 | reached 0.5703 | reached 0.5702 | reached 0.5703 | reached 0.5664 | reached 0.5664 |
| 36 | reached 0.6667 | reached 0.6495 | reached 0.6483 | reached 0.6495 | reached 0.6429 | reached 0.6429 |
| 37 | reached 0.6005 | reached 0.6001 | reached 0.6004 | reached 0.6001 | reached 0.598 | reached 0.599 |
| 38 | reached 0.6402 | reached 0.6459 | reached 0.6459 | reached 0.6459 | reached 0.6436 | reached 0.6436 |
| 39 | reached 0.6387 | reached 0.6362 | reached 0.6837 | reached 0.6362 | reached 0.6621 | reached 0.6621 |
| 40 | reached 0.6176 | reached 0.5993 | reached 0.598 | reached 0.5993 | reached 0.5969 | reached 0.5969 |
| 41 | reached 0.6235 | reached 0.6267 | reached 0.6267 | reached 0.6267 | reached 0.643 | reached 0.643 |
| 42 | reached 0.6662 | reached 0.6447 | reached 0.6754 | reached 0.6447 | reached 0.6762 | reached 0.6762 |
| 43 | reached 0.5447 | reached 0.5506 | reached 0.5504 | reached 0.5506 | reached 0.5441 | reached 0.5441 |
| 44 | reached 0.6173 | reached 0.6197 | reached 0.6197 | reached 0.6197 | reached 0.6155 | reached 0.6155 |
| 45 | reached 0.6361 | reached 0.6054 | reached 0.605 | reached 0.6054 | reached 0.5745 | reached 0.5745 |
| 46 | reached 0.6522 | reached 0.6373 | reached 0.6372 | reached 0.6373 | reached 0.6396 | reached 0.6395 |
| 47 | reached 0.6478 | reached 0.6437 | reached 0.6437 | reached 0.6437 | reached 0.6139 | reached 0.6139 |
| 48 | reached 0.5968 | reached 0.5996 | reached 0.6004 | reached 0.5996 | reached 0.6005 | reached 0.6005 |
| 49 | reached 0.6606 | reached 0.6439 | reached 0.6439 | reached 0.6439 | reached 0.644 | reached 0.644 |

Per run, narrow_gap (outcome, min clearance m):

| run | astar_carrot | astar_mpc | astar_mpc_cold | astar_mpc_nocorridor | astar_mpc_fast | astar_mpc_fast_nocorridor |
|---|---|---|---|---|---|---|
| 0 | reached 0.3252 | reached 0.3302 | reached 0.3302 | reached 0.3302 | reached 0.3199 | reached 0.3199 |
| 1 | reached 0.2388 | reached 0.2633 | reached 0.2633 | reached 0.2633 | reached 0.2067 | reached 0.2067 |
| 2 | reached 0.2404 | reached 0.2946 | reached 0.2948 | reached 0.2946 | reached 0.2644 | reached 0.2644 |
| 3 | reached 0.2691 | reached 0.3105 | reached 0.3111 | reached 0.3105 | reached 0.2967 | reached 0.2967 |
| 4 | reached 0.3522 | reached 0.396 | reached 0.396 | reached 0.396 | reached 0.378 | reached 0.378 |
| 5 | reached 0.3857 | reached 0.4138 | reached 0.4113 | reached 0.4138 | reached 0.3956 | reached 0.3956 |
| 6 | reached 0.2923 | reached 0.3775 | reached 0.3773 | reached 0.3775 | reached 0.3692 | reached 0.3692 |
| 7 | reached 0.2752 | reached 0.2903 | reached 0.2919 | reached 0.2903 | reached 0.2791 | reached 0.2791 |
| 8 | reached 0.2752 | reached 0.3648 | reached 0.3651 | reached 0.3648 | reached 0.3683 | reached 0.3683 |
| 9 | reached 0.3049 | reached 0.3635 | reached 0.361 | reached 0.3635 | reached 0.3557 | reached 0.3557 |
| 10 | reached 0.3001 | reached 0.3431 | reached 0.3436 | reached 0.3431 | reached 0.3597 | reached 0.3597 |
| 11 | reached 0.3432 | reached 0.3452 | reached 0.3531 | reached 0.3452 | reached 0.388 | reached 0.388 |
| 12 | reached 0.2392 | reached 0.3509 | reached 0.3503 | reached 0.3509 | reached 0.3179 | reached 0.3179 |
| 13 | reached 0.3292 | reached 0.4153 | reached 0.4153 | reached 0.4153 | reached 0.4113 | reached 0.4113 |
| 14 | reached 0.2687 | reached 0.3212 | reached 0.321 | reached 0.3212 | reached 0.2994 | reached 0.2996 |
| 15 | reached 0.2764 | reached 0.2718 | reached 0.2779 | reached 0.2718 | reached 0.2592 | reached 0.2592 |
| 16 | reached 0.2781 | reached 0.3335 | reached 0.3335 | reached 0.3335 | reached 0.3346 | reached 0.3346 |
| 17 | reached 0.2469 | reached 0.2385 | reached 0.2452 | reached 0.2385 | reached 0.264 | reached 0.264 |
| 18 | reached 0.3108 | reached 0.3747 | reached 0.3749 | reached 0.3747 | reached 0.3509 | reached 0.3509 |
| 19 | reached 0.231 | reached 0.2966 | reached 0.2332 | reached 0.2966 | reached 0.2185 | reached 0.2185 |
| 20 | reached 0.3999 | reached 0.391 | reached 0.3924 | reached 0.391 | reached 0.4234 | reached 0.4234 |
| 21 | reached 0.212 | reached 0.21 | reached 0.2122 | reached 0.21 | reached 0.1909 | reached 0.1677 |
| 22 | reached 0.2859 | reached 0.2822 | reached 0.2863 | reached 0.2822 | reached 0.2717 | reached 0.2717 |
| 23 | reached 0.279 | reached 0.2888 | reached 0.2587 | reached 0.2888 | reached 0.2582 | reached 0.2579 |
| 24 | reached 0.2844 | reached 0.3437 | reached 0.3448 | reached 0.3437 | reached 0.3411 | reached 0.3411 |
| 25 | reached 0.2538 | reached 0.2704 | reached 0.2697 | reached 0.2704 | reached 0.2439 | reached 0.2439 |
| 26 | reached 0.3262 | reached 0.35 | reached 0.3523 | reached 0.35 | reached 0.3965 | reached 0.3965 |
| 27 | reached 0.2328 | reached 0.2377 | reached 0.232 | reached 0.2377 | reached 0.2148 | reached 0.1764 |
| 28 | reached 0.2965 | reached 0.3982 | reached 0.397 | reached 0.3982 | reached 0.3785 | reached 0.3785 |
| 29 | reached 0.3137 | reached 0.3351 | reached 0.3423 | reached 0.3351 | reached 0.3152 | reached 0.3152 |
| 30 | reached 0.2536 | reached 0.2554 | reached 0.26 | reached 0.2554 | reached 0.2467 | reached 0.2467 |
| 31 | reached 0.2695 | reached 0.2597 | reached 0.2652 | reached 0.2597 | reached 0.2747 | reached 0.2747 |
| 32 | reached 0.1839 | reached 0.1794 | reached 0.1798 | reached 0.1794 | reached 0.1727 | collision 0.149 |
| 33 | reached 0.221 | reached 0.2234 | reached 0.2275 | reached 0.2148 | reached 0.2096 | reached 0.1786 |
| 34 | reached 0.1992 | reached 0.2115 | reached 0.2147 | reached 0.2075 | reached 0.1994 | reached 0.176 |
| 35 | reached 0.2843 | reached 0.4087 | reached 0.4092 | reached 0.4087 | reached 0.3733 | reached 0.3734 |
| 36 | reached 0.2223 | reached 0.261 | reached 0.2556 | reached 0.201 | reached 0.2302 | reached 0.2276 |
| 37 | reached 0.2836 | reached 0.2848 | reached 0.2862 | reached 0.2848 | reached 0.2885 | reached 0.2885 |
| 38 | reached 0.2532 | reached 0.2805 | reached 0.2715 | reached 0.2805 | reached 0.2466 | reached 0.2466 |
| 39 | reached 0.3058 | reached 0.4064 | reached 0.4034 | reached 0.4064 | reached 0.3932 | reached 0.3932 |
| 40 | reached 0.2042 | reached 0.1957 | reached 0.1966 | reached 0.194 | reached 0.192 | reached 0.1851 |
| 41 | reached 0.2342 | reached 0.2491 | reached 0.2553 | reached 0.2491 | reached 0.2087 | reached 0.2087 |
| 42 | reached 0.3232 | reached 0.4104 | reached 0.4103 | reached 0.4104 | reached 0.403 | reached 0.403 |
| 43 | reached 0.2599 | reached 0.2581 | reached 0.259 | reached 0.2581 | reached 0.2383 | reached 0.2383 |
| 44 | reached 0.1911 | reached 0.2216 | reached 0.2272 | reached 0.185 | reached 0.2241 | reached 0.2241 |
| 45 | reached 0.2891 | reached 0.3777 | reached 0.383 | reached 0.3777 | reached 0.3658 | reached 0.3658 |
| 46 | reached 0.2371 | reached 0.2752 | reached 0.2736 | reached 0.2752 | reached 0.2478 | reached 0.2478 |
| 47 | reached 0.2803 | reached 0.2921 | reached 0.2933 | reached 0.2921 | reached 0.2726 | reached 0.2726 |
| 48 | reached 0.2757 | reached 0.315 | reached 0.3151 | reached 0.315 | reached 0.2652 | reached 0.2652 |
| 49 | reached 0.3044 | reached 0.4092 | reached 0.4117 | reached 0.4092 | reached 0.4049 | reached 0.4049 |

Plot: [mpc_narrow_gap_0_run32.png](mpc_narrow_gap_0_run32.png), narrow_gap run 32 (narrow_gap run with the smallest carrot min clearance). Carrot reached, MPC reached. Orange = MPC corridor polytopes at t = 10.8 s.
