# Sample: Close-area any-angle planning: Theta* and Lazy Theta* against A* + shortcut on 8 arena families, known and unknown map

`sample:close-area-planner-thetastar` - code and walkthrough in [samples/close-area-planner-thetastar](../../samples/close-area-planner-thetastar/)

Own pure-Python Theta* (Daniel, Nash, Koenig, Felner 2010) and Lazy Theta* (Nash, Koenig, Tovey 2010) on the close-area arena's inflated 0.1 m grid with the same ESDF clearance cost as planners/astar_esdf: the any-angle edge parent(u) => v is priced by the A* cell cost integrated along the segment and must not touch a blocked cell, so the clearance cost still shapes the path. Exact uniform-cost-disc speed-up (checked equal to the plain walk on 80 searches). The flying planner subclasses AStarESDF (same two inflation levels, replan schedule, log-odds map, carrot follower and speed law) and drops only the post-hoc shortcut. make() works with no arguments; make(lazy=True); make(known_map=False, bounds=...) uses the benchmark's geofenced map. bench.py flights reuses close-area-benchmark's run_one for 8 families x 20 layouts on preset ideal (known and unknown map) plus crazyflie on random and office; its A* rows equal the benchmark matrix run by run. bench.py plans: single-process planning-only comparison (ms, length, cost, exact clearance). numpy + scipy only. Synthetic arena only.

**Verification:** ran 2026-11-10 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on Apple silicon arm64 (16 CPUs, shared with other jobs, 1-minute load average 38-256 recorded in each results file), in the sample venv (requirements.txt reuses the arena's): bench.py flights --layouts 20 --seed 0 --workers 14 (1080 runs, wall 781.5 s) wrote results/flights_0.*; bench.py plans --layouts 20 --seed 0 --repeats 3 (wall 123 s) wrote results/plans_0.*; a single-process unknown-map timing run (1 layout per family, wall 296.3 s) wrote results/timing_unknown_jobs1.*; bench.py check wrote results/matrix_check_0.md (A* rows identical to close-area-benchmark/results/matrix_0.json: 160/160 known, 160/160 unknown, 40/40 crazyflie). The uniform-disc speed-up returned identical paths and costs to the plain line walk on 80 searches (ad hoc check, not saved to results/). Every number in README is from results/ or the cited abstracts. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 3.14 without numpy. No file outside this folder was edited. Not run in Pyodide; replan ms are wall time under machine load. Layouts, vehicle and sensor are simulated; no SITL, no flight.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D point-mass arena on one shared Apple silicon machine; setup needs PyPI wheels (time not measured); offline not checked; Pyodide not run; Linux not tested.

**Readiness evidence:** [samples/close-area-planner-thetastar/README.md](../../samples/close-area-planner-thetastar/README.md), [samples/close-area-planner-thetastar/sample.json](../../samples/close-area-planner-thetastar/sample.json), [samples/close-area-planner-thetastar/results/flights_0.json](../../samples/close-area-planner-thetastar/results/flights_0.json)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `theta-star`, `lazy-theta-star`, `any-angle-planning`, `a-star`, `occupancy-grid`, `esdf`, `benchmark`, `python`, `numpy`, `scipy`, `pyodide-compatible`, `cpu-only`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Close-area benchmark matrix: 21 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md)
- explains: [python_motion_planning](../../catalog/repos/ai-winter__python_motion_planning.md)
- explains: [Nav2 (ROS 2 Navigation)](../../catalog/repos/ros-navigation__navigation2.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
