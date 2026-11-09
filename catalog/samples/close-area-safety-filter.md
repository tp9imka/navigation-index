# Sample: Close-area safety-filter kill test A: no filter, PX4 Collision Prevention style and PX4-CBF as shipped on A* under VIO faults, with map-only obstacles the range fan cannot see

`sample:close-area-safety-filter` - code and walkthrough in [samples/close-area-safety-filter](../../samples/close-area-safety-filter/)

Harness that puts a safety filter between a planner and the vehicle in the shared close-area-arena, for the kill test of the hub's integrity-aware safety-filter headline. filters.py defines the SafetyFilter interface filter(setpoint, pose, scan, map_obstacles, health, dt) -> (setpoint, intervened), a registry, and three arms: F0 pass-through; F1 CP-stop, PX4 Collision Prevention style per-sector velocity limit with CP_DIST, CP_DELAY, jerk-limited braking, sliding and CP_GUIDE_ANG guidance (read from PX4 docs; CP_DIST 0.5 m is ours); F2 PX4-CBF as shipped in the NTNU fork, the analytic single-constraint composite CBF on body-frame range points with doc 05 Table II gains, linear class-K, raw input, clamp after, low-passed output and no FoV constraint, wrapped around the planner's velocity setpoint with a P velocity loop. unsensed.py adds two map-only obstacles per layout (thin poles or glass panels) on the reference A* path: they are in the prior grid and truth collision checks but a wrapped range fan cannot see them. run_kill.py runs astar_esdf(known_map=True) on 100 random layouts under the arena estimator's none, jump, bias and dropout faults plus a truth reference, for each arm, with the unsensed obstacles on and off, and scores on truth. numpy + scipy only.

**Verification:** ran 2026-11-09 with CPython 3.11.15 + numpy 2.4.6 / scipy 1.17.1 on an Apple M3 Max, in the sample venv: run_kill.py --layouts 100 --seed 0 --workers 14 ran 3000 runs in 176.4 s and wrote results/kill_a_*; a rerun of 24 of those runs in one process gave identical scores. With F0, truth pose and unsensed obstacles off, the harness reproduced the arena's run.evaluate for astar_esdf exactly on layouts 0-4. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 3.14 without numpy. No arena file was edited. Layouts, vehicle, range fan and estimator faults are simulated; no SITL, no PX4 code was run (F1 is a reading of the PX4 docs, F2 follows doc 05's pseudo-code).

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D arena, one planner and one seed; no PX4 code run (F1 from docs, F2 from doc 05 pseudo-code). Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested.

**Readiness evidence:** [samples/close-area-safety-filter/README.md](../../samples/close-area-safety-filter/README.md), [samples/close-area-safety-filter/sample.json](../../samples/close-area-safety-filter/sample.json), [samples/close-area-safety-filter/results/kill_a_summary_0.md](../../samples/close-area-safety-filter/results/kill_a_summary_0.md)

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `close-area`, `a-to-b`, `safety-filter`, `control-barrier-function`, `cbf`, `px4-cbf`, `collision-prevention`, `cp-dist`, `kill-test`, `vio-fault`, `unsensed-obstacle`, `glass`, `thin-pole`, `a-star`, `python`, `numpy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Close-area A=>B navigation: synthesis](../../docs/research/close-area-nav/README.md) (mentions)
- [Research rounds: which one applies, and the innovation story per brief](../../docs/research/README.md) (mentions)
- [Demo script: close-area A to B](../../templates/demo-script-close-area.md) (mentions)
- [flight-repo: close-area A=>B flight loop starter](../../templates/flight-repo/README.md) (mentions)
- [Close-area pitch scaffold: A to B through obstacles](../../templates/pitch/close-area-story.md) (mentions)
- [Close-area benchmark matrix: 9 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md) (explains)
- [Close-area moving obstacles: walking people in the arena, A* replan vs A* + PX4-CBF range filter vs APF](../../catalog/samples/close-area-moving-obstacles.md) (explains)

_Indexed by lane(s): samples_
