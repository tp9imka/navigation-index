`python bench.py --layouts 5 --seed 0 --workers 1 --planners astar_unknown,hybrid_astar --vehicles stock --families random,office,maze --cf-families  --stem timing_jobs1_0` from samples/close-area-planner-hybrid-astar. Input: synthetic (simulated layouts, vehicle and sensor). Seed 0, 5 layouts per cell, 1 processes, wall 56.5 s. Planner maps: unknown (log-odds from range hits), geofenced.

Parity: astar_unknown on the stock vehicle vs close-area-benchmark/results/matrix_0.json, same outcome, min clearance and path length: 15/15 runs.

Replan ms are pooled over every replan of the cell, measured with all processes busy (not a clean timing; see timing_jobs1_0.md). Flown max / p95 heading change per metre: median over runs that reached B, truth path resampled every 0.25 m. Stuck while moving = scorer outcome stuck (|p(t) - p(t - 10 s)| < 0.2 m) with truth speed above 0.3 m/s over the last 0.5 s: the vehicle was flying back over the point it passed 10 s earlier (a dead end turned back from), not hovering. The arena scorer ends those runs; they count as stuck here too.

| vehicle | preset | planner | family | reached % | collision % | stuck % | timeout % | median time to B s | median path m | median min clearance m | flown max rad/m | flown p95 rad/m | replan ms median / p95 | grid fallback % of replans | stuck while moving % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| stock | ideal | astar_unknown | random | 100 | 0 | 0 | 0 | 18.38 | 23.95 | 0.608 | 0.474 | 0.151 | 29.66 / 84.48 | - | 0 |
| stock | ideal | astar_unknown | office | 100 | 0 | 0 | 0 | 24.56 | 13.758 | 0.242 | 2.653 | 1.45 | 6.82 / 23.26 | - | 0 |
| stock | ideal | astar_unknown | maze | 100 | 0 | 0 | 0 | 45.64 | 37.733 | 0.582 | 2.534 | 1.803 | 25.34 / 75.95 | - | 0 |
| stock | ideal | hybrid_astar | random | 100 | 0 | 0 | 0 | 18.54 | 23.971 | 0.609 | 0.663 | 0.166 | 11.89 / 23.8 | 0 | 0 |
| stock | ideal | hybrid_astar | office | 100 | 0 | 0 | 0 | 26.38 | 14.158 | 0.296 | 2.105 | 1.343 | 13.61 / 28.79 | 0 | 0 |
| stock | ideal | hybrid_astar | maze | 80 | 0 | 0 | 20 | 41.97 | 40.683 | 0.334 | 3.268 | 1.274 | 11.54 / 16.03 | 0 | 0 |

Totals per vehicle and preset (all families of the preset pooled):

| vehicle | preset | planner | runs | reached % | collision % | stuck % | stuck while moving % | timeout % | replan ms median / p95 |
|---|---|---|---|---|---|---|---|---|---|
| stock | ideal | astar_unknown | 15 | 100 | 0 | 0 | 0 | 0 | 14.12 / 75.57 |
| stock | ideal | hybrid_astar | 15 | 93.3 | 0 | 0 | 0 | 6.7 | 11.88 / 21.48 |

Replan wall time pooled over every replan of the file, per planner:

| planner | replans | median ms | p95 ms | p99 ms | max ms | replans > 200 ms |
|---|---|---|---|---|---|---|
| astar_unknown | 1171 | 14.12 | 75.57 | 92.01 | 129.06 | 0 |
| hybrid_astar | 1324 | 11.88 | 21.48 | 33.43 | 60.12 | 0 |

Paired: median of (planner - astar_unknown) time to B on runs where both reached, per vehicle (both presets):

| vehicle | planner | median delta time to B s | paired runs | median delta path m |
|---|---|---|---|---|
| stock | hybrid_astar | -0.87 | 14 | 0.48 |
