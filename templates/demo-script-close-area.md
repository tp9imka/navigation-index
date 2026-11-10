# Demo script: close-area A to B, the toolkit in 2 minutes

State on 2026-11-10: this is a script for the measured toolkit. Nothing on this page was rehearsed or
timed as a whole. Every number is `[synthetic]` (simulated room, vehicle, sensor and estimator, 2.5D
point mass, scored on truth) and comes from a committed results file named next to it. None is SITL
or flight.

What we pitch: the measured toolkit, plus a narrow claim only if the real brief fits it
([case study](../docs/case-study/README.md), [research decision](../docs/research/README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is)).
The two-arm safety-filter demo that used to be on this page is gone: that headline failed its own
kill test (F5 collided in 1.7 % [0.7, 3.8] of jump-fault runs against a 1 % bar,
[kill_e_tables.md](../samples/close-area-safety-filter/results/kill_e_tables.md), `[synthetic]`).
If the brief is VIO loss, use the [appendix](#appendix-if-the-brief-is-vio-loss-h1).

The flow on stage: room spec or sketch => `world_from_room.py` / `world_from_image.py` => Solver
(Import world JSON, Your drone, Quick, race view, Pareto view, Recommend) =>
`make first-flight PLANNER=bench:<id> WORLD=... ARM=...` => planned-vs-flown PNG + score line =>
(optional 15 s) scenario pack verdict. One driver at the laptop, one narrator. The driver never types
free text on stage: every command is in shell history (Ctrl-R + the keyword in the Action column).

Live site: [navigation-index.pages.dev](https://navigation-index.pages.dev/), Solver at
[/site/solver/](https://navigation-index.pages.dev/site/solver/). Generic demo rules:
[demo-script.md](demo-script.md).

## Pre-flight checklist (T-30 min)

Tabs open (Chrome, one window, zoom 125 %):

- [ ] Tab 1: [live Solver](https://navigation-index.pages.dev/site/solver/), loaded until the
      planner list appears (Python ready; 4.5 s on the recorded run, `python_ready_s` in
      [solver_custom.json](../site/solver/results/import_hall_8x6/solver_custom.json)). Reload it
      just before going on, then leave it.
- [ ] Tab 2: the same page from localhost, `http://localhost:8000/site/solver/?pyodide=local`
      (server below), also loaded. This is the CDN-blocked fallback.
- [ ] Tab 3: [recommend.md](../site/solver/results/import_hall_8x6/recommend.md) (committed copy) in
      the editor, scrolled to "## Pick".
- [ ] Tab 4: the fallback images in Preview:
      [room_hall_8x6.png](../samples/close-area-arena/results/room_hall_8x6.png),
      [sketch_hall.png](../samples/close-area-arena/rooms/sketch_hall.png),
      [solver_race_mid.png](../site/solver/results/solver_race_mid.png),
      [solver_pareto.png](../site/solver/results/solver_pareto.png),
      [first_flight_bench_dstar_lite_narrow_gap_0_F0.png](flight-repo/results/first_flight_bench_dstar_lite_narrow_gap_0_F0.png).
- [ ] Tab 5: [pack_hall_8x6.md](../samples/close-area-benchmark/results/pack_hall_8x6.md) in the editor.

Venvs warm (each built once and used once in rehearsal, so the first Python start is not on stage;
cold `make first-flight` took 205.89 s, warm 4.94 s,
[first_flight.txt](flight-repo/results/first_flight.txt),
[first_flight_warm.txt](flight-repo/results/first_flight_warm.txt)):

- [ ] `samples/close-area-arena/.venv` (arena requirements).
- [ ] `templates/flight-repo/.venv` (`make venv`), and `make bench-list` prints the ids.
- [ ] `samples/close-area-benchmark/.venv` (its `requirements.txt`, includes osqp), only for the
      optional pack beat.
- [ ] Local server running in its own terminal from the hub root: `python3 -m http.server 8000`.
- [ ] `python3 tools/venue_kit.py prepare` then `verify` ran with network and said `PASS`
      ([day-0 runbook](../docs/day0-runbook.md#browser-tools-offline)). Without it `?pyodide=local`
      has nothing to load.

Files downloaded and folders ready:

- [ ] `mkdir -p /tmp/demo templates/flight-repo/runs` (the flight writes to the gitignored `runs/`).
- [ ] Old `~/Downloads/recommend*.md` and `recommend*.json` removed, so the new download keeps its name.
- [ ] Chrome allowed multiple downloads for the live site and for localhost (Recommend writes two
      files from one click; a real profile may ask).

Commands in shell history (run each once in rehearsal, in this order; one terminal, font 20 pt):

```sh
# Ctrl-R "world_from_room"   (cwd samples/close-area-arena)
.venv/bin/python world_from_room.py rooms/hall_8x6.json -o /tmp/demo/hall_8x6.world.json
# Ctrl-R "world_from_image"  (alternative input, same hall drawn as a sketch)
.venv/bin/python world_from_image.py rooms/sketch_hall.png --ref 40 40 440 40 8.0 --origin-px 40 340 --a-m 0.8 0.8 --b-m 7.2 1.0 -o /tmp/demo/sketch_hall.world.json
# Ctrl-R "first-flight"      (cwd templates/flight-repo)
make first-flight PLANNER=bench:thetastar_known WORLD=/tmp/demo/hall_8x6.world.json ARM=F0 OUT=../runs/demo_hall_8x6
# Ctrl-R "open ../runs"      (or "open runs")
open runs/demo_hall_8x6.png
# Ctrl-R "pack.py"           (cwd samples/close-area-benchmark)
.venv/bin/python pack.py run packs/hall_8x6.json --workers 14 --out /tmp/demo/pack_hall_8x6
```

- The commands write to `/tmp/demo` and `templates/flight-repo/runs/` only. The README forms of
  these commands overwrite committed files (`rooms/*.world.json`, `results/room_*`,
  `results/pack_hall_8x6.*`); do not use those forms on the demo laptop.
- `OUT=../runs/...` works because the Makefile writes `results/$(OUT).*`; it was not run in this
  form (see Not verified).
- The Recommend command says `WORLD=my_world.json`; the demo flies the file that was imported
  instead, which is the same world.

Every frame carries its label: the Solver page prints "SYNTHETIC SIMULATION" at the top, the score
line starts `score input=synthetic`, and the slides add `[synthetic]` in a corner.

## Script

2:00 total. Spoken lines are for the narrator; the driver does the Action column only.

| Time | Spoken line | On screen | Action | Fallback |
|---|---|---|---|---|
| 0:00-0:15 | "Organisers gave us a room. We measured it: an 8 by 6 metre hall, a wall with a 0.9 m door, pillars and tables. One command turns that into a world file, and checks there is a free path from A to B." | Terminal: `wrote /tmp/demo/hall_8x6.world.json: 8 obstacles ...` then `ok from_json, ok has_free_path`. Then the sketch [sketch_hall.png](../samples/close-area-arena/rooms/sketch_hall.png): "a photo of a whiteboard works too" | Ctrl-R `world_from_room`, Enter. Cmd-Tab to Preview, sketch image | Command fails: import the committed [hall_8x6.world.json](../samples/close-area-arena/rooms/hall_8x6.world.json) at 0:15 instead. Show [room_hall_8x6.png](../samples/close-area-arena/results/room_hall_8x6.png) |
| 0:15-0:25 | "This is the Solver, on the public site. It runs our Python arena in the browser. Import the room. Here is our drone: radius, speed, sensor." | Tab 1: "Imported hall_8x6.world.json (8 obstacles)." Your drone panel open, defaults (0.15 m, 2 m/s, ideal sensor) | Click **Import world JSON**, Cmd-Shift-G `/tmp/demo`, pick the file. Click **Your drone** open, then closed. Leave defaults (the committed run used them) | CDN blocked or page stuck on "Loading Python": Tab 2 (`?pyodide=local`). No network at all: Tab 2 is localhost already |
| 0:25-0:50 | "Quick: every planner, 18 of them, five seeds each, A and B jittered per seed. 90 flights in about 20 seconds. Watch the race." | Race view filling, one colour per planner; then the headline. Recorded run: 90 runs in 19.4 s on 4 workers, 41 reached, 48 stuck, 1 timeout `[synthetic]` ([measure_import.json](../site/solver/results/measure_import.json), Solver README "Day-1 import pass") | Click **Quick**. When done, click **Animate race** | Over 35 s, or the page hangs: say "here is the recorded run", Tab 4 [solver_race_mid.png](../site/solver/results/solver_race_mid.png) (random_0, not the hall; say so) and go to Tab 3 |
| 0:50-1:05 | "Nine planners tie at the top: 5 of 5, which only says 57 to 100 percent. The page says so instead of naming a winner. Nine are clearly worse, 0 of 5. The Pareto view picks fast and safe inside the tie." | Headline "9 planners tie at the top". Pareto view under the matrix: `lazy_thetastar_unknown` 27.58 s / 0.253 m, `mppi_astar` 13.51 s / 0.251 m `[synthetic]` ([recommend.md](../site/solver/results/import_hall_8x6/recommend.md)) | Scroll to the Pareto view, point | Tab 3: the committed recommend.md, "Tied with the best" table and the Pareto line |
| 1:05-1:15 | "Recommend writes the pick and the command. It also measured the narrowest passage on the route, 0.65 metres, so it switches off our range filter and warns about it." | recommend.md: pick `thetastar_known`, 5/5, median 21.90 s, min clearance 0.214 m; `ARM=F0` warning, narrowest passage 0.65 m `[synthetic]` ([recommend.md](../site/solver/results/import_hall_8x6/recommend.md)) | Click **Recommend**. Open the downloaded `recommend.md` in the editor | Download blocked: Tab 3, same file committed |
| 1:15-1:40 | "Same pick, same room, through the flight loop the team ships: 20 hertz, arrival rule, scorer. Planned path against flown path." | Terminal: `score input=synthetic ... planner=bench:thetastar_known safety=arm:F0 reached=... collided=... outcome=...`, then the `score_log.py` block; then `runs/demo_hall_8x6.png`. Read out only `reached`, `collided` and `outcome` for this run | Ctrl-R `first-flight`, Enter. When `wrote ...png` prints: Ctrl-R `open`, Enter | No `wrote` line within 15 s, or an error: Tab 4 [first_flight_bench_dstar_lite_narrow_gap_0_F0.png](flight-repo/results/first_flight_bench_dstar_lite_narrow_gap_0_F0.png) and its committed line `reached=True ... outcome=arrived`, 24.96 s to goal, min clearance 0.293 m `[synthetic]` ([first_flight_bench.txt](flight-repo/results/first_flight_bench.txt)). Say "a recorded flight on the narrow-gap preset" |
| 1:40-1:55 (optional) | "Last: the bar, as a file. Our real drone's camera and radius, ten seeds. A* known map: 10 of 10, and the file still says NOT PROVEN, because 90 percent needs 35 clean runs. The fastest planner in the Solver collided 10 of 10 with this camera." | [pack_hall_8x6.md](../samples/close-area-benchmark/results/pack_hall_8x6.md): `astar_known` NOT PROVEN, 10/10, CI [0.72, 1.00], needs 35 runs; `mppi_astar` FAIL, 10 collisions in 10 runs; exit 1 `[synthetic]` (depth_cam_87, radius 0.2 m) | Tab 5 (committed file). Live only if 15 s are spare: Ctrl-R `pack.py`, Enter (60 runs, 21.1 s on 1 worker in [pack_hall_8x6_stdout.txt](../samples/close-area-benchmark/results/pack_hall_8x6_stdout.txt); on 14 workers not in a committed file) | Skip the beat; nothing later depends on it |
| 1:55-2:00 | "Room to world, world to ranked planners, pick to scored flight, in two minutes. All of it simulated, and it says so on every screen." | Back to Tab 1 | none | - |

If the slot is under 90 s: drop the sketch image (0:00), drop Animate race, drop the pack beat.

### Numbers on screen and where they come from

All `[synthetic]`. Show only these. A live run is one run: say "this run", never "over N".

| Number | Time | File | Input |
|---|---|---|---|
| 8 obstacles; 0.9 m door; 8 x 6 m | 0:00 | [rooms/hall_8x6.json](../samples/close-area-arena/rooms/hall_8x6.json), [room_hall_8x6.json](../samples/close-area-arena/results/room_hall_8x6.json) | made-up room spec `[synthetic]` |
| Python ready 4.5 s | pre-flight | [solver_custom.json](../site/solver/results/import_hall_8x6/solver_custom.json) `pool.python_ready_s` | headless Chrome 140, M3 Max |
| 90 runs, 19.4 s, 4 workers; 41 reached, 48 stuck, 1 timeout | 0:25 | [measure_import.json](../site/solver/results/measure_import.json), [solver_custom.json](../site/solver/results/import_hall_8x6/solver_custom.json) | `[synthetic]` |
| 9 tied at 5/5 (57-100 %), 9 clearly worse at 0/5 (0-43 %) | 0:50 | [recommend.md](../site/solver/results/import_hall_8x6/recommend.md) | `[synthetic]`, 5 seeds, one map |
| Pareto: `lazy_thetastar_unknown` 27.58 s / 0.253 m, `mppi_astar` 13.51 s / 0.251 m (4/5) | 0:50 | [recommend.md](../site/solver/results/import_hall_8x6/recommend.md) | `[synthetic]` |
| Pick `thetastar_known` 5/5, median 21.90 s, 0.214 m; narrowest passage 0.65 m => `ARM=F0` | 1:05 | [recommend.md](../site/solver/results/import_hall_8x6/recommend.md) | `[synthetic]` |
| Expected for the live flight: browser seed 0 `thetastar_known` reached, 22.28 s, 0.214 m, path 9.645 m | 1:15 (narrator's reference, not on screen) | [solver_custom.json](../site/solver/results/import_hall_8x6/solver_custom.json) record seed 0 | `[synthetic]`, browser worker 10 Hz, not the flight loop |
| Fallback flight: reached, 24.96 s, 0.293 m, `outcome=arrived` | 1:15 fallback | [first_flight_bench.txt](flight-repo/results/first_flight_bench.txt), [score JSON](flight-repo/results/first_flight_bench_dstar_lite_narrow_gap_0_F0_score.json) | `[synthetic]`, narrow_gap_0, truth pose |
| Pack: `astar_known` 10/10 [0.72, 1.00] NOT PROVEN, needs 35; `mppi_astar` 10 collisions in 10 | 1:40 | [pack_hall_8x6.md](../samples/close-area-benchmark/results/pack_hall_8x6.md) | `[synthetic]`, depth_cam_87, radius 0.2 m |

Why `ARM=F0` matters, if a judge asks: with F2 the same pick class stops in front of a narrow gap.
On narrow_gap_0 (0.764 m gap) `bench:dstar_lite` with F2 ended 12.8 m from B, with F0 it reached
([first_flight_bench.txt](flight-repo/results/first_flight_bench.txt), `[synthetic]`).

## Fallback plan

| Failure | Detect | Switch to | Max time lost |
|---|---|---|---|
| CDN blocked (cdn.jsdelivr.net) | Tab 1 stays on "Loading Python" | Tab 2, `http://localhost:8000/site/solver/?pyodide=local` (filled by `tools/venue_kit.py prepare`, checked by `verify`) | 5 s |
| No network | Tab 1 errors | Tab 2 is localhost already (`python3 -m http.server 8000` from the hub root). On another laptop: `python3 tools/venue_kit.py bundle` output, `python3 serve.py` | 5 s |
| Slow browser (Quick past 35 s) | Progress counter far from 90/90 | Tab 3 (committed recommend.md) and Tab 4 PNGs; say "the recorded run" | 10 s |
| `world_from_room.py` fails | No `ok has_free_path` line | Import the committed `rooms/hall_8x6.world.json` | 5 s |
| `make first-flight` fails or is slow | No `wrote ...png` within 15 s | Committed narrow_gap_0 F0 PNG and score line | 10 s |
| Projector or laptop dies | Black screen | Laptop 2, backup video | 30 s |

Never debug on stage. Say "switching to the recording", switch, continue.

## Recording the backup

H+30 to H+36, on the demo laptop, with the pre-flight checklist done.

- Record the full 2:00 once, screen and narration, no cuts. First frame: the commit hash.
- Copy the video, `/tmp/demo/*`, `templates/flight-repo/runs/demo_hall_8x6*` and the downloaded
  `recommend.md` / `.json` to laptop 2 and a USB stick. Check the video plays offline.
- Keep the downloaded `recommend.md` from the recording: if the live one differs, the team knows why
  before the judges ask.

## Appendix: if the brief is VIO loss (H1)

Use only if the brief says the drone loses its visual odometry indoors, the room is open, and the
drone has a dense range sensor and a prior map. Replace the 1:15-1:55 rows. The claim is narrow:
the relocalization arm passed only on the open families (random, u_trap) and failed on narrow_gap,
office, warehouse, maze and glass_office
([relocalize README](../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56)).
With 4 beams the best arm reached 66-89 % against a 90 % bar
([case study](../docs/case-study/README.md#relocalization-on-4-beams)). Do not claim novelty
(prior art in [doc 10](../docs/research/close-area-nav/10-relocalization-prior-art.md)).

### Variant rows for the alternative hooks

| Time | Spoken line | On screen | Action | Fallback |
|---|---|---|---|---|
| 1:15-1:30 | "Now VIO jumps mid-flight. Without help the loop refuses to claim arrival: it ends 0.64 m from B and says unconfirmed, not arrived." | [first_flight_jump.png](flight-repo/results/first_flight_jump.png); line `reached=False final_dist_m=0.640 ... unconfirmed:1` `[synthetic]` ([first_flight_health_gate.txt](flight-repo/results/first_flight_health_gate.txt)) | Tab with the committed PNG | - |
| 1:30-1:50 | "With relocalization the drone hovers, matches its range scan to the map, re-anchors and goes on. Four loss events, zero wrong commits, 1.6 seconds of hover, arrived 0.12 m from B." | [first_flight_reloc.png](flight-repo/results/first_flight_reloc.png); line `reached=True final_dist_m=0.120 ... outcome=arrived`, `reloc ... events=4 reanchors=4 wrong_commits=0`, 29.6 s to goal `[synthetic]` ([first_flight_reloc.txt](flight-repo/results/first_flight_reloc.txt)) | Committed PNG. Live only if rehearsed: `make first-flight FAULT="--fault jump --reloc --reloc-dir ../../samples/close-area-relocalize" OUT=../runs/demo_reloc` (cwd templates/flight-repo; not run in this form) | Committed PNG and txt |
| 1:50-1:55 | "One layout, one seed. Over held-out layouts it holds on open rooms only, and not on a 4-beam sensor." | Slide with the two limits above | none | - |

`make first-flight-jump` and `make first-flight-reloc` write into the committed
`templates/flight-repo/results/`; do not run them on stage.

## Not verified

- No row was rehearsed or timed end to end; the 2:00 is the sum of the planned rows.
- The live site was fetched (page loads, 2026-11-10) but no button was clicked on it for this page.
  The recorded Import + Quick + Recommend pass was headless Chrome 140 on localhost
  ([measure_import.json](../site/solver/results/measure_import.json)). The Pareto view on hall_8x6 was
  not screenshotted; the committed [solver_pareto.png](../site/solver/results/solver_pareto.png) is
  random_0 Stress.
- `make first-flight PLANNER=bench:thetastar_known WORLD=<hall_8x6> ARM=F0` was flown once by the loop
  driver on 2026-11-10: reached, time to goal 22.3 s, min clearance 0.2133 m, path 9.626 m `[synthetic]`
  ([score](flight-repo/results/first_flight_bench_thetastar_known_hall_8x6.world_score.json),
  [PNG](flight-repo/results/first_flight_bench_thetastar_known_hall_8x6.world.png)); 38.8 s wall for the
  whole make target on a loaded laptop. The `OUT=../runs/...` and `-o /tmp/demo/...` forms and
  `pack.py --out /tmp/demo/...` were read from the Makefile and scripts, not run.
- The pack wall time on 14 workers (about 8 s in the benchmark README) is not in a committed file.
- Live Quick numbers may differ from the recorded ones: planners with keep-alive ticks are
  wall-clock dependent ([flight-repo README](flight-repo/README.md#result-2026-11-10-synthetic-venv-uv-cpython-31115-numpy-246-scipy-1171)).
- Firefox, Safari and touch were never tried with the Solver.
