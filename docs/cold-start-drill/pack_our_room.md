# Scenario pack `our_room`

`python pack.py run packs/our_room.json --workers 4` from samples/close-area-benchmark, 2026-11-10. Input: synthetic (simulated world, vehicle and sensor, 2.5D point mass), planner sees the true pose, scored on truth. 105 runs, 4 worker processes, wall 16.4 s, Python 3.11.15, numpy 2.4.6.

Worlds: `our_room` (../../close-area-arena/rooms/our_room.world.json, family custom, limit 60 s).
Vehicle: radius 0.2 m, v_max 1.5 m/s, a_max 3.0 m/s^2, tau 0.15 s. Sensor `depth_cam_87`: 30 beams, fov 87 deg, 0.3-5.0 m, noise 0.04 m, cone 3 deg, dropout 0.05.
Seeds 0-34: seed 0 exact A/B, seeds > 0 move A and B up to 0.5 m (same points for every planner).

Rates: 95 % Wilson interval on distinct runs; `>=` judged on the lower bound, `<=` on the upper. "Runs needed if every run succeeds" is the smallest n whose all-success Wilson bound meets the bar. Counts: every run of that outcome counts; PASS needs at least min_runs distinct runs (default seeds x worlds = 35). A count PASS says "none (or at most k) happened in n runs"; it is not a rate claim, the Wilson bound next to it is what n runs support. Time quantile: distribution-free 95 % interval, a run that did not reach B counts as inf.

| planner | reached_rate >= 0.9 | collisions == 0 (min 35 runs) | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| thetastar_known | PASS: 35/35 = 1.00, CI [0.90, 1.00]; lower 0.90 >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 35 distinct runs; 0 == 0 in 35 >= 35 distinct runs; rate <= 0.10 (95 % Wilson bound, not a rate claim) | PASS: 22.2 s, CI [21.9, 22.3], n=35; upper 22.3 <= 30 | **PASS** |
| astar_known | PASS: 35/35 = 1.00, CI [0.90, 1.00]; lower 0.90 >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 35 distinct runs; 0 == 0 in 35 >= 35 distinct runs; rate <= 0.10 (95 % Wilson bound, not a rate claim) | PASS: 23.7 s, CI [23.6, 24.2], n=35; upper 24.2 <= 30 | **PASS** |
| lazy_thetastar_unknown | FAIL: 17/35 = 0.49, CI [0.33, 0.64]; upper 0.64 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 18 collision in 35 distinct runs; 18 == 0 is false; rate <= 0.67 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [29.3, inf], n=35; upper inf misses <= 30, lower 29.3 meets it | **FAIL** |

- thetastar_known: PASS (35 runs)
- astar_known: PASS (35 runs)
- lazy_thetastar_unknown: FAIL (35 runs)

Exit code 0: at least one planner passes every criterion.

## Outcomes

| planner | runs | reached | collision | stuck | timeout | error |
|---|---|---|---|---|---|---|
| thetastar_known | 35 | 35 | 0 | 0 | 0 | 0 |
| astar_known | 35 | 35 | 0 | 0 | 0 | 0 |
| lazy_thetastar_unknown | 35 | 17 | 18 | 0 | 0 | 0 |
