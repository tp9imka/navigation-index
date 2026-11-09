`python experiment.py --layouts 100 --seed 0` (synthetic), wall 70.7 s, 8 workers

| fault | arm | runs | reached % | collision % | stuck % | timeout % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | still hovering at end | median recover s | median run max err m | fault fired runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dropout | truth | 100 | 100.0 | 0.0 | 0.0 | 0.0 | - | - | - | - | - | - | - |
| dropout | estimator | 100 | 64.0 | 1.0 | 35.0 | 0.0 | - | - | - | - | - | 0.4554 | 100 |
| dropout | hover_only | 100 | 59.0 | 4.0 | 37.0 | 0.0 | 0/104/0 | - | - | 0 | 1.8 | 0.4683 | 100 |
| dropout | single | 100 | 100.0 | 0.0 | 0.0 | 0.0 | 96/96/287 | 461 | 2 | 1 | 0.2 | 0.2866 | 100 |
| dropout | multi | 100 | 80.0 | 0.0 | 20.0 | 0.0 | 83/96/227 | 386 | 0 | 20 | 0.4 | 0.2938 | 100 |
| dropout | single_noinnov | 100 | 80.0 | 0.0 | 20.0 | 0.0 | 100/102/0 | 189 | 0 | 0 | 0.2 | 0.3483 | 100 |
| dropout | multi_noinnov | 100 | 67.0 | 0.0 | 33.0 | 0.0 | 91/103/0 | 178 | 0 | 16 | 0.4 | 0.3364 | 100 |
| jump | truth | 100 | 100.0 | 0.0 | 0.0 | 0.0 | - | - | - | - | - | - | - |
| jump | estimator | 100 | 36.0 | 9.0 | 55.0 | 0.0 | - | - | - | - | - | 0.6275 | 89 |
| jump | hover_only | 100 | 38.0 | 6.0 | 56.0 | 0.0 | 89/4/0 | - | - | 0 | 0.2 | 0.6453 | 89 |
| jump | single | 100 | 100.0 | 0.0 | 0.0 | 0.0 | 88/2/331 | 419 | 4 | 0 | 0.2 | 0.3453 | 88 |
| jump | multi | 100 | 93.0 | 0.0 | 7.0 | 0.0 | 87/3/259 | 339 | 0 | 10 | 0.4 | 0.4832 | 87 |
| jump | single_noinnov | 100 | 71.0 | 0.0 | 29.0 | 0.0 | 89/3/0 | 91 | 0 | 0 | 0.2 | 0.4168 | 89 |
| jump | multi_noinnov | 100 | 76.0 | 0.0 | 24.0 | 0.0 | 89/2/0 | 89 | 0 | 2 | 0.4 | 0.5113 | 89 |
