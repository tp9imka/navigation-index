`python tune.py` (synthetic arena, seed 1, 20 layouts per cell). Cells: reached % / collision %.

## APF escape variants

stall_window: also trigger the escape when distance to B fell < 0.3 m over the last 3 s. wf_weighted: wall direction = weighted mean of close returns instead of the nearest return.

| stall_window | wf_weighted | default random | default u_trap | default narrow_gap | cf4 random | cf4 u_trap | cf4 narrow_gap |
|---|---|---|---|---|---|---|---|
| False | False | 95.0 / 0.0 | 100.0 / 0.0 | 0.0 / 0.0 | 85.0 / 10.0 | 0.0 / 50.0 | 10.0 / 45.0 |
| False | True | 90.0 / 0.0 | 95.0 / 0.0 | 0.0 / 0.0 | 75.0 / 25.0 | 0.0 / 60.0 | 0.0 / 35.0 |
| True | False | 90.0 / 0.0 | 100.0 / 0.0 | 0.0 / 0.0 | 70.0 / 25.0 | 0.0 / 45.0 | 0.0 / 30.0 |
| True | True | 90.0 / 0.0 | 100.0 / 0.0 | 0.0 / 0.0 | 65.0 / 30.0 | 0.0 / 55.0 | 0.0 / 25.0 |

## VFH+ safety distance and thresholds

tau_low = tau_high / 2.

| d_s m | tau_high | default random | default narrow_gap | cf4 random | cf4 narrow_gap |
|---|---|---|---|---|---|
| 0.05 | 12 | 85.0 / 0.0 | 50.0 / 0.0 | 35.0 / 65.0 | 0.0 / 100.0 |
| 0.05 | 24 | 100.0 / 0.0 | 55.0 / 0.0 | 35.0 / 65.0 | 0.0 / 100.0 |
| 0.05 | 48 | 95.0 / 0.0 | 50.0 / 0.0 | 35.0 / 65.0 | 5.0 / 95.0 |
| 0.1 | 12 | 60.0 / 0.0 | 35.0 / 0.0 | 35.0 / 65.0 | 0.0 / 100.0 |
| 0.1 | 24 | 100.0 / 0.0 | 55.0 / 0.0 | 35.0 / 65.0 | 5.0 / 95.0 |
| 0.1 | 48 | 100.0 / 0.0 | 45.0 / 0.0 | 35.0 / 65.0 | 0.0 / 95.0 |
| 0.2 | 12 | 35.0 / 0.0 | 0.0 / 0.0 | 55.0 / 45.0 | 20.0 / 35.0 |
| 0.2 | 24 | 85.0 / 0.0 | 15.0 / 0.0 | 50.0 / 50.0 | 20.0 / 50.0 |
| 0.2 | 48 | 100.0 / 0.0 | 25.0 / 0.0 | 50.0 / 50.0 | 15.0 / 45.0 |

Shipped defaults: APF stall_window False, wf_weighted False; VFH+ d_s 0.1, tau_high 24, tau_low 12. Wall 109 s.
