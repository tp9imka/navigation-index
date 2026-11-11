# Sample: Close-area benchmark matrix: 14 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format

`sample:close-area-benchmark` - code and walkthrough in [samples/close-area-benchmark](../../samples/close-area-benchmark/)

Runs every close-area planner in the hub through the shared close-area-arena on the same seeded layouts and scores them on truth: straight, freest_beam, APF with wall-follow escape, VFH+, A* + ESDF on the known map, A* + ESDF on a map built from range hits (with the area geofence as its map prior), Informed RRT* 5000 on the known map, A* with the corridor MPC follower, the unknown-map A* behind the F2 PX4-CBF safety filter, and (added later) DWA, DWA with 3 s of scan memory, Bug2, TangentBug and D* Lite on the unknown map. Families: random, u_trap, narrow_gap, office, warehouse, forest, maze, glass_office. Presets: ideal 72-ray fan and a Crazyflie Multi-ranger preset (4 cone beams, 3 m, glass invisible). 20 layouts per cell, seed 0, 14 worker processes, 120 s limit on maze and warehouse. Writes one reached / collision table per preset with the best planner per family, and export_replays.py writes one replay per family x planner (layout 0) embedding the close-area-world/1 document, truth path, clearance per step and outcome, checked against the matrix rows. Planners are imported by path from their samples, unedited. Synthetic arena only.

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 / osqp 1.1.3 on an Apple M3 Max (16 cores, macOS arm64), in the sample venv: bench.py --layouts 20 --seed 0 --workers 14 --parity ran once, 2,880 flights, wall 323.4 s, parity with run.evaluate 10/10 for straight and astar_known; bench.py prior-check run (shipped vs geofenced unknown-map A*, ideal, office / warehouse / glass_office) wall 28.6 s; export_replays.py wrote 72 replays (max 22,673 bytes), 72/72 outcomes and min clearances match results/matrix_0.json, 72/72 world JSON round trips. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 without numpy. The matrix was run once, not repeated for determinism (the replay re-runs of layout 0 match it). Layouts, vehicle and sensors are simulated; planner sees the true pose; no SITL, no real drone. The showcase and playground pages were not checked against replays_v2. Added rows (loop-46c): bench.py --add-to matrix_0 --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite --recheck vfh_plus,astar_unknown --workers 14, 2,240 flights, wall 216.2 s, same interpreter; re-checked rows 320/320 identical; DWA / Bug rows match close-area-planner-dwa-bug's own run 60/60 per planner; export_replays.py --merge wrote 40 more replays, 112/112 total match the matrix.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D arena, true pose, exact prior map for the prior-map rows; 20 layouts per cell, seed 0 only. The full matrix wants many cores (timed with 14 worker processes). Setup needs network for PyPI wheels (uv venv + uv pip install, osqp included); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host (macOS arm64); Linux not tested.

**Readiness evidence:** [samples/close-area-benchmark/README.md](../../samples/close-area-benchmark/README.md), [samples/close-area-benchmark/sample.json](../../samples/close-area-benchmark/sample.json), [samples/close-area-benchmark/results/matrix_0.json](../../samples/close-area-benchmark/results/matrix_0.json)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `benchmark`, `a-star`, `rrt-star`, `informed-rrt-star`, `mpc`, `apf`, `vfh-plus`, `safety-filter`, `cbf`, `crazyflie`, `multi-ranger`, `glass`, `office`, `warehouse`, `maze`, `forest`, `replay`, `dwa`, `bug2`, `tangent-bug`, `dstar-lite`, `python`, `numpy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../../catalog/samples/close-area-planner-reactive.md)
- explains: [Close-area sampling planners: RRT* and Informed RRT* against A* on narrow gaps 0.4-1.2 m, in the close-area arena](../../catalog/samples/close-area-planner-sampling.md)
- explains: [Close-area corridor MPC: linear MPC with OSQP in an ESDF half-plane corridor on the arena A*, vs the carrot follower](../../catalog/samples/close-area-planner-mpc.md)
- explains: [Close-area safety-filter kill test A: no filter, PX4 Collision Prevention style and PX4-CBF as shipped on A* under VIO faults, with map-only obstacles the range fan cannot see](../../catalog/samples/close-area-safety-filter.md)
- explains: [Close-area local planners: DWA (Nav2-style dynamic window) and Bug2 / TangentBug, range sensor only, next to APF and VFH+ on 72-beam and Crazyflie-like 4-beam fans](../../catalog/samples/close-area-planner-dwa-bug.md)
- explains: [D* Lite vs A* from scratch for unknown-map replanning in the close-area arena](../../catalog/samples/close-area-planner-dstar.md)

## Referenced by

- [Cold-start drill: close-area A=>B from a fresh clone, one agent, no team](../../docs/cold-start-drill.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [First-day intake: close-area A=>B, answers => stack](../../docs/first-day-intake.md) (mentions)
- [How it was built: method, kill tests and fact-check error rates](../../docs/how-it-was-built.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Quickstart: fresh clone => flown, scored first flight => regression bar](../../docs/quickstart-first-flight.md) (mentions)
- [Close-area A=>B: planning and mapping for a small multirotor](../../docs/research/close-area-nav/01-planning-and-mapping.md) (mentions)
- [08. Crazyflie sensing limits: what the planner and safety filter can rely on](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md) (mentions)
- [Close-area A=>B navigation: synthesis](../../docs/research/close-area-nav/README.md) (mentions)
- [Four selective offline starter bundles](../../docs/starter-bundles.md) (mentions)
- [Demo script: close-area A to B, the toolkit in 2 minutes](../../templates/demo-script-close-area.md) (mentions)
- [flight-repo: close-area A=>B flight loop starter](../../templates/flight-repo/README.md) (mentions)
- [Close-area pitch scaffold: A to B through obstacles](../../templates/pitch/close-area-story.md) (mentions)
- [Judge drill: close-area A=>B, relocalization pitch (H1)](../../templates/pitch/judge-drill-close-area.md) (mentions)
- [Judge drill: close-area A=>B, measured-toolkit pitch](../../templates/pitch/judge-drill-toolkit.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [Close-area search for B: frontier, nominal-first, lawnmower and random-walk arms when B is a region or unknown, then A* to the detected B](../../catalog/samples/close-area-explore.md) (explains)
- [Close-area Hybrid A*: kinematically feasible (x, y, heading) search with turn-rate-limited primitives against A* + follower, in the close-area arena](../../catalog/samples/close-area-planner-hybrid-astar.md) (explains)
- [Close-area MPPI: sampling-based MPC (Model Predictive Path Integral) from range returns, alone and on an unknown-map A* path, vs A* on 8 arena families](../../catalog/samples/close-area-planner-mppi.md) (explains)
- [Close-area any-angle planning: Theta* and Lazy Theta* against A* + shortcut on 8 arena families, known and unknown map](../../catalog/samples/close-area-planner-thetastar.md) (explains)

_Indexed by lane(s): samples_
