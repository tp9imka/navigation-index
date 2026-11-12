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
.venv/bin/python bench.py --layouts 20 --seed 0 --jobs 10   # ~9 min on 10 processes, results/bench_0.*
.venv/bin/python analyze.py                                 # ~3 s, results/analysis_0.md
.venv/bin/python export_replay.py                           # ~1.5 s, one replay JSON
.venv/bin/python -m unittest test_smoke -v                  # ~1.5 s; skips without numpy
```

One run from code (no processes, so it also fits a Pyodide page; not tried there):
`import explore; explore.run_one("nominal_frontier", "office", 0, 0, 5.0, "ideal")`.

## Results (ran 2026-11-10, Apple M3 Max, macOS 26.6.2, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

Re-run on 2026-11-12 with the arena's dropped-beam fix on
([upstream-findings section 22](../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls)):
`python bench.py --layouts 20 --seed 0 --jobs 10`, 1560 runs, wall 556.2 s on 10 processes
([results/bench_0.md](results/bench_0.md), every run row in
[results/bench_0.json](results/bench_0.json); the stdout kept in
[results/bench_stdout.txt](results/bench_stdout.txt) is the 2026-11-10 run, 460.5 s on 14 processes).
A rerun of 104 rows with the fix off reproduced the 2026-11-10 rows exactly, so the changes below are the fix. Families random, office, warehouse;
layouts 0-19 of seed 0; presets `ideal` (72 rays, 6 m) and `crazyflie` (4 cones, 3 m) from the
arena's [presets.py](../close-area-arena/presets.py). True pose. Wilson 95 % intervals. Times are
medians over the runs that found / reached B, from take-off.

Pooled over the three families, 60 runs per cell
([results/analysis_0.md](results/analysis_0.md), same numbers as bench_0.md; `frontier`
ignores the region, so it has one row):

| region | arm | ideal found % [95 % CI] | ideal collision % [95 % CI] | ideal median time to find s | ideal median time to B s | crazyflie found % [95 % CI] | crazyflie collision % [95 % CI] | crazyflie median time to B s |
|---|---|---|---|---|---|---|---|---|
| B given | oracle | 100.0 [94.0, 100.0] | 0.0 [0.0, 6.0] | 0.0 | 22.05 | 100.0 [94.0, 100.0] | 38.3 [27.1, 51.0] | 23.39 |
| 0 m | nominal_frontier | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 19.8 | 21.82 | 58.3 [45.7, 69.9] | 28.3 [18.5, 40.8] | 23.46 |
| 0 m | lawnmower | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 19.1 | 21.68 | 53.3 [40.9, 65.4] | 30.0 [19.9, 42.5] | 22.29 |
| 0 m | random_walk | 95.0 [86.3, 98.3] | 0.0 [0.0, 6.0] | 20.1 | 22.18 | 60.0 [47.4, 71.4] | 35.0 [24.2, 47.6] | 23.69 |
| 2 m | nominal_frontier | 88.3 [77.8, 94.2] | 0.0 [0.0, 6.0] | 21.1 | 23.0 | 50.0 [37.7, 62.3] | 40.0 [28.6, 52.6] | 24.13 |
| 2 m | lawnmower | 91.7 [81.9, 96.4] | 0.0 [0.0, 6.0] | 30.4 | 32.84 | 51.7 [39.3, 63.8] | 35.0 [24.2, 47.6] | 23.2 |
| 2 m | random_walk | 86.7 [75.8, 93.1] | 0.0 [0.0, 6.0] | 20.3 | 23.92 | 63.3 [50.7, 74.4] | 30.0 [19.9, 42.5] | 24.92 |
| 5 m | nominal_frontier | 81.7 [70.1, 89.4] | 0.0 [0.0, 6.0] | 26.3 | 30.88 | 55.0 [42.5, 66.9] | 21.7 [13.1, 33.6] | 71.78 |
| 5 m | lawnmower | 83.3 [72.0, 90.7] | 1.7 [0.3, 8.9] | 47.8 | 49.72 | 40.0 [28.6, 52.6] | 43.3 [31.6, 55.9] | 36.8 |
| 5 m | random_walk | 85.0 [73.9, 91.9] | 0.0 [0.0, 6.0] | 41.4 | 43.38 | 46.7 [34.6, 59.1] | 38.3 [27.1, 51.0] | 28.52 |
| unknown | frontier | 41.7 [30.1, 54.3] | 0.0 [0.0, 6.0] | 78.4 | 81.28 | 18.3 [10.6, 29.9] | 0.0 [0.0, 6.0] | 140.48 |
| unknown | lawnmower | 31.7 [21.3, 44.2] | 5.0 [1.7, 13.7] | 152.5 | 152.81 | 10.0 [4.7, 20.1] | 51.7 [39.3, 63.8] | 160.06 |
| unknown | random_walk | 18.3 [10.6, 29.9] | 1.7 [0.3, 8.9] | 91.4 | 95.04 | 6.7 [2.6, 15.9] | 53.3 [40.9, 65.4] | 66.98 |

Oracle "found" is 100 % by definition. Per family, reached %, stuck % and timeout % are in
[results/bench_0.md](results/bench_0.md). Selected per-family cells (ideal, found %):

| family | oracle reached % | R = 5 m nominal_frontier | R = 5 m lawnmower | R = 5 m random_walk | unknown frontier | unknown lawnmower |
|---|---|---|---|---|---|---|
| random | 100.0 | 95.0 | 100.0 | 100.0 | 50.0 | 80.0 |
| office | 100.0 | 80.0 | 75.0 | 85.0 | 70.0 | 15.0 |
| warehouse | 80.0 | 70.0 | 75.0 | 70.0 | 5.0 | 0.0 |

Reading:

- **A nominal is worth more than any search rule.** With an ideal sensor, every arm given a
  nominal within 2 m found B in 86.7-95.0 % of runs, about as fast as the oracle (median time to
  B 21.68-32.84 s vs 22.05 s). With B unknown the best arm, `frontier`, found it in 41.7 % [30.1, 54.3]
  within 180 s. Ask whoever set the task for a nominal B, even a rough one.
- **Frontier exploration finishes the map, not the search.** The 6 m range sensor maps the
  room faster than a 2 m detector sweeps it. In the ideal `frontier` runs that missed B, the
  map was nearly complete: median coverage 0.98 in the 11 runs that ended hovering (a rerun confirmed
  all 11 had no frontier left) and 0.80 in the 24 timeouts ([results/analysis_0.md](results/analysis_0.md)). A search needs a frontier of the detector's footprint, not of the map.
  This sample did not build one.
- **With R = 5 m, simple beats clever on found %, not on time.** `random_walk` 85.0 %,
  `lawnmower` 83.3 %, `nominal_frontier` 81.7 % (intervals overlap). `nominal_frontier` is the
  fastest when it finds B (median 26.3 s vs 41.4 s and 47.8 s) but misses more, for the same
  reason as above. The warehouse is the hard family for it (70 %).
- **R = 0 arms differ only after a failed approach.** All four fly to the nominal first; their
  found % (88.3-95.0) differs where the A* to the nominal failed once and the arm fell back to
  frontier search.
- **On the crazyflie preset, collisions decide, not search.** The oracle itself collides in
  38.3 % [27.1, 51.0] of runs (office 50 %, warehouse 65 %), the known 4-beam weakness of the
  unknown-map A* ([close-area-benchmark](../close-area-benchmark/README.md)). Search arms that
  fly more metres collide more: `lawnmower` with B unknown 51.7 %. `frontier` with B unknown had no
  collision on this preset (18.3 % found).
- **Ideal-preset collisions are grazes.** All 5 ideal collisions had a min clearance of
  0.1483-0.1493 m against the 0.15 m radius ([results/bench_0.md](results/bench_0.md)
  "Collisions"), 4 of them in runs with B unknown.

Baseline for scale: the arena's straight planner reaches 40 % of random layouts with B given
([close-area-arena results](../close-area-arena/results/straight_random_0.md)).

### Replay

`python export_replay.py` (defaults: office layout 0, `nominal_frontier`, R = 5 m, ideal) wrote
[results/replay_office_0_nominal_frontier_r5_ideal.json](results/replay_office_0_nominal_frontier_r5_ideal.json),
50,278 bytes ([results/export_replay.log](results/export_replay.log)): found at 172.2 s, at B
174.16 s, outcome and min clearance match its row in bench_0.json. Same top-level fields as the
benchmark's replays (`close-area-replay/2`, `world` in `close-area-world/1`, truth path and
clearance at 10 Hz), plus a `search` object (region, nominal, detection range, time found). The
`world` round-trips through the arena's `world_json.from_json` unchanged. B in `world.b` is the
true B; the planner was given `search.nominal`.

## Limits

- Detection is geometric: 2 m, omnidirectional, line of sight, no false positives and no pose
  error. A real camera has a field of view (the AprilTag sample's is 65 deg horizontal), so a
  real search must also turn to look. The tag's view-angle limit is not modelled.
- The planner sees the true pose. No VIO drift, so "known B" after detection is exact.
- Map coverage: until 2026-11-12 the arena's `LogOddsMap` traced a dropped beam (2 % dropout on
  the ideal preset) as free out to the full range, through walls, so coverage reached 1.25 and cells
  behind walls looked explored. With the fix a dropped beam adds nothing: coverage stays at or below
  0.99, and the three highest-coverage runs rerun with dropout 0 end within 0.02 of it
  ([results/analysis_0.md](results/analysis_0.md)).
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
