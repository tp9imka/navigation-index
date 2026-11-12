# Proposed hub wiring for the depth-camera column (text only)

The driver applies these. This change edited no shared file. Links resolve from this file
(samples/close-area-benchmark/); rewrite them relative to the target file when applying.

Source of every number: [results/matrix_depth_0.md](results/matrix_depth_0.md) and
[results/matrix_depth_0.compare.md](results/matrix_depth_0.compare.md). Input: synthetic (2.5D
point-mass arena, simulated sensor), seed 0, 6 layouts per cell, scored on truth. Directional only.
Yaw fixed toward B (benchmark loop and playground default). Numbers updated 2026-11-12 after the re-run with the
dropped-beam fix on ([upstream-findings section 22](../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls));
the cheat-sheet part below is applied, the decoder "Main risk" part is not.

## Cheat sheet (docs/cheatsheets/close-area-a-to-b.md), planner table

Add a column "Without a map, depth camera" after "Without a map, 4 beams". Only the five map-free
rows below were run on the depth preset; prior-map rows are unchanged ("With a map" becomes "all
sensors", since those planners never read the scan).

| Family | Without a map, depth camera (n = 6, directional) |
|---|---|
| random clutter | `astar_unknown`, `astar_unknown_f2`, `dstar_lite` or `mppi_astar` 100 / 0 |
| u_trap | `astar_unknown`, `astar_unknown_f2`, `dstar_lite` or `mppi_astar` 100 / 0 |
| narrow_gap (0.5-0.9 m) | `mppi_astar` 83 / 0 |
| office | `mppi_astar` 100 / 0 (`astar_unknown` or `dstar_lite` 83 / 0) |
| warehouse | `astar_unknown` or `mppi_astar` 83 / 0 |
| forest (open poles) | `astar_unknown`, `astar_unknown_f2`, `dstar_lite`, `dwa_mem` or `mppi_astar` 100 / 0 |
| maze | `mppi_astar` 100 / 0 (`astar_unknown` or `dstar_lite` 83 / 0) |
| glass_office | none works: `astar_unknown`, `dstar_lite` or `mppi_astar` 17 / 83; `astar_unknown_f2` 0 / 0 or `dwa_mem` 17 / 0 are safest |

Text above the table: add `"Depth camera" = depth_cam_87 (30 beams over 87 deg forward, 0.3-5 m,
glass invisible, RealSense D435i class), yaw held toward B; 6 layouts per cell, so read it as a
direction, not a ranking.`

Add one bullet to "How to read it":

- **No map, forward depth camera:** `mppi_astar` first (85 % reached [73, 93], 10 % collision
  [5, 22] pooled over 48 synthetic runs, 95 % Wilson), `astar_unknown` (75 / 17) and `dstar_lite`
  (73 / 15) behind. Glass rooms still need a map: glass is invisible to the camera (glass_office
  83 % collision for all three).

## Decoder (docs/problem-statement-decoder.md), row 31

Add to "Main risk":

With a forward depth camera (RealSense class, 87 deg, 0.3-5 m) and no map, the best map-free planner
in the synthetic arena (`mppi_astar`) reaches B in 85 % [73, 93] of 48 runs with 10 % collisions,
against 94 % and 0 % on an ideal 360 deg fan, and glass walls still cause most of the collisions
([close-area-benchmark](./README.md#forward-depth-camera)).
