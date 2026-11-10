# Scenario pack `hall_8x6`

`python pack.py run packs/hall_8x6.json --workers 14` from samples/close-area-benchmark, 2026-11-10. Input: synthetic (simulated world, vehicle and sensor, 2.5D point mass), planner sees the true pose, scored on truth. 60 runs, 14 worker processes, wall 8.3 s, Python 3.12.10, numpy 2.5.4.

Worlds: `hall_8x6` (../../close-area-arena/rooms/hall_8x6.world.json, family custom, limit 60 s).
Vehicle: radius 0.2 m, v_max 2.0 m/s, a_max 3.0 m/s^2, tau 0.15 s. Sensor `depth_cam_87`: 30 beams, fov 87 deg, 0.3-5.0 m, noise 0.04 m, cone 3 deg, dropout 0.05.
Seeds 0-9: seed 0 exact A/B, seeds > 0 move A and B up to 0.5 m (same points for every planner).

Rates: 95 % Wilson interval on distinct runs; `>=` judged on the lower bound, `<=` on the upper. Time quantile: distribution-free 95 % interval, a run that did not reach B counts as inf.

| planner | reached_rate >= 0.9 | collision_rate <= 0 | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| astar_known | NOT PROVEN: 10/10 = 1.00, CI [0.72, 1.00]; lower 0.72 misses >= 0.9, upper 1.00 meets it | NOT PROVEN: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses <= 0, lower 0.00 meets it | PASS: 23.7 s, CI [22.9, 24.6], n=10; upper 24.6 <= 30 | **NOT PROVEN** |
| astar_unknown | FAIL: 3/10 = 0.30, CI [0.11, 0.60]; upper 0.60 misses >= 0.9 | FAIL: 7/10 = 0.70, CI [0.40, 0.89]; lower 0.40 misses <= 0 | NOT PROVEN: inf s, CI [29.2, inf], n=10; upper inf misses <= 30, lower 29.2 meets it | **FAIL** |
| astar_unknown_f2 | FAIL: 0/9 = 0.00, CI [0.00, 0.30]; upper 0.30 misses >= 0.9 | NOT PROVEN: 0/9 = 0.00, CI [0.00, 0.30]; upper 0.30 misses <= 0, lower 0.00 meets it | FAIL: inf s, CI [inf, inf], n=9; lower inf misses <= 30 | **FAIL** |
| mppi_astar | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9 | FAIL: 10/10 = 1.00, CI [0.72, 1.00]; lower 0.72 misses <= 0 | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |
| tangent_bug | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9 | FAIL: 2/10 = 0.20, CI [0.06, 0.51]; lower 0.06 misses <= 0 | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |
| straight | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9 | NOT PROVEN: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses <= 0, lower 0.00 meets it | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |

- astar_known: NOT PROVEN (10 runs)
- astar_unknown: FAIL (10 runs)
- astar_unknown_f2: FAIL (10 runs)
- mppi_astar: FAIL (10 runs)
- tangent_bug: FAIL (10 runs)
- straight: FAIL (10 runs)

Exit code 1: no planner passes every criterion.

## Outcomes

| planner | runs | reached | collision | stuck | timeout | error |
|---|---|---|---|---|---|---|
| astar_known | 10 | 10 | 0 | 0 | 0 | 0 |
| astar_unknown | 10 | 3 | 7 | 0 | 0 | 0 |
| astar_unknown_f2 | 10 | 0 | 0 | 10 | 0 | 0 |
| mppi_astar | 10 | 0 | 10 | 0 | 0 | 0 |
| tangent_bug | 10 | 0 | 2 | 7 | 1 | 0 |
| straight | 10 | 0 | 0 | 10 | 0 | 0 |
