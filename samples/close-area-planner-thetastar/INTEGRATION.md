# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links below resolve from
this file (so check_links passes). When pasting into a file under docs/, replace `./` with
`../samples/close-area-planner-thetastar/` (from docs/cheatsheets/: `../../samples/close-area-planner-thetastar/`).
None of the snippets in (a) and (b) was run: the playground and the benchmark were not
touched. All numbers are synthetic (simulated arena), seed 0.

## (a) Browser playground (site/playground/)

### manifest.json, "files" (after the "sampling" group)

```json
    {"group": "thetastar", "src": "../../samples/close-area-planner-thetastar/arena.py", "dst": "thetastar/arena.py"},
    {"group": "thetastar", "src": "../../samples/close-area-planner-thetastar/thetastar.py", "dst": "thetastar/thetastar.py"},
```

Also add to the manifest "comment": `thetastar = Theta* and Lazy Theta* from
samples/close-area-planner-thetastar (its arena.py finds close_area_arena already imported).`

### worker.js, DRIVER_PY (after the Informed RRT* block)

```python
# Theta* and Lazy Theta* (samples/close-area-planner-thetastar). Unknown map offered as Lazy only:
# plain Theta* unknown-map replans were 1.88 s p95 in CPython (README).
try:
    _theta = _load_sample(THETASTAR_DIR, ["thetastar"])["thetastar"]
    PLANNERS["thetastar_known"] = lambda: _theta.make(known_map=True)
    PLANNERS["lazy_thetastar_known"] = lambda: _theta.make(known_map=True, lazy=True)
    PLANNERS["lazy_thetastar_unknown"] = lambda w: _theta.make(known_map=False, lazy=True, bounds=_bounds(w))
    WORLD_PLANNERS.add("lazy_thetastar_unknown")
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["thetastar"] = repr(e)
```

### worker.js, the runPython line that sets the folder variables (JS side)

Append `\nTHETASTAR_DIR = "${HOME}thetastar"` to the string that already sets
`SAMPLING_DIR = "${HOME}sampling"`.

### playground.js, LABELS.planner

```js
    thetastar_known: "Theta* (any-angle), known map", lazy_thetastar_known: "Lazy Theta*, known map",
    lazy_thetastar_unknown: "Lazy Theta*, unknown map (geofenced)",
```

Pyodide 314.0.7 was not run with these files. Expect replans slower than the CPython numbers.

## (b) close-area-benchmark/bench.py

```python
_theta = _load_sample("close-area-planner-thetastar", ["thetastar"])
```

PLANNERS entries:

```python
    "thetastar_known": (lambda w: _theta["thetastar"].make(known_map=True), None,
                        "Theta* known map", "close-area-planner-thetastar"),
    "lazy_thetastar_known": (lambda w: _theta["thetastar"].make(known_map=True, lazy=True), None,
                             "Lazy Theta* known map", "close-area-planner-thetastar"),
    "thetastar_unknown": (lambda w: _theta["thetastar"].make(known_map=False, bounds=_bounds(w)), None,
                          "Theta* unknown map", "close-area-planner-thetastar"),
    "lazy_thetastar_unknown": (lambda w: _theta["thetastar"].make(known_map=False, lazy=True, bounds=_bounds(w)),
                               None, "Lazy Theta* unknown map", "close-area-planner-thetastar"),
```

And: NEEDS `"thetastar_known": (_theta, "thetastar")` (same for the other three); add
`thetastar_known` and `lazy_thetastar_known` to PRIOR_MAP; SLOW `{"thetastar_unknown": 0,
"lazy_thetastar_unknown": 0, "thetastar_known": 1, "lazy_thetastar_known": 1}`. These rows were
already flown through the benchmark's own `run_one` by [bench.py](./bench.py) (results in
[results/flights_0.md](./results/flights_0.md)); the `--add-to matrix_0` run itself was not done.

## (c) Decoder and cheat sheet

### Decoder (docs/problem-statement-decoder.md), row 31 "Start from"

[close-area-planner-thetastar](./README.md) (Theta* / Lazy Theta*: same grid and cost as A*,
faster flights with a prior map, too slow per replan without one)

Search keywords: `theta star any-angle`, `lazy theta star`, `any-angle grid path`.

### Cheat sheet (docs/cheatsheets/close-area-a-to-b.md), section 4 "Numbers you can cite"

- Theta* vs A* + shortcut, same grid and cost, 20 layouts x 8 families: with a prior map Theta*
  reached B sooner in 157 of 160 layouts (median 6-34 % less time per family) on 0.5-7 % longer
  paths; pick Lazy Theta* (`make(lazy=True)`, plan median 73 ms vs A* 18 ms) when you have the map
  and a few hundred ms per replan. Without a map keep `astar_unknown`: Theta* replans hit 0.39-1.88 s
  p95 and 4-beam office collisions rose from 25 % to 35-60 %. Not re-run
  ([close-area-planner-thetastar](../../samples/close-area-planner-thetastar/README.md)).

The link above is written for docs/cheatsheets/close-area-a-to-b.md.

### Evidence matrix (docs/evidence-matrix.md), section 14 Close-area A=>B

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-planner-thetastar](./README.md#results-ran-2026-11-10-apple-silicon-arm64-16-cpus-cpython-31210-numpy-254-scipy-1181) | Own pure-Python Theta* and Lazy Theta* on astar_esdf's inflated 0.1 m grid and ESDF cost (any-angle edge priced by the cost integral), astar_esdf follower, no post-hoc shortcut | Paired time to B Theta* / A*: median 0.659-0.937 per family (known map), 0.749-0.908 (unknown); flown length 1.005-1.073; reached same as A* within one run except warehouse unknown (60-65 vs 55 %). Plan median 118 ms Theta*, 73 ms Lazy, 18 ms A* (known map, 1 process); unknown-map replan p95 1.88 s / 0.39 s / 75 ms. Crazyflie office collisions 60 / 35 / 25 % | synthetic (2.5D point-mass arena) | 20 layouts x 8 families, seed 0, ideal; crazyflie random and office; 1080 flights | Timing on a shared machine (load 38-256); Pyodide not run; cost model is an adaptation of the length-only papers; crazyflie office increase not traced |

### Record proposals (not created: data/ is outside this job's paths)

- `res:daniel-nash-koenig-felner-thetastar-jair-2010`: "Theta*: Any-Angle Path Planning on
  Grids", JAIR 39, 2010, arXiv 1401.3843. Concepts: `concept:path-planning`.
- `res:nash-koenig-tovey-lazy-thetastar-aaai-2010`: "Lazy Theta*: Any-Angle Path Planning and
  Path Length Analysis in 3D", AAAI 2010. Concepts: `concept:path-planning`.

`python3 tools/query.py search "theta star any-angle"` returned no paper record (only
`repo:ai-winter/python_motion_planning`, which implements Theta*). Titles, venues and authors were
checked against the AAAI and arXiv abstract pages; volume and pages of the JAIR paper were not.
