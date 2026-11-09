`python worlds_complex.py --sanity --layouts 20 --seed 0` (synthetic), wall 117.0 s

| family | planner | reached % | collision % | stuck % | timeout % | median time to goal s | median obstacles | layout draws median / max |
|---|---|---|---|---|---|---|---|---|
| office | straight | 0.0 | 0.0 | 100.0 | 0.0 | - | 26.5 | 1 / 1 |
| office | astar_esdf_known | 100.0 | 0.0 | 0.0 | 0.0 | 21.01 | 26.5 | 1 / 1 |
| warehouse | straight | 0.0 | 0.0 | 100.0 | 0.0 | - | 22 | 1 / 1 |
| warehouse | astar_esdf_known | 100.0 | 0.0 | 0.0 | 0.0 | 43.74 | 22 | 1 / 1 |
| forest | straight | 15.0 | 0.0 | 85.0 | 0.0 | 26.02 | 59 | 1 / 1 |
| forest | astar_esdf_known | 100.0 | 0.0 | 0.0 | 0.0 | 22.72 | 59 | 1 / 1 |
| maze | straight | 0.0 | 5.0 | 95.0 | 0.0 | - | 43 | 1 / 1 |
| maze | astar_esdf_known | 100.0 | 0.0 | 0.0 | 0.0 | 41.03 | 43 | 1 / 1 |
| glass_office | straight | 0.0 | 0.0 | 100.0 | 0.0 | - | 29.5 | 1 / 1 |
| glass_office | astar_esdf_known | 100.0 | 0.0 | 0.0 | 0.0 | 25.12 | 29.5 | 1 / 1 |
