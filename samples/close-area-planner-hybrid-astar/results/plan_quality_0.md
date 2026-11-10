`python plan_quality.py --layouts 20 --seed 0` from samples/close-area-planner-hybrid-astar, single process, wall 13.3 s. Input: synthetic (arena layouts, known prior grid). One plan from A per layout, 20 layouts per family.

Medians over layouts. rad/m = heading change per metre at 0.25 m spacing. share > k = share of joints with heading change above 0.67 rad/m (1.0 rad/s at 1.5 m/s). Time stock / turn1 = minimum rest-to-rest time along the path at |v| <= 1.5, |a| <= 3, lateral <= 3 m/s^2, turn1 adds turn rate <= 1.0 rad/s (metrics.py). Min sdf = exact clearance of the path centre line (vehicle radius 0.15 m).

| family | planner | found % | plan ms median / p95 | path m | max rad/m | p95 rad/m | share > k | total turn rad | time stock s | time turn1 s | min sdf m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| random | astar_esdf | 100 | 7.76 / 17.96 | 24.33 | 1.321 | 0 | 0.015 | 0.592 | 16.725 | 17.23 | 0.64 |
| random | hybrid_astar | 100 | 6.78 / 8.45 | 24.618 | 0.735 | 0.585 | 0.026 | 2.413 | 16.995 | 17.195 | 0.79 |
| u_trap | astar_esdf | 100 | 16.31 / 23.3 | 25.407 | 1.804 | 0 | 0.02 | 0.754 | 17.59 | 17.96 | 0.62 |
| u_trap | hybrid_astar | 100 | 7.26 / 7.71 | 26.025 | 1.457 | 0.661 | 0.044 | 4.383 | 17.945 | 18.2 | 0.864 |
| narrow_gap | astar_esdf | 100 | 25.73 / 35.75 | 25.248 | 3.077 | 0 | 0.039 | 1.705 | 17.695 | 18.775 | 0.353 |
| narrow_gap | hybrid_astar | 100 | 7.3 / 8.47 | 25.887 | 2.135 | 0.665 | 0.05 | 5.297 | 17.855 | 18.24 | 0.279 |
| office | astar_esdf | 100 | 11.18 / 21.13 | 11.863 | 4.29 | 2.319 | 0.156 | 3.822 | 9.02 | 10.99 | 0.38 |
| office | hybrid_astar | 100 | 8.24 / 13.24 | 12.279 | 2.272 | 0.975 | 0.232 | 5.954 | 8.865 | 9.635 | 0.293 |
| warehouse | astar_esdf | 100 | 25.91 / 30.78 | 35.987 | 5.484 | 0 | 0.028 | 3.144 | 25.015 | 25.975 | 0.574 |
| warehouse | hybrid_astar | 100 | 6.38 / 7.48 | 36.736 | 2.54 | 0.685 | 0.077 | 8.276 | 25.14 | 25.87 | 0.405 |
| forest | astar_esdf | 100 | 13.15 / 33.75 | 25.013 | 2.322 | 0.202 | 0.036 | 1.495 | 17.45 | 18.275 | 0.636 |
| forest | hybrid_astar | 100 | 7.78 / 8.98 | 25.473 | 1.377 | 0.671 | 0.068 | 6.709 | 17.565 | 17.845 | 0.593 |
| maze | astar_esdf | 100 | 46.3 / 68.87 | 38.557 | 5.771 | 2.647 | 0.106 | 11.521 | 27.965 | 31.98 | 0.593 |
| maze | hybrid_astar | 100 | 13.59 / 19.79 | 39.434 | 3.686 | 0.939 | 0.235 | 17.563 | 27.17 | 29.31 | 0.611 |
| glass_office | astar_esdf | 100 | 15.26 / 40.26 | 13.659 | 3.773 | 2.203 | 0.141 | 4.533 | 10.405 | 12.56 | 0.318 |
| glass_office | hybrid_astar | 100 | 8.21 / 15.5 | 14.584 | 2.638 | 0.756 | 0.266 | 7.722 | 10.395 | 11.725 | 0.295 |
| all | astar_esdf | 100 | 18.27 / 47.04 | 25.06 | 3.248 | 0.202 | 0.04 | 2.8 | 17.43 | 18.085 | 0.583 |
| all | hybrid_astar | 100 | 7.54 / 15.07 | 25.647 | 2.131 | 0.677 | 0.084 | 6.429 | 17.7 | 18.055 | 0.483 |

Hybrid A* plans that fell back to the grid path: 0 %.

Paired per layout (hybrid_astar - astar_esdf):

| metric | median delta | hybrid lower in % of layouts | layouts |
|---|---|---|---|
| time_stock_s | 0.065 | 43.1 | 160 |
| time_turn1_s | -0.435 | 68.1 | 160 |
| path_length_m | 0.482 | 13.1 | 160 |
| max_rad_per_m | -1.021 | 76.2 | 160 |
