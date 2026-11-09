# Sample: Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer

`sample:close-area-arena` - code and walkthrough in [samples/close-area-arena](../../samples/close-area-arena/)

Small deterministic simulator that every close-area A=>B approach in the hub is compared in. Walled 20 x 20 m area, axis-aligned boxes and cylinders in three seeded layout families (random clutter, a U trap with its inside corner on the A-B line, a wall with one 0.5-0.9 m gap), exact signed distance and ray casts, a 0.1 m occupancy grid, and a guaranteed free path (4-connected BFS on the grid inflated by the 0.15 m vehicle radius, else resample). 50 Hz double-integrator vehicle with a 0.15 s first-order velocity lag and acceleration and speed limits, z held. Ray-cast range fan with noise and dropout. Planners only see the published Pose / RangeScan / Setpoint / Adapter interface, so they port to a real drone adapter unchanged; a pose_source hook lets later samples substitute a faulty estimator while scans and scoring stay on truth. Scorer: reached (0.3 m), collision (clearance < radius), stuck (< 0.2 m in 10 s), timeout, time to goal, min clearance, path length. Ships three planners to start from: straight (floor), freest_beam (reactive, in run_faults.py) and astar_esdf (A* + ESDF, known or unknown map, planners/astar_esdf.py); a VIO-like EKF with seeded faults (estimator.py, faults.py, run_faults.py); a flight-log scorer for sim or real logs (score_log.py, log_format.md); a CLI with summary tables, JSON results and a PNG plot written without matplotlib, a scipy EDT timing on a 2M-cell grid, and CONTRACT.md for later planners, estimators and safety filters. numpy + scipy; matplotlib only for score_log.py.

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max: run.py --planner straight --layouts 20 --seed 0 ran twice (once with --plot) with identical per-run scores, and once each with --family u_trap and --family narrow_gap (with --plot); bench_edt.py wrote results/edt_timing.json. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 without numpy; it loads the folder as a package the way CONTRACT.md tells sibling samples to. checks.py wrote results/checks.json: the BFS rejects a 0.3 m gap and accepts 0.4 m, and the straight planner with the slow-down disabled collides in 60 % of the 20 random layouts, so the scorer's collision path fires. Layouts, vehicle and sensor are simulated; no SITL, no real drone, and templates/drone-adapter was not present in this checkout to diff the interface against. Follow-up 2026-11-09 (same M3 Max, macOS 26.6.2 arm64): templates/drone-adapter is now present in the checkout; the interface diff against it is not yet done. Cold setup measured: uv venv --python 3.12 .venv && uv pip install --no-cache --python .venv -r requirements.txt took 16.5 s wall (numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2 wheels from PyPI; the CPython 3.12.10 interpreter was already on the machine). The first command then ran under sandbox-exec with all network access denied (curl to pypi.org failed in the same sandbox) and gave per-run scores identical to results/straight_random_0.json (timings excluded); that run's rewritten results files were restored. test_smoke.py: 1 passed in the fresh venv.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | verified | 0.3 min | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D point-mass arena on one M3 Max; setup needs network for PyPI wheels (16.5 s cold, interpreter already present); offline checked for the first command only; no SITL, no real drone, Linux not tested.

**Readiness evidence:** [samples/close-area-arena/README.md](../../samples/close-area-arena/README.md), [samples/close-area-arena/sample.json](../../samples/close-area-arena/sample.json), [samples/close-area-arena/results/straight_random_0.json](../../samples/close-area-arena/results/straight_random_0.json)

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `benchmark`, `simulator`, `occupancy-grid`, `esdf`, `distance-transform`, `range-sensor`, `raycast`, `u-trap`, `narrow-gap`, `drone-adapter`, `offboard-velocity`, `python`, `numpy`, `scipy`, `astar`, `freest-beam`, `planner-baseline`, `estimator`, `fault-injection`, `flight-log`, `apple-silicon`, `cpu-only`

## Related

- explains: [Potential field methods and their inherent limitations for mobile robot navigation](../../catalog/resources/koren-borenstein-apf-limits-icra-1991.md)
- explains: [gym-pybullet-drones](../../catalog/repos/learnsyslab__gym-pybullet-drones.md)
- explains: [RotorPy](../../catalog/repos/spencerfolk__rotorpy.md)

## Referenced by

- [Challenge 2 "Autonomous Frontiers": entry point](../../docs/challenge-2-autonomous-flight.md) (mentions)
- [Cheat sheets: pick one in 30 seconds](../../docs/cheatsheets/README.md) (mentions)
- [Dataset cards](../../docs/dataset-cards/README.md) (mentions)
- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Navigation primer](../../docs/primer/README.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [08. Crazyflie sensing limits: what the planner and safety filter can rely on](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md) (mentions)
- [Close-area A=>B navigation: synthesis](../../docs/research/close-area-nav/README.md) (mentions)
- [Research rounds: which one applies, and the innovation story per brief](../../docs/research/README.md) (mentions)
- [Demo dashboard](../../templates/demo-dashboard/README.md) (mentions)
- [drivers: Adapter implementations for real platforms](../../templates/drone-adapter/drivers/README.md) (mentions)
- [flight-repo: close-area A=>B flight loop starter](../../templates/flight-repo/README.md) (mentions)
- [Close-area pitch scaffold: A to B through obstacles](../../templates/pitch/close-area-story.md) (mentions)
- [Hackathon kit templates](../../templates/README.md) (mentions)
- [Close-area moving obstacles: walking people in the arena, A* replan vs A* + PX4-CBF range filter vs APF](../../catalog/samples/close-area-moving-obstacles.md) (explains)
- [Close-area corridor MPC: linear MPC with OSQP in an ESDF half-plane corridor on the arena A*, vs the carrot follower](../../catalog/samples/close-area-planner-mpc.md) (explains)
- [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../../catalog/samples/close-area-planner-reactive.md) (explains)
- [Close-area sampling planners: RRT* and Informed RRT* against A* on narrow gaps 0.4-1.2 m, in the close-area arena](../../catalog/samples/close-area-planner-sampling.md) (explains)
- [Close-area relocalization after VIO loss: scan-to-map pose hypotheses, ratio + persistence acceptance, hover until one wins](../../catalog/samples/close-area-relocalize.md) (explains)
- [Close-area safety-filter kill test A: no filter, PX4 Collision Prevention style and PX4-CBF as shipped on A* under VIO faults, with map-only obstacles the range fan cannot see](../../catalog/samples/close-area-safety-filter.md) (explains)

_Indexed by lane(s): samples_
