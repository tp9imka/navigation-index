# Sample: D* Lite vs A* from scratch for unknown-map replanning in the close-area arena

`sample:close-area-planner-dstar` - code and walkthrough in [samples/close-area-planner-dstar](../../samples/close-area-planner-dstar/)

D* Lite on the same inflated grid and cost model as astar_esdf's unknown-map mode, compared with A* replanning from scratch on 50 seed-0 layouts per family. Same outcomes (random, u_trap), identical path costs at all 10,017 frozen-map checks, 4-7x less search time per replan; on tiled maps A* search grows to 5.8 s (8x8 tiles) while D* Lite stays at 2.5-7 ms. Synthetic.

**Verification:** 2026-11-09: compare run/verify/scale/fuzz ran on Apple M3 Max, CPython 3.12.10 (results/ files); README written afterwards from those files after the build run timed out.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `close-area`, `a-to-b`, `moving-obstacles`, `dynamic-obstacles`, `pedestrians`, `replanning`, `a-star`, `esdf`, `safety-filter`, `px4-cbf`, `control-barrier-function`, `apf`, `potential-field`, `benchmark`, `python`, `numpy`, `scipy`, `cpu-only`

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Close-area benchmark matrix: 14 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md) (explains)

_Indexed by lane(s): samples_
