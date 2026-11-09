# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links are written relative
to this file (samples/close-area-safety-filter/) so they resolve here; the driver rewrites them
for the target file.

## Decoder (docs/problem-statement-decoder.md)

Add to the "Start from" cell of the close-area A=>B row:

[close-area-safety-filter](./README.md) (safety-filter
harness between planner and vehicle on the arena; F0 none, F1 PX4 Collision Prevention style,
F2 PX4-CBF as shipped; A* under VIO faults, with and without obstacles the range fan cannot see)

Add to that row's "Main risk": a range-only filter (PX4-CBF) already removes every collision
with obstacles a 360 deg fan sees (0 % in all fault cases, synthetic); it does nothing for
map-only obstacles (glass, thin poles), where A* under a 0.5 m VIO jump still collides in 11 %
of runs. Pitch the integrity margin for what the sensor cannot see, not as a general filter.

Search keywords for the row: `safety filter cbf range px4`, `collision prevention cp_dist`,
`unsensed obstacle glass pole map only`.

## Evidence matrix (docs/evidence-matrix.md), close-area section

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-safety-filter](./README.md#results-ran-2026-11-09-apple-m3-max-cpython-31115-numpy-246-scipy-1171) | Safety filter between arena A* (known map) and vehicle, VIO-like EKF with faults; F0 none, F1 CP-stop (PX4 docs reading, CP_DIST 0.5 m ours), F2 PX4-CBF analytic, doc 05 Table II gains | Unsensed off: collisions F0 7 / 4 / 1 % (jump / bias / dropout), F1 and F2 0 % in all cases. Unsensed on (2 map-only obstacles per layout): F2 3 / 11 / 7 / 4 % (none / jump / bias / dropout), all with unsensed obstacles. F2 truth-pose reach 92 % (on), 86 % (off) vs 100 % F0 | synthetic (2.5D point-mass arena) | 100 random layouts x 5 cases x 3 arms x 2, seed 0 | Doc 04 fail condition met without map-only obstacles; F2 at 50 Hz, no FoV constraint (fan is 360 deg); one planner, one seed; reach under faults limited by estimator drift (median max pose error 0.34-0.68 m) |

## Cheat sheet (docs/cheatsheets/README.md)

Extend the close-area line's "Sheet" cell:

"safety filter", "CBF", "collision prevention", "PX4-CBF": [close-area-safety-filter](../../samples/close-area-safety-filter/) (range-only CBF already stops collisions with sensed obstacles under VIO faults; only map-only obstacles are left for an integrity margin)

## Research synthesis (docs/research/close-area-nav/README.md), "Kill test" paragraph

Proposed sentence: "Kill test A (2026-11-09, synthetic, [close-area-safety-filter](./README.md)):
PX4-CBF as shipped reaches 0 % collisions in all fault cases when every obstacle is visible to
the range fan, which meets the fail condition for that setting; with two map-only obstacles per
layout it collides in 3-11 %, all with those obstacles. The headline survives only as a margin
for obstacles the range sensor cannot see."
