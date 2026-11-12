# Sample: Close-area Hybrid A*: kinematically feasible (x, y, heading) search with turn-rate-limited primitives against A* + follower, in the close-area arena

`sample:close-area-planner-hybrid-astar` - code and walkthrough in [samples/close-area-planner-hybrid-astar](../../samples/close-area-planner-hybrid-astar/)

Own numpy + scipy Hybrid A* (Dolgov et al. 2008 / 2010) over continuous (x, y, heading) states binned 0.25 m x 10 deg: fast arcs at 1.5 m/s and slow arcs at 0.5 m/s limited by a 1.0 rad/s turn rate and the arena's 3 m/s^2, turns in place, a straight-line shot to B when the ESDF segment is clear (no Reeds-Shepp), cost = flight time x astar_esdf's clearance and unknown-cell cost, heuristic = cost-weighted 2D Dijkstra (scipy.sparse.csgraph). Subclasses the arena's astar_esdf: same range-built log-odds map, inflation, replan rule and carrot follower, plus a speed profile from the primitives. vehicle_turn.py adds a turn-rate-limited vehicle (velocity direction turns at <= 1.0 rad/s, subclass of the arena vehicle). bench.py: 1200 flights, 8 families x 20 layouts on preset ideal plus crazyflie on random and office, stock and turn-limited vehicle, against astar_unknown (benchmark row, 200/200 runs identical to the benchmark) and astar_unknown with a pure-pursuit turn speed cap. plan_quality.py: first plan on the known map, max heading change per metre and minimum time to B under the same limits. Synthetic arena only.

**Verification:** ran 2026-11-10 with CPython 3.12.10 + numpy 2.5.4 / scipy 1.18.1 on an Apple M3 Max (16 cores, host shared with other jobs, load average 128-266 seen right after the runs), in the sample venv (requirements.txt reuses the arena's): bench.py --layouts 20 --seed 0 --workers 14 (1200 flights, wall 207.5 s; an earlier identical command gave the same reached / collision / stuck numbers) wrote results/bench_0.*, and its astar_unknown rows on the stock vehicle equal close-area-benchmark/results/matrix_0.json in 200/200 runs (outcome, min clearance, path length); plan_quality.py --layouts 20 --seed 0 (single process, 13.3 s) wrote results/plan_quality_0.*; a single-process timing run (30 flights, 56.5 s) wrote results/timing_jobs1_0.*. test_smoke.py: 1 passed in the venv, 1 skipped under plain python3 3.14 without numpy. Not run in Pyodide or the browser playground. No arena or shared file was edited. Layouts, vehicle and sensor are simulated; no SITL, no flight.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `close-area`, `a-to-b`, `hybrid-astar`, `kinodynamic-planning`, `motion-primitives`, `turn-rate-limit`, `a-star`, `esdf`, `occupancy-grid`, `benchmark`, `python`, `numpy`, `scipy`, `pyodide`

## Related

- explains: [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md)
- explains: [Close-area benchmark matrix: 21 planners x 8 arena families x 2 range-sensor presets, with replays in the world JSON format](../../catalog/samples/close-area-benchmark.md)
- explains: [Path Planning for Autonomous Vehicles in Unknown Semi-structured Environments](../../catalog/resources/dolgov-hybrid-astar-ijrr-2010.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [How it was built: method, kill tests and fact-check error rates](../../docs/how-it-was-built.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Hard questions a reviewer will ask, with 20-second answers](../../templates/presenting/hard-questions.md) (mentions)

_Indexed by lane(s): samples_
