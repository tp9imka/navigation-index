`python run_yaw.py --corridor --runs 20` (synthetic), wall 202.6 s, 12 workers

| case | bias deg | arm | runs | yaw fault fired | reached % | collision % | stuck % | wrong commits (> 0.5 m), all events | jump event => accepted / wrong / open | jump event recover s median / p95 | all events recover s median / p95 | still hovering at end | yaw err at end deg median / max | ms per matched scan median / p95 (scans) | median run max err m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| corridor_jump | +-10 | (f) no yaw search | 20 | 20 | 0.0 | 50.0 | 45.0 | 37 | 20 => 17 / 13 / 3 | 7.0 / 11.12 | 0.6 / 10.78 | 9 | 10.0 / 10.0 | 3.65 / 13.32 (2464) | 2.2426 |
| corridor_jump | +-10 | (f) + yaw search +-15 deg | 20 | 20 | 45.0 | 25.0 | 15.0 | 0 | 20 => 15 / 0 / 5 | 11.1 / 11.4 | 0.4 / 11.32 | 5 | 0.25 / 10.25 | 35.0 / 46.83 (2232) | 0.9916 |
| corridor_jump | +-10 | (f) + yaw search + heading first | 20 | 20 | 70.0 | 0.0 | 30.0 | 0 | 20 => 16 / 0 / 4 | 11.05 / 12.18 | 0.4 / 11.3 | 4 | 0.0 / 0.75 | 34.86 / 45.92 (2222) | 0.6023 |
| corridor_jump | 180 | (f) no yaw search | 20 | 20 | 0.0 | 0.0 | 95.0 | 21 | 20 => 15 / 15 / 5 | 11.1 / 11.53 | 0.4 / 11.35 | 5 | 180.0 / 180.0 | 3.57 / 4.99 (2083) | 9.5977 |
| corridor_jump | 180 | (f) + yaw search +-15 deg | 20 | 20 | 0.0 | 0.0 | 100.0 | 22 | 20 => 16 / 16 / 4 | 11.0 / 11.53 | 0.4 / 11.34 | 4 | 180.0 / 180.0 | 34.79 / 46.01 (2100) | 9.6389 |
| corridor_jump | 180 | (f) + yaw search + heading first | 20 | 20 | 0.0 | 0.0 | 100.0 | 22 | 20 => 16 / 16 / 4 | 11.0 / 11.53 | 0.4 / 11.34 | 4 | 180.0 / 180.0 | 34.78 / 45.21 (2100) | 9.6389 |

Static 180 deg twin check, 20 poses near the corridor middle: {"ratio_min": 0.9838, "ratio_median": 0.999, "ratio_max": 1.0285, "poses_ratio_below_rule": 18, "best_is_flipped": 20, "best_is_true": 0, "flipped_in_top5": 20, "best_ratio_true_over_flipped_median": 1.0042, "best_ratio_min": 1.0, "best_ratio_max": 1.0098, "flipped_best_score_median": 0.9719, "flipped_best_score_min": 0.9633, "full_circle_ms_median": 249.7}
