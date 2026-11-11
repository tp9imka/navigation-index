# Judge drill: close-area A=>B, measured-toolkit pitch

Use this at H+36 to rehearse the hard questions for the toolkit pitch: the measured toolkit, plus a
narrow claim only if the real brief fits it ([case study](../../docs/how-it-was-built.md#summary-2-minutes),
[research decision](../../docs/research/README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is)).
The demo it backs is the 2-minute toolkit demo in [demo-script-close-area.md](../demo-script-close-area.md#script).
If the pitch leads with relocalization after VIO loss (H1), use
[judge-drill-close-area.md](judge-drill-close-area.md) instead.

State on 2026-11-10: every flight number below is `[synthetic]` (simulated room, vehicle, range
sensor and estimator, 2.5D point mass, scored on truth). None is SITL or flight. Wall times are
real, measured on an Apple M3 Max laptop. Numbers are copied from committed READMEs and result
files; none was rerun for this page. They are hub numbers. Replace them with your team's own runs
from `runs/results.md` where you have them.

## How to run the drill

1. One person reads a question from the table. The answerer has 20 s, with a timer.
2. The answer says the number and "in simulation" in the same sentence.
3. If the answerer misses the label or the caveat, read the answer below aloud and go again.
4. Go through all 11 once, then the ones the team got wrong twice more.

## Quick reference

| # | Question | Number to say | Input |
|---|---|---|---|
| 1 | A forward depth camera, not a 360 deg sensor? | Camera reached B in 6 of 6 geofenced runs, as the 360 deg fan did; +3.04 to +3.44 s on office_0 | synthetic |
| 2 | Your map is a drawing | Spec 23.98 s, 9.204 m, 8 obstacles; sketch 25.54 s, 9.629 m, 45 boxes; both reached | synthetic |
| 3 | 17 planners tie. What did the Solver decide? | No winner by success rate; Pareto view names 3 of 17 | synthetic |
| 4 | Why not your safety filter everywhere? | F2 closes gaps under about 1.4 m: 0 of 21 planners passed a 0.764 m gap with F2, 15 of 21 with F0 | synthetic |
| 5 | People walking through? | VO gate 100 of 100 reached, 0 collisions, held-out seed; A* + F2 92 %, 0 collisions, 8 % stuck | synthetic |
| 6 | What if B is unknown? | Frontier found B in 43.3 % [31.6, 55.9]; a nominal within 2 m: 88.3-100 % | synthetic |
| 7 | Why show Hybrid A* losing? | 81.9 % vs 91.2 % reached for A*, 0 % collisions for both | synthetic |
| 8 | Nothing here is novel. What is the contribution? | 21 planners x 8 room families x 2 sensors, 6720 flights; 2 own headlines failed their kill tests | synthetic |
| 9 | Brief to first flight, how long? | 6 min 7 s clone to pack verdict, agent-driven; 2 min 26 s of it commands | wall time real, flights synthetic |
| 10 | Is the arena biased? | Dropped beams mark free space behind walls; fix moves reached by -3.7 to +5.7 points | synthetic |
| 11 | The question we hope they do not ask: has any of it flown? | No number. No SITL run, no flight | - |

## Questions and answers

### 1. "Your drone has a forward depth camera, not a 360 deg sensor."

"We flew that case. A simulated 87 deg depth camera, modelled on a RealSense D435i, reached B in
6 of 6 geofenced runs, the same as the 360 deg fan, but slower: 3 to 3.4 s more on the office
map and up to 9.5 s more in the maze. One layout per family, so those are examples. In the Solver
on office_0 with that camera, 8 of 18 planners reached B in 3 of 3 runs."

- **Number:** 6 of 6 reached (2 planners x 3 worlds), +3.04 to +3.44 s on office_0, +3.54 to +9.5 s on maze_0 `[synthetic]`, one layout per family, truth pose; Solver Quick on office_0: 54 runs, 25 reached, 26 stuck, 2 collision, 1 timeout `[synthetic]`, 3 seeds.
- **Source:** [custom_sensor_0.md](../../samples/close-area-arena/results/custom_sensor_0.md#result),
  [Solver office_0 depth camera sweep](../../site/solver/README.md#result-one-quick-sweep-on-office_0-with-depth_cam_87),
  [quick_office_0_depth_cam.json](../../site/solver/results/quick_office_0_depth_cam.json).
- **Say also:** camera noise is constant over range in the sim, and no camera data was flown.

### 2. "Your map is a drawing."

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

### 3. "17 planners tie. What did the Solver decide?"

"It decided not to name a winner by success rate, because five or fifteen runs cannot separate them.
On random_0 under Stress, 15 runs per planner, 17 of 18 planners stayed tied. Inside the tie the
Pareto view, time to B against clearance, names 3 of 17. Recommend then writes the pick and the
flight command."

- **Number:** 17 tied (best 12/15, 55-93 % Wilson), Pareto-optimal 3 of 17: `lazy_thetastar_unknown` 17.69 s / 0.506 m, `dstar_lite` 20.25 s / 0.516 m, `thetastar_known` 17.08 s / 0.334 m `[synthetic]`, one map, 5 seeds x 3 variations.
- **Source:** [Stress and the Pareto view](../../site/solver/README.md#stress-and-the-pareto-view-loop-89),
  [Stress result on random_0](../../site/solver/README.md#result-one-stress-sweep-on-random_0),
  [recommend_random_0_stress.md](../../site/solver/results/recommend_random_0_stress.md).
- **Say also:** on the demo hall Quick gave 9 tied at 5/5 and 2 on the Pareto line
  ([recommend.md](../../site/solver/results/import_hall_8x6/recommend.md)).

### 4. "Why not run your safety filter everywhere?"

"Because it blocks narrow passages. The range filter F2 holds the drone 0.7 m from every return,
so it closes gaps under about 1.4 m. On a world with a 0.764 m gap no planner got through with
F2, 0 of 21; with the filter off, 15 of 21 reached B, in simulation. The Solver's Recommend
measures the narrowest passage of the map and, below 1.4 m, writes the command without the filter
and with a warning."

- **Number:** F2: 0 of 21 ids reached, all ended 11.2-16.8 m from B; F0: 15 of 21 reached `[synthetic]`, narrow_gap_0, one run per id, truth pose.
- **Source:** [Fly what the Solver picks](../flight-repo/README.md#fly-what-the-solver-picks-benchid-in-a-world-file),
  [bench_parity.txt](../flight-repo/results/bench_parity.txt),
  [first_flight_bench.txt](../flight-repo/results/first_flight_bench.txt),
  [Solver Recommend ARM rule](../../site/solver/README.md#recommend-loop-80).
- **Say also:** with the filter off, nothing stops the drone hitting what the planner missed. That
  is the trade.

### 5. "People will walk through."

"We tested that with simulated people walking at 0.5 and 1 m/s. On a held-out seed, plain A*
replanning collided in 28 % of runs. A* with the range filter had 0 collisions but got stuck in 8 %.
A velocity-obstacle gate on tracked people reached B in 100 of 100, 0 collisions. Its gain is
reaching B where the filter deadlocked, not fewer collisions."

- **Number:** `astar_vo` 100 % reached (96.3-100), 0 % collisions; `astar_f2` 92 % reached, 0 % collisions, 8 % stuck; `astar` 28 % collisions `[synthetic]`, held-out seed 1, 100 runs per arm, sign test p = 0.0078.
- **Source:** [Prediction arms](../../samples/close-area-moving-obstacles/README.md#prediction-arms-constant-velocity-tracks-space-time-a-vo-gate-ran-2026-11-10),
  [predict_0_1.md](../../samples/close-area-moving-obstacles/results/predict_0_1.md).
- **Say also:** sim people walk straight lines at constant speed and ignore the drone, which favours
  this predictor. 0 in 100 still allows a true rate up to 3.7 %.

### 6. "What if B is a marker somewhere, not a coordinate?"

"Then ask the organisers for a rough position. With B unknown, our best search, frontier
exploration, found B in 43 % of runs within 180 s, in simulation. Given a nominal within 2 m, every
search arm found it in 88-100 %, about as fast as knowing B. The map fills before the detector
has swept the room, and we did not build a detector-aware frontier."

- **Number:** frontier 43.3 % [31.6, 55.9] found, B unknown; 88.3-100 % with a nominal within 2 m `[synthetic]`, 60 runs per cell, 3 families, ideal sensor, geometric detection model.
- **Source:** [close-area-explore results](../../samples/close-area-explore/README.md#results-ran-2026-11-10-apple-m3-max-macos-2662-cpython-31210-numpy-254-scipy-1181),
  [analysis_0.md](../../samples/close-area-explore/results/analysis_0.md).

### 7. "Why show Hybrid A* losing?"

"Because it answers the question you would ask next: would a fancier planner help? We built it
and it did not, for a multirotor here. Hybrid A* reached B in 82 % against 91 % for plain A* on a
turn-limited vehicle, 0 collisions for both, in simulation. It was about 1 s faster when both
arrived. So A* stays the default, and the page says when to pick Hybrid A*."

- **Number:** 81.9 % vs 91.2 % reached; median 0.94 s faster when both reached, 152 paired runs `[synthetic]`, 8 families x 20 layouts, ideal sensor.
- **Source:** [hybrid-astar reading](../../samples/close-area-planner-hybrid-astar/README.md#reading),
  [case study: Hybrid A*](../../docs/how-it-was-built.md#hybrid-a).
- **Say also:** our own untuned implementation, no path smoothing.

### 8. "Nothing here is novel. What is the contribution?"

"Agreed, the planners and filters are published. What we add is a method and a measured toolkit:
one shared arena, 21 planners through 8 room families with 2 sensors, 6720 simulated flights, and
a browser page that ranks planners for your map. We ran kill tests against our own two headline
ideas and both failed. Those failures are in the repo with their numbers."

- **Number:** 21 planners, 8 families, 2 sensor presets, 6720 runs; safety filter 1.7 % [0.7, 3.8] collisions against a 1 % bar; relocalization on 4 beams 66-89 % against a 90 % bar `[synthetic]`.
- **Source:** [case study summary](../../docs/how-it-was-built.md#summary-2-minutes),
  [what failed and why](../../docs/how-it-was-built.md#what-failed-and-why),
  [research decision](../../docs/research/README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is).

### 9. "How long from brief to first flight?"

"One agent-driven pass, fresh clone of the repo to a scored flight and a regression verdict, took
6 minutes 7 seconds. 2 minutes 26 of that were commands: Solver 30 s, cold first flight 44 s, a
105-run pack 51 s. The flights are simulated. A team clicking by hand was not timed; the drill
page suggests budgeting 15 minutes once the room is measured."

- **Number:** 367 s total, 146 s of commands; 198 simulated runs. Wall time real (Apple M3 Max, warm uv cache), flights `[synthetic]`.
- **Source:** [cold-start-drill.md Total](../../docs/cold-start-drill.md#run-2-total),
  [timed steps](../../docs/cold-start-drill.md#run-2-timed-steps).

### 10. "Is your arena biased?"

"Yes, in one known way, and it is written down. The sim's mapper treats a dropped beam as free
space out to max range, so it can mark cells behind a wall as free. We sized it: fixing it moves
the unknown-map planners' reach rate by -3.7 to +5.7 points, inside single-seed noise. The fix is
on the backlog; the published tables carry the note."

- **Number:** dropped beams 2 % (ideal) and 5 % (crazyflie); falsely-free cells median 6.7-8.8 % => about 0.4 % with the fix (ideal); reached changes -3.7 to +1.3 points (ideal), -1.9 to +5.7 (crazyflie) `[synthetic]`, seed 0, 20 layouts x 8 families.
- **Source:** [upstream-findings section 22](../../docs/upstream-findings.md#22-close-area-arena-a-dropped-beam-marks-free-space-behind-walls),
  [dropout_fix_tables.md](../../samples/close-area-benchmark/results/dropout_fix_tables.md).
- **Say also:** the seed noise floor was not measured (that arm crashed), so "inside noise" rests
  on most per-family changes being 1-2 layouts.

### 11. The question we hope they do not ask: "Has any of this flown, or run on a real autopilot?"

"No. Everything in the toolkit is simulation: a 2.5D point mass with a velocity lag, no attitude,
wind or contact physics, scored on truth. No SITL run of the flight loop, no real flight. The
drivers for PX4, ArduPilot, Crazyflie and Tello are written from SDK docs and have not run. If we
fly here, that is the first flight, and the score line will say so."

- **Number:** no number.
- **Source:** [arena limits](../../samples/close-area-arena/README.md#limits),
  [drivers table](../drone-adapter/drivers/README.md),
  [demo script, not verified](../demo-script-close-area.md#not-verified).
- **Say also:** the only SITL evidence in the hub is a VIO bridge whose constant pose the PX4 and
  ArduPilot EKFs fused ([judge-drill-close-area.md](judge-drill-close-area.md#quick-reference), row 9).
