# Proposed hub wiring (text only, not applied)

The driver applies these; this sample did not edit any shared file.

## Decoder row (docs/problem-statement-decoder.md)

Proposed as row 31, after row 30.

| # | Problem statement | Recommended approach | Stack | Datasets | Start from | Main risk | Pitch |
|---|---|---|---|---|---|---|---|
| 31 | Fly a drone from A to B in a close area, possibly with obstacles | Write the planner against three calls (`pose()`, `ranges()`, `send_setpoint()`) and compare it in one seeded arena before touching hardware: straight baseline, then APF and grid A* with clearance cost; score on truth (reached, collision, stuck, min clearance). Same planner then drives SITL or the real drone through an adapter. | [close-area-nav synthesis](../../docs/research/close-area-nav/README.md), [planning and mapping](../../docs/research/close-area-nav/01-planning-and-mapping.md) section 5a, [sims and platforms](../../docs/research/close-area-nav/02-sims-platforms-competitions.md), [RotorPy](../../catalog/repos/spencerfolk__rotorpy.md), [gym-pybullet-drones](../../catalog/repos/learnsyslab__gym-pybullet-drones.md) | none (synthetic layouts: random, u_trap, narrow_gap) | [close-area-arena](../close-area-arena/) (seeded 2.5D arena, truth scorer, straight baseline), [sitl-docker](../sitl-docker/) | A 2.5D point-mass arena hides attitude dynamics, tracking error and sensor artefacts; the estimate, not the planner, is what broke past competitions | "Every planner we tried was scored on the same seeded layouts, on truth, and the code that won flies the drone unchanged." |

Search keywords for the row: `close area A to B obstacle avoidance arena`, `occupancy grid ESDF A* range sensor`, `u trap potential field local minimum`.

## Evidence-matrix line (docs/evidence-matrix.md)

Proposed for a new section "14. Close-area A=>B" (or section 13 if the driver prefers to keep it
with functional checks):

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-arena](../close-area-arena/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181) | Straight-line baseline that slows to a stop for returns ahead, 72-beam 6 m range fan | Reached 40 %, collision 0 %, stuck 60 % on random layouts, median time to goal 16.94 s; reached 0 % on u_trap and narrow_gap (100 % stuck); scipy EDT on 200 x 200 x 50 median 183 ms (M3 Max) | synthetic (2.5D point-mass arena) | 20 layouts per family, seed 0; EDT 7 calls | Baseline only; the arena is 2.5D with a point-mass vehicle and ideal ray casts |

## Cheat-sheet line (docs/cheatsheets/README.md)

| The brief says... | Sheet | Decoder rows |
|---|---|---|
| "point A to B", "obstacles", "close area", "arena", "indoor", "avoid" | none yet: start at [close-area-arena](../../samples/close-area-arena/) and the [close-area-nav synthesis](../../docs/research/close-area-nav/README.md) | 31 |
