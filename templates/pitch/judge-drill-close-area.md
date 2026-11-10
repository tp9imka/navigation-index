# Judge drill: close-area A=>B, relocalization pitch (H1)

For the default toolkit pitch (decided 2026-11-09 evening) use [judge-drill-toolkit.md](judge-drill-toolkit.md); this page is for the H1 variant.

Use this at H+36 to rehearse the hard questions for the close-area pitch. The pitch leads with
relocalization after VIO loss (H1 in [close-area-story.md](close-area-story.md#h1-relocalization-after-vio-loss-the-pivot-if-the-kill-test-fails)),
because the safety-filter headline failed on held-out seeds. Every answer below is 2-4 sentences,
fits in 20 s spoken, and carries a number with its input label, or says "no number".

State on 2026-11-09: every relocalization number is `[synthetic]` (simulated layouts, vehicle,
VIO-like estimator and 72-beam range fan, A* known-map planner). The only `[SITL]` evidence is
the VIO bridge fusing a constant pose. The only `[real]` number is the OpenVINS drift on a public
dataset. Numbers are copied from the sample READMEs and result files; none was rerun for this page.
They are hub numbers. Replace them with your team's own runs from `runs/results.md` where you have them.

## How to run the drill

1. One person reads a question from the table. The answerer has 20 s, with a timer.
2. The answer must say the number and its label in the same sentence ("in simulation", "in SITL").
3. If the answerer misses the label or the caveat, read the answer below aloud and go again.
4. Go through all 15 once, then the 5 the team got wrong twice more.

What judges score, from 10 past events ([06 TL;DR](../../docs/research/close-area-nav/06-task-phrasing-survey.md#tldr)):
completion and accuracy first, then speed; crash, out of bounds and human touch disqualify;
off-board compute is priced (IMAV 0.7 vs 1.0 onboard, rulebook). So lead every answer with
"reached B" and "collisions", not with method names.

## Quick reference

| # | Question | Number to say | Input |
|---|---|---|---|
| 1 | Is this only simulation? | 100 % reached, 0 wrong commits on open layouts only; 83-97 % in office, maze, warehouse, narrow gap, glass office; drift calibrated to real OpenVINS RPE 1.5 % / 10 m | synthetic; real (UZH-FPV) |
| 2 | Why 2.5D? | 3D ESDF rebuild 183 ms median vs 1.5 ms in 2D; yaw search: 5 deg error 38 % => 100 % reached | synthetic (laptop timing) |
| 3 | Only seed 0? | Held-out seeds 2-4 x 7 families: PASS on random and u_trap only (100 %, 0 wrong) | synthetic |
| 4 | New vs Tan 2025 / existing relocalization? | Our separation score 70 % vs Fox-style 80 % in the corridor | synthetic |
| 5 | Why not just add more sensors? | 72 beams: 4-10 % collisions on glass; 4 beams: 90-100 % | synthetic |
| 6 | Crazyflie with 4 beams? | Spin + move: 48 / 64 % reached vs 98 / 100 % on 72 beams, 0 wrong commits | synthetic |
| 7 | People walking? | A* replan 14 / 36 % collisions; with range filter 0 %, 16 % stuck | synthetic |
| 8 | VIO lost next to glass? | glass_office (fan sees glass): 83.3 % reached, 16-18 % collisions; unmapped obstacles: 7 % collisions | synthetic |
| 9 | PX4 / ArduPilot? | EKF fused the bridge's pose on both SITLs; constant pose only | SITL |
| 10 | Your safety filter idea? | Fixed 0.2 m bound worst 1.0 %; ours 2.5 % on held-out jumps | synthetic |
| 11 | Path to product and certification? | No number | - |
| 12 | Commit-at-once also reached 100 %. Why not? | 8 of 20 wrong commits in the corridor, 7.3-9.4 s flown on them | synthetic |
| 13 | Is it really the innovation test doing the work? | 227-331 triggers per 100 runs; without it 80 / 71 % | synthetic |
| 14 | What if the room was never mapped? | Map from an outbound flight: 93.9 / 92.9 % reached, 2 % collisions | synthetic |
| 15 | How fast, and does it run onboard? | 0.4 s median recovery; 1.7-1.9 ms per scan (20-23 ms with yaw search) on a laptop | synthetic |

## Questions and answers

### 1. "Is this only simulation?"

"Yes, the relocalization results are simulation only. Over 100 random layouts per fault, hover +
match + one disambiguating move reached B in 99-100 % with 0 collisions and 0 wrong commits,
against 36-64 % with the estimator alone. The sim's VIO drift is calibrated against a real number,
OpenVINS at 1.5 % RPE over 10 m on the UZH-FPV dataset (ATE 0.36 m over 278.3 m). On held-out
seeds that holds only in open rooms; in offices, mazes and warehouses it reached 83-97 %, with
up to 33 wrong commits in warehouses. Not measured: SITL with the relocalizer, real flight."

- **Number:** 99-100 % reached vs 36-64 % on random layouts; held-out seeds 2-4: 100 % on random and u_trap, 83.3-97.2 % in five other families `[synthetic]`; RPE 1.5 % over 10 m, ATE 0.36 m `[real]`, 2 runs, a long FPV flight, not our course.
- **Source:** [relocalize disambiguating moves](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b),
  [held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56),
  [arena drift calibration](../../samples/close-area-arena/README.md#estimator-and-faults-ran-2026-11-09-synthetic),
  [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md#results).

### 2. "Why 2.5D?"

"Because the question is the estimator, not the altitude, and we needed thousands of exact, seeded
runs on a laptop. A full 3D ESDF rebuild of a 20 x 20 x 5 m room took 183 ms median against
1.5 ms in 2D, and pybullet has no macOS arm64 wheel. The price: no overhangs and no altitude
changes. The matcher searches yaw within +-15 deg: a 5 deg heading error alone dropped reach to
38 % without that search and 100 % with it; a 180 deg flip in a symmetric corridor still fails."

- **Number:** 182.95 ms (3D) vs 1.48 ms (2D) median EDT, Apple M3 Max `[synthetic]` timing; yaw search 38 % => 100 % reached at +-5 deg, 100 random layouts, seed 2 `[synthetic]`.
- **Source:** [arena results (EDT timing)](../../samples/close-area-arena/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181),
  [arena limits](../../samples/close-area-arena/README.md#limits),
  [yaw search](../../samples/close-area-relocalize/README.md#yaw-search-3-dof-relocalization-loop-60),
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits).

### 3. "Only seed 0?"

"No. The move design was chosen on seed 0, then flown once on seed 1 with nothing changed: the
Fox-style move arm reached 100 % under both dropout and jump, 0 collisions, 0 wrong commits. Be
honest about one thing: the matcher thresholds were calibrated on seed-1 static poses, so seed 1
is held out for the flights and the move, not for the thresholds. Seeds 2-4 across 7 room types
then passed only in open rooms: 100 % with 0 wrong commits on random and u_trap, and a FAIL in
the other five."

- **Number:** seed 1, 100 layouts per fault: 100 / 100 % reached, 0 wrong commits; seeds 2-4, 180 runs per family: random and u_trap 100.0 % [97.9, 100.0], office 94.4 %, glass_office 83.3 %, warehouse 97.2 % with 33 wrong commits `[synthetic]`.
- **Source:** [held-out check, seed 1](../../samples/close-area-relocalize/README.md#held-out-check-seed-1-run-by-the-loop-driver),
  [held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56),
  [disamb_random_1.md](../../samples/close-area-relocalize/results/disamb_random_1.md),
  [thresholds](../../samples/close-area-relocalize/README.md#what-is-in-it).

### 4. "What is new vs Tan 2025 / existing relocalization work?"

"Tan et al. IROS 2025 already sets safety-filter margins from fault-excluded estimates on a PX4
drone; that is one reason we dropped the filter as our headline. Choosing a move to separate
pose hypotheses is Fox, Burgard and Thrun 1998, and our own separation score did not beat a
Fox-style information-gain move: 70 % vs 80 % in the corridor. What is ours is the composition:
loss triggers, innovation test, ratio-persistence acceptance, the move, and never committing on a tie."

- **Number:** corridor reach 70 % (ours) vs 80 % (Fox-style), 20 runs `[synthetic]`.
- **Source:** [07 verdict (Tan 2025, Zhang/Li/Clark)](../../docs/research/close-area-nav/07-pl-margin-prior-art.md#1-verdict),
  [innovation-prior-art 01](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md#2-prior-art),
  [relocalize verdict](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b).

### 5. "Why not just add more sensors?"

"More beams help a lot: on the glass layouts the ideal 72-beam fan collided in 4-10 %, a
Crazyflie-like 4-beam deck in 90-100 %. But no ToF ranger sees glass, and the platform is the
organisers' choice. The relocalizer adds no sensor: it reuses the range scan the drone already
has for avoidance."

- **Number:** glass family, 50 layouts: 4 / 10 % collisions (72 beams) vs 90 / 100 % (4 beams) `[synthetic]`.
- **Source:** [arena sensor realism](../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic),
  [08 Crazyflie limits](../../docs/research/close-area-nav/08-crazyflie-sensing-limits.md#1-bottom-line).

### 6. "What happens on a Crazyflie with 4 beams?"

"It does not work well, and we measured it in simulation. The matcher needs 10 returns per scan,
so on 4 beams it accepted nothing until we added a yaw spin that stacks a quarter turn. With the
spin and the move it reached B in 48 % (dropout) and 64 % (jump) of runs, against 98-100 % on 72
beams, still with 0 wrong commits, after a median 9-12 s of spinning. Under dropout that is worse
than not relocalizing at all (64 %)."

- **Number:** 48 / 64 % reached, 3 / 7 % collisions, 0 wrong commits, 100 random layouts, seed 0, yaw is truth in the sim `[synthetic]`. Context: without a map 4 beams drop the unknown-map A* from 95 to 35 % reached in office layouts.
- **Source:** [4-beam spin](../../samples/close-area-relocalize/README.md#relocalization-with-a-4-beam-sensor-hover-and-yaw-spin-loop-54),
  [acceptance rule](../../samples/close-area-relocalize/README.md#what-is-in-it),
  [benchmark crazyflie preset](../../samples/close-area-benchmark/README.md#preset-crazyflie),
  [benchmark reading](../../samples/close-area-benchmark/README.md#reading).

### 7. "What if there are people walking?"

"Relocalization was only run on static, exactly mapped rooms; people were not in those runs.
For the planner, A* replanning alone hit walking people in 14 % of runs at 0.5 m/s and 36 % at
1.0 m/s; with a PX4-CBF-style range filter on top, 0 % at both, at the cost of 16 % stuck. So
the range filter stays in our stack under the relocalizer."

- **Number:** 14 / 36 % collisions => 0 %, 16 % stuck, 50 layouts, truth pose `[synthetic]`. Relocalization with people: no number.
- **Source:** [moving-obstacles results](../../samples/close-area-moving-obstacles/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181),
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits).

### 8. "What if VIO is lost next to glass?"

"Glass offices are one of our failing cases. With a sensor that does see the glass, relocalization
reached B in 83 % of runs and collided in 16-18 %, with no wrong commit; small pose errors are
enough to clip a doorway. A ranger that misses glass was not run with the relocalizer. The known
risk is the move after the hover: with obstacles missing from the map it collided in 7 % of runs,
and every hit on a missing obstacle came after a move, because the move check trusts the map."

- **Number:** glass_office, held-out seeds 2-4, 72-beam fan that sees glass: 83.3 % reached, 16-18 % collisions; unmapped added obstacles: 7 % collisions, 12 of 14 into the unmapped obstacles, all after a move, seed 2 `[synthetic]`. Relocalization with a glass-blind ranger: no number.
- **Source:** [held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56),
  [stale map](../../samples/close-area-relocalize/README.md#imperfect-prior-map-loop-55),
  [arena sensor realism](../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic).

### 9. "How does this get onto PX4 / ArduPilot?"

"The relocalizer runs on the companion and re-anchors the pose it sends as MAVLink ODOMETRY,
incrementing reset_counter so the EKF treats the step as a reset (doc 03 advice, not tested). The bridge for that message was checked in
SITL on PX4 v1.17.0 and ArduCopter 4.6.3: both EKFs fused it, with a constant pose on the ground.
Setpoints go out through PX4 Offboard or ArduPilot GUIDED drivers that are written from the SDK
docs and not yet run on a vehicle."

- **Number:** EKF fusion flags on (PX4 `cs_ev_pos: True`; ArduPilot "using external nav data"), constant pose only `[SITL]`. Drivers: no number (unrun).
- **Source:** [vio-to-mavlink-bridge SITL run](../../samples/vio-to-mavlink-bridge/README.md#run-against-sitl-ran-2026-11-06),
  [drivers platform table](../drone-adapter/drivers/README.md#platform-table),
  [flight-repo driver swap](../flight-repo/README.md#swap-the-mock-for-a-real-driver).

### 10. "What did your safety filter idea show?"

"It failed against a tuned fixed bound. A plain 0.2 m margin stayed at 1.0 % collisions or less in
every case on seeds 0-2; ours collided in 2.5 % of held-out jump runs and reached B 0.56 as often
as the range-only filter on jumps. Four of our seven jump collisions ended while hovering, so the
hover rule was the leak. That is why we pitch relocalization, and keep the range filter."

- **Number:** F4 0.2 m worst 1.0 % [0.3, 2.9]; ours 2.5 % [1.1, 5.7] held-out jump; reach ratio 0.56 `[synthetic]`.
- **Source:** [safety-filter Part e verdict](../../samples/close-area-safety-filter/README.md#verdict-against-doc-04-section-34-random-family-seeds-0-2-300-runs-per-cell-synthetic),
  [Part e answers](../../samples/close-area-safety-filter/README.md#answers).

### 11. "What is the path to product and certification?"

"We would not certify the relocalizer. It ships as a candidate pose next to the stock EKF, behind a
simple monitor, with the autopilot's own failsafe as the fallback: the ASTM F3269 runtime-assurance
pattern. The monitor and fallback carry the safety argument. We claim no assurance level and no compliance."

- **Number:** no number.
- **Source:** [path-to-product section 4](../../docs/path-to-product.md#4-runtime-assurance-ship-the-new-algorithm-next-to-a-trusted-baseline),
  [section 3](../../docs/path-to-product.md#3-certification-and-assurance-map-in-plain-language).

### 12. "Commit-at-once also reached 100 %. Why not use it?"

"In random rooms it got lucky: the innovation test corrected its wrong commits later. In a
symmetric corridor it committed to a pose 0.59-1.43 m wrong in 8 of 20 runs and flew 7.3-9.4 s on
it. Without the innovation test, that kind of wrong commit gave 40 % collisions at the corridor
exit. Ours reached 80 % there with 0 wrong commits."

- **Number:** 8 of 20 wrong commits; 40 % collisions without the test; ours 80 %, 0 wrong, one corridor geometry `[synthetic]`.
- **Source:** [corridor case](../../samples/close-area-relocalize/README.md#symmetric-case-a-2-m-x-148-m-corridor),
  [disamb_corridor.md](../../samples/close-area-relocalize/results/disamb_corridor.md).

### 13. "Is it really relocalization, or the innovation test doing the work?"

"Partly the innovation test, and we say so. It fires 227-331 times per 100 runs, so the system is
also a continuous map-based correction, not only loss recovery. With reported-loss triggers only,
commit-at-once drops to 80 / 71 % reached and hypothesis tracking to 67 / 76 %."

- **Number:** 227-331 triggers per 100 runs; 80 / 71 % and 67 / 76 % without the test (dropout / jump) `[synthetic]`.
- **Source:** [relocalize results](../../samples/close-area-relocalize/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181),
  [limits](../../samples/close-area-relocalize/README.md#limits).

### 14. "What if the room was never mapped?"

"Then we map it on the way out. In simulation the drone built its map flying A to B, lost VIO on
the way back, and relocalized against that self-built map: 93.9 % (dropout) and 92.9 % (jump)
reached, 2 % collisions, but 13 and 14 wrong commits. With no first pass at all there is
nothing to match; then the plan is hover, then land, and that fallback is not measured."

- **Number:** self-built map: 93.9 / 92.9 % reached, 2 % collisions, 13 / 14 wrong commits (map frame), 100 layouts, one seed (2) `[synthetic]`. No first pass: no number.
- **Source:** [stale map, e_selfmap rung](../../samples/close-area-relocalize/README.md#imperfect-prior-map-loop-55),
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits),
  [H1 judge questions](close-area-story.md#h1-relocalization-after-vio-loss-the-pivot-if-the-kill-test-fails).

### 15. "How fast is it, and does it run onboard?"

"Median 0.4 s from loss to a confirmed pose; when a move was needed, about 2-3 s. The corridor is
the slow case: about 11 s and several moves. Scan matching costs 1.7-1.9 ms per scan median on an Apple
laptop, about 20-23 ms with the yaw search; on 4 beams the spin alone takes a median 9-12 s. It
was not timed on a flight computer, and the hover in the sim is perfect."

- **Number:** 0.4 s median; 1.95-2.9 s after a move; corridor 11.0 s; 1.7-1.9 ms per scan (max 2.8 ms), 20-23 ms with yaw search (12-worker load); 4-beam spin 9-12 s median per loss event `[synthetic]`, laptop timing.
- **Source:** [disambiguating moves](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b),
  [yaw search](../../samples/close-area-relocalize/README.md#yaw-search-3-dof-relocalization-loop-60),
  [4-beam spin](../../samples/close-area-relocalize/README.md#relocalization-with-a-4-beam-sensor-hover-and-yaw-spin-loop-54),
  [held-out check](../../samples/close-area-relocalize/README.md#held-out-check-seed-1-run-by-the-loop-driver),
  [relocalize results](../../samples/close-area-relocalize/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181).

## Not verified

- No answer on this page was rehearsed or timed. The 20 s fit is a word-count estimate (about 50-70 words).
  Answers 1, 2, 3, 6, 8, 14 and 15 grew in loop-28 and may now run past 20 s.
- Numbers were copied from the sample READMEs and result files listed; no sample was rerun for this page.
- Question 8: relocalization with a ranger that misses glass was not run; the glass_office rows
  use the 72-beam fan, which sees glass.
- Questions 4, 7 and 9 were not re-checked against the later runs: 7 still says "exactly mapped
  rooms" and 9 still calls the reset_counter step "not tested", while doc 10 section 4 has since
  read the autopilot code (not run).
- Tan 2025 and Zhang/Li/Clark come from the hub's doc 07, which read them on arXiv; their code was not run.
- The IMAV 0.7 off-board factor comes from doc 06, which parsed the rulebook PDF with a crude parser.

### Verified since (loop-28, all synthetic)

- Question 6, "4 beams never reach the 10-return rule": measured. Without a yaw spin the matcher
  accepted 0 poses on the crazyflie preset
  ([4-beam](../../samples/close-area-relocalize/README.md#relocalization-with-a-4-beam-sensor-hover-and-yaw-spin-loop-54)).

### Refuted since (loop-28, all synthetic)

- The old answer 1 and 3 line "99-100 %, 0 wrong commits" as a general result: on held-out seeds
  2-4 it holds on random and u_trap only
  ([held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56)).
- The old answer 14 "no number": a self-built map gave 93.9 / 92.9 % reached
  ([stale map](../../samples/close-area-relocalize/README.md#imperfect-prior-map-loop-55)).
