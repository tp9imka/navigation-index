# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links resolve from this file
(the sample is ./); rewrite them relative to the target file when pasting.

## Decoder (docs/problem-statement-decoder.md)

Row 33 "Indoor drone flight through VIO loss and recovery". In the "Start from" cell, replace
"No runnable indoor VIO-loss starter in the hub (sample pending: samples/close-area-arena)" with:

[close-area-relocalize](./) (scan-to-map relocalization with up
to 5 hypotheses on the close-area arena; dropout and jump faults, A* known map, 100 layouts)

Add to that row's "Main risk": in the synthetic arena, "hover until one hypothesis wins" deadlocks
when the scan has under 10 returns or two poses tie (a corridor: 20 of 20 runs hovered until
stuck); committing to the best match at once and re-checking it with a scan-to-map innovation
test reached B in 100 % of runs. Keep the innovation test; bound the hover or add a move that
separates the hypotheses.

Search keywords for the row: `relocalization scan matching occupancy grid`,
`multi-hypothesis relocalization hover`, `vio loss reset_counter innovation`.

## Evidence matrix (docs/evidence-matrix.md), section 14 Close-area A=>B

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-relocalize](./README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181) | After VIO loss (reset_counter, quality 0 or scan innovation test): correlative scan-to-map grid search on a likelihood field, up to 5 hypotheses, accept on score >= 0.6, best >= 1.02 x second, 3 scans in a row; hover while relocalizing; A* known-map planner | Dropout / jump faults: no relocalization reached 64 % / 36 % (1 % / 9 % collisions); commit-at-once 100 % / 100 %, 2 / 4 wrong commits (> 0.5 m), all later corrected; multi-hypothesis rule 80 % / 93 %, 0 wrong commits, 20 / 7 runs end hovering (too few returns or a tie); 0 % collisions for every relocalizing arm. Symmetric corridor: rule hovers in 20 of 20; commit-at-once 8 wrong commits, 100 % reached with the innovation test, 40 % collisions without it. Median recover 0.2 s vs 0.4 s | synthetic (2.5D point-mass arena) | 100 random layouts, seed 0, per fault; corridor 20 runs; thresholds set on seed 1 | Yaw is truth; map is the exact prior grid; hover is perfect in the sim; the innovation test also corrects dark-zone drift (227-331 triggers per 100 runs) |

## Cheat sheet (docs/cheatsheets/README.md)

The table has no close-area line yet. If one is added for "fly A to B indoors", add to its
"Sheet" cell:

"VIO lost", "relocalize", "kidnapped", "what if tracking fails": [close-area-relocalize](./) (commit to the best scan-to-map match and keep checking it; a hover-until-unique rule deadlocks in corridors)
