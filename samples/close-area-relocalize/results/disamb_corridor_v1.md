`python run_disambiguate.py --corridor --runs 20 --out /tmp/disamb_try` (synthetic), wall 31.1 s, 8 workers

| fault | arm | runs | reached % | collision % | stuck % | relocs accepted | wrong commits (> 0.5 m) | still hovering at end | median / p95 / max recover s | moves flown | events with a move => accepted / wrong / open | median recover s after a move | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| corridor_jump | (b) single | 20 | 100.0 | 0.0 | 0.0 | 86 | 8 | 0 | 0.2 / 0.2 / 0.2 | - | - | - | 0.4974 |
| corridor_jump | (c) multi | 20 | 0.0 | 0.0 | 100.0 | 15 | 0 | 20 | 0.4 / 0.4 / 0.4 | - | - | - | 0.5733 |
| corridor_jump | (d) multi_random | 20 | 15.0 | 0.0 | 85.0 | 23 | 0 | 17 | 0.4 / 10.98 / 11.9 | 62 | 20 => 3 / 0 / 17 | 11.0 | 0.5733 |
| corridor_jump | (e) multi_sep | 20 | 70.0 | 0.0 | 30.0 | 55 | 0 | 7 | 0.4 / 11.1 / 11.3 | 54 | 20 => 15 / 0 / 5 | 11.0 | 0.5733 |
| corridor_jump | (f) multi_ig | 20 | 75.0 | 0.0 | 25.0 | 58 | 0 | 6 | 0.4 / 11.13 / 11.3 | 55 | 20 => 16 / 0 / 4 | 11.05 | 0.5733 |
