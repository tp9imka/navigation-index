Seed-1 dev flight (not held out), crazyflie preset only, before the final seed-0 run. Code as final: quarter-turn stack (90 deg).

`python run_sparse.py --layouts 100 --seed 1 --presets crazyflie --arms spin,spin_ig --stack-arc-deg 90 --stem sparse_dev_seed1_arc90` (synthetic), wall 47.5 s, 8 workers

| preset | fault | arm | reached % | collision % | stuck % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | closed no_returns | still lost at end: none few / none low / ambiguous | median / p95 recover s | median spin s per event | median lost s per run | moves flown | median first-stack returns | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crazyflie | dropout | (g) spin | 15.0 | 1.0 | 84.0 | 0/100/0 | 26 | 1 | 0 | 48 / 0 / 24 | 2.8 / 5.85 | 10.2 | 10.2 | - | 9.0 | 0.3407 |
| crazyflie | dropout | (i) spin_ig | 47.0 | 1.0 | 52.0 | 0/100/0 | 63 | 2 | 0 | 10 / 0 / 25 | 8.9 / 27.99 | 12.45 | 12.45 | 198 | 9.0 | 0.3983 |
| crazyflie | jump | (g) spin | 34.0 | 1.0 | 65.0 | 83/1/0 | 41 | 0 | 0 | 9 / 0 / 34 | 2.8 / 7.0 | 9.9 | 4.6 | - | 14.0 | 0.6178 |
| crazyflie | jump | (i) spin_ig | 45.0 | 6.0 | 48.0 | 83/1/0 | 59 | 0 | 0 | 14 / 0 / 11 | 3.6 / 27.82 | 9.0 | 7.5 | 132 | 14.0 | 0.6288 |
