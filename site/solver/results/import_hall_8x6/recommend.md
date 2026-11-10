# Recommend: custom world

**Synthetic 2.5D simulation, scored on truth, not a flight result; 5 seeds on one map is a small sample.**

Solver headline: 9 planners tie at the top; run Thorough or more seeds to separate them (n=5 per planner, best 5/5 reached B, 95 % CI 57 %-100 %).

No path: 0 runs (every run had a free path A=>B at the vehicle radius, worker free_path).

## Pick: no clear winner, tied set of 9, 9 clearly worse

Every planner whose 95 % Wilson interval overlaps the best one's (Theta* (any-angle), known map, 57 %-100 %). The command below flies the top of the ranking (success, then median time to B); any row is an equally supported choice at this n.

### Tied with the best (9)

| planner | bench id | reached | 95 % Wilson | n | n distinct | median time to B s | min clearance m | collisions | no path (not counted) |
|---|---|---|---|---|---|---|---|---|---|
| Theta* (any-angle), known map | thetastar_known | 5/5 | 57 %-100 % | 5 | 5 | 21.90 | 0.214 | 0 | 0 |
| Lazy Theta*, known map | lazy_thetastar_known | 5/5 | 57 %-100 % | 5 | 5 | 21.98 | 0.216 | 0 | 0 |
| A* + ESDF, known map | astar_known | 5/5 | 57 %-100 % | 5 | 5 | 23.72 | 0.214 | 0 | 0 |
| Informed RRT* 5000, known map | informed_rrt_star | 5/5 | 57 %-100 % | 5 | 5 | 25.52 | 0.222 | 0 | 0 |
| Lazy Theta*, unknown map (geofenced) | lazy_thetastar_unknown | 5/5 | 57 %-100 % | 5 | 5 | 27.58 | 0.253 | 0 | 0 |
| A* + ESDF, unknown map | astar_unknown | 5/5 | 57 %-100 % | 5 | 5 | 28.76 | 0.223 | 0 | 0 |
| D* Lite, unknown map (geofenced) | dstar_lite | 5/5 | 57 %-100 % | 5 | 5 | 28.76 | 0.223 | 0 | 0 |
| MPPI on the unknown-map A* path | mppi_astar | 4/5 | 38 %-96 % | 5 | 5 | 13.51 | 0.251 | 0 | 0 |
| TangentBug | tangent_bug | 2/5 | 12 %-77 % | 5 | 5 | 28.59 | 0.253 | 0 | 0 |

Pareto-optimal: Lazy Theta*, unknown map (geofenced) (27.58 s, 0.253 m), MPPI on the unknown-map A* path (13.51 s, 0.251 m). Fast and safe among the 9 tied planners, pooled over every variation of the sweep: no other tied planner is as fast to B (median) and as far from every surface (min clearance) and better in one.

### Clearly worse (9)

95 % Wilson interval does not overlap the best one's.

| planner | bench id | reached | 95 % Wilson | n | n distinct | median time to B s | min clearance m | collisions | no path (not counted) |
|---|---|---|---|---|---|---|---|---|---|
| APF + wall follow | apf_escape | 0/5 | 0 %-43 % | 5 | 5 | - | 0.486 | 0 | 0 |
| Bug2 | bug2 | 0/5 | 0 %-43 % | 5 | 5 | - | 0.430 | 0 | 0 |
| DWA (dynamic window) | dwa | 0/5 | 0 %-43 % | 5 | 5 | - | 0.274 | 0 | 0 |
| DWA + 3 s scan memory | dwa_mem | 0/5 | 0 %-43 % | 5 | 5 | - | 0.264 | 0 | 0 |
| freest beam (reactive) | freest_beam | 0/5 | 0 %-43 % | 5 | 5 | - | 0.376 | 0 | 0 |
| Hybrid A*, unknown map (geofenced) | hybrid_astar | 0/5 | 0 %-43 % | 5 | 5 | - | 0.253 | 0 | 0 |
| MPPI, goal only (no global plan) | mppi | 0/5 | 0 %-43 % | 5 | 5 | - | 0.486 | 0 | 0 |
| straight line to B | straight | 0/5 | 0 %-43 % | 5 | 5 | - | 0.407 | 0 | 0 |
| VFH+ | vfh_plus | 0/5 | 0 %-43 % | 5 | 5 | - | 0.247 | 0 | 0 |

What more seeds buy: Quick separates 5/5 from 0/5; telling 5/5 from 4/5 needs about 33 seeds (95 % Wilson: 5/5 57 %-100 %, 0/5 0 %-43 %). The tied set spans 100 % to 40 %; separating those two rates needs about 10 distinct runs per planner (Thorough flies 10 seeds per sensor).

## Fly it: templates/flight-repo

```sh
cd templates/flight-repo
make first-flight PLANNER=bench:thetastar_known WORLD=my_world.json ARM=F0
```

Writes results/first_flight_bench_thetastar_known_my_world.jsonl, .png and _score.json (score_log.py). ARM=F0.

> WARNING: ARM=F0 flies with NO safety filter. The narrowest passage on the best route A=>B is about 0.65 m (at 3.125, 2.025), below 1.4 m: F2 keeps the centre 0.7 m from every return and cannot pass (flight-repo results/first_flight_bench.txt: narrow_gap_0, F2 stuck, F0 reached). Retry F2 with a smaller eps before a real flight.

- World file: Custom world: save it from recommend.json (its "world" field) next to the Makefile: python3 -c "import json; json.dump(json.load(open('recommend.json'))['world'], open('my_world.json', 'w'))"
- Narrowest passage: 0.65 m (bottleneck clearance 0.326 m at 3.125, 2.025); proxy 2 x the pick's min clearance = 0.43 m, not used.
- How: Narrowest passage = 2 x the bottleneck clearance of the best route A=>B on a 0.05 m ESDF grid of the world (maximin search, cells within 0.7 m of A free, goal = within 0.2 m of B). Chosen over 2 x the winner's min clearance because a run's min clearance is its closest approach to any surface (a corner it cut), not the width it had to pass: in site/solver/results/quick_random_0.json D* Lite's 0.583 m gives 1.17 m (=> F0) on a map whose best route never narrows below 3.6 m. Grid error up to about 0.05 m.
- The command flies run.DEFAULTS, not the sweep: vehicle radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s; sensor ideal: 72 beams, 360 deg, 6 m, noise 0.02 m, dropout 0.02 (run.DEFAULTS); pose truth; seed 0; the world file's exact A and B; 20 Hz loop with the arm filter.

## What the sweep flew

- Vehicle: radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s (arena default)
- Sensor ideal: 72 beams, FoV 360 deg, 0-6 m, noise 0.02 m
- Variations: ideal / truth pose
- Yaw: asked fixed, worker reported off
- Start/goal jitter: 0.5 m radius (seed 0 exact map)
- Run time limit: 60 s of sim time (Auto: no benchmark family, default).
- Seeds: 5 (0..4), 90 runs; finished 2026-11-10T10:42:33.249Z

## Benchmark rows for thetastar_known (beyond this map)

From site/playground/data/advisor.json (built from samples/close-area-benchmark/results/matrix_0.json): 20 layouts per family, seed 0, true pose (no VIO, no faults), 2026-11-10; synthetic. Cells: reached % / collision %.

| family | ideal | crazyflie |
|---|---|---|
| random | 100 / 0 | 100 / 0 |
| u_trap | 100 / 0 | 100 / 0 |
| narrow_gap | 100 / 0 | 100 / 0 |
| office | 100 / 0 | 100 / 0 |
| warehouse | 100 / 0 | 100 / 0 |
| forest | 100 / 0 | 100 / 0 |
| maze | 100 / 0 | 100 / 0 |
| glass_office | 100 / 0 | 100 / 0 |

Tied set on the custom family (benchmark, reached % / collision %):

| bench id | ideal | crazyflie |
|---|---|---|
| thetastar_known | - | - |
| lazy_thetastar_known | - | - |
| astar_known | - | - |
| informed_rrt_star | - | - |
| lazy_thetastar_unknown | - | - |
| astar_unknown | - | - |
| dstar_lite | - | - |
| mppi_astar | - | - |
| tangent_bug | - | - |

Generated by the Solver's Recommend button (site/solver/recommend.js).
