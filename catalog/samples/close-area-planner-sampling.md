# Sample: Close-area sampling planners: RRT* and Informed RRT* against A* on narrow gaps 0.4-1.2 m, in the close-area arena

`sample:close-area-planner-sampling` - code and walkthrough in [samples/close-area-planner-sampling](../../samples/close-area-planner-sampling/)

Own numpy RRT* (rewiring with subtree cost update, goal bias 5 %, step 1.0 m, rewire radius from the RRT* bound capped at 2.0 m) with an Informed RRT* mode (ellipse sampling after the first solution), planning on the arena's known inflated 0.1 m grid with the same two-level inflation (0.25 m, then 0.15 m) and the same clearance-keeping shortcut as the A* + ESDF baseline, and flying with that baseline's carrot follower (subclass of planners/astar_esdf). arena.py builds narrow_gap layouts with a fixed gap width from the arena's own random stream. sweep.py: planning-only success, path length (mean, within-layout std over 10 RNG seeds, ratio to A*), planning time median / p95 and exact path clearance at 7 gap widths, A* vs RRT* and Informed RRT* at 1000 and 5000 samples, 30 layouts per width. bench.py: 50-layout arena flights on random and narrow_gap for Informed RRT* 5000 and A*. Shows why A* stays the default in a small 2.5D arena. Synthetic arena only.

**Verification:** ran 2026-11-09 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max, in the sample venv (requirements.txt reuses the arena's): sweep.py --layouts 30 --seeds 10 (8610 plans, wall 173.7 s on 14 processes) wrote results/sweep_0.*; a single-process timing rerun on 5 layouts x 3 seeds wrote results/timing_jobs1/; clearance.py wrote results/sweep_0_clearance.md; bench.py --layouts 50 --seed 0 --iters 5000 --informed 1 ran twice with identical outcomes, path lengths and clearances in all 4 cells (planner timings excluded), and its A* summaries equal the arena's astar_esdf results. gap_world(None) was checked equal to the arena narrow_gap layouts 0-49. Every number in README is from results/. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 3.14 without numpy. No arena file was edited. Layouts, vehicle and sensor are simulated; known static map only; no SITL, no flight.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| cpu | none | unknown | unknown | 0 MB | macos-arm64 | integrated |

**Main limitation:** Synthetic 2.5D arena, known static map; RRT* not tuned; sweep timings under 14-process load. Setup needs network for PyPI wheels (uv venv + uv pip install); cold setup time not measured; no network-denied run, so offline is unknown. README names an Apple M3 Max host; macOS assumed from the M3 Max host, Linux not tested.

**Readiness evidence:** [samples/close-area-planner-sampling/README.md](../../samples/close-area-planner-sampling/README.md), [samples/close-area-planner-sampling/sample.json](../../samples/close-area-planner-sampling/sample.json), [samples/close-area-planner-sampling/results/sweep_0.json](../../samples/close-area-planner-sampling/results/sweep_0.json)

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `rrt-star`, `informed-rrt-star`, `sampling-based-planning`, `a-star`, `narrow-gap`, `narrow-passage`, `occupancy-grid`, `esdf`, `benchmark`, `python`, `numpy`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Sampling-based Algorithms for Optimal Motion Planning](../../catalog/resources/karaman-frazzoli-rrtstar-ijrr-2011.md)
- explains: [PathPlanning (zhm-real)](../../catalog/repos/zhm-real__pathplanning.md)
- explains: [OMPL - Open Motion Planning Library](../../catalog/repos/ompl__ompl.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Choose a stack you can run](../../docs/practical-readiness.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Close-area benchmark matrix: 14 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md) (explains)

_Indexed by lane(s): samples_
