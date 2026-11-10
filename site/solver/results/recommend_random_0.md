# Recommend: random_0

**Synthetic 2.5D simulation, scored on truth, not a flight result; 3 seeds on one map is a small sample.**

Solver headline: No clear winner: Theta* (any-angle), known map and Lazy Theta*, known map are within noise on this map (n=3).

## Pick: no clear winner, tied set of 18

Every planner whose 95 % Wilson interval overlaps the best one's (Theta* (any-angle), known map, 44 %-100 %). The command below flies the top of the ranking (success, then median time to B); any row is an equally supported choice at this n.

| planner | bench id | reached | 95 % Wilson | n | n distinct | median time to B s | min clearance m | collisions |
|---|---|---|---|---|---|---|---|---|
| Theta* (any-angle), known map | thetastar_known | 3/3 | 44 %-100 % | 3 | 3 | 16.82 | 0.882 | 0 |
| Lazy Theta*, known map | lazy_thetastar_known | 3/3 | 44 %-100 % | 3 | 3 | 16.88 | 0.845 | 0 |
| Lazy Theta*, unknown map (geofenced) | lazy_thetastar_unknown | 3/3 | 44 %-100 % | 3 | 3 | 17.14 | 0.869 | 0 |
| D* Lite, unknown map (geofenced) | dstar_lite | 3/3 | 44 %-100 % | 3 | 3 | 18.66 | 0.583 | 0 |
| Hybrid A*, unknown map (geofenced) | hybrid_astar | 3/3 | 44 %-100 % | 3 | 3 | 18.74 | 0.513 | 0 |
| A* + ESDF, unknown map | astar_unknown | 3/3 | 44 %-100 % | 3 | 3 | 18.86 | 0.581 | 0 |
| A* + ESDF, known map | astar_known | 3/3 | 44 %-100 % | 3 | 3 | 18.94 | 0.561 | 0 |
| MPPI on the unknown-map A* path | mppi_astar | 3/3 | 44 %-100 % | 3 | 3 | 19.88 | 0.574 | 0 |
| MPPI, goal only (no global plan) | mppi | 3/3 | 44 %-100 % | 3 | 3 | 20.36 | 0.336 | 0 |
| TangentBug | tangent_bug | 3/3 | 44 %-100 % | 3 | 3 | 24.16 | 0.432 | 0 |
| freest beam (reactive) | freest_beam | 3/3 | 44 %-100 % | 3 | 3 | 25.32 | 0.470 | 0 |
| VFH+ | vfh_plus | 3/3 | 44 %-100 % | 3 | 3 | 25.50 | 0.233 | 0 |
| Informed RRT* 5000, known map | informed_rrt_star | 3/3 | 44 %-100 % | 3 | 3 | 26.64 | 0.221 | 0 |
| APF + wall follow | apf_escape | 3/3 | 44 %-100 % | 3 | 3 | 28.24 | 0.636 | 0 |
| Bug2 | bug2 | 3/3 | 44 %-100 % | 3 | 3 | 29.48 | 0.513 | 0 |
| DWA (dynamic window) | dwa | 3/3 | 44 %-100 % | 3 | 3 | 43.68 | 0.263 | 0 |
| DWA + 3 s scan memory | dwa_mem | 3/3 | 44 %-100 % | 3 | 3 | 44.84 | 0.240 | 0 |
| straight line to B | straight | 0/3 | 0 %-56 % | 3 | 3 | - | 0.371 | 0 |

## Fly it: templates/flight-repo

```sh
cd templates/flight-repo
make first-flight PLANNER=bench:thetastar_known WORLD=../../site/playground/presets/random_0.json ARM=F2
```

Writes results/first_flight_bench_thetastar_known_random_0.jsonl, .png and _score.json (score_log.py). ARM=F2 (default): the narrowest passage is 3.60 m, at least 1.4 m.

- World file: Preset random_0: the hub ships it at site/playground/presets/random_0.json (the path below is relative to templates/flight-repo). The same world is inline in recommend.json ("world").
- Narrowest passage: 3.60 m (bottleneck clearance 1.799 m at 8.988, 14.105); proxy 2 x the pick's min clearance = 1.76 m, not used.
- How: Narrowest passage = 2 x the bottleneck clearance of the best route A=>B on a 0.05 m ESDF grid of the world (maximin search, cells within 0.7 m of A free, goal = within 0.2 m of B). Chosen over 2 x the winner's min clearance because a run's min clearance is its closest approach to any surface (a corner it cut), not the width it had to pass: in site/solver/results/quick_random_0.json D* Lite's 0.583 m gives 1.17 m (=> F0) on a map whose best route never narrows below 3.6 m. Grid error up to about 0.05 m.
- The command flies run.DEFAULTS, not the sweep: vehicle radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s; sensor ideal: 72 beams, 360 deg, 6 m, noise 0.02 m, dropout 0.02 (run.DEFAULTS); pose truth; seed 0; the world file's exact A and B; 20 Hz loop with the arm filter.

## What the sweep flew

- Vehicle: radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s (arena default)
- Sensor ideal: 72 beams, FoV 360 deg, 0-6 m, noise 0.02 m
- Variations: ideal / truth pose
- Yaw: asked fixed, worker reported off
- Start/goal jitter: 0.5 m radius (seed 0 exact map)
- Run time limit: 60 s of sim time (Auto: random family, default).
- Seeds: 3 (0..2), 54 runs; finished 2026-11-10T09:28:27.791Z

## Benchmark rows for thetastar_known (beyond this map)

From site/playground/data/advisor.json (built from samples/close-area-benchmark/results/matrix_0.json): 20 layouts per family, seed 0, true pose (no VIO, no faults), 2026-11-10; synthetic. Cells: reached % / collision %.

| family | ideal | crazyflie |
|---|---|---|
| random (this map's family) | 100 / 0 | 100 / 0 |
| u_trap | 100 / 0 | 100 / 0 |
| narrow_gap | 100 / 0 | 100 / 0 |
| office | 100 / 0 | 100 / 0 |
| warehouse | 100 / 0 | 100 / 0 |
| forest | 100 / 0 | 100 / 0 |
| maze | 100 / 0 | 100 / 0 |
| glass_office | 100 / 0 | 100 / 0 |

Tied set on the random family (benchmark, reached % / collision %):

| bench id | ideal | crazyflie |
|---|---|---|
| thetastar_known | 100 / 0 | 100 / 0 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 |
| lazy_thetastar_unknown | 100 / 0 | 100 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 |
| hybrid_astar | 100 / 0 | 95 / 5 |
| astar_unknown | 100 / 0 | 100 / 0 |
| astar_known | 100 / 0 | 100 / 0 |
| mppi_astar | 100 / 0 | 80 / 20 |
| mppi | 90 / 0 | 55 / 40 |
| tangent_bug | 95 / 0 | 55 / 45 |
| freest_beam | 80 / 0 | 50 / 5 |
| vfh_plus | 100 / 0 | 45 / 55 |
| informed_rrt_star | 100 / 0 | 100 / 0 |
| apf_escape | 100 / 0 | 85 / 0 |
| bug2 | 90 / 0 | 90 / 10 |
| dwa | 80 / 0 | 40 / 35 |
| dwa_mem | 75 / 0 | 55 / 5 |
| straight | 40 / 0 | 40 / 40 |

Generated by the Solver's Recommend button (site/solver/recommend.js).
