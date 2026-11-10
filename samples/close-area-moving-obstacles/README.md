# close-area-moving-obstacles: walking people in the arena, A* replan vs A* + PX4-CBF filter vs APF

Goal: give the Day-1 intake question "static or moving obstacles?"
([Q7](../../docs/day1-close-area-intake.md#35-q7-obstacles)) a measured answer. One to three
person-sized cylinders walk seeded segments across the A-B corridor at 0.5 or 1.0 m/s. Three
approaches already in the hub fly through them in the shared
[close-area-arena](../close-area-arena/README.md), scored on truth:

- **astar**: the arena's A* + ESDF planner (`planners/astar_esdf.py`, unchanged search, cost and
  follower) on a grid rebuilt at every replan from the prior static map plus the hits of the
  latest range scan. Replans every 0.4 s (2.5 Hz), plus early when a new hit touches the path,
  capped at 5 Hz. `astar_5hz` is the same with a 0.2 s period (rate sensitivity).
- **astar_f2**: the astar planner, then F2 from
  [close-area-safety-filter](../close-area-safety-filter/README.md) (PX4-CBF as shipped:
  composite CBF on body-frame range points, 50 Hz, own fan at 16.7 Hz, the same wiring as its
  `run_kill.py`).
- **apf**: [close-area-planner-reactive](../close-area-planner-reactive/README.md) `apf.py` with
  its defaults (range only, wall-follow escape, 1.0 m/s cruise).

Speed 0.0 is a control: the same movers frozen at their start points, so they are unmapped
static obstacles.

## Files

| File | What |
|---|---|
| `moving.py` | `draw_movers` (seeded segments) and `MovingWorld` (wraps the arena World; `set_time(t)` moves the cylinders, then `sdf`, `clearance` and `raycast` see them; `.grid` stays the static prior) |
| `astar_replan.py` | `AStarReplan`: subclass of the arena's `AStarESDF`, map = prior OR latest scan hits, 2.5-5 Hz replans |
| `run_moving.py` | Harness: layouts x speeds x arms, process pool, writes `results/moving_<seed>.*` |
| `analyze.py` | Post-hoc facts from `results/moving_0.json` => `results/analysis_0.md` |
| `arena.py` | Loads the arena as package `close_area_arena` (CONTRACT.md recipe), plus `filters.py` and `apf.py` from the sibling samples by path |
| `test_smoke.py` | Mover geometry, every arm runs, one saved collision run reproduces |

Mover model (`moving.py`): radius 0.25 m. Count 1-3 per layout. Segment centre near the A-B line
at 30-70 % of the way (lateral offset up to 1 m), direction within 45 deg of perpendicular to
A-B, half-length 1.5-3.0 m. Constant-speed ping-pong with an instant turn at each end. The
segment keeps 0.2 m from static surfaces, 1.5 m from A and 1.0 m from B (beyond the 0.25 m
radius). Segments come from rng `[seed, index, 4301]` and do not depend on speed, so the three
speeds of a layout share the same movers. The static layout is arena family `random`.

Truth collision = vehicle clearance < 0.15 m to static surfaces or to any mover at its current
position. A person walking into a hovering drone counts as a collision: the people do not
avoid the drone.

## Run

```sh
cd samples/close-area-moving-obstacles
uv venv --python 3.12 .venv && uv pip install --python .venv -r requirements.txt   # numpy + scipy
.venv/bin/python run_moving.py --layouts 50 --seed 0 --workers 14   # ~21 s, writes results/moving_0.*
.venv/bin/python analyze.py                                         # < 1 s, writes results/analysis_0.md
.venv/bin/python -m unittest test_smoke -v                          # ~3 s; skips without numpy
```

The arena, safety-filter and reactive folders must sit next to this one (`../close-area-arena`
and so on). No sibling file is edited.

## Results (ran 2026-11-09, Apple M3 Max, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

All inputs are **synthetic**: simulated layouts, people, vehicle and range fan, truth pose. No
SITL, no flight.

`python run_moving.py --layouts 50 --seed 0 --workers 14`, wall 21.4 s for 600 runs on 14
workers ([results/moving_0.md](results/moving_0.md), per-run rows in `results/moving_0.json`,
console in `results/run_stdout.txt`). 99 movers in 50 layouts (16 layouts with 1, 19 with 2, 15
with 3); none dropped.

| arm | mover speed m/s | layouts | reached % | collision % | stuck % | timeout % | collisions with mover / static | of which vehicle < 0.2 m/s | median min clearance m | median min mover clearance m | median time to goal s | median replan Hz |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar | 0.0 | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0 / 0 | 0 | 0.639 | 0.67 | 20.12 | 2.52 |
| astar | 0.5 | 50 | 86.0 | 14.0 | 0.0 | 0.0 | 7 / 0 | 0 | 0.619 | 0.713 | 20.02 | 2.53 |
| astar | 1.0 | 50 | 64.0 | 36.0 | 0.0 | 0.0 | 18 / 0 | 1 | 0.551 | 0.551 | 20.07 | 2.54 |
| astar_5hz | 0.0 | 50 | 100.0 | 0.0 | 0.0 | 0.0 | 0 / 0 | 0 | 0.636 | 0.675 | 20.16 | 5.03 |
| astar_5hz | 0.5 | 50 | 88.0 | 12.0 | 0.0 | 0.0 | 6 / 0 | 0 | 0.605 | 0.774 | 20.43 | 5.03 |
| astar_5hz | 1.0 | 50 | 64.0 | 36.0 | 0.0 | 0.0 | 18 / 0 | 0 | 0.575 | 0.575 | 20.26 | 5.02 |
| astar_f2 | 0.0 | 50 | 80.0 | 0.0 | 20.0 | 0.0 | 0 / 0 | 0 | 0.855 | 0.913 | 19.78 | 2.52 |
| astar_f2 | 0.5 | 50 | 84.0 | 0.0 | 16.0 | 0.0 | 0 / 0 | 0 | 0.832 | 0.92 | 19.95 | 2.52 |
| astar_f2 | 1.0 | 50 | 84.0 | 0.0 | 16.0 | 0.0 | 0 / 0 | 0 | 0.629 | 0.629 | 20.62 | 2.54 |
| apf | 0.0 | 50 | 96.0 | 0.0 | 4.0 | 0.0 | 0 / 0 | 0 | 0.687 | 0.748 | 27.99 | - |
| apf | 0.5 | 50 | 98.0 | 0.0 | 2.0 | 0.0 | 0 / 0 | 0 | 0.674 | 0.708 | 27.74 | - |
| apf | 1.0 | 50 | 94.0 | 2.0 | 4.0 | 0.0 | 1 / 0 | 0 | 0.577 | 0.587 | 28.82 | - |

Time to collision for the collided runs. `t_collision` is the time from take-off to contact.
Warning = contact time minus the first planner step at which the hit mover was visible to the fan
(exact geometry, before noise and dropout).

| arm | mover speed m/s | collisions | t_collision min | p25 | median | p75 | max | warning n | warning min | warning median | warning max | median vehicle closing speed m/s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astar | 0.5 | 7 | 6.48 | 9.56 | 11.38 | 12.12 | 13.38 | 7 | 4.08 | 5.58 | 8.74 | -0.05 |
| astar | 1.0 | 18 | 4.94 | 6.75 | 9.49 | 11.29 | 14.26 | 18 | 2.94 | 4.41 | 6.74 | -0.02 |
| astar_5hz | 0.5 | 6 | 6.76 | 9.73 | 12.35 | 13.08 | 15.3 | 6 | 4.22 | 5.79 | 7.6 | -0.02 |
| astar_5hz | 1.0 | 18 | 4.92 | 6.28 | 7.88 | 12.49 | 13.96 | 18 | 2.72 | 4.53 | 6.46 | 0.0 |
| apf | 1.0 | 1 | 9.7 | 9.7 | 9.7 | 9.7 | 9.7 | 1 | 7.6 | 7.6 | 7.6 | 0.07 |

Rows with 0 collisions are omitted here; they are in [results/moving_0.md](results/moving_0.md)
with every collided run listed.

What the numbers say:

- **A* replanning alone fails against walking people.** It collides in 14 % of runs at 0.5 m/s
  and 36 % at 1.0 m/s, against 0 % with the same people frozen. Every collision is with a
  mover. Replanning at 5 Hz instead of 2.5 Hz gives 12 % and 36 %: rate is not the fix.
- **The person walks into the drone.** At contact the A* vehicle moves at a median 0.30 m/s
  (0.5 m/s people) and 0.39 m/s (1.0 m/s people), close to the planner's 0.3 m/s clearance
  floor (`V_MIN_FRAC` x `V_CRUISE` in `astar_esdf.py`). Its velocity component towards the
  person is under 0.1 m/s in 7 of 7 and 14 of 18 astar collisions
  ([results/analysis_0.md](results/analysis_0.md)). The planner keeps 0.25 m of inflation around
  where the person is now. A person at 1.0 m/s covers 0.4 m in one 0.4 s replan period.
  Warning time was 2.7-8.7 s across both A* arms, so the person was seen early; without motion prediction the planner
  still routes past the person's current position.
- **F2 on top removes every collision: 0 % at both speeds**, with median min mover clearance
  0.92 m (0.5 m/s) and 0.63 m (1.0 m/s). The price is 16 % stuck. The 8 stuck layouts at 0.5 and
  1.0 m/s are all layouts where F2 already gets stuck with no movers (9 of layouts 0-49 in the
  safety-filter kill test, truth pose, [analysis_0.md](results/analysis_0.md)). So the movers
  add no new stuck runs; F2's static deadlock with A* does. The frozen control adds one
  (layout 17).
- **APF is the safest planner here without a filter:** reached 98 % / 94 %, collision 0 % / 2 %
  (1 run at 1.0 m/s). It also cruises slower (1.0 vs 1.5 m/s; median 28 s vs 20 s to B), which
  gives a walking person more room. This test does not separate the speed effect from the
  method.
- For scale, the straight planner reaches 40 % on 20 random layouts with no movers
  ([straight_random_0.md](../close-area-arena/results/straight_random_0.md), synthetic).

Reproducibility: a single-process rerun of 27 of the 600 runs (every 23rd) gave identical
outcome, min clearance, path length, collision time and warning time
([results/rerun_check.txt](results/rerun_check.txt)). `test_smoke.py` reruns
astar / 1.0 m/s / layout 1 against the saved row.

## Prediction arms: constant-velocity tracks, space-time A*, VO gate (ran 2026-11-10)

The sim people walk straight segments at constant speed with an instant U-turn at each end.
That is the constant-velocity model, so this setup favours a constant-velocity predictor. Real
people stop, wander and react to the drone; expect worse numbers on a real floor.

| File | What |
|---|---|
| `predict.py` | Range hits the prior map does not explain (prior ESDF > 0.15 m) => single-linkage clusters (0.4 m) => centre (centroid pushed 0.7 x 0.25 m away from the sensor) => alpha-beta tracks (0.5 / 0.1, confirmed after 3 hits, dropped after 0.6 s) => constant-velocity extrapolation to 3 s, footprint radius 0.25 m + 0.1 m/s x tau. Turn-around hedge: the disc a person can reach from where it is now at its peak-held speed |
| `planners_st.py` | Arm `st_astar`: space-time A* on the 0.1 m prior grid, 0.2 s layers, 8 s horizon, 5 Hz replan; each layer blocks the predicted swept footprint (capsule over the step) plus 0.25 m inflation and 0.3 m margin, and for tau <= 0.5 s the turn-around disc; static clearance cost and geodesic heuristic from the arena A*; time-indexed follower |
| `vo.py` | Arm `astar_vo`: the existing `astar_replan` planner unchanged, its carrot command gated by a truncated velocity obstacle (3 s, 0.3 m margin) per track plus a 1 s turn-around cone; numpy over 162 candidate velocities x tracks |
| `run_predict.py` | 50 layouts x 0.5 / 1.0 m/s x seeds 0 and 1 x five arms through `run_moving.run_one` unchanged; Wilson 95 % intervals; paired sign test against `astar_f2`; predictor error against truth; replay JSON |

Run (about 45 s for 1000 runs on 14 workers, Apple M3 Max):

```sh
cd samples/close-area-moving-obstacles
.venv/bin/python run_predict.py --layouts 50 --seeds 0,1 --workers 14
```

Seed 0 tuned the margins and the hedge (10 `st_astar` and 8 `astar_vo` configurations,
[results/predict_tuning.md](results/predict_tuning.md)). Seed 1 is held out. The three existing
arms on seed 0 match `results/moving_0.json` in all 300 runs (outcome, min clearance, duration,
warning time).

Held-out seed 1, both speeds pooled, 100 runs per arm (95 % Wilson interval):

| arm | reached % | collision % | stuck % | median time to B s |
|---|---|---|---|---|
| astar | 72.0 (62.5-79.9) | 28.0 (20.1-37.5) | 0.0 (0.0-3.7) | 20.22 |
| astar_f2 | 92.0 (85.0-95.9) | 0.0 (0.0-3.7) | 8.0 (4.1-15.0) | 20.61 |
| apf | 92.0 (85.0-95.9) | 2.0 (0.6-7.0) | 6.0 (2.8-12.5) | 28.25 |
| st_astar | 97.0 (91.5-99.0) | 3.0 (1.0-8.5) | 0.0 (0.0-3.7) | 18.72 |
| astar_vo | 100.0 (96.3-100.0) | 0.0 (0.0-3.7) | 0.0 (0.0-3.7) | 20.62 |

Per speed, per seed, warning times and every collided run are in
[results/predict_0_1.md](results/predict_0_1.md).

Verdict against "gain over A* + F2" (rule fixed before seed 1 ran: no more collisions than
`astar_f2`, more runs reach B, exact sign test on discordant layouts p < 0.05; seed 1, 100 paired
runs):

- **`astar_vo`: PASS.** 0 vs 0 collisions; reached in 8 runs where `astar_f2` did not, 0 the other
  way, p = 0.0078. The 8 runs are the 4 layouts (1, 28, 34, 43) where `astar_f2` gets stuck at
  both speeds (per-run rows). So the gain is reaching B where F2 deadlocks, at the same zero
  collision count; it does not show that VO handles people better than F2. Zero collisions in
  100 runs still allows a true rate up to 3.7 %.
- **`st_astar`: FAIL.** 3 collisions (1 at 0.5 m/s, 2 at 1.0 m/s) vs 0; reached 8 vs 3
  discordant, p = 0.227. It is the fastest arm (median 18.6-18.9 s to B per speed vs 20.1-20.7 s
  for `astar_f2`) and never stuck, but it plans close passes in front of people and a U-turn
  inside the 0.2 s replan cycle catches it. Vehicle speed at contact was 0.21-0.64 m/s
  (collided-run table).
- Against plain `astar` both arms remove most contacts: at 1.0 m/s on seed 1, 38 % => 4 %
  (`st_astar`) and 0 % (`astar_vo`).

How good is the constant-velocity guess here (confirmed tracks vs truth, seed 1, 1.0 m/s)? Position
error now: median 0.06 m. 1 s ahead: median 0.38 m, p90 1.56 m. 3 s ahead: median 2.53 m, p90
5.24 m (0.73 m median at 0.5 m/s). Segments are 3-6 m long, so a 1.0 m/s person often turns
within 3 s; the 3 s prediction is often wrong even for straight-line walkers. The turn-around
hedge was needed because of this (seed-0 traces in
[results/predict_tuning.md](results/predict_tuning.md)).

Planning cost (Python, one core): `st_astar` median 9.9-10.4 ms per search (median of run medians), max 127 ms;
`astar_vo` 3.3-4.0 ms median for the inner A* search (the gate is not timed). Timings move between reruns; outcomes do not (an earlier identical run gave the same outcomes with a 150 ms st_astar max).

Limits:

- People walk straight lines at constant speed and ignore the drone; that favours constant
  velocity. No stopping, wandering, groups or yielding.
- Margins and the hedge are tuned on seed 0 only; seed 1 is one held-out draw of 50 layouts.
- One static family (`random`), truth pose, ideal 360 deg fan. Under a narrow FoV the tracker
  sees people later and loses them at the sides.
- `astar_vo` was not combined with F2. Its zero collisions rest on the VO gate alone.
- The tracker uses a person-size prior (0.25 m) and a 2.5 m/s speed cap; other drones or
  vehicles would need other priors.

## Limits

- **No prediction of obstacle motion.** Every arm reacts to where the person is, not where the
  person is going. A constant-velocity predictor is built: see [Prediction arms](#prediction-arms-constant-velocity-tracks-space-time-a-vo-gate-ran-2026-11-10).
- **Constant-velocity segments.** People walk straight lines at a fixed speed with an instant
  U-turn. They do not stop, accelerate, wander, react to the drone or avoid each other (movers
  may overlap). Real people are less predictable on a straight line and more cautious near a
  drone.
- 2.5D: people are infinite-height cylinders of radius 0.25 m. The 72-beam, 360 deg, 6 m fan
  sees them with ideal geometry, 0.02 m noise and 2 % dropout. A narrow-FoV depth camera would see
  them later or not at all from the side.
- Truth pose only. No estimator faults combined with movers.
- One static family (`random`), one seed, 50 layouts. `u_trap` and `narrow_gap` with movers are
  not run.
- A* planner constants and F2 parameters are the sibling samples' defaults, not tuned for
  movers. The 0.3 m/s speed floor and the 0.25 m inflation drive the A* result. A larger
  inflation for unmapped hits was not tried.
- APF and A* cruise at different speeds (1.0 vs 1.5 m/s), so the comparison is per shipped
  default, not at equal speed.
- Warning time uses exact visibility at 10 Hz planner steps, before noise and dropout.

## Sources

- Arena, scorer and A* + ESDF planner: [close-area-arena](../close-area-arena/README.md),
  [CONTRACT.md](../close-area-arena/CONTRACT.md).
- F2 (PX4-CBF as shipped) and its harness wiring:
  [close-area-safety-filter](../close-area-safety-filter/README.md); the parameters and their sources are in its `filters.py`.
- APF: [close-area-planner-reactive](../close-area-planner-reactive/README.md) (Khatib 1986,
  wall-follow escape).
- "Replan fast, decay occupancy" for dynamic obstacles:
  [01-planning-and-mapping.md section 6](../../docs/research/close-area-nav/01-planning-and-mapping.md#6-failure-modes-and-what-to-do-about-each).
