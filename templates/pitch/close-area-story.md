# Close-area pitch scaffold: A to B through obstacles

Fill this on Day 2 when the task is "fly a drone from A to B in a close area, with obstacles".
It replaces the PNT story families in [story-bank.md](story-bank.md) for that task. The
research behind it is [docs/research/close-area-nav/README.md](../../docs/research/close-area-nav/README.md).
The live-demo script for it is [demo-script-close-area.md](../demo-script-close-area.md).

State on 2026-11-09: the close-area baselines ran in
[close-area-arena](../../samples/close-area-arena/README.md), all `[synthetic]` (simulated
layouts, vehicle and sensor; no SITL, no flight). Over 50 seed-0 random layouts, A* + ESDF reached
B in 100 % with a known map and with an unknown map
([results](../../samples/close-area-arena/results/astar_esdf_random_0.md)). The range-only
`freest_beam` planner fell from 86 % reach on truth to 42 % with a VIO jump and 40 % with bias,
with 0 % collisions in every case, because the arena's ranges come from the true pose
([results](../../samples/close-area-arena/results/faults_freest_beam_summary_0.md)). These are
hub context numbers, not your team's result.

The kill test ran parts a, b and d on seed 0
([close-area-safety-filter](../../samples/close-area-safety-filter/README.md), synthetic). Part d
result: ours (F5) has 0 % collisions in all six fault cases, but **FAILS the reach bar**: 61-89 %
of PX4-CBF's reach, against the 90 % the gate asks for
([part d verdict](../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).
**Update, evening: H1 is narrowed too.** Relocalization holds on open layouts with a dense range sensor and an exact map, but not on 4 beams (48-64 %), in warehouses (33 wrong commits) or with unmapped obstacles, and the mechanism is published (Jensfelt 2001, AF-MCL 2026). Read the decision at the end of [docs/research/README.md](../../docs/research/README.md) before pitching any novelty.

**Decision (held-out rerun, Part e): the safety-filter headline FAILS.** A hand-tuned fixed bound
(MR-CBF 0.2 m) stays at <= 1 % collisions on seeds 0-2; ours collides in 2.5 % [1.1, 5.7] of
held-out jump runs and reaches B less often. Pitch H1, the relocalization story in section 3. The relocalization pivot (section 3, H1) is filled with measured
numbers and ready to use. Placeholders `<NUMBER from ...>` that remain are the team's own Day-1/2
runs. A slot you cannot fill is said aloud as "not measured".

Contents: [Facts that hold either way](#0-facts-that-hold-either-way) - [Story](#1-the-story) -
[Kill test gate](#2-kill-test-gate-decide-the-story-at-h24) -
[Alternative hooks](#3-alternative-hooks-if-the-kill-test-fails) (H1 is the pivot) -
[3-minute skeleton](#4-3-minute-skeleton) - [Judge questions](#5-judge-questions) -
[Numbers to fill](#6-numbers-to-fill-and-where-they-come-from) - [Not verified](#7-not-verified)

## Fill order on Day 2

1. **H+24.** Read the kill-test result (section 2). Keep the main story or pick one alternative
   hook (section 3). Cross out the others. If the held-out rerun confirms the reach FAIL, the
   default pick is H1.
2. **H+26.** Write the five beats for the chosen story on the wall, one line each.
3. **H+30.** Fill the 3-minute skeleton (section 4, or H1's own skeleton) with what actually runs.
   Record the backup video ([demo-script-close-area.md](../demo-script-close-area.md#recording-the-backup)).
4. **H+36.** Rehearse with [judge-drill-close-area.md](judge-drill-close-area.md) (15 questions with numbers): one person asks, the answerer has 20 s.
   Any answer that still says "pending" is either filled or reworded to "not measured".
5. **H+40.** Score with [judging-self-assessment.md](../judging-self-assessment.md) and copy every
   number into the [one-pager](one-pager-template.md) and `runs/results.md`.

## 0. Facts that hold either way

These are measured, hub-run, and true whatever the kill-test verdict. All `[synthetic]`: simulated
layouts, vehicle and sensors, no SITL, no flight. Use them in beat 2 ("why it matters") of any
story, or as answers to judge questions. They are hub numbers, not your team's result.

| Fact | Number | Input | Source |
|---|---|---|---|
| A range filter stops walking people that A* replanning alone hits | A* replan at 2.5 Hz collides in 14 % (people at 0.5 m/s) and 36 % (1.0 m/s); A* + PX4-CBF-style filter (F2): 0 % at both speeds, at the cost of 16 % stuck. 50 layouts, truth pose. Only A* was run under the filter | `[synthetic]` | [moving-obstacles results](../../samples/close-area-moving-obstacles/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181), [moving_0.md](../../samples/close-area-moving-obstacles/results/moving_0.md) |
| Against what the ranger sees, a range-only filter is enough | With every obstacle visible, F1 (CP-stop) and F2 (PX4-CBF) have 0 % collisions in every case, VIO jump, bias and dropout included (500 runs per arm); bare A*: 7 / 4 / 1 % (jump / bias / dropout) | `[synthetic]` | [safety-filter part a](../../samples/close-area-safety-filter/README.md#reading), [kill_a_unsensed_off_0.md](../../samples/close-area-safety-filter/results/kill_a_unsensed_off_0.md) |
| Against what it cannot see, it is not | With 2 sensor-invisible obstacles per layout, F2 collides in 3-11 %, every hit on an invisible obstacle | `[synthetic]` | [kill_a_unsensed_on_0.md](../../samples/close-area-safety-filter/results/kill_a_unsensed_on_0.md) |
| 4-beam rangers miss glass | Crazyflie 4 x 27 deg preset on the glass family: collisions 90 % (freest_beam) and 100 % (A* unknown map); bright-light preset 96 % and 100 %. The ideal 72-beam fan: 4 % and 10 %. 50 layouts; glass sits on the A-B line by design | `[synthetic]` | [arena sensor realism](../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic) |
| Relocalization against the map turns VIO loss into a recoverable event | Estimator only: 64 % / 36 % reached (dropout / jump), 1 % / 9 % collisions. Hover + match + disambiguating move: 99-100 % reached, 0 % collisions, 0 wrong commits, held-out seed 1 included. Known map only Scope: open layouts, 72-beam sensor, exact map; held-out seeds 2-4 give 83-97 % in rooms, 48-64 % on 4 beams (see Narrowed since). | `[synthetic]` | H1 below, [close-area-relocalize](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b) |

## 1. The story

Use it only if the kill test passes (section 2). Part d on seed 0 did not pass the reach bar.

**One line:** "Any planner gets the drone from A to B; our filter keeps it safe when the drone
is wrong about where it is."

| Beat | Line to say | Filled from |
|---|---|---|
| 1. Problem | "In a close area the gap is about a metre. The drone does not crash because the planner is bad. It crashes because it is wrong about where it is." | Gap size is an estimate in [doc 03 section 1](../../docs/research/close-area-nav/03-close-area-localization.md#1-bottom-line) (doorway ~0.8 m), analysis, not a measurement |
| 2. Why it matters | "Past drone competitions broke on state estimation, not on planning. And the filters that report the uncertainty are overconfident." | [doc 02 section 3.1](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores) item 5; [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#is-the-reported-covariance-realistic-evidence) |
| 3. What we built | "A filter between any planner and the autopilot. It never hits what the range sensor sees. For what it cannot see, the margin comes from a fault-detecting nav monitor, not the filter's own covariance. When nav health drops it slows down and holds a hover." | [doc 04 section 3.2](../../docs/research/close-area-nav/04-innovation-prior-art.md#32-what-may-remain-narrow) |
| 4. Honest numbers | Seed 0 version: "Over 100 layouts, each with 2 obstacles the range sensor cannot see, under injected VIO jumps and bias: collisions 0 % for ours vs 9 % (jump) and 3 % (bias) for a covariance margin, `[synthetic]`. The price: ours reached B in 20 % of jump runs against 33 % for PX4-CBF, because it hovers when the monitor cannot tell which source is lying. A fixed 0.2 m margin tuned on the same seed matched our safety. Not measured: real flight." Held-out seeds 1-2 (Part e): ours collided in 2.5 % [1.1, 5.7] of jump runs, the tuned 0.2 m margin stayed at <= 1 %, so this branch is not pitched; use section 3 (H1) | [part d](../../samples/close-area-safety-filter/README.md#part-d-ours-f5-against-the-baselines-ran-2026-11-09-synthetic-seed-0-only), [kill_d_summary_0.md](../../samples/close-area-safety-filter/results/kill_d_summary_0.md) |
| 5. What's next | "Same filter on PX4 Offboard in SITL, then on the organisers' drone. It ships as a runtime-assurance monitor next to the stock autopilot." | [path-to-product.md section 4](../../docs/path-to-product.md#4-runtime-assurance-ship-the-new-algorithm-next-to-a-trusted-baseline) |

**The narrow claim (say it exactly, do not widen it):** for obstacles the range sensor cannot
see (out of field of view, thin, glass, geofence) and under VIO jumps or bias, a fault-aware
margin beats a covariance margin. Source:
[close-area README](../../docs/research/close-area-nav/README.md#recommended-direction). On seed 0
it beat the covariance margin (F3) on collisions, but not a fixed 0.2 m bound (F4), and it lost reach.

**What is not ours, say it first:** range-only filtering inside PX4 is PX4-CBF
([catalog](../../catalog/repos/ntnu-arl__px4-cbf.md), ICUAS 2025, preprint abstract only + code,
BSD-3). A margin from the EKF covariance is Belief-CBF
([catalog](../../catalog/resources/vahs-belief-cbf-2023.md), preprint, abstract only). Our part is
joining them with the hub's integrity monitor
([multi-source-fde](../../samples/multi-source-fde/README.md)). Engineering, not theory.

## 2. Kill test gate (decide the story at H+24)

From [doc 04 section 3.4](../../docs/research/close-area-nav/04-innovation-prior-art.md#34-falsification-experiment)
(thresholds are the research lane's proposal).

**Part d result, seed 0** ([verdict](../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic),
`[synthetic]`, 100 layouts per case, 2 unsensed obstacles per layout):

| Criterion | Ours (F5) | Verdict |
|---|---|---|
| Collisions 1 % or less | 0 % in none, jump, bias, dropout, UWB NLOS and VIO+UWB (600 runs) | met |
| At least 3x lower than Belief-CBF (F3) on jump and bias | 0 vs 9 % (jump), 0 vs 3 % (bias); bias rests on 3 collisions | met, weak on bias |
| Goal reach at least 90 % of PX4-CBF (F2) | 89 % (none), 61 % (jump, 20 vs 33 % reached), 85 % (bias), 86 % (dropout) | **FAIL** |
| Better than MR-CBF with a fixed 0.2 m bound (F4) | Same safety (F4: 0 / 0 / 0 / 1 %); F4 reaches more on jump (29 vs 20 %) | not better on seed 0 |

The jump loss is the hover rule: 33 of the 80 stuck jump runs ended while hovering on an
ambiguous monitor. The in-loop protection level breached its 1e-3 risk in the VIO+UWB case
(1.84e-3 of epochs), with no collision following.

| Held-out rerun says | Story |
|---|---|
| All three criteria met | Keep section 1. Still say a fixed 0.2 m bound matched safety on seed 0 |
| Reach still under 90 % of F2 (as on seed 0) | **Kill test FAIL. Pivot to H1 (relocalization).** Use [facts that hold either way](#0-facts-that-hold-either-way) for beat 2; mention the filter as "measured, safe, too cautious" in one sentence |
| Belief-CBF arm within 1 percentage point of ours on jump and bias | Drop the headline. Pick H1, H2 or H3 below |
| Range-only arm (PX4-CBF style) already at 1 % or less everywhere | Drop the headline. Honest pitch: "we integrated PX4-CBF and measured it". Use H3 |
| Rerun not finished by H+24 | Decide on seed 0: that is a FAIL. Pivot to H1 |

Write the result in `runs/results.md` with arms, layouts, fault cases and seeds before choosing.

## 3. Alternative hooks if the kill test fails

Each hook keeps the five-beat shape. Swap beats 1, 3 and 4 of section 1; beats 2 and 5 mostly stay.

### H1. Relocalization after VIO loss (the pivot if the kill test FAILs)

**Headline:** "The drone recovers from VIO loss without guessing."

**Pick it when:** a prior map or a first pass of the room exists (the hypotheses need something to
match against), and Day 1 logs show tracking loss. In a never-seen room there is nothing to
relocalize against. Say so before a judge does.

**What it does** ([close-area-relocalize](../../samples/close-area-relocalize/README.md)): on a VIO
reset, a quality drop to 0, or a scan that no longer fits the map at the estimate (innovation
test), the drone hovers. It matches the range scan against the known map and keeps up to 5 pose
hypotheses. It accepts one only when it is at least 1.02x better than the second for 3 scans in a
row. If none wins within 1 s, it flies one short collision-checked move (1 or 2 m) chosen to
separate the hypotheses, then checks again. On a tie it keeps hovering. It never commits.

**The numbers** (all `[synthetic]`: simulated layouts, vehicle, VIO-like estimator and 72-beam
range fan, A* known-map planner; 100 random layouts per fault; no SITL, no flight):

| Arm | Dropout reached % (collision %) | Jump reached % (collision %) | Wrong commits (> 0.5 m) | Source |
|---|---|---|---|---|
| Estimator only, no relocalization | 64 (1) | 36 (9) | - | [reloc_random_0.md](../../samples/close-area-relocalize/results/reloc_random_0.md), seed 0 |
| Hover while lost, no matching | 59 (4) | 38 (6) | - | same |
| Commit to the best match at once + innovation test | 100 (0) | 100 (0) | 2 / 4 | same |
| Hover until one hypothesis wins (no move) | 80 (0) | 93 (0) | 0 / 0 | same |
| **Hover + disambiguating move, seed 0** | 99 (0) | 99 (0) | 0 / 0 | [disamb_random_0.md](../../samples/close-area-relocalize/results/disamb_random_0.md), info-gain move |
| **Hover + disambiguating move, held-out seed 1** | 100 (0) | 100 (0) | 0 / 0 | [disamb_random_1.md](../../samples/close-area-relocalize/results/disamb_random_1.md), nothing tuned on seed 1 |

- **Recovery time:** median 0.4 s from trigger to accepted pose; when a move was needed, median
  2.4 / 1.95 s (seed 0, dropout / jump) and 2.9 / 2.55 s (seed 1)
  ([disambiguating moves](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b),
  [held-out check](../../samples/close-area-relocalize/README.md#held-out-check-seed-1-run-by-the-loop-driver)).
- **Why "without guessing" matters, the corridor:** in a symmetric 2 m x 14.8 m corridor, the
  commit-at-once arm reached 100 % of 20 runs but committed to a pose 0.59-1.43 m wrong in 8 of 20,
  and flew on it for 7.3-9.4 s before the innovation test caught it. The move arm made 0 wrong
  commits and reached 80 %; hover until one wins, without a move, reached 0 %
  ([corridor](../../samples/close-area-relocalize/README.md#symmetric-case-a-2-m-x-148-m-corridor),
  [disamb_corridor.md](../../samples/close-area-relocalize/results/disamb_corridor.md)).
- **Cost:** scan matching median 1.7-1.9 ms per scan, max 2.8 ms, on an Apple M3 Max laptop,
  not on a flight computer
  ([results](../../samples/close-area-relocalize/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181)).

**Five beats:**

| Beat | Line to say | Filled from |
|---|---|---|
| 1. Problem | "Indoors, VIO will lose track: a dark corner, a blank wall, a fast turn. With the estimator alone our drone reached B in 36 % of runs after a VIO jump and hit something in 9 %." | Estimator-only row above, `[synthetic]` |
| 2. Why it matters | "Past drone competitions broke on state estimation, not planning. And the obvious fix, snap to the best map match, guesses: in a corridor it picked the wrong spot in 8 of 20 runs." | [doc 02 section 3.1](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores) item 5; corridor bullet above |
| 3. What we built | "When tracking drops, the drone hovers and keeps up to five pose hypotheses from the map. It flies on only when one wins clearly. If none wins, it makes one short move that tells them apart. It never commits on a tie." | [relocalize README](../../samples/close-area-relocalize/README.md#what-is-in-it) |
| 4. Honest numbers | "Over 100 random layouts per fault: 99-100 % reached, 0 collisions, 0 wrong commits, on a held-out seed too, `[synthetic]`. Median 0.4 s to a confirmed pose, about 2-3 s when a move is needed. In a symmetric corridor: 80 %, still 0 wrong commits. Not measured: SITL, real flight, a map with errors." Scope: open layouts, 72-beam sensor, exact map; held-out seeds 2-4 give 83-97 % in rooms, 48-64 % on 4 beams (see Narrowed since). | Table above |
| 5. What's next | "Same matcher on the drone's lidar or depth scan, map from a first pass of the room, triggers from the autopilot's ODOMETRY quality and reset counter. Then SITL, then the organisers' drone." | Triggers: [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#4-estimator-health-signals-a-planner-can-consume) |

**What is not ours, say it first:** choosing a move to separate pose hypotheses is active Markov
localization (Fox, Burgard, Thrun 1998, via
[innovation-prior-art 01](../../docs/research/innovation-prior-art/01-disambiguating-maneuvers.md)).
Our own separation score did not beat that Fox-style information-gain move (corridor 70 % vs 80 %).
The arm in the numbers is the Fox-style one. Our part is the composition: loss triggers + innovation
test + ratio-persistence acceptance + the move + "hover, never commit on a tie". Engineering, not theory.

**3-minute skeleton for H1** (the demo rows are in
[demo-script-close-area.md](../demo-script-close-area.md#variant-rows-for-the-alternative-hooks)):

| Time | Beat | Say | Show |
|---|---|---|---|
| 0:00-0:20 | Problem | Beat 1. The platform and sensors the organisers gave us | Title slide: top-down room, A and B, a dark zone marked |
| 0:20-0:40 | Why it matters | Beat 2. One number with its label: the 8 of 20 wrong commits in the corridor | One slide, one number, `[synthetic]` in the corner |
| 0:40-1:00 | What we built | VIO + EKF => loss trigger => hover => scan matcher (5 hypotheses) => accept or move => re-anchor => planner. Say which boxes are real and which are stubs | Architecture slide |
| 1:00-2:00 | Live demo | Seed 1, jump fault, layout 97: commit-at-once grabs a pose 0.63 m wrong; hover until one wins stalls; ours makes one 1 m move and accepts 0.07 m from truth 1.7 s after the trigger, then reaches B | Demo script H1 rows |
| 2:00-2:35 | Honest numbers | The six-row table above, reduced to: estimator only 64 / 36 %, commit-at-once 100 % with 2-4 wrong commits, ours 99-100 % with 0, corridor 80 %. Say "not measured: SITL, flight, map errors" | Results table |
| 2:35-3:00 | What's next | Beat 5, and the scope line ("the vehicle's own navigation only") | Path-to-product slide |

**Judge questions specific to H1** (20 s each):

- *"Commit-at-once also reached 100 %. Why not use it?"* "Here the innovation test rescued it
  later. In the corridor it flew 7.3-9.4 s on a pose up to 1.43 m wrong. Without that test the same
  kind of wrong commit gave 40 % collisions at the corridor exit. Ours reached less there, 80 %, but
  never flew on a wrong pose." Source: [corridor](../../samples/close-area-relocalize/README.md#symmetric-case-a-2-m-x-148-m-corridor).
- *"What if the room was never mapped?"* "Then there is nothing to match. We need a first pass or
  a floor plan." Without one, the hub has no measured fallback; say "hover, then land" only as a plan.
- *"What if the truth is in none of the hypotheses?"* "After 10 scans with no good match the
  search window doubles to +-4 m. If still nothing, it keeps hovering. The move's collision check
  trusts the hypotheses, so this case is a known weak spot." Source:
  [relocalize limits](../../samples/close-area-relocalize/README.md#limits).

**Limits to say if asked** ([relocalize limits](../../samples/close-area-relocalize/README.md#limits)):
2D xy search with yaw from the estimator (truth yaw in the sim); the map is the exact prior grid
(no map error, no people); the sim hover is perfect; the innovation test fires often (227-331
triggers per 100 runs), so part of the gain is continuous map-based correction, not only loss
recovery. Only one corridor geometry and one jump size (0.5 m).

### H2. Fiducial goal

- **Hook:** "We do not need to know exactly where B is. We need to see it. An AprilTag at B turns a
  drifting estimate into a fixed landing."
- **Pick it when:** the organisers allow a marker at B, or B is given as a marker or object
  ([doc 03 section 3](../../docs/research/close-area-nav/03-close-area-localization.md#3-how-b-is-specified-and-what-it-implies)).
- **Measure:** final distance to B centre `<NUMBER from runs/results.md>` with and without the tag
  over `<NUMBER from runs/results.md>` runs; tag acquisition range `<NUMBER from runs/results.md>`.
- **Hub ground:** AprilTag ([catalog](../../catalog/repos/aprilrobotics__apriltag.md), BSD-2) and
  `apriltag_ros` ([catalog](../../catalog/repos/christianrauch__apriltag_ros.md), MIT). PX4 precision
  landing defaults `PLD_HACC_RAD` 0.2 m, `PLD_BTOUT` 5 s, docs, and the page says it needs a valid
  global position, so check indoors (doc 03 section 3). Judges give cheap points for a visible
  arrival at B: IMAV 2026 pays +1 for a static ArUco landing
  ([doc 02 section 3](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#3-competition-formats-and-lessons), rulebook text extracted with a crude parser).
- **Say also:** the tag fixes the last metres only. The flight to the tag still rides on VIO or flow.

### H3. Plain robust baseline

- **Hook:** "Slow, sure, and it tells you when it is not sure. Our drone finished `<NUMBER from runs/results.md>`
  of `<NUMBER from runs/results.md>` random layouts without a touch on the sticks."
- **Pick it when:** the kill test failed or was not run, H1 has no map to match against, and the
  baseline planner flies reliably.
- **Measure:** completion rate, collisions, stuck count, time to goal over random layouts; any
  intervention by a person. Report "stuck" apart from "reached" and "crashed"
  ([doc 04 section 1.5](../../docs/research/close-area-nav/04-innovation-prior-art.md#15-failure-modes)).
- **Hub ground:** judges score completion before speed, onboard autonomy as a multiplier and
  replanning on moved obstacles ([doc 02 section 3.1](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores)).
  Baseline recipe: [doc 01 section 5](../../docs/research/close-area-nav/01-planning-and-mapping.md#5-fastest-credible-baseline).
  The moving-people fact in [section 0](#0-facts-that-hold-either-way) is the reason to keep a range filter in it.
- **Say also:** "no new algorithm; the contribution is a measured, honest baseline and the health
  log". If PX4-CBF is inside, name it.

## 4. 3-minute skeleton

For the section 1 story. H1 has its own skeleton in section 3. Same beats as
[pitch-structure.md](pitch-structure.md#3-minute-skeleton). Screen content per
20 s is in [demo-script-close-area.md](../demo-script-close-area.md#script).

| Time | Beat | Say | Show |
|---|---|---|---|
| 0:00-0:20 | Problem | The one-line story (or the chosen hook). The platform and sensors the organisers gave us | Title slide: top-down view of the course, A and B marked |
| 0:20-0:40 | Why it matters | "Estimation broke past competitions, and reported covariance is overconfident." One hub number with its label (section 6, rows C1-C2) | One slide, one number, label in the corner |
| 0:40-1:00 | What we built | planner => safety filter => autopilot; nav monitor => margin and speed cap. Say which boxes are real and which are stubs. Say where each box runs | Architecture slide |
| 1:00-2:00 | Live demo | Same seed, two arms side by side; VIO fault injected; covariance-margin arm breaches the unseen obstacle, ours widens, slows, holds, reaches B; then our failure case | Sim view full screen |
| 2:00-2:35 | Honest numbers | Ours vs PX4-CBF-style vs Belief-CBF-style, layouts x fault cases, `[synthetic]` or `[SITL]`, stuck rate, one "not measured". On seed 0: collisions 0 % vs 11 % (F2) and 9 % (F3) on jumps; reach 20 % vs 33 % (F2) | Results table |
| 2:35-3:00 | What's next | Runtime-assurance path, next three steps, scope line ("the vehicle's own navigation only") | Path-to-product slide ([path-to-product.md section 6](../../docs/path-to-product.md#6-the-path-to-product-slide)) |

Cut order if over time: "What we built" shrinks to one sentence first. "Honest numbers" never
goes below "ours vs baseline, N layouts, label".

## 5. Judge questions

Rehearse with a timer: 20 s per answer. "Where the answer lives" is the file to open if a judge
asks for evidence. "pending: X" means the hub has no answer yet; fill X on Day 1-2 or say
"not measured". Seed-0 kill-test numbers below are from
[kill_d_summary_0.md](../../samples/close-area-safety-filter/results/kill_d_summary_0.md), `[synthetic]`.

### 1. "Why not just use the lidar / rangefinder?"

- **Answer pattern:** "For what the sensor sees, we do, and we need no position for it. Our margin
  only matters for what it cannot see: outside the field of view, thin poles, glass, the geofence,
  and when the sensor itself degrades. Here is the run where the range-only arm hits one of those."
- **Where the answer lives:** [doc 04 section 0](../../docs/research/close-area-nav/04-innovation-prior-art.md#0-one-finding-that-shapes-all-three-ideas);
  range-only arm result: PX4-CBF (F2) collides in 3-11 % with 2 unsensed obstacles per layout,
  every hit on an unsensed one; 0 % when every obstacle is visible; a 4-beam Crazyflie preset hits
  glass in 90-100 % (section 0, `[synthetic]`).

### 2. "What is new vs PX4 Collision Prevention?"

- **Answer pattern:** "Collision Prevention works only in Position mode and only stops; it does not
  plan or slow down on bad navigation. PX4-CBF already filters from ranges inside PX4. We add the
  map and geofence barrier with a margin from a fault-detecting monitor, plus a speed cap and hover
  on nav health."
- **Where the answer lives:** [PX4 Collision Prevention docs](../../catalog/resources/px4-collision-prevention-docs.md)
  (docs: Position mode only, zeroes velocity after 0.5 s without range data, Hold after 5 s, per
  [doc 02 section 2](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#2-platform-cheat-table));
  [PX4-CBF](../../catalog/resources/misyats-px4-cbf-icuas2025.md) (preprint, abstract only);
  [doc 04 section 3.2](../../docs/research/close-area-nav/04-innovation-prior-art.md#32-what-may-remain-narrow).

### 3. "Why not just inflate by the covariance, like Belief-CBF?"

- **Answer pattern:** "Because the covariance does not see a VIO jump or a slow bias. On those
  faults the covariance arm collided in 9 % (jump) and 3 % (bias), ours 0 % and 0 %, `[synthetic]`,
  seed 0." Then say the other half: "A fixed 0.2 m bound did as well as ours on safety, and ours
  lost reach." If the kill test failed, say that and switch to the hook you picked.
- **Where the answer lives:** kill test in [doc 04 section 3.4](../../docs/research/close-area-nav/04-innovation-prior-art.md#34-falsification-experiment);
  [part d verdict](../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic);
  overconfidence evidence in [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#is-the-reported-covariance-realistic-evidence).

### 4. "What if VIO is lost?"

- **Answer pattern:** name the trigger (ODOMETRY `quality`, `reset_counter`, tracking state,
  innovation rejects), the action (speed cap => hover, flow + rangefinder keep the hover), and how
  long the hover holds before land. With a map: "we relocalize. Hover + scan match + one
  disambiguating move reached 99-100 % with 0 wrong commits, against 36-64 % with the estimator
  alone, `[synthetic]`." Then show the run.
- **Where the answer lives:** H1 in section 3;
  [close-area-relocalize](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b);
  [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#4-estimator-health-signals-a-planner-can-consume)
  and [section 5a](../../docs/research/close-area-nav/03-close-area-localization.md#a-indoor-no-gnss);
  VIO-to-autopilot plumbing in [vio-to-mavlink-bridge](../../samples/vio-to-mavlink-bridge/README.md)
  (EKF fusion checked in SITL with a constant pose, not in flight). Hover drift after loss on a
  real drone: pending: `<NUMBER from runs/results.md>` (the sim hover is perfect).

### 5. "Where does the planner run?"

- **Answer pattern:** say the box: laptop, companion or flight controller. If it is the laptop, say
  so, and say what moves onboard first. The flight controller never runs the planner; it runs the
  EKF and failsafes.
- **Where the answer lives:** [path-to-product.md section 1](../../docs/path-to-product.md#1-onboard-compute-what-fits-where)
  (vendor and benchmark numbers, not ours). IMAV 2026 scores off-board compute at 0.7 of onboard
  ([doc 02 section 3.1](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores),
  rulebook, docs). Our loop time: pending: `<NUMBER from runs/results.md>` ms p99 on `<board>`.

### 6. "Is that sim or real?"

- **Answer pattern:** label first. "`[synthetic]`: point-mass sim with a VIO fault model" or
  "`[SITL]`: real PX4 firmware, simulated sensors". Then the gap: real VIO noise, wind, latency.
- **Where the answer lives:** label rules in [pitch README](README.md#rules-for-numbers-non-negotiable).
  The hub's one real VIO number: OpenVINS stereo on UZH-FPV indoor_forward_3, ATE 0.36 m, max
  1.57 m over 278.3 m, `[real]`, 2 runs ([relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md#results)).
  It is a long FPV flight, not our course.

### 7. "Does the filter just freeze the drone?"

- **Answer pattern:** give goal reach and stuck count next to the breach rate. On seed 0: "Goal
  reach 61-89 % of the range-only arm's, below our own 90 % bar. Stuck in 36 / 80 / 72 / 49 of 100
  layouts (none / jump / bias / dropout); 33 of the 80 jump runs ended hovering on an ambiguous
  monitor. The filter changed the command on 36-49 % of steps, against 23-24 % for PX4-CBF. So yes,
  it is too cautious, `[synthetic]`."
- **Where the answer lives:** pass rule (goal reach at least 90 % of PX4-CBF arm) and the
  freezing-robot failure mode in [doc 04 sections 1.5 and 3.4](../../docs/research/close-area-nav/04-innovation-prior-art.md#34-falsification-experiment);
  [kill_d_summary_0.md](../../samples/close-area-safety-filter/results/kill_d_summary_0.md).

### 8. "What if we move an obstacle? Is the path hard-coded?"

- **Answer pattern:** "Random layouts in every test, replanning at `<NUMBER from runs/results.md>` Hz.
  Move one now." Offer it at the judging table. For people walking through: A* replanning alone hit
  them in 14-36 % of runs; with a range filter on top, 0 %, `[synthetic]` (section 0).
- **Where the answer lives:** [doc 02 section 3.1](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores)
  item 3 (LSY and IMAV randomize layouts); replan design in
  [doc 01 section 1](../../docs/research/close-area-nav/01-planning-and-mapping.md#1-recommendation-in-one-paragraph);
  [close-area-moving-obstacles](../../samples/close-area-moving-obstacles/README.md#results-ran-2026-11-09-apple-m3-max-cpython-31210-numpy-254-scipy-1181).

### 9. "How is this certified? What is the path to product?"

- **Answer pattern:** "We would not certify the planner. The filter is the simple monitor in a
  runtime-assurance design (ASTM F3269 pattern); the stock autopilot failsafe is the fallback.
  Monitor and fallback carry the safety argument." Do not claim a level or a compliance.
- **Where the answer lives:** [path-to-product.md sections 3, 4 and 6](../../docs/path-to-product.md#4-runtime-assurance-ship-the-new-algorithm-next-to-a-trusted-baseline);
  [ASTM F3269](../../catalog/resources/astm-f3269-21-rta.md) (paywalled; free explanation
  [Nagarajan 2021](../../catalog/resources/nagarajan-2021-astm-f3269-scitech.md)). Civil operations:
  [SORA 2.5](../../catalog/resources/easa-ed-decision-2025-018-r-sora-2-5.md).

### 10. "What breaks it?"

- **Answer pattern:** name the failure case you ran on purpose and show it. Then the ones you did
  not run: an obstacle that is neither sensed nor mapped, a "second source" that shares VIO's error,
  range delay, wind. For H1: a symmetric corridor (80 %, median recovery about 11 s after a move) and a
  room with no map.
- **Where the answer lives:** [doc 04 section 3.5](../../docs/research/close-area-nav/04-innovation-prior-art.md#35-failure-modes);
  [doc 03 section 6](../../docs/research/close-area-nav/03-close-area-localization.md#6-failure-modes-to-rehearse-on-day-1).
  Our failure run: pending: `<run id from runs/results.md>`.

## 6. Numbers to fill and where they come from

Context numbers (C) are the hub's, never "ours". Result numbers (R) for the kill test are the
hub's seed-0 runs until your team reruns them; R-H1 rows are the hub's relocalization runs. Say
"hub run" if you present them without rerunning.

| # | Number | Where it comes from | Label | Status |
|---|---|---|---|---|
| C1 | OpenVINS stereo VIO, ATE 0.36 m, max 1.57 m over 278.3 m | [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md#results), [evidence matrix section 5](../../docs/evidence-matrix.md#5-relative-navigation-and-drift-without-gnss) | `[real]` UZH-FPV, 2 runs | Hub-measured |
| C2 | OpenVINS-fitted drift model with the default filter tuning: 358 of 600 epochs misleading | [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md#altpnt-integrity-with-a-measured-relative-source), matrix section 3 | `[synthetic]`, error models fitted on real data, long-range scenario | Hub-measured; say "long-range scenario, same lesson" |
| C3 | FAST-LIO2 NEES about 21x too tight per axis | `smfeval` README via [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#is-the-reported-covariance-realistic-evidence) | code README, not re-run by the hub | Quote only as "reported by the smfeval authors" |
| R1 | Collision % per arm, none / jump / bias / dropout: F2 3 / 11 / 7 / 4, F3 0 / 9 / 3 / 1, F4 0.2 m 0 / 0 / 0 / 1, F5 ours 0 / 0 / 0 / 0 | [kill_d_summary_0.md](../../samples/close-area-safety-filter/results/kill_d_summary_0.md) | `[synthetic]`, seed 0, 100 layouts | Hub-measured; held-out pending (item 37) |
| R2 | Reached % per arm, same order: F2 72 / 33 / 33 / 59, F5 64 / 20 / 28 / 51 (61-89 % of F2, bar 90 %: FAIL); F5 stuck 36 / 80 / 72 / 49 | same | `[synthetic]`, seed 0 | Hub-measured; held-out pending |
| R3 | Filter intervention fraction: F2 0.23-0.24, F5 0.36-0.49 (VIO cases) | same | `[synthetic]`, seed 0 | Hub-measured |
| R4 | Same comparison in PX4 SITL, fewer layouts | `<NUMBER from runs/results.md>` | `[SITL]` | pending |
| R5 | Loop time p99 on the target board | `<NUMBER from runs/results.md>` | measured on `<board>` | pending |
| R6 | Real-flight completions, if a drone is given | `<NUMBER from runs/results.md>` | `[real]` | pending |
| R-H1a | Reached % (dropout / jump): estimator only 64 / 36; hover + match + move 99 / 99 (seed 0), 100 / 100 (seed 1); 0 wrong commits | [reloc_random_0.md](../../samples/close-area-relocalize/results/reloc_random_0.md), [disamb_random_0.md](../../samples/close-area-relocalize/results/disamb_random_0.md), [disamb_random_1.md](../../samples/close-area-relocalize/results/disamb_random_1.md) | `[synthetic]`, 100 layouts per fault | Hub-measured, held-out seed included |
| R-H1b | Corridor: commit-at-once 8 of 20 wrong commits; ours 80 % reached, 0 wrong | [disamb_corridor.md](../../samples/close-area-relocalize/results/disamb_corridor.md) | `[synthetic]`, 20 runs, one geometry | Hub-measured |
| R-H1c | Time to confirmed pose: median 0.4 s; after a move 1.95-2.9 s median | [relocalize README](../../samples/close-area-relocalize/README.md#disambiguating-moves-after-a-hover-timeout-loop-22b) | `[synthetic]` | Hub-measured |
| R-H1d | Same on the organisers' map or drone | `<NUMBER from runs/results.md>` | `[SITL]` / `[real]` | pending |

Every R number also goes into `runs/results.md` with layouts, seeds and the command that made it.

## 7. Not verified

- No row of this scaffold was rehearsed or timed.
- Kill-test thresholds, IMAV factors and PX4 parameter defaults come from the close-area research
  docs, which read most papers as abstracts only and the IMAV rulebook with a crude parser.
- The authors' PX4-CBF and Belief-CBF code was not run. Since this page was first written, doc 05
  read both papers in full and the safety-filter sample re-implemented them in Python as F2 and
  F3 (synthetic), so section 1's "abstract only" labels are stale.
- The ~0.8 m doorway width is the research lane's estimate, not a measurement.
- R1-R3 are seed 0. The held-out rerun (Part e of the safety-filter README) gave the FAIL verdict
  above; quote it, not the seed-0 rows, if a judge asks about the safety filter.
- Every hub number on this page is `[synthetic]` except C1. None is SITL or flight.
- The relocalization seed-1 run was reproduced for this page (same table, wall 64.8 s, Apple
  laptop, 3 arms); the seed-0 and corridor runs were not rerun, their numbers are copied from the
  sample's result files.

### Narrowed since (reconciled 2026-11-09, loop-28)

Later runs in the same samples narrow the H1 numbers in section 0 (last row) and section 3. Say
these with the H1 numbers. All `[synthetic]`; the relocalization arm is (f), the info-gain move.

- **Held-out matrix, seeds 2-4 x 7 families, 72 beams:** "99-100 %, 0 wrong commits" holds only
  on random and u_trap (100.0 % [97.9, 100.0], 0 wrong). FAIL on office 94.4 %, glass_office
  83.3 %, narrow_gap 85.6 % (4 wrong), warehouse 97.2 % (33 wrong) and maze 97.2 % (6 wrong).
  (f) collided in 4-7 % (office), 16-18 % (glass_office) and 10-12 % (narrow_gap) of runs
  ([held-out matrix](../../samples/close-area-relocalize/README.md#held-out-matrix-seeds-2-4-7-families-harder-faults-loop-56)).
  Jumps of 1 m and 2 m and a 5 s dropout on random seed 2: 100 %, 0 wrong commits, so "one jump
  size" in the H1 limits is answered for random layouts.
- **4-beam Crazyflie-like sensor:** without a yaw spin the matcher accepted 0 poses; spin + move
  reached 48 % / 64 % (dropout / jump) vs 98 % / 100 % on 72 beams, 0 wrong commits, 3 % / 7 %
  collisions, median 9-12 s spinning per loss event. Under dropout that is worse than no
  relocalization (64 %)
  ([4-beam](../../samples/close-area-relocalize/README.md#relocalization-with-a-4-beam-sensor-hover-and-yaw-spin-loop-54)).
- **Map with errors (H1 said "not measured"):** FAIL on unmapped added obstacles, 89 / 88 %
  reached, 7 % collisions, 16 / 21 wrong commits; a self-built map from an outbound flight gave
  93.9 / 92.9 % with 2 % collisions. One seed (2)
  ([stale map](../../samples/close-area-relocalize/README.md#imperfect-prior-map-loop-55)).
- **Yaw (H1 limits said "yaw from the estimator"):** a +-15 deg yaw search exists now. Without
  it, a 5 deg heading error took (f) to 38 % reached; with it, 100 %, 0 wrong commits, at 20-23 ms
  instead of 1.8 ms per matched scan. A 180 deg flip in the symmetric corridor fails in every arm
  ([yaw search](../../samples/close-area-relocalize/README.md#yaw-search-3-dof-relocalization-loop-60)).
- **Prior art:** the mechanism exists (Jensfelt 2001, AF-MCL 2026,
  [doc 10](../../docs/research/close-area-nav/10-relocalization-prior-art.md)). An AF-MCL-style arm
  was added later (loop-67, seed 2 held out, synthetic: on the 72-beam sensor the hub's arm reached B as often or more than an AF-MCL-style filter in all 4 cells, 0 wrong commits vs 0-32; on 4 beams every arm fails; [relocalize README](../../samples/close-area-relocalize/README.md#af-mcl-baseline-particle-filter-with-random-particle-injection-loop-67)).
- **Safety filter:** the Part e verdict above is unchanged, FAIL. Do not quote the seed-0 "F5 0 %
  collisions" row of section 2; held out it is 2.5 % [1.1, 5.7] on jump runs
  ([Part e](../../samples/close-area-safety-filter/README.md#part-e-held-out-seeds-and-families-ran-2026-11-09-synthetic)).
