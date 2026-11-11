`python3 samples/close-area-benchmark/results/cross_check_loop73.py`. Input: synthetic. Checks for the 7 rows added by `bench.py --add-to matrix_0` on 2026-11-10.

1. Older rows unchanged vs the committed matrix_0.json (git HEAD): 4480 runs identical, summaries identical.

2. Matrix rows vs the source sample's own run (same family, preset, layout index, seed 0), identical in outcome, min_clearance_m, time_to_goal_s, path_length_m:

| source file | matrix row | preset | runs identical |
|---|---|---|---|
| samples/close-area-planner-thetastar/results/flights_0.json | thetastar_unknown | ideal | 160/160 |
| samples/close-area-planner-thetastar/results/flights_0.json | lazy_thetastar_unknown | ideal | 160/160 |
| samples/close-area-planner-thetastar/results/flights_0.json | thetastar_known | ideal | 160/160 |
| samples/close-area-planner-thetastar/results/flights_0.json | lazy_thetastar_known | ideal | 160/160 |
| samples/close-area-planner-thetastar/results/flights_0.json | thetastar_unknown | crazyflie | 40/40 |
| samples/close-area-planner-thetastar/results/flights_0.json | lazy_thetastar_unknown | crazyflie | 40/40 |
| samples/close-area-planner-mppi/results/bench_ideal_0.json | mppi | ideal | 160/160 |
| samples/close-area-planner-mppi/results/bench_ideal_0.json | mppi_astar | ideal | 160/160 |
| samples/close-area-planner-mppi/results/bench_crazyflie_0.json | mppi | crazyflie | 40/40 |
| samples/close-area-planner-mppi/results/bench_crazyflie_0.json | mppi_astar | crazyflie | 40/40 |
| samples/close-area-planner-hybrid-astar/results/bench_0.json | hybrid_astar | ideal | 160/160 |
| samples/close-area-planner-hybrid-astar/results/bench_0.json | hybrid_astar | crazyflie | 40/40 |

Differences: 0
