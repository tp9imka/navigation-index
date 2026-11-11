# Hard questions a reviewer will ask, with 20-second answers

Use this in the last rehearsal before the talk, for the close-area A=>B task. Two question sets,
one per story in [close-area-story.md](close-area-story.md):

- [Part A: measured-toolkit story](#part-a-measured-toolkit-story) (the default, decided 2026-11-09
  evening): the measured toolkit, plus a narrow claim only if the real brief fits it.
- [Part B: relocalization story (H1)](#part-b-relocalization-story-h1): the talk leads with
  relocalization after VIO loss.

Every answer is 2-4 sentences, fits in 20 s spoken, and carries a number with its input label, or
says "no number". Numbers are copied from committed READMEs and result files; none was rerun for
this page. They are hub numbers. Replace them with your own runs from `runs/results.md` where you
have them.

## How to run the drill

1. One person reads a question from the table. The answerer has 20 s, with a timer.
2. The answer says the number and its label in the same sentence ("in simulation", "in SITL").
3. If the answerer misses the label or the caveat, read the answer below aloud and go again.
4. Go through every question in your part once, then the ones you got wrong twice more
   (Part B: the 5 you got wrong).

What reviewers score, from 10 past competitions ([06 TL;DR](../../docs/research/close-area-nav/06-task-phrasing-survey.md#tldr)):
completion and accuracy first, then speed; crash, out of bounds and human touch disqualify;
off-board compute is priced (IMAV 0.7 vs 1.0 onboard, rulebook). So lead every answer with
"reached B" and "collisions", not with method names.

## Part A: measured-toolkit story

The demo it backs is the 2-minute toolkit demo in [live-demo-script-close-area.md](live-demo-script-close-area.md#script)
([how it was built](../../docs/how-it-was-built.md#summary-2-minutes),
[research decision](../../docs/research/README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is)).

State on 2026-11-10: every flight number in Part A is `[synthetic]` (simulated room, vehicle, range
sensor and estimator, 2.5D point mass, scored on truth). None is SITL or flight. Wall times are
real, measured on an Apple M3 Max laptop.

### Part A quick reference

| # | Question | Number to say | Input |
|---|---|---|---|
| A1 | A forward depth camera, not a 360 deg sensor? | Camera reached B in 6 of 6 geofenced runs, as the 360 deg fan did; +3.04 to +3.44 s on office_0 | synthetic |
| A2 | Your map is a drawing | Spec 23.98 s, 9.204 m, 8 obstacles; sketch 25.54 s, 9.629 m, 45 boxes; both reached | synthetic |
| A3 | 17 planners tie. What did the Solver decide? | No winner by success rate; Pareto view names 3 of 17 | synthetic |
| A4 | Why not your safety filter everywhere? | F2 closes gaps under about 1.4 m: 0 of 21 planners passed a 0.764 m gap with F2, 15 of 21 with F0 | synthetic |
| A5 | People walking through? | VO gate 100 of 100 reached, 0 collisions, held-out seed; A* + F2 92 %, 0 collisions, 8 % stuck | synthetic |
| A6 | What if B is unknown? | Frontier found B in 43.3 % [31.6, 55.9]; a nominal within 2 m: 88.3-100 % | synthetic |
| A7 | Why show Hybrid A* losing? | 81.9 % vs 91.2 % reached for A*, 0 % collisions for both | synthetic |
| A8 | Nothing here is novel. What is the contribution? | 21 planners x 8 room families x 2 sensors, 6720 flights; 2 own headlines failed their kill tests | synthetic |
| A9 | Brief to first flight, how long? | 6 min 7 s clone to pack verdict, agent-driven; 2 min 26 s of it commands | wall time real, flights synthetic |
| A10 | Is the arena biased? | Dropped beams mark free space behind walls; fix moves reached by -3.7 to +5.7 points | synthetic |
| A11 | The question we hope nobody asks: has any of it flown? | No number. No SITL run, no flight | - |

### A1. "Your drone has a forward depth camera, not a 360 deg sensor."

"We flew that case. A simulated 87 deg depth camera, modelled on a RealSense D435i, reached B in
6 of 6 geofenced runs, the same as the 360 deg fan, but slower: 3 to 3.4 s more on the office
map and up to 9.5 s more in the maze. One layout per family, so those are examples. In the Solver
on office_0 with that camera, 8 of 18 planners reached B in 3 of 3 runs."

- **Number:** 6 of 6 reached (2 planners x 3 worlds), +3.04 to +3.44 s on office_0, +3.54 to +9.5 s on maze_0 `[synthetic]`, one layout per family, truth pose; Solver Quick on office_0: 54 runs, 25 reached, 26 stuck, 2 collision, 1 timeout `[synthetic]`, 3 seeds.
- **Source:** [custom_sensor_0.md](../../samples/close-area-arena/results/custom_sensor_0.md#result),
  [Solver office_0 depth camera sweep](../../site/solver/README.md#result-one-quick-sweep-on-office_0-with-depth_cam_87),
  [quick_office_0_depth_cam.json](../../site/solver/results/quick_office_0_depth_cam.json).
- **Say also:** camera noise is constant over range in the sim, and no camera data was flown.

### A2. "Your map is a drawing."

"Yes, and we measured what the drawing costs. The same 8 by 6 m hall went in twice: once as a
measured room spec, once as a pencil sketch. A* with the known map reached B on both, in simulation.
The sketch gave 45 boxes instead of 8 obstacles, a path 0.425 m longer and 1.56 s slower. The image
scale error is about 0.35 % for a 400 px reference."

- **Number:** spec 23.98 s, min clearance 0.2212 m, path 9.204 m, 8 obstacles; sketch 25.54 s, 0.2153 m, 9.629 m, 45 boxes `[synthetic]`, one run each, truth pose. The sketch is a synthetic drawing, not a photo.
- **Source:** [room_hall_8x6.json](../../samples/close-area-arena/results/room_hall_8x6.json),
  [room_sketch_hall.json](../../samples/close-area-arena/results/room_sketch_hall.json),
  [Your room in the arena](../../samples/close-area-arena/README.md#your-room-in-the-arena-ran-2026-11-10-synthetic).
- **Say also:** boxes sit on 0.1 m cells, so a door can lose up to 0.2 m on the planner's grid;
  no perspective correction.

### A3. "17 planners tie. What did the Solver decide?"

"It decided not to name a winner by success rate, because five or fifteen runs cannot separate them.
On random_0 under Stress, 15 runs per planner, 17 of 18 planners stayed tied. Inside the tie the
Pareto view, time to B against clearance, names 3 of 17. Recommend then writes the pick and the
flight command."

- **Number:** 17 tied (best 12/15, 55-93 % Wilson), Pareto-optimal 3 of 17: `lazy_thetastar_unknown` 17.69 s / 0.506 m, `dstar_lite` 20.25 s / 0.516 m, `thetastar_known` 17.08 s / 0.334 m `[synthetic]`, one map, 5 seeds x 3 variations.
- **Source:** [Solver README, section "Stress and the Pareto view"](../../site/solver/README.md),
  [Stress result on random_0](../../site/solver/README.md#result-one-stress-sweep-on-random_0),
  [recommend_random_0_stress.md](../../site/solver/results/recommend_random_0_stress.md).
- **Say also:** on the demo hall Quick gave 9 tied at 5/5 and 2 on the Pareto line
  ([recommend.md](../../site/solver/results/import_hall_8x6/recommend.md)).

### A4. "Why not run your safety filter everywhere?"

"Because it blocks narrow passages. The range filter F2 holds the drone 0.7 m from every return,
so it closes gaps under about 1.4 m. On a world with a 0.764 m gap no planner got through with
F2, 0 of 21; with the filter off, 15 of 21 reached B, in simulation. The Solver's Recommend
measures the narrowest passage of the map and, below 1.4 m, writes the command without the filter
and with a warning."

- **Number:** F2: 0 of 21 ids reached, all ended 11.2-16.8 m from B; F0: 15 of 21 reached `[synthetic]`, narrow_gap_0, one run per id, truth pose.
- **Source:** [Fly what the Solver picks](../flight-repo/README.md#fly-what-the-solver-picks-benchid-in-a-world-file),
  [bench_parity.txt](../flight-repo/results/bench_parity.txt),
  [first_flight_bench.txt](../flight-repo/results/first_flight_bench.txt),
  [Solver README, section "Recommend" (ARM rule)](../../site/solver/README.md).
- **Say also:** with the filter off, nothing stops the drone hitting what the planner missed. That
  is the trade.

### A5. "People will walk through."

"We tested that with simulated people walking at 0.5 and 1 m/s. On a held-out seed, plain A*
replanning collided in 28 % of runs. A* with the range filter had 0 collisions but got stuck in 8 %.
A velocity-obstacle gate on tracked people reached B in 100 of 100, 0 collisions. Its gain is
reaching B where the filter deadlocked, not fewer collisions."

- **Number:** `astar_vo` 100 % reached (96.3-100), 0 % collisions; `astar_f2` 92 % reached, 0 % collisions, 8 % stuck; `astar` 28 % collisions `[synthetic]`, held-out seed 1, 100 runs per arm, sign test p = 0.0078.
- **Source:** [Prediction arms](../../samples/close-area-moving-obstacles/README.md#prediction-arms-constant-velocity-tracks-space-time-a-vo-gate-ran-2026-11-10),
  [predict_0_1.md](../../samples/close-area-moving-obstacles/results/predict_0_1.md).
- **Say also:** sim people walk straight lines at constant speed and ignore the drone, which favours
  this predictor. 0 in 100 still allows a true rate up to 3.7 %.

### A6. "What if B is a marker somewhere, not a coordinate?"

"Then ask whoever set the task for a rough position. With B unknown, our best search, frontier
exploration, found B in 43 % of runs within 180 s, in simulation. Given a nominal within 2 m, every
search arm found it in 88-100 %, about as fast as knowing B. The map fills before the detector
has swept the room, and we did not build a detector-aware frontier."

- **Number:** frontier 43.3 % [31.6, 55.9] found, B unknown; 88.3-100 % with a nominal within 2 m `[synthetic]`, 60 runs per cell, 3 families, ideal sensor, geometric detection model.
- **Source:** [close-area-explore results](../../samples/close-area-explore/README.md#results-ran-2026-11-10-apple-m3-max-macos-2662-cpython-31210-numpy-254-scipy-1181),
  [analysis_0.md](../../samples/close-area-explore/results/analysis_0.md).

### A7. "Why show Hybrid A* losing?"

"Because it answers the question you would ask next: would a fancier planner help? We built it
and it did not, for a multirotor here. Hybrid A* reached B in 82 % against 91 % for plain A* on a
turn-limited vehicle, 0 collisions for both, in simulation. It was about 1 s faster when both
arrived. So A* stays the default, and the page says when to pick Hybrid A*."

- **Number:** 81.9 % vs 91.2 % reached; median 0.94 s faster when both reached, 152 paired runs `[synthetic]`, 8 families x 20 layouts, ideal sensor.
- **Source:** [hybrid-astar reading](../../samples/close-area-planner-hybrid-astar/README.md#reading),
  [how it was built: Hybrid A*](../../docs/how-it-was-built.md#hybrid-a).
- **Say also:** our own untuned implementation, no path smoothing.

### A8. "Nothing here is novel. What is the contribution?"

"Agreed, the planners and filters are published. What we add is a method and a measured toolkit:
one shared arena, 21 planners through 8 room families with 2 sensors, 6720 simulated flights, and
a browser page that ranks planners for your map. We ran kill tests against our own two headline
ideas and both failed. Those failures are in the repo with their numbers."

- **Number:** 21 planners, 8 families, 2 sensor presets, 6720 runs; safety filter 1.7 % [0.7, 3.8] collisions against a 1 % bar; relocalization on 4 beams 66-89 % against a 90 % bar `[synthetic]`.
- **Source:** [how it was built, summary](../../docs/how-it-was-built.md#summary-2-minutes),
  [what failed and why](../../docs/how-it-was-built.md#what-failed-and-why),
  [research decision](../../docs/research/README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is).

### A9. "How long from brief to first flight?"

"One agent-driven pass, fresh clone of the repo to a scored flight and a regression verdict, took
6 minutes 7 seconds. 2 minutes 26 of that were commands: Solver 30 s, cold first flight 44 s, a
105-run pack 51 s. The flights are simulated. A team clicking by hand was not timed; the drill
page suggests budgeting 15 minutes once the room is measured."

- **Number:** 367 s total, 146 s of commands; 198 simulated runs. Wall time real (Apple M3 Max, warm uv cache), flights `[synthetic]`.
- **Source:** [cold-start-drill.md Total](../../docs/cold-start-drill.md#run-2-total),
  [timed steps](../../docs/cold-start-drill.md#run-2-timed-steps).

### A10. "Is your arena biased?"

"Yes, in one known way, and it is written down. The sim's mapper treats a dropped beam as free
space out to max range, so it can mark cells behind a wall as free. We sized it: fixing it moves
the unknown-map planners' reach rate by -3.7 to +5.7 points, inside single-seed noise. The fix is
on the backlog; the published tables carry the note."

- **Number:** dropped beams 2 % (ideal) and 5 % (crazyflie); falsely-free cells median 6.7-8.8 % => about 0.4 % with the fix (ideal); reached changes -3.7 to +1.3 points (ideal), -1.9 to +5.7 (crazyflie) `[synthetic]`, seed 0, 20 layouts x 8 families.
- **Source:** [upstream-findings section 22](../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls),
  [dropout_fix_tables.md](../../samples/close-area-benchmark/results/dropout_fix_tables.md).
- **Say also:** the seed noise floor was not measured (that arm crashed), so "inside noise" rests
  on most per-family changes being 1-2 layouts.

### A11. The question we hope nobody asks: "Has any of this flown, or run on a real autopilot?"

"No. Everything in the toolkit is simulation: a 2.5D point mass with a velocity lag, no attitude,
wind or contact physics, scored on truth. No SITL run of the flight loop, no real flight. The
drivers for PX4, ArduPilot, Crazyflie and Tello are written from SDK docs and have not run. If we
fly here, that is the first flight, and the score line will say so."

- **Number:** no number.
- **Source:** [arena limits](../../samples/close-area-arena/README.md#limits),
  [drivers table](../drone-adapter/drivers/README.md),
  [demo script, not verified](live-demo-script-close-area.md#not-verified).
- **Say also:** the only SITL evidence in the hub is a VIO bridge whose constant pose the PX4 and
  ArduPilot EKFs fused ([Part B quick reference](#part-b-quick-reference), row B9).

## Part B: relocalization story (H1)

Use this set when the talk leads with relocalization after VIO loss (H1 in
[close-area-story.md](close-area-story.md#h1-relocalization-after-vio-loss-the-pivot-if-the-kill-test-fails)),
because the safety-filter headline failed on held-out seeds.

State on 2026-11-09: every relocalization number is `[synthetic]` (simulated layouts, vehicle,
VIO-like estimator and 72-beam range fan, A* known-map planner). The only `[SITL]` evidence is
the VIO bridge fusing a constant pose. The only `[real]` number is the OpenVINS drift on a public
dataset.

### Part B quick reference

| # | Question | Number to say | Input |
|---|---|---|---|
| B1 | Is this only simulation? | 100 % reached, 0 wrong commits on open layouts only; 83-97 % in office, maze, warehouse, narrow gap, glass office; drift calibrated to real OpenVINS RPE 1.5 % / 10 m | synthetic; real (UZH-FPV) |
| B2 | Why 2.5D? | 3D ESDF rebuild 183 ms median vs 1.5 ms in 2D; yaw search: 5 deg error 38 % => 100 % reached | synthetic (laptop timing) |
| B3 | Only seed 0? | Held-out seeds 2-4 x 7 families: PASS on random and u_trap only (100 %, 0 wrong) | synthetic |
| B4 | New vs Tan 2025 / existing relocalization? | Our separation score 70 % vs Fox-style 80 % in the corridor | synthetic |
| B5 | Why not just add more sensors? | 72 beams: 4-10 % collisions on glass; 4 beams: 90-100 % | synthetic |
| B6 | Crazyflie with 4 beams? | Spin + move: 48 / 64 % reached vs 98 / 100 % on 72 beams, 0 wrong commits | synthetic |
| B7 | People walking? | A* replan 14 / 36 % collisions; with range filter 0 %, 16 % stuck | synthetic |
| B8 | VIO lost next to glass? | glass_office (fan sees glass): 83.3 % reached, 16-18 % collisions; unmapped obstacles: 7 % collisions | synthetic |
| B9 | PX4 / ArduPilot? | EKF fused the bridge's pose on both SITLs; constant pose only | SITL |
| B10 | Your safety filter idea? | Fixed 0.2 m bound worst 1.0 %; ours 2.5 % on held-out jumps | synthetic |
| B11 | Path to product and certification? | No number | - |
| B12 | Commit-at-once also reached 100 %. Why not? | 8 of 20 wrong commits in the corridor, 7.3-9.4 s flown on them | synthetic |
| B13 | Is it really the innovation test doing the work? | 227-331 triggers per 100 runs; without it 80 / 71 % | synthetic |
| B14 | What if the room was never mapped? | Map from an outbound flight: 93.9 / 92.9 % reached, 2 % collisions | synthetic |
| B15 | How fast, and does it run onboard? | 0.4 s median recovery; 1.7-1.9 ms per scan (20-23 ms with yaw search) on a laptop | synthetic |

### B1. "Is this only simulation?"

"Yes, the relocalization results are simulation only. Over 100 random layouts per fault, hover +
match + one disambiguating move reached B in 99-100 % with 0 collisions and 0 wrong commits,
against 36-64 % with the estimator alone. The sim's VIO drift is calibrated against a real number,
OpenVINS at 1.5 % RPE over 10 m on the UZH-FPV dataset (ATE 0.36 m over 278.3 m). On held-out
seeds that holds only in open rooms; in offices, mazes and warehouses it reached 83-97 %, with
up to 33 wrong commits in warehouses. Not measured: SITL with the relocalizer, real flight."

- **Number:** 99-100 % reached vs 36-64 % on random layouts; held-out seeds 2-4: 100 % on random and u_trap, 83.3-97.2 % in five other families `[synthetic]`; RPE 1.5 % over 10 m, ATE 0.36 m `[real]`, 2 runs, a long FPV flight, not our course.
- **Source:** [relocalize disambiguating moves](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout),
  [held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults),
  [arena drift calibration](../../samples/close-area-arena/README.md#estimator-and-faults-ran-2026-11-09-synthetic),
  [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md#results).

### B2. "Why 2.5D?"

"Because the question is the estimator, not the altitude, and we needed thousands of exact, seeded
runs on a laptop. A full 3D ESDF rebuild of a 20 x 20 x 5 m room took 183 ms median against
1.5 ms in 2D, and pybullet has no macOS arm64 wheel. The price: no overhangs and no altitude
changes. The matcher searches yaw within +-15 deg: a 5 deg heading error alone dropped reach to
38 % without that search and 100 % with it; a 180 deg flip in a symmetric corridor still fails."

- **Number:** 182.95 ms (3D) vs 1.48 ms (2D) median EDT, Apple M3 Max `[synthetic]` timing; yaw search 38 % => 100 % reached at +-5 deg, 100 random layouts, seed 2 `[synthetic]`.
- **Source:** [arena results (EDT timing)](../../samples/close-area-arena/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181),
  [arena limits](../../samples/close-area-arena/README.md#limits),
  [yaw search](../../samples/close-area-relocalize/README.md#yaw-search-3-dof-relocalization),
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits).

### B3. "Only seed 0?"

"No. The move design was chosen on seed 0, then flown once on seed 1 with nothing changed: the
Fox-style move arm reached 100 % under both dropout and jump, 0 collisions, 0 wrong commits. Be
honest about one thing: the matcher thresholds were calibrated on seed-1 static poses, so seed 1
is held out for the flights and the move, not for the thresholds. Seeds 2-4 across 7 room types
then passed only in open rooms: 100 % with 0 wrong commits on random and u_trap, and a FAIL in
the other five."

- **Number:** seed 1, 100 layouts per fault: 100 / 100 % reached, 0 wrong commits; seeds 2-4, 180 runs per family: random and u_trap 100.0 % [97.9, 100.0], office 94.4 %, glass_office 83.3 %, warehouse 97.2 % with 33 wrong commits `[synthetic]`.
- **Source:** [held-out check, seed 1](../../samples/close-area-relocalize/README.md#held-out-check-seed-1-independent-rerun),
  [held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults),
  [disamb_random_1.md](../../samples/close-area-relocalize/results/disamb_random_1.md),
  [thresholds](../../samples/close-area-relocalize/README.md#what-is-in-it).

### B4. "What is new vs Tan 2025 / existing relocalization work?"

"Tan et al. IROS 2025 already sets safety-filter margins from fault-excluded estimates on a PX4
drone; that is one reason we dropped the filter as our headline. Choosing a move to separate
pose hypotheses is Fox, Burgard and Thrun 1998, and our own separation score did not beat a
Fox-style information-gain move: 70 % vs 80 % in the corridor. What is ours is the composition:
loss triggers, innovation test, ratio-persistence acceptance, the move, and never committing on a tie."

- **Number:** corridor reach 70 % (ours) vs 80 % (Fox-style), 20 runs `[synthetic]`.
- **Source:** [07 verdict (Tan 2025, Zhang/Li/Clark)](../../docs/research/close-area-nav/07-pl-margin-prior-art.md#1-verdict),
  [innovation-prior-art 01](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md#2-prior-art),
  [relocalize verdict](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout).

### B5. "Why not just add more sensors?"

"More beams help a lot: on the glass layouts the ideal 72-beam fan collided in 4-10 %, a
Crazyflie-like 4-beam deck in 90-100 %. But no ToF ranger sees glass, and the platform is chosen
by whoever set the task. The relocalizer adds no sensor: it reuses the range scan the drone already
has for avoidance."

- **Number:** glass family, 50 layouts: 4 / 10 % collisions (72 beams) vs 90 / 100 % (4 beams) `[synthetic]`.
- **Source:** [arena sensor realism](../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic),
  [08 Crazyflie limits](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md#1-bottom-line).

### B6. "What happens on a Crazyflie with 4 beams?"

"It does not work well, and we measured it in simulation. The matcher needs 10 returns per scan,
so on 4 beams it accepted nothing until we added a yaw spin that stacks a quarter turn. With the
spin and the move it reached B in 48 % (dropout) and 64 % (jump) of runs, against 98-100 % on 72
beams, still with 0 wrong commits, after a median 9-12 s of spinning. Under dropout that is worse
than not relocalizing at all (64 %)."

- **Number:** 48 / 64 % reached, 3 / 7 % collisions, 0 wrong commits, 100 random layouts, seed 0, yaw is truth in the sim `[synthetic]`. Context: without a map 4 beams drop the unknown-map A* from 95 to 35 % reached in office layouts.
- **Source:** [4-beam spin](../../samples/close-area-relocalize/README.md#relocalization-with-a-4-beam-sensor-hover-and-yaw-spin),
  [acceptance rule](../../samples/close-area-relocalize/README.md#what-is-in-it),
  [benchmark crazyflie preset](../../samples/close-area-benchmark/README.md#preset-crazyflie),
  [benchmark reading](../../samples/close-area-benchmark/README.md#reading).

### B7. "What if there are people walking?"

"Relocalization was only run on static, exactly mapped rooms; people were not in those runs.
For the planner, A* replanning alone hit walking people in 14 % of runs at 0.5 m/s and 36 % at
1.0 m/s; with a PX4-CBF-style range filter on top, 0 % at both, at the cost of 16 % stuck. So
the range filter stays in our stack under the relocalizer."

- **Number:** 14 / 36 % collisions => 0 %, 16 % stuck, 50 layouts, truth pose `[synthetic]`. Relocalization with people: no number.
- **Source:** [moving-obstacles results](../../samples/close-area-moving-obstacles/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181),
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits).

### B8. "What if VIO is lost next to glass?"

"Glass offices are one of our failing cases. With a sensor that does see the glass, relocalization
reached B in 83 % of runs and collided in 16-18 %, with no wrong commit; small pose errors are
enough to clip a doorway. A ranger that misses glass was not run with the relocalizer. The known
risk is the move after the hover: with obstacles missing from the map it collided in 7 % of runs,
and every hit on a missing obstacle came after a move, because the move check trusts the map."

- **Number:** glass_office, held-out seeds 2-4, 72-beam fan that sees glass: 83.3 % reached, 16-18 % collisions; unmapped added obstacles: 7 % collisions, 12 of 14 into the unmapped obstacles, all after a move, seed 2 `[synthetic]`. Relocalization with a glass-blind ranger: no number.
- **Source:** [held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults),
  [stale map](../../samples/close-area-relocalize/README.md#imperfect-prior-map),
  [arena sensor realism](../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic).

### B9. "How does this get onto PX4 / ArduPilot?"

"The relocalizer runs on the companion and re-anchors the pose it sends as MAVLink ODOMETRY,
incrementing reset_counter so the EKF treats the step as a reset (doc 03 advice, not tested). The bridge for that message was checked in
SITL on PX4 v1.17.0 and ArduCopter 4.6.3: both EKFs fused it, with a constant pose on the ground.
Setpoints go out through PX4 Offboard or ArduPilot GUIDED drivers that are written from the SDK
docs and not yet run on a vehicle."

- **Number:** EKF fusion flags on (PX4 `cs_ev_pos: True`; ArduPilot "using external nav data"), constant pose only `[SITL]`. Drivers: no number (unrun).
- **Source:** [vio-to-mavlink-bridge SITL run](../../samples/vio-to-mavlink-bridge/README.md#run-against-sitl-ran-2026-11-06),
  [drivers platform table](../drone-adapter/drivers/README.md#platform-table),
  [flight-repo driver swap](../flight-repo/README.md#swap-the-mock-for-a-real-driver).

### B10. "What did your safety filter idea show?"

"It failed against a tuned fixed bound. A plain 0.2 m margin stayed at 1.0 % collisions or less in
every case on seeds 0-2; ours collided in 2.5 % of held-out jump runs and reached B 0.56 as often
as the range-only filter on jumps. Four of our seven jump collisions ended while hovering, so the
hover rule was the leak. That is why we lead with relocalization, and keep the range filter."

- **Number:** F4 0.2 m worst 1.0 % [0.3, 2.9]; ours 2.5 % [1.1, 5.7] held-out jump; reach ratio 0.56 `[synthetic]`.
- **Source:** [safety-filter Part e verdict](../../samples/close-area-safety-filter/README.md#verdict-against-doc-04-section-34-random-family-seeds-0-2-300-runs-per-cell-synthetic),
  [Part e answers](../../samples/close-area-safety-filter/README.md#answers).

### B11. "What is the path to product and certification?"

"We would not certify the relocalizer. It ships as a candidate pose next to the stock EKF, behind a
simple monitor, with the autopilot's own failsafe as the fallback: the ASTM F3269 runtime-assurance
pattern. The monitor and fallback carry the safety argument. We claim no assurance level and no compliance."

- **Number:** no number.
- **Source:** [path-to-product section 4](../../docs/path-to-product.md#4-runtime-assurance-ship-the-new-algorithm-next-to-a-trusted-baseline),
  [section 3](../../docs/path-to-product.md#3-certification-and-assurance-map-in-plain-language).

### B12. "Commit-at-once also reached 100 %. Why not use it?"

"In random rooms it got lucky: the innovation test corrected its wrong commits later. In a
symmetric corridor it committed to a pose 0.59-1.43 m wrong in 8 of 20 runs and flew 7.3-9.4 s on
it. Without the innovation test, that kind of wrong commit gave 40 % collisions at the corridor
exit. Ours reached 80 % there with 0 wrong commits."

- **Number:** 8 of 20 wrong commits; 40 % collisions without the test; ours 80 %, 0 wrong, one corridor geometry `[synthetic]`.
- **Source:** [corridor case](../../samples/close-area-relocalize/README.md#symmetric-case-a-2-m-x-148-m-corridor),
  [disamb_corridor.md](../../samples/close-area-relocalize/results/disamb_corridor.md).

### B13. "Is it really relocalization, or the innovation test doing the work?"

"Partly the innovation test, and we say so. It fires 227-331 times per 100 runs, so the system is
also a continuous map-based correction, not only loss recovery. With reported-loss triggers only,
commit-at-once drops to 80 / 71 % reached and hypothesis tracking to 67 / 76 %."

- **Number:** 227-331 triggers per 100 runs; 80 / 71 % and 67 / 76 % without the test (dropout / jump) `[synthetic]`.
- **Source:** [relocalize results](../../samples/close-area-relocalize/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181),
  [limits](../../samples/close-area-relocalize/README.md#limits).

### B14. "What if the room was never mapped?"

"Then we map it on the way out. In simulation the drone built its map flying A to B, lost VIO on
the way back, and relocalized against that self-built map: 93.9 % (dropout) and 92.9 % (jump)
reached, 2 % collisions, but 13 and 14 wrong commits. With no first pass at all there is
nothing to match; then the plan is hover, then land, and that fallback is not measured."

- **Number:** self-built map: 93.9 / 92.9 % reached, 2 % collisions, 13 / 14 wrong commits (map frame), 100 layouts, one seed (2) `[synthetic]`. No first pass: no number.
- **Source:** [stale map, e_selfmap rung](../../samples/close-area-relocalize/README.md#imperfect-prior-map),
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits),
  [H1 reviewer questions](close-area-story.md#h1-relocalization-after-vio-loss-the-pivot-if-the-kill-test-fails).

### B15. "How fast is it, and does it run onboard?"

"Median 0.4 s from loss to a confirmed pose; when a move was needed, about 2-3 s. The corridor is
the slow case: about 11 s and several moves. Scan matching costs 1.7-1.9 ms per scan median on an Apple
laptop, about 20-23 ms with the yaw search; on 4 beams the spin alone takes a median 9-12 s. It
was not timed on a flight computer, and the hover in the sim is perfect."

- **Number:** 0.4 s median; 1.95-2.9 s after a move; corridor 11.0 s; 1.7-1.9 ms per scan (max 2.8 ms), 20-23 ms with yaw search (12-worker load); 4-beam spin 9-12 s median per loss event `[synthetic]`, laptop timing.
- **Source:** [disambiguating moves](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout),
  [yaw search](../../samples/close-area-relocalize/README.md#yaw-search-3-dof-relocalization),
  [4-beam spin](../../samples/close-area-relocalize/README.md#relocalization-with-a-4-beam-sensor-hover-and-yaw-spin),
  [held-out check](../../samples/close-area-relocalize/README.md#held-out-check-seed-1-independent-rerun),
  [relocalize results](../../samples/close-area-relocalize/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181).

### Part B: not verified

- No answer in Part B was rehearsed or timed. The 20 s fit is a word-count estimate (about 50-70 words).
  Answers B1, B2, B3, B6, B8, B14 and B15 grew in a later revision and may now run past 20 s.
- Numbers were copied from the sample READMEs and result files listed; no sample was rerun for this page.
- Question B8: relocalization with a ranger that misses glass was not run; the glass_office rows
  use the 72-beam fan, which sees glass.
- Questions B4, B7 and B9 were not re-checked against the later runs: B7 still says "exactly mapped
  rooms" and B9 still calls the reset_counter step "not tested", while doc 10 section 4 has since
  read the autopilot code (not run).
- Tan 2025 and Zhang/Li/Clark come from the hub's doc 07, which read them on arXiv; their code was not run.
- The IMAV 0.7 off-board factor comes from doc 06, which parsed the rulebook PDF with a crude parser.

### Part B: verified since (all synthetic)

- Question B6, "4 beams never reach the 10-return rule": measured. Without a yaw spin the matcher
  accepted 0 poses on the crazyflie preset
  ([4-beam](../../samples/close-area-relocalize/README.md#relocalization-with-a-4-beam-sensor-hover-and-yaw-spin)).

### Part B: refuted since (all synthetic)

- The old answer B1 and B3 line "99-100 %, 0 wrong commits" as a general result: on held-out seeds
  2-4 it holds on random and u_trap only
  ([held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults)).
- The old answer B14 "no number": a self-built map gave 93.9 / 92.9 % reached
  ([stale map](../../samples/close-area-relocalize/README.md#imperfect-prior-map)).
