# Day-1 drill 2026-11: brief drops => scored first flight => regression bar (loop-92)

**Next action if you are on Day 1:** read [Blockers](#blockers) (two of them change what you type),
then follow [day1-quickstart.md](day1-quickstart.md) steps 2-6.

What this is: one coding agent followed [day1-quickstart.md](day1-quickstart.md) steps 2-6 literally,
on 2026-11-10, in a fresh clone of commit a385efb in `$TMPDIR`, for a fake brief. Every command was
timed with `date +%s` before and after. Nothing in the hub was edited; fixes are in
[Driver edits needed](#driver-edits-needed).

Input types: every flight number on this page is **synthetic** (simulated room, vehicle, range sensor,
truth pose, scored on truth). No SITL, no real flight. Wall times are real, measured on an Apple M3
Max (16 cores, shared host; load average 34.2 at the start, 6.1 at the first-flight step), Chrome
140.0.7339.208 headless, node 22.22.2, uv 0.11.23 with a warm wheel cache, host python3 3.14.6.

Brief: "Fly a PX4-class quadrotor (radius 0.2 m, v_max 1.5 m/s, forward depth camera ~87 deg, 5 m)
from A to B across an 8 x 6 m hall with pillars and tables; people may walk through; B is a landing
pad marker." Room: [samples/close-area-arena/rooms/hall_8x6.json](../samples/close-area-arena/rooms/hall_8x6.json),
copied as `rooms/our_room.json` (quickstart step 2 gotcha: use your own spec name). The room spec is
already measured, so `world_from_image.py` was not needed.

## Timed steps

Raw: [drill-2026-11/timings.csv](drill-2026-11/timings.csv). cwd per row is the quickstart's.

| step | command | wall s | outcome | blocker |
|---|---|---|---|---|
| 1 Clone | `git clone -q <this checkout> $TMPDIR/drill < /dev/null` | 6 | rc 0, 377 MB, HEAD a385efb | - |
| 2a Arena venv | `uv venv .venv && uv pip install --python .venv -r requirements.txt` | 2 | rc 0, 12 packages (warm cache) | - |
| 2b Room => world | `.venv/bin/python world_from_room.py rooms/our_room.json --preview results/room_our_room.png` | 12 | rc 0, `rooms/our_room.world.json`, 8 obstacles | B1 (overwrote a committed file) |
| 3 Solver | headless Chrome via [drill_solver.mjs](drill-2026-11/drill_solver.mjs): load, Import world JSON, Your drone (0.2 m, 1.5 m/s, depth_cam_87), Quick, headline + Pareto, Recommend button | 30 | 90 of 90 runs, 0 console errors; Python ready 4.3 s, Quick 21.05 s on K = 4; both downloads arrived | - |
| 4a Save world | `python3 -c "...recommend.json')['world']..."` (the one-liner in recommend.md) | 0 | `my_world.json`, identical to `rooms/our_room.world.json` | B3 (extra step) |
| 4b First flight | `make first-flight PLANNER=bench:thetastar_known WORLD=my_world.json ARM=F0` | 44 | rc 0, reached, cold flight-repo venv (12 packages) | - |
| 4c Same, warm | same with `OUT=warm_rerun` | 2 | rc 0, identical score line | - |
| 6a Bench venv | `uv venv .venv && uv pip install --python .venv -r requirements.txt` | 1 | rc 0 (warm cache) | - |
| 6b Write pack | copy `packs/hall_8x6.json` => `packs/our_room.json`, edit 5 keys | 0 (scripted; by hand a few minutes, not timed) | valid pack | - |
| 6c Run pack | `.venv/bin/python pack.py run packs/our_room.json --workers 4` | 51 | rc 0, 105 runs (script: 16.4 s) | B2 (Solver and pack disagree on one planner) |

Step 5 (read the score line and the PNG) is reading, folded into 4b.

## Total

| span | wall |
|---|---|
| Clone start => pack verdict (1794307252 => 1794307619) | **367 s (6 min 7 s)** |
| Commands only (sum of the rows above, without the warm re-run 4c) | 146 s (2 min 26 s) |
| Agent reading, writing the Solver driver script and checking outputs | the rest, about 3 min 40 s |

Simulated runs: 1 (room preview) + 90 (Quick) + 2 (first flight, cold and warm) + 105 (pack) = 198.
Stress and Thorough were not run: the Pareto view already named one planner, and the CPU budget was about 200 runs.

A team clicking the Solver by hand adds the clicks and the reading of recommend.md; not timed here.

## Final artefacts

- **recommend.md headline** ([recommend.md](drill-2026-11/recommend.md)): "8 planners tie at the top;
  run Thorough or more seeds to separate them (n=5 per planner, best 5/5 reached B, 95 % CI 57 %-100 %)."
  Pareto-optimal: **Theta* (any-angle), known map** (21.88 s, 0.222 m), the only point on the front.
  Command: `make first-flight PLANNER=bench:thetastar_known WORLD=my_world.json ARM=F0`; F0 because the
  narrowest passage is 0.65 m (the 0.9 m door), below 1.4 m. Synthetic, 5 seeds, depth_cam_87, truth pose.
- **First-flight score line** ([04_first_flight.txt](drill-2026-11/04_first_flight.txt),
  [score JSON](drill-2026-11/first_flight_bench_thetastar_known_my_world_score.json),
  [PNG](drill-2026-11/first_flight_bench_thetastar_known_my_world.png), 76 KB):
  `score input=synthetic adapter=world:my_world.json fault=truth planner=bench:thetastar_known safety=arm:F0 reached=True final_dist_m=0.156 t_s=23.66 collided=False min_clearance_m=0.213 ... intervened=0 keepalive=0 planner_errors=0 outcome=arrived`;
  score_log.py: reached, time to goal 22.3 s, min clearance 0.2133 m, path 9.626 m. Synthetic, arena
  default vehicle (0.15 m, 2 m/s) and ideal sensor, not the brief's drone (quickstart step 4 gotcha).
- **Pack verdict** ([pack_our_room.md](drill-2026-11/pack_our_room.md), [pack file](drill-2026-11/pack_our_room.json)):
  exit 0. `thetastar_known` **PASS** (35/35 reached, Wilson lower 0.90; 0 collisions in 35; p50 22.2 s),
  `astar_known` **PASS** (35/35; 0 collisions; p50 23.7 s), `lazy_thetastar_unknown` **FAIL** (17/35
  reached, 18 collisions). Synthetic, radius 0.2 m, v_max 1.5 m/s, depth_cam_87, 35 seeds, jitter 0.5 m.
  35 seeds because `reached_rate >= 0.9` needs 35 clean distinct runs (quickstart step 6); the shipped
  hall_8x6 pack has 10 and can only end NOT PROVEN.

Not covered by steps 2-6: people walking through (no pack key for moving obstacles; quickstart step 8
points to `run_predict.py`, 1000 runs, over this drill's budget) and B as a landing pad marker (decoder
row 32). Both were not run.

## Blockers

None stopped the path. Every command exited 0 on the first try.

| # | step | what happened | what fixed it / what should change |
|---|---|---|---|
| B1 | 2b | Using an own spec file name (`rooms/our_room.json`, as the gotcha says) still overwrote the committed `samples/close-area-arena/results/room_hall_8x6.json` ([diff](drill-2026-11/room_hall_8x6_overwrite.diff)): `--preview` implies `--fly`, which writes `results/room_<name>.json` with `<name>` from the spec's `"name"` field (world_from_room.py line 212), and the copied spec still says `"hall_8x6"`. The score line also says "on hall_8x6" | Not fixed in the drill (the clone was disposable). Change the gotcha in docs/day1-quickstart.md step 2 to say: set `"name"` in the spec too (exact text below). Optional code change: none proposed here |
| B2 | 3 vs 6c | Solver Quick and the pack disagree on the no-map planner with the same world, vehicle (0.2 m, 1.5 m/s), sensor (depth_cam_87) and the same jittered A and B on seeds 0-4: Solver `lazy_thetastar_unknown` 5/5 reached, 0 collisions; pack 2/5 on those seeds (seeds 1, 2, 3 collision at min clearance 0.1965-0.199 m, under the 0.2 m radius). Known-map planners agree: `thetastar_known` reached on all 5 seeds in both, times within 0.28 s. Cause found and fixed in loop-99: the pack inflated by the shipped 0.15 m while the Solver used the 0.2 m drone radius; after the fix they agree on all 15 runs and the 35-seed pack gives 34/35 reached ([solver_vs_pack.md](../samples/close-area-benchmark/results/pack_drill_solver_vs_pack.md)) | Did not change the pick (the Pareto pick passed the pack). Trust the pack verdict for the bar. Add a gotcha to docs/day1-quickstart.md step 6 (text below) and a to-do to find the cause (worker.js `DRIVER_PY` vs samples/close-area-benchmark/bench.py `run_one`) |
| B3 | 4a | Recommend gives `WORLD=my_world.json` plus a python one-liner to extract the world from recommend.json, although the team imported `rooms/our_room.world.json`, which is the identical file (checked with `==` on the parsed JSON) | Ran the one-liner (0 s). docs/day1-quickstart.md step 4 can say the imported file works directly (text below) |

Smaller notes, no edit needed:

- The Recommend button downloaded both `recommend.md` and `recommend.json` in headless Chrome with
  `Browser.setDownloadBehavior allow`; the "allow multiple downloads" prompt did not appear. A desktop
  Chrome may still ask (not tested).
- The world JSON carries `"radius": 0.15` (world_from_room.py default). The Solver's jitter reads the
  world radius, the pack the vehicle radius (benchmark README, Schema). Here the two gave the same A
  and B on seeds 0-4.
- Pack wall 51 s against 16.4 s inside the script: about 35 s before the first run on a fresh venv, the
  same first-start wait the quickstart reports for first-flight (205.89 s there). Not diagnosed.

## Driver edits needed

Exact replacement text. `=>` reads "replace with".

1. **docs/cheatsheets/close-area-a-to-b.md**, line 50:
   `All synthetic. One pass takes about 15 minutes once the room is measured.`
   =>
   `All synthetic. One pass took 6 min 7 s in the loop-92 drill (clone to pack verdict, agent-driven, warm uv cache; 2 min 26 s of that was commands: Solver Quick 30 s, cold first flight 44 s, 105-run pack 51 s on 4 workers), see `docs/day1-drill-2026-11.md`. Budget 15 minutes by hand once the room is measured (hand clicks not timed).`
2. **docs/day1-quickstart.md**, line 3:
   `**Next action:** run step 1, then work down. One pass is about 15 minutes once the room is measured`
   =>
   `**Next action:** run step 1, then work down. One pass took 6 min 7 s agent-driven (`docs/day1-drill-2026-11.md`); budget 15 minutes by hand once the room is measured`
3. **docs/day1-quickstart.md**, step 2, lines 52-53:
   `  - The example commands overwrite committed files (`rooms/*.world.json`, `results/room_*`). For`
   `    your room use your own spec name and `-o`, e.g. `rooms/our_room.json`.`
   =>
   `  - The example commands overwrite committed files (`rooms/*.world.json`, `results/room_*`). For`
   `    your room use your own spec file and set its `"name"` field too, e.g. `rooms/our_room.json` with`
   `    `"name": "our_room"`: `--preview` / `--fly` write `results/room_<name>.json` from that field, so a`
   `    copied hall_8x6 spec still overwrites `results/room_hall_8x6.json` (drill 2026-11, blocker B1).`
4. **docs/day1-quickstart.md**, step 2, line 49: `- Wall: not measured.`
   => `- Wall: venv 2 s (warm uv cache), world_from_room.py with --preview 12 s (drill 2026-11).`
5. **docs/day1-quickstart.md**, step 3, after the line ending `Python ready 6.8 s after navigation on a fresh profile.`, add:
   `  Custom world (hall_8x6 copy, 8 obstacles) with Your drone 0.2 m, 1.5 m/s, depth_cam_87: Quick 21.05 s for 90 runs, whole step 30 s incl. load, import and Recommend; 8 tied, 1 Pareto-optimal (drill 2026-11).`
6. **docs/day1-quickstart.md**, step 4, lines 116-117:
   `([Brief to first flight](../templates/flight-repo/README.md#brief-to-first-flight)). A `bench:` flight`
   `  with a warm venv: not measured.`
   =>
   `([Brief to first flight](../templates/flight-repo/README.md#brief-to-first-flight)). A `bench:` flight`
   `  on a custom world: 44 s with a cold flight-repo venv, 2 s warm (drill 2026-11).`
   and add a gotcha under step 4:
   `  - An imported world file works as `WORLD=` directly (e.g. `WORLD=../../samples/close-area-arena/rooms/our_room.world.json`); recommend.md's `my_world.json` one-liner gives the identical file. The OUT stem then follows the file name.`
7. **docs/day1-quickstart.md**, step 6, line 162:
   `- Wall: about 8 s (hall_8x6, 60 runs, 14 workers), about 15 s (office_crazyflie, 75 runs).`
   =>
   `- Wall: about 8 s (hall_8x6, 60 runs, 14 workers), about 15 s (office_crazyflie, 75 runs); 51 s for 105 runs on 4 workers on a fresh venv (16.4 s inside the script, drill 2026-11). On a laptop use `--workers 4`.`
   and add a gotcha under step 6:
   `  - The Solver and the pack can disagree on a no-map planner: on the drill room `lazy_thetastar_unknown` reached 5/5 in Solver Quick and 2/5 in the pack on the same seeds, A, B, vehicle and sensor (known-map planners agreed). Cause not found; the bar is the pack verdict.`

## Raw files

All in [drill-2026-11/](drill-2026-11/): [timings.csv](drill-2026-11/timings.csv), command output
(`02a_arena_venv.txt`, [02b_world_from_room.txt](drill-2026-11/02b_world_from_room.txt),
`04_first_flight.txt`, `04_first_flight_warm.txt`, `06a_bench_venv.txt`,
[06c_pack_run.txt](drill-2026-11/06c_pack_run.txt)), the world ([our_room.world.json](drill-2026-11/our_room.world.json),
[room preview](drill-2026-11/room_our_room.png)), the Solver driver and its record
([drill_solver.mjs](drill-2026-11/drill_solver.mjs), [solver_check.json](drill-2026-11/solver_check.json),
[quick_export.json](drill-2026-11/quick_export.json), [recommend.json](drill-2026-11/recommend.json)),
the pack result ([pack_our_room.json](drill-2026-11/pack_our_room.json)) and the clone's
`git status` after the drill ([clone_git_status.txt](drill-2026-11/clone_git_status.txt)).
The temporary clone was deleted after the run.
