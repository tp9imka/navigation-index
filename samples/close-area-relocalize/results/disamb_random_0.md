`python run_disambiguate.py --layouts 100 --seed 0` (synthetic), wall 75.2 s, 8 workers

| fault | arm | runs | reached % | collision % | stuck % | relocs accepted | wrong commits (> 0.5 m) | still hovering at end | median / p95 / max recover s | moves flown | events with a move => accepted / wrong / open | median recover s after a move | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dropout | (b) single | 100 | 100.0 | 0.0 | 0.0 | 461 | 2 | 1 | 0.2 / 0.2 / 0.2 | - | - | - | 0.2866 |
| dropout | (c) multi | 100 | 80.0 | 0.0 | 20.0 | 386 | 0 | 20 | 0.4 / 0.4 / 3.3 | - | - | - | 0.2938 |
| dropout | (d) multi_random | 100 | 97.0 | 0.0 | 3.0 | 428 | 0 | 4 | 0.4 / 0.6 / 13.2 | 40 | 22 => 19 / 0 / 3 | 2.6 | 0.3048 |
| dropout | (e) multi_sep | 100 | 99.0 | 0.0 | 1.0 | 439 | 0 | 1 | 0.4 / 1.3 / 4.7 | 28 | 25 => 24 / 0 / 1 | 2.2 | 0.309 |
| dropout | (f) multi_ig | 100 | 99.0 | 0.0 | 1.0 | 439 | 0 | 2 | 0.4 / 1.3 / 4.7 | 26 | 25 => 24 / 0 / 1 | 2.4 | 0.3044 |
| jump | (b) single | 100 | 100.0 | 0.0 | 0.0 | 419 | 4 | 0 | 0.2 / 0.2 / 0.2 | - | - | - | 0.3453 |
| jump | (c) multi | 100 | 93.0 | 0.0 | 7.0 | 339 | 0 | 10 | 0.4 / 0.4 / 2.6 | - | - | - | 0.4832 |
| jump | (d) multi_random | 100 | 98.0 | 0.0 | 2.0 | 354 | 0 | 5 | 0.4 / 0.4 / 11.8 | 20 | 9 => 7 / 0 / 2 | 4.1 | 0.4859 |
| jump | (e) multi_sep | 100 | 100.0 | 0.0 | 0.0 | 362 | 0 | 3 | 0.4 / 0.4 / 5.7 | 9 | 9 => 9 / 0 / 0 | 2.2 | 0.4879 |
| jump | (f) multi_ig | 100 | 99.0 | 0.0 | 1.0 | 359 | 0 | 4 | 0.4 / 0.4 / 3.9 | 12 | 9 => 8 / 0 / 1 | 1.95 | 0.4894 |
