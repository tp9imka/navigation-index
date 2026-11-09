`python run_disambiguate.py --layouts 100 --seed 1 --out results` (synthetic), wall 76.5 s, 8 workers

| fault | arm | runs | reached % | collision % | stuck % | relocs accepted | wrong commits (> 0.5 m) | still hovering at end | median / p95 / max recover s | moves flown | events with a move => accepted / wrong / open | median recover s after a move | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dropout | (b) single | 100 | 100.0 | 0.0 | 0.0 | 440 | 2 | 2 | 0.2 / 0.2 / 0.2 | - | - | - | 0.303 |
| dropout | (c) multi | 100 | 84.0 | 0.0 | 16.0 | 388 | 0 | 19 | 0.4 / 0.4 / 1.1 | - | - | - | 0.2909 |
| dropout | (d) multi_random | 100 | 93.0 | 0.0 | 7.0 | 412 | 0 | 10 | 0.4 / 0.4 / 12.6 | 42 | 17 => 10 / 0 / 7 | 3.2 | 0.3207 |
| dropout | (e) multi_sep | 100 | 99.0 | 0.0 | 1.0 | 434 | 0 | 4 | 0.4 / 0.7 / 7.3 | 24 | 19 => 18 / 0 / 1 | 2.7 | 0.3233 |
| dropout | (f) multi_ig | 100 | 100.0 | 0.0 | 0.0 | 432 | 0 | 3 | 0.4 / 0.7 / 15.0 | 25 | 19 => 19 / 0 / 0 | 2.9 | 0.3227 |
| jump | (b) single | 100 | 100.0 | 0.0 | 0.0 | 388 | 3 | 1 | 0.2 / 0.2 / 0.2 | - | - | - | 0.3919 |
| jump | (c) multi | 100 | 95.0 | 0.0 | 5.0 | 337 | 0 | 7 | 0.4 / 0.4 / 5.0 | - | - | - | 0.501 |
| jump | (d) multi_random | 100 | 100.0 | 0.0 | 0.0 | 346 | 0 | 2 | 0.4 / 0.4 / 8.7 | 8 | 6 => 6 / 0 / 0 | 3.2 | 0.501 |
| jump | (e) multi_sep | 100 | 99.0 | 0.0 | 1.0 | 346 | 0 | 3 | 0.4 / 0.4 / 3.5 | 8 | 6 => 5 / 0 / 1 | 2.0 | 0.501 |
| jump | (f) multi_ig | 100 | 100.0 | 0.0 | 0.0 | 346 | 0 | 2 | 0.4 / 0.4 / 5.0 | 6 | 6 => 6 / 0 / 0 | 2.55 | 0.501 |
