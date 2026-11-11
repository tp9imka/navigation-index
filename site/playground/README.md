# Arena playground: the close-area arena in the browser (Pyodide)

Open [index.html](index.html) (served from the repo root: `python3 -m http.server 8000`, then
`http://localhost:8000/site/playground/`). Draw or load an arena, drag A and B, pick a planner,
sensor preset, VIO fault, VIO loss recovery and safety filter, optionally your drone's radius, top speed
and yaw (**Advanced: your drone**), press Run, and watch the replay with a score panel. Press **Copy link** to share the world and config: opening the link restores both and runs.
If the first load fails (no network, blocked or slow cdn.jsdelivr.net), press **Retry**, or see
[Offline / blocked CDN](#offline--blocked-cdn).

The page runs the hub's real Python code with Pyodide in a Web Worker: the arena
([samples/close-area-arena](../../samples/close-area-arena/README.md)), APF and VFH+
([close-area-planner-reactive](../../samples/close-area-planner-reactive/README.md)), DWA, Bug2 and
TangentBug ([close-area-planner-dwa-bug](../../samples/close-area-planner-dwa-bug/README.md)), D* Lite
([close-area-planner-dstar](../../samples/close-area-planner-dstar/README.md)), Informed RRT*
([close-area-planner-sampling](../../samples/close-area-planner-sampling/README.md)), Theta* and Lazy Theta*
([close-area-planner-thetastar](../../samples/close-area-planner-thetastar/README.md)), MPPI
([close-area-planner-mppi](../../samples/close-area-planner-mppi/README.md)), Hybrid A*
([close-area-planner-hybrid-astar](../../samples/close-area-planner-hybrid-astar/README.md)), the F2 filter
([close-area-safety-filter](../../samples/close-area-safety-filter/README.md)) and relocalization after
VIO loss ([close-area-relocalize](../../samples/close-area-relocalize/README.md)). Nothing is re-implemented
in JS. Everything is **synthetic**: a simulated 2.5D point-mass vehicle, simulated range sensors and
a simulated VIO. No number here is a flight result.

## Your drone: radius, top speed, yaw

Under the seed field, **Advanced: your drone** (closed by default) holds three controls. They apply to
configs A and B, go into `readCfg` and into the copied link.

| Control | Range | Run message | Link param |
|---|---|---|---|
| Radius, m | 0.05-0.6 (default 0.15) | `cfg.vehicle.radius_m` | `radius` |
| Max speed v_max, m/s | 0.1-5 (default 2) | `cfg.vehicle.v_max` | `v_max` |
| Yaw | fixed (default), look where you go | `cfg.yaw` | `yaw` |

`cfg.vehicle` is sent only when radius or v_max differ from the default (a_max 3 m/s^2 and tau 0.15 s
stay at `run.DEFAULTS`), and `cfg.yaw` only when it is not `fixed`. So a run with the panel untouched
sends the same message as before and gets the same result. The link carries the three params only
when they are not the default; a value outside the range in a link is ignored with a message, a value
typed in the form is clamped. The score table shows the radius, v_max and yaw each run flew. The
Sensor select also offers `depth_cam_87` (30 beams over 87 deg forward, 0.3-5 m, D435i class) and
`lidar_2d` (360 beams, 12 m, RPLIDAR A1 class) from `presets.py`.

**Radius rule.** Every planner inflates obstacles by the flown radius. The planner samples hardcode the
0.15 m arena radius, so `DRIVER_PY` (`radius_override`) sets each radius constant to radius_m + (its
shipped value - 0.15 m) for that run and restores it after, also after an error. The planners' own
margins on top of the radius stay as shipped. At 0.15 m nothing is touched. Sample files are not edited.

| Set per run | Planners |
|---|---|
| `astar_esdf.RADIUS`, `astar_esdf.CARROT_CLEAR_M` (RADIUS + 0.10 m) | A* known / unknown map, D* Lite, Theta*, Lazy Theta*, the MPPI-A* guide path, the relocalization arms (all read `astar_esdf.RADIUS` at run time; same module object, checked) |
| `hybrid_astar.RADIUS`, `rrt_star.RADIUS` (copies made at import) | Hybrid A*, Informed RRT* |
| `mppi.R_COLL`, `mppi.D_SAFE` (0.25 m beyond the radius as shipped) | MPPI, MPPI on the A* path |
| `dwa.RADIUS`, `bug.RADIUS` | DWA, DWA + memory, Bug2, TangentBug |
| instance: `APF.radius`, `VFHPlus.r_rs` = radius + d_s 0.1 m | APF, VFH+ |

Not reached: **straight** (flies the line to B, no obstacle model) and **freest_beam** (fixed 1.0 m
free-beam and 0.6 m repulsion thresholds, no radius term) behave as before at any radius. Also unchanged:
speed laws that read clearance (`astar_esdf.V_CLEAR_STOP_M` 0.25 m and the like) and the relocalizer's
0.35 m hypothesis motion check (`disambiguate.CLEAR_M`). The result's `inflation` field lists what was set.
The arena itself already used the radius for collision, scoring and the free-path check.

Narrow gap, before (planners at 0.15 m, native `inflate=False`) and after, seed 0, truth pose, ideal
sensor ([playground_custom.md](results/playground_custom.md), browser = native on all 7 cases; synthetic):

| planner | radius m | free path at the radius | before: outcome / time to B s / min clearance m / path m | after |
|---|---|---|---|---|
| mppi_astar | 0.25 | yes | reached / 21.6 / 0.2652 / 25.194 | reached / 40 / 0.3595 / 45.096 |
| mppi_astar | 0.35 | no | collision / - / 0.3467 / 12.999 | stuck / - / 0.6173 / 33.293 |
| astar_unknown | 0.25 | yes | reached / 24.98 / 0.301 / 25.195 | reached / 53.24 / 0.3264 / 55.086 |
| astar_unknown | 0.35 | no | collision / - / 0.3484 / 12.956 | stuck / - / 0.418 / 34.379 |

At 0.25 m both planners now keep more clearance and take the long way round (about twice the path) instead
of threading the gap with 0.0152 m (MPPI) to spare. At 0.35 m the BFS finds no free path, B is unreachable,
and both now stop short (stuck) instead of flying into the gap and colliding. One layout: an example, not a rate.

**Yaw.** `cfg.yaw = "look_where_you_go"` turns the vehicle toward its commanded velocity (gain 2 /s, cap
1 rad/s, toward B below 0.2 m/s). Default `fixed` for every sensor. In the first version of this panel the policy was on by default
for sensors under 360 deg; it was slower than fixed yaw in 4 of 4 office_0 / maze_0 runs with the depth
camera ([custom_sensor_0.md](../../samples/close-area-arena/results/custom_sensor_0.md)), so it is now opt-in.
Example: office_0, MPPI on the A* path, depth_cam_87: reached in 14.14 s fixed, 15.88 s look where you go
(browser = native). The result carries `yaw` and `config.yaw`.

Checks: [native_parity_custom.json](results/native_parity_custom.json) 11/11 (the sensor dict = the preset
name; driver = `run.run_one` with the override; constants restored and a default run unchanged after the
custom-radius runs; `cfg.yaw` absent = the original fixed-yaw path; an explicit 0.15 m vehicle = none).
In the browser ([playground_custom.md](results/playground_custom.md)): 7/7 cases, 4/4 refusals (incl.
`cfg.yaw` "spin"), 6/6 page checks (sensor select, panel => `readCfg` and link, link => panel, clamp).

## A* unknown map is geofenced (fix)

The playground's `astar_unknown` used the shipped log-odds map corner at (-2.5, -2.5). office_0's B is at
(-6.75, -7.39), outside that map, so the planner never moved (stuck, 0.0 m path). It now uses the
benchmark's construction (`GeofencedAStar` in `DRIVER_PY`, same as `close-area-benchmark/bench.py`): map
corner = area corner - 2 m, same 24 m size, as D* Lite already was. Changed rows in
[native_parity.json](results/native_parity.json) (browser = native for each, [playground_check.md](results/playground_check.md)):

| world | sensor | before: outcome / time to B s / duration s / min clearance m / path m | after |
|---|---|---|---|
| random_0 | ideal | reached / 18.68 / 18.68 / 0.6432 / 23.947 | reached / 18.7 / 18.7 / 0.6624 / 23.95 |
| glass_office_0 | crazyflie | stuck / - / 10 / 0.8616 / 0 | collision / - / 55.28 / 0.1472 / 25.733 |
| office_0 (new row) | ideal | (not a case; stuck, 0.0 m path in custom_sensor_0.md) | reached / 21.96 / 21.96 / 0.2892 / 13.764 |

glass_office_0 with the Crazyflie sensor now flies and then hits glass it cannot see (min clearance
0.1472 m, under the 0.15 m radius). office_0 against `matrix_0.json` (layout 0, ideal, generated world):
reached / 22.0 / 22.0 / 0.2892 / 13.758 there, same outcome and clearance; time and path differ by the
4-decimal JSON rounding (check B gives the matrix numbers exactly on the generated world, check E is
identical to `bench.py`'s factory on the same JSON world). The Advisor's note about the map corner was
updated ([data/advisor.json](data/advisor.json), via `results/build_advisor_loop73.py`).

## VIO loss recovery

The **VIO loss recovery** select (per config) is active when the VIO fault is jump or dropout:

| Option | Arm in samples/close-area-relocalize | What it does |
|---|---|---|
| none | `experiment.py` arm `estimator` | VIO EKF only, no relocalizer |
| single | (b) `single` | match the scan against the known map, commit to the best match at once |
| multi | (c) `multi` | keep up to 5 hypotheses, `RatioPersistence`, hover until one wins |
| multi + info-gain move | (f) `multi_ig` | (c) plus, after 1 s without an accept, a 1 or 2 m move chosen by expected entropy reduction (up to 4 per event) |

[pg_reloc.py](pg_reloc.py) builds each arm with `run_disambiguate.build(arm, world, estimator, seed, index)`,
the call `run_disambiguate.py` makes, so the pose source and planner (A* + ESDF known map behind the
hover gate) are the sample's own. With an arm selected the planner is fixed to A* known map and the
filter to none (the sample has no F2 arm). The relocalizer reads its own 72-ray, 6 m scan (the
sample's model, rng `[seed, index, 4301]`), whatever the sensor preset. pg_reloc.py only records:
the hypotheses each scan produced, a status per 10 Hz frame, and `run_disambiguate.extra()`.

- **Ghost markers**: rings at each hypothesis from the last 2 s, fainter when older or lower in score;
  the current set has dots and scores. Blue arrow = an info-gain move. Green ring = accepted pose,
  dark ring with a cross = wrong commit.
- **Verdict strip**: one row per run, coloured per frame: lost (red: settling or no hypothesis
  explains the scan), hovering (ambiguous or pending), info-gain move, accepted (re-anchored),
  wrong commit (accepted more than 0.5 m from truth, the sample's own scoring), VIO nominal (grey).
  For arm none it shows lost only while the estimator reports quality 0.
- **Compare all recovery arms**: runs config A with none, single, multi and multi + info-gain on one
  world and overlays the four runs (range beams of the first run only).
- The preset menu adds **VIO-loss demo: random seed 1, layout 97 (jump)**: `world.make_world("random", 1, 97)`
  through `world_json` ([results/reloc_demo_random_1_97.json](results/reloc_demo_random_1_97.json),
  written by `native_parity.py`), the H1 case of
  [live-demo-script-close-area.md](../../templates/presenting/live-demo-script-close-area.md). Loading it sets seed 1, jump
  and compare all arms.

Result on the demo world (synthetic, [results/playground_check.md](results/playground_check.md)):
single commits 0.6281 m wrong after the 13.0 s trigger and reaches B in 21.78 s; multi stays
ambiguous and ends stuck at 22.88 s; multi + info-gain flies 1 move, accepts 1.7 s after the trigger
0.0748 m from truth, and reaches B in 20.34 s. none reaches B in 18.7 s with a 0.6562 m max pose
error. **Browser = native on 4/4 relocalization cases** (3 arms on the demo world, multi + info-gain
on u_trap_0 with dropout): score fields and every loss event (trigger time, reason, result, recover
s, error, moves). Natively the driver also equals `run.run_one` + `run_disambiguate.build` on the
same JSON world in 4/4 (check G in [native_parity.json](results/native_parity.json)). Against the
sample's published `disamb_random_1.json` run 97 (generated world, not JSON): multi and
multi + info-gain identical, single differs in min clearance only (0.5182 m here, 0.5183 m there),
the 4-decimal JSON rounding of check B below. Screenshot: [pg_reloc_arms.png](results/pg_reloc_arms.png).

## Loading: retries and the Retry button

Dry-run blocker 7 ([docs/cold-start-drill.md](../../docs/cold-start-drill.md)): a cold load stalled 122.5 s and
failed with "Failed to fetch"; there was no retry. Now `worker.js` runs each load step as a named
step with 3 attempts and waits of 2 s and 6 s between them: `manifest.json`, `Pyodide runtime`
(`pyodide.mjs` + `loadPyodide`; a retry imports `pyodide.mjs?attempt=N`, because a failed module import
stays cached under its URL), `hub .py files` (refetches only the missing ones) and
`numpy + scipy wheels` (checks `loadedPackages`; after a timed-out attempt it starts a fresh runtime,
since the hung call may hold Pyodide's package lock). Timeouts: 20 s, 120 s, 30 s and 180 s. The
load line shows each failed attempt and the wait. When all attempts fail, or the load runs over 45 s,
a **Retry** button appears; it terminates the worker (and any fetch that still hangs) and starts a
new one.

Measured (headless Chrome 140, cdn.jsdelivr.net mapped to 127.0.0.1, so every CDN request is refused,
[playground_check.md](results/playground_check.md)): 3 attempts of `Pyodide runtime` failed, the page
showed the error and the Retry button 8.9 s after navigation
([pg_blocked_retry.png](results/pg_blocked_retry.png)); pressing Retry started a new worker that
retried again. The 122 s stall itself (a fetch that hangs, then fails) was not reproduced.

## Offline / blocked CDN

One command does all of this: `python3 tools/offline_browser_kit.py prepare` vendors Pyodide with sha256 checks,
`verify` checks the playground and the Solver with the CDN blocked, `bundle` writes a zip that runs
with `python3 serve.py` ([first-three-hours](../../docs/first-three-hours.md)). The manual steps below do the same by hand.

The playground needs Pyodide 314.0.7, numpy and scipy. By default it loads them from
cdn.jsdelivr.net. To run without the CDN (venue Wi-Fi that blocks it, or no network), vendor them
into `site/playground/pyodide-local/` once, while you still have network (about 30 MB on disk,
7 files):

```sh
mkdir -p site/playground/pyodide-local && cd site/playground/pyodide-local
B=https://cdn.jsdelivr.net/pyodide/v314.0.7/full/
for f in pyodide.mjs pyodide.asm.mjs pyodide.asm.wasm python_stdlib.zip pyodide-lock.json; do curl -fsSLO "$B$f"; done
python3 -c "import json; P = json.load(open('pyodide-lock.json'))['packages']; print(P['numpy']['file_name']); print(P['scipy']['file_name'])" \
  | while read w; do curl -fsSLO "$B$w"; done
cd ../../..
python3 -m http.server 8000     # then http://localhost:8000/site/playground/
```

Do not commit the folder (the wheels are 17 MB). Pyodide checks each wheel against the sha256 in
`pyodide-lock.json` when it loads it. Note: Pyodide 314 has `pyodide.asm.mjs`, not `pyodide.asm.js`
(the `.js` name gives 404).

Manifest options ([manifest.json](manifest.json)):

| Key | Value | Meaning |
|---|---|---|
| `pyodide_base` | `https://cdn.jsdelivr.net/pyodide/v314.0.7/full/` | the CDN folder |
| `pyodide_local` | `pyodide-local/` | the vendored folder, relative to manifest.json |
| `pyodide_source` | `auto` (default), `cdn` or `local` | `auto`: the local folder when `<pyodide_local>pyodide.mjs` answers a HEAD request, else the CDN. `local`: fail with a message if the folder is missing |

The page URL overrides `pyodide_source`: `index.html?pyodide=cdn`, `?pyodide=local` or `?pyodide=auto`.
The status line under the page says which source loaded.

Measured with the folder filled by the commands above and the CDN blocked as in the previous section:
`?pyodide=auto` loaded from the local folder, ready 3.7 s after navigation, 0 successful jsdelivr
requests, and the demo `single` case gave the same score and events as native. The folder was
deleted after the check.

## Result

Source: [results/playground_check.md](results/playground_check.md), written by
`results/measure_playground.mjs` in headless Chrome 140 on an Apple M3 Max, against
[results/native_parity.json](results/native_parity.json) from `results/native_parity.py` (CPython 3.12.10).
Input type: synthetic.

- **18 planners in the browser: 18 of the 21 benchmarked rows** of
  [close-area-benchmark](../../samples/close-area-benchmark/README.md). Added on 2026-11-10: Theta* and Lazy
  Theta* (known map), Lazy Theta* (unknown map, geofenced), MPPI (goal only), MPPI on the unknown-map A*
  path and Hybrid A* (unknown map, geofenced); see "New planners" below. Left out of the
  playground: the benchmark row `thetastar_unknown` (plain Theta* without a map; its sample README
  reports slow replans, so only the Lazy variant is offered). Added before them (2026-11-09): DWA, DWA + 3 s
  memory, Bug2, TangentBug, D* Lite (unknown map) and Informed RRT* (known map). The other 2 rows left out:
  `astar_mpc` needs osqp, and the Pyodide 314.0.7 `pyodide-lock.json` lists 357 packages but no osqp
  (only clarabel and cvxpy-base, checked 2026-11-09); `astar_unknown_f2` is not a separate planner
  here. A* unknown map + filter F2 is the same combination: now both A* unknown maps are
  geofenced (see "A* unknown map is geofenced").
- **Browser = native on 21/21 preset cases** (27/27 in the re-run after the drone-panel change, which added office_0 A* unknown
  map and the run-time-limit cases; [playground_check.md](results/playground_check.md)) (outcome, time to goal, duration, min clearance, path
  length; seed 0). Example: random_0, A* known map => reached in 19.38 s, min clearance 0.5647 m,
  path 23.838 m in both. The cases cover all 12 planners, all 3 sensor presets, faults none / jump /
  bias / dropout and F2. The 6 new planners, one preset each:

  | world | planner | outcome / time to goal s / min clearance m / path m (browser = native) | browser Python s | native Python s |
  |---|---|---|---|---|
  | random_0 | dwa | reached / 43.68 / 0.2682 / 24.261 | 1.018 | 0.601 |
  | u_trap_0 | dwa_mem | stuck (28.94 s) / - / 0.2757 / 12.447 | 2.383 | 1.5 |
  | office_0 | bug2 | stuck (28.94 s) / - / 0.4578 / 11.281 | 0.196 | 0.109 |
  | forest_0 | tangent_bug | reached / 25.68 / 0.3731 / 24.519 | 0.235 | 0.133 |
  | narrow_gap_0 | dstar_lite | reached / 24.52 / 0.3288 / 25.187 | 1.28 | 0.824 |
  | office_0 | informed_rrt_star | reached / 25.88 / 0.2762 / 13.578 | 0.82 | 0.434 |

- **Shareable link works in a fresh profile.** A hand-drawn world with compare mode (TangentBug vs
  D* Lite + F2, Crazyflie sensor, VIO on, seed 7) gave a 491-character link (461 before the recovery param was added). A second headless Chrome
  with a new profile and cold cache opened it, restored the identical world and config, ran by
  itself, and got both scores identical to the source tab (A collision at 8.5 s, B reached in 28.4 s).
  The `w=` value is 426-1610 characters for the 8 presets (forest_0 is the longest, 6966 characters
  of JSON). The Copy link button put the link in the clipboard and the address bar. A broken `w=`
  shows a message and loads random_0.
- A box drawn with real pointer events on an empty world: A* known map and freest_beam give the same
  score in the browser and in native CPython on the saved [custom_world.json](results/custom_world.json).
- The page stays responsive: during a 3.2 s A* unknown-map run in the worker, the longest gap
  between animation frames was 10 ms.
- Cold load in a fresh profile: Python ready 5.6 s after the page script starts, 22.3 MB
  downloaded from cdn.jsdelivr.net. The load starts when the page opens, so it overlaps with drawing.
- 390 px wide phone viewport: no horizontal scroll, runs work.
- Screenshots (viewport only): [loading](results/pg_loading.png),
  [compare A* vs freest_beam](results/pg_compare_random0.png),
  [hand-drawn box](results/pg_custom_drawn.png), [shared link in a fresh profile](results/pg_shared_link.png), [VIO jump, no filter vs F2, dark theme](results/pg_jump_f2_dark.png),
  [phone 390 px](results/pg_phone_390.png).

### New planners

Source: [results/playground_loop73.md](results/playground_loop73.md) (`results/measure_loop73.mjs`,
headless Chrome 140, Pyodide 314.0.7) against
[results/native_parity_loop73.json](results/native_parity_loop73.json) (`results/native_parity_loop73.py`,
CPython 3.12.10). Seed 0, sensor ideal, truth pose, no filter. Input type: synthetic. **Browser = native on
12/12 cases** (outcome, time to goal, duration, min clearance, path length), and natively the driver equals
`run.run_one` with the `bench.py` planner factory on the same JSON world in 12/12 (check E). The browser
wall times are one run each on a shared host (load average 45.8 at the start), so read them as rough.

  | world | planner | outcome / time to goal s / min clearance m / path m (browser = native) | browser Python s | native Python s |
  |---|---|---|---|---|
  | random_0 | thetastar_known | reached / 17.08 / 0.8833 / 24.123 | 3.28 | 2.059 |
  | maze_0 | thetastar_known | reached / 31.88 / 0.8223 / 39.463 | 9.873 | 6.214 |
  | random_0 | lazy_thetastar_known | reached / 17.12 / 0.8494 / 24.098 | 2.268 | 1.401 |
  | maze_0 | lazy_thetastar_known | reached / 31.88 / 0.8208 / 39.448 | 6.253 | 3.616 |
  | random_0 | lazy_thetastar_unknown | reached / 17.6 / 0.8919 / 24.653 | 10.179 | 6.44 |
  | maze_0 | lazy_thetastar_unknown | reached / 33.78 / 0.7908 / 40.487 | 30.727 | 19.599 |
  | random_0 | mppi | reached / 20.82 / 0.341 / 24.051 | 1.673 | 1.112 |
  | maze_0 | mppi | stuck / - / 0.6542 / 9.441 | 1.673 | 1.083 |
  | random_0 | mppi_astar | reached / 20.24 / 0.5812 / 23.917 | 5.321 | 3.122 |
  | maze_0 | mppi_astar | reached / 31.28 / 0.357 / 35.589 | 10.177 | 5.684 |
  | random_0 | hybrid_astar | reached / 18.74 / 0.6417 / 24.371 | 1.084 | 0.868 |
  | maze_0 | hybrid_astar | reached / 39.26 / 0.2553 / 38.439 | 2.262 | 1.932 |

Information only (check F, `native_parity_loop73.py --matrix-only`): against the benchmark's rows on the
generated worlds (layout 0, ideal), 12/12 same outcome and 6/12 identical in every field. Five differ by
0.0001 m in clearance or 0.001 m in path (the 4-decimal JSON rounding of check B); Hybrid A* on random_0
reaches B at 18.74 s here and 18.54 s in the matrix.

No run took over 60 s of browser Python, so all 6 stay in the list. Lazy Theta* unknown map is the slowest
option: 30.7 s for one maze_0 run. MPPI, MPPI + A* and Hybrid A* take the world as an argument (geofence on
the area bounds, as in the benchmark), like D* Lite.

### Run time limit = the benchmark's

A run ends as `timeout` at the world's run time limit, in sim time. `worker.js` `max_time_for` takes it
from the world's `family` with the table of `samples/close-area-benchmark/bench.py` `LONG_FAMILIES`:
**maze and warehouse 120 s**, every other family 60 s (`run.DEFAULTS`). A world drawn from "New empty"
(family `custom`) or without a family gets 60 s; an edited preset keeps its family. A run message may
override the limit with `cfg.max_time_s` (clamped to 10-300 s; the Solver uses this for its fixed
choices). Every result carries `max_time_s` and `max_time_source` (`family`, `default` or `cfg`), and the
score table shows it next to the outcome, for example "reached (limit 120 s)". Before this change every run
stopped at 60 s, so on maze_0 Bug2 (105.22 s) and Informed RRT* (69.7 s) timed out here and reached B in
the benchmark.

Source: [results/playground_loop73b.md](results/playground_loop73b.md) (`results/measure_loop73b.mjs`,
headless Chrome 140, Pyodide 314.0.7), every maze_0 and warehouse_0 case of
[native_parity.json](results/native_parity.json) and
[native_parity_loop73.json](results/native_parity_loop73.json). Seed 0, sensor ideal, truth pose, no
filter. Input type: synthetic. **Browser = native on 11/11 cases**; the worker reported the same limit as
native (120 s) and the score table showed it in 11/11. The 6 new-planner maze_0 rows did not change with the
longer limit (all of them end before 60 s). One browser run each on a shared host (load average 29.1).

| world | planner | limit s (browser / native / table) | browser outcome / time to goal s / min clearance m / path m | native | same | browser Python s | native Python s |
|---|---|---|---|---|---|---|---|
| maze_0 | astar_known | 120 / 120 / 120 | reached / 41.26 / 0.5937 / 36.981 | reached / 41.26 / 0.5937 / 36.981 | yes | 5.076 | 1.974 |
| warehouse_0 | astar_known | 120 / 120 / 120 | reached / 49.26 / 0.5151 / 34.978 | reached / 49.26 / 0.5151 / 34.978 | yes | 4.237 | 1.649 |
| maze_0 | bug2 | 120 / 120 / 120 | reached / 105.22 / 0.4043 / 65.49 | reached / 105.22 / 0.4043 / 65.49 | yes | 0.662 | 0.313 |
| warehouse_0 | bug2 | 120 / 120 / 120 | timeout / - / 0.4254 / 70.725 | timeout / - / 0.4254 / 70.725 | yes | 0.714 | 0.321 |
| maze_0 | informed_rrt_star | 120 / 120 / 120 | reached / 69.7 / 0.2754 / 33.637 | reached / 69.7 / 0.2754 / 33.637 | yes | 0.932 | 0.415 |
| maze_0 | thetastar_known | 120 / 120 / 120 | reached / 31.88 / 0.8223 / 39.463 | reached / 31.88 / 0.8223 / 39.463 | yes | 9.844 | 4.509 |
| maze_0 | lazy_thetastar_known | 120 / 120 / 120 | reached / 31.88 / 0.8208 / 39.448 | reached / 31.88 / 0.8208 / 39.448 | yes | 6.203 | 2.736 |
| maze_0 | lazy_thetastar_unknown | 120 / 120 / 120 | reached / 33.78 / 0.7908 / 40.487 | reached / 33.78 / 0.7908 / 40.487 | yes | 31.816 | 14.253 |
| maze_0 | mppi | 120 / 120 / 120 | stuck / - / 0.6542 / 9.441 | stuck / - / 0.6542 / 9.441 | yes | 1.721 | 0.825 |
| maze_0 | mppi_astar | 120 / 120 / 120 | reached / 31.28 / 0.357 / 35.589 | reached / 31.28 / 0.357 / 35.589 | yes | 10.109 | 4.314 |
| maze_0 | hybrid_astar | 120 / 120 / 120 | reached / 39.26 / 0.2553 / 38.439 | reached / 39.26 / 0.2553 / 38.439 | yes | 2.466 | 1.516 |

Benchmark parity (check F, information only; driver on the preset JSON vs `matrix_0.json`, layout 0, seed
0, ideal, generated world, both at 120 s): A* known map on maze_0 is identical in every field (reached,
41.26 s, 0.5937 m, 36.981 m). On warehouse_0 the outcome and time are the same (reached, 49.26 s); min
clearance is 0.5151 m here and 0.515 m in the matrix, a 0.0001 m difference from the 4-decimal JSON export
(check B). Bug2 on maze_0 and warehouse_0 and Informed RRT* on maze_0 are identical to the matrix.

The driver loop matches the arena's own loops, checked natively in `native_parity.py`
([native_parity.json](results/native_parity.json), 29/37 checks identical after the drone-panel change; every reference loop gets
the driver's run time limit, `cfg_for`):

| check | identical |
|---|---|
| A: driver == `run.run_one` on the same JSON world (truth pose, ideal sensor), 11 cases of the first 6 planners (incl. A* known on maze_0 and warehouse_0, A* unknown on office_0) | 11/11 |
| E: driver == `run.run_one` with the planner built by `close-area-benchmark/bench.py` `PLANNERS[name][0]` called with the world, same JSON world, the 6 planners added on 2026-11-09 plus Bug2 on maze_0 / warehouse_0, Informed RRT* on maze_0, and A* unknown on random_0 and office_0 | 11/11 |
| C: driver == `run.run_one` + `estimator.make_pose_source_factory(fault)` (the `run.evaluate` path) | 2/2 |
| D: driver with F2 == `close-area-safety-filter/run_kill.run_one("F2", case, unsensed off)` | 2/2 |
| B: driver on the preset JSON == `run.run_one` on `world.make_world` (no JSON) | 3/11 (A* unknown on random_0 now differs by 0.0001 m clearance; on office_0 by 0.04 s) |
| G (separate count `reloc_summary`): driver with recovery == `run.run_one` + `run_disambiguate.build`, same JSON world, score + loss events | 4/4 |

Information only: the 6 cases for the planners added on 2026-11-09 and the 5 run-time-limit maze_0 / warehouse_0 cases against the
benchmark's own rows in `samples/close-area-benchmark/results/matrix_0.json` (generated worlds, preset
ideal, layout 0): 9/11 identical, 11/11 same outcome. With A* unknown on random_0 and office_0 added: 9/13
identical, 13/13 same outcome; both differ by the JSON rounding only. Informed RRT* on office_0 differs in min clearance
only (0.2762 m here, 0.2761 m in the matrix), A* known map on warehouse_0 too (0.5151 m vs 0.515 m): the
same 4-decimal JSON rounding as check B.

Check B is a real difference, not a bug in the playground: `world_json` rounds every number to 4
decimals (0.1 mm), and that is enough to move some runs a little. Example: straight on random_0
gives duration 20.3 s on the JSON world and 20.38 s on the generated world. So a playground score
equals the native score **on the same JSON world**, and can differ slightly from the published
`results/*.json` of the arena, which were run on generated worlds.

## What a run does

`worker.js` holds `DRIVER_PY`, about 260 lines of Python glue. It calls `world_json.from_json`,
`worlds_complex.has_free_path`, `presets.make_sensor`, `estimator.make_pose_source_factory`,
the planner `make()` functions, `filters.make("F2")` and `scorer.score`. Each planner is built the
way `close-area-benchmark/bench.py` builds it: the DWA / Bug, D* Lite and RRT* samples each import
their own `arena.py`, so they load with bench.py's recipe (folder on `sys.path` only while importing).
D* Lite and (since the drone-panel change) A* unknown map get the benchmark's geofence (log-odds map corner = area
corner - 2 m); before that change A* unknown map kept the shipped corner at (-2.5, -2.5) and did not move
when B was outside it. The loop is `run.run_one`
when the filter is off (pose at the 10 Hz planner rate), and `run_kill.run_one` when F2 is on (pose
and filter every 50 Hz step, a second sensor copy for the filter at 16.7 Hz, rng `[seed, index, 8]`).
The only additions are a sensor-preset argument, trace recording, the run time limit by family
(120 s on maze and warehouse, as `bench.py`; see "Run time limit" above), and the per-run
radius override and the opt-in yaw policy (see "Your drone").

| Control | Options | Source |
|---|---|---|
| Planner | straight, freest_beam, A* + ESDF known map, A* + ESDF unknown map, APF, VFH+, DWA, DWA + 3 s scan memory, Bug2, TangentBug, D* Lite unknown map, Informed RRT* 5000 known map, Theta* known map, Lazy Theta* known map, Lazy Theta* unknown map, MPPI goal only, MPPI on the unknown-map A* path, Hybrid A* unknown map | `planners/`, `run_faults.FreestBeam`, `close-area-planner-reactive`, `close-area-planner-dwa-bug`, `close-area-planner-dstar`, `close-area-planner-sampling`, `close-area-planner-thetastar`, `close-area-planner-mppi`, `close-area-planner-hybrid-astar` |
| Sensor | ideal (72 rays, 6 m), crazyflie (4 cone beams, 3 m), crazyflie_bright (0.73 m), depth_cam_87 (30 beams, 87 deg, 0.3-5 m), lidar_2d (360 beams, 12 m) | `presets.py` |
| VIO fault | off (planner sees truth), VIO no fault, jump, bias, dropout | `estimator.py`, `faults.py`; the VIO options add 2 seeded dark zones |
| VIO loss recovery | none, single, multi, multi + info-gain move (with VIO jump or dropout; fixes planner A* known map and filter none) | `close-area-relocalize` via [pg_reloc.py](pg_reloc.py) and `run_disambiguate.build` |
| Filter | none, F2 (PX4-CBF as shipped, on ranges) | `close-area-safety-filter/filters.py` |
| Seed | 0-9999 | sensor noise, dark zones, fault timing |
| Advanced: your drone | radius 0.05-0.6 m, v_max 0.1-5 m/s, yaw fixed / look where you go | `cfg.vehicle`, `cfg.yaw` (see "Your drone") |

Each run returns the 10 Hz trace (truth, estimate, sigma, quality, yaw, range scan), the planned
path snapshots, truth clearance, dark zones, the fault log and the scorer row. The replay draws
truth and estimate paths, the range beams, the planned path (A*, D* Lite, RRT*) and the vehicle at
its true size (0.15 m unless the drone panel says otherwise).
Compare mode runs config B on the same world and overlays it, with both columns in the score table.

## Editor

Tools: Move (drag obstacles, A or B), Box, Wall (axis-aligned, 0.1 m thick), Cylinder (drag the
radius), Glass (0.04 m wall, material glass: cone sensors do not see it, truth and the A* prior map
do). Snap 0.1 m, Undo (Ctrl+Z), Delete, material per obstacle. Presets: 8 worlds in
[presets/](presets/index.json) (office, warehouse, forest, maze, glass_office, random, u_trap,
narrow_gap; seed 0, layout 0), exported with `world_json.to_json` by `results/export_presets.py`.
Download / open `close-area-world/1` JSON, or keep one world in localStorage. Any edit clears the
replay, because the trace no longer matches the world. The area bounds of a preset cannot be
resized in the editor; "New empty" gives a 20 x 20 m area.

## Shareable link

**Copy link** builds `index.html?CONFIG#w=WORLD`, copies it and puts it in the address bar.

- `w=`: the `close-area-world/1` JSON, compressed with `CompressionStream("deflate")` (zlib) and
  base64url coded without padding.
- Query params: `planner`, `preset`, `fault`, `filter` for config A; the same with `_b` for config B
  and `compare=1` when compare is on; `seed`; `radius`, `v_max`, `yaw` when the drone panel is not
  the default (both configs); `src=<preset>` when the world is an unedited preset
  (used only to show the native parity note, after checking the decoded world equals the preset file).
- Opening the link restores world and config and runs once Python is ready. Unknown param values
  are ignored with a message. Editing the world or loading another one removes the link from the
  address bar, so a reload does not bring back an old world.

## Files

| File | What |
|---|---|
| [index.html](index.html), [playground.css](playground.css), [playground.js](playground.js) | The page. Uses `../showcase.css` for the palette and light / dark theme. `window.PG` is a small API for scripted checks |
| [worker.js](worker.js) | ES module worker: loads Pyodide 314.0.7 (`pyodide.mjs`, CDN or local folder), numpy, scipy and the 42 files in the manifest once, with named retries, then serves `run` messages |
| [pg_reloc.py](pg_reloc.py) | VIO loss recovery glue: builds the arms with `run_disambiguate.build`, records hypotheses, verdict status per frame and loss events |
| [manifest.json](manifest.json) | Pyodide pin, CDN and local source, packages, files (shared with the spike) |
| [results/reloc_demo_random_1_97.json](results/reloc_demo_random_1_97.json) | The VIO-loss demo world (written by `native_parity.py`) |
| [presets/](presets/index.json) | Preset world JSON |
| `results/native_parity_custom.py`, `measure_custom.mjs` | Native reference and browser check for cfg.vehicle, cfg.sensor, cfg.yaw, the radius rule and the drone panel / link ([playground_custom.md](results/playground_custom.md)) |
| `results/measure_loop73b.mjs` | Browser check of every maze_0 / warehouse_0 case with the benchmark run time limit ([playground_loop73b.md](results/playground_loop73b.md)) |
| `results/native_parity_loop73.py`, `measure_loop73.mjs` | Native reference and browser check for the 6 planners added on 2026-11-10 ([playground_loop73.md](results/playground_loop73.md)) |
| `results/build_advisor_loop73.py` | Runs `data/build_advisor.py` unchanged with planner docs for the 7 benchmark rows added on 2026-11-10; rebuilds [data/advisor.json](data/advisor.json) |
| `results/export_presets.py`, `native_parity.py`, `measure_playground.mjs` | Export presets; native reference + loop parity (incl. the relocalization cases); headless Chrome check, link check in a second fresh profile, blocked-CDN check in a third, and screenshots ([pg_shared_link.png](results/pg_shared_link.png)) |

Re-run (needs the arena venv, Chrome at the macOS default path, network for the CDN):

```sh
uv venv --python 3.12 samples/close-area-arena/.venv
uv pip install --python samples/close-area-arena/.venv -r samples/close-area-arena/requirements.txt
samples/close-area-arena/.venv/bin/python site/playground/results/export_presets.py
samples/close-area-arena/.venv/bin/python site/playground/results/native_parity.py   # about 1 minute
node site/playground/results/measure_playground.mjs                                  # about 2 minutes
samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_loop73.py   # about 2 minutes
node site/playground/results/measure_loop73.mjs                                      # about 2 minutes
node site/playground/results/measure_loop73b.mjs                                     # about 2 minutes
samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_custom.py   # about 2 minutes
node site/playground/results/measure_custom.mjs                                      # about 3 minutes
# optional: fill site/playground/pyodide-local/ first (Offline / blocked CDN) to also measure the local load
```

Finding: `importScripts` of the CDN `pyodide.js` failed in a classic worker in Chrome 140
(NetworkError, while `fetch` of the same URL returned 200), and `pyodide.mjs` refuses classic
workers. The worker is therefore started with `{type: "module"}` and uses `import()`.

## Not verified (playground)

- GitHub Pages hosting. Only `python3 -m http.server` locally.
- Firefox and Safari, real phones and touch input. Only headless Chrome 140 with mouse events and
  a 390 x 844 emulated viewport.
- The shareable link was checked in Chrome only: `CompressionStream` needs Chrome 80+, Firefox 113+,
  Safari 16.4+ (not tried). Very long links (over about 8000 characters, for example a world with
  hundreds of obstacles) were not tried; some chat tools and servers cut long URLs.
- The 6 new planners have a native reference on one preset each, with the ideal sensor and truth
  pose. Other sensors, faults and F2 run through the same driver code but are not compared with
  native for them; the link check (TangentBug, D* Lite + F2) is browser vs browser only.
- The 6 planners added on 2026-11-10: compared with native on random_0 and maze_0 only, ideal sensor, truth pose,
  no filter. `measure_playground.mjs` and `native_parity.py` (the older 21 cases, link and CDN checks) were
  not re-run after the 6 extra files went into the manifest and DRIVER_PY.
- Pointer drawing was checked for the Box tool only. Wall, Cylinder, Glass, Move, Undo, Delete,
  material change and file open / save / localStorage were not exercised by the scripted check.
- `spike.html` with the extended manifest (it now also writes the 19 extra files) was not re-run.
- Run time limit: `measure_playground.mjs` (its 21 cases, link and CDN checks) was not re-run;
  the 5 new maze_0 / warehouse_0 cases in native_parity.json were compared with the browser by
  `measure_loop73b.mjs` only. The `cfg.max_time_s` override and its clamp were spot-checked once in native
  CPython through `play()` (result not saved), not in a browser run. Office, forest and the other 60 s families were not re-run
  (their limit did not change).
- Worlds much larger than 20 x 20 m, and runs near the 60 s / 120 s limit with A* unknown map. Estimate,
  not measured: browser Python ran about 2x slower than native in the check, so such a run would
  take about 10 s.
- Real or SITL flight: everything is the synthetic arena.
- Drone panel: the radius rule was compared with native on narrow_gap_0 only (MPPI on the A* path
  and A* unknown map, 0.25 and 0.35 m). The other planners get the same constants set but no run at another
  radius was compared or looked at; v_max other than 2 m/s was not run in a check. The panel was driven by
  script (values set, `PG.config`, link round trip), not clicked; its layout at 390 px was not looked at.
  look-where-you-go yaw on a 360 deg sensor runs but was not compared with native.
- Re-run of `measure_playground.mjs` after the drone-panel change: its nav-link check at 390 px reported the Playground link
  not found on site/showcase.html and site/index.html (right edge null). Those pages and nav.js were not
  changed here; not investigated. The local Pyodide folder case was not measured (no
  site/playground/pyodide-local/ in this checkout).
- Retries: only a refused connection was tested (CDN mapped to 127.0.0.1). A fetch that
  hangs and then fails, as in blocker 7, the 120 s / 180 s step timeouts, the 45 s "still loading"
  Retry, and the fresh-runtime path after a timed-out `loadPackage` were not exercised. Venue Wi-Fi
  not tried.
- Offline folder: measured once on localhost with the folder present; a machine with no network at
  all was not tried (the CDN was blocked by host mapping, the local server still ran).
- VIO loss recovery: 4 cases compared with native, all with the ideal sensor preset. Other presets
  run (the relocalizer keeps its own 72-ray scan), but were not compared. The symmetric corridor case
  of the sample (`CorridorJump`) is not in the playground. Ghost markers, strip and arrows were checked
  by eye on one screenshot. The info-gain move arrow is drawn from the estimate when the move started,
  in the map frame; the move is flown in the raw VIO frame, so after a jump the arrow can be offset
  from the flown path.
- `spike.html` with the extended manifest: not re-run. Its file loop makes a stray directory for
  `pg_reloc.py` (no folder in its `dst`); harmless, not tested.

# Spike: can the arena run in the browser?

Feasibility spike for a browser playground (draw an arena, place A and B, pick a planner, watch
it fly). Question: can the hub's real Python arena and planners
([samples/close-area-arena](../../samples/close-area-arena/README.md)) run in the browser fast
enough, so the playground and the benchmarks share one implementation?

### Verdict

**Yes, PASS.** A projected 30 s run takes 0.1-1.0 s of wall time for `straight` and
`astar_esdf` (known map), and 4.6-5.9 s for `astar_esdf` with an unknown map. The target was
under 15 s. The browser gives the same scores as native CPython on all 6 measured cases. Source:
[results/spike_timing.md](results/spike_timing.md). Input type: synthetic (simulated layouts,
vehicle and range sensor), measured in headless Chrome 140 on an Apple M3 Max.

The real cost is page load. Cold cache, the page is ready 4.9 s after navigation and downloads
22.0 MB from cdn.jsdelivr.net. The scipy wheel alone is 13.5 MB. With a warm cache, ready takes
2.6 s.

The host was shared with other jobs (load average 109-147 on 16 cores during the measurement), so
every absolute time here is pessimistic.

### Numbers (headless Chrome, Pyodide 314.0.7, synthetic input)

| What | Cold cache | Warm cache |
|---|---|---|
| Pyodide + numpy + scipy load (script start => arena files written) | 3851 ms | 1598 ms |
| of which `loadPackage(["numpy", "scipy"])` | 1276 ms | 742 ms |
| Arena import (numpy + scipy.ndimage import 915 ms, arena modules 19 ms) | 938 ms | 886 ms |
| Ready, since navigation start | 4915 ms | 2606 ms |

| Planner | Layout | Simulated s | Browser wall s (median of 3) | Wall per simulated s | 30 s run => wall s | Native wall per simulated s | Browser / native |
|---|---|---|---|---|---|---|---|
| straight | random/0 | 20.4 | 0.079 | 0.0039 | 0.12 | 0.0028 | 1.39x |
| astar_esdf known map | random/0 | 19.38 | 0.652 | 0.0337 | 1.01 | 0.0162 | 2.08x |
| astar_esdf unknown map | random/0 | 18.68 | 2.875 | 0.1539 | 4.62 | 0.0727 | 2.12x |
| straight | u_trap/1 | 20.48 | 0.074 | 0.0036 | 0.11 | 0.002 | 1.8x |
| astar_esdf known map | u_trap/1 | 20.06 | 0.596 | 0.0297 | 0.89 | 0.0142 | 2.09x |
| astar_esdf unknown map | u_trap/1 | 22.16 | 4.38 | 0.1976 | 5.93 | 0.0917 | 2.15x |

- Total for one 20 s run, cold page: 4.9 s to ready, then 0.65 s for astar_esdf known map on
  random/0 (19.38 s simulated).
- The first run takes the same time as later runs (astar known random/0: 0.653 s first, 0.652 s
  median). There is no warm-up penalty after import.
- Layout build (`world.make_world`, raster + BFS free-path check): 77-78 ms per layout.
- Streaming cost: positions go to JS through the `pose_source` hook at 10 Hz (194-204 calls per
  run). A run with streaming takes the same time as one without (astar known random/0: 0.652 s
  vs 0.651 s).
- Memory: the wasm heap is 90 MB after import and does not grow over 24 runs. The Chrome JS heap is
  179-182 MB after import (`performance.memory`, Chrome only).
- Scores (outcome, time to goal, duration, min clearance, path length) are identical to
  `samples/close-area-arena/results/astar_esdf_{family}_0.json`, which was run with CPython 3.11 /
  numpy 2.4.6. They also match today's native run (CPython 3.12.10 / numpy 2.5.4). Pyodide uses
  Python 3.14.2 / numpy 2.4.6 / scipy 1.18.0.

### What the playground has to deal with

The main thread freezes while Python runs, because `run_one` is one synchronous call. The freeze
lasts 0.08 s for straight, 0.6-0.65 s for astar known map, and 2.9-4.4 s for astar unknown map
(table above). Positions cannot be drawn while the run is computing. This spike computes the whole
run first, then replays the streamed positions at 4x speed. Ranked options:

1. **Run Pyodide in a Web Worker, keep compute-then-replay (recommended).** The UI stays
   responsive and the arena code does not change. The worker posts positions with `postMessage`,
   in chunks or at the end. Estimate: about half a day, roughly 100-150 lines of JS moved into
   `worker.js` plus a message protocol. Not built or measured here.
2. **Ship as measured, on the main thread.** No extra cost. A 0.6 s freeze for astar known map is
   tolerable. The 4-6 s freeze for unknown map is not, so hide that planner or show a "computing"
   state.
3. **Lower the planner or physics rate.** Not needed: the slowest case is already 5x faster than
   real time. Changing `plan_hz` or `HZ` would also make playground results differ from the
   benchmarks.
4. **Precompute runs offline.** This already exists for the showcase
   (`export_replay.py`). It does not cover user-drawn arenas, so it does not answer the brief.
5. **Port a subset to JS.** Estimate: 2-4 days for vehicle, range fan, scorer, straight and A* +
   ESDF (an EDT would also be needed). It saves the 22 MB download and about 4 s of cold load. The
   cost is a second implementation that drifts from the benchmarks. Only worth it if cold load on
   the Pages site turns out to be unacceptable.

To cut cold load without porting, the playground can start loading Pyodide when the page opens,
while the user is still drawing. The service-worker or HTTP cache then makes repeat visits about
2.6 s (warm column).

Custom arenas: the playground will need a few lines of Python that build a `World` from the drawn
boxes and cylinders, then call `rasterize()` and the BFS check, the way `make_world` does. No
arena file needs to change for that. Not written or tested here.

### Files

| File | What |
|---|---|
| [spike.html](spike.html) | The page. `?bench=1` runs the full 6-case matrix; `?reps=N` sets the repetitions |
| [spike.js](spike.js) | Loads Pyodide from the URL in the manifest, `loadPackage` numpy + scipy, writes the arena files into `/home/pyodide/close_area_arena/`, runs `DRIVER_PY` (imports + `bench_case`), streams positions, draws canvases. `window.SPIKE_RESULT` holds every measurement |
| [manifest.json](manifest.json) | Pyodide version and base URL, packages, and the arena files (11 for the spike, 23 now that the playground also loads estimator, faults, presets, sensors_cone, world_json, worlds_complex, world_glass, run_faults, APF, VFH+ and filters.py; `src` is relative to the manifest, so `../../` is the repo root) |
| [results/measure.mjs](results/measure.mjs) | Runs `DRIVER_PY` under native CPython from the arena venv, then the page in headless Chrome over the DevTools protocol: cold profile with `?bench=1`, then warm with the default page. Writes everything below |
| [results/spike_timing.md](results/spike_timing.md) | Generated report: environment, load, runs, score parity, memory, downloads |
| `results/spike_cold.json`, `spike_warm.json`, `native_baseline.json` | Raw measurements |
| [results/spike_bench.png](results/spike_bench.png), [results/spike_interactive.png](results/spike_interactive.png) | 1280 x 900 viewport screenshots |

### Run

```sh
python3 -m http.server 8000            # from the repo root
# open http://localhost:8000/site/playground/spike.html  (add ?bench=1 for the matrix)
```

Re-measure (needs the arena venv for the native baseline, Chrome, and network for the CDN):

```sh
uv venv --python 3.12 samples/close-area-arena/.venv
uv pip install --python samples/close-area-arena/.venv -r samples/close-area-arena/requirements.txt
node site/playground/results/measure.mjs        # about 4 minutes on the loaded host
```

Version notes: Pyodide moved to Python-version numbering. `314.0.7` was the jsdelivr `latest`
tag on 2026-11-09, and its `pyodide-lock.json` lists numpy 2.4.6 and scipy 1.18.0. The older line,
`0.29.5`, ships scipy 1.14.1. Pyodide 314 converts JS `null` to `JsNull`, which is not Python
`None`, so `spike.js` passes `undefined` for "no callback".

### Not verified

- GitHub Pages hosting (only `python3 -m http.server` locally). Pages serves `.py` files as static
  files, but that was not tried.
- Firefox, Safari, phones, and slower laptops. Only headless Chrome 140 on one M3 Max, under heavy
  host load.
- The JS-port estimates: these are estimates, not measurements. (The Web Worker variant was built and measured later: see the playground section above.)
- Runs of exactly 30 s: the measured runs end at 18.7-22.2 s simulated (reached or stuck). The 30 s
  figures are wall per simulated second x 30.
- Narrow-gap layouts, the estimator and fault hooks, and user-drawn arenas.
- Real or SITL flight: everything here is the synthetic arena.
