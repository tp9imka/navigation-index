# Judge drill: close-area A=>B, relocalization pitch (H1)

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
| 1 | Is this only simulation? | 99-100 % reached, 0 collisions, all in simulation; drift calibrated to real OpenVINS RPE 1.5 % / 10 m | synthetic; real (UZH-FPV) |
| 2 | Why 2.5D? | 3D ESDF rebuild 183 ms median vs 1.5 ms in 2D | synthetic (laptop timing) |
| 3 | Only seed 0? | Held-out seed 1: 100 / 100 % reached, 0 wrong commits | synthetic |
| 4 | New vs Tan 2025 / existing relocalization? | Our separation score 70 % vs Fox-style 80 % in the corridor | synthetic |
| 5 | Why not just add more sensors? | 72 beams: 4-10 % collisions on glass; 4 beams: 90-100 % | synthetic |
| 6 | Crazyflie with 4 beams? | Matcher needs 10 returns per scan; 4 beams give at most 4. Not measured | no number for relocalization |
| 7 | People walking? | A* replan 14 / 36 % collisions; with range filter 0 %, 16 % stuck | synthetic |
| 8 | VIO lost next to glass? | Not measured for relocalization; 4-beam glass collisions 90-100 % | no number for relocalization |
| 9 | PX4 / ArduPilot? | EKF fused the bridge's pose on both SITLs; constant pose only | SITL |
| 10 | Your safety filter idea? | Fixed 0.2 m bound worst 1.0 %; ours 2.5 % on held-out jumps | synthetic |
| 11 | Path to product and certification? | No number | - |
| 12 | Commit-at-once also reached 100 %. Why not? | 8 of 20 wrong commits in the corridor, 7.3-9.4 s flown on them | synthetic |
| 13 | Is it really the innovation test doing the work? | 227-331 triggers per 100 runs; without it 80 / 71 % | synthetic |
| 14 | What if the room was never mapped? | No number | - |
| 15 | How fast, and does it run onboard? | 0.4 s median recovery; 1.7-1.9 ms per scan on a laptop | synthetic |

## Questions and answers

### 1. "Is this only simulation?"

"Yes, the relocalization results are simulation only. Over 100 random layouts per fault, hover +
match + one disambiguating move reached B in 99-100 % with 0 collisions and 0 wrong commits,
against 36-64 % with the estimator alone. The sim's VIO drift is calibrated against a real number,
OpenVINS at 1.5 % RPE over 10 m on the UZH-FPV dataset (ATE 0.36 m over 278.3 m). Not measured: SITL with the relocalizer, real flight, a map with errors."

- **Number:** 99-100 % reached vs 36-64 % `[synthetic]`; RPE 1.5 % over 10 m, ATE 0.36 m `[real]`, 2 runs, a long FPV flight, not our course.
- **Source:** [relocalize disambiguating moves](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b),
  [arena drift calibration](../../samples/close-area-arena/README.md#estimator-and-faults-ran-2026-11-09-synthetic),
  [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md#results).

### 2. "Why 2.5D?"

"Because the question is the estimator, not the altitude, and we needed thousands of exact, seeded
runs on a laptop. A full 3D ESDF rebuild of a 20 x 20 x 5 m room took 183 ms median against
1.5 ms in 2D, and pybullet has no macOS arm64 wheel. The price: no overhangs, no altitude
changes, and the scan matcher searches x and y only, with yaw from the estimator."

- **Number:** 182.95 ms (3D) vs 1.48 ms (2D) median EDT, Apple M3 Max `[synthetic]` timing.
- **Source:** [arena results (EDT timing)](../../samples/close-area-arena/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181),
  [arena limits](../../samples/close-area-arena/README.md#limits),
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits).

### 3. "Only seed 0?"

"No. The move design was chosen on seed 0, then flown once on seed 1 with nothing changed: the
Fox-style move arm reached 100 % under both dropout and jump, 0 collisions, 0 wrong commits. Be
honest about one thing: the matcher thresholds were calibrated on seed-1 static poses, so seed 1
is held out for the flights and the move, not for the thresholds."

- **Number:** seed 1, 100 layouts per fault: 100 / 100 % reached, 0 wrong commits `[synthetic]`.
- **Source:** [held-out check, seed 1](../../samples/close-area-relocalize/README.md#held-out-check-seed-1-run-by-the-loop-driver),
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

"Our relocalization was not run with 4 beams. As written, the acceptance rule needs at least 10
returns per scan, and a Multi-ranger gives at most 4, so it would keep hovering and never accept.
On a Crazyflie we would need scan accumulation over a short yaw sweep, or a different map cue.
For context, without a map 4 beams drop the unknown-map A* from 95 to 35 % reached in office layouts."

- **Number:** no number for relocalization on 4 beams. Context: office 95 => 35 % reached, 20 layouts `[synthetic]`.
- **Source:** [acceptance rule](../../samples/close-area-relocalize/README.md#what-is-in-it),
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

"Not measured. The relocalization runs had no glass, and the ideal fan in them would see it
anyway. A ranger that misses glass returns a scan that disagrees with a map that has the glass
in it, so the match score drops and the rule keeps hovering rather than guessing. The real risk is
the move after the hover: its collision check uses the map, so mapped glass is avoided, unmapped
glass is not."

- **Number:** no number for relocalization near glass. Context: 4-beam glass collisions 90-100 % `[synthetic]`.
- **Source:** [arena sensor realism](../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic),
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits).

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

"Then there is nothing to match against, and this method does not apply. We need a floor plan or a
first pass of the room. Without one, our plan is hover, then land, and that fallback is not measured."

- **Number:** no number.
- **Source:** [relocalize limits](../../samples/close-area-relocalize/README.md#limits),
  [H1 judge questions](close-area-story.md#h1-relocalization-after-vio-loss-the-pivot-if-the-kill-test-fails).

### 15. "How fast is it, and does it run onboard?"

"Median 0.4 s from loss to a confirmed pose; when a move was needed, about 2-3 s. The corridor is
the slow case: about 11 s and several moves. Scan matching costs 1.7-1.9 ms per scan median on an Apple
laptop; it was not timed on a flight computer, and the hover in the sim is perfect."

- **Number:** 0.4 s median; 1.95-2.9 s after a move; corridor 11.0 s; 1.7-1.9 ms per scan (max 2.8 ms) `[synthetic]`, laptop timing.
- **Source:** [disambiguating moves](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b),
  [held-out check](../../samples/close-area-relocalize/README.md#held-out-check-seed-1-run-by-the-loop-driver),
  [relocalize results](../../samples/close-area-relocalize/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181).

## Not verified

- No answer on this page was rehearsed or timed. The 20 s fit is a word-count estimate (about 50-70 words).
- Numbers were copied from the sample READMEs and result files listed; no sample was rerun for this page.
- Question 6 (4 beams never reach the 10-return rule) and question 8 (glass lowers the match score)
  are read from the code description in the relocalize README, not from a run.
- Tan 2025 and Zhang/Li/Clark come from the hub's doc 07, which read them on arXiv; their code was not run.
- The IMAV 0.7 off-board factor comes from doc 06, which parsed the rulebook PDF with a crude parser.
