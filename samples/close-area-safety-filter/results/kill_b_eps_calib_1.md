`python run_kill.py --calibrate --layouts 100 --seed 1 --workers 14` (synthetic), wall 6.1 s

F4 bound calibration: per-run maximum of the estimate's state error |(dp, dv)| against truth, arm F2, case none (dark zones, no injected fault), unsensed off, 100 layouts, seed 1.

| statistic over runs | state error (m, m/s) | position error m |
|---|---|---|
| median | 0.4103 | 0.386 |
| 95th percentile | 0.768 | 0.7565 |
| max (=> F4 eps_m) | 1.0558 | 0.9907 |
