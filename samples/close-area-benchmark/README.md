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

Measured on an Apple M3 Max (16 cores), macOS arm64, CPython 3.12.10, numpy 2.5.4, scipy 1.18.1,
osqp 1.1.3 (`env` in [results/matrix_0.json](results/matrix_0.json)). The matrix took 323.4 s wall
with 14 worker processes (2,880 flights). The replay export took 58.0 s, one process
([results/export_replays_0.log](results/export_replays_0.log)).

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
  prior blocks the left main aisle, which here happened to help).

The loop is `run.run_one`'s, with the sensor and an optional filter passed in. `--parity` checks
it against `run.evaluate` on ideal x random: 10 of 10 runs identical in outcome and min clearance
for both `straight` and `astar_known`.

## Results (ran 2026-11-09, synthetic)

`python bench.py --layouts 20 --seed 0 --workers 14 --parity`, wall 323.4 s. Cell = reached % /
collision %. Source: [results/matrix_0.md](results/matrix_0.md) (also stuck, timeout, median time,
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

Best planner per family: the three prior-map planners (`astar_known`, `informed_rrt_star`,
`astar_mpc`) reach 100 % with 0 % collisions in every family. Best without a prior map:
`astar_unknown` in every family (random 100, u_trap 100, narrow_gap 90, office 95, warehouse 55,
forest 100, maze 95, glass_office 95), tied on random, u_trap and forest with reactive planners
or the F2 arm.

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

Best planner per family: again the three prior-map planners, 100 / 0 everywhere. Best without a
prior map: random `astar_unknown` and `astar_unknown_f2` (100 / 0), u_trap `astar_unknown_f2`
(100 / 0), narrow_gap `astar_unknown` (25 / 5), office `astar_unknown_f2` (50 / 5), warehouse
none reaches (best 0 / 0), forest `astar_unknown` and `astar_unknown_f2` (95 / 5), maze
`astar_unknown_f2` (55 / 0), glass_office `freest_beam` (5 / 5).

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
- **glass_office on ideal is just an office.** The ideal ray fan sees glass. The glass cost shows
  only on the crazyflie preset, which is why the replays use it for that family.

## Replays

`export_replays.py` flies layout 0 of each family again for every planner (crazyflie for
glass_office, ideal otherwise) and writes `site/data/showcase/replays_v2/<family>__<planner>.json`
plus `index.json` grouped by family. 72 files, largest 22,673 bytes (cap 120,000), all at 10 Hz.
Each file embeds `world_json.to_json(world)` (`close-area-world/1`), the truth path, `est: null`
(true pose in every run), truth clearance per kept sample, the outcome and the scorer row. Every
outcome and min clearance matches its row in results/matrix_0.json: 72 of 72
([results/export_replays_0.log](results/export_replays_0.log)). The world JSON in all 72 files
round-trips through `world_json.from_json` unchanged (same log). Last export run: 58.0 s wall.

## Not included yet

- DWA and Bug2 (`close-area-planner-dwa-bug`) and D* Lite (`close-area-planner-dstar`): no such
  samples in this checkout. Add a row in `PLANNERS` in [bench.py](bench.py) once they exist.
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
  [safety filter](../close-area-safety-filter/README.md).
- Research lane: [docs/research/close-area-nav](../../docs/research/close-area-nav/README.md).
- Hub wiring proposals: [INTEGRATION.md](INTEGRATION.md).
