`python bench.py --layouts 50 --seed 0` (synthetic arena, seed 0, 50 layouts per cell), wall 75.8 s

Fans: default = {'n_beams': 72, 'fov': 6.283185307179586, 'max_range': 6.0, 'noise_std': 0.02, 'dropout': 0.02}; cf4 = {'n_beams': 4, 'fov': 6.283185307179586, 'max_range': 4.0, 'noise_std': 0.02, 'dropout': 0.02} (angles in rad).

| planner | fan | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m |
|---|---|---|---|---|---|---|---|---|---|
| apf | default | random | 50 | 98.0 | 0.0 | 2.0 | 0.0 | 26.0 | 0.774 |
| apf | default | u_trap | 50 | 92.0 | 0.0 | 6.0 | 2.0 | 43.78 | 0.65 |
| apf | default | narrow_gap | 50 | 0.0 | 0.0 | 94.0 | 6.0 | - | 0.646 |
| apf | cf4 | random | 50 | 82.0 | 8.0 | 10.0 | 0.0 | 26.58 | 0.474 |
| apf | cf4 | u_trap | 50 | 2.0 | 54.0 | 24.0 | 20.0 | 38.96 | 0.15 |
| apf | cf4 | narrow_gap | 50 | 6.0 | 34.0 | 28.0 | 32.0 | 40.56 | 0.301 |
| apf_noescape | default | random | 50 | 86.0 | 0.0 | 14.0 | 0.0 | 25.68 | 0.792 |
| apf_noescape | default | u_trap | 50 | 2.0 | 0.0 | 98.0 | 0.0 | 36.32 | 0.877 |
| apf_noescape | default | narrow_gap | 50 | 0.0 | 0.0 | 88.0 | 12.0 | - | 0.736 |
| apf_noescape | cf4 | random | 50 | 62.0 | 6.0 | 32.0 | 0.0 | 25.96 | 0.56 |
| apf_noescape | cf4 | u_trap | 50 | 0.0 | 2.0 | 98.0 | 0.0 | - | 0.561 |
| apf_noescape | cf4 | narrow_gap | 50 | 0.0 | 6.0 | 90.0 | 4.0 | - | 0.414 |
| vfh_plus | default | random | 50 | 96.0 | 0.0 | 4.0 | 0.0 | 25.68 | 0.278 |
| vfh_plus | default | u_trap | 50 | 0.0 | 0.0 | 94.0 | 6.0 | - | 0.956 |
| vfh_plus | default | narrow_gap | 50 | 62.0 | 0.0 | 38.0 | 0.0 | 27.56 | 0.274 |
| vfh_plus | cf4 | random | 50 | 28.0 | 72.0 | 0.0 | 0.0 | 24.62 | 0.148 |
| vfh_plus | cf4 | u_trap | 50 | 0.0 | 98.0 | 2.0 | 0.0 | - | 0.146 |
| vfh_plus | cf4 | narrow_gap | 50 | 4.0 | 96.0 | 0.0 | 0.0 | 29.13 | 0.148 |

| planner | fan | family | where runs ended (count) | median end distance to B, failed runs, m | escape / stop |
|---|---|---|---|---|---|
| apf | default | random | reached 49, near_obstacle 1 | 4.92 | escape in 13, reached after escape 12 |
| apf | default | u_trap | reached 46, in_cup 2, outside_cup 2 | 12.79 | escape in 50, reached after escape 46 |
| apf | default | narrow_gap | before_wall 50 | 17.05 | escape in 50, reached after escape 0 |
| apf | cf4 | random | reached 41, near_obstacle 9 | 16.04 | escape in 23, reached after escape 16 |
| apf | cf4 | u_trap | in_cup 25, outside_cup 24, reached 1 | 15.2 | escape in 49, reached after escape 1 |
| apf | cf4 | narrow_gap | before_wall 31, at_gap 16, reached 3 | 14.32 | escape in 49, reached after escape 3 |
| apf_noescape | default | random | reached 43, open 4, near_obstacle 3 | 16.29 | escape in 0, reached after escape 0 |
| apf_noescape | default | u_trap | in_cup 48, outside_cup 1, reached 1 | 11.66 | escape in 0, reached after escape 0 |
| apf_noescape | default | narrow_gap | before_wall 43, at_gap 7 | 9.71 | escape in 0, reached after escape 0 |
| apf_noescape | cf4 | random | reached 31, near_obstacle 15, open 4 | 14.88 | escape in 0, reached after escape 0 |
| apf_noescape | cf4 | u_trap | in_cup 45, outside_cup 5 | 11.75 | escape in 0, reached after escape 0 |
| apf_noescape | cf4 | narrow_gap | before_wall 30, at_gap 20 | 10.57 | escape in 0, reached after escape 0 |
| vfh_plus | default | random | reached 48, open 2 | 3.67 | no-valley stop in 0 |
| vfh_plus | default | u_trap | in_cup 50 | 12.08 | no-valley stop in 0 |
| vfh_plus | default | narrow_gap | reached 31, before_wall 18, at_gap 1 | 9.96 | no-valley stop in 1 |
| vfh_plus | cf4 | random | near_obstacle 36, reached 14 | 12.39 | no-valley stop in 0 |
| vfh_plus | cf4 | u_trap | in_cup 44, outside_cup 6 | 11.09 | no-valley stop in 0 |
| vfh_plus | cf4 | narrow_gap | before_wall 42, at_gap 6, reached 2 | 12.86 | no-valley stop in 0 |
