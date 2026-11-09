# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links below resolve from
this file (so check_links passes). When pasting into a file under docs/, replace `./` with
`../samples/close-area-planner-sampling/`; the cheat-sheet link already works from
docs/cheatsheets/.

## Decoder (docs/problem-statement-decoder.md)

Add to the "Start from" cell of the close-area A=>B row (row 31):

[close-area-planner-sampling](./README.md) (RRT* and
Informed RRT* against A* on the same grid; shows why A* is the default)

Add to that row's "Main risk": a sampling planner (RRT*) cannot tell "no path" from "not found
yet"; with 1000 samples it found a 0.4 m gap in 28.3 % of plans where A* found it in 100 %
(synthetic arena). If you use one, size the budget for the narrowest gap.

Search keywords for the row: `rrt star narrow gap`, `informed rrt star ellipse`,
`sampling planner vs a star grid`.

## Evidence matrix (docs/evidence-matrix.md), section 14 Close-area A=>B

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-planner-sampling](./README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181) | Own numpy RRT* and Informed RRT* on the known inflated 0.1 m grid, same inflation rule, shortcut and carrot follower as astar_esdf; budgets 1000 and 5000 samples | Planning success vs gap 0.4 / 0.5 / 0.6 / 1.2 m: A* 100 / 100 / 100 / 100 %, RRT* 1000 28.3 / 60.3 / 82.7 / 100 %, RRT* 5000 85.7 / 99.3 / 100 / 100 %; plan median A* 30-76 ms, RRT* 5000 310-621 ms (14-process load). Arena flights, 50 layouts: Informed RRT* 5000 and A* both 100 % reached on random and narrow_gap; time to goal 23.58 vs 18.81 s (random), median min clearance 0.269 vs 0.635 m | synthetic (2.5D point-mass arena) | Sweep: 30 layouts x 10 RNG seeds per width, seed 0; flights: 50 layouts, seed 0 | Known static map only; RRT* not tuned; no RRT-Connect or narrow-passage samplers; at the 0.15 m fallback inflation 6-28 % of planned paths (A* and RRT*) dip below the 0.15 m radius on exact geometry |

## Cheat sheet (docs/cheatsheets/README.md)

The table has no close-area line in this checkout. If the driver adds one for the close-area
samples, add to its "Sheet" cell:

"RRT", "sampling planner", "narrow gap": [close-area-planner-sampling](../../samples/close-area-planner-sampling/README.md) (A* is complete and 8x faster on a small grid; RRT* misses narrow gaps at low budgets)

## Record proposal (not created: data/ is outside this job's paths)

`res:gammell-informed-rrtstar-iros-2014`: Gammell, Srinivasa, Barfoot, "Informed RRT*: Optimal
sampling-based path planning focused via direct sampling of an admissible ellipsoidal
heuristic", IROS 2014. Concepts: `concept:path-planning`. A search for "gammell informed rrt
ellipsoid" returned no record. The bibliographic fields were written from memory and were
not checked against the paper; verify the DOI before adding.
