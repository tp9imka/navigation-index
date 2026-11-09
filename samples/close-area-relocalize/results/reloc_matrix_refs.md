`python run_matrix.py --part refs --layouts 30` (synthetic), wall 166.5 s, 14 workers, seeds [2, 3, 4], 30 layouts per seed per cell. Run time limit 60 s, 120 s for maze and warehouse. Reached % and runs with a wrong commit carry 95 % Wilson intervals. 'still hovering at end' counts loss events open when the run ended, by the last rule verdict.

| family | fault | arm | runs | reached % | 95 % CI | per seed reached % | collision % | stuck % | timeout % | wrong commits (> 0.5 m) | runs with a wrong commit (95 % CI) | still hovering at end: none (< 10 returns) / none (low score) / ambiguous | fault fired runs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random | dropout | (ref) truth | 90 | 100.0 | 95.9-100.0 | 100/100/100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 0 |
| random | dropout | (a) estimator | 90 | 55.6 | 45.3-65.4 | 63.3/50/53.3 | 3.3 | 41.1 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 90 |
| random | jump | (a) estimator | 90 | 27.8 | 19.6-37.8 | 33.3/30/20 | 12.2 | 60.0 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 75 |
| u_trap | dropout | (ref) truth | 90 | 100.0 | 95.9-100.0 | 100/100/100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 0 |
| u_trap | dropout | (a) estimator | 90 | 66.7 | 56.4-75.5 | 70/60/70 | 1.1 | 32.2 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 90 |
| u_trap | jump | (a) estimator | 90 | 21.1 | 14.0-30.6 | 26.7/16.7/20 | 6.7 | 72.2 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 89 |
| narrow_gap | dropout | (ref) truth | 90 | 100.0 | 95.9-100.0 | 100/100/100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 0 |
| narrow_gap | dropout | (a) estimator | 90 | 34.4 | 25.4-44.7 | 33.3/26.7/43.3 | 53.3 | 12.2 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 87 |
| narrow_gap | jump | (a) estimator | 90 | 6.7 | 3.1-13.8 | 6.7/6.7/6.7 | 84.4 | 8.9 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 90 |
| office | dropout | (ref) truth | 90 | 100.0 | 95.9-100.0 | 100/100/100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 0 |
| office | dropout | (a) estimator | 90 | 33.3 | 24.5-43.6 | 30/40/30 | 48.9 | 17.8 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 89 |
| office | jump | (a) estimator | 90 | 7.8 | 3.8-15.2 | 6.7/3.3/13.3 | 77.8 | 13.3 | 1.1 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 89 |
| warehouse | dropout | (ref) truth | 90 | 100.0 | 95.9-100.0 | 100/100/100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 0 |
| warehouse | dropout | (a) estimator | 90 | 66.7 | 56.4-75.5 | 73.3/60/66.7 | 5.6 | 27.8 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 90 |
| warehouse | jump | (a) estimator | 90 | 11.1 | 6.1-19.3 | 13.3/13.3/6.7 | 44.4 | 44.4 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 90 |
| maze | dropout | (ref) truth | 90 | 100.0 | 95.9-100.0 | 100/100/100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 0 |
| maze | dropout | (a) estimator | 90 | 58.9 | 48.6-68.5 | 73.3/40/63.3 | 15.6 | 25.6 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 90 |
| maze | jump | (a) estimator | 90 | 10.0 | 5.4-17.9 | 10/13.3/6.7 | 74.4 | 15.6 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 89 |
| glass_office | dropout | (ref) truth | 90 | 100.0 | 95.9-100.0 | 100/100/100 | 0.0 | 0.0 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 0 |
| glass_office | dropout | (a) estimator | 90 | 43.3 | 33.6-53.6 | 46.7/40/43.3 | 43.3 | 13.3 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 85 |
| glass_office | jump | (a) estimator | 90 | 5.6 | 2.4-12.4 | 0/3.3/13.3 | 85.6 | 8.9 | 0.0 | 0 | 0 (0.0-4.1) | 0 / 0 / 0 | 88 |
