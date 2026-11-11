# Sample: Close-area MPPI: sampling-based MPC (Model Predictive Path Integral) from range returns, alone and on an unknown-map A* path, vs A* on 8 arena families

`sample:close-area-planner-mppi` - code and walkthrough in [samples/close-area-planner-mppi](../../samples/close-area-planner-mppi/)

Own numpy MPPI (information-theoretic update of Williams et al. 2017) for the close-area arena. Every 10 Hz step: integrate the range scan into the arena's log-odds grid (hits only, no prior map), take its ESDF with scipy, sample K = 256 velocity-setpoint sequences over 20 x 0.1 s with AR(1) noise (sigma 0.6 m/s, beta 0.8) plus three fixed samples (nominal, hover, straight at the target), roll them out vectorised on the arena point-mass model (tau 0.15 s lag, 3 m/s^2, 2 m/s, 50 Hz substeps, checked against vehicle.py), cost = distance to the target over the horizon + terminal distance + ESDF obstacle cost + collision penalty + setpoint smoothness + the information-theoretic cross term, softmin weights with temperature lambda = 1, send the first setpoint and warm-start the next step. Two variants: make(guide='none') targets B directly; make(guide='astar') targets a point 2 m along the arena's unknown-map A* path on the same map, with a pull towards the path, replacing the A* carrot follower. bench.py flies both and the benchmark's geofenced unknown-map A* on random, u_trap, narrow_gap, office, warehouse, forest, maze and glass_office (20 layouts, seed 0, ideal 72-ray sensor) and on random and office with the Crazyflie 4-beam preset, with the close-area-benchmark flight loop (astar_unknown rows identical to its matrix run by run); sweep.py sweeps K 64/256/1024 x horizon 1/2/4 s on random and maze; one-process step timing. numpy + scipy only, so it fits the Pyodide browser playground. Synthetic arena only.

**Verification:** ran 2026-11-10 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max (macOS 26.6.2, 16 CPUs), in the sample venv: bench.py --preset ideal --layouts 20 --seed 0 --workers 14 (wall 99.1 s) and --preset crazyflie --families random,office (wall 15.2 s) wrote results/bench_*_0.json/.md; their astar_unknown runs are identical to close-area-benchmark/results/matrix_0.json in outcome, min clearance and path length (160/160 ideal, 40/40 crazyflie). A second ideal run gave identical outcome, min clearance, path length and time to goal in 480/480 runs (results/determinism_check.txt). bench.py --timing --workers 1 (wall 65.8 s) wrote results/timing_0.*; sweep.py --layouts 10 --seed 0 --workers 14 (flights wall 91.6 s) wrote results/sweep_0.*; the dev-seed run bench.py --seed 1 --layouts 10 wrote results/bench_ideal_1.*. A first seed-0 sweep before the straight-at-target sample was added is kept as results/sweep_0_before_direct_sample.* (superseded). Every number in README is from results/ or labelled console-only. test_smoke.py: 1 passed in the venv (rollout vs arena vehicle within 1e-9 m, make() with no arguments steps, u_trap run 0 matches results), 1 skipped under plain python3 without numpy. Browser loading was emulated in CPython by copying the manifest's arena files and this sample's arena.py + mppi.py into a Pyodide-like folder layout and loading them with the playground's _load_sample recipe (3 runs on office layout 0); it was not run in Pyodide and Pyodide timing is not measured. Layouts, vehicle and sensor are simulated, pose is truth; no SITL, no real drone, no estimator faults.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D point-mass arena with true pose on one M3 Max; collides often with a 4-beam sensor; not run in Pyodide; setup needs PyPI wheels and its cold time was not measured.

**Readiness evidence:** [samples/close-area-planner-mppi/README.md](../../samples/close-area-planner-mppi/README.md), [samples/close-area-planner-mppi/results/bench_ideal_0.json](../../samples/close-area-planner-mppi/results/bench_ideal_0.json), [samples/close-area-planner-mppi/results/timing_0.json](../../samples/close-area-planner-mppi/results/timing_0.json)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `mppi`, `model-predictive-path-integral`, `sampling-based-mpc`, `mpc`, `local-minima`, `u-trap`, `maze`, `esdf`, `occupancy-grid`, `a-star`, `unknown-map`, `crazyflie`, `pyodide`, `benchmark`, `python`, `numpy`, `scipy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Close-area benchmark matrix: 14 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md)
- alternative_to: [Close-area corridor MPC: linear MPC with OSQP in an ESDF half-plane corridor on the arena A*, vs the carrot follower](../../catalog/samples/close-area-planner-mpc.md)
- alternative_to: [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../../catalog/samples/close-area-planner-reactive.md)
- explains: [Nav2 (ROS 2 Navigation)](../../catalog/repos/ros-navigation__navigation2.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
