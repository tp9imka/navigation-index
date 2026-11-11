# 03. Localization and state estimation for short-range A => B in a cluttered close area

Research lane, 2026-11-09, for a close-area A=>B task. Working assumption: "move a drone
from A to B in a close area, possibly with obstacles". Indoor vs outdoor, GNSS, sensors and
platform are unknown until the task is announced. Scope: the vehicle's own navigation.

Records added: `data/repos/close-area-localization.json` (7 repos, each checked with
`gh api repos/...` on 2026-11-09) and `data/resources/close-area-localization.json`
(15 resources). Already in the hub and used below: OpenVINS, VINS-Fusion, ORB-SLAM3,
Kimera-VIO, Basalt, cuVSLAM / Isaac ROS Visual SLAM, FAST-LIO2, Point-LIO, GLIM, DLIO,
Crazyflie firmware, Loco UWB, PX4 / ArduPilot optical-flow docs, PX4 external-vision doc,
`samples/relative-nav-benchmark`, `samples/vio-to-mavlink-bridge`.

Source labels:

- **peer-reviewed** - journal or conference paper; "(abstract)" if only the abstract was read.
- **preprint** - arXiv, abstract page read.
- **code** - repository checked with `gh api`, README read, code not run.
- **docs** - vendor or project documentation page read.
- **community** - forum post or single-author benchmark, not reviewed.
- **hub-measured** - number produced by a sample in this repo.

## 1. Bottom line

- In a close area the error budget is small (a doorway is ~0.8 m, an obstacle gap maybe
  1 m), so **drift per metre matters less than jumps, resets and lost tracking**. A VIO
  that drifts 0.3 % is fine over 50 m (~15 cm). A VIO that silently loses tracking for 2 s
  during a fast yaw is not.
- **Default indoor stack: stereo + IMU VIO on a companion, fed to PX4 EKF2 as ODOMETRY
  (or ArduPilot EKF3 ExternalNav), with AprilTags at A and B, flow + downward rangefinder
  as the backup velocity source.** Mocap or Lighthouse, if the venue has it, replaces VIO
  for localization in one launch file.
- **Default outdoor stack: GNSS (RTK if offered) in EKF2/EKF3 for the global frame, VIO
  running in parallel as the local and fallback source, B as a GNSS point plus a fiducial
  or detected marker for the last few metres.**
- **Do not trust reported covariance as-is.** Every source checked says VIO / LIO filters
  are overconfident. Inflate by a factor fitted on first-day logs and gate on tracking
  quality, feature count and reset events instead.

## 2. Sensor options

Accuracy column: what was actually found. "-" means no number was verified for this lane.

| Option | Gives | Accuracy evidence | Drift | Main failure modes | Compute | License | Feed into autopilot |
|---|---|---|---|---|---|---|---|
| Motion capture (VICON, OptiTrack, Qualisys) | Absolute 6-DoF pose | mm per vendor table (Bitcraze overview, docs); 0.1 mm static jitter as reference in Taffanel 2021 (preprint) | None inside the volume | Line of sight, marker occlusion, reflective surfaces; only exists if the venue has it | Offboard | Commercial; `vrpn_mocap` MIT (code) | `vrpn_mocap` => MAVROS `vision_pose` => VISION_POSITION_ESTIMATE / ODOMETRY; PX4 EKF2 `EKF2_EV_CTRL`, ArduPilot `VISO_TYPE=1`, `EK3_SRC1_POSXY=6` |
| Bitcraze Lighthouse | Absolute position (Crazyflie deck) | Mean / median 2-4 cm vs mocap, flight outliers ~5 cm, jitter 0.3-3.9 mm (Taffanel 2021, preprint + code). Vendor table says "mm" (docs) | None in coverage | Line of sight; glass and mirrors; volume ~8x8x3 m with up to 4 base stations (docs) | Onboard Crazyflie EKF | Firmware GPL-3.0 | Native in Crazyflie firmware; not a PX4 / ArduPilot path |
| UWB anchors (Loco LPS, others) | Absolute position | Static TWR: per-axis jitter ~0.5-2 cm, one 3D point ~0.24 m error, raw ranges biased short 0.2-0.4 m by antenna delay (Bitcraze wiki, docs, "not a specification"). Vendor table: "dm" | None, but bias from anchor survey errors | NLOS through people / metal, anchor placement, poor Z geometry when anchors share a height | Light | Crazyflie GPL-3.0 | Crazyflie native; ArduPilot has a Beacon source (`EK3_SRC1_POSXY=4`) |
| Optical flow + downward rangefinder (PX4 Flow, PMW3901 / Flow deck, MTF-01 class) | Ground-relative velocity + height | - (no measured number found for this lane). ToF height "within a few mm", 4 m max on Flow deck v2 (docs) | Position = integrated velocity, grows with distance and heading error | Texture-poor or glossy floors, low light, height beyond ranger, propwash dust, fast yaw if gyro compensation is off | Tiny | Hardware | PX4 EKF2 optical flow (`EKF2_OF_CTRL`, `EKF2_OF_QMIN`); ArduPilot `EK3_SRC1_VELXY=5` |
| Stereo / mono + IMU VIO (OpenVINS, VINS-Fusion, Basalt, Kimera-VIO, ORB-SLAM3) | Local 6-DoF pose, velocity | OpenVINS stereo on UZH-FPV indoor_forward_3: ATE 0.36 m, final error 0.26 % over 278 m (hub-measured, `samples/relative-nav-benchmark`). Delmerico 2018: ranking depends on the onboard computer (peer-reviewed, slides only) | Yes; yaw and position unobservable, so drift is unbounded without landmarks / loop closure | Low texture, white walls, darkness, motion blur on fast yaw, dynamic objects, IR emitter dots on RealSense, bad time sync, bad IMU-camera calibration | CPU, 1-2 cores on Jetson / NUC class | OpenVINS, VINS-Fusion, ORB-SLAM3 GPL-3.0; Basalt BSD-3; Kimera-VIO BSD-2 | ROS topic => MAVROS / `vision_to_mavros` / `samples/vio-to-mavlink-bridge` => ODOMETRY; EKF2 `EKF2_EV_CTRL`, `EKF2_EV_DELAY`; EKF3 `VISO_TYPE=1`, `EK3_SRC1_*=6` |
| cuVSLAM / Isaac ROS Visual SLAM | Stereo VIO + SLAM | - here (see `res:cuvslam-2025` in the hub) | Bounded if loop closure fires | Same as VIO; needs NVIDIA GPU | Jetson GPU | Isaac ROS wrapper Apache-2.0; cuVSLAM core NOASSERTION (check terms) | Same ROS => MAVROS path; publishes `vo_state` 0/1/2 (code) |
| ModalAI VOXL 2 VIO (qVIO or OpenVINS server) | Local pose + health | No accuracy claim in the docs | As VIO | Auto-reset on >20 m/s, low features for 10 s, or spinning in place (docs) | On VOXL | Platform-bound | Forwards odometry to PX4 on the same board (docs); ArduPilot `VISO_TYPE=3` |
| Intel RealSense T265 (legacy) | VIO pose from a sealed module | No vendor drift spec found | As VIO | End of life, sales stopped 2022 (docs); do not plan on one | On camera | Hardware | ArduPilot `VISO_TYPE=2`; hub doc `res:ardupilot-vio-tracking-camera` |
| LiDAR-inertial (FAST-LIO2, Point-LIO, DLIO, GLIM) on Livox Mid-360 class | Local pose + map | In a VICON arena on Mid-360 + Orin NX: APE RMSE GLIM 0.040 m (GPU, loop closure), DLIO 0.096 m, FAST-LIO2 0.112 m, KISS-ICP 0.123 m (community, GT was Pixhawk EKF fused with VICON) | Low; FAST-LIO paper reports <0.3 % indoor on 32 m (peer-reviewed, via search summary, not read) | Degenerate geometry (long corridor, open field), minimum range blind zone near walls, point timestamp loss, 10 Hz output unless IMU-propagated (Gaona 2026, preprint) | CPU, Orin-class | FAST-LIO GPL-2.0; Point-LIO NOASSERTION; GLIM / DLIO MIT | ROS => MAVROS ODOMETRY; raise output rate to IMU rate before feeding EKF2 |
| AprilTag / ArUco landmarks | Camera-relative pose to a known tag | - (accuracy papers found but not read) | None while a tag is in view | Small or far tags at near-frontal view => pose ambiguity; blur; partial occlusion | Light CPU | AprilTag BSD-2; `apriltag_ros` MIT | As goal: LANDING_TARGET or a planner goal. As landmark: tag map => pose => VISION_POSITION_ESTIMATE (COEX Clover does this, hub `repo:copterexpress/clover`) |
| GNSS standalone | Global position | - (metre-level is common knowledge, not verified here) | None | Multipath and blockage near buildings and trees | None | - | Native |
| RTK GNSS | Global position | - (cm-level with a fixed solution, hub RTK records; not re-verified here) | None when fixed | Float / lost fix under cover, base-station link | Light | - (RTKLIB licence not re-checked) | Native; GPS_INPUT or a second GPS |

## 3. How "B" is specified, and what it implies

No primary source on hackathon task phrasing was searched (out of scope). The options below
are analysis.

| B given as | Localization implied | Notes |
|---|---|---|
| Coordinates in a local frame ("3 m forward, 10 m right of A") | Any local odometry from A; drift must be small vs the goal tolerance | Simplest. A VIO / flow stack started at A is enough. Ask what the tolerance is. |
| Coordinates in a venue frame (mocap / UWB / Lighthouse frame) | Must use the venue's absolute system or align to it | Alignment of VIO to the venue frame needs at least one known pose; an AprilTag at A gives it. |
| GPS point (outdoor) | GNSS, ideally RTK; VIO only for the gap | 2-5 m GNSS error can exceed the close-area tolerance; terminal phase needs a relative cue. |
| A visual marker or object ("land on the H", "fly to the red gate") | Relative goal detection; global localization only needs to be good enough to get it in view | Most robust option for the last metres. PX4 already handles a marker goal via LANDING_TARGET (docs: `PLD_HACC_RAD` default 0.2 m, `PLD_BTOUT` 5 s; the page says it needs a valid global position, so check indoors). |
| "Somewhere behind the obstacles" (search) | Exploration + detection; localization to avoid revisits | Out of this lane; see the planning lane. |

**Relative goal detection as an alternative to global localization.** If B is a marker, the
drone only needs (1) odometry good enough to explore without hitting things and (2) a
detector. Fiducials (AprilTag 3, `apriltag_ros`) give metric pose from a calibrated camera.
A learned detector (any YOLO-class model) gives a bearing and maybe range from size or depth;
it needs training data that only exists on the first day. Recommendation: put an AprilTag next to
the official marker in testing, and keep the learned detector only if whoever set the task forbids
fiducials.

## 4. Estimator health signals a planner can consume

### What the stacks actually publish

| Signal | Where it comes from | Use |
|---|---|---|
| `quality` (-1 failed, 0 unknown, 1-100) | MAVLink ODOMETRY field (MAVLink common.xml, docs) | PX4 `EKF2_EV_QMIN`: EV only fused above this quality. ArduPilot `VISO_QUAL_MIN`: -1 send all, 0 send if good or unknown (parameter refs, docs) |
| `reset_counter` | ODOMETRY and VISION_POSITION_ESTIMATE | Increment on any jump (loop closure, relocalization). Planner should replan from the new pose, not chase the jump |
| Pose / velocity covariance (21-element upper triangle) | Same messages | PX4 `EKF2_EV_NOISE_MD=0` uses the message variance with `EKF2_EVP_NOISE` as a lower bound; `=1` ignores it and uses params (docs) |
| Innovation test ratio | PX4 `EKF2_EVP_GATE` / `EKF2_EVV_GATE` (SD gate, docs); ArduPilot EKF3 innovations | Rejected EV fusions are a direct "VIO disagrees with IMU" flag |
| Tracking state | Isaac ROS `VisualSlamStatus.vo_state` 0 unknown / 1 success / 2 failed (code) | Hard stop / hover trigger |
| Feature count, quality state, auto-reset | ModalAI OpenVINS server: `ov_extended` has covariances, feature counts, quality, error codes; INITIAL / GOOD / BAD hysteresis (docs) | Slow down or rotate toward texture when features drop |
| Spectral power of the velocity estimate | Lanegger 2026: detects 51-58 % of labelled failures at 60-84 % precision on real VIO / LIO / RIO flights (preprint) | Estimator-agnostic second vote |

### Is the reported covariance realistic? Evidence

- **Theory: EKF VIO is overconfident by construction.** Hesch et al. 2014 (peer-reviewed,
  abstract) show standard EKF VINS gains spurious information along unobservable directions,
  so the covariance shrinks too fast. OC-VINS / FEJ fixes this; OpenVINS ships FEJ. Huang
  2010 (already in hub) is the precursor.
- **Systematic, therefore calibratable.** Tsuei et al. ICRA 2021 (peer-reviewed, abstract):
  EKF means are good, covariances are not, and the error is systematic enough to learn a
  correction from ground truth on a real VIO.
- **Tail risk is bigger than benchmarks suggest.** Tsuei and Soatto 2023 (preprint): feature
  attribution errors dominate VIO error; >1 in 100 runs look like the high-noise case even at
  small noise.
- **Measured on LIO, strongly overconfident.** Ronning et al. 2026 (preprint): four ground LIO
  filters all overconfident. `smfeval` README (code, not run here): FAST-LIO2 on Oxford Spires
  christ-church-03 has median translation NEES 1.04e3 vs 2.37 calibrated, ~21x too tight per
  axis, 90 % ellipsoid coverage 0.000.
- **Hub-measured, VIO.** `samples/relative-nav-benchmark` fed OpenVINS errors into
  `altpnt-integrity`: with the default filter tuning, 358 of 600 epochs were misleading; after
  inflating VIO noise the error fell from 495 m RMS to 16.9 m. Long-range scenario, but same
  lesson: the tuned noise was far too tight.
- **Not found:** a peer-reviewed real-flight NEES study for a mainstream VIO (OpenVINS,
  VINS-Fusion) in a small indoor arena. Treat the overconfidence factor for VIO as unknown and
  measure it.

**Practical rule for 48 h.** Record one first-day flight with any reference (mocap, tape-measured
tags, or two estimators against each other with `smfeval pair`, which gives a lower bound on
overconfidence without ground truth). Fit one inflation factor. Feed EKF2 with
`EKF2_EV_NOISE_MD=0` plus that inflation, or `=1` with honest fixed noise. Gate the planner on
quality / features / `reset_counter` / innovation rejects, not on the covariance alone.

## 5. Recommended stacks for a 48 h build

### (a) Indoor, no GNSS

| Layer | Choice | Why |
|---|---|---|
| Autopilot | PX4 EKF2 (or ArduPilot EKF3 if the platform ships it) | Both take external vision via ODOMETRY; bridge exists in the hub |
| Primary pose | If venue mocap / Lighthouse exists: use it. Else stereo + IMU VIO: OpenVINS on CPU, or Isaac ROS Visual SLAM if a Jetson is provided | Mocap ends the localization problem. OpenVINS is the best-documented open VIO and already ran in the hub sample; cuVSLAM is the fast path on Jetson |
| Camera | D435i / D455 with emitter off, or the platform's stereo pair | T265 is EOL |
| Backup velocity / height | Downward flow + ToF / lidar rangefinder into EKF2 | Keeps hover alive when VIO drops; PX4 can fuse both |
| Anchors | AprilTags at A and B (and 2-3 on walls if allowed) | Gives a frame at A, a terminal goal at B, and a drift reset |
| Health | ODOMETRY `quality`, `reset_counter`; `vo_state` or feature count; EKF2 EV innovation rejects | Planner slows, hovers or replans on these |
| LiDAR | Only if the platform carries one: FAST-LIO2 with IMU-rate output | Best in geometry-rich clutter; weight and integration cost are high otherwise |

### (b) Outdoor, GNSS available

| Layer | Choice | Why |
|---|---|---|
| Global frame | GNSS in EKF2 / EKF3; RTK if whoever set the task offers a base | Removes drift; RTK gets close to the obstacle-gap tolerance |
| Local / fallback | The same VIO as indoor, fused as velocity or as a second source; ArduPilot source sets (`EK3_SRC2_*`) or PX4 EV + GNSS together | Bridges multipath near obstacles and GNSS dropouts under cover |
| Goal | GNSS point to get close, AprilTag / marker detection for the last metres | GNSS error is metres; the last metres need a relative cue |
| Health | GNSS fix type / satellites / EKF2 GNSS checks + the VIO signals above | Switch to VIO-led on GNSS degradation |

## 6. Failure modes to rehearse before the first flight

- **Low texture / white walls / dark corners** => VIO feature count collapses. Mitigation:
  flow backup, slow down, yaw toward texture, posters / tags on walls if allowed.
- **Fast yaw** => motion blur and lost tracks. Limit yaw rate in the planner.
- **Lighting changes** (windows, flicker) => exposure jumps. Fix auto-exposure limits.
- **Propwash dust / downwash on the floor** => flow and downward camera degrade at low height.
- **RealSense IR emitter** => dot pattern breaks feature tracking. Turn it off for VIO.
- **Time sync and IMU-camera extrinsics** => slow divergence. Calibrate with Kalibr (in hub);
  tune `EKF2_EV_DELAY` from innovations.
- **Frame conventions** => ENU / FLU vs NED / FRD mistakes. Use `samples/vio-to-mavlink-bridge`
  (unit-tested conversion) or MAVROS `vision_pose`.
- **Relocalization jumps** => EKF2 sees a step. Increment `reset_counter`; replan.
- **LiDAR**: degenerate corridors, near-wall blind zone, 10 Hz output to a 250 Hz controller.
- **Mocap / Lighthouse / UWB**: line of sight, reflective surfaces, anchor survey errors.

## 7. Not verified

Reconciled 2026-11-09 against the samples and docs written after this page. Still open:

- No accuracy number for optical flow drift was verified. Vendor pages give height accuracy
  only.
- AprilTag pose-accuracy papers (Kallwies and Forkel, ICRA 2020; an MDPI Sensors 2019 study)
  were located but not read (PDF / 403). AprilTag 2 (Wang and Olson, IROS 2016) is recorded as
  metadata only. A hub stand-in on rendered images exists since (synthetic, no lens distortion,
  so it does not verify those papers): a 0.16 m tag36h11 tag detected in >= 90 % of frames to 5 m
  frontal, position error p95 <= 0.091 m where detection holds, heading flips from 3 m
  ([fiducial-goal-apriltag](../../../samples/fiducial-goal-apriltag/README.md#results-ran-2026-11-09-synthetic)).
- Delmerico and Scaramuzza 2018 was read via author slides and a search summary only; the
  PDF did not parse.
- The FAST-LIO "<0.3 % on 32 m" figure comes from a search summary of the FAST-LIO paper, not
  from reading it.
- The Mid-360 community benchmark ground truth was the Pixhawk EKF fused with VICON, not raw
  mocap. Single author.
- `smfeval` numbers are from its README; the tool was not run. It is a LIO result on a
  handheld / ground dataset, not VIO on a drone.
- Lanegger 2026: only the abstract was read; the claim seen in a search summary that RoVIO
  3-sigma bounds miss the error was not checked.
- Whether EKF2 / EKF3 `reset_counter` handling behaves as read in code (see Verified since) was
  not tested in SITL or flight.
- PX4 precision landing "needs a valid global position" is quoted from the docs; whether a
  vision-only local position satisfies it was not tested.
- RTK and standalone GNSS accuracy figures are general knowledge, not re-verified here.
- No sensor or stack in this document was flown or run for this lane, except the hub-measured
  OpenVINS numbers from `samples/relative-nav-benchmark`. The arena's VIO-like estimator runs
  since are synthetic and do not change this.

### Verified since

- PX4 EKF2 does act on ODOMETRY `reset_counter` (code read at tag v1.17.0, not run): a changed
  counter sets `ev_reset` (`ev_control.cpp:52`), and with quality passing and no GNSS fused EKF2
  snaps its horizontal position to the new pose (`ev_pos_control.cpp:246`). ArduPilot EKF3 does
  the same through `posReset` at Copter-4.7.2. So the companion must hold `quality` low while it
  is lost and increment the counter only at a confirmed pose
  ([10 section 4](10-relocalization-prior-art.md#4-what-the-autopilots-do-with-reset_counter)).
