`python run_disambiguate.py --layouts 100 --seed 0` (synthetic), wall 73.7 s, 8 workers

| fault | arm | runs | reached % | collision % | stuck % | relocs accepted | wrong commits (> 0.5 m) | still hovering at end | median / p95 / max recover s | moves flown | events with a move => accepted / wrong / open | median recover s after a move | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dropout | (b) single | 100 | 100.0 | 0.0 | 0.0 | 461 | 2 | 1 | 0.2 / 0.2 / 0.2 | - | - | - | 0.2866 |
| dropout | (c) multi | 100 | 80.0 | 0.0 | 20.0 | 386 | 0 | 20 | 0.4 / 0.4 / 3.3 | - | - | - | 0.2938 |
| dropout | (d) multi_random | 100 | 95.0 | 0.0 | 5.0 | 425 | 0 | 5 | 0.4 / 0.48 / 13.2 | 37 | 19 => 16 / 0 / 3 | 3.25 | 0.3048 |
| dropout | (e) multi_sep | 100 | 97.0 | 0.0 | 3.0 | 434 | 0 | 3 | 0.4 / 0.84 / 4.7 | 22 | 21 => 20 / 0 / 1 | 2.3 | 0.309 |
| dropout | (f) multi_ig | 100 | 98.0 | 0.0 | 2.0 | 437 | 0 | 2 | 0.4 / 1.3 / 4.7 | 22 | 22 => 22 / 0 / 0 | 2.55 | 0.3044 |
| jump | (b) single | 100 | 100.0 | 0.0 | 0.0 | 419 | 4 | 0 | 0.2 / 0.2 / 0.2 | - | - | - | 0.3453 |
| jump | (c) multi | 100 | 93.0 | 0.0 | 7.0 | 339 | 0 | 10 | 0.4 / 0.4 / 2.6 | - | - | - | 0.4832 |
| jump | (d) multi_random | 100 | 97.0 | 0.0 | 3.0 | 352 | 0 | 6 | 0.4 / 0.4 / 11.8 | 13 | 6 => 5 / 0 / 1 | 2.8 | 0.4859 |
| jump | (e) multi_sep | 100 | 98.0 | 0.0 | 2.0 | 357 | 0 | 5 | 0.4 / 0.4 / 3.5 | 7 | 7 => 7 / 0 / 0 | 2.1 | 0.4859 |
| jump | (f) multi_ig | 100 | 98.0 | 0.0 | 2.0 | 357 | 0 | 5 | 0.4 / 0.4 / 3.9 | 7 | 7 => 7 / 0 / 0 | 1.7 | 0.4879 |
