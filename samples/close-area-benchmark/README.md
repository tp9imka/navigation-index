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
.venv/bin/python bench.py --layouts 20 --seed 0 --workers 10 --parity   # ~50 min on 10 processes, 21 rows
.venv/bin/python export_replays.py                                      # 168 replays, 21 planners x 8 families
.venv/bin/python bench.py --render matrix_0                             # rebuild the .md from the .json
.venv/bin/python -m unittest test_smoke -v                              # ~5 s, skips without numpy
```

The full command above runs all 21 rows; that is how the current results/matrix_0.json was made, on
2026-11-12. Before that the matrix grew in three runs, and `--add-to` is still the way to add a planner
without re-running the rest. The five rows added second (DWA, `dwa_mem`, Bug2, TangentBug, D* Lite)
were run into the existing matrix without re-running the old nine:

```sh
.venv/bin/python bench.py --add-to matrix_0 --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite \
    --recheck vfh_plus,astar_unknown --workers 14                                  # ~3.6 min
.venv/bin/python bench.py --cross-check matrix_0                                     # ~1 s
.venv/bin/python export_replays.py --merge --planners dwa,dwa_mem,bug2,tangent_bug,dstar_lite   # ~35 s, 40 replays
```

The seven rows added on 2026-11-10 (Theta* x 4, MPPI x 2, Hybrid A*) were added the same way, without a recheck run
(`matrix_0_recheck.*` still holds the 2026-11-09 check):

```sh
.venv/bin/python bench.py --add-to matrix_0 --planners thetastar_known,lazy_thetastar_known,thetastar_unknown,\
lazy_thetastar_unknown,mppi,mppi_astar,hybrid_astar --workers 14                     # ~34 min on a shared host
python3 results/cross_check_loop73.py                                                # ~1 s, stdlib
```

Measured on an Apple M3 Max (16 cores), macOS arm64, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1,
osqp 1.1.3 (`env` in [results/matrix_0.json](results/matrix_0.json)). The current matrix took 2963.7 s
wall with 10 worker processes for 6,720 flights, on 2026-11-12, with the dropped-beam fix on
(`regenerated` in matrix_0.json). Its replays were re-exported with `--merge` for the 8 planners the fix
changed and the 7 rows that had none ([results/export_replays_regen_0.log](results/export_replays_regen_0.log));
all 168 match their matrix row. History of the earlier runs: the first matrix took 323.4 s wall
with 14 worker processes (2,880 flights). The replay export took 58.0 s, one process
([results/export_replays_0.log](results/export_replays_0.log)). The added rows took 216.2 s wall
with 14 processes for 2,240 flights (1,600 new + 640 re-check), same interpreter and versions
([results/add_46c_stdout.txt](results/add_46c_stdout.txt)); their
replay export took 35.3 s ([results/export_replays_add_0.log](results/export_replays_add_0.log)).
The 2026-11-10 rows took 2058.5 s wall with 14 processes for 2,240 flights, same interpreter and versions, on a
host shared with other jobs ([results/add_73_stdout.txt](results/add_73_stdout.txt)). No replays were
exported for them until 2026-11-12. The `additions` records of those runs are in the git history of matrix_0.json.

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
  run of the shipped prior on ideal ([results/prior_check_0.md](results/prior_check_0.md), both arms
  run on 2026-11-09, before the dropped-beam fix): office 15 % vs 95 % reached, glass_office 25 % vs 95 %, warehouse 70 % vs 55 % (the shipped
  prior blocks the left main aisle, which here happened to help). `dstar_lite` subclasses the same
  `astar_esdf` unknown-map planner, so it gets the same geofence (a subclass in bench.py; the
  D* Lite sample is not edited). Its shipped prior was not run here.

The loop is `run.run_one`'s, with the sensor and an optional filter passed in. `--parity` checks
it against `run.evaluate` on ideal x random: 10 of 10 runs identical in outcome and min clearance
for both `straight` and `astar_known`.

Checks on the 2026-11-12 run, which replaced every row: the 13 planners that build no map from the scan
reproduced their earlier runs in 4160 of 4160, and the 6 unknown-map rows that the dropout-fix study also ran
equal its `status` arm (the same fix applied by a wrapper) in 1920 of 1920 runs on outcome, min clearance, path
length and time to goal. Checks made when rows were added, before that run:

- **Old rows unchanged.** `vfh_plus` and `astar_unknown` were re-run in the same pool: 320 of 320
  runs each identical in outcome, min clearance, path length and time to goal
  ([results/matrix_0_recheck.md](results/matrix_0_recheck.md)). The 2,880 old rows in
  matrix_0.json were kept as they were.
- **2026-11-10 rows** ([results/matrix_0_loop73_checks.md](results/matrix_0_loop73_checks.md)): the 4,480
  older runs and their summaries equal the committed matrix_0.json; every run that the three source samples
  flew themselves is identical in outcome, min clearance, time to goal and path length, 1,440 of 1,440
  (Theta* flights_0.json, MPPI bench_ideal_0 / bench_crazyflie_0, Hybrid A* bench_0 stock vehicle).
- **Same as the source sample.** On ideal x random, u_trap and narrow_gap (layouts 0-19), DWA,
  `dwa_mem`, Bug2 and TangentBug match `close-area-planner-dwa-bug`'s own `run.evaluate` run on
  its 72-beam "default" fan: 60 of 60 runs each, same outcome and min clearance
  ([results/matrix_0_cross_checks.md](results/matrix_0_cross_checks.md)).

## Results (ran 2026-11-12, synthetic)

`python bench.py --layouts 20 --seed 0 --workers 10 --parity`, all 21 rows in one run, wall 2963.7 s, with the
dropped-beam fix on ([upstream-findings section 22](../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls)).
The 13 planners that do not build a map from the scan reproduced their earlier runs exactly (4160 of 4160);
the 8 that do moved by -3.7 to +1.3 points of reach on ideal and -5.6 to +5.7 on crazyflie. Cell = reached % / collision %. Source: [results/matrix_0.md](results/matrix_0.md) (also stuck, timeout, median time,
min clearance, material hit), per-run rows in [results/matrix_0.json](results/matrix_0.json).

### Preset `ideal`

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| straight | 40 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 15 / 0 | 0 / 5 | 0 / 0 |
| freest_beam | 80 / 0 | 0 / 0 | 0 / 0 | 15 / 5 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 5 |
| apf_escape | 100 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 10 / 0 | 0 / 0 |
| vfh_plus | 100 / 0 | 0 / 0 | 50 / 0 | 40 / 0 | 20 / 0 | 100 / 0 | 10 / 0 | 50 / 0 |
| astar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown | 100 / 0 | 100 / 0 | 80 / 0 | 90 / 0 | 50 / 0 | 100 / 0 | 90 / 0 | 90 / 0 |
| informed_rrt_star | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_mpc | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown_f2 | 80 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 65 / 0 | 0 / 0 | 0 / 0 |
| dwa | 80 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 90 / 0 | 0 / 0 | 5 / 0 |
| dwa_mem | 75 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 75 / 0 | 0 / 0 | 5 / 0 |
| bug2 | 90 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 20 / 0 | 0 / 0 |
| tangent_bug | 95 / 0 | 90 / 0 | 45 / 0 | 25 / 0 | 20 / 0 | 100 / 0 | 15 / 0 | 25 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 | 85 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 90 / 0 |
| thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| thetastar_unknown | 100 / 0 | 100 / 0 | 80 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 95 / 0 |
| lazy_thetastar_unknown | 100 / 0 | 100 / 0 | 100 / 0 | 85 / 0 | 55 / 0 | 100 / 0 | 85 / 0 | 90 / 0 |
| mppi | 90 / 0 | 0 / 0 | 25 / 0 | 25 / 0 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 0 |
| mppi_astar | 100 / 0 | 100 / 0 | 95 / 0 | 95 / 0 | 55 / 0 | 100 / 0 | 95 / 0 | 95 / 0 |
| hybrid_astar | 100 / 0 | 100 / 0 | 85 / 0 | 90 / 0 | 50 / 0 | 100 / 0 | 90 / 0 | 85 / 0 |

Best planner per family: the prior-map planners (`astar_known`, `informed_rrt_star`, `astar_mpc`,
and since 2026-11-10 `thetastar_known`, `lazy_thetastar_known`) reach 100 % with 0 % collisions in every
family. The paragraph below compares the 14 older rows; the 2026-11-10 rows are in "Reading, rows added 2026-11-10". Best without a prior map:
`dstar_lite` in every family (random 100, u_trap 100, narrow_gap 85, office 90, warehouse 55,
forest 100, maze 90, glass_office 90). `astar_unknown` ties it on random, u_trap, office, forest, maze
and glass_office and is 5 points lower on narrow_gap (80) and warehouse (50). Other ties: `apf_escape` and `vfh_plus` on random, `astar_unknown_f2` on u_trap,
and `freest_beam`, `apf_escape`, `vfh_plus`, `bug2` and `tangent_bug` on forest.

### Preset `crazyflie`

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office |
|---|---|---|---|---|---|---|---|---|
| straight | 40 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 15 / 0 | 0 / 5 | 0 / 0 |
| freest_beam | 80 / 0 | 0 / 0 | 0 / 0 | 15 / 5 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 5 |
| apf_escape | 100 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 10 / 0 | 0 / 0 |
| vfh_plus | 100 / 0 | 0 / 0 | 50 / 0 | 40 / 0 | 20 / 0 | 100 / 0 | 10 / 0 | 50 / 0 |
| astar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown | 100 / 0 | 100 / 0 | 80 / 0 | 90 / 0 | 50 / 0 | 100 / 0 | 90 / 0 | 90 / 0 |
| informed_rrt_star | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_mpc | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| astar_unknown_f2 | 80 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 65 / 0 | 0 / 0 | 0 / 0 |
| dwa | 80 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 90 / 0 | 0 / 0 | 5 / 0 |
| dwa_mem | 75 / 0 | 0 / 0 | 10 / 0 | 5 / 0 | 10 / 0 | 75 / 0 | 0 / 0 | 5 / 0 |
| bug2 | 90 / 0 | 90 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 20 / 0 | 0 / 0 |
| tangent_bug | 95 / 0 | 90 / 0 | 45 / 0 | 25 / 0 | 20 / 0 | 100 / 0 | 15 / 0 | 25 / 0 |
| dstar_lite | 100 / 0 | 100 / 0 | 85 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 90 / 0 |
| thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| lazy_thetastar_known | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 | 100 / 0 |
| thetastar_unknown | 100 / 0 | 100 / 0 | 80 / 0 | 90 / 0 | 55 / 0 | 100 / 0 | 90 / 0 | 95 / 0 |
| lazy_thetastar_unknown | 100 / 0 | 100 / 0 | 100 / 0 | 85 / 0 | 55 / 0 | 100 / 0 | 85 / 0 | 90 / 0 |
| mppi | 90 / 0 | 0 / 0 | 25 / 0 | 25 / 0 | 15 / 0 | 100 / 0 | 0 / 0 | 10 / 0 |
| mppi_astar | 100 / 0 | 100 / 0 | 95 / 0 | 95 / 0 | 55 / 0 | 100 / 0 | 95 / 0 | 95 / 0 |
| hybrid_astar | 100 / 0 | 100 / 0 | 85 / 0 | 90 / 0 | 50 / 0 | 100 / 0 | 90 / 0 | 85 / 0 |

Best planner per family: again the prior-map planners, 100 / 0 everywhere; `astar_unknown` and
`astar_unknown_f2` tie them on random, u_trap and forest, `dstar_lite` on random and u_trap. Best of the
14 older rows without a prior map (highest reached %, then lowest collision %): random and u_trap
`astar_unknown`, `astar_unknown_f2` and `dstar_lite` (100 / 0), narrow_gap `dstar_lite` (20 / 0), office
`astar_unknown_f2` (40 / 5), warehouse `astar_unknown_f2` (30 / 0), forest `astar_unknown` and
`astar_unknown_f2` (100 / 0), maze `dstar_lite` (55 / 0), glass_office `astar_unknown` and `dstar_lite`
(15 / 60). The glass_office pick by that rule is weak: `freest_beam` and `dwa_mem` (5 / 5) are far safer
than the 60 % collisions of the top two.

### Reading, rows added 2026-11-10

- **Theta* with a prior map ties A* known map**: 100 / 0 in every family on both presets.
- **Without a map, on ideal, `mppi_astar` is the best or tied-best map-free row in every family but
  narrow_gap** (by the bench's rule in [results/matrix_0.md](results/matrix_0.md)): office 95 vs 90 for
  `astar_unknown`, maze 95 vs 90, warehouse 55 vs 50 (tied with `dstar_lite` and both Theta* rows). On
  narrow_gap `lazy_thetastar_unknown` reaches 100 vs 95. `mppi` alone gets 0 % on u_trap and maze.
- **With 4 beams the new map-free rows collide more in rooms.** `mppi_astar` collides in 80-100 % on
  narrow_gap, office, warehouse, maze and glass_office (`astar_unknown`: 0-60 % in the same families).
  `thetastar_unknown` collides in 40 % on office and warehouse. On crazyflie the 2026-11-10 rows tie
  the older map-free leaders on random, u_trap and forest and lead alone only on glass_office
  (`thetastar_unknown`, 20 / 65).
- **Hybrid A* flies like `astar_unknown` on ideal**: tied in six families, 85 vs 80 on narrow_gap and
  85 vs 90 on glass_office. Before the dropped-beam fix it was 5-20 points lower in four rooms.

### Reading

- **A prior map solves every family here.** The prior-map rows are the same on both presets
  because those planners never read the scan. That is an upper bound: the map is exact and the
  pose is true.
- **Without a map, 4 beams break the harder rooms.** `astar_unknown` falls from 90 to 30 % on
  office, 50 to 5 % on warehouse (55 % collision) and 90 to 15 % on glass_office (60 % collision:
  8 runs hit glass, 4 hit matte surfaces between beams).
- **F2 trades reach for safety, and the sign depends on the sensor.** With 72 beams it freezes
  the vehicle in doors, gaps and aisles (0 % reached on narrow_gap, office, warehouse, maze,
  glass_office; runs end stuck). With 4 beams it sees fewer points and cuts in less: warehouse
  collisions 55 => 0 %, warehouse reached 5 => 30 %, office 30 => 40 %. It cannot see glass:
  glass_office still 65 % collision, all 13 on glass.
- **Reactive planners only fit open clutter.** Forest is 100 % for all of them on ideal; office,
  warehouse and maze are 0-40 %. VFH+ on the 4-beam preset collides in 55-100 % of runs.
- **D* Lite flies like the unknown-map A* it is built on.** Same map, cost and follower, only the
  search is incremental. On ideal 155 of 160 runs end with the same outcome as `astar_unknown`;
  on crazyflie 127 of 160 ([results/matrix_0_cross_checks.md](results/matrix_0_cross_checks.md)).
  The 4-beam differences go both ways: office 30 => 35 %, warehouse 5 => 10 %, maze 45 => 55 %, but
  forest 100 => 95 %. Equal-cost ties between the two searches are a likely cause; no run was traced.
  Mean planner step 3.0 vs 7.7 ms on ideal, 2.1 vs 9.2 ms on crazyflie, measured with 10 processes in
  parallel, so read it only as "a few times less".
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

## Forward depth camera

A RealSense D435i-class forward depth camera is the likeliest range sensor on a PX4-class drone.
This section adds it as a third sensor column for the five map-free planners that matter on the first day.
Ran 2026-11-10, re-run 2026-11-12 with the dropped-beam fix on; synthetic (simulated layouts, vehicle and
sensor), scored on truth.

```
.venv/bin/python bench.py --presets depth_cam_87 --planners astar_unknown,astar_unknown_f2,dstar_lite,dwa_mem,mppi_astar \
    --layouts 6 --workers 10 --stem matrix_depth_0         # 240 runs, wall 59 s on 10 processes
python3 results/matrix_depth_0.compare.py                  # pairs it with matrix_0 layouts 0-5, no flights
```

- **Sensor:** preset `depth_cam_87` from [presets.py](../close-area-arena/presets.py): 30 beams of 3 deg
  over 87 deg forward, 0.3-5 m, 0.04 m noise, 5 % dropout, glass and mirror invisible. No code change
  in bench.py was needed: `--presets` takes any `presets.SENSOR_PRESETS` name and `--stem` exists.
- **Yaw:** the benchmark loop sets yaw toward B at the start and none of the five planners sends a yaw
  rate, so the camera stays pointed at B for the whole flight (fixed yaw). That is the same as the
  playground default (`fixed`, [site/playground](../../site/playground/README.md)).
  "Look where you go" was not run here.
- **Prior-map planners are not re-run.** They never read the scan: in matrix_0 their ideal and
  crazyflie rows are identical in 160/160 runs each
  ([results/matrix_depth_0.compare.md](results/matrix_depth_0.compare.md)). Their depth column equals
  ideal (100 / 0 in every family).
- **Dropout fix on:** a dropped beam adds nothing to the map
  ([upstream-findings section 22](../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls)).
- **Small sample, directional only.** n = 6 layouts per cell (seed 0, indices 0-5); one layout moves a
  cell by 17 points. Intervals below are 95 % Wilson on the 48 pooled runs per row.

Cell = reached % / collision %, n = 6, from [results/matrix_depth_0.md](results/matrix_depth_0.md).
Directional.

| planner | random | u_trap | narrow_gap | office | warehouse | forest | maze | glass_office | pooled reached % [95 % CI] | pooled collision % [95 % CI] |
|---|---|---|---|---|---|---|---|---|---|---|
| astar_unknown | 100 / 0 | 100 / 0 | 33 / 50 | 83 / 0 | 83 / 0 | 100 / 0 | 83 / 0 | 17 / 83 | 75 [61, 85] (36/48) | 17 [9, 30] (8/48) |
| astar_unknown_f2 | 100 / 0 | 100 / 0 | 0 / 0 | 0 / 0 | 17 / 17 | 100 / 0 | 50 / 0 | 0 / 0 | 46 [33, 60] (22/48) | 2 [0, 11] (1/48) |
| dstar_lite | 100 / 0 | 100 / 0 | 33 / 33 | 83 / 0 | 67 / 0 | 100 / 0 | 83 / 0 | 17 / 83 | 73 [59, 83] (35/48) | 15 [7, 27] (7/48) |
| dwa_mem | 67 / 17 | 0 / 0 | 17 / 0 | 0 / 0 | 0 / 0 | 100 / 0 | 0 / 0 | 17 / 0 | 25 [15, 39] (12/48) | 2 [0, 11] (1/48) |
| mppi_astar | 100 / 0 | 100 / 0 | 83 / 0 | 100 / 0 | 83 / 0 | 100 / 0 | 100 / 0 | 17 / 83 | 85 [73, 93] (41/48) | 10 [5, 22] (5/48) |

The same five planners on the same six layouts, pooled over 8 families (48 runs, from
[results/matrix_depth_0.compare.md](results/matrix_depth_0.compare.md)):

| planner | ideal (72 rays, 360 deg, 6 m) | depth_cam_87 | crazyflie (4 beams, 3 m) |
|---|---|---|---|
| astar_unknown | 88 [75, 94] / 0 [0, 7] | 75 [61, 85] / 17 [9, 30] | 52 [38, 66] / 17 [9, 30] |
| astar_unknown_f2 | 31 [20, 45] / 0 [0, 7] | 46 [33, 60] / 2 [0, 11] | 52 [38, 66] / 12 [6, 25] |
| dstar_lite | 92 [80, 97] / 0 [0, 7] | 73 [59, 83] / 15 [7, 27] | 48 [34, 62] / 23 [13, 37] |
| dwa_mem | 29 [18, 43] / 0 [0, 7] | 25 [15, 39] / 2 [0, 11] | 17 [9, 30] / 6 [2, 17] |
| mppi_astar | 94 [83, 98] / 0 [0, 7] | 85 [73, 93] / 10 [5, 22] | 38 [25, 52] / 58 [44, 71] |

Reading (all synthetic, directional):

- **The depth camera sits between the two old columns.** Best pooled row: `mppi_astar` 85 % reached,
  10 % collision; `astar_unknown` 75 / 17 and `dstar_lite` 73 / 15 overlap it. On ideal the best rows
  reach 88-94 % with no collision; on crazyflie the best reach 48-52 %.
- **Glass is the main loss.** Glass is invisible to the depth preset, so glass_office collides in
  83 % for the three map-based rows. 14 of the 20 collisions of those rows hit glass (outcome mix
  in the compare file).
- **`mppi_astar` leads on the depth camera.** 100 / 0 on office and maze, 83 / 0 on narrow_gap and
  warehouse. Before the dropped-beam fix it collided in 50 % on office and warehouse.
- **F2 freezes as on ideal.** `astar_unknown_f2` ends stuck in 22 of 48 runs (0 % reached on
  narrow_gap, office, glass_office) with 1 collision.
- **`dwa_mem` stays a clutter-only planner:** 100 % in forest, 0 % in u_trap, office, warehouse, maze.

Environment: the 2026-11-12 re-run used Python 3.12.10 and numpy 2.5.4, the same as matrix_0 (the first run
used 3.11.15 and 2.4.6). `dwa_mem`, which builds no map, reproduced its first-run rows in 48 of 48 runs.
Proposed cheat-sheet column and decoder sentence: [INTEGRATION_depth.md](INTEGRATION_depth.md).

## Replays

`export_replays.py` flies layout 0 of each family again for every planner (crazyflie for
glass_office, ideal otherwise) and writes `site/data/showcase/replays_v2/<family>__<planner>.json`
plus `index.json` grouped by family. 168 files (21 planners x 8 families), largest 34,492 bytes
(cap 120,000), all at 10 Hz. `export_replays.py --merge --planners ...` rewrites only the named planners and keeps
every other file and index entry as it was. Each file embeds `world_json.to_json(world)` (`close-area-world/1`),
the truth path, `est: null` (true pose in every run), truth clearance per kept sample, the outcome and the scorer
row. Every outcome and min clearance matches its row in results/matrix_0.json, 168 of 168, and the world JSON in
every file round-trips through `world_json.from_json` unchanged. Logs: the first 72
([results/export_replays_0.log](results/export_replays_0.log), 58.0 s), the 40 of the rows added second
([results/export_replays_add_0.log](results/export_replays_add_0.log), 35.3 s), and on 2026-11-12 the 64 of
the 8 planners the dropped-beam fix changed (5 of them had none before) and the 16 of the two prior-map
Theta* rows ([results/export_replays_regen_0.log](results/export_replays_regen_0.log), 329.1 s and 36.7 s).

## Scenario packs

A scenario pack is one JSON file that holds "our room + our drone + the bar". On the first day you
write it once and re-runs it after every tuning change. [pack.py](pack.py) flies it with this
benchmark's own flight loop and prints PASS / FAIL / NOT PROVEN per planner and criterion.

```sh
.venv/bin/python pack.py run packs/office_crazyflie.json --workers 14   # ~15 s, results/pack_office_crazyflie.*
.venv/bin/python pack.py run packs/hall_8x6.json --workers 14           # ~8 s, results/pack_hall_8x6.*
.venv/bin/python pack.py check-matrix results/pack_office_crazyflie.json   # seed-0 rows vs matrix_0.json
```

Exit code: 0 if at least one planner passes every criterion, 1 if none does, 2 if the pack is invalid.
`--out results/<stem>` changes the output stem (default `results/pack_<name>`).
`--shipped-inflation` keeps the planners' shipped 0.15 m inflation (the pack before 2026-11-10, see "Vehicle radius").

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
F2 filter wiring and scorer as the matrix. Check: on office layouts 0-2 at seed 0 with `crazyflie`, 14 of
the 15 pack runs have the same outcome as results/matrix_0.json, with min clearance within 0.2 mm, because
the world JSON rounds coordinates to 0.1 mm. The 15th (astar_unknown_f2, office #0) gets stuck on the
unrounded layout and reaches B on the rounded one: that rounding is enough to flip an unknown-map run.
The same code on the unrounded layouts is identical in outcome and min clearance, 15 of 15
([results/pack_office_crazyflie_matrix_check.md](results/pack_office_crazyflie_matrix_check.md)).

**Vehicle radius.** The pack radius changes the vehicle, the collision stop, the scoring and (since
2026-11-10) how far the planners inflate obstacles. pack.py applies the Solver worker's per-run override
(site/playground/worker.js `radius_override`): each constant in `pack.RADIUS_CONSTS`
(`astar_esdf.RADIUS`, `astar_esdf.CARROT_CLEAR_M`, `hybrid_astar.RADIUS`, `rrt_star.RADIUS`,
`mppi.R_COLL`, `mppi.D_SAFE`, `dwa.RADIUS`, `bug.RADIUS`) is set to radius + (shipped value - 0.15 m)
for that run and restored after it; APF and VFH+ get the radius on the instance. At 0.15 m nothing
changes. The result JSON lists what was set under `planner_inflation`. Before that change a pack with
`radius_m` 0.2 flew planners that planned for 0.15 m, while the Solver inflated by 0.2 m, so the two
disagreed (drill 2026-11, blocker B2).

Drill room check (synthetic, [results/pack_drill_solver_vs_pack.md](results/pack_drill_solver_vs_pack.md)):
on docs/cold-start-drill/our_room.world.json, radius 0.2 m, `depth_cam_87`, seeds 0-4, the worker driver
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

### Results (ran 2026-11-12, synthetic)

Re-run on 2026-11-12 with the dropped-beam fix on (`SKIP_DROPPED_BEAMS = True`, upstream-findings section 22)
and with the per-run radius override, so the hall planners (0.2 m vehicle) now inflate by the drone radius.
The office pack uses the default 0.15 m vehicle, where the override changes nothing.

Both packs ran on an Apple M3 Max (16 cores), macOS arm64, CPython 3.12.10, numpy 2.5.4, 1 worker
process. Every number below is from results/pack_*.md / .json. The planner sees the true pose and
runs are scored on truth.

**`packs/office_crazyflie.json`**: `preset:office_0`, `family:office:1`, `family:office:2`, default
vehicle, `crazyflie` sensor, 5 planners x 3 worlds x 5 seeds = 75 runs, exit code 1
([results/pack_office_crazyflie.md](results/pack_office_crazyflie.md)).

| planner | reached_rate >= 0.9 | collisions == 0 (min 15 runs) | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| astar_known | NOT PROVEN: 15/15 = 1.00, CI [0.80, 1.00]; lower 0.80 misses >= 0.9, upper 1.00 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | PASS: 18.1 s, CI [13.8, 22.6], n=15; upper 22.6 <= 30 | **NOT PROVEN** |
| astar_unknown | FAIL: 5/15 = 0.33, CI [0.15, 0.58]; upper 0.58 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 4 collision in 15 distinct runs; 4 == 0 is false; rate <= 0.52 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [27.5, inf], n=15; upper inf misses <= 30, lower 27.5 meets it | **FAIL** |
| astar_unknown_f2 | NOT PROVEN: 13/15 = 0.87, CI [0.62, 0.96]; lower 0.62 misses >= 0.9, upper 0.96 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | NOT PROVEN: 28.2 s, CI [18.4, 32.3], n=15; upper 32.3 misses <= 30, lower 18.4 meets it | **NOT PROVEN** |
| lazy_thetastar_unknown | FAIL: 7/15 = 0.47, CI [0.25, 0.70]; upper 0.70 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 5 collision in 15 distinct runs; 5 == 0 is false; rate <= 0.58 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [17.4, inf], n=15; upper inf misses <= 30, lower 17.4 meets it | **FAIL** |
| dwa_mem | FAIL: 1/15 = 0.07, CI [0.01, 0.30]; upper 0.30 misses >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 15 distinct runs; 0 == 0 in 15 >= 15 distinct runs; rate <= 0.20 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=15; lower inf misses <= 30 | **FAIL** |

Sample-size hint: astar_known: NOT PROVEN only on sample size. reached_rate >= 0.9 needs 35 distinct runs if every run succeeds (has 15) => at least 12 seeds x 3 worlds.

**`packs/hall_8x6.json`**: [rooms/hall_8x6.world.json](../close-area-arena/rooms/hall_8x6.world.json),
vehicle radius 0.2 m (stock speed limits), `depth_cam_87` (30 beams over 87 deg, 0.3-5 m), 6 planners
x 10 seeds = 60 runs, exit code 1 ([results/pack_hall_8x6.md](results/pack_hall_8x6.md)).
The hall keeps a free path at 0.2 m for all 10 seeds' A and B.

| planner | reached_rate >= 0.9 | collisions == 0 (min 10 runs) | time_to_goal_p50_s <= 30 | verdict |
|---|---|---|---|---|
| astar_known | NOT PROVEN: 10/10 = 1.00, CI [0.72, 1.00]; lower 0.72 misses >= 0.9, upper 1.00 meets it; runs needed if every run succeeds: 35 | PASS: 0 collision in 10 distinct runs; 0 == 0 in 10 >= 10 distinct runs; rate <= 0.28 (95 % Wilson bound, not a rate claim) | PASS: 23.3 s, CI [22.6, 25.0], n=10; upper 25.0 <= 30 | **NOT PROVEN** |
| astar_unknown | NOT PROVEN: 8/10 = 0.80, CI [0.49, 0.94]; lower 0.49 misses >= 0.9, upper 0.94 meets it; runs needed if every run succeeds: 35 | FAIL: 2 collision in 10 distinct runs; 2 == 0 is false; rate <= 0.51 (95 % Wilson bound, not a rate claim) | NOT PROVEN: 29.5 s, CI [28.5, inf], n=10; upper inf misses <= 30, lower 28.5 meets it | **FAIL** |
| astar_unknown_f2 | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 10 distinct runs; 0 == 0 in 10 >= 10 distinct runs; rate <= 0.28 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |
| mppi_astar | FAIL: 4/10 = 0.40, CI [0.17, 0.69]; upper 0.69 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 5 collision in 10 distinct runs; 5 == 0 is false; rate <= 0.76 (95 % Wilson bound, not a rate claim) | NOT PROVEN: inf s, CI [19.4, inf], n=10; upper inf misses <= 30, lower 19.4 meets it | **FAIL** |
| tangent_bug | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | FAIL: 1 collision in 10 distinct runs; 1 == 0 is false; rate <= 0.40 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |
| straight | FAIL: 0/10 = 0.00, CI [0.00, 0.28]; upper 0.28 misses >= 0.9; runs needed if every run succeeds: 35 | PASS: 0 collision in 10 distinct runs; 0 == 0 in 10 >= 10 distinct runs; rate <= 0.28 (95 % Wilson bound, not a rate claim) | FAIL: inf s, CI [inf, inf], n=10; lower inf misses <= 30 | **FAIL** |

Sample-size hint: astar_known: NOT PROVEN only on sample size. reached_rate >= 0.9 needs 35 distinct runs if every run succeeds (has 10) => at least 35 seeds x 1 worlds.

Reading:

- **No planner passes either pack.** Both exit with code 1. With the count rule for collisions,
  A* with the true map passes the collision and time bars and is NOT PROVEN only on sample size: 15 or 10
  runs are below the 35 that `reached_rate >= 0.9` needs. Under the old rate rule `collision_rate <= 0`
  could never pass.
- **A* with the true map is the best candidate in both.** It reached B in 15 of 15 office runs and
  10 of 10 hall runs with no collision. Its median time to B is 18.1 s (office) and 23.3 s (hall), and the
  time criterion passes on the upper bound. The collision count rule passes; the reach criterion is NOT
  PROVEN only because n is small.
- **Without a map, F2 is the safest in the offices but stalls in the hall.** In the offices
  `astar_unknown_f2` reached B in 13 of 15 runs with 0 collisions, while `astar_unknown` reached 5 of 15
  with 4 collisions. In the hall `astar_unknown_f2` ended stuck in all 10 runs.
- **In the hall the map-free planners still collide, less than before.** `astar_unknown` reached 8 of 10
  and collided in 2; `mppi_astar` reached 4 and collided in 5. On 2026-11-10 they collided in 7 and 10 of 10,
  with planners that inflated by 0.15 m for the 0.2 m vehicle. Since then the radius override and the
  dropped-beam fix both changed, and these runs do not separate the two. The 87 deg camera only turns when
  the planner turns it.
- **Baseline.** `straight` reached B in 0 of 10 hall runs, all stuck. On random layouts it reaches 40 %
  (results/matrix_0.md, ideal).

## Not included yet

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
