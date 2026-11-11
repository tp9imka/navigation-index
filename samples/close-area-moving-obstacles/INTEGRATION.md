# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file. Links are written relative
to this file (samples/close-area-moving-obstacles/) so they resolve here; the driver rewrites
them for the target file.

## Decoder (docs/problem-statement-decoder.md), row 31

Add to the "Start from" cell:

[close-area-moving-obstacles](./README.md) (1-3 walking people per layout at 0.5 and 1.0 m/s
in the arena; A* replan on prior map + latest scan, A* + PX4-CBF range filter, APF; collisions,
stuck, time and warning before contact)

Add to "Main risk": A* replanning alone collides with walking people in 14 % (0.5 m/s) and 36 %
(1.0 m/s) of runs, against 0 % with them frozen, and 5 Hz replanning does not help (12 % / 36 %).
The person walks into the slow drone (vehicle closing speed under 0.1 m/s in most contacts). A
range-only CBF filter (F2) on top gives 0 % collisions but 16 % stuck. Synthetic, no motion
prediction.

Search keywords for the row: `moving obstacles people replan`, `dynamic obstacle cbf apf`.

## Evidence matrix (docs/evidence-matrix.md), section 14 Close-area A=>B

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-moving-obstacles](./README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181) | 1-3 cylinders r 0.25 m per random layout on seeded segments across A-B, constant-speed ping-pong at 0.0 (frozen control), 0.5, 1.0 m/s; arms: arena A* + ESDF on prior map + latest scan hits (2.5 Hz, early replan to 5 Hz; and 5 Hz periodic), the same + F2 PX4-CBF as shipped (close-area-safety-filter), APF with escape (close-area-planner-reactive) | Collision 0 / 0.5 / 1.0 m/s: A* 0 / 14 / 36 %, A* 5 Hz 0 / 12 / 36 %, A* + F2 0 / 0 / 0 %, APF 0 / 0 / 2 %. Reached: A* 100 / 86 / 64 %, A* + F2 80 / 84 / 84 % (stuck 20 / 16 / 16 %, all but one on layouts F2 already sticks on without movers), APF 96 / 98 / 94 %. A* collisions: contact 4.9-15.3 s after take-off, mover visible 2.7-8.7 s before contact, vehicle at median 0.30-0.39 m/s with near-zero closing speed | synthetic (2.5D point-mass arena, truth pose) | 50 random layouts x 3 speeds x 4 arms, seed 0 | No motion prediction; people walk straight lines and ignore the drone; 360 deg ideal fan; one family, one seed; planner and filter defaults from sibling samples, not tuned for movers; APF cruises at 1.0 vs A* 1.5 m/s |

## First-day intake (docs/first-day-intake.md), section 3.5 Q7, replace the "Dynamic" bullet

- **Dynamic (people, other drones)** => A* replanning on the latest scan is not enough: in the
  arena it collided in 14 % (0.5 m/s people) and 36 % (1.0 m/s) of runs, 5 Hz replans did not
  help. Put a range-only CBF filter (PX4-CBF style) under the planner: 0 % collisions, at 16 %
  stuck. APF also held 0-2 %. Synthetic, no motion prediction
  ([close-area-moving-obstacles](./README.md)).

## Cheat sheet (docs/cheatsheets/close-area-a-to-b.md)

Section 3 "Which planner first", new row:

| Moving obstacles (people walking through) | A* replan + F2 range filter ([close-area-moving-obstacles](./README.md)) | A* alone collided in 14-36 % of runs; with F2 0 %, 16 % stuck; APF 0-2 % (synthetic) |

Section 4 "Arena limits" item: replace "no dynamic obstacles" with "dynamic obstacles only as
constant-speed people in close-area-moving-obstacles (no prediction, random family only)".

## Cheat-sheet index (docs/cheatsheets/README.md)

Extend the close-area line's "Sheet" cell:

"moving obstacles", "people", "dynamic obstacles": [close-area-moving-obstacles](./README.md)
(A* replan alone collides with walking people in 14-36 % of runs; a PX4-CBF style range filter
removes them at a 16 % stuck cost)
