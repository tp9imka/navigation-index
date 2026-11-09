# close-area-arena: one small sim to compare every close-area A=>B approach

Goal: a deterministic, numpy + scipy only 2.5D arena where a drone flies from A to B in a
walled 20 x 20 m area with obstacles. Planners, faulty estimators and safety filters from later
samples plug into it and are scored the same way, on truth. Planner code talks only to the
published drone interface (`pose()`, `ranges()`, `send_setpoint()`), so it ports to a real
drone adapter (`templates/drone-adapter`) unchanged.

Interfaces for later jobs: [CONTRACT.md](CONTRACT.md). Hub wiring proposals: [INTEGRATION.md](INTEGRATION.md).

Why not gym-pybullet-drones (the primary light sim in
[lane 02](../../docs/research/close-area-nav/02-sims-platforms-competitions.md)): pybullet has no
macOS arm64 wheel and compiles from source, and the comparison needs exact, cheap, seeded
geometry more than contact physics. This arena follows the pure-Python design of
[lane 01 section 5a](../../docs/research/close-area-nav/01-planning-and-mapping.md) in 2D.

## Run

```sh
cd samples/close-area-arena
uv venv .venv && uv pip install --python .venv -r requirements.txt
.venv/bin/python run.py --planner straight --layouts 20 --seed 0 --plot   # ~1.5 s
.venv/bin/python run.py --planner straight --layouts 20 --seed 0 --family u_trap
.venv/bin/python run.py --planner straight --layouts 20 --seed 0 --family narrow_gap
.venv/bin/python bench_edt.py                                              # ~2 s
.venv/bin/python checks.py                                                 # ~2 s
.venv/bin/python -m unittest test_smoke -v                                 # skips without numpy
```

## What is in it

| File | Does |
|---|---|
| `world.py` | Seeded layouts, families `random` (8-15 boxes and cylinders), `u_trap` (cup with its inside corner on the A-B line, opening towards A, plus 2-5 clutter), `narrow_gap` (wall across the area with one 0.5-0.9 m gap, plus clutter). A within 0.5 m of (1.5, 1.5), B within 0.5 m of (18.5, 18.5) in area coordinates; the local frame has its origin at A. Exact signed distance and ray casts; 0.1 m occupancy grid; resample until 4-connected BFS finds A=>B on the grid inflated by 0.15 m |
| `sensors.py` | `RangeFan`: beams, FoV, max range, Gaussian noise, dropout => `RangeScan`. Default 72 beams, 360 deg, 6 m, 0.02 m, 2 % |
| `vehicle.py` | 50 Hz double integrator, velocity lag tau 0.15 s, a <= 3 m/s^2, v <= 2 m/s, radius 0.15 m, z held at 1.0 m |
| `adapter.py` | `Pose`, `RangeScan`, `Setpoint`, `Adapter` (published interface) and `SimAdapter` with the `pose_source` hook |
| `scorer.py` | reached (0.3 m), collision (clearance < radius), stuck (< 0.2 m in 10 s), timeout (60 s), time to goal, min clearance, path length. Truth only |
| `planners/` | `base.Planner`, `straight` baseline (straight line, slows to a stop for returns within 30 deg of the line, never steers) |
| `run.py` | CLI and `evaluate()` for other samples; writes `results/<planner>_<family>_<seed>.json` and `.md`, `--plot` writes a PNG |
| `checks.py` | BFS gap-width probe and a no-slow-down straight run, so the arena is shown to reject sealed gaps and to register collisions |
| `bench_edt.py` | Times `scipy.ndimage.distance_transform_edt` on 200 x 200 x 50 and 200 x 200 |

`checks.py` writes [results/checks.json](results/checks.json) (synthetic): on a wall with one gap,
the BFS guarantee rejects gaps of 0.3 m (the vehicle diameter) and 0.35 m and accepts 0.4 m and
wider. The same file shows the scorer's collision path firing: the straight planner with its
slow-down disabled collides in 60 % of the 20 random seed-0 layouts (median min clearance
0.147 m, below the 0.15 m radius) and reaches B in the same 40 % as the baseline.

## Results (ran 2026-11-09, Apple M3 Max, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

All inputs are **synthetic**: simulated layouts, vehicle and sensor. Nothing here is a flight or
SITL result.

Straight baseline, `python run.py --planner straight --layouts 20 --seed 0 --plot`, wall 1.5 s
([results/straight_random_0.md](results/straight_random_0.md), `.json`):

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m |
|---|---|---|---|---|---|---|---|---|
| straight | random | 20 | 40.0 | 0.0 | 60.0 | 0.0 | 16.94 | 0.383 |

Same planner on the trap families, 20 layouts each, seed 0, wall 1.5 s and 1.4 s
([u_trap](results/straight_u_trap_0.md), [narrow_gap](results/straight_narrow_gap_0.md)):

| planner | family | layouts | reached % | collision % | stuck % | timeout % | median time to goal s | median min clearance m |
|---|---|---|---|---|---|---|---|---|
| straight | u_trap | 20 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.383 |
| straight | narrow_gap | 20 | 0.0 | 0.0 | 100.0 | 0.0 | - | 0.37 |

Reading: the straight line is clear in 8 of 20 random layouts; in the other 12 the slow-down
stops the vehicle in front of an obstacle (min clearance 0.37-0.41 m in those runs, per-run
table in the `.md`), so the scorer calls it stuck, not a collision. Both trap families are built so the straight line is
always blocked. A second run of the random command gave identical per-run scores (timings
excluded); `test_smoke.py` checks the same on 2 layouts.

Plot of random run 0 (stuck at the big box; orange = stuck point, grey band = 0.15 m
inflation): [results/straight_random_0_run0.png](results/straight_random_0_run0.png). The trap
runs: [u_trap](results/straight_u_trap_0_run0.png), [narrow_gap](results/straight_narrow_gap_0_run0.png).

EDT timing, `python bench_edt.py` ([results/edt_timing.json](results/edt_timing.json)), 5 %
random occupancy, one warm-up, 7 timed calls, script wall 2.2 s:

| grid | cells | median ms | min ms | max ms |
|---|---|---|---|---|
| 200 x 200 x 50 | 2,000,000 | 182.95 | 178.42 | 188.0 |
| 200 x 200 | 40,000 | 1.48 | 1.32 | 2.57 |

So a full 3D ESDF rebuild of a 20 x 20 x 5 m volume at 0.1 m fits a 2-5 Hz replan budget on
this machine; the 2D arena grid costs about 1.5 ms. An earlier run of the same script gave a 187 ms
median for 3D (overwritten; timings move a few percent with load).

## Limits

- 2.5D only: no altitude changes, no overhangs, z is held. Obstacles are axis-aligned boxes
  and vertical cylinders; no thin or transparent obstacles, no dynamic obstacles.
- Point-mass vehicle with a velocity lag, not rigid-body dynamics: no attitude, wind,
  ground effect, motor saturation or contact physics. A collision ends the run.
- The range sensor is an ideal ray cast plus Gaussian noise and random dropout; no beam
  width, no multipath, no glass or dark-surface returns.
- `stuck` is a displacement rule (0.2 m in 10 s). A planner that oscillates with more than
  0.2 m amplitude is never stuck; it times out at 60 s instead.
- The setpoint timeout (0.5 s => zero velocity) is our choice, modelled on PX4 leaving Offboard
  when the stream stops; the exact PX4 value was not checked in this job.
- Timing numbers (EDT, planner ms) depend on the machine and its load.
- The straight baseline is the only planner here; A*, APF and safety filters come in later
  samples.

## Sources

- Hub research docs, read in full: [close-area-nav README](../../docs/research/close-area-nav/README.md),
  [01 planning and mapping](../../docs/research/close-area-nav/01-planning-and-mapping.md)
  (section 5a design, section 7 lists sub-second EDT on 2M cells as unmeasured),
  [02 sims and platforms](../../docs/research/close-area-nav/02-sims-platforms-competitions.md)
  (pybullet arm64 wheel). These are hub docs, not external sources.
- [code] `scipy.ndimage.distance_transform_edt`, SciPy 1.18.1, used as installed; docs not re-read.
- [docs] MAVLink `ODOMETRY.quality` semantics are taken from the published interface in the
  task brief, not re-read.
