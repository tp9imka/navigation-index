`python run_mcl.py --arms mcl,mcl_gate --hardened --stem seed2_hardened` (synthetic), wall 87.4 s, 14 workers, 100 layouts, seed 2.

| family | preset | fault | arm | reached % (95 % CI) | collision % | stuck % | wrong commits (> 0.5 m at resume) | runs > 0.5 m off before the fault | runs flown on a > 0.5 m pose (median s) | truth recover s median / p95 (loss runs, not recovered) | event recover s median / p95 | still lost at end | median hover s per run | ms per scan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | ideal | dropout | (m) mcl | 100.0 (96.3-100.0) | 0.0 | 0.0 | 4 | 2 | 10 (1.0) | 3.77 / 8.33 (47, 2) | 0.4 / 1.92 | 0 | 0.0 | 0.44 |
| random | ideal | dropout | (m+g) mcl_gate | 100.0 (96.3-100.0) | 0.0 | 0.0 | 3 | 3 | 4 (1.4) | 3.82 / 8.6 (48, 0) | 0.4 / 1.6 | 0 | 0.0 | 0.45 |
| random | ideal | jump | (m) mcl | 94.0 (87.5-97.2) | 4.0 | 2.0 | 30 | 4 | 72 (0.9) | 4.3 / 9.4 (86, 17) | 0.6 / 2.6 | 2 | 0.0 | 0.44 |
| random | ideal | jump | (m+g) mcl_gate | 93.0 (86.3-96.6) | 1.0 | 6.0 | 23 | 6 | 42 (0.6) | 4.5 / 11.22 (86, 9) | 0.7 / 3.3 | 6 | 1.45 | 0.44 |
| random | crazyflie | dropout | (m) mcl | 24.0 (16.7-33.2) | 75.0 | 1.0 | 40 | 58 | 99 (11.2) | 4.62 / 15.9 (95, 71) | 2.4 / 15.99 | 91 | 0.0 | 0.08 |
| random | crazyflie | dropout | (m+g) mcl_gate | 1.0 (0.2-5.4) | 0.0 | 99.0 | 10 | 57 | 16 (1.85) | 1.22 / 3.0 (98, 94) | 0.55 / 3.0 | 99 | 10.2 | 0.1 |
| random | crazyflie | jump | (m) mcl | 23.0 (15.8-32.2) | 75.0 | 2.0 | 60 | 77 | 99 (13.5) | 2.7 / 21.22 (90, 82) | 2.4 / 16.28 | 91 | 0.0 | 0.09 |
| random | crazyflie | jump | (m+g) mcl_gate | 1.0 (0.2-5.4) | 0.0 | 99.0 | 24 | 76 | 25 (0.8) | 1.3 / 1.84 (27, 24) | 0.65 / 7.49 | 99 | 10.2 | 0.1 |
| office | ideal | dropout | (m) mcl | 90.0 (82.6-94.5) | 10.0 | 0.0 | 0 | 2 | 6 (3.0) | 4.06 / 9.94 (24, 4) | 0.3 / 2.02 | 12 | 0.0 | 0.74 |
| office | ideal | dropout | (m+g) mcl_gate | 93.0 (86.3-96.6) | 3.0 | 4.0 | 0 | 0 | 0 (-) | 3.47 / 7.07 (25, 0) | 0.3 / 2.1 | 5 | 1.5 | 0.75 |
| office | ideal | jump | (m) mcl | 71.0 (61.5-79.0) | 29.0 | 0.0 | 25 | 0 | 65 (0.9) | 3.1 / 10.0 (100, 24) | 0.5 / 3.48 | 24 | 0.0 | 0.76 |
| office | ideal | jump | (m+g) mcl_gate | 75.0 (65.7-82.5) | 13.0 | 12.0 | 28 | 0 | 16 (1.15) | 3.0 / 7.99 (100, 18) | 0.35 / 3.3 | 13 | 4.6 | 0.72 |
| office | crazyflie | dropout | (m) mcl | 10.0 (5.5-17.4) | 80.0 | 9.0 | 26 | 68 | 95 (7.3) | 2.53 / 16.94 (78, 50) | 1.2 / 13.26 | 85 | 0.0 | 0.14 |
| office | crazyflie | dropout | (m+g) mcl_gate | 0.0 (0.0-3.7) | 1.0 | 99.0 | 21 | 66 | 14 (0.7) | 2.37 / 2.93 (90, 84) | 0.5 / 5.76 | 99 | 10.05 | 0.13 |
| office | crazyflie | jump | (m) mcl | 1.0 (0.2-5.4) | 81.0 | 16.0 | 45 | 42 | 99 (6.6) | 5.7 / 14.23 (95, 83) | 1.0 / 11.75 | 89 | 0.0 | 0.15 |
| office | crazyflie | jump | (m+g) mcl_gate | 0.0 (0.0-3.7) | 3.0 | 97.0 | 23 | 55 | 18 (0.4) | 1.4 / 2.8 (80, 75) | 0.5 / 5.25 | 97 | 9.95 | 0.13 |
