# Sample: Close-area local planners: DWA (Nav2-style dynamic window) and Bug2 / TangentBug, range sensor only, next to APF and VFH+ on 72-beam and Crazyflie-like 4-beam fans

`sample:close-area-planner-dwa-bug` - code and walkthrough in [samples/close-area-planner-dwa-bug](../../samples/close-area-planner-dwa-bug/)

Two more classic map-free local planners for close-area A=>B, written as close-area-arena Planners that read only the pose and the range scan, and measured on the same arena families and fans as the reactive sample. dwa.py: holonomic dynamic window approach (Fox, Burgard, Thrun 1997; the idea behind Nav2's DWB controller): (vx, vy) samples in the window the arena vehicle can reach in 0.2 s at 3 m/s^2, 1.5 s rollouts through the arena's velocity-lag model, admissibility by clearance and braking distance, cost = heading to B + clearance + speed with named weights; memory_s gives a dwa_mem variant with 3 s of remembered returns. bug.py: Bug2 (m-line, fixed-side wall follow, m-line leave rule, unreachable exit) and TangentBug (free-segment test, range-discontinuity tangent points, heuristic-rise switch to boundary following, d_reach < d_followed leave rule, one-scan dropout hold), state machines documented in the file. bench.py runs DWA, dwa_mem, Bug2, TangentBug, APF with wall-follow escape and VFH+ (imported unchanged from close-area-planner-reactive) on random, u_trap and narrow_gap, 50 layouts each, with the 72-beam 6 m fan and a 4-beam 4 m Multi-ranger-like fan, and reports path length against a known-map A* length. tune.py holds the dev-seed sweep and a narrow-gap time-budget check. Synthetic arena only.

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max (macOS 26.6.2), in the sample venv (requirements.txt reuses the arena's): bench.py --layouts 50 --seed 0 wrote results/dwa_bug_0.* in 730.7 s wall; a second run with --only dwa,bug2,tangent_bug --no-write printed identical rows for those 18 cells (dwa_mem not re-run). The APF and VFH+ rows match results/reactive_0.md of close-area-planner-reactive cell for cell. tune.py (seed 1, 20 layouts) wrote results/dev_seed1_tuning.md and tune.py --budget-check wrote results/dev_seed1_budget.md. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 3.14.6 without numpy. No arena or reactive-sample file was edited. Layouts, vehicle and sensor are simulated; the 4-beam fan is a geometry model of the Multi-ranger; dwa_mem remembers returns with the truth pose; no SITL, no Crazyflie, no Nav2.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `close-area`, `a-to-b`, `dwa`, `dynamic-window-approach`, `nav2`, `dwb`, `bug-algorithm`, `bug2`, `tangent-bug`, `wall-following`, `local-minimum`, `u-trap`, `narrow-gap`, `range-sensor`, `scan-memory`, `crazyflie`, `multi-ranger`, `map-free`, `python`, `numpy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../../catalog/samples/close-area-planner-reactive.md)
- explains: [Potential field methods and their inherent limitations for mobile robot navigation](../../catalog/resources/koren-borenstein-apf-limits-icra-1991.md)
- explains: [Multi-ranger deck](../../catalog/resources/bitcraze-multi-ranger-deck.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [08. Crazyflie sensing limits: what the planner and safety filter can rely on](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md) (mentions)
- [Close-area benchmark matrix: 14 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md) (explains)

_Indexed by lane(s): samples_
