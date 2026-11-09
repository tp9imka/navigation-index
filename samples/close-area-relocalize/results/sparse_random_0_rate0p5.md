`python run_sparse.py --layouts 100 --seed 0 --presets crazyflie --arms spin_ig --spin-rate 0.5 --stem sparse_random_0_rate0p5` (synthetic), wall 58.1 s, 8 workers

| preset | fault | arm | reached % | collision % | stuck % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | closed no_returns | still lost at end: none few / none low / ambiguous | median / p95 recover s | median spin s per event | median lost s per run | moves flown | median first-stack returns | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crazyflie | dropout | (i) spin_ig | 48.0 | 3.0 | 47.0 | 0/101/0 | 68 | 1 | 0 | 11 / 0 / 22 | 5.25 / 35.46 | 15.5 | 15.55 | 183 | 18.0 | 0.3949 |
| crazyflie | jump | (i) spin_ig | 67.0 | 1.0 | 31.0 | 90/2/0 | 77 | 0 | 0 | 8 / 0 / 7 | 5.3 / 27.94 | 12.3 | 12.0 | 118 | 28.0 | 0.6045 |
