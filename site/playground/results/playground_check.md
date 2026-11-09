# Playground check: headless Chrome vs native CPython

Written by `node site/playground/results/measure_playground.mjs` on 2026-11-09. Input: synthetic (simulated layouts, vehicle, range sensors and VIO from samples/close-area-arena). Raw data: [playground_check.json](playground_check.json). Native reference: [native_parity.json](native_parity.json) from `native_parity.py`, which runs the same `DRIVER_PY` string from worker.js.

Browser: Chrome/140.0.7339.208 headless, Pyodide 314.0.7 (Python 3.14.2, numpy 2.4.6, scipy 1.18.0). Native: CPython 3.12.10, numpy 2.5.4, scipy 1.18.1, arm64.

## Load (fresh Chrome profile, cold HTTP cache)

- Python ready 5705 ms after the page script started; 22.2 MB downloaded (Resource Timing in the worker).
- Worker steps: Pyodide runtime 2823 ms, numpy + scipy + 30 hub files 1379 ms, imports 1408 ms (scipy.ndimage 659.7, arena 34.5, reactive 3, DWA / Bug / D* Lite / RRT* 11.6, safety filter 439.9 ms).
- Planners loaded: straight, freest_beam, astar_known, astar_unknown, apf, vfh_plus, dwa, dwa_mem, bug2, tangent_bug, dstar_lite, informed_rrt_star. Filters: none, F2. Load errors: {}.

## Browser score = native score on the preset worlds: 21/21

Fields: outcome, time_to_goal_s, duration_s, min_clearance_m, path_length_m. Seed 0.

| world | planner | sensor | VIO fault | filter | browser: outcome / time_to_goal_s / duration_s / min_clearance_m / path_length_m | same as native | browser Python s | native Python s |
|---|---|---|---|---|---|---|---|---|
| random_0 | straight | ideal | truth | none | stuck / - / 20.3 / 0.3797 / 13.266 | yes | 0.187 | 0.093 |
| random_0 | freest_beam | ideal | truth | none | reached / 26.08 / 26.08 / 0.4702 / 24.504 | yes | 0.186 | 0.116 |
| random_0 | astar_known | ideal | truth | none | reached / 19.38 / 19.38 / 0.5647 / 23.838 | yes | 0.737 | 0.375 |
| random_0 | astar_unknown | ideal | truth | none | reached / 18.68 / 18.68 / 0.6432 / 23.947 | yes | 2.927 | 1.713 |
| random_0 | apf | ideal | truth | none | reached / 28.88 / 28.88 / 0.6356 / 24.9 | yes | 0.192 | 0.118 |
| random_0 | vfh_plus | ideal | truth | none | reached / 26.12 / 26.12 / 0.2332 / 24.478 | yes | 0.204 | 0.152 |
| random_0 | astar_known | ideal | jump | none | collision / - / 14.2 / 0.1497 / 15.888 | yes | 0.781 | 0.415 |
| random_0 | astar_known | ideal | jump | F2 | stuck / - / 32.88 / 0.3383 / 25.344 | yes | 1.307 | 0.791 |
| random_0 | freest_beam | ideal | bias | none | reached / 25.84 / 25.84 / 0.4728 / 24.569 | yes | 0.274 | 0.157 |
| random_0 | astar_known | ideal | dropout | F2 | reached / 20.6 / 20.6 / 0.8379 / 24.334 | yes | 0.977 | 0.533 |
| office_0 | astar_known | ideal | truth | none | reached / 22.74 / 22.74 / 0.2997 / 13.765 | yes | 0.873 | 0.452 |
| office_0 | freest_beam | ideal | truth | none | stuck / - / 13.04 / 0.434 / 7.115 | yes | 0.131 | 0.084 |
| office_0 | freest_beam | crazyflie | none | none | stuck / - / 13.1 / 0.4871 / 6.86 | yes | 0.168 | 0.099 |
| glass_office_0 | astar_unknown | crazyflie | truth | none | stuck / - / 10 / 0.8616 / 0 | yes | 0.623 | 0.404 |
| u_trap_0 | astar_known | crazyflie_bright | bias | F2 | stuck / - / 29.4 / 0.6862 / 25.73 | yes | 0.88 | 0.482 |
| random_0 | dwa | ideal | truth | none | reached / 43.68 / 43.68 / 0.2682 / 24.261 | yes | 1.018 | 0.601 |
| u_trap_0 | dwa_mem | ideal | truth | none | stuck / - / 28.94 / 0.2757 / 12.447 | yes | 2.383 | 1.5 |
| office_0 | bug2 | ideal | truth | none | stuck / - / 28.94 / 0.4578 / 11.281 | yes | 0.196 | 0.109 |
| forest_0 | tangent_bug | ideal | truth | none | reached / 25.68 / 25.68 / 0.3731 / 24.519 | yes | 0.235 | 0.133 |
| narrow_gap_0 | dstar_lite | ideal | truth | none | reached / 24.52 / 24.52 / 0.3288 / 25.187 | yes | 1.28 | 0.824 |
| office_0 | informed_rrt_star | ideal | truth | none | reached / 25.88 / 25.88 / 0.2762 / 13.578 | yes | 0.82 | 0.434 |

## Hand-drawn world (box drawn with pointer events)

One box from (7, 7) to (13, 12) on an empty 20 x 20 m area, A (1.5, 1.5), B (18.5, 18.5): {"type":"box","cx":10,"cy":9.5,"hx":3,"hy":2.5,"material":"matte","tag":"box"}. BFS free path: yes. Saved as [custom_world.json](custom_world.json).

| planner | browser: outcome / time_to_goal_s / duration_s / min_clearance_m / path_length_m | native: same? |
|---|---|---|
| astar_known | reached / 19.06 / 19.06 / 0.6116 / 25.172 | yes |
| freest_beam | reached / 29.96 / 29.96 / 0.3199 / 26.733 | yes |

## Page stays responsive while Python runs

During astar_unknown on random_0 (2.931 s of Python in the worker) the page drew 350 animation frames; longest gap between frames 10 ms, median 8 ms.

## Shareable link

World: the hand-drawn box world above. Config A {"planner":"tangent_bug","preset":"crazyflie","fault":"none","filter":"none","seed":7}, B {"planner":"dstar_lite","preset":"crazyflie","fault":"none","filter":"F2","seed":7}. Link length 461 characters (world JSON 267 characters). Copy link button: address bar holds the link: yes; clipboard holds the link: yes. Button message: "Link copied (461 characters). Opening it restores this world and config and runs it."

Opened in a second headless Chrome with a fresh profile (new --user-data-dir, cold cache): world identical yes, config identical yes, ran automatically yes, both scores identical to the source tab yes. Page message: "World and config restored from the link (1 obstacles).". Screenshot: [pg_shared_link.png](pg_shared_link.png).

| run | source tab: outcome / time_to_goal_s / duration_s / min_clearance_m / path_length_m | fresh profile: same? |
|---|---|---|
| A | collision / - / 8.5 / 0.1499 / 7.643 | yes |
| B | reached / 28.4 / 28.4 / 0.5954 / 27.397 | yes |

Broken link (`#w=notdeflate`): "This link does not hold a readable world (w= is not deflate + base64url data). Loaded the default preset random_0." World family after fallback: random.

Link length per preset world (characters of the `w=` value vs the world JSON):

| preset | world JSON chars | w= chars |
|---|---|---|
| office_0 | 3330 | 863 |
| warehouse_0 | 2829 | 606 |
| forest_0 | 6966 | 1610 |
| maze_0 | 4346 | 691 |
| glass_office_0 | 2213 | 723 |
| random_0 | 906 | 506 |
| u_trap_0 | 764 | 463 |
| narrow_gap_0 | 609 | 426 |

Console errors / warnings / exceptions in the fresh profile: 0.

## Other runs shown in the screenshots

- Compare, random_0: A astar_known reached / 19.38 / 19.38 / 0.5647 / 23.838; B freest_beam reached / 26.08 / 26.08 / 0.4702 / 24.504. Page note: "A: same score as native CPython 3.12.10; B: same score as native CPython 3.12.10 on this preset (native_parity.json)."
- VIO jump on random_0, astar_known: no filter collision / - / 14.2 / 0.1497 / 15.888 (jump fired at 5.1 s); F2 stuck / - / 32.88 / 0.3383 / 25.344, F2 intervened on 26.8 % of 50 Hz steps.
- Phone 390 x 844 @2x: office_0 astar_known reached / 22.74 / 22.74 / 0.2997 / 13.765; document scroll width 390 px, body 390 px => no horizontal scroll.

- Nav link at 390 px: site/showcase.html scroll width 390 px, Playground link visible (right edge 277 px); site/index.html scroll width 390 px, Playground link visible (right edge 295 px).

Viewport screenshots (checked with `sips -g pixelHeight`): [pg_loading.png](pg_loading.png) 1280 x 900, [pg_compare_random0.png](pg_compare_random0.png) 1280 x 900, [pg_custom_drawn.png](pg_custom_drawn.png) 1280 x 900, [pg_jump_f2_dark.png](pg_jump_f2_dark.png) 1280 x 900, [pg_shared_link.png](pg_shared_link.png) 1280 x 900, [pg_phone_390.png](pg_phone_390.png) 780 x 1688.

Console errors / warnings / exceptions: 0.
