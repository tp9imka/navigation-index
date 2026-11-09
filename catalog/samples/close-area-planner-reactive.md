# Sample: Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan

`sample:close-area-planner-reactive` - code and walkthrough in [samples/close-area-planner-reactive](../../samples/close-area-planner-reactive/)

Map-free fallback planners for close-area A=>B, written as close-area-arena Planners that read only the pose and the range scan. apf.py: velocity-form artificial potential field on raw returns (attractive goal, repulsive returns weighted by each beam's share of the circle), a range-only brake, and a named escape rule, wall-follow after 3 s of no progress with a Bug-style leave rule; escape=False gives plain APF. vfh_plus.py: VFH+ with a 72-sector polar histogram, enlargement by radius plus safety distance, binary histogram with hysteresis, valley selection with the goal / heading / previous-direction cost, speed from obstacle density, no escape rule. bench.py runs both on the arena's random, u_trap and narrow_gap families with the default 72-beam 6 m fan and a 4-beam 4 m Multi-ranger-like fan, scores on truth, and classifies where failed runs ended (inside the U cup, before the gap wall, at the gap). tune.py holds the dev-seed sweep that set the defaults. Synthetic arena only.

**Verification:** ran 2026-11-09 with CPython 3.11.15 + numpy 2.4.6 / scipy 1.17.1 on an Apple M3 Max, in the sample venv (requirements.txt reuses the arena's): bench.py --layouts 50 --seed 0 ran twice with identical per-run scores in all 18 cells (planner timings excluded), wall 75.8 s for the kept run; tune.py on seed 1 wrote results/dev_seed1_tuning.md. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 3.14 without numpy. No arena file was edited. Layouts, vehicle and sensor are simulated; the 4-beam fan is a geometry model of the Multi-ranger (no beam cone, arena noise and dropout); no SITL, no Crazyflie.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D arena; 4-beam fan is ideal rays with no beam cone; no Crazyflie or SITL. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested.

**Readiness evidence:** [samples/close-area-planner-reactive/README.md](../../samples/close-area-planner-reactive/README.md), [samples/close-area-planner-reactive/sample.json](../../samples/close-area-planner-reactive/sample.json), [samples/close-area-planner-reactive/results/reactive_0.json](../../samples/close-area-planner-reactive/results/reactive_0.json)

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `close-area`, `a-to-b`, `potential-field`, `apf`, `vfh-plus`, `vector-field-histogram`, `local-minimum`, `u-trap`, `narrow-gap`, `wall-following`, `bug-algorithm`, `range-sensor`, `crazyflie`, `multi-ranger`, `map-free`, `python`, `numpy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Real-Time Obstacle Avoidance for Manipulators and Mobile Robots](../../catalog/resources/khatib-potential-fields-ijrr-1986.md)
- explains: [Potential field methods and their inherent limitations for mobile robot navigation](../../catalog/resources/koren-borenstein-apf-limits-icra-1991.md)
- explains: [VFH+: reliable obstacle avoidance for fast mobile robots](../../catalog/resources/ulrich-borenstein-vfhplus-icra-1998.md)
- explains: [Multi-ranger deck](../../catalog/resources/bitcraze-multi-ranger-deck.md)

## Referenced by

- [Challenge 2 "Autonomous Frontiers": entry point](../../docs/challenge-2-autonomous-flight.md) (mentions)
- [Cheat sheets: pick one in 30 seconds](../../docs/cheatsheets/README.md) (mentions)
- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Close-area A=>B navigation: synthesis](../../docs/research/close-area-nav/README.md) (mentions)
- [Research rounds: which one applies, and the innovation story per brief](../../docs/research/README.md) (mentions)

_Indexed by lane(s): samples_
