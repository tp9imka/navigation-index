# Playground check: headless Chrome vs native CPython

Written by `node site/playground/results/measure_playground.mjs` on 2026-11-10. Input: synthetic (simulated layouts, vehicle, range sensors and VIO from samples/close-area-arena). Raw data: [playground_check.json](playground_check.json). Native reference: [native_parity.json](native_parity.json) from `native_parity.py`, which runs the same `DRIVER_PY` string from worker.js.

Browser: Chrome/140.0.7339.208 headless, Pyodide 314.0.7 (Python 3.14.2, numpy 2.4.6, scipy 1.18.0). Native: CPython 3.12.10, numpy 2.5.4, scipy 1.18.1, arm64.

## Load (fresh Chrome profile, cold HTTP cache)

- Python ready 7334 ms after the page script started; 22.3 MB downloaded (Resource Timing in the worker).
- Worker steps: Pyodide runtime 2557 ms, numpy + scipy + 42 hub files 3227 ms, imports 1537 ms (scipy.ndimage 677, arena 36.1, reactive 3.1, DWA / Bug / D* Lite / RRT* 227.9, safety filter 307.3 ms).
- Planners loaded: straight, freest_beam, astar_known, astar_unknown, apf, vfh_plus, dwa, dwa_mem, bug2, tangent_bug, dstar_lite, informed_rrt_star, thetastar_known, lazy_thetastar_known, lazy_thetastar_unknown, mppi, mppi_astar, hybrid_astar. Filters: none, F2. Load errors: {}.

## Browser score = native score on the preset worlds: 27/27

Fields: outcome, time_to_goal_s, duration_s, min_clearance_m, path_length_m. Seed 0.

| world | planner | sensor | VIO fault | filter | browser: outcome / time_to_goal_s / duration_s / min_clearance_m / path_length_m | same as native | browser Python s | native Python s |
|---|---|---|---|---|---|---|---|---|
| random_0 | straight | ideal | truth | none | stuck / - / 20.3 / 0.3797 / 13.266 | yes | 0.19 | 0.079 |
| random_0 | freest_beam | ideal | truth | none | reached / 26.08 / 26.08 / 0.4702 / 24.504 | yes | 0.191 | 0.092 |
| random_0 | astar_known | ideal | truth | none | reached / 19.38 / 19.38 / 0.5647 / 23.838 | yes | 0.785 | 0.341 |
| random_0 | astar_unknown | ideal | truth | none | reached / 18.7 / 18.7 / 0.6624 / 23.95 | yes | 3.065 | 1.372 |
| random_0 | apf | ideal | truth | none | reached / 28.88 / 28.88 / 0.6356 / 24.9 | yes | 0.193 | 0.099 |
| random_0 | vfh_plus | ideal | truth | none | reached / 26.12 / 26.12 / 0.2332 / 24.478 | yes | 0.213 | 0.105 |
| random_0 | astar_known | ideal | jump | none | collision / - / 14.2 / 0.1497 / 15.888 | yes | 0.806 | 0.36 |
| random_0 | astar_known | ideal | jump | F2 | stuck / - / 32.88 / 0.3383 / 25.344 | yes | 1.411 | 0.65 |
| random_0 | freest_beam | ideal | bias | none | reached / 25.84 / 25.84 / 0.4728 / 24.569 | yes | 0.277 | 0.141 |
| random_0 | astar_known | ideal | dropout | F2 | reached / 20.6 / 20.6 / 0.8379 / 24.334 | yes | 0.998 | 0.477 |
| office_0 | astar_known | ideal | truth | none | reached / 22.74 / 22.74 / 0.2997 / 13.765 | yes | 0.932 | 0.419 |
| office_0 | freest_beam | ideal | truth | none | stuck / - / 13.04 / 0.434 / 7.115 | yes | 0.135 | 0.068 |
| office_0 | freest_beam | crazyflie | none | none | stuck / - / 13.1 / 0.4871 / 6.86 | yes | 0.167 | 0.09 |
| glass_office_0 | astar_unknown | crazyflie | truth | none | collision / - / 55.28 / 0.1472 / 25.733 | yes | 2.73 | 1.402 |
| u_trap_0 | astar_known | crazyflie_bright | bias | F2 | stuck / - / 29.4 / 0.6862 / 25.73 | yes | 0.877 | 0.447 |
| random_0 | dwa | ideal | truth | none | reached / 43.68 / 43.68 / 0.2682 / 24.261 | yes | 1.098 | 0.568 |
| u_trap_0 | dwa_mem | ideal | truth | none | stuck / - / 28.94 / 0.2757 / 12.447 | yes | 2.69 | 1.337 |
| office_0 | bug2 | ideal | truth | none | stuck / - / 28.94 / 0.4578 / 11.281 | yes | 0.214 | 0.102 |
| forest_0 | tangent_bug | ideal | truth | none | reached / 25.68 / 25.68 / 0.3731 / 24.519 | yes | 0.242 | 0.122 |
| narrow_gap_0 | dstar_lite | ideal | truth | none | reached / 24.52 / 24.52 / 0.3288 / 25.187 | yes | 1.393 | 0.772 |
| office_0 | informed_rrt_star | ideal | truth | none | reached / 25.88 / 25.88 / 0.2762 / 13.578 | yes | 0.948 | 0.413 |
| maze_0 | astar_known | ideal | truth | none | reached / 41.26 / 41.26 / 0.5937 / 36.981 | yes | 4.302 | 1.99 |
| warehouse_0 | astar_known | ideal | truth | none | reached / 49.26 / 49.26 / 0.5151 / 34.978 | yes | 3.915 | 1.699 |
| maze_0 | bug2 | ideal | truth | none | reached / 105.22 / 105.22 / 0.4043 / 65.49 | yes | 0.603 | 0.29 |
| warehouse_0 | bug2 | ideal | truth | none | timeout / - / 120 / 0.4254 / 70.725 | yes | 0.61 | 0.301 |
| maze_0 | informed_rrt_star | ideal | truth | none | reached / 69.7 / 69.7 / 0.2754 / 33.637 | yes | 0.842 | 0.404 |
| office_0 | astar_unknown | ideal | truth | none | reached / 21.96 / 21.96 / 0.2892 / 13.764 | yes | 1.278 | 0.592 |

## VIO loss recovery: browser = native on 4/4 cases

Arms built by `pg_reloc.py` with `samples/close-area-relocalize/run_disambiguate.build`; A* known map behind the hover gate, ideal sensor. Compared: the score fields above plus, per loss event, trigger time, reason, result, recover s, error of the accepted pose to truth, moves flown.

| world | fault | seed | recovery | browser: outcome / time_to_goal_s / duration_s / min_clearance_m / path_length_m | events / accepted / wrong / open at end / moves | same as native | browser Python s | native Python s |
|---|---|---|---|---|---|---|---|---|
| reloc_demo_random_1_97 | jump | 1 | single | reached / 21.78 / 21.78 / 0.5182 / 24.151 | 6 / 6 / 1 / 0 / 0 | yes | 1.061 | 0.445 |
| reloc_demo_random_1_97 | jump | 1 | multi | stuck / - / 22.88 / 0.853 / 17.66 | 2 / 1 / 0 / 1 / 0 | yes | 1.247 | 0.586 |
| reloc_demo_random_1_97 | jump | 1 | multi_ig | reached / 20.34 / 20.34 / 0.6982 / 24.35 | 2 / 2 / 0 / 0 / 1 | yes | 0.979 | 0.449 |
| u_trap_0 | dropout | 0 | multi_ig | reached / 21.76 / 21.76 / 0.6216 / 24.609 | 6 / 6 / 0 / 0 / 1 | yes | 0.822 | 0.39 |

Compare all arms, reloc_demo_random_1_97, seed 1, jump ([pg_reloc_arms.png](pg_reloc_arms.png), t 13.6 s):

| arm | outcome | time to B s | events | accepted | wrong commits | open at end | moves | first recover s |
|---|---|---|---|---|---|---|---|---|
| none | reached | 18.7 | 0 | 0 | 0 | 0 | 0 | - |
| single | reached | 21.78 | 6 | 6 | 1 | 0 | 0 | 0.2 |
| multi | stuck | - | 2 | 1 | 0 | 1 | 0 | 0.4 |
| multi_ig | reached | 20.34 | 2 | 2 | 0 | 0 | 1 | 0.4 |

Verdict strip at 13.6 s: none nominal, single wrong, multi hovering, multi+IG hovering. Page note: "single: same score and loss events as native CPython 3.12.10; multi: same score and loss events as native CPython 3.12.10; multi+IG: same score and loss events as native CPython 3.12.10 on this world (native_parity.json)."

## Blocked CDN (cdn.jsdelivr.net mapped to 127.0.0.1, fresh profile)

- `?pyodide=cdn`: load failed after 9.058 s, Retry button visible: yes. Attempts: manifest.json #1 ok (10 ms), Pyodide runtime #1 failed (1 ms), Pyodide runtime #2 failed (1 ms), Pyodide runtime #3 failed (1 ms). Message: "load failed: Pyodide runtime: 3 of 3 attempts failed, last error: Failed to fetch dynamically imported module: https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs?attempt=3. Needs cdn.jsdelivr.net, or a local Pyodide folder (README: Offline / blocked CDN)." ([pg_blocked_retry.png](pg_blocked_retry.png)).
- Retry pressed: new worker, attempt 2; 3.004 s later: "Pyodide runtime: attempt 2 of 3 failed (Failed to fetch dynamically imported module: https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs?attempt=2). Trying again in 6 s..."
- site/playground/pyodide-local/ not present: local load not measured in this run.
- Console errors / warnings / exceptions in this profile: 0.

## Hand-drawn world (box drawn with pointer events)

One box from (7, 7) to (13, 12) on an empty 20 x 20 m area, A (1.5, 1.5), B (18.5, 18.5): {"type":"box","cx":10,"cy":9.5,"hx":3,"hy":2.5,"material":"matte","tag":"box"}. BFS free path: yes. Saved as [custom_world.json](custom_world.json).

| planner | browser: outcome / time_to_goal_s / duration_s / min_clearance_m / path_length_m | native: same? |
|---|---|---|
| astar_known | reached / 19.06 / 19.06 / 0.6116 / 25.172 | yes |
| freest_beam | reached / 29.96 / 29.96 / 0.3199 / 26.733 | yes |

## Page stays responsive while Python runs

During astar_unknown on random_0 (2.971 s of Python in the worker) the page drew 355 animation frames; longest gap between frames 10 ms, median 8 ms.

## Shareable link

World: the hand-drawn box world above. Config A {"planner":"tangent_bug","preset":"crazyflie","fault":"none","filter":"none","recovery":"none","seed":7}, B {"planner":"dstar_lite","preset":"crazyflie","fault":"none","filter":"F2","recovery":"none","seed":7}. Link length 491 characters (world JSON 267 characters). Copy link button: address bar holds the link: yes; clipboard holds the link: yes. Button message: "Link copied (491 characters). Opening it restores this world and config and runs it."

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

- Compare, random_0: A astar_known reached / 19.38 / 19.38 / 0.5647 / 23.838; B freest_beam reached / 26.08 / 26.08 / 0.4702 / 24.504. Page note: "A: same score as native CPython 3.12.10; B: same score as native CPython 3.12.10 on this world (native_parity.json)."
- VIO jump on random_0, astar_known: no filter collision / - / 14.2 / 0.1497 / 15.888 (jump fired at 5.1 s); F2 stuck / - / 32.88 / 0.3383 / 25.344, F2 intervened on 26.8 % of 50 Hz steps.
- Phone 390 x 844 @2x: office_0 astar_known reached / 22.74 / 22.74 / 0.2997 / 13.765; document scroll width 390 px, body 390 px => no horizontal scroll.

- Nav link at 390 px: site/showcase.html scroll width 390 px, Playground link NOT fully visible (right edge null px); site/index.html scroll width 390 px, Playground link NOT fully visible (right edge null px).

Viewport screenshots (checked with `sips -g pixelHeight`): [pg_loading.png](pg_loading.png) 1280 x 900, [pg_compare_random0.png](pg_compare_random0.png) 1280 x 900, [pg_custom_drawn.png](pg_custom_drawn.png) 1280 x 900, [pg_jump_f2_dark.png](pg_jump_f2_dark.png) 1280 x 900, [pg_shared_link.png](pg_shared_link.png) 1280 x 900, [pg_phone_390.png](pg_phone_390.png) 780 x 1688, [pg_reloc_arms.png](pg_reloc_arms.png) 1280 x 900, [pg_blocked_retry.png](pg_blocked_retry.png) 1280 x 900.

Console errors / warnings / exceptions: 0.
