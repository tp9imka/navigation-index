# close-area-benchmark: every close-area planner x every arena family x two sensor presets

Goal: one results table that says which planner in the hub gets from A to B in which kind of
room, with an ideal range sensor and with a Crazyflie-like one. Plus one replay per family and
planner, in the world JSON format the showcase and the playground read.

Everything here is **synthetic**: simulated layouts, vehicle and sensors in
[close-area-arena](../close-area-arena/README.md). No SITL, no real flight.

## Run

```sh
cd samples/close-area-benchmark
uv venv .venv && uv pip install --python .venv -r requirements.txt   # arena deps + osqp
.venv/bin/python bench.py --layouts 20 --seed 0 --workers 14 --parity   # ~5.5 min on 14 processes
.venv/bin/python export_replays.py                                      # ~1 min, 72 replays
.venv/bin/python bench.py --render matrix_0                             # rebuild the .md from the .json
.venv/bin/python -m unittest test_smoke -v                              # ~5 s, skips without numpy
```

The full command above now runs all 21 rows. The five rows added later (DWA, `dwa_mem`, Bug2,
TangentBug, D* Lite) were run into the existing matrix without re-running the old nine:

```sh
.venv/bin/python bench.py --add-to matrix_0 --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite \
    --recheck vfh_plus,astar_unknown --workers 14                                  # ~3.6 min
.venv/bin/python bench.py --cross-check matrix_0                                     # ~1 s
.venv/bin/python export_replays.py --merge --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite   # ~35 s, 40 replays
```

The seven rows of loop-73 (Theta* x 4, MPPI x 2, Hybrid A*) were added the same way, without a recheck run
(`matrix_0_recheck.*` still holds the loop-46c check):

```sh
.venv/bin/python bench.py --add-to matrix_0 --planners thetastar_known,lazy_thetastar_known,thetastar_unknown,\
lazy_thetastar_unknown,mppi,mppi_astar,hybrid_astar --workers 14                     # ~34 min on a shared host
python3 results/cross_check_loop73.py                                                # ~1 s, stdlib
```

Measured on an Apple M3 Max (16 cores), macOS arm64, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1,
osqp 1.1.3 (`env` in [results/matrix_0.json](results/matrix_0.json)). The matrix took 323.4 s wall
with 14 worker processes (2,880 flights). The replay export took 58.0 s, one process
([results/export_replays_0.log](results/export_replays_0.log)). The added rows took 216.2 s wall
with 14 processes for 2,240 flights (1,600 new + 640 re-check), same interpreter and versions
([results/add_46c_stdout.txt](results/add_46c_stdout.txt), `additions` in matrix_0.json); their
replay export took 35.3 s ([results/export_replays_add_0.log](results/export_replays_add_0.log)).
The loop-73 rows took 2058.5 s wall with 14 processes for 2,240 flights, same interpreter and versions, on a
host shared with other jobs ([results/add_73_stdout.txt](results/add_73_stdout.txt), `additions` in
matrix_0.json). No replays were exported for them.

## What is in the matrix

Planners, imported by path from their samples. No planner file was edited.

| Row | Code | Map |
|---|---|---|
| `straight` | [close-area-arena planners/straight.py](../close-area-arena/planners/straight.py) | none |
| `freest_beam` | `FreestBeam` in [close-area-arena run_faults.py](../close-area-arena/run_faults.py) | none |
| `apf_escape` | [close-area-planner-reactive apf.py](../close-area-planner-reactive/apf.py), defaults (escape on) | none |
| `vfh_plus` | [close-area-planner-reactive vfh_plus.py](../close-area-planner-reactive/vfh_plus.py) | none |
| `astar_known` | [astar_esdf.py](../close-area-arena/planners/astar_esdf.py) `known_map=True` | true prior grid |
| `astar_unknown` | `astar_esdf` `known_map=False`, map placed on the area geofence (below) | built from range hits |
| `informed_rrt_star` | [close-area-planner-sampling rrt_star.py](../close-area-planner-sampling/rrt_star.py) `iters=5000, informed=True` | true prior grid |
| `astar_mpc` | [close-area-planner-mpc mpc.py](../close-area-planner-mpc/mpc.py) `AStarMPC(known_map=True)` | true prior grid |
| `astar_unknown_f2` | `astar_unknown` + F2 (PX4-CBF as shipped) from [close-area-safety-filter filters.py](../close-area-safety-filter/filters.py), on every 50 Hz step, own scan every 3 steps | built from range hits |
| `dwa` | [close-area-planner-dwa-bug dwa.py](../close-area-planner-dwa-bug/dwa.py) `make()` | none |
| `dwa_mem` | `dwa.make(memory_s=3.0)`: 3 s of remembered returns | last 3 s of returns |
| `bug2` | [close-area-planner-dwa-bug bug.py](../close-area-planner-dwa-bug/bug.py) `make("bug2")` | none |
| `tangent_bug` | `bug.make("tangent_bug")` | none |
| `dstar_lite` | [close-area-planner-dstar dstar_lite.py](../close-area-planner-dstar/dstar_lite.py) `GridReplanner(backend="dstar")`, same geofence as `astar_unknown` | built from range hits |
| `thetastar_known` | [close-area-planner-thetastar thetastar.py](../close-area-planner-thetastar/thetastar.py) `make(known_map=True)` | true prior grid |
| `lazy_thetastar_known` | `thetastar.make(known_map=True, lazy=True)` | true prior grid |
| `thetastar_unknown` | `thetastar.make(known_map=False, bounds=...)`, area geofence | built from range hits |
| `lazy_thetastar_unknown` | `thetastar.make(known_map=False, lazy=True, bounds=...)`, area geofence | built from range hits |
| `mppi` | [close-area-planner-mppi mppi.py](../close-area-planner-mppi/mppi.py) `make(guide="none", bounds=...)` | built from range hits |
| `mppi_astar` | `mppi.make(guide="astar", bounds=...)`: tracks the unknown-map A* path | built from range hits |
| `hybrid_astar` | [close-area-planner-hybrid-astar hybrid_astar.py](../close-area-planner-hybrid-astar/hybrid_astar.py) `make(bounds=...)` | built from range hits |

Families: `random`, `u_trap`, `narrow_gap` (world.py) and `office`, `warehouse`, `forest`, `maze`,
`glass_office` (worlds_complex.py), all through `world_glass.make_any_world`. Presets from
[presets.py](../close-area-arena/presets.py): `ideal` (72 rays, 360 deg, 6 m; it sees every
material, glass included) and `crazyflie` (4 cone beams of 27 deg, 3 m, glass invisible).
20 layouts per cell, seed 0, planner sees the true pose, scored on truth by the arena scorer.

Two settings differ from the arena defaults. Both are stated in [bench.py](bench.py).

- **Run time limit 120 s on maze and warehouse** (60 s elsewhere). It was needed: Informed RRT*
  reached B after more than 60 s in 30 of its 40 maze + warehouse successes on each preset
  ([results/long_runs_0.md](results/long_runs_0.md)). A* known never needed it (0 of 40).
- **Geofence for the unknown-map A*.** As shipped, its 24 m log-odds map starts at (-2.5, -2.5)
  in the A frame, so a B at negative x or y is clamped to the map edge. In office layouts A sits
  in any room. `astar_unknown` gets the area corner - 2 m as its map corner instead. A diagnostic
  run of the shipped prior on ideal ([results/prior_check_0.md](results/prior_check_0.md)):
  office 15 % vs 95 % reached, glass_office 25 % vs 95 %, warehouse 70 % vs 55 % (the shipped
  prior blocks the left main aisle, which here happened to help). `dstar_lite` subclasses the same
  `astar_esdf` unknown-map planner, so it gets the same geofence (a subclass in bench.py; the
  D* Lite sample is not edited). Its shipped prior was not run here.

The loop is `run.run_one`'s, with the sensor and an optional filter passed in. `--parity` checks
it against `run.evaluate` on ideal x random: 10 of 10 runs identical in outcome and min clearance
for both `straight` and `astar_known`.

Checks for the five added rows:

- **Old rows unchanged.** `vfh_plus` and `astar_unknown` were re-run in the same pool: 320 of 320
  runs each identical in outcome, min clearance, path length and time to goal
  ([results/matrix_0_recheck.md](results/matrix_0_recheck.md)). The 2,880 old rows in
  matrix_0.json are kept as they were.
- **loop-73 rows** ([results/matrix_0_loop73_checks.md](results/matrix_0_loop73_checks.md)): the 4,480
  older runs and their summaries equal the committed matrix_0.json; every run that the three source samples
  flew themselves is identical in outcome, min clearance, time to goal and path length, 1,440 of 1,440
  (Theta* flights_0.json, MPPI bench_ideal_0 / bench_crazyflie_0, Hybrid A* bench_0 stock vehicle).
- **Same as the source sample.** On ideal x random, u_trap and narrow_gap (layouts 0-19), DWA,
  `dwa_mem`, Bug2 and TangentBug match `close-area-planner-dwa-bug`'s own `run.evaluate` run on
  its 72-beam "default" fan: 60 of 60 runs each, same outcome and min clearance
  ([results/matrix_0_cross_checks.md](results/matrix_0_cross_checks.md)).

## Results (ran 2026-11-09, synthetic)

`python bench.py --layouts 20 --seed 0 --workers 14 --parity`, wall 323.4 s, plus the five rows
added by `bench.py --add-to matrix_0` (above), wall 216.2 s, and the seven loop-73 rows (2026-11-10),
wall 2058.5 s. Cell = reached % / collision %. Source: [results/matrix_0.md](results/matrix_0.md) (also stuck, timeout, median time,
min clearance, material hit), per-run rows in [results/matrix_0.json](results/matrix_0.json).

### Preset `ideal`

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| straight | 40 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 15 / 0 | 0 / 5 | 0 / 0 |
| freest_beam | 80 / 0 | 0 / 0 | 0 / 0 | 15 / 5 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 5 |
| apf_escape | 100 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 10 / 0 | 0 / 0 |
| vfh_plus | 100 / 0 | 0 / 0 | 50 / 0 | 40 / 0 | 20 / 0 | 100 / 0 | 10 / 0 | 50 / 0 |
| astar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown | 100 / 0 | 100 / 0 | 90 / 0 | 95 / 0 | 55 / 0 | 100 / 0 | 95 / 0 | 95 / 0 |
| informed_rrt_star | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_mpc | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown_f2 | 75 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 65 / 0 | 0 / 0 | 0 / 0 |
| dwa | 80 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 90 / 0 | 0 / 0 | 5 / 0 |
| dwa_mem | 75 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 75 / 0 | 0 / 0 | 5 / 0 |
| bug2 | 90 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 20 / 0 | 0 / 0 |
| tangent_bug | 95 / 0 | 90 / 0 | 45 / 0 | 25 / 0 | 20 / 0 | 100 / 0 | 15 / 0 | 25 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 | 85 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 95 / 0 |
| thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| thetastar_unknown | 100 / 0 | 100 / 0 | 90 / 0 | 90 / 0 | 60 / 0 | 100 / 0 | 95 / 0 | 90 / 0 |
| lazy_thetastar_unknown | 100 / 0 | 100 / 0 | 90 / 0 | 90 / 0 | 65 / 0 | 100 / 0 | 90 / 0 | 95 / 0 |
| mppi | 90 / 0 | 0 / 0 | 25 / 0 | 25 / 0 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 0 |
| mppi_astar | 100 / 0 | 100 / 0 | 95 / 0 | 100 / 0 | 65 / 0 | 100 / 0 | 95 / 0 | 95 / 0 |
| hybrid_astar | 100 / 0 | 100 / 0 | 70 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 85 / 0 |

Best planner per family: the prior-map planners (`astar_known`, `informed_rrt_star`, `astar_mpc`,
and since loop-73 `thetastar_known`, `lazy_thetastar_known`) reach 100 % with 0 % collisions in every
family. The paragraph below compares the 14 older rows; the loop-73 rows are in "Reading, loop-73 rows". Best without a prior map:
`astar_unknown` in every family (random 100, u_trap 100, narrow_gap 90, office 95, warehouse 55,
forest 100, maze 95, glass_office 95). `dstar_lite` ties it on random, u_trap, warehouse
(55 / 0), forest and glass_office (95 / 0) and is 5 points lower on narrow_gap (85), office (90)
and maze (90). Other ties: `apf_escape` and `vfh_plus` on random, `astar_unknown_f2` on u_trap,
and `freest_beam`, `apf_escape`, `vfh_plus`, `bug2` and `tangent_bug` on forest.

### Preset `crazyflie`

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| straight | 40 / 40 | 0 / 65 | 0 / 70 | 0 / 65 | 0 / 65 | 15 / 60 | 0 / 80 | 5 / 70 |
| freest_beam | 50 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 35 / 15 | 0 / 10 | 5 / 5 |
| apf_escape | 85 / 0 | 35 / 20 | 0 / 5 | 0 / 10 | 0 / 0 | 60 / 25 | 0 / 15 | 5 / 20 |
| vfh_plus | 45 / 55 | 0 / 100 | 5 / 95 | 5 / 90 | 0 / 95 | 35 / 65 | 0 / 100 | 0 / 90 |
| astar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown | 100 / 0 | 95 / 5 | 25 / 5 | 35 / 25 | 0 / 50 | 95 / 5 | 35 / 15 | 5 / 65 |
| informed_rrt_star | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_mpc | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown_f2 | 100 / 0 | 100 / 0 | 15 / 5 | 50 / 5 | 0 / 0 | 95 / 5 | 55 / 0 | 5 / 45 |
| dwa | 40 / 35 | 0 / 15 | 0 / 40 | 0 / 55 | 0 / 50 | 10 / 90 | 0 / 65 | 5 / 60 |
| dwa_mem | 55 / 5 | 0 / 0 | 5 / 0 | 5 / 0 | 0 / 20 | 45 / 15 | 0 / 15 | 5 / 5 |
| bug2 | 90 / 10 | 20 / 30 | 0 / 0 | 0 / 35 | 15 / 20 | 50 / 40 | 0 / 20 | 5 / 40 |
| tangent_bug | 55 / 45 | 35 / 15 | 5 / 10 | 10 / 45 | 0 / 35 | 25 / 75 | 0 / 50 | 5 / 50 |
| dstar_lite | 100 / 0 | 100 / 0 | 15 / 10 | 20 / 40 | 5 / 45 | 100 / 0 | 40 / 25 | 10 / 65 |
| thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| thetastar_unknown | 100 / 0 | 90 / 5 | 5 / 15 | 35 / 60 | 5 / 60 | 95 / 5 | 65 / 10 | 20 / 65 |
| lazy_thetastar_unknown | 100 / 0 | 100 / 0 | 15 / 25 | 45 / 35 | 30 / 20 | 95 / 5 | 50 / 0 | 30 / 55 |
| mppi | 55 / 40 | 0 / 95 | 0 / 100 | 5 / 75 | 0 / 100 | 100 / 0 | 0 / 95 | 10 / 75 |
| mppi_astar | 80 / 20 | 40 / 60 | 15 / 85 | 10 / 85 | 0 / 100 | 100 / 0 | 0 / 100 | 5 / 85 |
| hybrid_astar | 95 / 5 | 100 / 0 | 10 / 5 | 40 / 45 | 0 / 35 | 90 / 10 | 35 / 15 | 5 / 75 |

Best planner per family: again the three prior-map planners, 100 / 0 everywhere; `dstar_lite`
ties them on random, u_trap and forest. Best without a prior map (highest reached %, then lowest
collision %): random `astar_unknown`, `astar_unknown_f2` and `dstar_lite` (100 / 0), u_trap
`astar_unknown_f2` and `dstar_lite` (100 / 0), narrow_gap `astar_unknown` (25 / 5), office
`astar_unknown_f2` (50 / 5), warehouse `bug2` (15 / 20), forest `dstar_lite` (100 / 0), maze
`astar_unknown_f2` (55 / 0), glass_office `dstar_lite` (10 / 65). The last two picks by that rule
are weak: warehouse had no reach at all before (best 0 / 0, `astar_unknown_f2`), and on
glass_office `freest_beam` and `dwa_mem` (5 / 5) are far safer than `dstar_lite`'s 65 % collisions.

### Reading, loop-73 rows

- **Theta* with a prior map ties A* known map**: 100 / 0 in every family on both presets.
- **Without a map, on ideal, `mppi_astar` is the best or tied-best map-free row in every family** (by the
  bench's rule in [results/matrix_0.md](results/matrix_0.md)): narrow_gap 95 vs 90 for `astar_unknown`,
  office 100 vs 95, warehouse 65 vs 55 (tied with `lazy_thetastar_unknown`). `mppi` alone gets 0 % on
  u_trap and maze.
- **With 4 beams the new map-free rows collide more in rooms.** `mppi_astar` collides in 60-100 % on
  u_trap, narrow_gap, office, warehouse, maze and glass_office (`astar_unknown`: 5-65 %). `thetastar_unknown`
  collides in 60 % on office and warehouse. `lazy_thetastar_unknown` is the bench's map-free pick on crazyflie
  warehouse (30 / 20) and glass_office (30 / 55), `thetastar_unknown` on maze (65 / 10).
- **Hybrid A* reaches less often than `astar_unknown` on ideal** in narrow_gap (70 vs 90), office (90 vs 95),
  maze (90 vs 95) and glass_office (85 vs 95), and ties it elsewhere (warehouse 55 both).

### Reading

- **A prior map solves every family here.** The prior-map rows are the same on both presets
  because those planners never read the scan. That is an upper bound: the map is exact and the
  pose is true.
- **Without a map, 4 beams break the harder rooms.** `astar_unknown` falls from 95 to 35 % on
  office, 55 to 0 % on warehouse (50 % collision) and 95 to 5 % on glass_office (65 % collision:
  7 runs hit glass, 6 hit matte surfaces between beams).
- **F2 trades reach for safety, and the sign depends on the sensor.** With 72 beams it freezes
  the vehicle in doors, gaps and aisles (0 % reached on narrow_gap, office, warehouse, maze,
  glass_office; runs end stuck). With 4 beams it sees fewer points and cuts in less: warehouse
  collisions 50 => 0 %, maze reached 35 => 55 %, office 35 => 50 %. It cannot see glass:
  glass_office still 45 % collision, all 9 on glass.
- **Reactive planners only fit open clutter.** Forest is 100 % for all of them on ideal; office,
  warehouse and maze are 0-40 %. VFH+ on the 4-beam preset collides in 55-100 % of runs.
- **D* Lite flies like the unknown-map A* it is built on.** Same map, cost and follower, only the
  search is incremental. On ideal 153 of 160 runs end with the same outcome as `astar_unknown`;
  on crazyflie 115 of 160 ([results/matrix_0_cross_checks.md](results/matrix_0_cross_checks.md)).
  The 4-beam differences go both ways: office 35 => 20 %, narrow_gap 25 => 15 %, but warehouse
  0 => 5 %, maze 35 => 40 %, u_trap 95 => 100 %. Equal-cost ties between the two searches are a
  likely cause; no run was traced. Mean planner step 4.2 vs 10.7 ms on ideal, 2.9 vs 13.4 ms on
  crazyflie, measured with 14 processes in parallel, so read it only as "a few times less".
- **DWA alone does not leave a U trap or find a door.** 0 % on u_trap and maze on both presets,
  at most 10 % on narrow_gap, office and warehouse. It is a local planner meant to run under a
  global one (see the [dwa-bug README](../close-area-planner-dwa-bug/README.md)).
- **3 s of scan memory is what makes DWA usable with 4 beams.** `dwa` => `dwa_mem` collisions on
  crazyflie: random 35 => 5 %, office 55 => 0 %, forest 90 => 15 %, maze 65 => 15 %,
  glass_office 60 => 5 %. Reach barely moves (random 40 => 55 %); in the rooms the runs now end stuck instead (office 95 %,
  maze 80 %, glass_office 90 % stuck). The
  memory uses the true pose, so it has no drift here.
- **Bug2 and TangentBug get out of a U trap, not out of rooms.** On ideal both reach 90 % on
  u_trap, as `apf_escape`, but at most 25 % on office, warehouse and glass_office and 20 % on maze.
  TangentBug is the best pure local planner on ideal narrow_gap after VFH+ (45 vs 50 %). On
  crazyflie Bug2 reaches 90 % on random (10 % collision), the most of any map-free local planner,
  but collides in 20-40 % of runs on u_trap, office, warehouse, forest, maze and glass_office.
  TangentBug collides in 10-75 % of crazyflie runs in every family.
- **glass_office on ideal is just an office.** The ideal ray fan sees glass. The glass cost shows
  only on the crazyflie preset, which is why the replays use it for that family.

## Replays

`export_replays.py` flies layout 0 of each family again for every planner (crazyflie for
glass_office, ideal otherwise) and writes `site/data/showcase/replays_v2/<family>__<planner>.json`
plus `index.json` grouped by family. 112 files (14 planners x 8 families), largest 34,492 bytes
(cap 120,000), all at 10 Hz. The 40 files of the five added rows were written by
`export_replays.py --merge`, which keeps the 72 older files and their index entries as they were.
Each file embeds `world_json.to_json(world)` (`close-area-world/1`), the truth path, `est: null`
(true pose in every run), truth clearance per kept sample, the outcome and the scorer row. Every
outcome and min clearance matches its row in results/matrix_0.json: 72 of 72 for the first export
([results/export_replays_0.log](results/export_replays_0.log)) and 40 of 40 for the added rows
([results/export_replays_add_0.log](results/export_replays_add_0.log)). The world JSON in all 112
files round-trips through `world_json.from_json` unchanged (same logs). Export walls: 58.0 s for
the first 72, 35.3 s for the 40 added.

## Scenario packs

A scenario pack is one JSON file that holds "our room + our drone + the bar". On the day the team
writes it once and re-runs it after every tuning change. [pack.py](pack.py) flies it with this
benchmark's own flight loop and prints PASS / FAIL / NOT PROVEN per planner and criterion.

```sh
.venv/bin/python pack.py run packs/office_crazyflie.json --workers 14   # ~15 s, results/pack_office_crazyflie.*
.venv/bin/python pack.py run packs/hall_8x6.json --workers 14           # ~8 s, results/pack_hall_8x6.*
.venv/bin/python pack.py check-matrix results/pack_office_crazyflie.json   # seed-0 rows vs matrix_0.json
```

Exit code: 0 if at least one planner passes every criterion, 1 if none does, 2 if the pack is invalid.
`--out results/<stem>` changes the output stem (default `results/pack_<name>`).
`--shipped-inflation` keeps the planners' shipped 0.15 m inflation (the pack before loop-99, see "Vehicle radius").

### Schema `close-area-pack/1`

| key | required | value |
|---|---|---|
| `schema` | yes | `"close-area-pack/1"` |
| `name` | yes | `[a-z0-9_-]+`, also the default output stem |
| `description` | no | free text |
| `worlds` | yes | list. Each entry is an inline `close-area-world/1` dict ([world_json.py](../close-area-arena/world_json.py)), a file path relative to the pack file, `"preset:<name>"` (a file in [site/playground/presets/](../../site/playground/presets/index.json)) or `"family:<family>:<index>[:<seed>]"` (the benchmark's own generated layout, seed 0 by default) |
| `vehicle` | no | `"default"` or `{"radius_m", "v_max", "a_max", "tau"}`, all four ([presets.py](../close-area-arena/presets.py) `vehicle_kwargs`). Default `"default"` = 0.15 m, 2 m/s, 3 m/s^2, 0.15 s |
| `sensor` | no | a `presets.SENSOR_PRESETS` name (`ideal`, `crazyflie`, `crazyflie_bright`, `dense`, `depth_cam_87`, `lidar_2d`) or a sensor dict `{"beams", "fov_deg", "max_range_m", "min_range_m", "noise_sigma_m"}` + optional `cone_deg`, `dropout`. Default `"ideal"` |
| `planners` | yes | ids of `PLANNERS` in [bench.py](bench.py) |
| `seeds` | no | `n` or `{"n": n, "jitter_m": R}`, n in 1..200, default 5 seeds, R = 0.5 m. Seed 0 flies the exact A and B. Seed k > 0 moves A and B by a seeded offset within R that keeps vehicle radius + 0.1 m from every surface, the same offset for every planner. It is a port of `seedJitter` in [site/solver/sweep.js](../../site/solver/sweep.js) (same PRNG; seeds 0-9 on hall_8x6 and office_0 give the same points as the JS). One difference: the clearance uses the pack's vehicle radius, the Solver reads the world's. The seed also picks the sensor noise stream, as in bench.py |
| `max_time_s` | no | `"auto"` (default: `bench.max_time(family)`, 120 s for maze and warehouse, else 60 s) or seconds |
| `criteria` | yes | `{metric: "<op> <number>"}`, op in `>=`, `>`, `<=`, `<` (`==` for count rules). A count rule may also be `{"rule": "<op> <n>", "min_runs": N}`; a top-level `"min_runs": N` inside `criteria` sets it for every count rule |

Metrics and how each is judged:

- `<outcome>_rate` for `reached`, `collision`, `stuck`, `timeout`, `error`: k of n runs, 95 % Wilson
  interval (z = 1.96, as the Solver). Identical runs (same world, outcome, time to B and path length at
  3 dp) count once, as in the Solver. `>=` passes only if the **lower** bound meets the threshold, `<=` only if
  the **upper** bound does. The bar then still holds at the pessimistic end of the interval, so a lucky
  small sample cannot pass. It is FAIL when even the optimistic bound misses the bar, and NOT PROVEN in
  between (more seeds or worlds needed). Each rate cell also prints "runs needed if every run
  succeeds": the smallest n whose all-success Wilson bound passes the bar, or "never".
- `<outcome>_count`, or `collisions`, `timeouts`, `errors`: k = runs with that outcome, every run
  counted (duplicates included). `<=`, `<` and `==` FAIL as soon as k is past the bar, because more runs
  cannot lower k. Otherwise the rule is NOT PROVEN until there are at least `min_runs` distinct runs
  (default: the pack's seeds x worlds), and then the bar decides. The cell prints the Wilson bound of
  the same outcome's rate next to the verdict, for example `rate <= 0.20` after 0 collisions in 15 runs.
- `time_to_goal_p<q>_s`: the nearest-rank q-quantile of time to B over all runs, with a run that did
  not reach B counted as infinite. The interval is the distribution-free 95 % interval from order statistics
  (binomial ranks). Same rule: `<=` passes on the upper end.
- `min_clearance_m`: the smallest min clearance over all flown runs. It is the observed worst case,
  with no interval, so it is only PASS or FAIL.
- Planner verdict: PASS if every criterion passes, FAIL if any fails, else NOT PROVEN.

What the rule implies for small packs (from the Wilson formula; with no failures the lower bound is
n / (n + 1.96^2), `pack.runs_needed`, checked in test_smoke.py):

| bar | runs needed if every run succeeds |
|---|---|
| `reached_rate >= 0.8` | 16 |
| `reached_rate >= 0.9` | 35 |
| `reached_rate >= 0.95` | 73 |
| `collision_rate <= 0.05` | 73 |
| `collision_rate <= 0` | never: with 0 collisions the upper bound is 3.84 / (n + 3.84), above 0 for any n |

When a planner is NOT PROVEN and every open criterion is met by its observed value (all-success rates,
count rules short of `min_runs`, a quantile whose point value meets the bar), the table ends with a
sample-size hint: how many distinct runs each open bar needs and the seed count that gives them at
the pack's world count.

**Count rule or rate rule.** A rate rule (`collision_rate <= 0.05`) is a claim about the planner on
runs you have not flown: with 95 % confidence the true rate is below the bar. A count rule
(`collisions == 0`) says only what happened: no collision in these n runs. Use a count rule when the
bar is "zero events" or "at most k events" and the run budget is fixed, which is the case for a
safety bar on a small pack. Use a rate rule when the claim must carry to new runs, and fly the runs
the table says it needs. The count cell prints the rate bound next to the verdict so nobody reads
"0 collisions in 15 runs" as "collision rate 0": 15 clean runs support a rate of at most 0.20.

**Flight loop.** Each run calls `bench.run_one`'s own code object. Four of its module globals are
swapped: `run.DEFAULTS` (the pack vehicle), `world_glass.make_any_world` (the pack world),
`presets.make_sensor` (the pack sensor) and `max_time` (the pack limit). Same loop, stop conditions,
F2 filter wiring and scorer as the matrix. Check: on office layouts 0-2 at seed 0 with `crazyflie`, the 15
pack runs have the same outcome as results/matrix_0.json. Their min clearance is within 0.2 mm, because
the world JSON rounds coordinates to 0.1 mm. The same code on the unrounded layouts is identical in
outcome and min clearance, 15 of 15
([results/pack_office_crazyflie_matrix_check.md](results/pack_office_crazyflie_matrix_check.md)).

**Vehicle radius.** The pack radius changes the vehicle, the collision stop, the scoring and (since
loop-99) how far the planners inflate obstacles. pack.py applies the Solver worker's per-run override
(site/playground/worker.js `radius_override`, loop-75b): each constant in `pack.RADIUS_CONSTS`
(`astar_esdf.RADIUS`, `astar_esdf.CARROT_CLEAR_M`, `hybrid_astar.RADIUS`, `rrt_star.RADIUS`,
`mppi.R_COLL`, `mppi.D_SAFE`, `dwa.RADIUS`, `bug.RADIUS`) is set to radius + (shipped value - 0.15 m)
for that run and restored after it; APF and VFH+ get the radius on the instance. At 0.15 m nothing
changes. The result JSON lists what was set under `planner_inflation`. Before loop-99 a pack with
`radius_m` 0.2 flew planners that planned for 0.15 m, while the Solver inflated by 0.2 m, so the two
disagreed (drill 2026-11, blocker B2).

Drill room check (synthetic, [results/pack_drill_solver_vs_pack.md](results/pack_drill_solver_vs_pack.md)):
on docs/drill-2026-11/our_room.world.json, radius 0.2 m, `depth_cam_87`, seeds 0-4, the worker driver
without the override equals the old pack and the driver with it equals the pack with it, 15 of 15
(planner, seed) runs, all four score fields
([results/pack_drill_b2_confirm.json](results/pack_drill_b2_confirm.json)). After the fix the 35-seed pack
([results/pack_drill_our_room_after.md](results/pack_drill_our_room_after.md)) matches the drill's Solver
export on all 15 seed 0-4 runs. `lazy_thetastar_unknown` went from 17/35 reached, 18 collisions to
34/35 reached, 1 collision (seed 34, min clearance 0.1996 m): still FAIL on the collision bar.
`thetastar_known` and `astar_known` stay 35/35, PASS.

**Heading.** The bench loop has no yaw policy: the vehicle starts facing B and turns only if the
planner commands a yaw rate. The playground turns a sensor with less than 360 deg of view toward the
direction of travel; that policy is not applied here. This matters for `depth_cam_87`.

### Results (ran 2026-11-10, synthetic)

These two packs ran before loop-99, so their planners inflated by the shipped 0.15 m. The office pack
uses the default 0.15 m vehicle and is unaffected; the hall numbers (0.2 m) were not re-run with the
override.

Both packs ran on an Apple M3 Max (16 cores), macOS arm64, CPython 3.12.10, numpy 2.5.4, 14 worker
processes. Every number below is from results/pack_*.md / .json. The planner sees the true pose and
runs are scored on truth. Each pack was run more than once while pack.py was written (office 3 times,
hall 2 times), with the same numbers every time.

**`packs/office_crazyflie.json`**: `preset:office_0`, `family:office:1`, `family:office:2`, default
vehicle, `crazyflie` sensor, 5 planners x 3 worlds x 5 seeds = 75 runs, exit code 1
([results/pack_office_crazyflie.md](results/pack_office_crazyflie.md)).

| planner | reached_rate >= 0.9 | collisions == 0 (min 15 runs) | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| astar_known | NOT PROVEN: 15/15 = 1.00, CI [0.80, 1.00]; lower 0.80 misses >= 0.9, upper 1.00 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | PASS: 18.1 s, CI [13.8, 22.6], n=15; upper 22.6 <= 30 | **NOT PROVEN** |
| astar_unknown | FAIL: 6/15 = 0.40, CI [0.20, 0.64]; upper 0.64 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 3 collision in 15 distinct runs; 3 == 0 is false; rate <= 0.45 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [18.2, inf], n=15; upper inf misses <= 30, lower 18.2 meets it | **FAIL** |
| astar_unknown_f2 | NOT PROVEN: 12/15 = 0.80, CI [0.55, 0.93]; lower 0.55 misses >= 0.9, upper 0.93 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | NOT PROVEN: 26.6 s, CI [18.3, 32.3], n=15; upper 32.3 misses <= 30, lower 18.3 meets it | **NOT PROVEN** |
| lazy_thetastar_unknown | FAIL: 7/15 = 0.47, CI [0.25, 0.70]; upper 0.70 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 5 collision in 15 distinct runs; 5 == 0 is false; rate <= 0.58 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [19.5, inf], n=15; upper inf misses <= 30, lower 19.5 meets it | **FAIL** |
| dwa_mem | FAIL: 1/15 = 0.07, CI [0.01, 0.30]; upper 0.30 misses >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=15; lower inf misses <= 30 | **FAIL** |

Sample-size hint: astar_known: NOT PROVEN only on sample size. reached_rate >= 0.9 needs 35 distinct runs if every run succeeds (has 15) => at least 12 seeds x 3 worlds.

**`packs/hall_8x6.json`**: [rooms/hall_8x6.world.json](../close-area-arena/rooms/hall_8x6.world.json),
vehicle radius 0.2 m (stock speed limits), `depth_cam_87` (30 beams over 87 deg, 0.3-5 m), 6 planners
x 10 seeds = 60 runs, exit code 1 ([results/pack_hall_8x6.md](results/pack_hall_8x6.md)).
The hall keeps a free path at 0.2 m for all 10 seeds' A and B.

| planner | reached_rate >= 0.9 | collisions == 0 (min 10 runs) | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| astar_known | NOT PROVEN: 10/10 = 1.00, CI [0.72, 1.00]; lower 0.72 misses >= 0.9, upper 1.00 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 10 distinct runs; 0 == 0 in 10 >= 10 distinct runs; rate <= 0.28 (95 % Wilson bound, not a rate claim) | PASS: 23.7 s, CI [22.9, 24.6], n=10; upper 24.6 <= 30 | **NOT PROVEN** |
| astar_unknown | FAIL: 3/10 = 0.30, CI [0.11, 0.60]; upper 0.60 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 7 collision in 10 distinct runs; 7 == 0 is false; rate <= 0.89 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [29.2, inf], n=10; upper inf misses <= 30, lower 29.2 meets it | **FAIL** |
| astar_unknown_f2 | FAIL: 0/9 = 0.00, CI [0.00, 0.30]; upper 0.30 misses >= 0.9; runs needed if every run succeeds: 35 | NOT PROVEN: 0 collision in 9 distinct runs (10 flown); 9 distinct runs < min_runs 10; rate <= 0.30 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=9; lower inf misses <= 30 | **FAIL** |
| mppi_astar | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 10 collision in 10 distinct runs; 10 == 0 is false; rate <= 1.00 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |
| tangent_bug | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 2 collision in 10 distinct runs; 2 == 0 is false; rate <= 0.51 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |
| straight | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 10 distinct runs; 0 == 0 in 10 >= 10 distinct runs; rate <= 0.28 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |

Sample-size hint: astar_known: NOT PROVEN only on sample size. reached_rate >= 0.9 needs 35 distinct runs if every run succeeds (has 10) => at least 35 seeds x 1 worlds.

Reading:

- **No planner passes either pack.** Both exit with code 1. With the count rule for collisions (loop-86),
  A* with the true map passes the collision and time bars and is NOT PROVEN only on sample size: 15 or 10
  runs are below the 35 that `reached_rate >= 0.9` needs. Under the old rate rule `collision_rate <= 0`
  could never pass.
- **A* with the true map is the best candidate in both.** It reached B in 15 of 15 office runs and
  10 of 10 hall runs with no collision. Its median time to B is 18.1 s (office) and 23.7 s (hall), and the
  time criterion passes on the upper bound. The collision count rule passes; the reach criterion is NOT
  PROVEN only because n is small.
- **Without a map, F2 is the safest in the offices but stalls in the hall.** In the offices
  `astar_unknown_f2` reached B in 12 of 15 runs with 0 collisions, while `astar_unknown` reached 6 of 15
  with 3 collisions. In the hall `astar_unknown_f2` ended stuck in all 10 runs.
- **In the hall the map-free planners collide.** `astar_unknown` collided in 7 of 10 runs and
  `mppi_astar` in 10 of 10. The 0.2 m vehicle flies planners that inflate by 0.15 m, and the 87 deg camera
  only turns when the planner turns it. These runs do not separate those two causes from the planners
  themselves.
- **Baseline.** `straight` reached B in 0 of 10 hall runs, all stuck. On random layouts it reaches 40 %
  (results/matrix_0.md, ideal).

## Not included yet

- Replays (`export_replays.py --merge`) for the seven loop-73 rows: not exported, since the replay folder
  is generated site data outside loop-73's paths.
- The diagnostic shipped-prior run for `dstar_lite` (only `astar_unknown` has one), and a scan
  memory for APF, VFH+ or the Bug planners.
- The other safety-filter arms (F1 CP-stop, the map-based CBFs) and the estimator faults: the
  matrix gives every planner the true pose.
- `crazyflie_bright` and `dense` presets, and seeds other than 0.

## Limits

- 20 layouts per cell: one run is 5 percentage points. Seed 0 only; the planners' own tuning was
  partly done on seed-0 layouts of random, u_trap and narrow_gap, so those are not held out.
- 2.5D point-mass arena, exact prior map, true pose. Planner timings are not part of the scores.
- The geofence change to the unknown-map A* is a bench choice; the shipped default is the
  diagnostic row in results/prior_check_0.md.
- One machine (M3 Max, macOS). Linux not tested.

## Sources

- Arena, families, presets, scorer: [close-area-arena README](../close-area-arena/README.md),
  [CONTRACT.md](../close-area-arena/CONTRACT.md).
- Planner samples: [reactive](../close-area-planner-reactive/README.md),
  [sampling](../close-area-planner-sampling/README.md), [mpc](../close-area-planner-mpc/README.md),
  [safety filter](../close-area-safety-filter/README.md),
  [DWA / Bug2 / TangentBug](../close-area-planner-dwa-bug/README.md),
  [D* Lite](../close-area-planner-dstar/README.md).
- Research lane: [docs/research/close-area-nav](../../docs/research/close-area-nav/README.md).
- Hub wiring proposals: [INTEGRATION.md](INTEGRATION.md).
