# Cheat sheet: close-area A to B, maybe with obstacles

Briefs like "fly a drone from A to B in a close area", "through obstacles", "indoor arena",
"land on the pad / fly to the marker", "keep flying when VIO is lost". Decoder rows 31 (A to B
through obstacles), 32 (goal is a marker, pad or tag), 33 (indoor, VIO loss). Platform, sensors,
indoor or outdoor, and sim or real are unknown until Day 1: ask with the
[Day-1 intake](../day1-close-area-intake.md) first (20 minutes). Research behind this sheet:
[close-area-nav synthesis](../research/close-area-nav/README.md).

Every number below is **synthetic** (simulated layouts, vehicle and sensor) unless marked
otherwise. None is a flight or SITL result.

## 1. What judges likely want (30 s)

Completion first, then no collisions, then no manual help. IMAV 2026 indoor multiplies the score
by 1.0 onboard, 0.7 with off-board compute or beacons, 0.4 with any manual intervention
([06 task phrasing](../research/close-area-nav/06-task-phrasing-survey.md), another event's rules).
Show a replan when an obstacle moves. Say what the drone does when its own position is wrong:
estimation, not planning, broke past competitions (lane 02).

## 2. First 3 commands

From the hub root. Re-run on 2026-11-09 for this sheet (Apple M3 Max, venv on CPython 3.11.15);
outputs matched the sample READMEs.

```sh
# 1. Arena + truth scorer, straight baseline (install ~15 s, run 1.5 s)
cd samples/close-area-arena && uv venv .venv && uv pip install --python .venv -r requirements.txt \
  && .venv/bin/python run.py --planner straight --layouts 20 --seed 0 --out /tmp/arena
# 2. A* + ESDF on a known map, U-trap family (~6 s)
.venv/bin/python run.py --planner astar_esdf --layouts 20 --seed 0 --family u_trap --out /tmp/arena
# 3. Range-only baseline under estimator faults (~55 s)
.venv/bin/python run_faults.py --planner freest_beam --layouts 50 --seed 0 --out /tmp/arena
```

Command 1 prints reached 40 %, collision 0 %, stuck 60 %. Keep `--out`: without it the scripts
write to the sample's `results/`, and command 2 would overwrite the committed
`astar_esdf_u_trap_0.*` (a 50-layout, three-mode comparison) with a 20-layout known-map run.
`run.py --planner astar_esdf` is the known-map mode; the unknown-map comparison is
`python -m planners.astar_esdf --layouts 50 --seed 0` (about 7 min, writes `results/`).

Then, on the vehicle side (stdlib, about 2 s):
`(cd templates/drone-adapter && python3 -m unittest -v && python3 example_loop.py)` => 10 tests
OK, `final_distance_m=0.096 collided=False` on the mock. Fly the arena planners through the
real loop with [flight-repo](../../templates/flight-repo/README.md) (`make sim`,
`--planner arena:<name>`).

### Day-1 flow with the browser tools

All synthetic. One pass takes about 15 minutes once the room is measured.

1. **Room => world JSON.** Measured room: `world_from_room.py rooms/<room>.json`. Floor plan or
   whiteboard photo: `world_from_image.py <plan>.png --ref X1 Y1 X2 Y2 D ...` (both in
   [close-area-arena, Your room in the arena](../../samples/close-area-arena/README.md#your-room-in-the-arena-ran-2026-11-10-synthetic)).
   Both exit 1 when A and B have no free path.
2. **Solver, Quick.** Open the [Solver](../../site/solver/README.md) (live:
   [navigation-index.pages.dev/site/solver/](https://navigation-index.pages.dev/site/solver/)),
   **Import world JSON**, set **Your drone** (radius, speed, sensor), press **Quick** (5 seeds, the
   drone's sensor, truth pose).
3. **Tied? Run Thorough.** Quick often ties: on random_0, 17 of 18 planners tied at 5 of 5. **Thorough**
   = 10 seeds, ideal + crazyflie + the drone's sensor.
4. **Recommend.** Downloads `recommend.md` / `.json` with the pick, the tied set and the command to fly.
5. **Fly it in flight-repo.** From `templates/flight-repo`:
   `make first-flight PLANNER=bench:<id> WORLD=<file.json> ARM=<F0|F2>`
   ([Fly what the Solver picks](../../templates/flight-repo/README.md#fly-what-the-solver-picks-benchid-in-a-world-file)).
6. **Scenario pack as the regression bar.** Write room + drone + bar once as a
   `close-area-pack/1` file, re-run after every tuning change:
   `.venv/bin/python pack.py run packs/<name>.json --workers 14` in
   [close-area-benchmark](../../samples/close-area-benchmark/README.md#scenario-packs). Use a count
   rule (`collisions == 0`) for a safety bar on a small pack; `reached_rate >= 0.9` needs 35 clean
   runs before it can PASS.

Venue network blocks the CDN? `python3 tools/venue_kit.py prepare`, then `verify`, before the event
([day-0 runbook, Browser tools offline](../day0-runbook.md#browser-tools-offline)).

## 3. Which planner first

Read the [close-area-benchmark](../../samples/close-area-benchmark/README.md#results-ran-2026-11-09-synthetic)
matrix before writing a planner: 14 planners x 8 room families x 2 range sensors, 20 layouts per
cell, seed 0, true pose, synthetic. Cell = reached % / collision %. "Ideal" = 72 rays, 6 m, sees
glass. "4 beams" = the Crazyflie-like preset (4 x 27 deg cones, 3 m, glass invisible). Try the
picks in the browser: [playground](../../site/playground/index.html) (its advisor panel shows the
same table; it stops runs at 60 s, the benchmark allowed 120 s on maze and warehouse).

| Family | With a map (both sensors) | Without a map, ideal | Without a map, 4 beams |
|---|---|---|---|
| random clutter | `astar_known` 100 / 0 | `astar_unknown` 100 / 0 | `astar_unknown`, `astar_unknown_f2` or `dstar_lite` 100 / 0 |
| u_trap | `astar_known` 100 / 0 | `astar_unknown` 100 / 0 | `astar_unknown_f2` or `dstar_lite` 100 / 0 |
| narrow_gap (0.5-0.9 m) | `astar_known` 100 / 0 | `astar_unknown` 90 / 0 | `astar_unknown` 25 / 5 (weak) |
| office | `astar_known` 100 / 0 | `astar_unknown` 95 / 0 | `astar_unknown_f2` 50 / 5 |
| warehouse | `astar_known` 100 / 0 | `astar_unknown` 55 / 0 | none works: `bug2` 15 / 20 reaches most, `astar_unknown_f2` 0 / 0 is safest |
| forest (open poles) | `astar_known` 100 / 0 | `astar_unknown` 100 / 0 (reactive planners tie) | `dstar_lite` 100 / 0 |
| maze | `astar_known` 100 / 0 | `astar_unknown` 95 / 0 | `astar_unknown_f2` 55 / 0 |
| glass_office | `astar_known` 100 / 0 | `astar_unknown` 95 / 0 | none works: `dstar_lite` 10 / 65; `freest_beam` or `dwa_mem` 5 / 5 are safest |

How to read it:

- **Get a map if you can.** A floor plan, a layout file or one slow first pass of the room. All
  three prior-map planners (`astar_known`, `informed_rrt_star`, `astar_mpc`) score 100 / 0 in all
  16 cells; start from `astar_known` (`planners/astar_esdf.py`). Informed RRT* needed more than
  60 s in 30 of its 40 maze + warehouse successes. The map is exact and the pose true here, so
  100 % is an upper bound.
- **No map, dense sensor:** `astar_unknown` (`astar_esdf` with `known_map=False`). `dstar_lite`
  ends the same way in 153 of 160 runs and searches a few times faster; it matters only on maps
  beyond about 40 x 40 m ([close-area-planner-dstar](../../samples/close-area-planner-dstar/README.md)).
- **No map, 4 beams:** `astar_unknown` + F2 range filter. It is the only map-free row at 50 % or
  more in office and maze. Warehouse and glass rooms have no working map-free planner: ask for the
  map. On 72 beams do not put F2 under it by default: it freezes in doors and aisles (0 % reached
  in office, warehouse, maze, narrow_gap and glass_office).
- **Reactive planners** (APF, VFH+, DWA, Bug2, TangentBug) only fit open clutter: 0-40 % in
  office, warehouse and maze on ideal. On 4 beams, 3 s of scan memory cuts DWA collisions sharply
  (office 55 => 0 %), at the cost of runs ending stuck.

Situations the matrix does not cover:

| Situation | Start with | Why |
|---|---|---|
| Moving obstacles (people walking through) | A* replan + F2 range filter ([close-area-moving-obstacles](../../samples/close-area-moving-obstacles/README.md)) | A* alone collided in 14-36 % of runs; with F2 0 %, 16 % stuck; APF 0-2 %. With tracks: A* + VO gate (`run_predict.py`) reached B in 100 of 100 held-out runs, 0 collisions, vs 92 % for A* + F2 (people walk straight lines) |
| Windows, bars, B at another height | `planners/astar_esdf_3d.py` on a prior 3D map ([window_bar](../../samples/close-area-arena/README.md#altitude-windows-and-bars-ran-2026-11-09-synthetic)) | 2.5D at 1 m reached 14 %, 3D 100 %, 0 % collisions (50 layouts) |
| Estimator faults, no map | `freest_beam` (inside `run_faults.py`) | Range-only, so faults cut reach, not safety; A* under faults is in [close-area-safety-filter](../../samples/close-area-safety-filter/README.md) |
| Goal B is a tag or pad | Any of the above to bring the tag into view, then [fiducial-goal-apriltag](../../samples/fiducial-goal-apriltag/README.md) `final_approach.py` | Tag-relative servo for the last metres |

Do not start from `straight`: it never steers, so it is only the floor.

## 4. Numbers you can cite

All synthetic, seed 0, from the sample READMEs. "Re-run" means repeated for this sheet with
identical results.

- A* + ESDF, 50 layouts per family: straight reached 26 % / 0 % / 0 % (random / u_trap /
  narrow_gap); known map 100 % on all three; unknown map 100 % / 100 % / 80 %, 0 % collision.
  Seed 0 was also the tuning seed; a held-out seed-3 spot check (10 u_trap layouts) matched
  ([arena README](../../samples/close-area-arena/README.md#a--esdf-grid-planner-ran-2026-11-09-synthetic)).
  Not re-run (about 7 min).
- freest_beam under faults, 50 layouts: reached 86 % on truth, 58 % with VIO dark zones, 42 %
  jump, 40 % bias, 46 % dropout; 0 % collision in every case. Re-run, 55 s
  ([estimator and faults](../../samples/close-area-arena/README.md#estimator-and-faults-ran-2026-11-09-synthetic)).
- Reactive planners on a 4-beam Crazyflie-like fan, 50 layouts: VFH+ collides in 72-98 %, APF
  in 8-54 %. With 72 beams, APF with escape reaches 92 % on u_trap, without escape 2 %. Re-run,
  about 112 s ([close-area-planner-reactive](../../samples/close-area-planner-reactive/README.md)).
- AprilTag goal: a 0.16 m tag36h11 is detected in 90 % or more of frames out to 5 m frontal and
  2 m at 70 deg; the tag-relative final approach ends within 0.1 m in 50 of 50 seeds, worst
  0.031 m. Final approach re-run, 39 s on 8 processes
  ([fiducial-goal-apriltag](../../samples/fiducial-goal-apriltag/README.md)).
- Safety filter, kill test A, 100 layouts: with every obstacle visible to the 360 deg fan, PX4-CBF and CP-stop have 0 % collisions in every VIO fault case (bare A* 7 % under a 0.5 m jump); with 2 map-only obstacles per layout PX4-CBF collides in 3-11 %, all with those obstacles. Not re-run ([close-area-safety-filter](../../samples/close-area-safety-filter/README.md)).
- Integrity-aware filter (the old headline), held-out seeds: **FAIL**. Ours collides in 2.5 % [1.1, 5.7] of held-out jump runs and reaches B in 0.55 as many jump runs as PX4-CBF; MR-CBF with a hand-tuned fixed 0.2 m bound stays at 1.0 % [0.3, 2.9] or less in every case on seeds 0-2 (95 % Wilson intervals). Not re-run ([Part e](../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).
- Walking people, 50 layouts: A* replanning alone collides in 14 % (0.5 m/s) and 36 % (1.0 m/s) of runs; A* + PX4-CBF 0 % at 16 % stuck; APF 0 % / 2 %. Not re-run ([close-area-moving-obstacles](../../samples/close-area-moving-obstacles/README.md)).
- Crazyflie 4-beam preset on the glass family, 50 layouts: collisions 90 % (freest_beam) and 100 % (A* unknown map); the ideal 72-beam fan 4 % and 10 %. Not re-run ([sensor realism](../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic)).
- First flight: `make first-flight` in [flight-repo](../../templates/flight-repo/README.md#brief-to-first-flight) flies arena A* + PX4-CBF through the 20 Hz loop: reached in 19.76 s, min clearance 0.83 m; with the VIO jump fault it ends `unconfirmed` 0.64 m from B instead of claiming arrival. One layout. Not re-run.
- Corridor MPC (OSQP) vs the A* carrot follower, 50 layouts per family: both 100 % reached, 0 % collision; MPC 21.97 vs 24.23 s to goal through narrow gaps; QP 0.22 ms median on an M3 Max laptop. Not re-run ([close-area-planner-mpc](../../samples/close-area-planner-mpc/README.md)).
- RRT* vs A* on the same grid: A* plans a 0.4 m gap in 100 % of layouts, RRT* with 1000 samples in 28.3 % (5000: 85.7 %); keep A* as the default. Not re-run ([close-area-planner-sampling](../../samples/close-area-planner-sampling/README.md)).
- Benchmark, 20 layouts per cell: without a map on 4 beams, `astar_unknown` reaches office 35 % (25 % collision), warehouse 0 % (50 %), glass_office 5 % (65 %); with a map every prior-map planner 100 / 0. Not re-run ([close-area-benchmark](../../samples/close-area-benchmark/README.md)).
- VIO lost, 100 layouts: no relocalization reached 64 % (dropout) / 36 % (jump); committing to the best scan-to-map match and re-checking it reached 100 % / 100 %, 0 % collisions, but with 2-4 wrong commits; a hover-until-unique rule deadlocks in a corridor (20 of 20). Hover plus a short info-gain move after 1 s: 99-100 % reached, 0 wrong commits, held-out seed 1 included; corridor 80 %. Not re-run ([close-area-relocalize](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b)). Held-out seeds 2-4 narrowed it: 100 %, 0 wrong commits on random and u_trap only; office 94.4 %, glass_office 83.3 %, narrow_gap 85.6 %, warehouse 97.2 % with 33 wrong commits; 48-64 % on 4 beams with a yaw-spin; 7 % collisions with unmapped added obstacles ([held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56)).
- Replan cost: a full 200 x 200 x 50 scipy EDT took 183 ms median on an M3 Max (synthetic grid),
  so a 20 x 20 x 5 m ESDF at 0.1 m fits a 2-5 Hz replan. Not re-run.
- **Real dataset** reference for VIO drift: OpenVINS ATE 0.36 m over 278 m on UZH-FPV
  indoor_forward_3, RPE over 10 m 1.5 %
  ([relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md)).

More in [evidence matrix section 14](../evidence-matrix.md#14-close-area-ab).

## 5. Platform notes

All four drivers are **unrun stubs written from docs**
([drivers README](../../templates/drone-adapter/drivers/README.md)); do its 3 bench checks
before any planner flight. Rules per platform: [frames.md](../../templates/drone-adapter/frames.md).

- **PX4**: `px4_mavsdk.py`, Offboard `set_velocity_ned` at 20 Hz, keep-alive started before
  `offboard.start()`. `VelocityNedYaw` takes an absolute heading, not a yaw rate. PX4 no longer
  plans around obstacles; Collision Prevention only stops, in Position mode only. Our planner
  sends the setpoints.
- **ArduPilot**: `ardupilot_pymavlink.py`, GUIDED, `SET_POSITION_TARGET_LOCAL_NED` mask 3527
  (velocity only), stops after 3 s without commands. BendyRuler / Dijkstra's in GUIDED is the
  zero-code fallback (not tested in the hub). Indoors the EKF needs an origin first.
- **Crazyflie**: `crazyflie_cflib.py`, `send_velocity_world_setpoint` at 20 Hz. Yaw-rate sign
  on current firmware not confirmed. Multi-ranger: 4 horizontal beams to about 4 m, plus up.
  Planning usually runs on the laptop over Crazyradio.
- **Tello**: `tello_djitellopy.py`, `send_rc_control` takes stick values, not m/s; the driver
  refuses to fly until the scales are set. No obstacle sensor, lands after 15 s without a command.
- **Sim**: the arena for planner work; [sitl-docker](../../samples/sitl-docker/) PX4 SIH or
  ArduCopter 4.6.3 (ran, headless, no obstacles) for credibility.

## 6. Top traps

1. **4-beam fans collide.** A memoryless 4-beam scan has no return from corners between beams:
   VFH+ 72-98 % collisions, APF 8-54 % (synthetic). Keep a scan memory or a map, yaw-sweep, or
   cap speed hard.
2. **Glass and thin obstacles.** Range sensors miss them. In BatDeck real office flights with a
   single forward VL53L1, 10 of 10 flights crashed and most crashes were undetected glass doors
   (**real**, preprint, [08 Crazyflie sensing limits](../research/close-area-nav/08-crazyflie-sensing-limits.md)).
   Put glass, poles and nets in the map as map-only obstacles.
3. **VIO faults and overconfidence.** Reported covariance is not trustworthy: published NEES of
   131-363 against 3 expected for a sliding-window VI filter on EuRoC (Lisus et al. RA-L 2023,
   [09 VIO NEES](../research/close-area-nav/09-vio-nees-feasibility.md)). Gate on ODOMETRY
   `quality`, `reset_counter` and rejected fusions
   ([03 localization](../research/close-area-nav/03-close-area-localization.md)). In the arena,
   an overconfident estimator changes nothing for the planners, which do not read `sigma_xy`.
4. **Arena limits.** 2.5D point mass, ideal ray casts by default, axis-aligned boxes and
   cylinders. Glass only with the cone sensor presets (`run_sensors.py`); dynamic obstacles only
   as constant-speed people in close-area-moving-obstacles (no prediction, random family only). A* under VIO faults collides in 1-7 % of runs without a filter
   ([close-area-safety-filter](../../samples/close-area-safety-filter/README.md), synthetic).
5. **Frames and keep-alive.** ENU vs NED, absolute heading vs yaw rate, stick values vs m/s.
   Command +x on the bench and watch which way it moves before the first planner flight.
6. **F2 vs narrow gaps.** F2 holds the drone centre 0.7 m from every return, so it cannot pass gaps
   under about 1.4 m. On narrow_gap_0 (0.764 m gap) every flight-repo `bench:` id with F2 ended
   11.2-16.8 m from B; with F0 dstar_lite reached in 24.96 s (synthetic,
   [flight-repo](../../templates/flight-repo/README.md#all-ids-on-narrow_gap_0-resultsbench_paritypy)).
   Recommend switches to `ARM=F0` with a warning below 1.4 m.
7. **Quick ties on easy maps.** On random_0 a 5-seed Quick sweep tied 17 of 18 planners at 5 of 5
   (95 % Wilson 57-100 %); only `straight` dropped out (synthetic,
   [Solver](../../site/solver/README.md#result-quick-sweeps-on-narrow_gap_0-and-random_0-loop-87-quick--5-seeds)).
   A tie is not a winner: run Thorough or a harder map.
8. **Frontier search is not a search for B.** With B unknown, nearest-frontier found B in 43.3 %
   [31.6, 55.9] of runs in 180 s; with a nominal B within 2 m every arm found it in 88.3-100 %. The
   6 m range sensor maps the room before the 2 m detector sees B (synthetic,
   [close-area-explore](../../samples/close-area-explore/README.md)). Ask for a nominal B.
9. **Planners on 4 beams.** Benchmark winners on the ideal 72-ray fan collide on the Crazyflie-like
   4-beam preset: MPPI on the A* path office 85 % collisions vs 25 % for A*
   ([close-area-planner-mppi](../../samples/close-area-planner-mppi/README.md)); unknown-map Theta*
   office collisions 25 % => 35-60 %
   ([close-area-planner-thetastar](../../samples/close-area-planner-thetastar/README.md)). All
   synthetic. Run the Solver with your drone's sensor, not ideal.

## 7. Stretch goal

Both close-area headlines were narrowed by their own kill tests
([decision](../research/README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is)).
Pitch the measured toolkit (14 planners x 8 rooms x 2 sensors, the browser playground, the kill
tests) plus the narrow claim that fits the real brief:

- **Open room, dense range sensor, map given:** relocalization after VIO loss. Hover, match the
  scan against the map with up to 5 hypotheses, fly one short collision-checked move when they
  tie, never commit on a tie. 100 % reached with 0 wrong commits on random and u_trap, held-out
  seeds 2-4 included; not in offices, warehouses, mazes or on 4 beams (section 4). Demo command:
  first block of the [close-area-relocalize Run section](../../samples/close-area-relocalize/README.md#run).
- **People walking through:** a range safety filter (PX4-CBF style) under any planner: 14-36 % =>
  0 % collisions ([close-area-moving-obstacles](../../samples/close-area-moving-obstacles/README.md)).

Claim novelty for neither: the relocalization mechanism exists (Jensfelt 2001, AF-MCL 2026,
[doc 10](../research/close-area-nav/10-relocalization-prior-art.md)), and the integrity-aware
safety filter failed: a hand-tuned fixed 0.2 m bound matched its safety
([Part e](../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).
Pitch: [close-area story](../../templates/pitch/close-area-story.md); demo:
[demo-script-close-area](../../templates/demo-script-close-area.md).

## 8. Links

- Decoder: [rows 31, 32, 33](../problem-statement-decoder.md#the-table); Day-1 routing:
  [day1-close-area-intake](../day1-close-area-intake.md); Challenge 2 page:
  [challenge-2-autonomous-flight](../challenge-2-autonomous-flight.md).
- Samples: [close-area-arena](../../samples/close-area-arena/README.md) (and its
  [CONTRACT.md](../../samples/close-area-arena/CONTRACT.md), [log_format.md](../../samples/close-area-arena/log_format.md)
  for `score_log.py`), [close-area-planner-reactive](../../samples/close-area-planner-reactive/README.md),
  [fiducial-goal-apriltag](../../samples/fiducial-goal-apriltag/README.md),
  [close-area-planner-mpc](../../samples/close-area-planner-mpc/README.md),
  [close-area-planner-sampling](../../samples/close-area-planner-sampling/README.md),
  [close-area-benchmark](../../samples/close-area-benchmark/README.md),
  [close-area-planner-dstar](../../samples/close-area-planner-dstar/README.md),
  [close-area-planner-dwa-bug](../../samples/close-area-planner-dwa-bug/README.md),
  [close-area-relocalize](../../samples/close-area-relocalize/README.md),
  [close-area-safety-filter](../../samples/close-area-safety-filter/README.md),
  [close-area-moving-obstacles](../../samples/close-area-moving-obstacles/README.md) (`run_predict.py`: VO gate),
  [close-area-explore](../../samples/close-area-explore/README.md),
  [close-area-planner-thetastar](../../samples/close-area-planner-thetastar/README.md),
  [close-area-planner-mppi](../../samples/close-area-planner-mppi/README.md),
  [close-area-planner-hybrid-astar](../../samples/close-area-planner-hybrid-astar/README.md),
  [vio-to-mavlink-bridge](../../samples/vio-to-mavlink-bridge/), [sitl-docker](../../samples/sitl-docker/).
- Templates: [drone-adapter](../../templates/drone-adapter/README.md) +
  [drivers](../../templates/drone-adapter/drivers/README.md),
  [flight-repo](../../templates/flight-repo/README.md).
- Browser: [home page](https://navigation-index.pages.dev/), [Solver](../../site/solver/README.md),
  [playground](../../site/playground/README.md). How the toolkit was built:
  [case study](../case-study/README.md).
- Research: [01 planning](../research/close-area-nav/01-planning-and-mapping.md),
  [02 sims and platforms](../research/close-area-nav/02-sims-platforms-competitions.md),
  [03 localization](../research/close-area-nav/03-close-area-localization.md),
  [07 kill search](../research/close-area-nav/07-pl-margin-prior-art.md).
- Cards: [PX4](../integration-cards/px4__px4-autopilot.md),
  [MAVSDK-Python](../integration-cards/mavlink__mavsdk-python.md),
  [ArduPilot](../integration-cards/ardupilot__ardupilot.md),
  [OpenVINS](../integration-cards/rpng__open_vins.md),
  [Crazyflie firmware](../integration-cards/bitcraze__crazyflie-firmware.md).
