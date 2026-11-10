# Recommend: random_0

**Synthetic 2.5D simulation, scored on truth, not a flight result; 5 seeds on one map is a small sample.**

Solver headline: 17 planners tie at the top; run Thorough or more seeds to separate them (n=15 per planner, best 12/15 reached B, 95 % CI 55 %-93 %).

## Pick: no clear winner, tied set of 17, 1 clearly worse

Every planner whose 95 % Wilson interval overlaps the best one's (Lazy Theta*, unknown map (geofenced), 55 %-93 %). The command below flies the top of the ranking (success, then median time to B); any row is an equally supported choice at this n.

### Tied with the best (17)

| planner | bench id | reached | 95 % Wilson | n | n distinct | median time to B s | min clearance m | collisions |
|---|---|---|---|---|---|---|---|---|
| Lazy Theta*, unknown map (geofenced) | lazy_thetastar_unknown | 12/15 | 55 %-93 % | 15 | 15 | 17.69 | 0.506 | 0 |
| D* Lite, unknown map (geofenced) | dstar_lite | 12/15 | 55 %-93 % | 15 | 15 | 20.25 | 0.516 | 0 |
| Hybrid A*, unknown map (geofenced) | hybrid_astar | 11/15 | 48 %-89 % | 15 | 15 | 19.20 | 0.361 | 0 |
| A* + ESDF, unknown map | astar_unknown | 11/15 | 48 %-89 % | 15 | 15 | 20.52 | 0.450 | 0 |
| Theta* (any-angle), known map | thetastar_known | 10/15 | 42 %-85 % | 15 | 15 | 17.08 | 0.334 | 0 |
| Lazy Theta*, known map | lazy_thetastar_known | 10/15 | 42 %-85 % | 15 | 15 | 17.10 | 0.292 | 0 |
| A* + ESDF, known map | astar_known | 10/15 | 42 %-85 % | 15 | 15 | 19.38 | 0.144 | 4 |
| Informed RRT* 5000, known map | informed_rrt_star | 10/15 | 42 %-85 % | 15 | 15 | 26.64 | 0.148 | 5 |
| Bug2 | bug2 | 10/15 | 42 %-85 % | 15 | 15 | 30.32 | 0.352 | 0 |
| APF + wall follow | apf_escape | 10/15 | 42 %-85 % | 15 | 15 | 30.58 | 0.438 | 0 |
| TangentBug | tangent_bug | 9/15 | 36 %-80 % | 15 | 15 | 25.64 | 0.148 | 1 |
| MPPI, goal only (no global plan) | mppi | 8/15 | 30 %-75 % | 15 | 15 | 20.87 | 0.126 | 3 |
| DWA + 3 s scan memory | dwa_mem | 8/15 | 30 %-75 % | 15 | 15 | 46.07 | 0.180 | 0 |
| MPPI on the unknown-map A* path | mppi_astar | 7/15 | 25 %-70 % | 15 | 15 | 20.26 | 0.128 | 4 |
| freest beam (reactive) | freest_beam | 7/15 | 25 %-70 % | 15 | 15 | 26.12 | 0.278 | 0 |
| VFH+ | vfh_plus | 7/15 | 25 %-70 % | 15 | 15 | 26.34 | 0.142 | 3 |
| DWA (dynamic window) | dwa | 6/15 | 20 %-64 % | 15 | 15 | 43.27 | 0.148 | 2 |

Pareto-optimal: Lazy Theta*, unknown map (geofenced) (17.69 s, 0.506 m), D* Lite, unknown map (geofenced) (20.25 s, 0.516 m), Theta* (any-angle), known map (17.08 s, 0.334 m). Fast and safe among the 17 tied planners, pooled over every variation of the sweep: no other tied planner is as fast to B (median) and as far from every surface (min clearance) and better in one.

### Clearly worse (1)

95 % Wilson interval does not overlap the best one's.

| planner | bench id | reached | 95 % Wilson | n | n distinct | median time to B s | min clearance m | collisions |
|---|---|---|---|---|---|---|---|---|
| straight line to B | straight | 0/15 | 0 %-20 % | 15 | 15 | - | 0.148 | 3 |

What more seeds buy: Quick separates 5/5 from 0/5; telling 5/5 from 4/5 needs about 33 seeds (95 % Wilson: 5/5 57 %-100 %, 0/5 0 %-43 %). The tied set spans 80 % to 40 %; separating those two rates needs about 21 distinct runs per planner (Thorough flies 10 seeds per sensor).

## Fly it: templates/flight-repo

```sh
cd templates/flight-repo
make first-flight PLANNER=bench:lazy_thetastar_unknown WORLD=../../site/playground/presets/random_0.json ARM=F2
```

Writes results/first_flight_bench_lazy_thetastar_unknown_random_0.jsonl, .png and _score.json (score_log.py). ARM=F2 (default): the narrowest passage is 3.60 m, at least 1.4 m.

- World file: Preset random_0: the hub ships it at site/playground/presets/random_0.json (the path below is relative to templates/flight-repo). The same world is inline in recommend.json ("world").
- Narrowest passage: 3.60 m (bottleneck clearance 1.799 m at 8.988, 14.105); proxy 2 x the pick's min clearance = 1.01 m, not used.
- How: Narrowest passage = 2 x the bottleneck clearance of the best route A=>B on a 0.05 m ESDF grid of the world (maximin search, cells within 0.7 m of A free, goal = within 0.2 m of B). Chosen over 2 x the winner's min clearance because a run's min clearance is its closest approach to any surface (a corner it cut), not the width it had to pass: in site/solver/results/quick_random_0.json D* Lite's 0.583 m gives 1.17 m (=> F0) on a map whose best route never narrows below 3.6 m. Grid error up to about 0.05 m.
- The command flies run.DEFAULTS, not the sweep: vehicle radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s; sensor ideal: 72 beams, 360 deg, 6 m, noise 0.02 m, dropout 0.02 (run.DEFAULTS); pose truth; seed 0; the world file's exact A and B; 20 Hz loop with the arm filter.

## What the sweep flew

- Vehicle: radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s (arena default)
- Sensor ideal: 72 beams, FoV 360 deg, 0-6 m, noise 0.02 m
- Sensor crazyflie: 4 beams, FoV 360 deg, 0.04-3 m, noise 0.02 m
- Variations: ideal / truth pose; ideal / VIO jump; crazyflie / truth pose
- Yaw: asked fixed, worker reported off
- Start/goal jitter: 0.5 m radius (seed 0 exact map)
- Run time limit: 60 s of sim time (Auto: random family, default).
- Seeds: 5 (0..4), 270 runs; finished 2026-11-10T10:08:07.198Z

## Benchmark rows for lazy_thetastar_unknown (beyond this map)

From site/playground/data/advisor.json (built from samples/close-area-benchmark/results/matrix_0.json): 20 layouts per family, seed 0, true pose (no VIO, no faults), 2026-11-10; synthetic. Cells: reached % / collision %.

| family | ideal | crazyflie |
|---|---|---|
| random (this map's family) | 100 / 0 | 100 / 0 |
| u_trap | 100 / 0 | 100 / 0 |
| narrow_gap | 90 / 0 | 15 / 25 |
| office | 90 / 0 | 45 / 35 |
| warehouse | 65 / 0 | 30 / 20 |
| forest | 100 / 0 | 95 / 5 |
| maze | 90 / 0 | 50 / 0 |
| glass_office | 95 / 0 | 30 / 55 |

Tied set on the random family (benchmark, reached % / collision %):

| bench id | ideal | crazyflie |
|---|---|---|
| lazy_thetastar_unknown | 100 / 0 | 100 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 |
| hybrid_astar | 100 / 0 | 95 / 5 |
| astar_unknown | 100 / 0 | 100 / 0 |
| thetastar_known | 100 / 0 | 100 / 0 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 |
| astar_known | 100 / 0 | 100 / 0 |
| informed_rrt_star | 100 / 0 | 100 / 0 |
| bug2 | 90 / 0 | 90 / 10 |
| apf_escape | 100 / 0 | 85 / 0 |
| tangent_bug | 95 / 0 | 55 / 45 |
| mppi | 90 / 0 | 55 / 40 |
| dwa_mem | 75 / 0 | 55 / 5 |
| mppi_astar | 100 / 0 | 80 / 20 |
| freest_beam | 80 / 0 | 50 / 5 |
| vfh_plus | 100 / 0 | 45 / 55 |
| dwa | 80 / 0 | 40 / 35 |

Generated by the Solver's Recommend button (site/solver/recommend.js).
