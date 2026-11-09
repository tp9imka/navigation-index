# close-area-safety-filter: does a range-only safety filter already make A* safe under estimator faults?

Goal: start the kill test for the hub's headline, the integrity-aware safety filter
([close-area-nav README, "Recommended direction"](../../docs/research/close-area-nav/README.md),
narrowed by [doc 07 section 2](../../docs/research/close-area-nav/07-pl-margin-prior-art.md)).
A safety filter sits between the planner and the vehicle. This sample builds that harness on the
shared [close-area-arena](../close-area-arena/README.md), adds obstacles the range fan cannot
see, and runs the first three arms on the arena A* planner under the arena's estimator faults.

The question for this round: **does a range-only filter (F1, F2) already prevent collisions?**
If PX4-CBF (F2) gets collisions to 1 % or less in every fault case, that is the
[doc 04 section 3.4](../../docs/research/close-area-nav/04-innovation-prior-art.md) fail
condition for the headline ("the honest pitch is: we integrated PX4-CBF").

## Run

```sh
cd samples/close-area-safety-filter
uv venv .venv && uv pip install --python .venv -r requirements.txt     # numpy + scipy
.venv/bin/python run_kill.py --layouts 100 --seed 0 --workers 14        # ~3 min on 14 workers
.venv/bin/python -m unittest test_smoke -v                              # ~6 s, skips without numpy
```

`arena.py` loads the arena folder as package `close_area_arena` (CONTRACT.md "Import" recipe,
copied from close-area-planner-reactive). No arena file is edited.

## What is in it

| File | Does |
|---|---|
| `filters.py` | `SafetyFilter` interface `filter(setpoint, pose, scan, map_obstacles, health, dt) -> (setpoint, intervened)`, the arms F0-F2 and the `REGISTRY` |
| `unsensed.py` | Obstacles in the prior map and in truth collision checks but invisible to the range fan (`VisibleOnlyFan` wraps the arena `RangeFan`), placed on the reference A* path |
| `run_kill.py` | The harness loop and the run matrix; writes `results/kill_a_*` |
| `arena.py` | Arena loader |
| `test_smoke.py` | Harness equals the arena on one layout; unsensed obstacles are in truth, not in scans; every arm runs; one saved result reproduces |

### Harness (run_kill.py)

Per 50 Hz physics step: estimated pose (arena `estimator.py`, called every step so the filter
sees a fresh estimate) => planner step at 10 Hz (`planners/astar_esdf.py`, `known_map=True`, the
layout's prior grid) => filter => vehicle. Two arena range fans (72 beams, 360 deg, 6 m, 0.02 m
noise, 2 % dropout), both wrapped by `VisibleOnlyFan`: the planner's at 10 Hz with the arena's
noise seed, the filter's every 3 steps (16.7 Hz, doc 05 section 1.5: 15 Hz in flight) with its
own seed. Scoring is the arena scorer on truth. Fault cases are the arena's `none` (dark zones
only), `jump`, `bias`, `dropout`, plus `truth` (no estimator) as a reference.

With F0, `truth` and unsensed off the loop reproduces `run.evaluate` for the A* planner exactly
(outcome, min clearance and path length identical on layouts 0-4, checked in `test_smoke.py` on
layout 0).

### Arms (filters.py)

Every parameter is named in the arm's `DEFAULTS`, with its source in a comment.

**F0** no filter.

**F1 CP-stop**, PX4 Collision Prevention style, Position-mode semantics as described in
[doc 01 section 3](../../docs/research/close-area-nav/01-planning-and-mapping.md) and the
[PX4 Collision Prevention page](https://docs.px4.io/main/en/computer_vision/collision_prevention.html):
72 sectors of 5 deg; per sector, the velocity component toward it is capped at the speed that
still stops `CP_DIST` short after `CP_DELAY` at the current estimated speed, with a jerk-limited
brake; the vehicle may slide along walls; guidance may turn the command up to `CP_GUIDE_ANG`;
no scan for 0.5 s => zero velocity. This is our reading of the docs, not PX4 code.

| Parameter | Value | Source |
|---|---|---|
| CP_DIST | 0.5 m | **ours**: the PX4 default is -1 (disabled) per the [PX4 parameter reference](https://docs.px4.io/main/en/advanced_config/parameter_reference.html) |
| CP_DELAY | 0.4 s | PX4 parameter reference default |
| CP_GUIDE_ANG | 30 deg | PX4 parameter reference default |
| CP_GO_NO_DATA | 0 | doc 01 section 3 (no effect with a 360 deg fan) |
| MPC_ACC_HOR, MPC_JERK_MAX | 3.0 m/s^2, 8.0 m/s^3 | PX4 parameter reference defaults |
| no-data timeout | 0.5 s | doc 01 section 3 |
| guidance step, margin | 5 deg, 10 % | ours |

**F2 PX4-CBF as shipped** (NTNU fork branch `cbf` HEAD): the closed-form single-constraint
composite CBF on body-frame range points of
[doc 05 section 1.7](../../docs/research/close-area-nav/05-cbf-baselines-faithful.md), linear
class-K `alpha*h`, raw input, per-axis clamp after the correction, low-passed output, **no FoV
constraint** (doc 05 sections 1.3, 1.6). No position is used; the estimated velocity and yaw are.
The planner's velocity setpoint is wrapped in a P velocity loop as doc 05 section 1.8 asks:
`a_sp = (v_sp - v_est) / tau`, `v_cmd = v_est + tau * a_out`, with tau = 0.15 s, the arena
vehicle's own velocity lag, so F2 with no correction and no low-pass sends what the planner sent.

| Parameter | Value | Source (doc 05) |
|---|---|---|
| eps | 0.7 m | 1.4, Table II and composite_cbf (fork param 0.5) |
| p0 | -2.5 | 1.4, Table II |
| kappa, gamma | 70, 40 | 1.4, Table II |
| alpha (linear) | 2 | 1.3 (linear in the fork), 1.4 Table II |
| output low-pass gain | 0.6 per 100 Hz step => 0.84 per 50 Hz step | 1.4 composite_cbf `lp_gain_out`, 1.5 rate |
| accel clamp | 3 m/s^2 per axis | 1.4 `CBF_CLAMP_XY` |
| obstacle timeout | 1 s | 1.4, 1.6 |
| max range | 5 m | 1.5 (ToF clamped at 5 m) |
| `||Lg h||^2` floor | 1e-5 | 1.6 |

Doc 05 says Table II, not the fork's parameter defaults, is what the authors flew; this arm uses
Table II. F2 runs at 50 Hz (the arena physics rate), not the paper's 100 Hz.

`intervened`: F1 when the output differs from the input by more than 1 mm/s; F2 when the CBF
correction `eta > 0` (the low-pass alone does not count).

### Unsensed obstacles (unsensed.py)

Two per layout, seeded per layout: a thin pole (radius 4-8 cm) or a 4 cm glass panel 0.6-1.2 m
long placed across the path. Each is centred on the reference A* path (planned on the layout
without them) at 20-45 % and 55-80 % of its length, offset up to 0.15 m sideways, at least 1 m
from A and B, and kept only if the arena's free-path check still passes. They are in the new
World's geometry and grid, so the known-map planner plans around them and the scorer counts a
hit, but `VisibleOnlyFan` ray-casts against the layout without them. In this run all 100
layouts got both (200 placed). "Unsensed off" runs the same layouts without them.

## Results (ran 2026-11-09, Apple M3 Max, CPython 3.11.15, numpy 2.4.6, scipy 1.17.1)

All inputs are **synthetic**: simulated layouts, vehicle, range fan and VIO-like estimator with
injected faults. Nothing here is a flight or SITL result.

`python run_kill.py --layouts 100 --seed 0 --workers 14`, 3000 runs, wall 176.4 s
([summary](results/kill_a_summary_0.md); per-run rows in
[kill_a_unsensed_on_0.json](results/kill_a_unsensed_on_0.json) and
[kill_a_unsensed_off_0.json](results/kill_a_unsensed_off_0.json)). Random family, 100 layouts,
seed 0. "Of which unsensed" counts collisions whose contact was with an unsensed obstacle.

**Unsensed obstacles on** ([kill_a_unsensed_on_0.md](results/kill_a_unsensed_on_0.md)):

| arm | case | layouts | collision % | of which unsensed | reached % | stuck % | timeout % | intervention fraction | median min clearance m | median time to goal s | median max pose err m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F0 | truth | 100 | 0.0 | 0 of 0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.61 | 20.52 | 0.0 |
| F0 | none | 100 | 3.0 | 2 of 3 | 72.0 | 25.0 | 0.0 | 0.0 | 0.54 | 20.71 | 0.343 |
| F0 | jump | 100 | 17.0 | 9 of 17 | 34.0 | 49.0 | 0.0 | 0.0 | 0.386 | 20.5 | 0.669 |
| F0 | bias | 100 | 9.0 | 7 of 9 | 28.0 | 63.0 | 0.0 | 0.0 | 0.452 | 20.38 | 0.609 |
| F0 | dropout | 100 | 7.0 | 4 of 7 | 60.0 | 33.0 | 0.0 | 0.0 | 0.518 | 20.93 | 0.464 |
| F1 | truth | 100 | 0.0 | 0 of 0 | 100.0 | 0.0 | 0.0 | 0.258 | 0.627 | 19.85 | 0.0 |
| F1 | none | 100 | 3.0 | 3 of 3 | 76.0 | 21.0 | 0.0 | 0.2407 | 0.596 | 19.97 | 0.341 |
| F1 | jump | 100 | 10.0 | 10 of 10 | 46.0 | 44.0 | 0.0 | 0.2194 | 0.636 | 19.54 | 0.664 |
| F1 | bias | 100 | 7.0 | 7 of 7 | 39.0 | 54.0 | 0.0 | 0.2085 | 0.6 | 19.9 | 0.608 |
| F1 | dropout | 100 | 3.0 | 3 of 3 | 63.0 | 34.0 | 0.0 | 0.2249 | 0.595 | 20.18 | 0.442 |
| F2 | truth | 100 | 0.0 | 0 of 0 | 92.0 | 8.0 | 0.0 | 0.2482 | 0.639 | 20.5 | 0.0 |
| F2 | none | 100 | 3.0 | 3 of 3 | 72.0 | 25.0 | 0.0 | 0.2382 | 0.647 | 20.97 | 0.338 |
| F2 | jump | 100 | 11.0 | 11 of 11 | 33.0 | 56.0 | 0.0 | 0.2378 | 0.586 | 21.4 | 0.676 |
| F2 | bias | 100 | 7.0 | 7 of 7 | 33.0 | 60.0 | 0.0 | 0.2342 | 0.652 | 20.26 | 0.607 |
| F2 | dropout | 100 | 4.0 | 4 of 4 | 59.0 | 37.0 | 0.0 | 0.2385 | 0.64 | 21.12 | 0.433 |

**Unsensed obstacles off** ([kill_a_unsensed_off_0.md](results/kill_a_unsensed_off_0.md)):

| arm | case | layouts | collision % | of which unsensed | reached % | stuck % | timeout % | intervention fraction | median min clearance m | median time to goal s | median max pose err m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F0 | truth | 100 | 0.0 | 0 of 0 | 100.0 | 0.0 | 0.0 | 0.0 | 0.633 | 19.04 | 0.0 |
| F0 | none | 100 | 0.0 | 0 of 0 | 69.0 | 31.0 | 0.0 | 0.0 | 0.589 | 19.3 | 0.402 |
| F0 | jump | 100 | 7.0 | 0 of 7 | 34.0 | 59.0 | 0.0 | 0.0 | 0.531 | 19.31 | 0.648 |
| F0 | bias | 100 | 4.0 | 0 of 4 | 30.0 | 66.0 | 0.0 | 0.0 | 0.553 | 18.74 | 0.65 |
| F0 | dropout | 100 | 1.0 | 0 of 1 | 63.0 | 36.0 | 0.0 | 0.0 | 0.573 | 19.36 | 0.461 |
| F1 | truth | 100 | 0.0 | 0 of 0 | 100.0 | 0.0 | 0.0 | 0.3336 | 1.03 | 18.1 | 0.0 |
| F1 | none | 100 | 0.0 | 0 of 0 | 73.0 | 27.0 | 0.0 | 0.2986 | 1.014 | 18.5 | 0.355 |
| F1 | jump | 100 | 0.0 | 0 of 0 | 59.0 | 41.0 | 0.0 | 0.2746 | 1.014 | 18.08 | 0.532 |
| F1 | bias | 100 | 0.0 | 0 of 0 | 39.0 | 61.0 | 0.0 | 0.2591 | 1.012 | 17.6 | 0.632 |
| F1 | dropout | 100 | 0.0 | 0 of 0 | 66.0 | 34.0 | 0.0 | 0.2884 | 1.017 | 18.78 | 0.436 |
| F2 | truth | 100 | 0.0 | 0 of 0 | 86.0 | 14.0 | 0.0 | 0.3336 | 0.839 | 18.9 | 0.0 |
| F2 | none | 100 | 0.0 | 0 of 0 | 65.0 | 35.0 | 0.0 | 0.287 | 0.847 | 19.5 | 0.381 |
| F2 | jump | 100 | 0.0 | 0 of 0 | 38.0 | 62.0 | 0.0 | 0.2806 | 0.843 | 19.96 | 0.66 |
| F2 | bias | 100 | 0.0 | 0 of 0 | 36.0 | 64.0 | 0.0 | 0.2955 | 0.858 | 18.32 | 0.613 |
| F2 | dropout | 100 | 0.0 | 0 of 0 | 60.0 | 40.0 | 0.0 | 0.2886 | 0.85 | 19.57 | 0.433 |

### Reading

- **Against obstacles the fan sees, a range-only filter already prevents collisions here.**
  With unsensed obstacles off, F1 and F2 have 0 collisions in every case (500 runs each); the
  bare A* planner collides in 7 % (jump), 4 % (bias) and 1 % (dropout). **That is the doc 04
  fail condition for the headline in this setting: F2 alone is at 1 % or less (0 %) in all fault
  cases.** A map-based, PL-sized margin adds nothing against obstacles a 360 deg fan sees.
- **Against obstacles it cannot see, a range-only filter does not help.** With unsensed
  obstacles on, F2 collides in 3 % (none), 11 % (jump), 7 % (bias) and 4 % (dropout), and every
  one of those collisions is with an unsensed obstacle (F1: 3, 10, 7, 3 %, also all unsensed).
  F0's unsensed hits are 2, 9, 7, 4 per 100; the filters remove the sensed hits and leave the
  unsensed ones. So the fail condition does **not** hold once the world has map-only obstacles,
  and that is the only place the headline can still win. The headline's pitch narrows to "a
  margin for what the range sensor cannot see", which matches doc 07's surviving claim.
- **The jump fault is the worst case**: the estimate steps 0.5 m when the vehicle is within
  1 m of an obstacle, the known-map planner then steers relative to the wrong position, and only
  sensed obstacles are caught.
- **F2 with the flight parameters costs reach even without faults**: 92 % (on) and 86 % (off)
  with truth pose, against 100 % for F0 and F1. The stuck runs end with min clearance 0.60-0.95 m
  (per-run rows), consistent with eps = 0.7 m holding the centre 0.7 m from every return, which
  closes passages narrower than about 1.4 m for a 0.15 m radius vehicle.
- **Reach under estimator cases is low for every arm** (28-76 %), mostly "stuck" at the
  estimated goal more than 0.3 m from the real B: median max pose error 0.34-0.68 m. That is the
  arena estimator's drift and faults, not the filters (same pattern in the arena README's
  "Estimator and faults" section). Compare reach between arms within a case, not with truth.
- A rerun of 24 runs (F2 jump, F1 bias, F0 none, layouts 0-7, unsensed on) in one process gave
  identical outcome, min clearance, path length, intervention fraction and unsensed-hit flags.

## Part b: estimation-aware baselines (ran 2026-11-09, synthetic)

Added by loop item 06b: F3 Belief-CBF (map barrier inflated by k * sigma from the EKF covariance,
plus the prediction margin gamma), F3p (F3 with the covariance prediction only), F4 MR-CBF with a
fixed error bound eps_m. F4's default eps_m = 0.99 m is the worst per-run position error seen on
seed 1 ([kill_b_eps_calib_1.md](results/kill_b_eps_calib_1.md)); 0.4, 0.2 and 0.1 m are swept.
`python run_kill.py --layouts 100 --seed 0 --workers 14 --tag kill_b --arms F2,F3,F3p,F4,F4@eps_m=0.4,F4@eps_m=0.2,F4@eps_m=0.1`
(807 s). Unsensed obstacles on, collision % (reached %):

| arm | none | jump | bias | dropout |
|---|---|---|---|---|
| F2 PX4-CBF | 3 (72) | 11 (33) | 7 (33) | 4 (59) |
| F3 Belief-CBF | 0 (62) | 9 (31) | 3 (31) | 1 (56) |
| F4 MR-CBF eps 0.99 m | 15 (0) | 13 (0) | 18 (0) | 15 (0) |
| F4 MR-CBF eps 0.2 m | 0 (60) | 0 (29) | 0 (29) | 1 (53) |
| F4 MR-CBF eps 0.1 m | 0 (65) | 11 (29) | 5 (33) | 4 (56) |

Full tables and barrier diagnostics: [kill_b_summary_0.md](results/kill_b_summary_0.md).

- **The bar for "ours" is now MR-CBF with a fixed 0.2 m bound:** 0-1 % collisions in every fault
  case with unsensed obstacles, at the same reach as F2/F3. Doc 04's fail line ("a baseline within
  1 pp") is close to met by this arm. Ours has to show either fewer collisions at equal reach or
  more reach at equal safety, and a reason a fixed bound cannot be chosen in advance.
- F4 with the calibrated worst-case bound (0.99 m) freezes: 0 % reach, 82-85 % stuck; its
  collisions are QP-infeasible slack, not unsensed hits.
- F3 Belief-CBF removes most fault collisions except jumps (9 %): a jump is not in the covariance.
- The 0.2 m value was swept on seed 0 itself, so it is tuned on the test seed. Item 37 reruns on
  held-out seeds. The job hit its time limit before writing this section; the loop driver wrote it
  from the result files.

## Integrity monitor (ran 2026-11-09, synthetic)

[integrity/](integrity/) adds a second position source (UWB anchors, NLOS bias fault) and a
solution-separation monitor that outputs a protection level (PL, integrity risk 1e-3 per epoch),
a detection flag and an "ambiguous" state. `python run_monitor.py --layouts 100 --seed 0` (55 s).
Table: [integrity/results/monitor_0.md](integrity/results/monitor_0.md).

- **The PL held in every case:** breach fraction (true error above PL) 0 to 1.3e-4 for the
  solution-separation variants, under VIO jump, bias, dropout, UWB NLOS and both at once.
- **Median PL 0.41-0.59 m** (single-exclusion variant), at or below 1.0 m in 82-100 % of epochs.
  That is the number a margin can use; the tuned fixed bound in part b was 0.2 m.
- **Max-separation exclusion picks the wrong source** (9 runs NLOS, 19 runs both faults), as the
  hub's multi-source-fde saw. The headline's "hover when ambiguous" rule exists for this case.
- The job hit its time limit before writing a README; the loop driver wrote this from the result
  files. Not yet used by any filter arm: that is item 34.

## Add an arm

1. In `filters.py`, subclass `SafetyFilter` with `NAME` (for example `"F3"`) and `DEFAULTS`
   (every parameter named, source in a comment); implement `reset()` and
   `filter(setpoint, pose, scan, map_obstacles, health, dt) -> (setpoint, intervened)`.
2. Add the class to `REGISTRY` and a line to `LABELS`.
3. Run `.venv/bin/python run_kill.py --layouts 100 --seed 0 --arms F0,F2,F3 --tag kill_b`.

Map-based arms read `map_obstacles` (the arena World: boxes, cylinders, grid, `sdf()`) at the
estimated position only, and `health` (`quality`, `reset_counter`, `sigma_xy`) from the
estimator. Planned next arms: F3 Belief-CBF, F4 MR-CBF with a fixed bound, F5 FT-CBF residual
dropping, F6 Tan union of plausible states, then ours. Belief-CBF needs the EKF covariance,
which the arena estimator does not expose through `Pose` (only `sigma_xy`); see "Driver edits"
in INTEGRATION.md.

## Limits

- 2.5D point mass with a velocity lag; the CBF acceleration is mapped back to a velocity command
  through that lag, so actuator dynamics the paper tuned against (100-200 ms rise time) are only
  approximated. F2 runs at 50 Hz, not 100 Hz.
- F2 is the shipped variant without the FoV constraint. The arena fan is 360 deg, so the FoV
  constraint the paper adds for a 90 deg fan would not bind here; a narrow-fan run is not done.
- F1 is written from the PX4 docs, not from `CollisionPrevention.cpp`; CP_DIST = 0.5 m is our
  choice. `max_speed_from_distance` uses the PX4 TrajMath closed form from memory, not re-read.
- One planner (A* known map), one family (random), one seed, 100 layouts; doc 04 asks for 200
  layouts and three planners (straight, A*, noisy learned). Unsensed obstacles are 2 per layout,
  always on the reference path, so their collision rate is set by that placement.
- Yaw is truth in the arena estimator, so body-frame points are never rotated wrongly.
- The estimator's dark zones, IMU noise and fault sizes are not calibrated (arena README).

## Sources

- Hub research docs, read for this job: [close-area-nav README](../../docs/research/close-area-nav/README.md),
  [doc 01 section 3](../../docs/research/close-area-nav/01-planning-and-mapping.md),
  [doc 04 section 3](../../docs/research/close-area-nav/04-innovation-prior-art.md),
  [doc 05 sections 0-1 and 5](../../docs/research/close-area-nav/05-cbf-baselines-faithful.md),
  [doc 07 sections 1-2](../../docs/research/close-area-nav/07-pl-margin-prior-art.md).
- [docs] [PX4 Collision Prevention](https://docs.px4.io/main/en/computer_vision/collision_prevention.html)
  and the [PX4 parameter reference](https://docs.px4.io/main/en/advanced_config/parameter_reference.html)
  (CP_*, MPC_ACC_HOR, MPC_JERK_MAX defaults), fetched 2026-11-09.
- [peer-reviewed + code] PX4-CBF: Misyats et al., ICUAS 2025, [arXiv 2504.15850](https://arxiv.org/abs/2504.15850);
  [ntnu-arl/PX4-Autopilot branch cbf](https://github.com/ntnu-arl/PX4-Autopilot/tree/cbf). Equations and
  parameters taken from doc 05, not re-read in this job.
