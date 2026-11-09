`python run_sparse.py --layouts 100 --seed 0 --presets crazyflie --arms spin_ig --spin-rate 2.0 --stem sparse_random_0_rate2` (synthetic), wall 48.5 s, 8 workers

| preset | fault | arm | reached % | collision % | stuck % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | closed no_returns | still lost at end: none few / none low / ambiguous | median / p95 recover s | median spin s per event | median lost s per run | moves flown | median first-stack returns | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crazyflie | dropout | (i) spin_ig | 34.0 | 6.0 | 60.0 | 7/101/0 | 71 | 5 | 0 | 25 / 0 / 12 | 7.4 / 22.85 | 10.85 | 11.4 | 218 | 7.5 | 0.4692 |
| crazyflie | jump | (i) spin_ig | 48.0 | 16.0 | 36.0 | 88/3/0 | 59 | 2 | 0 | 22 / 0 / 9 | 5.9 / 24.54 | 6.7 | 5.9 | 144 | 11.0 | 0.6088 |
