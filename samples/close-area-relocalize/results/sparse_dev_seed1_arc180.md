Seed-1 dev flight, same as sparse_dev_seed1_arc90.md but a half-turn stack (180 deg, --stack-arc-deg 180). Not better; 90 deg kept.

`python run_sparse.py --layouts 100 --seed 1 --presets crazyflie --arms spin,spin_ig --stack-arc-deg 180 --stem sparse_dev_seed1_arc180` (synthetic), wall 50.4 s, 8 workers

| preset | fault | arm | reached % | collision % | stuck % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | closed no_returns | still lost at end: none few / none low / ambiguous | median / p95 recover s | median spin s per event | median lost s per run | moves flown | median first-stack returns | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crazyflie | dropout | (g) spin | 18.0 | 0.0 | 82.0 | 0/100/0 | 27 | 0 | 0 | 43 / 0 / 30 | 4.4 / 6.81 | 10.2 | 10.2 | - | 11.5 | 0.3228 |
| crazyflie | dropout | (i) spin_ig | 43.0 | 1.0 | 55.0 | 0/100/0 | 61 | 0 | 0 | 13 / 0 / 26 | 12.1 / 34.2 | 20.0 | 20.0 | 214 | 11.5 | 0.3756 |
| crazyflie | jump | (g) spin | 33.0 | 1.0 | 66.0 | 83/1/0 | 37 | 0 | 0 | 2 / 0 / 45 | 4.4 / 7.98 | 9.9 | 7.35 | - | 22.0 | 0.6178 |
| crazyflie | jump | (i) spin_ig | 60.0 | 1.0 | 37.0 | 83/1/0 | 66 | 0 | 0 | 7 / 0 / 11 | 12.05 / 36.08 | 18.65 | 12.1 | 161 | 22.0 | 0.6319 |
