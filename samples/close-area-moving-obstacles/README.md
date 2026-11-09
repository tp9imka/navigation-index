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

## Limits

- **No prediction of obstacle motion.** Every arm reacts to where the person is, not where the
  person is going. A constant-velocity predictor is the obvious next arm; it is not built.
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
