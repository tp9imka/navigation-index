`python run_mcl.py --arms spin_ig --presets crazyflie --stem seed2_spin_ig` (synthetic), wall 36.6 s, 14 workers, 100 layouts, seed 2.

| family | preset | fault | arm | reached % (95 % CI) | collision % | stuck % | wrong commits (> 0.5 m at resume) | runs > 0.5 m off before the fault | runs flown on a > 0.5 m pose (median s) | truth recover s median / p95 (loss runs, not recovered) | event recover s median / p95 | still lost at end | median hover s per run | ms per scan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | crazyflie | dropout | (i) spin_ig | 36.0 (27.3-45.8) | 3.0 | 61.0 | 0 | 7 | 24 (6.05) | 5.81 / 24.36 (68, 32) | 9.0 / 28.52 | 41 | 16.2 | 1.4 |
| random | crazyflie | jump | (i) spin_ig | 53.0 (43.3-62.5) | 3.0 | 44.0 | 0 | 12 | 26 (8.3) | 8.45 / 17.45 (85, 29) | 7.3 / 19.16 | 22 | 8.9 | 1.32 |
| office | crazyflie | dropout | (i) spin_ig | 52.0 (42.3-61.5) | 35.0 | 13.0 | 0 | 2 | 14 (2.9) | 2.53 / 14.79 (52, 3) | 2.15 / 15.73 | 3 | 2.1 | 2.87 |
| office | crazyflie | jump | (i) spin_ig | 52.0 (42.3-61.5) | 26.0 | 22.0 | 0 | 1 | 16 (2.75) | 2.8 / 9.59 (97, 5) | 2.8 / 12.56 | 4 | 2.8 | 2.9 |
