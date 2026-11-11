# close-area-explore: find B when it is not a coordinate, then fly to it

Goal: in most events B is a marker, a nominal position or an area to search, not a bare
coordinate ([06-task-phrasing-survey.md](../../docs/research/close-area-nav/06-task-phrasing-survey.md)
section 2). The hub covers the last metres to a seen tag
([fiducial-goal-apriltag](../fiducial-goal-apriltag/README.md)) but had nothing that searches.
This sample searches for B in the shared [close-area-arena](../close-area-arena/README.md),
then flies to it with the same A*, and measures four search arms against each other.

**Every number here is synthetic**: simulated layouts, vehicle and range sensor, and a geometric
detection model. No camera, no SITL, no flight.

Hub wiring proposals: [INTEGRATION.md](INTEGRATION.md).

## Task model

- **B** is the arena layout's goal. The planner gets one of:
  - a **region**: a nominal point and a radius R = 0, 2 or 5 m. The true B lies within R of the
    nominal (nominal drawn uniform in the disk around B, seeded per layout, same direction and
    radial fraction for every R). R = 0 means B is at the nominal;
  - **unknown**: no nominal. Only the geofence (area bounds) is known.
- **Detection**: B counts as found when the vehicle is within **2 m** of it and the straight
  line to it is clear (exact ray cast on truth geometry). After that the planner knows B
  exactly and flies to it. The 2 m comes from the AprilTag sample's harsh-image sweep
  ([results/sweep_harsh.md](../fiducial-goal-apriltag/results/sweep_harsh.md), 0.16 m tag36h11,
  blur 1.5 px, noise 6 DN, synthetic): detection rate 1.00 at 2 m for view angles 0-50 deg and
  0.95 at 60 deg, p95 position error 0.025 m or less; at 3 m frontal it is already 0.85. The
  detection here is omnidirectional and has no position error.
- **Reached** = truth within 0.3 m of B (arena scorer). Budget 180 s per run (the arena's 60 s is
  too short to search a warehouse: B given as a coordinate already takes a median 59.16 s there,
  [results/bench_0.md](results/bench_0.md)).
- **Stuck** differs from the arena: truth path length over the last 10 s below 0.5 m (hovering).
  The arena rule (net displacement below 0.2 m in 10 s) fired on search loops that came back to
  their own track. Collision, reached and timeout are the arena's definitions.

## Arms

All arms drive with the arena's unknown-map A* + ESDF follower
([planners/astar_esdf.py](../close-area-arena/planners/astar_esdf.py), `known_map=False`, log-odds
map from range hits only), subclassed in [explore.py](explore.py). The planner reads only pose,
range scan, geofence, nominal and R.

| Arm | Search rule |
|---|---|
| `frontier` | Nearest frontier (frontier idea from Yamauchi 1997). Frontier = known-free cell next to an unknown cell, clusters of 4+ cells; nearest by path length over known-free cells (`scipy.sparse.csgraph.dijkstra`). Ignores the region |
| `nominal_frontier` | A* to the nominal first; then nearest frontier within R + 2 m of the nominal; then any frontier. With B unknown it is `frontier` |
| `lawnmower` | Boustrophedon lanes 3 m apart over the region's bounding box (the whole geofence when unknown), waypoints every 3 m, failed waypoints skipped; then nearest frontier |
| `random_walk` | Random waypoints, uniform in the region disk, or a 2-5 m step in a random heading when unknown |
| `oracle` | B handed over at t = 0 (B as a coordinate). Reference row |

A search target is dropped after max(15 s, 4 s per metre of straight-line distance) and
blacklisted. Constants are module globals at the top of [explore.py](explore.py).

## Run

```sh
cd samples/close-area-explore
uv venv --python 3.12 .venv && uv pip install --python .venv -r requirements.txt   # numpy + scipy
.venv/bin/python bench.py --layouts 20 --seed 0 --jobs 14   # ~8 min on 14 processes, results/bench_0.*
.venv/bin/python analyze.py                                 # ~3 s, results/analysis_0.md
.venv/bin/python export_replay.py                           # ~1.5 s, one replay JSON
.venv/bin/python -m unittest test_smoke -v                  # ~1.5 s; skips without numpy
```

One run from code (no processes, so it also fits a Pyodide page; not tried there):
`import explore; explore.run_one("nominal_frontier", "office", 0, 0, 5.0, "ideal")`.

## Results (ran 2026-11-10, Apple M3 Max, macOS 26.6.2, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

`python bench.py --layouts 20 --seed 0 --jobs 14`: 1560 runs, wall 460.5 s on 14 processes
([results/bench_0.md](results/bench_0.md), every run row in
[results/bench_0.json](results/bench_0.json), stdout in
[results/bench_stdout.txt](results/bench_stdout.txt)). Families random, office, warehouse;
layouts 0-19 of seed 0; presets `ideal` (72 rays, 6 m) and `crazyflie` (4 cones, 3 m) from the
arena's [presets.py](../close-area-arena/presets.py). True pose. Wilson 95 % intervals. Times are
medians over the runs that found / reached B, from take-off.

Pooled over the three families, 60 runs per cell
([results/analysis_0.md](results/analysis_0.md), same numbers as bench_0.md; `frontier`
ignores the region, so it has one row):

| region | arm | ideal found % [95 % CI] | ideal collision % [95 % CI] | ideal median time to find s | ideal median time to B s | crazyflie found % [95 % CI] | crazyflie collision % [95 % CI] | crazyflie median time to B s |
|---|---|---|---|---|---|---|---|---|
| B given | oracle | 100.0 [94.0, 100.0] | 0.0 [0.0, 6.0] | 0.0 | 22.8 | 100.0 [94.0, 100.0] | 38.3 [27.1, 51.0] | 23.68 |
| 0 m | nominal_frontier | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 20.0 | 21.98 | 55.0 [42.5, 66.9] | 35.0 [24.2, 47.6] | 23.54 |
| 0 m | lawnmower | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 19.9 | 21.82 | 55.0 [42.5, 66.9] | 33.3 [22.7, 45.9] | 23.54 |
| 0 m | random_walk | 100.0 [94.0, 100.0] | 0.0 [0.0, 6.0] | 20.15 | 23.66 | 58.3 [45.7, 69.9] | 36.7 [25.6, 49.3] | 23.77 |
| 2 m | nominal_frontier | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 22.7 | 24.9 | 50.0 [37.7, 62.3] | 35.0 [24.2, 47.6] | 24.67 |
| 2 m | lawnmower | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 25.5 | 28.96 | 53.3 [40.9, 65.4] | 41.7 [30.1, 54.3] | 24.82 |
| 2 m | random_walk | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 25.2 | 27.98 | 55.0 [42.5, 66.9] | 35.0 [24.2, 47.6] | 23.25 |
| 5 m | nominal_frontier | 81.7 [70.1, 89.4] | 0.0 [0.0, 6.0] | 29.2 | 32.16 | 48.3 [36.2, 60.7] | 31.7 [21.3, 44.2] | 42.26 |
| 5 m | lawnmower | 86.7 [75.8, 93.1] | 0.0 [0.0, 6.0] | 55.25 | 58.41 | 38.3 [27.1, 51.0] | 50.0 [37.7, 62.3] | 34.44 |
| 5 m | random_walk | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 43.2 | 44.94 | 41.7 [30.1, 54.3] | 43.3 [31.6, 55.9] | 28.18 |
| unknown | frontier | 43.3 [31.6, 55.9] | 5.0 [1.7, 13.7] | 70.75 | 73.12 | 3.3 [0.9, 11.4] | 16.7 [9.3, 28.0] | 132.97 |
| unknown | lawnmower | 26.7 [17.1, 39.0] | 6.7 [2.6, 15.9] | 158.35 | 153.6 | 8.3 [3.6, 18.1] | 75.0 [62.8, 84.2] | 153.3 |
| unknown | random_walk | 13.3 [6.9, 24.2] | 1.7 [0.3, 8.9] | 66.0 | 69.46 | 5.0 [1.7, 13.7] | 56.7 [44.1, 68.4] | 160.86 |

Oracle "found" is 100 % by definition. Per family, reached %, stuck % and timeout % are in
[results/bench_0.md](results/bench_0.md). Selected per-family cells (ideal, found %):

| family | oracle reached % | R = 5 m nominal_frontier | R = 5 m lawnmower | R = 5 m random_walk | unknown frontier | unknown lawnmower |
|---|---|---|---|---|---|---|
| random | 100.0 | 100.0 | 100.0 | 100.0 | 55.0 | 65.0 |
| office | 100.0 | 70.0 | 85.0 | 95.0 | 65.0 | 15.0 |
| warehouse | 95.0 | 75.0 | 75.0 | 80.0 | 10.0 | 0.0 |

Reading:

- **A nominal is worth more than any search rule.** With an ideal sensor, every arm given a
  nominal within 2 m found B in 88.3-100 % of runs, about as fast as the oracle (median time to
  B 21.82-28.96 s vs 22.8 s). With B unknown the best arm, `frontier`, found it in 43.3 % [31.6, 55.9]
  within 180 s. Ask whoever set the task for a nominal B, even a rough one.
- **Frontier exploration finishes the map, not the search.** The 6 m range sensor maps the
  room faster than a 2 m detector sweeps it. In the ideal `frontier` runs that missed B, the
  map was complete: median coverage 1.03 in the 8 runs that ended hovering (a rerun confirmed
  all 8 had no frontier left) and 1.02 in the 23 timeouts ([results/analysis_0.md](results/analysis_0.md); coverage above 1 is explained
  under Limits). A search needs a frontier of the detector's footprint, not of the map.
  This sample did not build one.
- **With R = 5 m, simple beats clever on found %, not on time.** `random_walk` 91.7 %,
  `lawnmower` 86.7 %, `nominal_frontier` 81.7 % (intervals overlap). `nominal_frontier` is the
  fastest when it finds B (median 29.2 s vs 43.2 s and 55.25 s) but misses more, for the same
  reason as above. The office is the hard family for it (70 %).
- **R = 0 arms differ only after a failed approach.** All four fly to the nominal first; their
  found % (91.7-100) differs where the A* to the nominal failed once and the arm fell back to
  frontier search.
- **On the crazyflie preset, collisions decide, not search.** The oracle itself collides in
  38.3 % [27.1, 51.0] of runs (office 50 %, warehouse 65 %), the known 4-beam weakness of the
  unknown-map A* ([close-area-benchmark](../close-area-benchmark/README.md)). Search arms that
  fly more metres collide more: `lawnmower` with B unknown 75.0 %.
- **Ideal-preset collisions are grazes.** All 8 ideal collisions had a min clearance of
  0.1466-0.1498 m against the 0.15 m radius ([results/bench_0.md](results/bench_0.md)
  "Collisions"), all in runs with B unknown.

Baseline for scale: the arena's straight planner reaches 40 % of random layouts with B given
([close-area-arena results](../close-area-arena/results/straight_random_0.md)).

### Replay

`python export_replay.py` (defaults: office layout 0, `nominal_frontier`, R = 5 m, ideal) wrote
[results/replay_office_0_nominal_frontier_r5_ideal.json](results/replay_office_0_nominal_frontier_r5_ideal.json),
16,593 bytes ([results/export_replay.log](results/export_replay.log)): found at 45.3 s, at B
47.18 s, outcome and min clearance match its row in bench_0.json. Same top-level fields as the
benchmark's replays (`close-area-replay/2`, `world` in `close-area-world/1`, truth path and
clearance at 10 Hz), plus a `search` object (region, nominal, detection range, time found). The
`world` round-trips through the arena's `world_json.from_json` unchanged. B in `world.b` is the
true B; the planner was given `search.nominal`.

## Limits

- Detection is geometric: 2 m, omnidirectional, line of sight, no false positives and no pose
  error. A real camera has a field of view (the AprilTag sample's is 65 deg horizontal), so a
  real search must also turn to look. The tag's view-angle limit is not modelled.
- The planner sees the true pose. No VIO drift, so "known B" after detection is exact.
- Map coverage above 1.0 in [results/analysis_0.md](results/analysis_0.md): the arena's
  `LogOddsMap` traces a no-return beam (2 % dropout on the ideal preset) as free out to the full
  range, through walls. Cells behind walls then look explored, which removes frontiers and
  helps hide B. The three highest-coverage runs (warehouse 1, 2, 4: 1.19, 1.20, 1.25) rerun
  with dropout 0 end at 0.85, 0.79, 0.98 (same file). Reported, not fixed (the arena is not
  edited here).
- B's placement is the arena's: always near the far corner from A (random), in a far room
  (office), or in the top aisle (warehouse). A whole-area lawnmower starting at A covers that
  corner last. Different B placement would change the "unknown" rows.
- 180 s budget, seed 0 only, 20 layouts per family: intervals are 25-30 points wide per family
  cell. Constants were set on a few seed-0 layouts, so seed 0 is not held out.
- No coverage-path optimisation (TSP over frontiers, information gain, FUEL-style viewpoints);
  `frontier` is the plain greedy baseline.
- Written for Pyodide (numpy + scipy, no threads or processes in explore.py) but not run there.
  `bench.py --jobs` uses a process pool on the CLI only.

## Sources

- [paper] B. Yamauchi, "A frontier-based approach for autonomous exploration", IEEE CIRA 1997,
  pp. 146-151 ([PDF at CMU](https://www.cs.cmu.edu/~motionplanning/papers/sbp_papers/integrated1/yamauchi_frontiers.pdf)).
  Only the abstract was read: frontiers are the boundary between open and unexplored space, and
  the robot moves to them until the environment is explored. The selection rule here (nearest by
  path over known-free cells, cluster size, blacklist) is this sample's.
- [code] Shared arena, A* + ESDF follower and log-odds map: [close-area-arena](../close-area-arena/README.md),
  [CONTRACT.md](../close-area-arena/CONTRACT.md).
- [sample] Detection range: [fiducial-goal-apriltag](../fiducial-goal-apriltag/README.md),
  [results/sweep_harsh.md](../fiducial-goal-apriltag/results/sweep_harsh.md).
- [survey] How B is given at events: [06-task-phrasing-survey.md](../../docs/research/close-area-nav/06-task-phrasing-survey.md).
- [code] scipy `ndimage` (distance transform, labelling) and `sparse.csgraph.dijkstra`; numpy.
