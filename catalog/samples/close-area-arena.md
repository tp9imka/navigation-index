# Sample: Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer

`sample:close-area-arena` - code and walkthrough in [samples/close-area-arena](../../samples/close-area-arena/)

Small deterministic simulator that every close-area A=>B approach in the hub is compared in. Walled 20 x 20 m area, axis-aligned boxes and cylinders in three seeded layout families (random clutter, a U trap with its inside corner on the A-B line, a wall with one 0.5-0.9 m gap), exact signed distance and ray casts, a 0.1 m occupancy grid, and a guaranteed free path (4-connected BFS on the grid inflated by the 0.15 m vehicle radius, else resample). 50 Hz double-integrator vehicle with a 0.15 s first-order velocity lag and acceleration and speed limits, z held. Ray-cast range fan with noise and dropout. Planners only see the published Pose / RangeScan / Setpoint / Adapter interface, so they port to a real drone adapter unchanged; a pose_source hook lets later samples substitute a faulty estimator while scans and scoring stay on truth. Scorer: reached (0.3 m), collision (clearance < radius), stuck (< 0.2 m in 10 s), timeout, time to goal, min clearance, path length. Ships a straight-line baseline, a CLI with summary tables, JSON results and a PNG plot written without matplotlib, a scipy EDT timing on a 2M-cell grid, and CONTRACT.md for later planners, estimators and safety filters. numpy + scipy only.

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max: run.py --planner straight --layouts 20 --seed 0 ran twice (once with --plot) with identical per-run scores, and once each with --family u_trap and --family narrow_gap (with --plot); bench_edt.py wrote results/edt_timing.json. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 without numpy; it loads the folder as a package the way CONTRACT.md tells sibling samples to. checks.py wrote results/checks.json: the BFS rejects a 0.3 m gap and accepts 0.4 m, and the straight planner with the slow-down disabled collides in 60 % of the 20 random layouts, so the scorer's collision path fires. Layouts, vehicle and sensor are simulated; no SITL, no real drone, and templates/drone-adapter was not present in this checkout to diff the interface against.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `benchmark`, `simulator`, `occupancy-grid`, `esdf`, `distance-transform`, `range-sensor`, `raycast`, `u-trap`, `narrow-gap`, `drone-adapter`, `offboard-velocity`, `python`, `numpy`, `scipy`

## Related

- explains: [Potential field methods and their inherent limitations for mobile robot navigation](../../catalog/resources/koren-borenstein-apf-limits-icra-1991.md)
- explains: [gym-pybullet-drones](../../catalog/repos/learnsyslab__gym-pybullet-drones.md)
- explains: [RotorPy](../../catalog/repos/spencerfolk__rotorpy.md)

## Referenced by

- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../../catalog/samples/close-area-planner-reactive.md) (explains)

_Indexed by lane(s): samples_
