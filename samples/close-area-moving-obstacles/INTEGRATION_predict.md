# Prediction arms for close-area-moving-obstacles (2026-11-10): proposed wiring, text only

A maintainer applies these. The change that built the prediction arms added only `predict.py`, `planners_st.py`, `vo.py`,
`run_predict.py`, `results/predict_*` and this file; no existing file was edited. Links are
relative to this folder (samples/close-area-moving-obstacles/).

All numbers below are **synthetic** (arena `random` layouts, simulated people, simulated range
fan, truth pose) and come from [results/predict_0_1.md](results/predict_0_1.md) (tables) or
[results/predict_0_1.json](results/predict_0_1.json) (per-run rows), unless a different file is
named.

## 1. README section (append to ./README.md, after "Results")

### Prediction arms: constant-velocity tracks, space-time A*, VO gate (ran 2026-11-10)

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

## 2. Replay JSON

One file, proposed path in the site:
`site/data/showcase/replays/moving_predict_astar_vo_s1_v1_i2.json`, copied from
[results/predict_replay_astar_vo_s1_v1_i2.json](results/predict_replay_astar_vo_s1_v1_i2.json)
(28 KB; seed 1, 1.0 m/s people, layout 2; `astar` collides on this layout, `astar_vo` reaches B).
Add to `site/data/showcase/replays/index.json`:

```json
{"file": "moving_predict_astar_vo_s1_v1_i2.json", "name": "moving_predict_astar_vo_s1_v1_i2",
 "title": "Walking people at 1 m/s: A* + velocity-obstacle gate", "outcome": "reached", "bytes": 28426}
```

The file keeps the arena replay fields (`area`, `a`, `b`, `boxes`, `cylinders`, `t`, `truth`,
`score`, 10 Hz) and adds `people` (true person centres per step), `person_radius` and `pred` (the
confirmed tracks the planner used: t, id, x, y, vx, vy). The showcase page was not checked: it
draws the static scene and the path, and does not know the new fields yet, so the people will not
show until the page draws `people`. The paired `astar` (collision) and `st_astar` (reached) replays
of the same layout are next to it in `results/`.

## 3. Hub text (driver)

Decoder row 31 (docs/problem-statement-decoder.md), add to "Start from":
[close-area-moving-obstacles](./README.md) `run_predict.py` (constant-velocity people tracker,
space-time A* and a velocity-obstacle gate on A*).

Add to "Main risk": with a constant-velocity tracker, a VO gate on A* reached B in 100 of 100
held-out runs with 0 collisions (A* + F2: 92 reached, 0 collisions, 8 stuck); space-time A*
reached 97 but collided in 3. Synthetic, people walk straight lines, which favours the
predictor.

Evidence matrix (docs/evidence-matrix.md) section 14, new row:

| Sample | Method | Measured | Input | Runs | Caveat |
|---|---|---|---|---|---|
| [close-area-moving-obstacles](./INTEGRATION_predict.md) prediction arms | alpha-beta tracks of unmapped range clusters, constant velocity 3 s; space-time A* (0.2 s x 8 s, 5 Hz) over predicted footprints; VO gate on A* carrot command | Held-out seed 1, 100 runs per arm: A* + VO reached 100 % (96.3-100.0), collision 0 % (0.0-3.7); space-time A* 97 % / 3 %; A* + F2 92 % / 0 % (stuck 8 %); A* alone 72 % / 28 %. Sign test VO vs F2 p = 0.0078 (gain from F2's 4 deadlock layouts) | synthetic (2.5D arena, truth pose) | 50 random layouts x 2 speeds x 5 arms x seeds 0 (tuning) and 1 (held out) | People walk straight lines at constant speed (favours constant velocity); margins tuned on seed 0; one family; ideal 360 deg fan |

sample.json `key_result` (append): "; with a constant-velocity tracker (held-out seed 1), a VO gate
on A* reaches 100 % with 0 collisions and space-time A* 97 % with 3 % collisions
(INTEGRATION_predict.md)".

Further reading on the methods (not used for any number above): velocity obstacles, Fiorini and
Shiller 1998; space-time / safe-interval planning, Phillips and Likhachev 2011 (SIPP).
