# Drill B2: Solver vs scenario pack on the drill room (loop-99)

Input: synthetic (2.5D point mass, simulated depth_cam_87, truth pose, scored on truth). Not a flight result.
World docs/drill-2026-11/our_room.world.json, vehicle radius 0.2 m, v_max 1.5 m/s, a_max 3, tau 0.15, seeds 0-4 with the Solver's jittered A and B.

## Cause (confirmed)

`pack_drill_b2_confirm.json` (pack_drill_b2_repro.py, 60 native runs, one process): the worker.js driver with its per-run radius override equals pack.fly inside the same override, and the driver without the override equals the shipped pack, on all 15 (planner, seed) pairs for outcome, time to goal, min clearance and path length.

| planner | seed | driver, inflate 0.2 m (Solver) | driver, 0.15 m | pack, shipped 0.15 m (drill) | pack + override |
|---|---|---|---|---|---|
| lazy_thetastar_unknown | 0 | reached 29.18 s, clr 0.215 m | reached 27.22 s, clr 0.252 m | reached 27.22 s, clr 0.252 m | reached 29.18 s, clr 0.215 m |
| thetastar_known | 0 | reached 22.26 s, clr 0.2219 m | reached 22.28 s, clr 0.214 m | reached 22.28 s, clr 0.214 m | reached 22.26 s, clr 0.2219 m |
| astar_known | 0 | reached 23.54 s, clr 0.2081 m | reached 23.98 s, clr 0.2212 m | reached 23.98 s, clr 0.2212 m | reached 23.54 s, clr 0.2081 m |
| lazy_thetastar_unknown | 1 | reached 33.76 s, clr 0.2062 m | collision None s, clr 0.1965 m | collision None s, clr 0.1965 m | reached 33.76 s, clr 0.2062 m |
| thetastar_known | 1 | reached 21.74 s, clr 0.2263 m | reached 21.78 s, clr 0.217 m | reached 21.78 s, clr 0.217 m | reached 21.74 s, clr 0.2263 m |
| astar_known | 1 | reached 22.92 s, clr 0.2189 m | reached 23.72 s, clr 0.2204 m | reached 23.72 s, clr 0.2204 m | reached 22.92 s, clr 0.2189 m |
| lazy_thetastar_unknown | 2 | reached 28.78 s, clr 0.2297 m | collision None s, clr 0.199 m | collision None s, clr 0.199 m | reached 28.78 s, clr 0.2297 m |
| thetastar_known | 2 | reached 21.88 s, clr 0.2293 m | reached 21.9 s, clr 0.2164 m | reached 21.9 s, clr 0.2164 m | reached 21.88 s, clr 0.2293 m |
| astar_known | 2 | reached 22.92 s, clr 0.2067 m | reached 23.66 s, clr 0.2235 m | reached 23.66 s, clr 0.2235 m | reached 22.92 s, clr 0.2067 m |
| lazy_thetastar_unknown | 3 | reached 29.68 s, clr 0.2173 m | collision None s, clr 0.1986 m | collision None s, clr 0.1986 m | reached 29.68 s, clr 0.2173 m |
| thetastar_known | 3 | reached 22.46 s, clr 0.2487 m | reached 22.3 s, clr 0.2146 m | reached 22.3 s, clr 0.2146 m | reached 22.46 s, clr 0.2487 m |
| astar_known | 3 | reached 23.8 s, clr 0.2112 m | reached 24.16 s, clr 0.2263 m | reached 24.16 s, clr 0.2263 m | reached 23.8 s, clr 0.2112 m |
| lazy_thetastar_unknown | 4 | reached 26.96 s, clr 0.2533 m | reached 23.9 s, clr 0.2249 m | reached 23.9 s, clr 0.2249 m | reached 26.96 s, clr 0.2533 m |
| thetastar_known | 4 | reached 21.1 s, clr 0.2479 m | reached 21.38 s, clr 0.2442 m | reached 21.38 s, clr 0.2442 m | reached 21.1 s, clr 0.2479 m |
| astar_known | 4 | reached 22.62 s, clr 0.2105 m | reached 22.9 s, clr 0.2141 m | reached 22.9 s, clr 0.2141 m | reached 22.62 s, clr 0.2105 m |

The drill's pack run (docs/drill-2026-11/pack_our_room.json) matches the `pack, shipped` column; the drill's Solver export (docs/drill-2026-11/quick_export.json) matches the `driver, inflate` column.

## After the fix: pack.py inflates by the pack radius

`python pack.py run results/pack_drill_our_room.json --workers 4 --out results/pack_drill_our_room_after` (105 runs, 4 workers). Seeds 0-4 vs the Solver export, fields outcome, time to goal, min clearance, path length:

| planner | seed | pack after fix | Solver | same |
|---|---|---|---|---|
| thetastar_known | 0 | reached 22.26 s, clr 0.2219 m | reached 22.26 s, clr 0.2219 m | yes |
| thetastar_known | 1 | reached 21.74 s, clr 0.2263 m | reached 21.74 s, clr 0.2263 m | yes |
| thetastar_known | 2 | reached 21.88 s, clr 0.2293 m | reached 21.88 s, clr 0.2293 m | yes |
| thetastar_known | 3 | reached 22.46 s, clr 0.2487 m | reached 22.46 s, clr 0.2487 m | yes |
| thetastar_known | 4 | reached 21.1 s, clr 0.2479 m | reached 21.1 s, clr 0.2479 m | yes |
| astar_known | 0 | reached 23.54 s, clr 0.2081 m | reached 23.54 s, clr 0.2081 m | yes |
| astar_known | 1 | reached 22.92 s, clr 0.2189 m | reached 22.92 s, clr 0.2189 m | yes |
| astar_known | 2 | reached 22.92 s, clr 0.2067 m | reached 22.92 s, clr 0.2067 m | yes |
| astar_known | 3 | reached 23.8 s, clr 0.2112 m | reached 23.8 s, clr 0.2112 m | yes |
| astar_known | 4 | reached 22.62 s, clr 0.2105 m | reached 22.62 s, clr 0.2105 m | yes |
| lazy_thetastar_unknown | 0 | reached 29.18 s, clr 0.215 m | reached 29.18 s, clr 0.215 m | yes |
| lazy_thetastar_unknown | 1 | reached 33.76 s, clr 0.2062 m | reached 33.76 s, clr 0.2062 m | yes |
| lazy_thetastar_unknown | 2 | reached 28.78 s, clr 0.2297 m | reached 28.78 s, clr 0.2297 m | yes |
| lazy_thetastar_unknown | 3 | reached 29.68 s, clr 0.2173 m | reached 29.68 s, clr 0.2173 m | yes |
| lazy_thetastar_unknown | 4 | reached 26.96 s, clr 0.2533 m | reached 26.96 s, clr 0.2533 m | yes |

15 of 15 runs identical.

## Pack verdicts, 35 seeds, before and after

| planner | drill pack (0.15 m inflation) | after fix (0.2 m inflation) |
|---|---|---|
| thetastar_known | 35/35 reached, 0 collisions, PASS | 35/35 reached, 0 collisions, PASS |
| astar_known | 35/35 reached, 0 collisions, PASS | 35/35 reached, 0 collisions, PASS |
| lazy_thetastar_unknown | 17/35 reached, 18 collisions, FAIL | 34/35 reached, 1 collision, FAIL |

lazy_thetastar_unknown still FAILs the bar after the fix: 1 collision (seed 34, min clearance 0.1996 m under the 0.2 m radius) and reached_rate NOT PROVEN (lower Wilson bound 0.85 < 0.9). The 5-seed Solver Quick sweep could not see this.
