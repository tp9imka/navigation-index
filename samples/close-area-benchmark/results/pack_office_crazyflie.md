# Scenario pack `office_crazyflie`

`python pack.py run packs/office_crazyflie.json --workers 1` from samples/close-area-benchmark, 2026-11-12. Input: synthetic (simulated world, vehicle and sensor, 2.5D point mass), planner sees the true pose, scored on truth. 75 runs, 1 worker processes, wall 56.2 s, Python 3.12.10, numpy 2.5.4.

Worlds: `office_0` (preset:office_0, family office, limit 60 s); `office_1` (family:office:1, family office, limit 60 s); `office_2` (family:office:2, family office, limit 60 s).
Vehicle: radius 0.15 m, v_max 2.0 m/s, a_max 3.0 m/s^2, tau 0.15 s. Sensor `crazyflie`: 4 beams, fov 360 deg, 0.04-3.0 m, noise 0.02 m, cone 27 deg, dropout 0.05.
Seeds 0-4: seed 0 exact A/B, seeds > 0 move A and B up to 0.5 m (same points for every planner).
Planner inflation: 0.15 m (shipped 0.15 m constants).

Rates: 95 % Wilson interval on distinct runs; `>=` judged on the lower bound, `<=` on the upper. "Runs needed if every run succeeds" is the smallest n whose all-success Wilson bound meets the bar. Counts: every run of that outcome counts; PASS needs at least min_runs distinct runs (default seeds x worlds = 15). A count PASS says "none (or at most k) happened in n runs"; it is not a rate claim, the Wilson bound next to it is what n runs support. Time quantile: distribution-free 95 % interval, a run that did not reach B counts as inf.

| planner | reached_rate >= 0.9 | collisions == 0 (min 15 runs) | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| astar_known | NOT PROVEN: 15/15 = 1.00, CI [0.80, 1.00]; lower 0.80 misses >= 0.9, upper 1.00 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | PASS: 18.1 s, CI [13.8, 22.6], n=15; upper 22.6 <= 30 | **NOT PROVEN** |
| astar_unknown | FAIL: 5/15 = 0.33, CI [0.15, 0.58]; upper 0.58 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 4 collision in 15 distinct runs; 4 == 0 is false; rate <= 0.52 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [27.5, inf], n=15; upper inf misses <= 30, lower 27.5 meets it | **FAIL** |
| astar_unknown_f2 | NOT PROVEN: 13/15 = 0.87, CI [0.62, 0.96]; lower 0.62 misses >= 0.9, upper 0.96 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | NOT PROVEN: 28.2 s, CI [18.4, 32.3], n=15; upper 32.3 misses <= 30, lower 18.4 meets it | **NOT PROVEN** |
| lazy_thetastar_unknown | FAIL: 7/15 = 0.47, CI [0.25, 0.70]; upper 0.70 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 5 collision in 15 distinct runs; 5 == 0 is false; rate <= 0.58 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [17.4, inf], n=15; upper inf misses <= 30, lower 17.4 meets it | **FAIL** |
| dwa_mem | FAIL: 1/15 = 0.07, CI [0.01, 0.30]; upper 0.30 misses >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=15; lower inf misses <= 30 | **FAIL** |

- astar_known: NOT PROVEN (15 runs)
- astar_unknown: FAIL (15 runs)
- astar_unknown_f2: NOT PROVEN (15 runs)
- lazy_thetastar_unknown: FAIL (15 runs)
- dwa_mem: FAIL (15 runs)

Sample-size hints (the observed runs meet every open bar; only n is short):

- astar_known: NOT PROVEN only on sample size. reached_rate >= 0.9 needs 35 distinct runs if every run succeeds (has 15) => at least 12 seeds x 3 worlds.

Exit code 1: no planner passes every criterion.

## Outcomes

| planner | runs | reached | collision | stuck | timeout | error |
|---|---|---|---|---|---|---|
| astar_known | 15 | 15 | 0 | 0 | 0 | 0 |
| astar_unknown | 15 | 5 | 4 | 5 | 1 | 0 |
| astar_unknown_f2 | 15 | 13 | 0 | 2 | 0 | 0 |
| lazy_thetastar_unknown | 15 | 7 | 5 | 3 | 0 | 0 |
| dwa_mem | 15 | 1 | 0 | 14 | 0 | 0 |
