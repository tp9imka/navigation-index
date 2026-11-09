`python run_submap.py --presets crazyflie --arms submap_arc_ig,submap_fwd,submap_fwd_ig,submap_arc_ig_notrack,submap_bridge --stem seed2_extras` (synthetic), wall 708.6 s, 14 workers, 100 layouts, seed 2.

| family | preset | fault | arm | reached % (95 % CI) | collision % | stuck % | wrong commits (> 0.5 m at resume) | runs > 0.5 m off before the fault | runs flown on a > 0.5 m pose (median s) | truth recover s median / p95 (loss runs, not recovered) | event recover s median / p95 | events / still lost at end | median hover s per run | submap returns at first match, median | ms per matched scan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | crazyflie | dropout | (a+ig) submap_arc_ig | 65.0 (55.3-73.6) | 1.0 | 34.0 | 5 | 7 | 20 (1.35) | 5.75 / 12.33 (67, 21) | 0.5 / 9.54 | 156 / 36 | 5.6 | 41.0 | 31.87 |
| random | crazyflie | dropout | (v) submap_fwd | 30.0 (21.9-39.6) | 1.0 | 69.0 | 3 | 5 | 13 (1.7) | 4.33 / 9.82 (73, 45) | 0.5 / 0.98 | 154 / 69 | 10.2 | 42.5 | 29.08 |
| random | crazyflie | dropout | (v+ig) submap_fwd_ig | 71.0 (61.5-79.0) | 1.0 | 28.0 | 4 | 5 | 18 (2.5) | 6.43 / 15.03 (78, 25) | 0.5 / 12.41 | 158 / 31 | 6.65 | 42.5 | 46.73 |
| random | crazyflie | dropout | (a+ig-t) submap_arc_ig_notrack | 58.0 (48.2-67.2) | 2.0 | 40.0 | 6 | 7 | 23 (3.0) | 5.0 / 17.62 (75, 40) | 0.5 / 10.22 | 184 / 44 | 8.45 | 42.0 | 35.04 |
| random | crazyflie | dropout | (x) submap_bridge | 58.0 (48.2-67.2) | 4.0 | 38.0 | 23 | 7 | 46 (12.55) | 4.38 / 11.47 (78, 54) | 0.3 / 1.18 | 202 / 0 | 0.6 | - | - |
| random | crazyflie | jump | (a+ig) submap_arc_ig | 87.0 (79.0-92.2) | 1.0 | 12.0 | 2 | 11 | 24 (2.35) | 3.5 / 10.16 (46, 8) | 1.1 / 9.88 | 92 / 16 | 1.5 | 40.0 | 27.61 |
| random | crazyflie | jump | (v) submap_fwd | 44.0 (34.7-53.8) | 0.0 | 56.0 | 1 | 9 | 15 (2.7) | 2.1 / 7.52 (48, 31) | 1.0 / 1.98 | 101 / 58 | 9.9 | 41.0 | 29.11 |
| random | crazyflie | jump | (v+ig) submap_fwd_ig | 89.0 (81.4-93.7) | 0.0 | 11.0 | 2 | 9 | 18 (2.65) | 4.0 / 13.11 (51, 11) | 2.8 / 12.5 | 107 / 16 | 3.25 | 41.0 | 38.83 |
| random | crazyflie | jump | (a+ig-t) submap_arc_ig_notrack | 75.0 (65.7-82.5) | 0.0 | 25.0 | 4 | 12 | 20 (2.85) | 3.05 / 10.77 (47, 17) | 1.05 / 12.82 | 127 / 27 | 3.4 | 40.0 | 31.82 |
| random | crazyflie | jump | (x) submap_bridge | 54.0 (44.3-63.4) | 5.0 | 41.0 | 10 | 13 | 40 (11.8) | 3.7 / 11.74 (59, 46) | 0.8 / 2.0 | 88 / 0 | 0.8 | - | - |
| office | crazyflie | dropout | (a+ig) submap_arc_ig | 54.0 (44.3-63.4) | 20.0 | 26.0 | 2 | 2 | 17 (1.1) | 4.93 / 9.29 (58, 25) | 0.5 / 5.52 | 170 / 30 | 3.3 | 97.5 | 63.49 |
| office | crazyflie | dropout | (v) submap_fwd | 57.0 (47.2-66.3) | 16.0 | 27.0 | 6 | 1 | 19 (1.4) | 4.37 / 9.07 (54, 21) | 0.5 / 0.8 | 190 / 28 | 1.0 | 95.0 | 69.12 |
| office | crazyflie | dropout | (v+ig) submap_fwd_ig | 66.0 (56.3-74.5) | 19.0 | 15.0 | 6 | 1 | 19 (1.4) | 4.67 / 12.25 (55, 13) | 0.5 / 4.1 | 190 / 17 | 1.0 | 95.0 | 72.12 |
| office | crazyflie | dropout | (a+ig-t) submap_arc_ig_notrack | 32.0 (23.7-41.7) | 30.0 | 38.0 | 5 | 2 | 21 (2.0) | 4.4 / 10.94 (53, 33) | 0.5 / 5.22 | 180 / 40 | 4.15 | 95.0 | 61.55 |
| office | crazyflie | dropout | (x) submap_bridge | 40.0 (30.9-49.8) | 46.0 | 14.0 | 19 | 2 | 36 (3.5) | 4.53 / 12.66 (59, 42) | 0.3 / 0.7 | 192 / 0 | 0.6 | - | - |
| office | crazyflie | jump | (a+ig) submap_arc_ig | 74.0 (64.6-81.6) | 20.0 | 6.0 | 1 | 0 | 12 (1.5) | 3.45 / 6.0 (22, 4) | 1.0 / 3.43 | 102 / 7 | 1.0 | 90.0 | 58.27 |
| office | crazyflie | jump | (v) submap_fwd | 68.0 (58.3-76.3) | 22.0 | 10.0 | 0 | 0 | 14 (1.9) | 2.15 / 8.26 (21, 7) | 1.0 / 1.95 | 106 / 10 | 1.0 | 91.0 | 60.53 |
| office | crazyflie | jump | (v+ig) submap_fwd_ig | 71.0 (61.5-79.0) | 26.0 | 3.0 | 0 | 0 | 14 (1.9) | 2.15 / 9.98 (21, 7) | 1.0 / 2.2 | 106 / 7 | 1.0 | 91.0 | 62.76 |
| office | crazyflie | jump | (a+ig-t) submap_arc_ig_notrack | 59.0 (49.2-68.1) | 27.0 | 14.0 | 2 | 1 | 18 (2.05) | 2.25 / 11.58 (24, 6) | 1.0 / 3.9 | 120 / 15 | 1.4 | 91.0 | 56.22 |
| office | crazyflie | jump | (x) submap_bridge | 45.0 (35.6-54.8) | 46.0 | 9.0 | 1 | 1 | 22 (2.6) | 3.15 / 7.35 (35, 21) | 0.8 / 1.9 | 99 / 0 | 0.8 | - | - |

Verdict (crazyflie, >= 90 % reached and 0 wrong commits in every family x fault cell): (a+ig) submap_arc_ig FAIL; (a+ig-t) submap_arc_ig_notrack FAIL; (v) submap_fwd FAIL; (v+ig) submap_fwd_ig FAIL

- random dropout (a+ig) submap_arc_ig: 65.0 % reached, 5 wrong commits => FAIL
- random dropout (v) submap_fwd: 30.0 % reached, 3 wrong commits => FAIL
- random dropout (v+ig) submap_fwd_ig: 71.0 % reached, 4 wrong commits => FAIL
- random dropout (a+ig-t) submap_arc_ig_notrack: 58.0 % reached, 6 wrong commits => FAIL
- random jump (a+ig) submap_arc_ig: 87.0 % reached, 2 wrong commits => FAIL
- random jump (v) submap_fwd: 44.0 % reached, 1 wrong commits => FAIL
- random jump (v+ig) submap_fwd_ig: 89.0 % reached, 2 wrong commits => FAIL
- random jump (a+ig-t) submap_arc_ig_notrack: 75.0 % reached, 4 wrong commits => FAIL
- office dropout (a+ig) submap_arc_ig: 54.0 % reached, 2 wrong commits => FAIL
- office dropout (v) submap_fwd: 57.0 % reached, 6 wrong commits => FAIL
- office dropout (v+ig) submap_fwd_ig: 66.0 % reached, 6 wrong commits => FAIL
- office dropout (a+ig-t) submap_arc_ig_notrack: 32.0 % reached, 5 wrong commits => FAIL
- office jump (a+ig) submap_arc_ig: 74.0 % reached, 1 wrong commits => FAIL
- office jump (v) submap_fwd: 68.0 % reached, 0 wrong commits => FAIL
- office jump (v+ig) submap_fwd_ig: 71.0 % reached, 0 wrong commits => FAIL
- office jump (a+ig-t) submap_arc_ig_notrack: 59.0 % reached, 2 wrong commits => FAIL
