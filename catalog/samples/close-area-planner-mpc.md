# Sample: Close-area corridor MPC: linear MPC with OSQP in an ESDF half-plane corridor on the arena A*, vs the carrot follower

`sample:close-area-planner-mpc` - code and walkthrough in [samples/close-area-planner-mpc](../../samples/close-area-planner-mpc/)

Replaces the close-area-arena A* carrot follower with a linear MPC path follower and measures the difference. Model: state p, v; input the velocity setpoint, with the exact zero-order-hold discretisation of the arena's first-order velocity lag (tau 0.15 s), so the output is sent to send_setpoint() unchanged. Horizon 20 x 0.1 s, per-axis boxes on velocity (1.4 m/s) and on acceleration via |u - v| <= tau a_max, tracking cost on a reference marched along the A* path with the carrot's ESDF speed rule. Corridor per horizon step from the same 0.1 m grid as the ESDF: nearest-point separating half-planes (safe-flight-corridor style, no ellipsoid) offset by radius + 0.05 m, plus a box that keeps it inside the 2 m search radius; rows soft with a heavy slack penalty. OSQP with fixed sparsity, per-step update of q, l, u and corridor values, warm start from the shifted previous solution. bench.py compares carrot vs MPC (and cold-start, no-corridor and constant-speed ablations) on 50 random and 50 narrow_gap layouts, scored on truth, and plots a narrow_gap run with both paths and the corridor. Synthetic arena, known map, truth pose.

**Verification:** ran 2026-11-09 with CPython 3.11.15 + numpy 2.4.6 / scipy 1.17.1 / osqp 1.1.3 on an Apple M3 Max (macOS 26.6.2), in the sample venv: bench.py --layouts 50 --seed 0 wrote results/mpc_compare_0.json/.md and results/mpc_narrow_gap_0_run32.png (wall 381.9 s; the PNG was re-drawn once with a corrected panel title through bench.plot, same run and outcomes). A second astar_mpc pass over the 50 narrow_gap layouts gave identical per-run outcome, min clearance, path length and time to goal (checked in the console, not saved). Every number in README is from results/. test_smoke.py: 1 passed in the venv (model vs the 50 Hz arena vehicle within 2 cm; narrow_gap run 0 matches results), 1 skipped under plain python3 without numpy. osqp license read from the installed wheel metadata (Apache-2.0). No arena file was edited. Layouts, vehicle and sensor are simulated, the map is known and the pose is truth; no SITL, no flight computer timing, no estimator faults.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D point-mass arena, known map, truth pose; QP timing is a laptop in Python, not a flight computer. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host (macOS 26.6.2); Linux not tested.

**Readiness evidence:** [samples/close-area-planner-mpc/README.md](../../samples/close-area-planner-mpc/README.md), [samples/close-area-planner-mpc/sample.json](../../samples/close-area-planner-mpc/sample.json), [samples/close-area-planner-mpc/results/mpc_compare_0.json](../../samples/close-area-planner-mpc/results/mpc_compare_0.json)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `close-area`, `a-to-b`, `mpc`, `model-predictive-control`, `osqp`, `qp`, `safe-flight-corridor`, `half-plane`, `esdf`, `path-following`, `warm-start`, `solve-time`, `narrow-gap`, `python`, `numpy`, `scipy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [OSQP](../../catalog/repos/osqp__osqp.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Close-area benchmark matrix: 21 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md) (explains)
- [Close-area MPPI: sampling-based MPC (Model Predictive Path Integral) from range returns, alone and on an unknown-map A* path, vs A* on 8 arena families](../../catalog/samples/close-area-planner-mppi.md) (alternative_to)

_Indexed by lane(s): samples_
