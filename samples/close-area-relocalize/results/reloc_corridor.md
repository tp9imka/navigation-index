`python experiment.py --corridor --runs 20` (synthetic), wall 21.3 s, 8 workers

| fault | arm | runs | reached % | collision % | stuck % | timeout % | triggers reset / q0 / innov | relocs accepted | wrong commits (> 0.5 m) | still hovering at end | median recover s | median run max err m | fault fired runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| corridor_jump | truth | 20 | 100.0 | 0.0 | 0.0 | 0.0 | - | - | - | - | - | - | - |
| corridor_jump | estimator | 20 | 15.0 | 25.0 | 60.0 | 0.0 | - | - | - | - | - | 0.6037 | 20 |
| corridor_jump | hover_only | 20 | 15.0 | 25.0 | 60.0 | 0.0 | 20/0/0 | - | - | 0 | 0.2 | 0.6056 | 20 |
| corridor_jump | single | 20 | 100.0 | 0.0 | 0.0 | 0.0 | 20/0/66 | 86 | 8 | 0 | 0.2 | 0.4974 | 20 |
| corridor_jump | multi | 20 | 0.0 | 0.0 | 100.0 | 0.0 | 20/0/15 | 15 | 0 | 20 | 0.4 | 0.5733 | 20 |
| corridor_jump | single_noinnov | 20 | 20.0 | 40.0 | 40.0 | 0.0 | 20/0/0 | 20 | 10 | 0 | 0.2 | 0.8294 | 20 |
| corridor_jump | multi_noinnov | 20 | 0.0 | 0.0 | 100.0 | 0.0 | 20/0/0 | 0 | 0 | 20 | - | 0.5523 | 20 |
