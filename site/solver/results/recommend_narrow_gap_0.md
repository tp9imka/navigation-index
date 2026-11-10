# Recommend: narrow_gap_0

**Synthetic 2.5D simulation, scored on truth, not a flight result; 3 seeds on one map is a small sample.**

Solver headline: No clear winner: MPPI on the unknown-map A* path and MPPI, goal only (no global plan) are within noise on this map (n=3).

## Pick: no clear winner, tied set of 18

Every planner whose 95 % Wilson interval overlaps the best one's (MPPI on the unknown-map A* path, 44 %-100 %). The command below flies the top of the ranking (success, then median time to B); any row is an equally supported choice at this n.

| planner | bench id | reached | 95 % Wilson | n | n distinct | median time to B s | min clearance m | collisions |
|---|---|---|---|---|---|---|---|---|
| MPPI on the unknown-map A* path | mppi_astar | 3/3 | 44 %-100 % | 3 | 3 | 21.22 | 0.261 | 0 |
| MPPI, goal only (no global plan) | mppi | 3/3 | 44 %-100 % | 3 | 3 | 21.94 | 0.213 | 0 |
| Lazy Theta*, known map | lazy_thetastar_known | 3/3 | 44 %-100 % | 3 | 3 | 22.22 | 0.365 | 0 |
| Theta* (any-angle), known map | thetastar_known | 3/3 | 44 %-100 % | 3 | 3 | 22.28 | 0.358 | 0 |
| Lazy Theta*, unknown map (geofenced) | lazy_thetastar_unknown | 3/3 | 44 %-100 % | 3 | 3 | 22.52 | 0.307 | 0 |
| Hybrid A*, unknown map (geofenced) | hybrid_astar | 3/3 | 44 %-100 % | 3 | 3 | 23.68 | 0.307 | 0 |
| D* Lite, unknown map (geofenced) | dstar_lite | 3/3 | 44 %-100 % | 3 | 3 | 24.14 | 0.323 | 0 |
| A* + ESDF, unknown map | astar_unknown | 3/3 | 44 %-100 % | 3 | 3 | 24.40 | 0.301 | 0 |
| A* + ESDF, known map | astar_known | 3/3 | 44 %-100 % | 3 | 3 | 24.62 | 0.321 | 0 |
| VFH+ | vfh_plus | 3/3 | 44 %-100 % | 3 | 3 | 27.20 | 0.226 | 0 |
| TangentBug | tangent_bug | 3/3 | 44 %-100 % | 3 | 3 | 27.34 | 0.298 | 0 |
| Informed RRT* 5000, known map | informed_rrt_star | 3/3 | 44 %-100 % | 3 | 3 | 28.46 | 0.264 | 0 |
| DWA + 3 s scan memory | dwa_mem | 3/3 | 44 %-100 % | 3 | 3 | 47.14 | 0.235 | 0 |
| DWA (dynamic window) | dwa | 3/3 | 44 %-100 % | 3 | 3 | 51.44 | 0.260 | 0 |
| APF + wall follow | apf_escape | 0/3 | 0 %-56 % | 3 | 3 | - | 0.608 | 0 |
| Bug2 | bug2 | 0/3 | 0 %-56 % | 3 | 3 | - | 0.482 | 0 |
| freest beam (reactive) | freest_beam | 0/3 | 0 %-56 % | 3 | 3 | - | 0.330 | 0 |
| straight line to B | straight | 0/3 | 0 %-56 % | 3 | 3 | - | 0.375 | 0 |

## Fly it: templates/flight-repo

```sh
cd templates/flight-repo
make first-flight PLANNER=bench:mppi_astar WORLD=../../site/playground/presets/narrow_gap_0.json ARM=F0
```

Writes results/first_flight_bench_mppi_astar_narrow_gap_0.jsonl, .png and _score.json (score_log.py). ARM=F0.

> WARNING: ARM=F0 flies with NO safety filter. The narrowest passage on the best route A=>B is about 0.72 m (at 10.603, 7.548), below 1.4 m: F2 keeps the centre 0.7 m from every return and cannot pass (flight-repo results/first_flight_bench.txt: narrow_gap_0, F2 stuck, F0 reached). Retry F2 with a smaller eps before a real flight.

- World file: Preset narrow_gap_0: the hub ships it at site/playground/presets/narrow_gap_0.json (the path below is relative to templates/flight-repo). The same world is inline in recommend.json ("world").
- Narrowest passage: 0.72 m (bottleneck clearance 0.359 m at 10.603, 7.548); proxy 2 x the pick's min clearance = 0.52 m, not used.
- How: Narrowest passage = 2 x the bottleneck clearance of the best route A=>B on a 0.05 m ESDF grid of the world (maximin search, cells within 0.7 m of A free, goal = within 0.2 m of B). Chosen over 2 x the winner's min clearance because a run's min clearance is its closest approach to any surface (a corner it cut), not the width it had to pass: in site/solver/results/quick_random_0.json D* Lite's 0.583 m gives 1.17 m (=> F0) on a map whose best route never narrows below 3.6 m. Grid error up to about 0.05 m.
- The command flies run.DEFAULTS, not the sweep: vehicle radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s; sensor ideal: 72 beams, 360 deg, 6 m, noise 0.02 m, dropout 0.02 (run.DEFAULTS); pose truth; seed 0; the world file's exact A and B; 20 Hz loop with the arm filter.

## What the sweep flew

- Vehicle: radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s (arena default)
- Sensor ideal: 72 beams, FoV 360 deg, 0-6 m, noise 0.02 m
- Variations: ideal / truth pose
- Yaw: asked fixed, worker reported off
- Start/goal jitter: 0.5 m radius (seed 0 exact map)
- Run time limit: 60 s of sim time (Auto: narrow_gap family, default).
- Seeds: 3 (0..2), 54 runs; finished 2026-11-10T09:27:55.540Z

## Benchmark rows for mppi_astar (beyond this map)

From site/playground/data/advisor.json (built from samples/close-area-benchmark/results/matrix_0.json): 20 layouts per family, seed 0, true pose (no VIO, no faults), 2026-11-10; synthetic. Cells: reached % / collision %.

| family | ideal | crazyflie |
|---|---|---|
| random | 100 / 0 | 80 / 20 |
| u_trap | 100 / 0 | 40 / 60 |
| narrow_gap (this map's family) | 95 / 0 | 15 / 85 |
| office | 100 / 0 | 10 / 85 |
| warehouse | 65 / 0 | 0 / 100 |
| forest | 100 / 0 | 100 / 0 |
| maze | 95 / 0 | 0 / 100 |
| glass_office | 95 / 0 | 5 / 85 |

Tied set on the narrow_gap family (benchmark, reached % / collision %):

| bench id | ideal | crazyflie |
|---|---|---|
| mppi_astar | 95 / 0 | 15 / 85 |
| mppi | 25 / 0 | 0 / 100 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 |
| thetastar_known | 100 / 0 | 100 / 0 |
| lazy_thetastar_unknown | 90 / 0 | 15 / 25 |
| hybrid_astar | 70 / 0 | 10 / 5 |
| dstar_lite | 85 / 0 | 15 / 10 |
| astar_unknown | 90 / 0 | 25 / 5 |
| astar_known | 100 / 0 | 100 / 0 |
| vfh_plus | 50 / 0 | 5 / 95 |
| tangent_bug | 45 / 0 | 5 / 10 |
| informed_rrt_star | 100 / 0 | 100 / 0 |
| dwa_mem | 10 / 0 | 5 / 0 |
| dwa | 10 / 0 | 0 / 40 |
| apf_escape | 0 / 0 | 0 / 5 |
| bug2 | 0 / 0 | 0 / 0 |
| freest_beam | 0 / 0 | 0 / 0 |
| straight | 0 / 0 | 0 / 70 |

Generated by the Solver's Recommend button (site/solver/recommend.js).
