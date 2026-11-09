# Close-area A=>B navigation: synthesis

Research round for EDGE hackathon Challenge 2, 2026-11-09, after new information that the task
is likely "move a drone from A to B in a close area, potentially with obstacles". This replaces
the long-range GNSS-denied frame of [innovation-prior-art](../innovation-prior-art/README.md) as
the default. Platform, sensors, indoor or outdoor, and sim vs real are still unknown until Day 1.

Nothing in these docs has been run. Thresholds are proposals. Most papers were read as abstracts
only; each lane doc labels its sources and has a "not verified" section.

| Doc | Lane | Bottom line |
|---|---|---|
| [01](01-planning-and-mapping.md) | Planning and mapping | Python baseline: 3D numpy grid + ESDF (scipy) => A* with clearance cost => shortcut => RotorPy MinSnap, replan 2-5 Hz. Same planner drives SITL over MAVSDK Offboard (PX4) or GUIDED (ArduPilot) |
| [02](02-sims-platforms-competitions.md) | Sims, platforms, competitions | Light sim: gym-pybullet-drones (fallback RotorPy). Product sim: PX4 SITL + gz Harmonic native on Apple Silicon (`x500_depth`, `walls`, `forest`). Judges reward completion, onboard autonomy, no manual help |
| [03](03-close-area-localization.md) | Localization | Indoor: stereo VIO into EKF2 / EKF3 as ODOMETRY, AprilTags at A and B, flow + rangefinder as backup. Outdoor: GNSS (RTK if offered) with VIO as fallback, marker for the last metres |
| [04](04-innovation-prior-art.md) | Innovation prior art | Headline: integrity-aware safety filter. Support: uncertainty-aware replan trigger. Perception-aware planning parked |
| [05](05-cbf-baselines-faithful.md) | Safety-filter baselines read in full | Shipped PX4-CBF (NTNU fork, branch `cbf`) has no FoV constraint; the paper's FoV QP is in an older commit. MR-CBF and gatekeeper already take an error bound, so the claim is producing a bound that stays valid under faults. Belief-CBF also predicts covariance growth; a plain sqrt(lambda_max) inflation is weaker than the paper |
| [07](07-pl-margin-prior-art.md) | Kill search for the headline | **The idea as first worded exists.** Tan et al. IROS 2025 (Caltech + TII, PX4 X500 with a geofence) and Zhang, Li, Clark TAC 2025 (fault-excluded EKF bank feeding a CBF) already set safety margins from fault-excluded estimates. What survives is a composition, see below |

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

One story: **any planner gets the drone from A to B; our filter keeps it safe when the drone is
wrong about where it is.**

1. **Baseline (hour 0-6).** The lane 01 Python planner in a light sim, written against three
   calls (`pose()`, `ranges()`, `send_setpoint()`) so it ports to Crazyflie, Tello or PX4.
2. **Headline: integrity-aware safety filter** (doc 04 idea C). Two barrier sets: obstacles the
   range sensor sees, in the body frame (no position needed, as PX4-CBF); map and geofence
   obstacles, with the margin set by a protection level from a fault-detecting monitor (the
   hub's [multi-source-fde](../../../samples/multi-source-fde/) idea), not the filter covariance.
   Nav health also caps speed and triggers a hover fallback.
3. **Support: replan trigger** (doc 04 idea A). Sustained filter intervention or a protection
   level above half the corridor width => replan on an inflated grid with a stopping-distance
   speed cap.

**Narrowed after [07](07-pl-margin-prior-art.md) (2026-11-09):** fault-aware safety margins are
prior art (Tan et al. 2025, Zhang/Li/Clark 2025). The claim left is the composition: range
barriers for what the drone sees, a protection level for what it cannot, and when the monitor
cannot tell which source is lying, the filter holds a hover instead of dropping the
largest-residual source (FT-CBF) or guessing. The kill test needs two more arms: FT-CBF residual
dropping and Tan's union of plausible states.

**Kill test before building more** (doc 04 section 3.4): 200 random layouts, injected VIO jump and
bias faults. Pass: breaches 1 % or less, at least 3x lower than Belief-CBF on fault cases, goal
reach at least 90 % of PX4-CBF. Fail and drop the headline if Belief-CBF comes within 1 pp or
PX4-CBF alone is already at 1 % or less.

Backups from the wider scan: multi-hypothesis relocalization after VIO loss (23/30), VLM goal
specification (20/30), NoMaD/ViNT as the planner under the filter (19/30).

## Ask the organisers on Day 1

Which drone and SDK; real flight, sim or both; sensors (depth, lidar, flow, GNSS, mocap); how B
is given (coordinates, marker, GPS point); known or unknown obstacles; scoring (time,
collisions, autonomy, interventions); onboard or ground compute.
