# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links are written relative
to the target file.

## Decoder (docs/problem-statement-decoder.md)

Add to the "Start from" cell of the close-area A=>B row (row 31 as proposed by
close-area-arena):

[close-area-planner-reactive](./) (APF with a wall-follow
escape and VFH+ from range returns only; measured on a 72-beam and a Crazyflie-like 4-beam fan)

Add to that row's "Main risk": with only 4 horizontal beams (Crazyflie Multi-ranger), a
memoryless reactive planner hits corners between beams (VFH+ 72-98 % collisions in the
synthetic arena); keep a scan memory or a map, or slow down hard.

Search keywords for the row: `potential field wall follow escape`, `vfh+ polar histogram range`,
`crazyflie multi-ranger 4 beam`.

## Evidence matrix (docs/evidence-matrix.md), close-area section

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-planner-reactive](./README.md#results-ran-2026-11-09-apple-m3-max-cpython-31115-numpy-246-scipy-1171) | APF on raw returns with a wall-follow escape after 3 s of no progress; VFH+ (polar histogram, hysteresis, valley cost, density speed); 72-beam 6 m fan and 4-beam 4 m fan | 72 beams: APF reached 98 % random, 92 % u_trap (2 % with the escape off), 0 % narrow_gap; VFH+ 96 % random, 0 % u_trap (50 of 50 stop inside the cup), 62 % narrow_gap; 0 % collisions. 4 beams: APF collisions 8 % random, 54 % u_trap, 34 % narrow_gap; VFH+ 72 %, 98 %, 96 % | synthetic (2.5D point-mass arena) | 50 layouts per cell, seed 0; defaults tuned on seed 1 | 4-beam fan is ideal rays with no beam cone; planners memoryless; hand-tuned on 20 dev layouts |

## Cheat sheet (docs/cheatsheets/README.md)

Extend the close-area line's "Sheet" cell:

"no map", "Crazyflie", "Multi-ranger", "reactive", "potential field": [close-area-planner-reactive](../../samples/close-area-planner-reactive/) (APF + escape beats VFH+ in a U trap, VFH+ beats APF through a narrow gap, both collide often on 4 beams)
