# Close-area pitch scaffold: A to B through obstacles

Fill this on Day 2 when the task is "fly a drone from A to B in a close area, with obstacles".
It replaces the PNT story families in [story-bank.md](story-bank.md) for that task. The
research behind it is [docs/research/close-area-nav/README.md](../../docs/research/close-area-nav/README.md).
The live-demo script for it is [demo-script-close-area.md](../demo-script-close-area.md).

State on 2026-11-09: nothing in the close-area lane has been run. The safety filter sample
`samples/close-area-safety-filter/` does not exist in the hub yet. Every `<NUMBER from ...>`
below stays a placeholder until a run writes it. A slot you cannot fill is said aloud as
"not measured".

Contents: [Story](#1-the-story) - [Kill test gate](#2-kill-test-gate-decide-the-story-at-h24) -
[Alternative hooks](#3-alternative-hooks-if-the-kill-test-fails) -
[3-minute skeleton](#4-3-minute-skeleton) - [Judge questions](#5-judge-questions) -
[Numbers to fill](#6-numbers-to-fill-and-where-they-come-from) - [Not verified](#7-not-verified)

## Fill order on Day 2

1. **H+24.** Read the kill-test result (section 2). Keep the main story or pick one alternative
   hook (section 3). Cross out the other three.
2. **H+26.** Write the five beats for the chosen story on the wall, one line each.
3. **H+30.** Fill the 3-minute skeleton (section 4) with what actually runs. Record the backup
   video ([demo-script-close-area.md](../demo-script-close-area.md#recording-the-backup)).
4. **H+36.** Rehearse the 10 judge questions (section 5): one person asks, the answerer has 20 s.
   Any answer that still says "pending" is either filled or reworded to "not measured".
5. **H+40.** Score with [judging-self-assessment.md](../judging-self-assessment.md) and copy every
   number into the [one-pager](one-pager-template.md) and `runs/results.md`.

## 1. The story

**One line:** "Any planner gets the drone from A to B; our filter keeps it safe when the drone
is wrong about where it is."

| Beat | Line to say | Filled from |
|---|---|---|
| 1. Problem | "In a close area the gap is about a metre. The drone does not crash because the planner is bad. It crashes because it is wrong about where it is." | Gap size is an estimate in [doc 03 section 1](../../docs/research/close-area-nav/03-close-area-localization.md#1-bottom-line) (doorway ~0.8 m), analysis, not a measurement |
| 2. Why it matters | "Past drone competitions broke on state estimation, not on planning. And the filters that report the uncertainty are overconfident." | [doc 02 section 3.1](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores) item 5; [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#is-the-reported-covariance-realistic-evidence) |
| 3. What we built | "A filter between any planner and the autopilot. It never hits what the range sensor sees. For what it cannot see, the margin comes from a fault-detecting nav monitor, not the filter's own covariance. When nav health drops it slows down and holds a hover." | [doc 04 section 3.2](../../docs/research/close-area-nav/04-innovation-prior-art.md#32-what-may-remain-narrow) |
| 4. Honest numbers | "Over `<NUMBER from samples/close-area-safety-filter/README.md>` layouts with injected VIO jumps and bias, breaches `<NUMBER from samples/close-area-safety-filter/README.md>` vs `<NUMBER from samples/close-area-safety-filter/README.md>` for a covariance margin, `[synthetic]`. Not measured: real flight." | pending: samples/close-area-safety-filter (kill test, doc 04 section 3.4) |
| 5. What's next | "Same filter on PX4 Offboard in SITL, then on the organisers' drone. It ships as a runtime-assurance monitor next to the stock autopilot." | [path-to-product.md section 4](../../docs/path-to-product.md#4-runtime-assurance-ship-the-new-algorithm-next-to-a-trusted-baseline) |

**The narrow claim (say it exactly, do not widen it):** for obstacles the range sensor cannot
see (out of field of view, thin, glass, geofence) and under VIO jumps or bias, a fault-aware
margin beats a covariance margin. Source:
[close-area README](../../docs/research/close-area-nav/README.md#recommended-direction).

**What is not ours, say it first:** range-only filtering inside PX4 is PX4-CBF
([catalog](../../catalog/repos/ntnu-arl__px4-cbf.md), ICUAS 2025, preprint abstract only + code,
BSD-3). A margin from the EKF covariance is Belief-CBF
([catalog](../../catalog/resources/vahs-belief-cbf-2023.md), preprint, abstract only). Our part is
joining them with the hub's integrity monitor
([multi-source-fde](../../samples/multi-source-fde/README.md)). Engineering, not theory.

## 2. Kill test gate (decide the story at H+24)

From [doc 04 section 3.4](../../docs/research/close-area-nav/04-innovation-prior-art.md#34-falsification-experiment)
(thresholds are the research lane's proposal, not measured).

| Result | Story |
|---|---|
| Breach rate of ours 1 % or less, at least 3x lower than the Belief-CBF arm on jump and bias faults, goal reach at least 90 % of the PX4-CBF arm | Keep section 1 |
| Belief-CBF arm within 1 percentage point of ours on jump and bias | Drop the headline. Pick hook H1, H2 or H3 below |
| Range-only arm (PX4-CBF style) already at 1 % or less everywhere | Drop the headline. Honest pitch: "we integrated PX4-CBF and measured it". Use hook H3 |
| Kill test not run by H+24 | Do not pitch section 1 as a result. Use H3 and mention the filter as "next" |

Write the result in `runs/results.md` with arms, layouts, fault cases and seeds before choosing.

## 3. Alternative hooks if the kill test fails

Each hook keeps the five-beat shape. Swap beats 1, 3 and 4 of section 1; beats 2 and 5 mostly stay.

### H1. Relocalization after VIO loss

- **Hook:** "Indoors, VIO will lose track. Our drone does not guess. It holds a hover, keeps two to
  five pose hypotheses and only flies on when one wins."
- **Pick it when:** a prior map or a first pass of the room exists (the hypotheses need something
  to match against), and Day 1 logs show tracking loss.
- **Measure:** time from track loss to a confirmed pose `<NUMBER from runs/results.md>`; wrong
  relocalizations `<NUMBER from runs/results.md>` out of `<NUMBER from runs/results.md>` losses;
  label each `[synthetic]` / `[SITL]` / `[real]`.
- **Hub ground:** ranked first of the wider scan, 23/30, scores are the lane's judgement from
  abstracts and READMEs ([doc 04 section 4](../../docs/research/close-area-nav/04-innovation-prior-art.md#4-wider-scan-ranked)).
  Health signals to trigger it: ODOMETRY `quality`, `reset_counter`, `vo_state`
  ([doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#4-estimator-health-signals-a-planner-can-consume)).
- **Say also:** in a never-seen room there is nothing to relocalize against. Say so before a judge does.

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
- **Pick it when:** the kill test failed or was not run, and the baseline planner flies reliably.
- **Measure:** completion rate, collisions, stuck count, time to goal over random layouts; any
  intervention by a person. Report "stuck" apart from "reached" and "crashed"
  ([doc 04 section 1.5](../../docs/research/close-area-nav/04-innovation-prior-art.md#15-failure-modes)).
- **Hub ground:** judges score completion before speed, onboard autonomy as a multiplier and
  replanning on moved obstacles ([doc 02 section 3.1](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores)).
  Baseline recipe: [doc 01 section 5](../../docs/research/close-area-nav/01-planning-and-mapping.md#5-fastest-credible-baseline).
- **Say also:** "no new algorithm; the contribution is a measured, honest baseline and the health
  log". If PX4-CBF is inside, name it.

## 4. 3-minute skeleton

Same beats as [pitch-structure.md](pitch-structure.md#3-minute-skeleton). Screen content per
20 s is in [demo-script-close-area.md](../demo-script-close-area.md#script).

| Time | Beat | Say | Show |
|---|---|---|---|
| 0:00-0:20 | Problem | The one-line story (or the chosen hook). The platform and sensors the organisers gave us | Title slide: top-down view of the course, A and B marked |
| 0:20-0:40 | Why it matters | "Estimation broke past competitions, and reported covariance is overconfident." One hub number with its label (section 6, rows C1-C2) | One slide, one number, label in the corner |
| 0:40-1:00 | What we built | planner => safety filter => autopilot; nav monitor => margin and speed cap. Say which boxes are real and which are stubs. Say where each box runs | Architecture slide |
| 1:00-2:00 | Live demo | Same seed, two arms side by side; VIO fault injected; covariance-margin arm breaches the unseen obstacle, ours widens, slows, holds, reaches B; then our failure case | Sim view full screen |
| 2:00-2:35 | Honest numbers | Ours vs PX4-CBF-style vs Belief-CBF-style, layouts x fault cases, `[synthetic]` or `[SITL]`, stuck rate, one "not measured" | Results table |
| 2:35-3:00 | What's next | Runtime-assurance path, next three steps, scope line ("the vehicle's own navigation only") | Path-to-product slide ([path-to-product.md section 6](../../docs/path-to-product.md#6-the-path-to-product-slide)) |

Cut order if over time: "What we built" shrinks to one sentence first. "Honest numbers" never
goes below "ours vs baseline, N layouts, label".

## 5. Judge questions

Rehearse with a timer: 20 s per answer. "Where the answer lives" is the file to open if a judge
asks for evidence. "pending: X" means the hub has no answer yet; fill X on Day 1-2 or say
"not measured".

### 1. "Why not just use the lidar / rangefinder?"

- **Answer pattern:** "For what the sensor sees, we do, and we need no position for it. Our margin
  only matters for what it cannot see: outside the field of view, thin poles, glass, the geofence,
  and when the sensor itself degrades. Here is the run where the range-only arm hits one of those."
- **Where the answer lives:** [doc 04 section 0](../../docs/research/close-area-nav/04-innovation-prior-art.md#0-one-finding-that-shapes-all-three-ideas);
  range-only arm result: `<NUMBER from samples/close-area-safety-filter/README.md>` (pending:
  samples/close-area-safety-filter).

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
  faults the covariance arm breached `<NUMBER from samples/close-area-safety-filter/README.md>`,
  ours `<NUMBER from samples/close-area-safety-filter/README.md>`, `[synthetic]`." If the kill test
  failed, say that and switch to the hook you picked.
- **Where the answer lives:** kill test in [doc 04 section 3.4](../../docs/research/close-area-nav/04-innovation-prior-art.md#34-falsification-experiment);
  overconfidence evidence in [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#is-the-reported-covariance-realistic-evidence).
  Result pending: samples/close-area-safety-filter.

### 4. "What if VIO is lost?"

- **Answer pattern:** name the trigger (ODOMETRY `quality`, `reset_counter`, tracking state,
  innovation rejects), the action (speed cap => hover, flow + rangefinder keep the hover), and how
  long the hover holds before land. Then show the run.
- **Where the answer lives:** [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#4-estimator-health-signals-a-planner-can-consume)
  and [section 5a](../../docs/research/close-area-nav/03-close-area-localization.md#a-indoor-no-gnss);
  VIO-to-autopilot plumbing in [vio-to-mavlink-bridge](../../samples/vio-to-mavlink-bridge/README.md)
  (EKF fusion checked in SITL with a constant pose, not in flight). Hover drift after loss:
  pending: `<NUMBER from runs/results.md>`.

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

- **Answer pattern:** give goal reach and stuck count next to the breach rate. "Goal reach
  `<NUMBER from samples/close-area-safety-filter/README.md>` of the range-only arm's; stuck in
  `<NUMBER from samples/close-area-safety-filter/README.md>` layouts; the filter changed the command
  on `<NUMBER from samples/close-area-safety-filter/README.md>` of steps."
- **Where the answer lives:** pass rule (goal reach at least 90 % of PX4-CBF arm) and the
  freezing-robot failure mode in [doc 04 sections 1.5 and 3.4](../../docs/research/close-area-nav/04-innovation-prior-art.md#34-falsification-experiment).
  Result pending: samples/close-area-safety-filter.

### 8. "What if we move an obstacle? Is the path hard-coded?"

- **Answer pattern:** "Random layouts in every test, replanning at `<NUMBER from runs/results.md>` Hz.
  Move one now." Offer it at the judging table.
- **Where the answer lives:** [doc 02 section 3.1](../../docs/research/close-area-nav/02-sims-platforms-competitions.md#31-what-this-tells-us-a-judge-scores)
  item 3 (LSY and IMAV randomize layouts); replan design in
  [doc 01 section 1](../../docs/research/close-area-nav/01-planning-and-mapping.md#1-recommendation-in-one-paragraph).

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
  range delay, wind.
- **Where the answer lives:** [doc 04 section 3.5](../../docs/research/close-area-nav/04-innovation-prior-art.md#35-failure-modes);
  [doc 03 section 6](../../docs/research/close-area-nav/03-close-area-localization.md#6-failure-modes-to-rehearse-on-day-1).
  Our failure run: pending: `<run id from runs/results.md>`.

## 6. Numbers to fill and where they come from

Context numbers (C) are the hub's, never "ours". Result numbers (R) are ours; all pending on
2026-11-09.

| # | Number | Where it comes from | Label | Status |
|---|---|---|---|---|
| C1 | OpenVINS stereo VIO, ATE 0.36 m, max 1.57 m over 278.3 m | [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md#results), [evidence matrix section 5](../../docs/evidence-matrix.md#5-relative-navigation-and-drift-without-gnss) | `[real]` UZH-FPV, 2 runs | Hub-measured |
| C2 | OpenVINS-fitted drift model with the default filter tuning: 358 of 600 epochs misleading | [relative-nav-benchmark](../../samples/relative-nav-benchmark/README.md#altpnt-integrity-with-a-measured-relative-source), matrix section 3 | `[synthetic]`, error models fitted on real data, long-range scenario | Hub-measured; say "long-range scenario, same lesson" |
| C3 | FAST-LIO2 NEES about 21x too tight per axis | `smfeval` README via [doc 03 section 4](../../docs/research/close-area-nav/03-close-area-localization.md#is-the-reported-covariance-realistic-evidence) | code README, not re-run by the hub | Quote only as "reported by the smfeval authors" |
| R1 | Breach rate per arm (F0-F4), jump and bias faults | `<NUMBER from samples/close-area-safety-filter/README.md>` | `[synthetic]` | pending |
| R2 | Goal reach and stuck count per arm | `<NUMBER from samples/close-area-safety-filter/README.md>` | `[synthetic]` | pending |
| R3 | Filter intervention rate | `<NUMBER from samples/close-area-safety-filter/README.md>` | `[synthetic]` | pending |
| R4 | Same comparison in PX4 SITL, fewer layouts | `<NUMBER from runs/results.md>` | `[SITL]` | pending |
| R5 | Loop time p99 on the target board | `<NUMBER from runs/results.md>` | measured on `<board>` | pending |
| R6 | Real-flight completions, if a drone is given | `<NUMBER from runs/results.md>` | `[real]` | pending |

Every R number also goes into `runs/results.md` with layouts, seeds and the command that made it.

## 7. Not verified

- No row of this scaffold was rehearsed or timed.
- Kill-test thresholds, IMAV factors and PX4 parameter defaults come from the close-area research
  docs, which read most papers as abstracts only and the IMAV rulebook with a crude parser.
- PX4-CBF and Belief-CBF descriptions come from abstracts and READMEs (doc 04); their code was not run.
- The ~0.8 m doorway width is the research lane's estimate, not a measurement.
