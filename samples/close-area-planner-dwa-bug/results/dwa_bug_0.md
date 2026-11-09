`python bench.py --layouts 50 --seed 0` (synthetic arena, seed 0, 50 layouts per cell), wall 730.7 s

Fans: default = {'n_beams': 72, 'fov': 6.283185307179586, 'max_range': 6.0, 'noise_std': 0.02, 'dropout': 0.02}; cf4 = {'n_beams': 4, 'fov': 6.283185307179586, 'max_range': 4.0, 'noise_std': 0.02, 'dropout': 0.02} (angles in rad).
dwa_mem keeps 3.0 s of returns. apf and vfh_plus are imported unchanged from samples/close-area-planner-reactive.

| planner | fan | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m | median path / A* known |
|---|---|---|---|---|---|---|---|---|---|---|
| dwa | default | random | 50 | 86.0 | 0.0 | 8.0 | 6.0 | 34.86 | 0.28 | 0.98 |
| dwa | default | u_trap | 50 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.292 | - |
| dwa | default | narrow_gap | 50 | 12.0 | 0.0 | 48.0 | 40.0 | 51.19 | 0.272 | 0.96 |
| dwa | cf4 | random | 50 | 30.0 | 52.0 | 18.0 | 0.0 | 26.16 | 0.15 | 0.98 |
| dwa | cf4 | u_trap | 50 | 0.0 | 10.0 | 90.0 | 0.0 | - | 0.196 | - |
| dwa | cf4 | narrow_gap | 50 | 0.0 | 58.0 | 22.0 | 20.0 | - | 0.15 | - |
| dwa_mem | default | random | 50 | 84.0 | 0.0 | 10.0 | 6.0 | 38.43 | 0.264 | 0.98 |
| dwa_mem | default | u_trap | 50 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.289 | - |
| dwa_mem | default | narrow_gap | 50 | 12.0 | 0.0 | 58.0 | 30.0 | 50.91 | 0.263 | 0.96 |
| dwa_mem | cf4 | random | 50 | 36.0 | 18.0 | 40.0 | 6.0 | 26.22 | 0.197 | 0.98 |
| dwa_mem | cf4 | u_trap | 50 | 0.0 | 4.0 | 94.0 | 2.0 | - | 0.225 | - |
| dwa_mem | cf4 | narrow_gap | 50 | 6.0 | 20.0 | 46.0 | 28.0 | 52.72 | 0.182 | 0.96 |
| bug2 | default | random | 50 | 92.0 | 0.0 | 0.0 | 8.0 | 30.16 | 0.498 | 1.02 |
| bug2 | default | u_trap | 50 | 94.0 | 0.0 | 2.0 | 4.0 | 44.44 | 0.476 | 1.29 |
| bug2 | default | narrow_gap | 50 | 0.0 | 0.0 | 0.0 | 100.0 | - | 0.483 | - |
| bug2 | cf4 | random | 50 | 74.0 | 20.0 | 4.0 | 2.0 | 28.62 | 0.297 | 1.0 |
| bug2 | cf4 | u_trap | 50 | 0.0 | 74.0 | 0.0 | 26.0 | - | 0.147 | - |
| bug2 | cf4 | narrow_gap | 50 | 0.0 | 8.0 | 2.0 | 90.0 | - | 0.275 | - |
| tangent_bug | default | random | 50 | 92.0 | 0.0 | 8.0 | 0.0 | 24.66 | 0.418 | 0.97 |
| tangent_bug | default | u_trap | 50 | 86.0 | 0.0 | 14.0 | 0.0 | 31.06 | 0.422 | 1.04 |
| tangent_bug | default | narrow_gap | 50 | 58.0 | 0.0 | 32.0 | 10.0 | 28.0 | 0.318 | 0.95 |
| tangent_bug | cf4 | random | 50 | 38.0 | 62.0 | 0.0 | 0.0 | 24.42 | 0.149 | 0.98 |
| tangent_bug | cf4 | u_trap | 50 | 30.0 | 46.0 | 0.0 | 24.0 | 31.66 | 0.182 | 1.06 |
| tangent_bug | cf4 | narrow_gap | 50 | 4.0 | 96.0 | 0.0 | 0.0 | 26.61 | 0.149 | 0.97 |
| apf | default | random | 50 | 98.0 | 0.0 | 2.0 | 0.0 | 26.0 | 0.774 | 0.99 |
| apf | default | u_trap | 50 | 92.0 | 0.0 | 6.0 | 2.0 | 43.78 | 0.65 | 1.24 |
| apf | default | narrow_gap | 50 | 0.0 | 0.0 | 94.0 | 6.0 | - | 0.646 | - |
| apf | cf4 | random | 50 | 82.0 | 8.0 | 10.0 | 0.0 | 26.58 | 0.474 | 1.01 |
| apf | cf4 | u_trap | 50 | 2.0 | 54.0 | 24.0 | 20.0 | 38.96 | 0.15 | 1.07 |
| apf | cf4 | narrow_gap | 50 | 6.0 | 34.0 | 28.0 | 32.0 | 40.56 | 0.301 | 1.08 |
| vfh_plus | default | random | 50 | 96.0 | 0.0 | 4.0 | 0.0 | 25.68 | 0.278 | 0.98 |
| vfh_plus | default | u_trap | 50 | 0.0 | 0.0 | 94.0 | 6.0 | - | 0.956 | - |
| vfh_plus | default | narrow_gap | 50 | 62.0 | 0.0 | 38.0 | 0.0 | 27.56 | 0.274 | 0.98 |
| vfh_plus | cf4 | random | 50 | 28.0 | 72.0 | 0.0 | 0.0 | 24.62 | 0.148 | 0.99 |
| vfh_plus | cf4 | u_trap | 50 | 0.0 | 98.0 | 2.0 | 0.0 | - | 0.146 | - |
| vfh_plus | cf4 | narrow_gap | 50 | 4.0 | 96.0 | 0.0 | 0.0 | 29.13 | 0.148 | 1.0 |
