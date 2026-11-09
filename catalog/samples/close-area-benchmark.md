# Sample: Close-area benchmark matrix: 9 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format

`sample:close-area-benchmark` - code and walkthrough in [samples/close-area-benchmark](../../samples/close-area-benchmark/)

Runs every close-area planner in the hub through the shared close-area-arena on the same seeded layouts and scores them on truth: straight, freest_beam, APF with wall-follow escape, VFH+, A* + ESDF on the known map, A* + ESDF on a map built from range hits (with the area geofence as its map prior), Informed RRT* 5000 on the known map, A* with the corridor MPC follower, and the unknown-map A* behind the F2 PX4-CBF safety filter. Families: random, u_trap, narrow_gap, office, warehouse, forest, maze, glass_office. Presets: ideal 72-ray fan and a Crazyflie Multi-ranger preset (4 cone beams, 3 m, glass invisible). 20 layouts per cell, seed 0, 14 worker processes, 120 s limit on maze and warehouse. Writes one reached / collision table per preset with the best planner per family, and export_replays.py writes one replay per family x planner (layout 0) embedding the close-area-world/1 document, truth path, clearance per step and outcome, checked against the matrix rows. Planners are imported by path from their samples, unedited. Synthetic arena only.

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 / osqp 1.1.3 on an Apple M3 Max (16 cores, macOS arm64), in the sample venv: bench.py --layouts 20 --seed 0 --workers 14 --parity ran once, 2,880 flights, wall 323.4 s, parity with run.evaluate 10/10 for straight and astar_known; bench.py prior-check run (shipped vs geofenced unknown-map A*, ideal, office / warehouse / glass_office) wall 28.6 s; export_replays.py wrote 72 replays (max 22,673 bytes), 72/72 outcomes and min clearances match results/matrix_0.json, 72/72 world JSON round trips. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 without numpy. The matrix was run once, not repeated for determinism (the replay re-runs of layout 0 match it). Layouts, vehicle and sensors are simulated; planner sees the true pose; no SITL, no real drone. The showcase and playground pages were not checked against replays_v2.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `benchmark`, `a-star`, `rrt-star`, `informed-rrt-star`, `mpc`, `apf`, `vfh-plus`, `safety-filter`, `cbf`, `crazyflie`, `multi-ranger`, `glass`, `office`, `warehouse`, `maze`, `forest`, `replay`, `python`, `numpy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../../catalog/samples/close-area-planner-reactive.md)
- explains: [Close-area sampling planners: RRT* and Informed RRT* against A* on narrow gaps 0.4-1.2 m, in the close-area arena](../../catalog/samples/close-area-planner-sampling.md)
- explains: [Close-area corridor MPC: linear MPC with OSQP in an ESDF half-plane corridor on the arena A*, vs the carrot follower](../../catalog/samples/close-area-planner-mpc.md)
- explains: [Close-area safety-filter kill test A: no filter, PX4 Collision Prevention style and PX4-CBF as shipped on A* under VIO faults, with map-only obstacles the range fan cannot see](../../catalog/samples/close-area-safety-filter.md)

## Referenced by

- [Judge drill: close-area A=>B, relocalization pitch (H1)](../../templates/pitch/judge-drill-close-area.md) (mentions)

_Indexed by lane(s): samples_
