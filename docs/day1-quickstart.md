# Day-1 quickstart: fresh clone => flown, scored first flight => regression bar

**Next action:** run step 1, then work down. One pass took 6 min 7 s agent-driven ([day1-drill-2026-11.md](day1-drill-2026-11.md)); budget 15 minutes by hand once the room is measured
([cheat sheet](cheatsheets/close-area-a-to-b.md#day-1-flow-with-the-browser-tools)), plus up to 4
minutes for the first cold venv (step 4).

For the EDGE internal hackathon (18 Nov 2026), brief likely "drone A=>B in a close area with
obstacles". Ask the organiser questions first: [day1-close-area-intake](day1-close-area-intake.md)
(20 minutes). Every number on this page is **synthetic** (simulated room, vehicle, sensor and
estimator, scored on truth), quoted from the linked README or results file. None is a flight or
SITL result. "From source" marks an expected line read from the script, not from a README.

## 1. Clone

```sh
git clone -q https://github.com/tp9imka/navigation-index < /dev/null
```

- Source: URL from [case-study](case-study/README.md) (the `origin` remote); `-q` and `< /dev/null`
  from [day1-dry-run step 1](day1-dry-run.md#1-clone-wall-5485-s-on-the-attempt-that-finished-1-hop-agentsmd)
  and [AGENTS.md](../AGENTS.md).
- cwd: any parent folder. Last line: none (`-q`).
- Wall: 54.85 s for a local clone of 66 MB on a loaded machine, 0.26 s CPU (dry run).
- Gotchas: without `< /dev/null` the clone hung past the 120 s agent tool timeout. Run every long
  command (clone, venv install, first run) with stdin closed or in the background.

## 2. Room => world JSON

Build the arena venv once (cheat sheet "First 3 commands", install about 15 s):

```sh
cd samples/close-area-arena && uv venv .venv && uv pip install --python .venv -r requirements.txt
```

Then one of ([arena, Your room in the arena](../samples/close-area-arena/README.md#your-room-in-the-arena-ran-2026-11-10-synthetic)):

```sh
# measured room => JSON spec (walls with door gaps, pillars, tables, A, B; format in the script's docstring)
.venv/bin/python world_from_room.py rooms/hall_8x6.json --preview results/room_hall_8x6.png
# floor plan or whiteboard photo => boxes; PNG/JPG needs Pillow (PGM/PBM do not)
uv pip install --python .venv -r requirements-image.txt
.venv/bin/python world_from_image.py rooms/sketch_hall.png --ref 40 40 440 40 8.0 --origin-px 40 340 \
    --a-m 0.8 0.8 --b-m 7.2 1.0 -o rooms/sketch_hall.world.json --preview results/room_sketch_hall.png
```

- cwd: `samples/close-area-arena`.
- Score line (README): `astar_known on hall_8x6: reached, time to goal 23.98 s, min clearance 0.2212 m, path 9.204 m, 8 obstacles (synthetic, truth pose)`.
  Last line (from source, `world_from_room.finish`): `wrote results/room_hall_8x6.json, results/room_hall_8x6.png`.
- Wall: venv 2 s (warm uv cache), world_from_room.py with --preview 12 s (drill 2026-11).
- Gotchas:
  - Both CLIs exit 1 when A and B have no free path (0.15 m radius + 0.1 m), or on a bad spec.
  - The example commands overwrite committed files (`rooms/*.world.json`, `results/room_*`). For
    your room use your own spec file and set its `"name"` field too, e.g. `rooms/our_room.json` with
    `"name": "our_room"`: `--preview` / `--fly` write `results/room_<name>.json` from that field, so a
    copied hall_8x6 spec still overwrites `results/room_hall_8x6.json` (drill 2026-11, blocker B1).
  - Axis-aligned boxes only; `world_from_room.py` rejects a diagonal wall. Any dark mark in an image
    becomes an obstacle; no perspective correction. A door can lose up to 0.2 m on the planner grid.
  - `--ref X1 Y1 X2 Y2 D`: two pixel points and their distance in metres; a 100 px reference gives
    +-1.4 % scale error.

## 3. Solver: rank planners on that world

Live: [navigation-index.pages.dev/site/solver/](https://navigation-index.pages.dev/site/solver/). Local,
from the hub root ([Solver README](../site/solver/README.md)):

```sh
python3 -m http.server 8000
```

then open `http://localhost:8000/site/solver/`. Clicks, in order:

1. **Import world JSON** => your `*.world.json` from step 2.
2. **Your drone**: radius, v_max, a_max, sensor preset or Custom (beams, FoV, range), yaw.
3. **Quick** (5 seeds, the drone's sensor, truth pose).
4. Tied? Read the **Pareto view** (median time to B vs min clearance). Still tied: **Stress**
   (drone sensor + crazyflie + one VIO fault, 5 seeds), then **Thorough** (10 seeds).
5. **Recommend** => `recommend.md` / `recommend.json` with the pick, the tied set and the step-4 command.

- Expected headline on an easy map: `17 planners tie at the top; run Thorough or more seeds to separate them`
  (random_0, [Recommend result](../site/solver/README.md#result-quick-sweeps-on-narrow_gap_0-and-random_0-loop-87-quick--5-seeds)).
- Wall (headless Chrome 140, M3 Max, 4 workers, 18 planners): Quick 48.3 s (random_0, 90 runs),
  68.1 s (narrow_gap_0); Stress 166.3 s (random_0, 270 runs,
  [Stress](../site/solver/README.md#stress-and-the-pareto-view-loop-89)). Thorough: not measured.
  Python ready 6.8 s after navigation on a fresh profile.
  Custom world (hall_8x6 copy, 8 obstacles) with Your drone 0.2 m, 1.5 m/s, depth_cam_87: Quick 21.05 s for 90 runs, whole step 30 s incl. load, import and Recommend; 8 tied, 1 Pareto-optimal (drill 2026-11, synthetic).
- Gotchas:
  - A tie is not a winner. On random_0 Quick tied 17 of 18; Stress still left 17 tied, 3 Pareto-optimal.
  - Recommend switches to `ARM=F0` with a warning when the narrowest passage is below 1.4 m.
  - A custom world comes out as `my_world.json`: save it with the one-line python command in
    `recommend.md` (that command was not run in the README).
  - Two downloads from one click may make Chrome ask to allow multiple downloads (button not clicked in tests).
  - Not run in a browser by the scripts: Thorough, a custom vehicle, the Custom sensor.
  - The live site and a plain local server load Pyodide from cdn.jsdelivr.net (22 MB cold). Blocked? Step 7.

## 4. Fly the pick: `make first-flight`

From [flight-repo, Fly what the Solver picks](../templates/flight-repo/README.md#fly-what-the-solver-picks-benchid-in-a-world-file)
(cheat sheet form):

```sh
make first-flight PLANNER=bench:<id> WORLD=<file.json> ARM=<F0|F2>
make first-flight PLANNER=bench:dstar_lite WORLD=../../site/playground/presets/narrow_gap_0.json
```

Copied out of the hub (the H+0 team-repo case, [Run it](../templates/flight-repo/README.md#run-it)):

```sh
make first-flight HUB=/path/to/navigation-index PLANNER=bench:dstar_lite WORLD=/path/to/navigation-index/site/playground/presets/narrow_gap_0.json
make first-flight ARENA=/path/to/hub/samples/close-area-arena SAFETY=/path/to/hub/samples/close-area-safety-filter
```

- cwd: `templates/flight-repo` (or your copy). `WORLD=` is relative to that cwd, e.g.
  `../../samples/close-area-arena/rooms/our_room.world.json`.
- Last lines ([copied_out_dry_run.txt](../templates/flight-repo/results/copied_out_dry_run.txt),
  default flight): `wrote results/first_flight_score.json`, then `wrote results/first_flight.png`.
  With `PLANNER=`/`WORLD=` the stem is `first_flight_<planner>_<world stem>` (Makefile `OUT`), or `OUT=my_run`.
- Wall: cold 205.89 s (whole target, 2.77 s CPU: waiting, cause not found; budget 4 minutes);
  copied-out cold venv 99.74 s; warm 4.94 s and 2.48 s
  ([Brief to first flight](../templates/flight-repo/README.md#brief-to-first-flight)). A `bench:` flight
  on a custom world: 44 s with a cold flight-repo venv, 2 s warm (drill 2026-11).
  - An imported world file works as `WORLD=` directly (e.g. `WORLD=../../samples/close-area-arena/rooms/our_room.world.json`); recommend.md's `my_world.json` one-liner gives the identical file. The OUT stem then follows the file name.
- Gotchas:
  - **F2 cannot pass gaps under about 1.4 m.** On narrow_gap_0 (0.764 m gap) every `bench:` id with F2
    ended 11.2-16.8 m from B; with F0 dstar_lite reached in 24.96 s
    ([All ids on narrow_gap_0](../templates/flight-repo/README.md#all-ids-on-narrow_gap_0-resultsbench_paritypy)). Use `ARM=F0` there.
  - Copied out without `HUB=`: rc 2 in 0.02 s, prints the path hint, creates nothing.
  - The command flies the arena default vehicle and ideal sensor, truth pose, seed 0, exact A and B,
    not the drone you set in the Solver (Recommend "What flew").
  - `bench:astar_mpc` does not load (osqp is not in the arena requirements).
  - Runs time out at 60 s (120 s for maze and warehouse). `keepalive>0` means the 30 ms planner budget
    was missed: that run end is wall-clock dependent.
  - `make bench-list` prints the valid `bench:` ids. `make test && make sim` must pass after every
    change ([flight-repo AGENTS.md](../templates/flight-repo/AGENTS.md)).

## 5. Read the score line and the PNG

Two outputs per flight ([Result](../templates/flight-repo/README.md#result-2026-11-09-synthetic-macos-arm64-uv-picked-cpython-31115-numpy-246)):

- `main.py` line: `score input=synthetic ... reached=True final_dist_m=0.165 t_s=21.10 collided=False min_clearance_m=0.827 ... outcome=arrived ...`.
  Check `reached`, `collided`, `min_clearance_m`, `outcome` (`arrived`, `unconfirmed` or `timeout`),
  `intervened` (filter changed the setpoint) and `keepalive`. `t_s` includes the 1.0 s arrival dwell.
- `score_log.py` block: `outcome reached`, `time to goal 19.76 s`, `min clearance 0.8268 m`,
  `path length 24.068 m`. This is the truth score from the 20 Hz log.
- `results/<OUT>.png`: planned path (orange lines) vs flown path. A flight stuck at a door with the
  plan running through it is the F2 case above, not a planner failure.
- `unconfirmed`: the estimate was near B but health was not `ok` for 1.0 s within 10 s; the loop
  refuses to claim arrival ([Arrival rule](../templates/flight-repo/README.md#arrival-rule-flightlooppy)).

## 6. Encode the bar as a scenario pack

Write room + drone + bar once as `close-area-pack/1`, re-run after every tuning change
([benchmark, Scenario packs](../samples/close-area-benchmark/README.md#scenario-packs)). Model it
on [packs/hall_8x6.json](../samples/close-area-benchmark/packs/hall_8x6.json): `worlds` (path
relative to the pack file), `vehicle`, `sensor`, `planners`, `seeds`, `criteria`, e.g.
`{"reached_rate": ">= 0.9", "collisions": "== 0", "time_to_goal_p50_s": "<= 30"}`.

```sh
uv venv .venv && uv pip install --python .venv -r requirements.txt   # arena deps + osqp
.venv/bin/python pack.py run packs/hall_8x6.json --workers 14           # ~8 s, results/pack_hall_8x6.*
```

- cwd: `samples/close-area-benchmark`. Venv install time: not measured.
- Last line ([pack_hall_8x6_stdout.txt](../samples/close-area-benchmark/results/pack_hall_8x6_stdout.txt),
  1 worker): `wall 21.1 s for 60 runs on 1 workers; wrote results/pack_hall_8x6.json, .md`.
  Exit code 0 = at least one planner passes every criterion, 1 = none does, 2 = invalid pack.
- Wall: about 8 s (hall_8x6, 60 runs, 14 workers), about 15 s (office_crazyflie, 75 runs); 51 s for 105 runs on 4 workers on a fresh venv (16.4 s inside the script, drill 2026-11). On a laptop use `--workers 4`.
  - The Solver and the pack can disagree on a no-map planner: on the drill room `lazy_thetastar_unknown` reached 5/5 in Solver Quick and 2/5 in the pack on the same seeds, A, B, vehicle and sensor (known-map planners agreed). Suspected cause: the Solver's worker plans with the drone radius, the pack's benchmark loop inflates by 0.15 m (being checked, loop item 99). Until then the bar is the pack verdict.
- Gotchas:
  - **Use a count rule for safety** (`"collisions": "== 0"`), not `collision_rate <= 0`, which can
    never pass. A count rule says only "0 in these n runs": 15 clean runs support a rate of at most 0.20.
  - `reached_rate >= 0.9` needs 35 clean distinct runs before it can PASS (0.8 needs 16). Both
    shipped packs exit 1: `astar_known` is NOT PROVEN on sample size only (10 or 15 runs).
  - The pack radius changes the vehicle and scoring, not planner inflation (0.15 m fixed). The bench
    loop has no yaw policy, which matters for `depth_cam_87`.
  - `--out results/<stem>` sets the output stem; default `results/pack_<name>`.

## 7. Offline fallbacks

Before the event, with network, from the hub root
([day-0 runbook, Browser tools offline](day0-runbook.md#browser-tools-offline)):

```sh
python3 tools/venue_kit.py prepare
python3 tools/venue_kit.py verify
python3 tools/venue_kit.py bundle
```

- Last lines (from source and `--help`): `prepare` and `verify` end `PASS` or `FAIL`; `bundle` ends
  `use: unzip venue-kit.zip -d venue-kit && cd venue-kit && python3 serve.py  => http://localhost:8000/site/playground/`.
- Wall: not measured. Disk: about 30 MB, 7 files for the manual vendoring
  ([playground, Offline](../site/playground/README.md#offline--blocked-cdn)).
- Gotchas: `verify` needs a Chrome already on the machine (`CHROME=...`); it never installs one.
  Do not commit `site/playground/pyodide-local/`.
- Wheels, Docker images, datasets: [templates/offline-kit](../templates/offline-kit/README.md),
  first command `python3 prep.py --dry-run --profile standard` (cwd `templates/offline-kit`). Its pip
  caches target Python 3.12 by default; the flight-repo venv was built on uv CPython 3.11.15, so pass
  `--python-version 3.11` or pin `uv venv --python 3.12` (not tested together).

## 8. Where next

- Decoder rows 31 (obstacles), 32 (visual goal B), 33 (indoor VIO loss):
  `python3 tools/query.py decode "<statement>"` (1.86 s in the dry run), table in
  [problem-statement-decoder](problem-statement-decoder.md#the-table).
- One page per brief: [cheat sheet close-area A to B](cheatsheets/close-area-a-to-b.md) (planner per room and sensor, top traps).
- People walking through: `.venv/bin/python run_predict.py --layouts 50 --seeds 0,1 --workers 14`
  in `samples/close-area-moving-obstacles` (own `.venv`, its Run section), about 45 s for 1000 runs; A* + VO gate reached B in
  100 of 100 held-out runs, 0 collisions, vs 92 % for A* + F2
  ([VO gate](../samples/close-area-moving-obstacles/README.md#prediction-arms-constant-velocity-tracks-space-time-a-vo-gate-ran-2026-11-10)).
- B is a marker at an unknown spot: `.venv/bin/python bench.py --layouts 20 --seed 0 --jobs 14` in
  `samples/close-area-explore` (own `.venv`), about 8 min on 14 processes; frontier found B in 43.3 % with B unknown, 88.3-100 %
  with a nominal B within 2 m ([close-area-explore](../samples/close-area-explore/README.md)). Ask for a nominal B.
- VIO lost: `make first-flight-reloc` in flight-repo, then
  [close-area-relocalize](../samples/close-area-relocalize/README.md) (holds on open rooms only).
