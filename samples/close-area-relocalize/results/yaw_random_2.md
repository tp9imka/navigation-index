`python run_yaw.py --layouts 100 --seed 2` (synthetic), wall 123.6 s, 12 workers

| case | bias deg | arm | runs | yaw fault fired | reached % | collision % | stuck % | wrong commits (> 0.5 m), all events | jump event => accepted / wrong / open | jump event recover s median / p95 | all events recover s median / p95 | still hovering at end | yaw err at end deg median / max | ms per matched scan median / p95 (scans) | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| jump | 0 | (f) no yaw search | 100 | 86 | 100.0 | 0.0 | 0.0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 1.69 | 0.4 / 0.4 | 2 | 0.0 / 0.0 | 1.8 / 3.35 (1285) | 0.4957 |
| jump | 0 | (f) + yaw search +-15 deg | 100 | 86 | 100.0 | 0.0 | 0.0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.88 | 0.4 / 0.6 | 2 | 0.25 / 1.0 | 20.12 / 42.79 (1633) | 0.4919 |
| jump | 0 | (f) + yaw search + heading first | 100 | 86 | 100.0 | 0.0 | 0.0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.88 | 0.4 / 0.6 | 2 | 0.25 / 1.0 | 20.87 / 46.39 (1635) | 0.4919 |
| jump | +-5 | (f) no yaw search | 100 | 86 | 38.0 | 0.0 | 62.0 | 7 | 82 => 68 / 1 / 14 | 0.4 / 6.13 | 0.4 / 7.17 | 83 | 5.0 / 5.0 | 7.01 / 24.98 (19298) | 0.7239 |
| jump | +-5 | (f) + yaw search +-15 deg | 100 | 86 | 100.0 | 0.0 | 0.0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.6 | 0.4 / 0.62 | 6 | 0.25 / 0.75 | 23.49 / 62.78 (1567) | 0.4955 |
| jump | +-5 | (f) + yaw search + heading first | 100 | 86 | 100.0 | 0.0 | 0.0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.6 | 0.4 / 0.64 | 8 | 0.25 / 0.75 | 23.72 / 64.17 (1561) | 0.4955 |
| jump | +-10 | (f) no yaw search | 100 | 86 | 18.0 | 7.0 | 74.0 | 52 | 82 => 52 / 16 / 30 | 0.4 / 6.05 | 0.4 / 4.49 | 84 | 10.0 / 10.0 | 7.07 / 24.41 (20392) | 1.0777 |
| jump | +-10 | (f) + yaw search +-15 deg | 100 | 86 | 100.0 | 0.0 | 0.0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.78 | 0.4 / 0.6 | 2 | 0.25 / 1.0 | 23.42 / 55.94 (1603) | 0.5002 |
| jump | +-10 | (f) + yaw search + heading first | 100 | 86 | 100.0 | 0.0 | 0.0 | 0 | 82 => 82 / 0 / 0 | 0.4 / 2.39 | 0.4 / 0.6 | 2 | 0.25 / 1.0 | 20.96 / 43.22 (1591) | 0.5007 |
