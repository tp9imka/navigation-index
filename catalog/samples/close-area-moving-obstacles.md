# Sample: Close-area moving obstacles: walking people in the arena, A* replan vs A* + PX4-CBF range filter vs APF

`sample:close-area-moving-obstacles` - code and walkthrough in [samples/close-area-moving-obstacles](../../samples/close-area-moving-obstacles/)

Moving-obstacle family for the shared close-area-arena. moving.py draws 1-3 person-sized cylinders (r 0.25 m) per layout on seeded segments across the A-B corridor and walks them at constant speed, ping-pong; MovingWorld wraps the arena World so the range fans and the truth collision check see the current positions while the prior OccGrid holds static obstacles only. astar_replan.py subclasses the arena's A* + ESDF planner to plan on the prior map plus the latest scan hits, rebuilt every replan (2.5 Hz periodic, early replan up to 5 Hz). run_moving.py flies 50 random layouts at mover speeds 0.0 (frozen control), 0.5 and 1.0 m/s with four arms: A* replan, A* at 5 Hz, A* + F2 (PX4-CBF as shipped, from close-area-safety-filter) and APF (from close-area-planner-reactive), scores on truth, and reports reached, collision, stuck, min clearance, time to collision, warning time from first sighting and the vehicle's closing speed at contact. No motion prediction. numpy + scipy only.

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max (macOS arm64), in the sample venv (uv venv --python 3.12): run_moving.py --layouts 50 --seed 0 --workers 14 ran 600 runs in 21.4 s and wrote results/moving_0.json/.md and results/run_stdout.txt; analyze.py wrote results/analysis_0.md from it; a single-process rerun of every 23rd run (27 runs) gave identical scores (results/rerun_check.txt). The harness reproduces close-area-safety-filter's F2 truth-pose stuck layouts with no movers (layout 2 min clearance 0.8981 m in both). Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 without numpy. No sibling sample file was edited. Layouts, people, vehicle and range fan are simulated, pose is truth; no SITL, no real drone, no motion prediction, one seed and one static family.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `close-area`, `a-to-b`, `moving-obstacles`, `dynamic-obstacles`, `pedestrians`, `replanning`, `a-star`, `esdf`, `safety-filter`, `px4-cbf`, `control-barrier-function`, `apf`, `potential-field`, `benchmark`, `python`, `numpy`, `scipy`, `cpu-only`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Close-area safety-filter kill test A: no filter, PX4 Collision Prevention style and PX4-CBF as shipped on A* under VIO faults, with map-only obstacles the range fan cannot see](../../catalog/samples/close-area-safety-filter.md)
- explains: [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../../catalog/samples/close-area-planner-reactive.md)

## Referenced by

- [Close-area pitch scaffold: A to B through obstacles](../../templates/pitch/close-area-story.md) (mentions)

_Indexed by lane(s): samples_
