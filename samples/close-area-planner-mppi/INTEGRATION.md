# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links below resolve from
this file. When pasting into a file under docs/, replace `./` with
`../samples/close-area-planner-mppi/`; the cheat-sheet link already works from docs/cheatsheets/.

All numbers: synthetic arena (2.5D point mass, simulated sensor, true pose), seed 0, 20 layouts
per family, from [results/bench_ideal_0.md](./results/bench_ideal_0.md),
[results/bench_crazyflie_0.md](./results/bench_crazyflie_0.md),
[results/timing_0.md](./results/timing_0.md) and [results/sweep_0.md](./results/sweep_0.md).

## (a) Browser playground (site/playground)

### manifest.json "files"

Append after the two `"sampling"` entries:

```json
    {"group": "mppi", "src": "../../samples/close-area-planner-mppi/arena.py", "dst": "mppi/arena.py"},
    {"group": "mppi", "src": "../../samples/close-area-planner-mppi/mppi.py", "dst": "mppi/mppi.py"},
```

Add to the manifest `"comment"` after the sampling sentence: `mppi = MPPI (guide none and on the
unknown-map A* path) from samples/close-area-planner-mppi (numpy + scipy only; its arena.py finds
close_area_arena already imported).`

### worker.js

1. In the `py.runPython(...)` call that defines the folder variables (the line ending
   `SAMPLING_DIR = "${HOME}sampling"\nRELOC_DIR = "${HOME}reloc"`), add `\nMPPI_DIR = "${HOME}mppi"`:

```js
    `DWABUG_DIR = "${HOME}dwa_bug"\nDSTAR_DIR = "${HOME}dstar"\nSAMPLING_DIR = "${HOME}sampling"\nRELOC_DIR = "${HOME}reloc"\nMPPI_DIR = "${HOME}mppi"`);
```

2. In DRIVER_PY, after the Informed RRT* `try` block (before the "A* + MPC ... is not offered"
   comment):

```python
# MPPI, unknown map, geofenced as in the benchmark (samples/close-area-planner-mppi)
try:
    _mppi = _load_sample(MPPI_DIR, ["mppi"])["mppi"]
    PLANNERS["mppi"] = lambda w: _mppi.make(guide="none", bounds=_bounds(w))
    PLANNERS["mppi_astar"] = lambda w: _mppi.make(guide="astar", bounds=_bounds(w))
    WORLD_PLANNERS.update(("mppi", "mppi_astar"))
except Exception as e:                       # noqa: BLE001
    LOAD_ERRORS["mppi"] = repr(e)
```

Without the geofence (sampling-group style, no world argument) the lines are
`PLANNERS["mppi"] = lambda: _mppi.make()` and
`PLANNERS["mppi_astar"] = lambda: _mppi.make(guide="astar")`. Then the map corner is set from B on
the first step; the numbers below were measured with the geofence.

3. Optional, playground.js `LABELS.planner`: `mppi: "MPPI, goal only (no global plan)",
   mppi_astar: "MPPI on the unknown-map A* path"`. Optional, index.html intro links: add
   `<a href="../../samples/close-area-planner-mppi/README.md">MPPI</a>,` next to Informed RRT*.

What was checked: the manifest arena files plus these two files were copied into a Pyodide-like
folder layout and loaded with the worker's `_load_sample` recipe in CPython 3.12, after the
sampling group (so `arena` is swapped correctly). All three factories flew office layout 0 (console only, not saved).
**Not run in Pyodide 314.0.7**; the step time there is not measured. The step is 4-5 ms median
in CPython ([results/timing_0.md](./results/timing_0.md)); wasm is slower, by how much is not known.

## (b) close-area-benchmark bench.py PLANNERS entry

Next to the other `_load_sample` calls:

```python
_mppi = _load_sample("close-area-planner-mppi", ["mppi"])
```

In `PLANNERS`:

```python
    "mppi": (lambda w: _mppi["mppi"].make(guide="none", bounds=_bounds(w)), None,
             "MPPI, goal only, unknown map", "close-area-planner-mppi"),
    "mppi_astar": (lambda w: _mppi["mppi"].make(guide="astar", bounds=_bounds(w)), None,
                   "MPPI on the unknown-map A* path", "close-area-planner-mppi"),
```

In `NEEDS`: `"mppi": (_mppi, "mppi"), "mppi_astar": (_mppi, "mppi"),`. Add both names to
`DEFAULT_PLANNERS` and to the docstring list, then
`python bench.py --add-to matrix_0 --planners mppi,mppi_astar --workers 14`.

What was checked: these exact lambdas, registered at runtime in the benchmark's own `run_one`,
gave rows identical to this sample's results in 32 of 32 runs (layouts 0-1, 8 families, both
entries; [results/benchmark_entry_check.txt](./results/benchmark_entry_check.txt)). Expected
matrix cells (ideal, reached / collision %): mppi 90/0, 0/0, 25/0, 25/0, 15/0, 100/0, 0/0, 10/0;
mppi_astar 100/0, 100/0, 95/0, 100/0, 65/0, 100/0, 95/0, 95/0 (random, u_trap, narrow_gap,
office, warehouse, forest, maze, glass_office). The crazyflie column was run only for random
and office here (mppi 55/40 and 5/75; mppi_astar 80/20 and 10/85).

## (c) Decoder and cheat sheet

### Decoder (docs/problem-statement-decoder.md), row 31 "Start from" cell

[close-area-planner-mppi](./README.md) (MPPI sampling-based MPC, numpy only, runs in the
browser; alone it stays in U traps and mazes (0 % reached), on an unknown-map A* path it reaches
as often as A* and is faster to B in 7 of 8 families; collides with 4 beams)

Add to row 31 "Main risk": MPPI without a global plan is a local controller: 0 % reached on
u_trap and maze (synthetic, 20 layouts). With the Crazyflie 4-beam preset it collided in 20 %
(random) and 85 % (office) of runs where the unknown-map A* collided in 0 % and 25 %.

Search keywords for the row: `mppi sampling mpc`, `model predictive path integral`,
`local minimum u trap maze`.

### Cheat sheet (docs/cheatsheets/close-area-a-to-b.md), one line under the planner picks

- MPPI ([close-area-planner-mppi](../../samples/close-area-planner-mppi/README.md)): pick it as
  the local controller on top of a global path (`make(guide='astar')`) when you want smooth,
  model-aware velocity setpoints, faster flights through rooms (maze median 33.6 vs 50.1 s to B)
  and no QP solver (runs in Pyodide). Never alone in rooms with dead ends (0 % on u_trap and
  maze), and not on a 4-beam sensor until unknown space has a cost (20-85 % collisions).
  Synthetic arena, not re-run on hardware.

## Evidence matrix (docs/evidence-matrix.md), section 14 Close-area A=>B

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-planner-mppi](./README.md#results-ran-2026-11-10-apple-m3-max-cpython-31210-numpy-254-scipy-1181) | Own numpy MPPI (Williams et al. 2017 update): K = 256 velocity-setpoint sequences x 2 s, AR(1) noise sigma 0.6 m/s, lambda 1, ESDF from the range-built log-odds map, point-mass rollouts matching vehicle.py; guide none (target B) or guide astar (2 m lookahead on the unknown-map A* path); vs the benchmark's geofenced unknown-map A* | Ideal sensor, reached %: MPPI alone 0 on u_trap and maze, 90 random, 100 forest; MPPI + A* 95-100 in 7 families (A* 90-100), warehouse 65 vs 55; 0 % collisions for all three; median time to B MPPI + A* vs A*: maze 33.62 vs 50.06 s, random 20.24 vs 19.01 s; median min clearance maze 0.365 vs 0.589 m. Crazyflie preset collisions MPPI + A* vs A*: random 20 vs 0 %, office 85 vs 25 %. Step 4.18-4.33 ms median, p95 57-64 ms, max 87 ms with the A* replans, one process; MPPI update alone 2.2-10.4 ms for K x H 64 x 10 to 1024 x 40. K 64-1024 changed outcomes by at most 1 of 10 layouts per sweep cell | synthetic (2.5D point-mass arena) | 20 layouts per family, seed 0 (sweep 10 layouts); astar_unknown rows identical to the benchmark matrix (200/200) | Constants tuned on dev seed 1; the straight-at-target sample was added after a first seed-0 sweep, so seed 0 is not fully held out for it; lambda and sigma not swept on seed 0; true pose; laptop CPython timing; not run in Pyodide |

## Record proposal (not created: data/ is outside this job's paths)

`res:williams-information-theoretic-mpc-icra-2017`: G. Williams, N. Wagener, B. Goldfain,
P. Drews, J. M. Rehg, B. Boots, E. A. Theodorou, "Information Theoretic MPC for Model-Based
Reinforcement Learning", ICRA 2017, PDF
https://homes.cs.washington.edu/~bboots/files/InformationTheoreticMPC.pdf. Concepts:
`concept:path-planning`, `concept:obstacle-avoidance`. `python3 tools/query.py search "mppi model
predictive path integral"` returned no paper record for it (only Nav2, which ships an MPPI
controller). The DOI was not checked; add it after looking it up. The journal version is
arXiv:1707.02342 (IEEE T-RO 2018).
