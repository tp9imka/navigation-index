# Playground check: headless Chrome vs native CPython

Written by `node site/playground/results/measure_playground.mjs` on 2026-11-09. Input: synthetic (simulated layouts, vehicle, range sensors and VIO from samples/close-area-arena). Raw data: [playground_check.json](playground_check.json). Native reference: [native_parity.json](native_parity.json) from `native_parity.py`, which runs the same `DRIVER_PY` string from worker.js.

Browser: Chrome/140.0.7339.208 headless, Pyodide 314.0.7 (Python 3.14.2, numpy 2.4.6, scipy 1.18.0). Native: CPython 3.12.10, numpy 2.5.4, scipy 1.18.1, arm64.

## Load (fresh Chrome profile, cold HTTP cache)

- Python ready 5390 ms after the page script started; 22.2 MB downloaded (Resource Timing in the worker).
- Worker steps: Pyodide runtime 2301 ms, numpy + scipy + 23 hub files 1624 ms, imports 1452 ms (scipy.ndimage 692.1, arena 36.4, reactive 3.2, safety filter 451.7 ms).
- Planners loaded: straight, freest_beam, astar_known, astar_unknown, apf, vfh_plus. Filters: none, F2. Load errors: {}.

## Browser score = native score on the preset worlds: 15/15

Fields: outcome, time_to_goal_s, duration_s, min_clearance_m, path_length_m. Seed 0.

| world | planner | sensor | VIO fault | filter | browser: outcome / time_to_goal_s / duration_s / min_clearance_m / path_length_m | same as native | browser Python s | native Python s |
|---|---|---|---|---|---|---|---|---|
| random_0 | straight | ideal | truth | none | stuck / - / 20.3 / 0.3797 / 13.266 | yes | 0.187 | 0.091 |
| random_0 | freest_beam | ideal | truth | none | reached / 26.08 / 26.08 / 0.4702 / 24.504 | yes | 0.192 | 0.098 |
| random_0 | astar_known | ideal | truth | none | reached / 19.38 / 19.38 / 0.5647 / 23.838 | yes | 0.765 | 0.386 |
| random_0 | astar_unknown | ideal | truth | none | reached / 18.68 / 18.68 / 0.6432 / 23.947 | yes | 3.039 | 1.589 |
| random_0 | apf | ideal | truth | none | reached / 28.88 / 28.88 / 0.6356 / 24.9 | yes | 0.197 | 0.103 |
| random_0 | vfh_plus | ideal | truth | none | reached / 26.12 / 26.12 / 0.2332 / 24.478 | yes | 0.212 | 0.114 |
| random_0 | astar_known | ideal | jump | none | collision / - / 14.2 / 0.1497 / 15.888 | yes | 0.805 | 0.406 |
| random_0 | astar_known | ideal | jump | F2 | stuck / - / 32.88 / 0.3383 / 25.344 | yes | 1.38 | 0.866 |
| random_0 | freest_beam | ideal | bias | none | reached / 25.84 / 25.84 / 0.4728 / 24.569 | yes | 0.28 | 0.163 |
| random_0 | astar_known | ideal | dropout | F2 | reached / 20.6 / 20.6 / 0.8379 / 24.334 | yes | 1.034 | 0.593 |
| office_0 | astar_known | ideal | truth | none | reached / 22.74 / 22.74 / 0.2997 / 13.765 | yes | 0.905 | 0.484 |
| office_0 | freest_beam | ideal | truth | none | stuck / - / 13.04 / 0.434 / 7.115 | yes | 0.136 | 0.075 |
| office_0 | freest_beam | crazyflie | none | none | stuck / - / 13.1 / 0.4871 / 6.86 | yes | 0.177 | 0.094 |
| glass_office_0 | astar_unknown | crazyflie | truth | none | stuck / - / 10 / 0.8616 / 0 | yes | 0.677 | 0.433 |
| u_trap_0 | astar_known | crazyflie_bright | bias | F2 | stuck / - / 29.4 / 0.6862 / 25.73 | yes | 0.926 | 0.517 |

## Hand-drawn world (box drawn with pointer events)

One box from (7, 7) to (13, 12) on an empty 20 x 20 m area, A (1.5, 1.5), B (18.5, 18.5): {"type":"box","cx":10,"cy":9.5,"hx":3,"hy":2.5,"material":"matte","tag":"box"}. BFS free path: yes. Saved as [custom_world.json](custom_world.json).

| planner | browser: outcome / time_to_goal_s / duration_s / min_clearance_m / path_length_m | native: same? |
|---|---|---|
| astar_known | reached / 19.06 / 19.06 / 0.6116 / 25.172 | yes |
| freest_beam | reached / 29.96 / 29.96 / 0.3199 / 26.733 | yes |

## Page stays responsive while Python runs

During astar_unknown on random_0 (3.021 s of Python in the worker) the page drew 361 animation frames; longest gap between frames 9 ms, median 8 ms.

## Other runs shown in the screenshots

- Compare, random_0: A astar_known reached / 19.38 / 19.38 / 0.5647 / 23.838; B freest_beam reached / 26.08 / 26.08 / 0.4702 / 24.504. Page note: "A: same score as native CPython 3.12.10; B: same score as native CPython 3.12.10 on this preset (native_parity.json)."
- VIO jump on random_0, astar_known: no filter collision / - / 14.2 / 0.1497 / 15.888 (jump fired at 5.1 s); F2 stuck / - / 32.88 / 0.3383 / 25.344, F2 intervened on 26.8 % of 50 Hz steps.
- Phone 390 x 844 @2x: office_0 astar_known reached / 22.74 / 22.74 / 0.2997 / 13.765; document scroll width 390 px, body 390 px => no horizontal scroll.

- Nav link at 390 px: site/showcase.html scroll width 390 px, Playground link visible (right edge 333 px); site/index.html scroll width 390 px, Playground link visible (right edge 295 px).

Viewport screenshots (checked with `sips -g pixelHeight`): [pg_loading.png](pg_loading.png) 1280 x 900, [pg_compare_random0.png](pg_compare_random0.png) 1280 x 900, [pg_custom_drawn.png](pg_custom_drawn.png) 1280 x 900, [pg_jump_f2_dark.png](pg_jump_f2_dark.png) 1280 x 900, [pg_phone_390.png](pg_phone_390.png) 780 x 1688.

Console errors / warnings / exceptions: 0.
