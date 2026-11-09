`python run_matrix.py --part rungs --layouts 30` (synthetic), wall 16.5 s, 14 workers, seeds [2], 30 layouts per seed per cell. Run time limit 60 s, 120 s for maze and warehouse. Reached % and runs with a wrong commit carry 95 % Wilson intervals. 'still hovering at end' counts loss events open when the run ended, by the last rule verdict.

| family | fault | arm | runs | reached % | 95 % CI | per seed reached % | collision % | stuck % | timeout % | wrong commits (> 0.5 m) | runs with a wrong commit (95 % CI) | still hovering at end: none (< 10 returns) / none (low score) / ambiguous | fault fired runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | jump_1.0m | (b) single | 30 | 100.0 | 88.6-100.0 | 100 | 0.0 | 0.0 | 0.0 | 2 | 2 (1.8-21.3) | 0 / 0 / 0 | 26 |
| random | jump_1.0m | (c) multi | 30 | 83.3 | 66.4-92.7 | 83.3 | 0.0 | 16.7 | 0.0 | 0 | 0 (0.0-11.4) | 0 / 0 / 4 | 25 |
| random | jump_1.0m | (f) multi_ig | 30 | 100.0 | 88.6-100.0 | 100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-11.4) | 0 / 0 / 0 | 26 |
| random | jump_2.0m | (b) single | 30 | 100.0 | 88.6-100.0 | 100 | 0.0 | 0.0 | 0.0 | 2 | 2 (1.8-21.3) | 0 / 0 / 0 | 26 |
| random | jump_2.0m | (c) multi | 30 | 86.7 | 70.3-94.7 | 86.7 | 0.0 | 13.3 | 0.0 | 0 | 0 (0.0-11.4) | 0 / 0 / 4 | 25 |
| random | jump_2.0m | (f) multi_ig | 30 | 100.0 | 88.6-100.0 | 100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-11.4) | 0 / 0 / 0 | 26 |
| random | dropout_5s | (b) single | 30 | 100.0 | 88.6-100.0 | 100 | 0.0 | 0.0 | 0.0 | 2 | 2 (1.8-21.3) | 0 / 0 / 0 | 30 |
| random | dropout_5s | (c) multi | 30 | 76.7 | 59.1-88.2 | 76.7 | 0.0 | 23.3 | 0.0 | 0 | 0 (0.0-11.4) | 4 / 0 / 3 | 30 |
| random | dropout_5s | (f) multi_ig | 30 | 100.0 | 88.6-100.0 | 100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-11.4) | 0 / 0 / 0 | 30 |
