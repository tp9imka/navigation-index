Seed-1 dev flight, quarter-turn stack plus a degeneracy-aware accept (correct only directions where the score drops >= 0.05 at 0.2 m, keep the prior along the others). Reach within 1-2 runs of sparse_dev_seed1_arc90.md, wrong commits (i) dropout 4 vs 2. Dropped from sparse.py.

`python run_sparse.py --layouts 100 --seed 1 --presets crazyflie --arms spin,spin_ig --stem sparse_dev_seed1_degen` (synthetic), wall 56.1 s, 8 workers

| preset | fault | arm | reached % | collision % | stuck % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | closed no_returns | still lost at end: none few / none low / ambiguous | median / p95 recover s | median spin s per event | median lost s per run | moves flown | median first-stack returns | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crazyflie | dropout | (g) spin | 16.0 | 1.0 | 83.0 | 0/100/0 | 26 | 1 | 0 | 48 / 0 / 24 | 2.8 / 5.85 | 10.2 | 10.2 | - | 9.0 | 0.3381 |
| crazyflie | dropout | (i) spin_ig | 46.0 | 2.0 | 52.0 | 0/100/0 | 63 | 4 | 0 | 10 / 0 / 25 | 8.9 / 27.99 | 12.45 | 12.45 | 198 | 9.0 | 0.4007 |
| crazyflie | jump | (g) spin | 33.0 | 1.0 | 66.0 | 83/1/0 | 41 | 0 | 0 | 9 / 0 / 34 | 2.8 / 7.0 | 9.9 | 4.6 | - | 14.0 | 0.6157 |
| crazyflie | jump | (i) spin_ig | 43.0 | 6.0 | 50.0 | 83/1/0 | 59 | 0 | 0 | 14 / 0 / 11 | 3.6 / 27.82 | 9.0 | 7.5 | 132 | 14.0 | 0.6288 |
