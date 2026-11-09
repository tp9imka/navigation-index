`python run_submap.py ` (synthetic), wall 208.9 s, 14 workers, 100 layouts, seed 2.

| family | preset | fault | arm | reached % (95 % CI) | collision % | stuck % | wrong commits (> 0.5 m at resume) | runs > 0.5 m off before the fault | runs flown on a > 0.5 m pose (median s) | truth recover s median / p95 (loss runs, not recovered) | event recover s median / p95 | events / still lost at end | median hover s per run | submap returns at first match, median | ms per matched scan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | crazyflie | dropout | (i) spin_ig | 36.0 (27.3-45.8) | 3.0 | 61.0 | 0 | 7 | 24 (6.05) | 5.81 / 24.36 (68, 32) | 9.0 / 28.52 | 100 / 41 | 16.2 | - | 1.18 |
| random | crazyflie | dropout | (m) mcl | 14.0 (8.5-22.1) | 81.0 | 5.0 | 6 | 62 | 100 (11.0) | 6.21 / 10.26 (90, 74) | 2.9 / 10.84 | 151 / 98 | 0.0 | - | 0.06 |
| random | crazyflie | dropout | (s) submap | 0.0 (0.0-3.7) | 1.0 | 99.0 | 5 | 5 | 10 (2.5) | 1.46 / 13.11 (48, 42) | 0.5 / 1.92 | 148 / 99 | 10.2 | 27.0 | 4.13 |
| random | crazyflie | dropout | (s+ig) submap_ig | 26.0 (18.4-35.4) | 5.0 | 69.0 | 21 | 9 | 37 (2.7) | 5.33 / 18.82 (80, 43) | 0.95 / 10.48 | 224 / 82 | 19.85 | 28.0 | 15.56 |
| random | crazyflie | jump | (i) spin_ig | 53.0 (43.3-62.5) | 3.0 | 44.0 | 0 | 12 | 26 (8.3) | 8.45 / 17.45 (85, 29) | 7.3 / 19.16 | 87 / 22 | 8.9 | - | 1.22 |
| random | crazyflie | jump | (m) mcl | 15.0 (9.3-23.3) | 77.0 | 8.0 | 14 | 80 | 100 (11.65) | 1.55 / 2.92 (88, 84) | 3.15 / 15.88 | 140 / 94 | 0.0 | - | 0.06 |
| random | crazyflie | jump | (s) submap | 1.0 (0.2-5.4) | 0.0 | 99.0 | 4 | 6 | 10 (3.95) | 2.55 / 6.61 (25, 17) | 0.5 / 1.7 | 146 / 99 | 10.2 | 27.0 | 4.25 |
| random | crazyflie | jump | (s+ig) submap_ig | 30.0 (21.9-39.6) | 4.0 | 65.0 | 19 | 21 | 34 (3.7) | 3.7 / 16.45 (75, 44) | 1.9 / 15.21 | 225 / 86 | 19.7 | 27.5 | 15.19 |
| office | crazyflie | dropout | (i) spin_ig | 52.0 (42.3-61.5) | 35.0 | 13.0 | 0 | 2 | 14 (2.9) | 2.53 / 14.79 (52, 3) | 2.15 / 15.73 | 97 / 3 | 2.1 | - | 2.85 |
| office | crazyflie | dropout | (m) mcl | 1.0 (0.2-5.4) | 97.0 | 1.0 | 6 | 85 | 100 (5.8) | 2.83 / 12.51 (63, 50) | 0.9 / 8.46 | 220 / 95 | 0.0 | - | 0.12 |
| office | crazyflie | dropout | (s) submap | 15.0 (9.3-23.3) | 12.0 | 73.0 | 16 | 4 | 19 (0.9) | 2.83 / 5.63 (61, 42) | 0.5 / 1.74 | 185 / 72 | 9.9 | 85.0 | 6.34 |
| office | crazyflie | dropout | (s+ig) submap_ig | 22.0 (15.0-31.1) | 23.0 | 54.0 | 23 | 4 | 29 (1.3) | 4.72 / 10.82 (68, 38) | 0.5 / 6.31 | 194 / 55 | 8.9 | 85.0 | 7.66 |
| office | crazyflie | jump | (i) spin_ig | 52.0 (42.3-61.5) | 26.0 | 22.0 | 0 | 1 | 16 (2.75) | 2.8 / 9.59 (97, 5) | 2.8 / 12.56 | 99 / 4 | 2.8 | - | 2.89 |
| office | crazyflie | jump | (m) mcl | 0.0 (0.0-3.7) | 94.0 | 5.0 | 21 | 77 | 100 (4.8) | 14.45 / 18.82 (81, 79) | 0.7 / 6.96 | 218 / 96 | 0.0 | - | 0.13 |
| office | crazyflie | jump | (s) submap | 26.0 (18.4-35.4) | 13.0 | 61.0 | 15 | 4 | 18 (3.25) | 2.3 / 9.95 (35, 19) | 1.0 / 2.05 | 151 / 60 | 9.65 | 83.0 | 7.04 |
| office | crazyflie | jump | (s+ig) submap_ig | 28.0 (20.1-37.5) | 18.0 | 54.0 | 21 | 4 | 22 (3.7) | 2.9 / 8.7 (38, 17) | 1.0 / 3.38 | 159 / 53 | 9.0 | 84.0 | 12.12 |
| random | ideal | dropout | (i) spin_ig | 99.0 (94.6-99.8) | 0.0 | 1.0 | 0 | 5 | 8 (0.7) | 3.0 / 8.92 (57, 0) | 2.4 / 8.9 | 345 / 2 | 9.7 | - | 30.4 |
| random | ideal | dropout | (m) mcl | 99.0 (94.6-99.8) | 1.0 | 0.0 | 5 | 4 | 46 (0.6) | 3.78 / 8.45 (53, 1) | 0.5 / 2.32 | 72 / 3 | 0.0 | - | 0.47 |
| random | ideal | dropout | (s) submap | 81.0 (72.2-87.5) | 0.0 | 19.0 | 1 | 3 | 7 (0.9) | 2.73 / 5.97 (43, 8) | 0.5 / 2.14 | 191 / 19 | 1.0 | 290.0 | 15.93 |
| random | ideal | dropout | (s+ig) submap_ig | 99.0 (94.6-99.8) | 0.0 | 1.0 | 1 | 3 | 7 (0.9) | 4.27 / 9.57 (44, 1) | 0.5 / 4.75 | 191 / 1 | 1.0 | 290.0 | 16.34 |
| random | ideal | jump | (i) spin_ig | 100.0 (96.3-100.0) | 0.0 | 0.0 | 0 | 11 | 7 (1.5) | 2.8 / 14.96 (85, 0) | 2.4 / 9.75 | 328 / 2 | 9.8 | - | 29.98 |
| random | ideal | jump | (m) mcl | 89.0 (81.4-93.7) | 10.0 | 1.0 | 32 | 11 | 87 (2.4) | 4.8 / 11.1 (87, 16) | 0.9 / 5.44 | 167 / 8 | 0.0 | - | 0.42 |
| random | ideal | jump | (s) submap | 82.0 (73.3-88.3) | 0.0 | 18.0 | 2 | 5 | 9 (0.5) | 2.0 / 4.67 (20, 6) | 1.0 / 1.96 | 86 / 18 | 1.0 | 288.0 | 15.99 |
| random | ideal | jump | (s+ig) submap_ig | 100.0 (96.3-100.0) | 0.0 | 0.0 | 2 | 5 | 9 (0.5) | 2.3 / 9.7 (21, 0) | 1.0 / 8.97 | 86 / 0 | 1.0 | 288.0 | 15.76 |

Verdict (crazyflie, >= 90 % reached and 0 wrong commits in every family x fault cell): (s) submap FAIL; (s+ig) submap_ig FAIL

- random dropout (s) submap: 0.0 % reached, 5 wrong commits => FAIL
- random dropout (s+ig) submap_ig: 26.0 % reached, 21 wrong commits => FAIL
- random jump (s) submap: 1.0 % reached, 4 wrong commits => FAIL
- random jump (s+ig) submap_ig: 30.0 % reached, 19 wrong commits => FAIL
- office dropout (s) submap: 15.0 % reached, 16 wrong commits => FAIL
- office dropout (s+ig) submap_ig: 22.0 % reached, 23 wrong commits => FAIL
- office jump (s) submap: 26.0 % reached, 15 wrong commits => FAIL
- office jump (s+ig) submap_ig: 28.0 % reached, 21 wrong commits => FAIL
