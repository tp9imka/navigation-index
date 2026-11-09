# Close-area A=>B navigation: synthesis

Use this when the brief says A to B, obstacles, indoor, arena, close area, or a marker / pad at
B, and you need the baseline, the localization stack or the headline idea. For a long-range brief
go to [innovation-prior-art](../innovation-prior-art/README.md); both rounds are compared in
[research/README.md](../README.md).

Research round for EDGE hackathon Challenge 2, 2026-11-09, after new information that the task
is likely "move a drone from A to B in a close area, potentially with obstacles". This replaces
the long-range GNSS-denied frame of [innovation-prior-art](../innovation-prior-art/README.md) as
the default. Platform, sensors, indoor or outdoor, and sim vs real are still unknown until Day 1.

The lane docs below are research: nothing in them was run, and thresholds are proposals. The
baseline they recommend has since run on synthetic inputs (2.5D point-mass arena, rendered tag
images), not SITL or flight:
[close-area-arena](../../../samples/close-area-arena/README.md),
[close-area-planner-reactive](../../../samples/close-area-planner-reactive/README.md) and
[fiducial-goal-apriltag](../../../samples/fiducial-goal-apriltag/README.md), followed by the
kill test, relocalization, moving obstacles, sensor presets and complex arenas (all synthetic).
Numbers: [evidence matrix section 14](../../evidence-matrix.md#14-close-area-ab). The headline's
kill test ran to a verdict. **Verdict after held-out seeds (Part e, synthetic):** FAIL. A hand-tuned fixed bound (MR-CBF 0.2 m) stays at <= 1 % collisions in every case on seeds 0-2; ours (F5, PL margin + hover on ambiguity) collides in 2.5 % [1.1, 5.7] of held-out jump runs and reaches B less often. Headline moves to relocalization after VIO loss; the range filter under any planner and the integrity monitor remain supporting results ([close-area-safety-filter](../../../samples/close-area-safety-filter/README.md)).
**Status after loop-61 (2026-11-09):** the planner question is answered by measurement, not by
the lane docs: [close-area-benchmark](../../../samples/close-area-benchmark/README.md) flies 14
planners x 8 room families x 2 range sensors (20 layouts per cell, synthetic). With a prior map A*
reached 100 % with 0 % collisions everywhere; without one, 4 beams break offices, warehouses and
glass rooms. Picks per family and sensor: [cheat sheet section 3](../../cheatsheets/close-area-a-to-b.md#3-which-planner-first).
The relocalization headline was narrowed by its own held-out runs (open layouts and a dense sensor
only), and its mechanism exists ([10](10-relocalization-prior-art.md)). Decision: pitch the
measured toolkit plus the narrow claim that fits the real brief
([research README, decision](../README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is)).
Docs 01-04 read most
papers as abstracts only; 05 read its four baselines in full. Each doc labels its sources
and has a "not verified" section.

| Page | Use it when | You get |
|---|---|---|
| [01](01-planning-and-mapping.md) planning and mapping | You pick the planner and map | Python baseline: 3D numpy grid + ESDF (scipy) => A* with clearance cost => shortcut => RotorPy MinSnap, replan 2-5 Hz. Same planner drives SITL over MAVSDK Offboard (PX4) or GUIDED (ArduPilot) |
| [02](02-sims-platforms-competitions.md) sims, platforms, competitions | You pick a simulator or need to know what judges score | Light sim: gym-pybullet-drones (fallback RotorPy). Product sim: PX4 SITL + gz Harmonic native on Apple Silicon (`x500_depth`, `walls`, `forest`). Judges reward completion, onboard autonomy, no manual help |
| [03](03-close-area-localization.md) localization | You pick the estimator, or VIO is lost indoors, or B is a marker | Indoor: stereo VIO into EKF2 / EKF3 as ODOMETRY, AprilTags at A and B, flow + rangefinder as backup. Outdoor: GNSS (RTK if offered) with VIO as fallback, marker for the last metres |
| [04](04-innovation-prior-art.md) innovation prior art | You need the headline idea, its prior art and the kill test (section 3.4) | Headline proposed there: integrity-aware safety filter (kill test FAIL on held-out seeds, see below). Support: uncertainty-aware replan trigger. Perception-aware planning parked. Its wider scan ranks relocalization after VIO loss, now the headline |
| [05](05-cbf-baselines-faithful.md) safety-filter baselines read in full | You implement a kill-test arm (PX4-CBF, Belief-CBF, gatekeeper, MR-CBF) | Shipped PX4-CBF (NTNU fork, branch `cbf`) has no FoV constraint; the paper's FoV QP is in an older commit. MR-CBF and gatekeeper already take an error bound, so the claim is producing a bound that stays valid under faults. Belief-CBF also predicts covariance growth; a plain sqrt(lambda_max) inflation is weaker than the paper |
| [06](06-task-phrasing-survey.md) task phrasing survey | You guess the Day-1 task shape, scoring, or questions for the organisers | 10 events. B is usually a marker or pad, late-issued coordinates, or a nominal pose revealed up close (LSY within 0.7 m). Off-board help is penalised, not banned (IMAV 1.0 / 0.7 / 0.4). Most likely Day-1 shape: a marked B in a small known arena with a few static obstacles |
| [07](07-pl-margin-prior-art.md) kill search for the headline | You pitch the headline and must say what is new | **The idea as first worded exists.** Tan et al. IROS 2025 (Caltech + TII, PX4 X500 with a geofence) and Zhang, Li, Clark TAC 2025 (fault-excluded EKF bank feeding a CBF) already set safety margins from fault-excluded estimates. What survives is a composition, see below |
| [08](08-crazyflie-sensing-limits.md) Crazyflie sensing limits | The platform is a Crazyflie with Multi-ranger and Flow decks, or you set arena sensor realism | Four 27 deg beams see 30 % of the horizontal circle; obstacles passed close drop out of view; glass is invisible (BatDeck preprint: one forward ranger crashed in 10 of 10 real flights, mostly at glass doors); range falls from about 3.6 m in the dark to about 0.73 m in strong light; 10 Hz. Derived geometry, not measured. Its "crazyflie" preset is now in the arena: glass-family collisions 90-100 % ([sensor realism](../../../samples/close-area-arena/README.md#sensor-realism-crazyflie-presets-and-glass-ran-2026-11-09-synthetic), synthetic) |
| [09](09-vio-nees-feasibility.md) VIO NEES feasibility | You want one measured number for VIO overconfidence | Plan, not run: yes, with OpenVINS on the UZH-FPV bag relative-nav-benchmark already uses (~21-29 min, needs a Docker build). Only OpenVINS writes a covariance; VINS-Fusion and ORB-SLAM3 do not. Published NEES: 131-363 vs 3 expected for a sliding-window VI filter on EuRoC (Lisus et al. RA-L 2023) |
| [10](10-relocalization-prior-art.md) relocalization prior art | You pitch relocalization after VIO loss and must say what is new | Kill search for the second headline: the mechanism exists (Jensfelt and Kristensen 2001; AF-MCL on a small indoor drone), so claim no novelty |

## Findings that change the plan

- **PX4 no longer plans around obstacles.** The companion avoidance interface (`COM_OBS_AVOID`) is
  removed; Collision Prevention (`CP_DIST`) only works in Position mode and only stops. A=>B
  avoidance on PX4 means our own planner sending Offboard setpoints. ArduPilot BendyRuler /
  Dijkstra's do work in GUIDED and are the zero-code fallback.
- **A range-only safety filter already exists inside PX4.** ntnu-arl/PX4-CBF (ICUAS 2025,
  BSD-3, checked with gh api) filters the setpoint from onboard ranges with no position estimate.
  Belief-CBF (Vahs 2023) already inflates clearance by the EKF covariance. Both are baselines,
  not our idea.
- **Reported covariance is not trustworthy.** VIO and LIO filters are overconfident (FAST-LIO2
  median NEES about 21x too tight per axis in the smfeval README, not re-run). Gate on
  ODOMETRY `quality`, `reset_counter` and rejected fusions, not on covariance alone.
- **Estimation, not planning, broke past competitions** (AlphaPilot, IROS ADR, SubT, per lane 02).
- **License traps:** SUPER and IPC (HKU) have no LICENSE file => read-only. Bubble Planner has
  no official code. Only nvblox needs CUDA; OctoMap, OMPL and numpy/scipy run on the Mac.

## Recommended direction

Status after the kill tests (2026-11-09, synthetic): the story below was the plan. Its headline
(step 2) **failed on held-out seeds**. The backup, **relocalization after VIO loss**
([close-area-relocalize](../../../samples/close-area-relocalize/README.md)), reached 100 % with 0
wrong commits on random and u_trap layouts (held-out seeds 2-4), against 36-64 % with the
estimator alone, but failed in office, warehouse, maze, narrow_gap and glass_office, on a 4-beam
sensor (48-64 %) and with unmapped added obstacles (7 % collisions); known map only. Final
decision: [research README](../README.md#decision-2026-11-09-evening-what-the-close-area-innovation-claim-is).
For the step-1 planner pick use [close-area-benchmark](../../../samples/close-area-benchmark/README.md). Pitch: [close-area story H1](../../../templates/pitch/close-area-story.md#3-alternative-hooks-if-the-kill-test-fails).
Steps 1 and 3 and the range filter of step 2 still stand.

The original story: **any planner gets the drone from A to B; our filter keeps it safe when the
drone is wrong about where it is.**

1. **Baseline (hour 0-6).** The lane 01 Python planner in a light sim, written against three
   calls (`pose()`, `ranges()`, `send_setpoint()`) so it ports to Crazyflie, Tello or PX4.
   Now runnable (synthetic only, 2026-11-09):
   [close-area-arena](../../../samples/close-area-arena/README.md) (seeded 2.5D arena, truth
   scorer, `planners/astar_esdf.py`, `estimator.py` + `run_faults.py`, `score_log.py`),
   [close-area-planner-reactive](../../../samples/close-area-planner-reactive/README.md) (APF,
   VFH+, 4-beam fan), [fiducial-goal-apriltag](../../../samples/fiducial-goal-apriltag/README.md)
   (marker goal at B), the [flight-repo](../../../templates/flight-repo/README.md) loop and the
   [drone-adapter drivers](../../../templates/drone-adapter/drivers/README.md) (unrun stubs).
   Day-1 routing: [day1-close-area-intake](../../day1-close-area-intake.md). Measured numbers:
   [evidence matrix section 14](../../evidence-matrix.md#14-close-area-ab).
2. **Headline: integrity-aware safety filter** (doc 04 idea C). Two barrier sets: obstacles the
   range sensor sees, in the body frame (no position needed, as PX4-CBF); map and geofence
   obstacles, with the margin set by a protection level from a fault-detecting monitor (the
   hub's [multi-source-fde](../../../samples/multi-source-fde/) idea), not the filter covariance.
   Nav health also caps speed and triggers a hover fallback. **Result: FAIL** (see the kill test
   status below). The range barrier alone (PX4-CBF style) is the part to keep: 0 % collisions
   with sensed obstacles under VIO faults and with walking people
   ([close-area-moving-obstacles](../../../samples/close-area-moving-obstacles/README.md)).
3. **Support: replan trigger** (doc 04 idea A). Sustained filter intervention or a protection
   level above half the corridor width => replan on an inflated grid with a stopping-distance
   speed cap.

**Narrowed after [07](07-pl-margin-prior-art.md) (2026-11-09):** fault-aware safety margins are
prior art (Tan et al. 2025, Zhang/Li/Clark 2025). The claim left is the composition: range
barriers for what the drone sees, a protection level for what it cannot, and when the monitor
cannot tell which source is lying, the filter holds a hover instead of dropping the
largest-residual source (FT-CBF) or guessing. Doc 04 section 3.4 now carries the two extra arms
this needs: FT-CBF residual dropping (F3f) and Tan's union of plausible states (F3t).

**Kill test before building more** ([doc 04 section 3.4](04-innovation-prior-art.md#34-falsification-experiment),
arms read faithfully in [05](05-cbf-baselines-faithful.md)): 200 random layouts, injected VIO
jump and bias faults. Pass: breaches 1 % or less, at least 3x lower than Belief-CBF on fault
cases, goal reach at least 90 % of PX4-CBF. Fail and drop the headline if Belief-CBF comes
within 1 pp or PX4-CBF alone is already at 1 % or less. Status: **Verdict after held-out seeds (Part e, synthetic):** FAIL. A hand-tuned fixed bound (MR-CBF 0.2 m) stays at <= 1 % collisions in every case on seeds 0-2; ours (F5, PL margin + hover on ambiguity) collides in 2.5 % [1.1, 5.7] of held-out jump runs and reaches B less often. Headline moves to relocalization after VIO loss; the range filter under any planner and the integrity monitor remain supporting results ([close-area-safety-filter](../../../samples/close-area-safety-filter/README.md)).

**Early signal (synthetic, before the kill test; confirmed by part a):** in the
[arena fault run](../../../samples/close-area-arena/README.md#estimator-and-faults-ran-2026-11-09-synthetic)
(50 layouts per case, 72-beam fan, every obstacle visible to the ranger), range-only planners had
0 % collisions under jump, bias, dropout and overconfidence, and lost reach instead. So the
headline can only win on obstacles the ranger cannot see. Section 3.4 already includes map-only
poles and a geofence box; on a Crazyflie the blind wedges add more ([08](08-crazyflie-sensing-limits.md)).
Kill test part a confirmed it: with every obstacle visible, PX4-CBF had 0 % collisions in every
fault case; only map-only obstacles produced collisions (3-11 %).

From the wider scan: multi-hypothesis relocalization after VIO loss (23/30) is now the headline
(measured, see the status at the top of this section); VLM goal specification (20/30) and
NoMaD/ViNT as the planner under the filter (19/30) stay backups.

## Ask the organisers on Day 1

Full ranked list with reasons: [06 section 4](06-task-phrasing-survey.md). Short form:

Which drone and SDK; real flight, sim or both; sensors (depth, lidar, flow, GNSS, mocap); how B
is given (coordinates, marker, GPS point); known or unknown obstacles; scoring (time,
collisions, autonomy, interventions); onboard or ground compute.
