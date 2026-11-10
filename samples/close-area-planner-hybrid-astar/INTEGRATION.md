# Proposed hub wiring (text only, not applied)

The driver applies these. This sample did not edit any shared file. Links below resolve from
this file, so check_links passes. When pasting into a file under docs/, replace `./` with
`../samples/close-area-planner-hybrid-astar/`. From docs/cheatsheets/, use
`../../samples/close-area-planner-hybrid-astar/`.

## (a) Browser playground (site/playground)

### manifest.json, "files" (after the "sampling" entries)

```json
    {"group": "hybrid-astar", "src": "../../samples/close-area-planner-hybrid-astar/arena.py", "dst": "hybrid_astar/arena.py"},
    {"group": "hybrid-astar", "src": "../../samples/close-area-planner-hybrid-astar/hybrid_astar.py", "dst": "hybrid_astar/hybrid_astar.py"},
```

Append to the manifest "comment": `hybrid-astar = Hybrid A* from
samples/close-area-planner-hybrid-astar (its arena.py finds close_area_arena already imported;
it needs scipy.sparse.csgraph from the scipy package already listed).`

### worker.js

1. In the `py.runPython(...)` line that sets the sample folders (next to `SAMPLING_DIR`), add:

```js
`\nHYBRID_DIR = "${HOME}hybrid_astar"`
```

so the string ends `...SAMPLING_DIR = "${HOME}sampling"\nRELOC_DIR = "${HOME}reloc"\nHYBRID_DIR = "${HOME}hybrid_astar"`.

2. In DRIVER_PY, after the Informed RRT* block (no backticks, no dollar-brace):

```python
# Hybrid A*, unknown map, geofenced as in the benchmark (samples/close-area-planner-hybrid-astar)
try:
    _ha = _load_sample(HYBRID_DIR, ["hybrid_astar"])["hybrid_astar"]
    PLANNERS["hybrid_astar"] = lambda w: _ha.make(bounds=_bounds(w))
    WORLD_PLANNERS.add("hybrid_astar")
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["hybrid_astar"] = repr(e)
```

Not tested in Pyodide. The module imports only numpy, scipy (`scipy.sparse`,
`scipy.sparse.csgraph`, and `scipy.ndimage` through astar_esdf) and the arena's adapter,
planners.base and planners.astar_esdf. All of them are already loaded by the playground.

## (b) samples/close-area-benchmark/bench.py

Next to the other `_load_sample` calls:

```python
_hybrid = _load_sample("close-area-planner-hybrid-astar", ["hybrid_astar"])
```

In `PLANNERS`:

```python
    "hybrid_astar": (lambda w: _hybrid["hybrid_astar"].make(bounds=_bounds(w)), None,
                     "Hybrid A* unknown map", "close-area-planner-hybrid-astar"),
```

In `NEEDS`: `"hybrid_astar": (_hybrid, "hybrid_astar"),`. Add `"hybrid_astar"` to
`DEFAULT_PLANNERS` and `"hybrid_astar": 1` to `SLOW`. Then add the row without rerunning the
others:

```sh
.venv/bin/python bench.py --add-to matrix_0 --planners hybrid_astar --workers 14
```

The flight loop in this sample's bench.py is the benchmark's `run_one` without the filter
branch. This sample's astar_unknown rows matched matrix_0.json in 200/200 runs, so the merged
hybrid_astar rows should equal the `stock` rows of [results/bench_0.json](./results/bench_0.json).
That is expected, not checked.

## (c) Decoder and cheat sheet

### docs/problem-statement-decoder.md, row 31 (close-area A=>B), "Start from" cell

[close-area-planner-hybrid-astar](./README.md) (Hybrid A* over x, y, heading with
turn-rate-limited primitives; pick it only when the vehicle cannot turn in place at speed)

Add to that row's "Main risk": a kinematically feasible plan did not reduce collisions in
the arena. Hybrid A* was about 1 s faster to B when it arrived (median -0.94 s on a 1 rad/s
turn-limited vehicle), but it reached B less often: 81.9 % vs 91.2 % for A* + follower over 8
families (synthetic). For a multirotor, keep A* + follower.

Search keywords for the row: `hybrid a star motion primitives`, `turn rate limited planner`,
`kinodynamic search drone`.

### docs/cheatsheets/close-area-a-to-b.md (or the close-area line of docs/cheatsheets/README.md)

"Hybrid A*", "turn rate", "fixed-wing-like", "kinodynamic": [close-area-planner-hybrid-astar](../../samples/close-area-planner-hybrid-astar/README.md) (pick it when the platform cannot turn in place at speed and time matters; it gave 0 collision gain and 9.3 points lower reached % than A* + follower on a 1 rad/s turn-limited vehicle, synthetic arena)

## Evidence matrix (docs/evidence-matrix.md), section Close-area A=>B

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-planner-hybrid-astar](./README.md#results-ran-2026-11-10-apple-m3-max-cpython-31210-numpy-254-scipy-1181) | Own numpy + scipy Hybrid A* (x, y, heading; arcs at 1.5 and 0.5 m/s limited to 1.0 rad/s, turns in place, straight shot to B, Dijkstra heuristic) on astar_esdf's range-built map and follower, vs astar_unknown and astar_unknown + pure-pursuit speed cap, on the stock and a 1.0 rad/s turn-limited vehicle | Ideal, 8 families: reached 86.2 vs 91.2 % (stock), 81.9 vs 91.2 % (turn-limited); collision 0 % for all; crazyflie random + office collision 25 vs 12.5 % (stock), 17.5 vs 17.5 % (turn-limited). Paired time to B -1.21 s (stock) / -0.94 s (turn-limited). Known-map plans: max heading change 2.131 vs 3.248 rad/m, total turn 6.429 vs 2.8 rad. Replan 13.30 / 24.75 ms median / p95 vs 20.67 / 85.55 ms (14 processes) | synthetic (2.5D point-mass arena) | 1200 flights: 20 layouts x 8 families (ideal) + 2 families (crazyflie), 3 planners, 2 vehicles, seed 0; plan quality 160 layouts | Own untuned implementation, no path smoothing; turn-limited vehicle is a chosen model, one limit (1.0 rad/s); most of the reached gap is runs scored stuck while flying back over their own track; host shared with other jobs; not run in Pyodide |

## Records

None created. The IJRR 2010 paper is already indexed as `res:dolgov-hybrid-astar-ijrr-2010`.
The 2008 workshop paper ("Practical search techniques in path planning for autonomous
driving") has no record. Its bibliographic data was written from memory; verify it before
adding.
