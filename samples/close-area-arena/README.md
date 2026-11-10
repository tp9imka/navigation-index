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
.venv/bin/python -m planners.astar_esdf --layouts 50 --seed 0              # ~7 min, A* vs straight
.venv/bin/python run_faults.py --planner freest_beam --layouts 50 --seed 0 # ~50 s, estimator faults
.venv/bin/python bench_edt.py                                              # ~2 s
.venv/bin/python checks.py                                                 # ~2 s
.venv/bin/python -m unittest test_smoke -v                                 # skips without numpy
```

### Which planner to start from

For every planner on every arena and sensor see [close-area-benchmark](../close-area-benchmark/README.md); the table below is the arena's own first pick.

Do not start from `straight`. It is the floor. All numbers below are synthetic, seed 0, 50 layouts.

| Planner | Where | Use it when | Reached on random (truth pose) |
|---|---|---|---|
| `astar_esdf` | [planners/astar_esdf.py](planners/astar_esdf.py) | You have a map, or can build one from range returns (`known_map=False`). The safety filters sit on it | 100 % known map, 100 % unknown map ([results](results/astar_esdf_random_0.md)) |
| `freest_beam` | `FreestBeam` in [run_faults.py](run_faults.py), same code as the [CONTRACT.md](CONTRACT.md#add-a-planner) example | Ranges only, no map, few lines to port (for example a Crazyflie multiranger) | 86 % ([results](results/faults_freest_beam_summary_0.md)) |
| `straight` | [planners/straight.py](planners/straight.py) | Floor for comparisons only | 26 % ([results](results/astar_esdf_random_0.md)) |

`freest_beam` is reactive: it was not scored on `u_trap` or `narrow_gap`. Use `astar_esdf` for
those (100 % known map on both, 80 % unknown map on narrow_gap; table below). `freest_beam` runs
only through `run_faults.py` (`--cases truth` for the truth-pose row). `run.py --planner` loads
`planners/<name>.py`, so `run.py --planner freest_beam` does not work. Reactive APF and VFH+
are in [close-area-planner-reactive](../close-area-planner-reactive/README.md).

### Readiness (measured 2026-11-09, Apple M3 Max, macOS 26.6.2 arm64)

CPU only, no GPU, no hardware, no dataset download. Cold setup with
`uv venv --python 3.12 .venv && uv pip install --no-cache --python .venv -r requirements.txt`
took 16.5 s wall. The wheels came from PyPI and CPython 3.12.10 was already installed. Then
the first command ran with all network access denied (`sandbox-exec`, `deny network*`). Its
per-run scores matched [results/straight_random_0.json](results/straight_random_0.json),
timings excluded. Not tested: Linux, Windows, a second laptop, offline runs of the other
commands.

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

## A* + ESDF grid planner (ran 2026-11-09, synthetic)

`planners/astar_esdf.py`: A* on a grid inflated by radius + 0.10 m margin, ESDF clearance cost,
shortcutting, carrot following with clearance-scaled speed, replan at 2-5 Hz. `known_map` plans
on the true grid; `unknown_map` builds the grid from range returns only and treats unknown cells
as passable with a penalty. This is the planner the safety filters sit on.

`.venv/bin/python -m planners.astar_esdf --layouts 50 --seed 0` (about 7 min):

| family | straight reached | known map reached | unknown map reached | unknown failures | plan ms median / p95 (known; unknown) |
|---|---|---|---|---|---|
| random | 26 % | 100 % | 100 % | none | 1.22 / 10.62; 21.01 / 57.53 |
| u_trap | 0 % | 100 % | 100 % | none | 1.47 / 15.08; 32.94 / 60.2 |
| narrow_gap | 0 % | 100 % | 80 % | 14 % stuck, 6 % timeout, 0 % collision | 3.85 / 39.08; 37.18 / 64.54 |

Source: [random](results/astar_esdf_random_0.md), [u_trap](results/astar_esdf_u_trap_0.md),
[narrow_gap](results/astar_esdf_narrow_gap_0.md). Tuned on seed-0 layouts 0-9, so seed 0 is not
held out. A held-out spot check by the loop driver (seed 3, 10 u_trap layouts) gave the same:
straight 0 %, known 100 %, unknown 100 %.

- Unknown-map "stuck" runs on narrow_gap are loops, not stops: the planner follows an unseen
  wall, sees more wall and turns back (2.6-11.7 m flown in the last 10 s). The scorer's 10 s
  displacement rule calls that stuck.
- For gaps under about 0.6 m the planner retries with radius-only inflation (272 known, 128
  unknown replans on narrow_gap). Paths planned at that 0.15 m fallback can pass closer than
  the vehicle radius on the exact geometry because of the 0.1 m grid (17 of 60 A* fallback plans,
  min 0.119 m; no flight collided):
  [sampling sweep clearance check](../close-area-planner-sampling/results/sweep_0_clearance.md).
- A* under the estimator faults, with and without safety filters: see
  [close-area-safety-filter](../close-area-safety-filter/README.md).

Followers: a linear corridor MPC (OSQP, 0.22 ms median solve) matches the carrot follower here
([close-area-planner-mpc](../close-area-planner-mpc/README.md)); sampling planners vs A*:
[close-area-planner-sampling](../close-area-planner-sampling/README.md).

## Sensor realism: Crazyflie presets and glass (ran 2026-11-09, synthetic)

`presets.py` (ideal, crazyflie 4 x 27 deg cones at 3.0 m, crazyflie_bright 0.73 m, values from
[doc 08](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md)), `sensors_cone.py`
(cone beams, materials: glass returns nothing) and `world_glass.py` (glass panels and 0.02-0.05 m
poles near the A-B line). `.venv/bin/python run_sensors.py --layouts 50 --seed 0` (about 11 min):

| planner | family | ideal reached / collision % | crazyflie | crazyflie_bright |
|---|---|---|---|---|
| freest_beam | random | 86 / 0 | 54 / 2 | 58 / 0 |
| freest_beam | glass | 82 / 4 | 0 / 90 | 0 / 96 |
| astar_esdf unknown map | random | 100 / 0 | 98 / 2 | 62 / 38 |
| astar_esdf unknown map | glass | 90 / 10 | 0 / 100 | 0 / 100 |

A drone that only trusts its rangers hits glass almost every time, and bright light breaks a
4-beam map-building planner even in plain rooms. Glass is placed on the A-B line by design, so
this measures the cost of the unsensed class, not a typical room. Details:
[results/sensors_notes.md](results/sensors_notes.md).

## Scoring a flight log (sim or real)

`score_log.py` scores any JSONL flight log in the [log_format.md](log_format.md) format (numpy +
matplotlib only, no arena import), so the same numbers come out of a sim run and a real flight:
`.venv/bin/python score_log.py results/log_hand_20line.jsonl --plot out.png`. On an arena run it
matches the arena scorer (17.76 s, 0.3792 m vs 0.3789 m at 10 Hz). Synthetic logs only so far.

Reactive planners (APF, VFH+, also with a 4-beam Crazyflie-like fan) are in
[close-area-planner-reactive](../close-area-planner-reactive/README.md).

## Estimator and faults (ran 2026-11-09, synthetic)

`estimator.py` is a position/velocity EKF fed by a 30 Hz VIO-like source and a 50 Hz IMU-like
accel, with 2 seeded dark zones per layout (drift x4, frame loss). It reports `quality`,
`reset_counter` and `sigma_xy`. `faults.py` adds five seeded cases: none, jump (0.5 m step near
an obstacle), bias (0.05 m/s for 10 s), dropout (2 s IMU only), overconfident (sigma_xy x0.25).
Planners see the estimate; ranges and scoring use truth.

`.venv/bin/python run_faults.py --planner freest_beam --layouts 50 --seed 0` (about 50 s):

| case | straight reached % | freest_beam reached % | collision % (both) | freest_beam est err median / max m |
|---|---|---|---|---|
| truth | 26 | 86 | 0 | - |
| none (dark zones on) | 16 | 58 | 0 | 0.165 / 1.09 |
| jump | 14 | 42 | 0 | 0.388 / 1.16 |
| bias | 16 | 40 | 0 | 0.406 / 1.28 |
| dropout | 16 | 46 | 0 | 0.291 / 1.22 |
| overconfident | 16 | 58 | 0 | 0.165 / 1.09 |

Source: [straight](results/faults_straight_summary_0.md), [freest_beam](results/faults_freest_beam_summary_0.md).

- **Faults cut reach, not safety, for range-only planners.** Ranges come from the true pose, so
  pose error only moves where the drone thinks B is. Runs end "stuck" at the estimated goal more
  than 0.3 m from the real one. A map-based planner (A*) is expected to turn the same error into
  collisions; not run yet.
- **Overconfident** changes nothing here because no planner reads `sigma_xy`; the error exceeds
  2 sigma at 99.6 % of steps (4.0 % for none).
- **Drift calibration:** random walk in distance fitted to C = 0.044 m/sqrt(m), about 0.14 m at
  10 m, against the hub's real OpenVINS number (RPE 1.5 % over 10 m,
  [relative-nav-benchmark](../relative-nav-benchmark/README.md)).
- Not calibrated: dark-zone numbers, IMU noise and bias. Yaw is truth, no VIO latency, no
  innovation gate.

## Complex arenas (ran 2026-11-09, synthetic)

[worlds_complex.py](worlds_complex.py) adds five layout families on the same 20 x 20 m world
model. Use them with `run.py --family <name>` or `run.evaluate(..., family="<name>")`.
`world.py` only registers them. Every layout is seeded by `[seed, index, 20-24]` and is
redrawn until a 4-connected path A => B exists on the grid inflated by the 0.15 m radius. A
and B must also have more than 0.25 m exact clearance. Sizes are arena choices, not
measurements of real buildings.

| family | layout |
|---|---|
| `office` | 1.6-2.0 m corridor, 3-6 rooms of 3.6-4.4 m square off it, one 0.8-1.0 m doorway each, 1-2 desks per room. A and B in different rooms |
| `warehouse` | shelf rows 0.8-1.0 m deep, 1.2-1.6 m aisles, a left main aisle, 1-2 cross aisles, 2-6 pallets against shelf faces. A bottom aisle, B top aisle |
| `forest` | 40-90 poles 0.1-0.35 m wide, 1.3 m minimum centre spacing (dart throwing), plus 3-6 tight spots with 0.3-0.6 m gaps |
| `maze` | 10 x 10 cells of 2 m, DFS spanning tree, 8-15 % of the interior walls removed for loops |
| `glass_office` | office plus 1-3 glass panels (material `glass`) across 45-65 % of the corridor width, between the doorways of A's and B's rooms |

Layout 0 of each family: [results/worlds_preview.png](results/worlds_preview.png).

### World JSON

[world_json.py](world_json.py) defines `close-area-world/1`: `bounds`, `a`, `b`, and
`obstacles` as `box`, `cylinder` or axis-aligned `wall` segments, each with a `material` and an
optional `tag`. The full schema is in the module docstring. `to_json(world)` writes it and
`from_json(dict)` validates it and builds a `World`. A browser playground and the replay viewer
are meant to read this one format. Neither reads it yet (see the limits below). One example per
family: [results/worlds_examples/](results/worlds_examples/office_0.json) (2.2-7.0 kB).

`.venv/bin/python world_json.py --check` runs a round trip (to_json => JSON text => from_json
=> to_json) on layouts 0-2 of all nine families. Result: 27 of 27 identical documents, max
signed-distance error 0.000116 m from the 0.1 mm rounding, and the free path still present.
At most 1 grid cell in 40 000 differs, on 2 forest layouts
([results/worlds_roundtrip.json](results/worlds_roundtrip.json)).

### Sanity table

`.venv/bin/python worlds_complex.py --sanity --layouts 20 --seed 0` took 117 s on an Apple M3
Max (CPython 3.11.15, numpy 2.4.6, scipy 1.17.1). It runs `straight` and `astar_esdf` with the
known map, ideal sensor and true pose:

| family | planner | reached % | collision % | stuck % | median time to goal s | median obstacles |
|---|---|---|---|---|---|---|
| office | straight | 0 | 0 | 100 | - | 26.5 |
| office | astar_esdf known | 100 | 0 | 0 | 21.01 | 26.5 |
| warehouse | straight | 0 | 0 | 100 | - | 22 |
| warehouse | astar_esdf known | 100 | 0 | 0 | 43.74 | 22 |
| forest | straight | 15 | 0 | 85 | 26.02 | 59 |
| forest | astar_esdf known | 100 | 0 | 0 | 22.72 | 59 |
| maze | straight | 0 | 5 | 95 | - | 43 |
| maze | astar_esdf known | 100 | 0 | 0 | 41.03 | 43 |
| glass_office | straight | 0 | 0 | 100 | - | 29.5 |
| glass_office | astar_esdf known | 100 | 0 | 0 | 25.12 | 29.5 |

No run timed out. Source: [results/worlds_sanity_0.md](results/worlds_sanity_0.md) and its
JSON with per-run rows.

- Every layout passed its free-path check on the first draw, so resampling never ran in
  these 100 layouts.
- The maze and warehouse medians (41 s and 44 s) are close to the 60 s limit. A slower
  planner will time out there for its speed, not because it fails to find the path.
- `glass_office` is the same as `office` here: the ideal fan sees glass. Only
  `sensors_cone.ConeRangeFan` ignores it. Use `worlds_complex.make_any_world` to keep the
  materials. `world_glass.make_any_world` resets every family it does not own to matte.
- Not run: unknown-map A*, reactive planners, the Crazyflie presets, estimator faults, or
  any seed other than 0.

## Altitude: windows and bars (ran 2026-11-09, synthetic)

IMAV-style indoor courses put B behind windows and under or over bars. A 2.5D planner at a fixed
1 m cannot pass them. `world_z.py` adds the `window_bar` family: a 20 x 20 x 3 m room with two
full-width walls between A and B. Each wall has either a 0.6 x 0.6 m window (centre height
0.5-2.5 m) or a 1.2-2.0 m opening crossed by 1-2 horizontal bars (0.4-2.6 m). At least one wall
has a window. Pillars and crates (0.4-1.4 m tall) sit between the walls. A and B are at 1.0 m.
Every obstacle has its own z range, and truth clearance (to boxes, walls, floor and ceiling) is
exact in 3D.

| planner | layouts | reached % | collision % | stuck % | median / p95 time to goal s | plan median / p95 ms | median min clearance m |
|---|---|---|---|---|---|---|---|
| `astar_esdf` 2.5D at z = 1.0 m | 50 | 14.0 | 0.0 | 86.0 | 28.16 / 36.42 | 44.79 / 82.79 | 1.0 (stuck at A) |
| `astar_esdf_3d` | 50 | 100.0 | 0.0 | 0.0 | 28.89 / 41.3 | 26.04 / 162.61 | 0.253 |

Seed 0, synthetic layouts, vehicle and sensor ([results](results/z_window_bar_0.md),
[json](results/z_window_bar_0.json)). The 2D map at 1.0 +- 0.15 m has a path A => B on 7 of 50
layouts. 2.5D reached exactly those 7. On the other 43 it found no path (4300 of its 4818
replans) and was scored stuck at A. 3D reached all 50 and flew between 0.55 and 2.44 m. Its
lowest clearance over all runs was 0.2022 m against the 0.15 m collision radius. Its first plan
per run also builds the ESDF and heuristic, with a median of 185.89 ms. Side view of run 0:
[results/z_window_bar_0_run0.png](results/z_window_bar_0_run0.png). Top panel: the true geometry
under the 3D track. Bottom panel: top view. The 2.5D track is hidden under the A marker because
it never left A.

    .venv/bin/python run_z.py --layouts 50 --seed 0   # ~5 min (295 s on Apple M3 Max, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1)

- `planners/astar_esdf_3d.py` needs the prior 3D map: there is no unknown-map mode.
- It is weighted A* (heuristic weight 2.0). Its heuristic is a geodesic distance computed on a
  2x coarser grid with scipy csgraph. Plain A* (weight 1.0) was far slower.
- The planning inflation is radius + 0.05 m (0.10 m leaves no free cell in a 0.6 m window).
  The follower keeps 0.25 m of chord clearance, because the grid ESDF can read about 0.09 m
  above the true clearance.
- `vehicle_z.VehicleZ`: |vz| <= 1.0 m/s. The planner caps commanded vz at 0.8 m/s and scales the
  whole velocity vector so its direction is kept.

Limits: synthetic only, axis-aligned boxes, truth pose, no estimator faults. The range fan is
horizontal at the vehicle's height and the planners do not use it. No downward or upward sensing.
No rotor downwash near window frames. B is always at 1.0 m. One seed. The 2.5D map is the
generous one (any box that overlaps the vehicle's height band). A thin 2D lidar slice was not
scored; it would see through bars just outside 1 m and is likely to collide rather than stop.

## Your room in the arena (ran 2026-11-10, synthetic)

Two CLIs write `close-area-world/1` JSON ([world_json.py](world_json.py), no schema change) for a
room of any size, for example an 8 x 6 m hall that the 20 x 20 m playground editor cannot hold.
Both check the result with `world_json.from_json` and the arena's free-path test
(`worlds_complex.has_free_path`, 0.15 m radius + 0.1 m at A and B) and exit 1 on a failure.
`--preview` flies `astar_esdf` with the known map through `run.run_one` (truth pose, arena defaults),
writes `results/room_<name>.json` and a PNG of map and path.

```sh
# 1. measured room => JSON spec (walls with door gaps, pillars, tables, A, B; format in the script's docstring)
.venv/bin/python world_from_room.py rooms/hall_8x6.json --preview results/room_hall_8x6.png
# 2. floor plan or whiteboard photo => boxes; PNG/JPG needs Pillow (PGM/PBM do not)
uv pip install --python .venv -r requirements-image.txt
.venv/bin/python world_from_image.py rooms/sketch_hall.png --ref 40 40 440 40 8.0 --origin-px 40 340 \
    --a-m 0.8 0.8 --b-m 7.2 1.0 -o rooms/sketch_hall.world.json --preview results/room_sketch_hall.png
```

`--ref X1 Y1 X2 Y2 D` = two pixel points (column, row) and their real distance in metres; or
`--m-per-px`. A and B take `--a-px COL ROW` or `--a-m X Y`. Then open `/site/solver/` and use
**Import world JSON**.

Inputs: [rooms/hall_8x6.json](rooms/hall_8x6.json) is a made-up 8 x 6 m hall (wall at x = 5 m with
a 0.9 m door, 2 pillars, 3 tables, 1 shelf). [rooms/sketch_hall.png](rooms/sketch_hall.png) (74 KB)
is the same hall drawn by [rooms/make_sketch.py](rooms/make_sketch.py) with wobbly pencil lines,
uneven paper and light smudges: a synthetic drawing, not a photo. Outputs:
[hall_8x6.world.json](rooms/hall_8x6.world.json), [sketch_hall.world.json](rooms/sketch_hall.world.json).

Score lines printed by the two commands ([room_hall_8x6.json](results/room_hall_8x6.json),
[room_sketch_hall.json](results/room_sketch_hall.json)), synthetic, truth pose, one run each:

```
astar_known on hall_8x6: reached, time to goal 23.98 s, min clearance 0.2212 m, path 9.204 m, 8 obstacles (synthetic, truth pose)
astar_known on sketch_hall: reached, time to goal 25.54 s, min clearance 0.2153 m, path 9.629 m, 45 obstacles (synthetic, truth pose)
```

- Image pipeline (`image` in [room_sketch_hall.json](results/room_sketch_hall.json)): scale 0.02 m/px
  from 400 px = 8.0 m, threshold 128, 12.49 % dark pixels, 96 x 76 cells, 1163 occupied => 45 boxes.
  Bounds came out [-0.1, -0.1, 8.1, 6.1] in [sketch_hall.world.json](rooms/sketch_hall.world.json):
  the drawn outer walls are about 0.1 m thick and sit on the bounds.
- Same hall, two inputs: the sketch path is 0.425 m longer and 1.56 s slower than the spec path,
  with 45 boxes instead of 8 obstacles.
- Previews: [room_hall_8x6.png](results/room_hall_8x6.png),
  [room_sketch_hall.png](results/room_sketch_hall.png). The Solver opened both worlds through its
  file input in headless Chrome 140 ("Imported sketch_hall.world.json (45 obstacles).", no console
  errors): [room_in_solver.png](results/room_in_solver.png), script
  [rooms/shot_solver.mjs](rooms/shot_solver.mjs), log [room_in_solver.json](results/room_in_solver.json).
  No sweep ran in the Solver.

Limits:

- Axis-aligned boxes and walls only. A diagonal wall or a round pillar in an image becomes a stair
  of boxes; `world_from_room.py` rejects a diagonal wall. Use `pillars` (cylinders) in the spec.
- Thresholds: a pixel is dark below grey 128 (`--threshold otsu` picks one from the histogram
  instead). A 0.1 m cell is occupied at 30 % dark
  pixels (`--fill`), blobs under 3 cells are dropped (`--min-cells`). Any dark mark (text, arrows,
  a shadow, a dark floor) becomes an obstacle; uneven light on a photo can need a higher or lower
  threshold. No perspective correction: photograph the plan straight on.
- Scale error: with `--ref`, +-1 px on each clicked point gives about +-1.4 px on the length. The CLI
  prints it (+-0.35 % for 400 px); a 100 px reference gives +-1.4 %. A tape-measure error adds to it.
- Boxes sit on 0.1 m cell edges, so a drawn edge moves by up to 0.1 m. The arena grid then marks
  cells within 0.05 m of a surface, so a door can lose up to another 0.2 m on the planner's grid.
- The free-path check is 2D at the hold altitude. `height_m` in the room spec only checks that
  `z_m` is at least 0.3 m below the ceiling.

## Limits

- 2.5D only: no altitude changes, no overhangs, z is held. Obstacles are axis-aligned boxes
  and vertical cylinders. Glass and thin poles: Sensor realism section; moving people:
  [close-area-moving-obstacles](../close-area-moving-obstacles/README.md).
- Point-mass vehicle with a velocity lag, not rigid-body dynamics: no attitude, wind,
  ground effect, motor saturation or contact physics. A collision ends the run.
- The range sensor is an ideal ray cast plus Gaussian noise and random dropout; no beam
  width, no multipath (cone beams, glass and dark surfaces: `sensors_cone.py`, Sensor realism).
- `stuck` is a displacement rule (0.2 m in 10 s). A planner that oscillates with more than
  0.2 m amplitude is never stuck; it times out at 60 s instead.
- The setpoint timeout (0.5 s => zero velocity) is our choice, modelled on PX4 leaving Offboard
  when the stream stops; the exact PX4 value was not checked in this job.
- Timing numbers (EDT, planner ms) depend on the machine and its load.
- Planners here: `straight`, `freest_beam` (in run_faults.py) and `astar_esdf`. APF and VFH+
  are in close-area-planner-reactive; safety filters in close-area-safety-filter; every planner
  on every arena in [close-area-benchmark](../close-area-benchmark/README.md).

## Sources

- Hub research docs, read in full: [close-area-nav README](../../docs/research/close-area-nav/README.md),
  [01 planning and mapping](../../docs/research/close-area-nav/01-planning-and-mapping.md)
  (section 5a design, section 7 lists sub-second EDT on 2M cells as unmeasured),
  [02 sims and platforms](../../docs/research/close-area-nav/02-sims-platforms-competitions.md)
  (pybullet arm64 wheel). These are hub docs, not external sources.
- [code] `scipy.ndimage.distance_transform_edt`, SciPy 1.18.1, used as installed; docs not re-read.
- [docs] MAVLink `ODOMETRY.quality` semantics are taken from the published interface in the
  task brief, not re-read.
