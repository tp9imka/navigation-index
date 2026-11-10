# Scenario pack `office_crazyflie`

`python pack.py run packs/office_crazyflie.json --workers 14` from samples/close-area-benchmark, 2026-11-10. Input: synthetic (simulated world, vehicle and sensor, 2.5D point mass), planner sees the true pose, scored on truth. 75 runs, 14 worker processes, wall 14.3 s, Python 3.12.10, numpy 2.5.4.

Worlds: `office_0` (preset:office_0, family office, limit 60 s); `office_1` (family:office:1, family office, limit 60 s); `office_2` (family:office:2, family office, limit 60 s).
Vehicle: radius 0.15 m, v_max 2.0 m/s, a_max 3.0 m/s^2, tau 0.15 s. Sensor `crazyflie`: 4 beams, fov 360 deg, 0.04-3.0 m, noise 0.02 m, cone 27 deg, dropout 0.05.
Seeds 0-4: seed 0 exact A/B, seeds > 0 move A and B up to 0.5 m (same points for every planner).

Rates: 95 % Wilson interval on distinct runs; `>=` judged on the lower bound, `<=` on the upper. Time quantile: distribution-free 95 % interval, a run that did not reach B counts as inf.

| planner | reached_rate >= 0.9 | collision_rate <= 0 | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| astar_known | NOT PROVEN: 15/15 = 1.00, CI [0.80, 1.00]; lower 0.80 misses >= 0.9, upper 1.00 meets it | NOT PROVEN: 0/15 = 0.00, CI [0.00, 0.20]; upper 0.20 misses <= 0, lower 0.00 meets it | PASS: 18.1 s, CI [13.8, 22.6], n=15; upper 22.6 <= 30 | **NOT PROVEN** |
| astar_unknown | FAIL: 6/15 = 0.40, CI [0.20, 0.64]; upper 0.64 misses >= 0.9 | FAIL: 3/15 = 0.20, CI [0.07, 0.45]; lower 0.07 misses <= 0 | NOT PROVEN: inf s, CI [18.2, inf], n=15; upper inf misses <= 30, lower 18.2 meets it | **FAIL** |
| astar_unknown_f2 | NOT PROVEN: 12/15 = 0.80, CI [0.55, 0.93]; lower 0.55 misses >= 0.9, upper 0.93 meets it | NOT PROVEN: 0/15 = 0.00, CI [0.00, 0.20]; upper 0.20 misses <= 0, lower 0.00 meets it | NOT PROVEN: 26.6 s, CI [18.3, 32.3], n=15; upper 32.3 misses <= 30, lower 18.3 meets it | **NOT PROVEN** |
| lazy_thetastar_unknown | FAIL: 7/15 = 0.47, CI [0.25, 0.70]; upper 0.70 misses >= 0.9 | FAIL: 5/15 = 0.33, CI [0.15, 0.58]; lower 0.15 misses <= 0 | NOT PROVEN: inf s, CI [19.5, inf], n=15; upper inf misses <= 30, lower 19.5 meets it | **FAIL** |
| dwa_mem | FAIL: 1/15 = 0.07, CI [0.01, 0.30]; upper 0.30 misses >= 0.9 | NOT PROVEN: 0/15 = 0.00, CI [0.00, 0.20]; upper 0.20 misses <= 0, lower 0.00 meets it | FAIL: inf s, CI [inf, inf], n=15; lower inf misses <= 30 | **FAIL** |

- astar_known: NOT PROVEN (15 runs)
- astar_unknown: FAIL (15 runs)
- astar_unknown_f2: NOT PROVEN (15 runs)
- lazy_thetastar_unknown: FAIL (15 runs)
- dwa_mem: FAIL (15 runs)

Exit code 1: no planner passes every criterion.

## Outcomes

| planner | runs | reached | collision | stuck | timeout | error |
|---|---|---|---|---|---|---|
| astar_known | 15 | 15 | 0 | 0 | 0 | 0 |
| astar_unknown | 15 | 6 | 3 | 5 | 1 | 0 |
| astar_unknown_f2 | 15 | 12 | 0 | 3 | 0 | 0 |
| lazy_thetastar_unknown | 15 | 7 | 5 | 3 | 0 | 0 |
| dwa_mem | 15 | 1 | 0 | 14 | 0 | 0 |
