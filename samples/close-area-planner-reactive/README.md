# close-area-planner-reactive: APF and VFH+ from range returns only, and where they get stuck

Goal: the fallback planners for when there is no map. They read only the range scan and the
pose, so they fit a Crazyflie with a Multi-ranger deck (4 horizontal beams) or a drone whose
mapping is not ready yet. Both run in the shared [close-area-arena](../close-area-arena/README.md)
and are scored there, on truth, against the straight baseline.

- `apf.py`: artificial potential field (Khatib 1986) on raw returns, a range-only brake, and a
  named escape rule, **wall-follow after 3 s of no progress** (Bug-style leave rule: leave when
  the distance to B is 0.5 m below the hit distance and the goal direction is free).
- `vfh_plus.py`: VFH+ (Ulrich and Borenstein 1998): 72-sector polar histogram with enlargement by
  radius + safety distance, binary histogram with hysteresis, valley selection with the
  goal / heading / previous-direction cost, speed from obstacle density. No escape rule, as
  published.
- `bench.py`: runs both (plus APF with the escape off) on the three arena families with two
  fans, and classifies where failed runs ended.
- `tune.py`: the dev-seed sweep (seed 1) that set the defaults. The report seed 0 was not used
  for tuning.

## Run

```sh
cd samples/close-area-planner-reactive
uv venv .venv && uv pip install --python .venv -r requirements.txt   # numpy + scipy, from the arena
.venv/bin/python bench.py --layouts 50 --seed 0      # ~76 s, writes results/reactive_0.*
.venv/bin/python tune.py                             # ~110 s, writes results/dev_seed1_tuning.md
.venv/bin/python -m unittest test_smoke -v           # skips without numpy
```

From another sample: `import arena, apf` then
`arena.run.evaluate(apf.make, "u_trap", 50, 0, cfg=arena.cfg_for("cf4"))`. `arena.py` loads the
arena folder as package `close_area_arena` (the recipe in its CONTRACT.md); no arena file is
edited.

Fans:

| fan | beams | FoV | range | noise | dropout |
|---|---|---|---|---|---|
| default | 72 | 360 deg | 6 m | 0.02 m | 2 % |
| cf4 | 4 (back, right, front, left; body frame) | 360 deg | 4 m | 0.02 m | 2 % |

cf4 copies the Multi-ranger's horizontal geometry (front/back/left/right, up to about 4 m, per
[lane 02](../../docs/research/close-area-nav/02-sims-platforms-competitions.md) and the
Bitcraze product page). The up sensor is not modelled (the arena is 2.5D). Noise and dropout
are the arena defaults, not VL53L1x figures. Both planners yaw towards their commanded
velocity, so the front beam faces travel.

## Results (ran 2026-11-09, Apple M3 Max, CPython 3.11.15, numpy 2.4.6, scipy 1.17.1)

All inputs are **synthetic**: simulated layouts, vehicle and sensor. Nothing here is a flight or
SITL result.

`python bench.py --layouts 50 --seed 0`, wall 75.8 s
([results/reactive_0.md](results/reactive_0.md), per-run rows in `results/reactive_0.json`,
console in `results/bench_stdout.txt`). 50 layouts per cell, seed 0:

| planner | fan | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m |
|---|---|---|---|---|---|---|---|---|---|
| apf | default | random | 50 | 98.0 | 0.0 | 2.0 | 0.0 | 26.0 | 0.774 |
| apf | default | u_trap | 50 | 92.0 | 0.0 | 6.0 | 2.0 | 43.78 | 0.65 |
| apf | default | narrow_gap | 50 | 0.0 | 0.0 | 94.0 | 6.0 | - | 0.646 |
| apf | cf4 | random | 50 | 82.0 | 8.0 | 10.0 | 0.0 | 26.58 | 0.474 |
| apf | cf4 | u_trap | 50 | 2.0 | 54.0 | 24.0 | 20.0 | 38.96 | 0.15 |
| apf | cf4 | narrow_gap | 50 | 6.0 | 34.0 | 28.0 | 32.0 | 40.56 | 0.301 |
| apf_noescape | default | random | 50 | 86.0 | 0.0 | 14.0 | 0.0 | 25.68 | 0.792 |
| apf_noescape | default | u_trap | 50 | 2.0 | 0.0 | 98.0 | 0.0 | 36.32 | 0.877 |
| apf_noescape | default | narrow_gap | 50 | 0.0 | 0.0 | 88.0 | 12.0 | - | 0.736 |
| apf_noescape | cf4 | random | 50 | 62.0 | 6.0 | 32.0 | 0.0 | 25.96 | 0.56 |
| apf_noescape | cf4 | u_trap | 50 | 0.0 | 2.0 | 98.0 | 0.0 | - | 0.561 |
| apf_noescape | cf4 | narrow_gap | 50 | 0.0 | 6.0 | 90.0 | 4.0 | - | 0.414 |
| vfh_plus | default | random | 50 | 96.0 | 0.0 | 4.0 | 0.0 | 25.68 | 0.278 |
| vfh_plus | default | u_trap | 50 | 0.0 | 0.0 | 94.0 | 6.0 | - | 0.956 |
| vfh_plus | default | narrow_gap | 50 | 62.0 | 0.0 | 38.0 | 0.0 | 27.56 | 0.274 |
| vfh_plus | cf4 | random | 50 | 28.0 | 72.0 | 0.0 | 0.0 | 24.62 | 0.148 |
| vfh_plus | cf4 | u_trap | 50 | 0.0 | 98.0 | 2.0 | 0.0 | - | 0.146 |
| vfh_plus | cf4 | narrow_gap | 50 | 4.0 | 96.0 | 0.0 | 0.0 | 29.13 | 0.148 |

Straight baseline from the arena for comparison (20 layouts, seed 0, so not the same layout
set): reached 40 % random, 0 % u_trap, 0 % narrow_gap, 0 % collision
([straight_random_0.md](../close-area-arena/results/straight_random_0.md)).

Where failed runs ended (end point classified from the layout after the run; the planner never
sees it). Full table with every cell: [results/reactive_0.md](results/reactive_0.md).

| planner | fan | family | where runs ended (count) | escape / stop |
|---|---|---|---|---|
| apf | default | u_trap | reached 46, in_cup 2, outside_cup 2 | escape in 50, reached after escape 46 |
| apf | default | narrow_gap | before_wall 50 | escape in 50, reached after escape 0 |
| apf_noescape | default | u_trap | in_cup 48, outside_cup 1, reached 1 | - |
| vfh_plus | default | u_trap | in_cup 50 | no-valley stop in 0 |
| vfh_plus | default | narrow_gap | reached 31, before_wall 18, at_gap 1 | no-valley stop in 1 |

### Reading

- **72-beam fan, U trap.** Both planners without an escape stop inside the cup: APF without
  escape 48 of 50 in_cup, VFH+ 50 of 50 in_cup. This is the Koren and Borenstein local minimum.
  The wall-follow escape lifts APF from 2 % to 92 % reached on u_trap, at a median 43.78 s to
  goal (random: 26.0 s).
- **72-beam fan, narrow gap.** APF reaches B in 0 of 50 even with the escape: repulsion from both
  gap edges keeps it out and all 50 runs end before_wall. In the dev-seed runs we plotted
  (seed 1, plots not kept), APF slid along the wall past the gap into the area corner, and the
  wall-follow then took the long way round and ran out of the 60 s budget. VFH+ reaches 62 %;
  our reading (not instrumented) is that its enlargement (radius 0.15 + d_s 0.1 m) leaves a
  valley open in the 0.5-0.9 m gaps once it is close. Its median min clearance is 0.274 m,
  against APF's 0.646 m.
- **4-beam fan (cf4).** Collisions dominate: VFH+ 72-98 %, APF 8-54 %. Median min clearance at
  or below the 0.15 m radius means the vehicle touched an obstacle. In the collisions we
  plotted (cf4 u_trap run 0 for both planners, two dev-seed random runs), the vehicle hit a
  corner lying between beams, where a memoryless 4-beam scan has no return; VFH+ weaves into
  the cup's inside corner. Our reading of why APF collides less: its brake caps speed towards
  any beam with a close return, while VFH+ speed comes only from histogram density, which is
  zero in the blind diagonals. This was not isolated by an experiment.
- On random clutter with 72 beams both are far above the straight baseline (98 % APF, 96 %
  VFH+, against 40 % straight on the 20-layout set).

Dev-seed sweep (seed 1, 20 layouts, [results/dev_seed1_tuning.md](results/dev_seed1_tuning.md)):
two APF escape variants (windowed stall trigger, weighted wall direction) lowered cf4 random
reached from 85 % to 65-75 % and were left off. VFH+ d_s 0.1 m / tau_high 24 was the best
default-fan setting; no VFH+ setting tried brought cf4 collisions below 35 %.

### Plots (u_trap, seed 0, run 0; blue = truth path, orange = stuck, magenta = collision)

| planner | default fan | cf4 fan |
|---|---|---|
| apf | [reached](results/apf_default_u_trap_0_run0.png): wall-follow out of the cup, round the lip | [collision](results/apf_cf4_u_trap_0_run0.png) |
| apf_noescape | [stuck in cup](results/apf_noescape_default_u_trap_0_run0.png) | [stuck](results/apf_noescape_cf4_u_trap_0_run0.png) |
| vfh_plus | [stuck in cup](results/vfh_plus_default_u_trap_0_run0.png) | [collision in the inside corner](results/vfh_plus_cf4_u_trap_0_run0.png) |

Determinism: two runs of the bench command gave identical per-run scores in all 18 cells
(planner timings excluded). `test_smoke.py` checks u_trap run 0 outcomes (APF reached, VFH+
stuck) and repeatability.

## Limits

- Everything inherits the arena limits: 2.5D, point-mass vehicle with a velocity lag, ideal ray
  casts with Gaussian noise and dropout, axis-aligned boxes and cylinders, no dynamic obstacles.
- cf4 is a geometry model of the Multi-ranger, not a VL53L1x model: no beam cone (a real ToF
  zone is a cone, not a ray, so it would see some of the "blind" corners; its width was not checked),
  no ranging rate, no surface effects. The 72-98 % VFH+ cf4 collision rate is therefore an upper
  bound for this geometry, not a Crazyflie prediction.
- Both planners are memoryless per scan (APF keeps only escape state, VFH+ only the binary
  histogram and last direction). A short scan memory or a yaw sweep would change the cf4
  numbers; neither was tried.
- VFH+ has no escape rule here and no masked histogram (the vehicle is holonomic). Adding the APF
  wall-follow to VFH+ was not tried.
- Parameters were tuned by hand on seed 1 with small sweeps (20 layouts); other settings may do
  better. The 60 s time budget caps long wall-follow detours.
- APF and VFH+ cells have 50 layouts; the straight baseline has 20, so the comparison is across
  different layout sets of the same families.

## Sources

- [peer] Khatib, Real-time obstacle avoidance for manipulators and mobile robots, IJRR 1986,
  doi 10.1177/027836498600500106 (hub record `res:khatib-potential-fields-ijrr-1986`). Not re-read;
  the method is the textbook form.
- [peer] Koren and Borenstein, Potential field methods and their inherent limitations, ICRA 1991,
  doi 10.1109/ROBOT.1991.131810 (`res:koren-borenstein-apf-limits-icra-1991`). Not re-read.
- [peer] Ulrich and Borenstein, VFH+, ICRA 1998, doi 10.1109/ROBOT.1998.677362
  (`res:ulrich-borenstein-vfhplus-icra-1998`). Not re-read: histogram magnitude a - b d^2,
  enlargement asin(r / d), hysteresis thresholds and the three-term cost follow the hub record
  and common descriptions; threshold values here are our own.
- [peer] Lumelsky and Stepanov, Bug algorithms, 1987: the wall-follow leave rule is Bug-style,
  simplified (distance margin instead of the m-line). Not re-read.
- [docs] Bitcraze Multi-ranger deck (`res:bitcraze-multi-ranger-deck`): five VL53L1x, front,
  back, left, right, up, up to about 4 m, as summarised in the hub record and lane 02.
- Hub docs: [close-area-nav README](../../docs/research/close-area-nav/README.md),
  [01 planning and mapping](../../docs/research/close-area-nav/01-planning-and-mapping.md)
  (APF and VFH+ rows, failure modes table),
  [02 sims and platforms](../../docs/research/close-area-nav/02-sims-platforms-competitions.md).
