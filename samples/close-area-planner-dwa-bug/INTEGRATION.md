# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links below are written
relative to this file (samples/close-area-planner-dwa-bug/); adjust them when pasting into the
target file.

## Decoder (../../docs/problem-statement-decoder.md)

Add to the "Start from" cell of row 31 (close-area A=>B with obstacles):

[close-area-planner-dwa-bug](./README.md) (DWA, Bug2 and TangentBug from range returns only,
measured next to APF and VFH+ on a 72-beam and a Crazyflie-like 4-beam fan)

Add to that row's "Main risk": a DWA with only a goal-heading term is a local planner and stays
in a U trap (0 % reached in the synthetic arena); Nav2 runs it under a global planner. Bug2's
completeness does not survive a wall follower that keeps 0.45 m off the wall: 0 % through
0.5-0.9 m gaps.

Search keywords for the row: `dynamic window approach dwa`, `bug2 tangentbug wall follow`,
`scan memory 4 beam`.

## Evidence matrix (../../docs/evidence-matrix.md), close-area section

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-planner-dwa-bug](./README.md#results-ran-2026-11-09-apple-m3-max-macos-2662-cpython-31210-numpy-254-scipy-1181) | Holonomic DWA (window from the arena a_max, 1.5 s rollouts, heading + clearance + speed), DWA with 3 s scan memory, Bug2, TangentBug; APF + escape and VFH+ from the reactive sample; 72-beam 6 m and 4-beam 4 m fans | 72 beams: TangentBug reached 92 % random, 86 % u_trap, 58 % narrow_gap; Bug2 92 %, 94 %, 0 %; DWA 86 %, 0 %, 12 %; 0 % collisions for all three. 4 beams, random: APF 82 % (8 % collisions), Bug2 74 % (20 %), TangentBug 38 % (62 %), DWA 30 % (52 %), DWA + memory 36 % (18 %). Only TangentBug leaves the U trap on 4 beams (30 %, 46 % collisions) | synthetic (2.5D point-mass arena) | 50 layouts per cell, seed 0; checked on seed 1 | 4-beam fan is ideal rays, no cone; DWA memory uses the truth pose; DWA is not Nav2 DWB (no global path, no critics); Bug planners simplified |

## Cheat sheet (../../docs/cheatsheets/README.md, and ../../docs/cheatsheets/close-area-a-to-b.md)

Extend the close-area line's "Sheet" cell:

"DWA", "dynamic window", "Nav2", "Bug2", "TangentBug", "wall follow": [close-area-planner-dwa-bug](./README.md) (no map, 72 beams: TangentBug best all-round, 0 % collisions; 4 beams: APF + escape still best, scan memory cuts collisions by about two thirds)

One line for the close-area one-pager, local planner section:

- Local planner without a map: 72-beam lidar => TangentBug; Crazyflie-like 4 beams => APF with
  the wall-follow escape plus a short scan memory, and a known map with A* for U traps and
  narrow gaps ([numbers](./README.md#reading)).

## Records (data/resources/, driver to add if wanted)

The hub has no records for these sources (`python3 tools/query.py search "dynamic window
approach"` and `search "bug2 tangentbug lumelsky"` returned nothing relevant on 2026-11-09):

- Fox, Burgard and Thrun 1997, The dynamic window approach to collision avoidance, IEEE RAM
  4(1), doi 10.1109/100.580977. Concepts: `concept:obstacle-avoidance`, `concept:path-planning`.
- Lumelsky and Stepanov 1987, Algorithmica 2, doi 10.1007/BF01840369 (Bug1 / Bug2). Same concepts.
- Kamon, Rivlin and Rimon 1998, TangentBug, IJRR 17(9), doi 10.1177/027836499801700903. Same
  concepts.

Once added, list their ids in this sample's `sample.json` "related".
