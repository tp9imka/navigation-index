# Sample: Close-area search for B: frontier, nominal-first, lawnmower and random-walk arms when B is a region or unknown, then A* to the detected B

`sample:close-area-explore` - code and walkthrough in [samples/close-area-explore](../../samples/close-area-explore/)

Search arms for the case where B is a marker, a nominal position or an area, not a coordinate. B is given as a nominal point with radius 0, 2 or 5 m (true B uniform in the disk) or not at all; it is detected when the vehicle is within 2 m with a clear line of sight (range from the fiducial-goal-apriltag harsh-image sweep, rate 1.00 at 2 m for 0-50 deg). Arms, all driving with the close-area-arena unknown-map A* + ESDF follower on its log-odds map: nearest frontier (Yamauchi 1997 frontiers, nearest by scipy csgraph Dijkstra path length), nominal-first then frontier inside the region, boustrophedon lawnmower over the region (3 m lanes), random waypoints, and an oracle reference with B given. Then A* to the detected B. bench.py runs random, office and warehouse layouts, 20 per family, ideal and crazyflie range presets, 180 s budget, and reports found %, reached %, collision % with Wilson intervals, time to find and time to B. analyze.py relates frontier failures to map coverage. export_replay.py writes one close-area-replay/2 file with the world in close-area-world/1. numpy + scipy only, no threads in the core module.

**Verification:** ran 2026-11-10 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max (macOS 26.6.2 arm64), in a sample venv built from requirements.txt (numpy + scipy only, matplotlib absent): bench.py --layouts 20 --seed 0 --jobs 14 ran 1560 runs in 460.5 s and wrote results/bench_0.*; re-run 2026-11-12 with the arena's dropped-beam fix on (--jobs 10, 556.2 s, same interpreter), after a 104-row rerun with the fix off reproduced the 2026-11-10 rows exactly; analyze.py wrote results/analysis_0.md (map coverage per outcome, and a rerun of the 11 ideal frontier runs that ended hovering: 11 of 11 had no frontier left); export_replay.py wrote one replay whose outcome and min clearance match its bench row and whose world round-trips through world_json.from_json. test_smoke.py: 3 passed in the venv (one reruns a bench row and matches outcome, time to find, path length and clearance), 3 skipped under plain python3 without numpy. No arena file was edited. Not run under Pyodide. Layouts, vehicle, range sensor and detection are simulated; true pose; no camera, no SITL, no flight.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D point-mass arena, geometric 2 m omnidirectional detection without false positives, true pose, seed 0 only (partly a tuning seed); offline run not checked; Pyodide not tried; Linux not tested.

**Readiness evidence:** [samples/close-area-explore/README.md](../../samples/close-area-explore/README.md), [samples/close-area-explore/sample.json](../../samples/close-area-explore/sample.json), [samples/close-area-explore/results/bench_0.json](../../samples/close-area-explore/results/bench_0.json)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `exploration`, `frontier-exploration`, `search`, `lawnmower`, `boustrophedon`, `random-walk`, `marker-goal`, `nominal-goal`, `occupancy-grid`, `log-odds`, `astar`, `wilson-interval`, `benchmark`, `python`, `numpy`, `scipy`, `pyodide`, `cpu-only`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [AprilTag goal B: detection envelope vs range and view angle, and a tag-relative final approach](../../catalog/samples/fiducial-goal-apriltag.md)
- explains: [Close-area benchmark matrix: 21 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md)
- explains: [FUEL - Fast UAV Exploration](../../catalog/repos/hkust-aerial-robotics__fuel.md)
- explains: [CMU Autonomous Exploration Development Environment](../../catalog/repos/hongbiaoz__autonomous_exploration_development_environment.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [First-day intake: close-area A=>B, answers => stack](../../docs/first-day-intake.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Quickstart: fresh clone => flown, scored first flight => regression bar](../../docs/quickstart-first-flight.md) (mentions)
- [Hard questions a reviewer will ask, with 20-second answers](../../templates/presenting/hard-questions.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)

_Indexed by lane(s): samples_
