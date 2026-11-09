Superseded v1 (seed 0, first full run): no stop-before-stack gate (STILL_MPS) and moves did not clear the stack. Replaced by sparse_random_0.md.

`python run_sparse.py --layouts 100 --seed 0` (synthetic), wall 195.9 s, 8 workers

| preset | fault | arm | reached % | collision % | stuck % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | closed no_returns | still lost at end: none few / none low / ambiguous | median / p95 recover s | median spin s per event | median lost s per run | moves flown | median first-stack returns | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ideal | dropout | (b) single | 100.0 | 0.0 | 0.0 | 96/96/287 | 461 | 2 | 17 | 0 / 0 / 0 | 0.2 / 0.2 | - | 1.0 | - | - | 0.2866 |
| ideal | dropout | (e) multi_sep | 99.0 | 0.0 | 1.0 | 84/98/258 | 439 | 0 | 0 | 0 / 0 / 1 | 0.4 / 1.3 | - | 2.0 | 28 | - | 0.309 |
| ideal | dropout | (f) multi_ig | 99.0 | 0.0 | 1.0 | 86/99/256 | 439 | 0 | 0 | 0 / 0 / 1 | 0.4 / 1.3 | - | 2.0 | 26 | - | 0.3044 |
| ideal | dropout | (g) spin | 79.0 | 0.0 | 21.0 | 8/79/238 | 303 | 0 | 0 | 1 / 0 / 20 | 2.0 / 2.09 | 2.0 | 8.0 | - | 643.0 | 0.3516 |
| ideal | dropout | (h) spin_single | 100.0 | 0.0 | 0.0 | 28/84/284 | 390 | 1 | 3 | 0 / 0 / 0 | 1.8 / 1.8 | 1.8 | 7.2 | - | 643.0 | 0.3526 |
| ideal | dropout | (i) spin_ig | 98.0 | 0.0 | 2.0 | 7/79/265 | 348 | 0 | 0 | 0 / 0 / 2 | 2.0 / 4.66 | 2.0 | 8.0 | 39 | 663.5 | 0.3569 |
| ideal | jump | (b) single | 100.0 | 0.0 | 0.0 | 88/2/331 | 419 | 4 | 2 | 0 / 0 / 0 | 0.2 / 0.2 | - | 0.8 | - | - | 0.3453 |
| ideal | jump | (e) multi_sep | 100.0 | 0.0 | 0.0 | 88/3/274 | 362 | 0 | 0 | 0 / 0 / 0 | 0.4 / 0.4 | - | 1.6 | 9 | - | 0.4879 |
| ideal | jump | (f) multi_ig | 99.0 | 0.0 | 1.0 | 88/3/272 | 359 | 0 | 0 | 1 / 0 / 0 | 0.4 / 0.4 | - | 1.6 | 12 | - | 0.4894 |
| ideal | jump | (g) spin | 75.0 | 0.0 | 25.0 | 81/2/209 | 266 | 0 | 0 | 0 / 0 / 25 | 2.0 / 2.0 | 2.0 | 8.0 | - | 635.0 | 0.5968 |
| ideal | jump | (h) spin_single | 100.0 | 0.0 | 0.0 | 85/1/263 | 348 | 3 | 0 | 0 / 0 / 0 | 1.8 / 1.8 | 1.8 | 5.4 | - | 650.0 | 0.5933 |
| ideal | jump | (i) spin_ig | 100.0 | 0.0 | 0.0 | 85/3/245 | 331 | 0 | 0 | 0 / 0 / 0 | 2.0 / 4.7 | 2.0 | 7.6 | 48 | 648.0 | 0.6002 |
| crazyflie | dropout | (b) single | 64.0 | 1.0 | 35.0 | 100/102/0 | 0 | 0 | 202 | 0 / 0 / 0 | - / - | - | 0.4 | - | - | 0.4474 |
| crazyflie | dropout | (e) multi_sep | 2.0 | 7.0 | 91.0 | 0/100/0 | 0 | 0 | 0 | 100 / 0 / 0 | - / - | - | 22.3 | 392 | - | 0.3507 |
| crazyflie | dropout | (f) multi_ig | 2.0 | 7.0 | 91.0 | 0/100/0 | 0 | 0 | 0 | 100 / 0 / 0 | - / - | - | 22.3 | 392 | - | 0.3507 |
| crazyflie | dropout | (g) spin | 26.0 | 1.0 | 73.0 | 0/100/0 | 39 | 2 | 0 | 40 / 0 / 20 | 2.1 / 7.36 | 10.05 | 10.05 | - | 12.0 | 0.3664 |
| crazyflie | dropout | (h) spin_single | 53.0 | 7.0 | 40.0 | 18/104/0 | 69 | 12 | 53 | 0 / 0 / 0 | 1.8 / 1.8 | 1.8 | 1.8 | - | 11.0 | 0.481 |
| crazyflie | dropout | (i) spin_ig | 53.0 | 3.0 | 43.0 | 0/101/0 | 82 | 1 | 0 | 9 / 0 / 9 | 4.75 / 15.37 | 6.3 | 6.4 | 155 | 12.0 | 0.4375 |
| crazyflie | jump | (b) single | 38.0 | 6.0 | 56.0 | 89/4/0 | 0 | 0 | 93 | 0 / 0 / 0 | - / - | - | 0.2 | - | - | 0.6453 |
| crazyflie | jump | (e) multi_sep | 12.0 | 23.0 | 65.0 | 88/2/0 | 0 | 0 | 0 | 90 / 0 / 0 | - / - | - | 15.6 | 308 | - | 0.6205 |
| crazyflie | jump | (f) multi_ig | 12.0 | 23.0 | 65.0 | 88/2/0 | 0 | 0 | 0 | 90 / 0 / 0 | - / - | - | 15.6 | 308 | - | 0.6205 |
| crazyflie | jump | (g) spin | 33.0 | 1.0 | 66.0 | 88/3/0 | 47 | 0 | 0 | 8 / 0 / 36 | 2.0 / 4.67 | 5.2 | 2.95 | - | 17.0 | 0.5822 |
| crazyflie | jump | (h) spin_single | 48.0 | 8.0 | 44.0 | 89/4/0 | 80 | 17 | 13 | 0 / 0 / 0 | 1.8 / 1.8 | 1.8 | 1.8 | - | 17.0 | 0.636 |
| crazyflie | jump | (i) spin_ig | 60.0 | 10.0 | 30.0 | 89/3/0 | 83 | 4 | 0 | 2 / 0 / 6 | 2.9 / 10.78 | 3.85 | 2.95 | 83 | 17.0 | 0.606 |
