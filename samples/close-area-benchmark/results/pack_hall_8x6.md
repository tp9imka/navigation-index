# Scenario pack `hall_8x6`

`python pack.py run packs/hall_8x6.json --workers 1` from samples/close-area-benchmark, 2026-11-10. Input: synthetic (simulated world, vehicle and sensor, 2.5D point mass), planner sees the true pose, scored on truth. 60 runs, 1 worker processes, wall 21.1 s, Python 3.12.10, numpy 2.5.4.

Worlds: `hall_8x6` (../../close-area-arena/rooms/hall_8x6.world.json, family custom, limit 60 s).
Vehicle: radius 0.2 m, v_max 2.0 m/s, a_max 3.0 m/s^2, tau 0.15 s. Sensor `depth_cam_87`: 30 beams, fov 87 deg, 0.3-5.0 m, noise 0.04 m, cone 3 deg, dropout 0.05.
Seeds 0-9: seed 0 exact A/B, seeds > 0 move A and B up to 0.5 m (same points for every planner).

Rates: 95 % Wilson interval on distinct runs; `>=` judged on the lower bound, `<=` on the upper. "Runs needed if every run succeeds" is the smallest n whose all-success Wilson bound meets the bar. Counts: every run of that outcome counts; PASS needs at least min_runs distinct runs (default seeds x worlds = 10). A count PASS says "none (or at most k) happened in n runs"; it is not a rate claim, the Wilson bound next to it is what n runs support. Time quantile: distribution-free 95 % interval, a run that did not reach B counts as inf.

| planner | reached_rate >= 0.9 | collisions == 0 (min 10 runs) | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| astar_known | NOT PROVEN: 10/10 = 1.00, CI [0.72, 1.00]; lower 0.72 misses >= 0.9, upper 1.00 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 10 distinct runs; 0 == 0 in 10 >= 10 distinct runs; rate <= 0.28 (95 % Wilson bound, not a rate claim) | PASS: 23.7 s, CI [22.9, 24.6], n=10; upper 24.6 <= 30 | **NOT PROVEN** |
| astar_unknown | FAIL: 3/10 = 0.30, CI [0.11, 0.60]; upper 0.60 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 7 collision in 10 distinct runs; 7 == 0 is false; rate <= 0.89 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [29.2, inf], n=10; upper inf misses <= 30, lower 29.2 meets it | **FAIL** |
| astar_unknown_f2 | FAIL: 0/9 = 0.00, CI [0.00, 0.30]; upper 0.30 misses >= 0.9; runs needed if every run succeeds: 35 | NOT PROVEN: 0 collision in 9 distinct runs (10 flown); 9 distinct runs < min_runs 10; rate <= 0.30 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=9; lower inf misses <= 30 | **FAIL** |
| mppi_astar | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 10 collision in 10 distinct runs; 10 == 0 is false; rate <= 1.00 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |
| tangent_bug | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 2 collision in 10 distinct runs; 2 == 0 is false; rate <= 0.51 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |
| straight | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 10 distinct runs; 0 == 0 in 10 >= 10 distinct runs; rate <= 0.28 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |

- astar_known: NOT PROVEN (10 runs)
- astar_unknown: FAIL (10 runs)
- astar_unknown_f2: FAIL (10 runs)
- mppi_astar: FAIL (10 runs)
- tangent_bug: FAIL (10 runs)
- straight: FAIL (10 runs)

Sample-size hints (the observed runs meet every open bar; only n is short):

- astar_known: NOT PROVEN only on sample size. reached_rate >= 0.9 needs 35 distinct runs if every run succeeds (has 10) => at least 35 seeds x 1 worlds.

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
