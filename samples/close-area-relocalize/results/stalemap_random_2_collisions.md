From `stalemap_random_2.json` (synthetic). One row per collided run of a relocalizing arm. `map ESDF` = clearance the map claimed at the collision point; `last move t` = last planner step that flew a disambiguating move; `to added` = distance from the collision point to the nearest added (unmapped) obstacle surface, c_added only.

| rung | fault | arm | layout | kind | map ESDF m | collision t s | last move t s | moves in run | wrong commits in run (map frame) | to added m |
|---|---|---|---|---|---|---|---|---|---|---|
| c_added | dropout | (b) single | 71 | mapped | 0.2 | 24.68 | - | 0 | 11 | 4.945 |
| c_added | dropout | (b) single | 74 | mapped | 0.2 | 19.58 | - | 0 | 3 | 7.882 |
| c_added | dropout | (f) multi_ig | 0 | move_unmapped | 2.8 | 16.86 | 16.8 | 2 | 0 | 0.148 |
| c_added | dropout | (f) multi_ig | 20 | unmapped | 1.703 | 16.8 | 15.6 | 2 | 0 | 0.133 |
| c_added | dropout | (f) multi_ig | 61 | unmapped | 1.389 | 16.44 | 14.200000000000001 | 2 | 2 | 0.15 |
| c_added | dropout | (f) multi_ig | 64 | move_mapped | 0.2 | 33.44 | 33.4 | 5 | 1 | 7.556 |
| c_added | dropout | (f) multi_ig | 89 | unmapped | 2.059 | 24.58 | 23.6 | 3 | 0 | 0.135 |
| c_added | dropout | (f) multi_ig | 90 | move_unmapped | 1.628 | 8.08 | 8.0 | 1 | 0 | 0.147 |
| c_added | dropout | (f) multi_ig | 95 | unmapped | 4.46 | 15.22 | 14.0 | 1 | 0 | 0.137 |
| c_added | jump | (b) single | 71 | mapped | 0.2 | 19.38 | - | 0 | 10 | 5.561 |
| c_added | jump | (f) multi_ig | 0 | unmapped | 2.7 | 18.42 | 13.4 | 2 | 1 | 0.144 |
| c_added | jump | (f) multi_ig | 2 | unmapped | 3.14 | 8.76 | 8.2 | 1 | 0 | 0.133 |
| c_added | jump | (f) multi_ig | 41 | move_unmapped | 5.0 | 15.5 | 15.4 | 1 | 0 | 0.15 |
| c_added | jump | (f) multi_ig | 43 | mapped | 0.1 | 28.86 | 27.7 | 3 | 2 | 1.499 |
| c_added | jump | (f) multi_ig | 89 | unmapped | 2.195 | 27.52 | 26.6 | 5 | 0 | 0.149 |
| c_added | jump | (f) multi_ig | 90 | move_unmapped | 1.628 | 8.08 | 8.0 | 1 | 0 | 0.148 |
| c_added | jump | (f) multi_ig | 95 | unmapped | 4.245 | 14.98 | 13.700000000000001 | 1 | 0 | 0.146 |
| e_selfmap | dropout | (c) multi | 28 | mapped | 0.2 | 21.8 | - | 0 | 2 | - |
| e_selfmap | dropout | (f) multi_ig | 98 | move_mapped | 0.1 | 26.46 | 26.400000000000002 | 5 | 3 | - |
| e_selfmap | dropout | (f) multi_ig | 99 | unmapped | 0.728 | 21.14 | 20.8 | 2 | 1 | - |
| e_selfmap | jump | (f) multi_ig | 3 | mapped | 0.141 | 10.42 | 10.1 | 1 | 0 | - |
| e_selfmap | jump | (f) multi_ig | 99 | unmapped | 0.728 | 17.86 | 17.1 | 1 | 1 | - |
