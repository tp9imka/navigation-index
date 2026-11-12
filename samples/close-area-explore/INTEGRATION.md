# Proposed hub wiring (text only, not applied)

The driver applies these. This sample edited no shared file. Links below resolve from this file
(samples/close-area-explore/); when pasting into docs/, replace `./` with
`../samples/close-area-explore/` (decoder, evidence matrix) or
`../../samples/close-area-explore/` (cheat sheet). All numbers are synthetic.

## Decoder row 32 (docs/problem-statement-decoder.md): drone flight to a visual goal B

Add to the "Approach" cell, after the first sentence:

If the brief does not put B in view from A, search first: fly to the nominal B if one is given,
then sweep the region at a lane spacing set by the detector's range, then hand over to the tag.
Plain frontier exploration is not a search: a 6 m range sensor maps the room before a 2 m
detector has seen it.

Add to the "Start from" cell:

[close-area-explore](./README.md) (synthetic: B as a region of radius 0 / 2 / 5 m or unknown,
detected within 2 m in line of sight; with a nominal within 2 m every arm found B in 86.7-95.0 %
of 60 runs, with R = 5 m random waypoints 85.0 %, lawnmower 83.3 %, nominal-first + frontier
81.7 %; with B unknown nearest-frontier found 41.7 % [30.1, 54.3] in 180 s)

Add to the "Main risk" cell:

B outside the detector's view from A. Without a nominal B, nearest-frontier search found B in
41.7 % of ideal-sensor runs (warehouse 5 %) in 180 s; with the 4-beam crazyflie preset 18.3 %.
Ask whether a nominal B is given and how far it can be off.

Search keywords for the row: `frontier exploration search`, `lawnmower sweep nominal goal`,
`find marker unknown position`.

## Close-area benchmark (samples/close-area-benchmark)

The benchmark matrix scores planners with B given; this sample adds a search axis that the
matrix does not have. Proposed text for the benchmark README "What is in the matrix" section, or
a row in its INTEGRATION.md cheat-sheet line:

- B not given as a coordinate: see [close-area-explore](./README.md). Same arena, same
  unknown-map A* follower (`astar_unknown` row), same presets, families random / office /
  warehouse, 180 s budget instead of 60 s, stuck = under 0.5 m of path in 10 s. Its `oracle`
  row (B given) uses the same follower as the benchmark's `astar_unknown` row, with the map
  origin at the geofence and the longer budget: ideal 93.3 % reached, crazyflie 38.3 % collision,
  pooled over the three families.

Replay for the showcase: copy
[results/replay_office_0_nominal_frontier_r5_ideal.json](./results/replay_office_0_nominal_frontier_r5_ideal.json)
to `site/data/showcase/replays_v2/office__explore_nominal_frontier_r5.json` and add it to that
folder's `index.json` under office. It has the `close-area-replay/2` top-level fields plus a
`search` object (nominal, region radius, detection range, time found); a viewer that ignores
unknown keys shows the path, and drawing the nominal circle needs a viewer change.

## Evidence matrix (docs/evidence-matrix.md), section 14 Close-area A=>B

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-explore](./README.md#results-ran-2026-11-10-apple-m3-max-macos-2662-cpython-31210-numpy-254-scipy-1181) | Search for B on the arena's unknown-map A*: nearest frontier (Yamauchi 1997), nominal-first then frontier, lawnmower (3 m lanes), random waypoints, oracle; B = nominal + radius 0 / 2 / 5 m or unknown; detected within 2 m with line of sight (AprilTag harsh-sweep range) | Ideal preset, 60 runs per cell: nominal within 2 m => found 88.3-100 %, median time to B 21.82-28.96 s (oracle 22.8 s); R = 5 m => random_walk 91.7 %, lawnmower 86.7 %, nominal_frontier 81.7 % (median time to find 43.2 / 55.25 / 29.2 s); unknown => frontier 43.3 % [31.6, 55.9], lawnmower 26.7 %, random_walk 13.3 %. Missed frontier runs ended with the map complete (median coverage 1.02-1.03). Crazyflie preset: oracle collides 38.3 %, unknown-B frontier finds 3.3 % | synthetic (2.5D point-mass arena, geometric detection) | 20 layouts x 3 families x 2 presets, seed 0, 1560 runs, 180 s budget | Detection omnidirectional, no false positives, no camera FOV; true pose; B placed by the arena near the far corner; seed 0 partly a tuning seed |

## Cheat sheet (docs/cheatsheets/close-area-a-to-b.md)

Add to section 6 "Top traps":

- **B is a marker you cannot see from A.** Frontier exploration maps the room, it does not
  search it: with a 6 m range sensor and a 2 m detector it found B in 43.3 % of runs in 180 s
  ([close-area-explore](../../samples/close-area-explore/README.md), synthetic). Get a nominal
  B; with one within 2 m every arm found B in 88.3 % or more.

## Record proposal (not created: data/ is outside this job's paths)

`res:yamauchi-frontier-exploration-cira-1997`: B. Yamauchi, "A frontier-based approach for
autonomous exploration", Proc. IEEE CIRA 1997, Monterey, pp. 146-151, DOI
10.1109/CIRA.1997.613851 (DOI as cited by a third-party repository README, not checked against
IEEE Xplore). PDF: https://www.cs.cmu.edu/~motionplanning/papers/sbp_papers/integrated1/yamauchi_frontiers.pdf.
Concepts: `concept:path-planning`. `python3 tools/query.py search "yamauchi frontier exploration"`
returned no such record (only FUEL, Co-NavGPT, the CMU exploration environment and RACER).

## Upstream finding for docs/upstream-findings.md (hub code, close-area-arena)

`planners/astar_esdf.py` `LogOddsMap.update` traces a beam with no return (`inf`, which the
sensor also returns for a dropped beam) as free out to `max_range`. A dropped beam therefore
marks cells behind a wall as free. In this sample the planner's known-free area at the end of a
run reached 1.25 x the true free area; the three highest-coverage runs (1.19-1.25) rerun with
dropout 0 ended at 0.79-0.98 ([results/analysis_0.md](./results/analysis_0.md), synthetic).
Possible fix: skip dropped beams, or trace no-return beams only when the sensor reports
"no target" separately from "dropout". Not changed here.
