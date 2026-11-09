# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links below are written
relative to the file each block is meant for.

## Decoder row 32 (docs/problem-statement-decoder.md)

Replace the "Start from" cell of row 32 ("No runnable marker-goal starter in the hub (sample
pending: samples/close-area-arena)...") with:

> [fiducial-goal-apriltag](../samples/fiducial-goal-apriltag/) (synthetic: 0.16 m tag36h11 detected at >= 90 % to 5 m frontal, 4 m at 20-50 deg, 2 m at 70 deg with a 640 x 480, fx 500 px camera; tag-relative servo from 3 m off-axis ended within 0.1 m in 50/50 seeds). Then read [03-close-area-localization.md](research/close-area-nav/03-close-area-localization.md) section 3 and [01-planning-and-mapping.md](research/close-area-nav/01-planning-and-mapping.md) for the path that brings the tag into view

Append to the "Main risk" cell of row 32:

> Measured on synthetic images: heading flips (pose ambiguity) from 3 m on a 0.16 m tag, p95 heading error 39.6 deg at 5 m / 20 deg; a 0.40 m pad tag is not detected at 0.5 m because it overfills the frame, so nest a small tag in the pad

Search keywords for the row (add): `apriltag detection range view angle`, `fiducial goal final approach servo`, `landing pad tag pose ambiguity`.

## Evidence-matrix line (docs/evidence-matrix.md, section 14 "Close-area A=>B")

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [fiducial-goal-apriltag](../samples/fiducial-goal-apriltag/README.md#results-ran-2026-11-09-synthetic) | pupil-apriltags on rendered tag36h11 (0.16 m) images, 640 x 480 pinhole fx 500 px, blur 0.8 px, noise 3 DN; tag-relative velocity servo with 1-frame latency | Detection >= 90 % to 5 m at 0-10 deg, 4 m at 20-50 deg, 3 m at 60 deg, 2 m at 70 deg; fails (< 50 %) at 6 m frontal and 3 m at 70 deg; position error p95 <= 0.091 m where detection holds; harsh images (blur 1.5 px, noise 6 DN) hold only to 2 m. Final approach from 3 m off-axis: 50/50 seeds within 0.1 m, median 0.0145 m, max 0.0307 m | synthetic (rendered images, kinematic point mass) | 20 frames per cell x 80 cells per sweep, 3 sweeps; 50 approach seeds x 2 image settings | No lens distortion, rolling shutter, exposure or motion-coupled blur; level camera, no attitude; heading flips counted (83 frames in the default approach run), not mitigated |

## Cheat-sheet line (docs/cheatsheets/README.md)

| The brief says... | Sheet | Decoder rows |
|---|---|---|
| "marker", "land on the pad", "landing pad / helipad", "fly to the tag", "precision landing", "AprilTag / ArUco" | none yet: start at [fiducial-goal-apriltag](../../samples/fiducial-goal-apriltag/) for tag size vs detection range, then [close-area-arena](../../samples/close-area-arena/) for the path that brings the tag into view | 32, 31 |

## samples/README.md

Generated from sample.json (group "Close-area A=>B: goal and localization", a new group); no
hand edit needed. If the driver prefers one close-area group, change `group` to
"Close-area A=>B: planning and safety".

## stdlib test list (tools/stdlib-sample-tests.txt)

Add the line `fiducial-goal-apriltag` (close-area-arena is already listed). Its `test_smoke.py`
skips under plain python3 without numpy, opencv or pupil-apriltags.
