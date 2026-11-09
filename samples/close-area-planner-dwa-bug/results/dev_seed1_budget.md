`python tune.py --budget-check --layouts 20 --seed 1` (synthetic arena, dev seed 1, 20 narrow_gap layouts, default fan), wall 14.0 s

| planner | budget s | reached % | collision % | stuck % | timeout % | median time to goal s | runs ending in Bug2 FAIL (back at hit point) |
|---|---|---|---|---|---|---|---|
| bug2 | 60 | 0.0 | 0.0 | 0.0 | 100.0 | None | 0 |
| bug2 | 180 | 0.0 | 0.0 | 100.0 | 0.0 | None | 20 |
| tangent_bug | 60 | 55.0 | 0.0 | 25.0 | 20.0 | 27.1 | 0 |
| tangent_bug | 180 | 55.0 | 0.0 | 30.0 | 15.0 | 27.1 | 0 |
