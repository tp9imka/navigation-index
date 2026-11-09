# Differentiators scan: what to bring besides satellite matching

<!-- about: res:cui-2026-ai-io-aerodynamics-inertial-odometry, res:ardupilot-copter-wind-estimation-docs, res:khaghani-skaloud-2018-vdm-navigation, res:leishman-2014-quadrotors-accelerometers, res:cioffi-2025-hdvio2-wind-disturbance, res:zhao-2025-tartan-imu-foundation-model, res:taylor-gross-2024-factor-graphs-navigation-tutorial, res:yang-2020-graduated-non-convexity -->

Scan date 2026-11-09, for EDGE hackathon Challenge 2 "Autonomous Frontiers" (details drop
2026-11-18). The brief asks for an innovative navigation algorithm and lists propulsion,
GNC, applied maths and applied physics among the expertise. Camera-to-satellite matching is a
commodity ([trends 2025-2026](landscape/trends-2025-2026.md) section 2), and the
[playbook differentiators](hackathon-playbook.md#11-differentiators-judges-have-not-seen)
already cover integrity, honest uncertainty, link loss and drop-in integration. This scan
looks for an algorithmic core that is new to judges and is not one of those.

Scope: navigation of the vehicle's own flight only.

Records added: `data/repos/nav-differentiators.json` (24 repos, each checked with
`gh api repos/...` on 2026-11-09) and `data/resources/nav-differentiators.json` (21
resources). Catalog pages for the new ids appear after the next `tools/build.py` run.

## 1. Ranked candidates

Score = novelty to judges + 48h buildability + open data + commercial license + fit with
existing samples, each 1-5, total out of 25. "Reported" means the number is quoted from the
source's abstract or README and was not reproduced here.

| # | Candidate | Why novel | 48h build path | Open code | Data | License | Risk | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | **Propulsion and drag as a virtual velocity sensor** (multirotor rotor-drag model, fixed-wing airspeed/aero model, wind as an explicit error state) | Hits the "propulsion / applied physics" wording head-on. No camera, no map, no RF. Judges see VIO and map matching; almost nobody demos the airframe itself as the sensor. Khaghani and Skaloud report one to two orders of magnitude better accuracy over 3-min GNSS outages on a real fixed-wing ([paper](../catalog/resources/khaghani-skaloud-2018-vdm-navigation.md), reported). | ArduCopter 4.6.3 SITL already models rotor momentum and bluff-body drag, and EKF3 already fuses drag (see 2.1). Measure GNSS-off holdover with and without it, then replay the same filter offline on real rotor-speed data. | ArduPilot EKF3 drag fusion, PX4 EKF2 drag fusion (`EKF2_DRAG_CTRL`), [AI-IO](../catalog/repos/sjtu-visys-team__ai-io.md), [pyulog](../catalog/repos/px4__pyulog.md) | [AI-IO dataset](../catalog/repos/sjtu-visys-team__ai-io.md) 363 MB; [NeuroBEM](../catalog/resources/neurobem-dataset.md) 657 MB processed + 455 MB raw, 1 h 15 min, 400 Hz motor speeds; [VID-Dataset](../catalog/repos/zju-fast-lab__vid-dataset.md) (size not verified); fixed-wing: [ALFA](../catalog/resources/keipour-2021-alfa-dataset.md) 272 MB processed / 541 MB Dataflash | ArduPilot GPL-3.0 (we only configure it); our own filter code is ours; AI-IO MIT; ALFA CC BY 4.0 / CC0; NeuroBEM no license stated | Wind is unobservable without an absolute fix, so the drag sensor bounds air-relative velocity, not position. SITL drag and EKF drag share one model => optimistic; real-data replay is required. | **22** |
| 2 | **Learned inertial odometry with rotor speed, fused as an EKF velocity update and cross-checked against the physics model** | Learned IO is 2025-2026 research (AirIO RA-L 2025, Tartan IMU CVPR 2025, AI-IO ICRA 2026), not a vendor product. AI-IO reports rotor speed improves velocity prediction by 36.9% ([paper](../catalog/resources/cui-2026-ai-io-aerodynamics-inertial-odometry.md), reported). Pairing it with candidate 1 gives two correlated velocity estimates and a disagreement check. | Run AI-IO's released checkpoint on its dataset, export velocity + covariance, feed the same EKF as candidate 1, gate both with the existing velocity-consistency test. | [AI-IO](../catalog/repos/sjtu-visys-team__ai-io.md) (MIT), [AirIO](../catalog/repos/air-io__air-io.md) (BSD-3), [TartanIMU](../catalog/repos/superxslam__tartanimu.md) (Apache-2.0), [PyPose](../catalog/repos/pypose__pypose.md) (Apache-2.0) | AI-IO 363 MB; AirIO's Blackbird split 17 MB release asset (the official Blackbird host timed out on 2026-11-06, [card](dataset-cards/blackbird.md)) | Permissive end to end for AI-IO / AirIO / TartanIMU code; weights and dataset terms follow the repo but are not separately stated | Indoor mocap data only, so the outdoor/wind generalisation gap is unknown. Training compute not measured. Out-of-distribution failure is silent unless cross-checked. | **20** |
| 3 | Fixed-wing aerodynamic model (VDM) with wind re-estimated from sparse absolute fixes | The hub's own [golden-demo-fixedwing](../samples/golden-demo-fixedwing/) measured the problem: airspeed + compass dead reckoning drifted about 1 m/s because EKF3 froze the wind at GNSS loss (844 m cross-track at the last waypoint after 20.8 km in the fast-detection run). A model-aided filter that re-learns wind at each TRN or visual fix attacks exactly that. | Treat as the fixed-wing branch of candidate 1 (see 2.1, step 5). Full VDM (aero coefficients as process model) is a stretch: no open VDM navigation code was found. | [Skywalker X8 model](../catalog/repos/krisgry__x8.md) (no license), [JSBSim](../catalog/repos/jsbsim-team__jsbsim.md) (LGPL-2.1) | ALFA (above); [IGN Flight 8](../catalog/resources/skaloud-2021-ign-flight8-fixed-wing-data.md) 5.9 GB CC BY 4.0, airspeed/motor logging not stated | Coefficients for our airframe unknown until the brief drops. [Ye et al. 2023](../catalog/resources/ye-2023-semi-aerodynamic-model-aided-iekf.md) report max error within 30 m over 130 s denial, but code was promised, not found. | 17 |
| 4 | Plug-and-play factor graph with robust kernels (GTSAM iSAM2 + graduated non-convexity, ASPN message types) | Speaks the DARPA ASPN / pntOS vocabulary; sensors add and drop at runtime; GNC is reported robust to 70-80% outliers ([paper](../catalog/resources/yang-2020-graduated-non-convexity.md), reported). | Wrap candidates 1-2 as factors in GTSAM (pip), name inputs after [ASPN-ICD](../catalog/repos/open-pnt__aspn-icd.md) types, show a source dropping out and coming back. | [GTSAM](../catalog/repos/borglab__gtsam.md) (BSD), [SymForce](../catalog/repos/symforce-org__symforce.md) (Apache-2.0), [libRSF](../catalog/repos/tuc-proaut__librsf.md) (GPL-3.0), [tutorial code](../catalog/repos/cntaylor__factorgraph2dsatelliteexample.md) | Any of the above | GTSAM BSD; ASPN-ICD CC-BY-4.0 | "Fusion architecture" alone reads as plumbing to judges. Best as the wrapper, not the headline. Hub already has strong integrity samples. | 17 |
| 5 | Radar-inertial odometry (mmWave) for night / smoke / featureless terrain | Weather- and light-independent velocity. | Replay [ekf-rio](../catalog/repos/christopherdoer__rio.md) on its drone datasets. | christopherdoer/rio | Doer's datasets (size not checked) | GPL-3.0 | Needs a radar on the vehicle; GPL; hub already indexes several RIO repos. | 13 |
| 6 | Thermal-inertial odometry for night | Night flight is where commodity VPS fails. | [ROVTIO](../catalog/repos/ntnu-arl__rovtio.md) replay; hub already has [thermal-geolocalization](../samples/thermal-geolocalization/). | ntnu-arl/rovtio | NTNU datasets (not checked) | Custom (NOASSERTION), not checked | ROS1 build; overlaps the existing thermal sample. | 13 |
| 7 | Event-inertial odometry | High dynamic range, fast motion. | [DEIO](../catalog/repos/arclab-hku__deio.md) on public event sets. | DEIO (MIT), [ESVO](../catalog/repos/hkust-aerial-robotics__esvo.md) | Public event benchmarks (VECtor etc.) | MIT | GPU, no event camera on a typical rig, no aerial night number checked. | 12 |
| 8 | LEO signals of opportunity (Starlink Doppler, Iridium) from the air | Strong 2025-2026 research momentum ([Kassas 2025](../catalog/resources/kozhaya-saroufim-kassas-2025-unveiling-starlink-pnt.md), [cold-start Doppler 2025](../catalog/resources/leo-doppler-cold-start-2025.md)). | Offline on recorded IQ only. | [starlink-leo-pnt](../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md), [gr-iridium](../catalog/repos/muccc__gr-iridium.md) (GPL-3.0) | Needs SDR recordings; hub trends doc already says "needs SDR hardware plus recorded data" | Mixed GPL | Hardware and data are the blocker, not the algorithm. | 10 |

Lower priority, one line each:

- Polarization / skylight compass: heading without magnetometer; hub has [PVI dataset](../catalog/repos/ts-fupeng__pvi-dataset.md) and [OpenSky simulator](../catalog/resources/opensky-sky-polarization-simulator-2024.md). Heading only, needs sky.
- Magnetic anomaly / quantum MagNav: real progress ([Q-CTRL 2025](../catalog/resources/qctrl-quantum-assured-magnav-2025.md), vendor-reported) and a hub sample ([magnav-quickstart](../samples/magnav-quickstart/)); sensors out of reach, already covered.
- Airflow sensing on multirotors: [Wang et al. 2025](../catalog/resources/wang-2025-airflow-inertial-odometry-anemometers.md) report 5.7 m drift over 203 s, indoors and wind-free. Needs custom anemometers.
- IMU foundation model: [TartanIMU](../catalog/resources/zhao-2025-tartan-imu-foundation-model.md) reports 36% ATE improvement over specialized models; an IROS 2026 Kaggle challenge is linked from its README (page not reachable from here, unverified). Fold into candidate 2 if AI-IO underperforms.
- Vision-based wind / airspeed estimation: no credible open code found in this pass.

## 2. Top 2 deep dive

The two are designed to share one filter and one metric, so the team builds one pipeline and
gets both stories.

### 2.1 Propulsion and drag as a virtual velocity sensor

**Idea.** On a multirotor in steady flight the horizontal accelerometer does not see gravity
tilt; it sees rotor and body drag, which is a function of air-relative velocity
([Leishman et al. 2014](../catalog/resources/leishman-2014-quadrotors-accelerometers.md),
[Abeywardena et al. 2013](../catalog/resources/abeywardena-2013-drift-free-velocity-estimator.md)).
So the IMU plus a two-parameter drag model gives a drift-free body-frame air velocity. Position
error then grows with wind-estimate error times time, instead of with integrated accelerometer
bias. On a fixed-wing the airspeed sensor plays the same role, and the dominant error is again
wind ([golden-demo-fixedwing](../samples/golden-demo-fixedwing/): ~1.1 m/s wind vector
error => ~800 m drift over ~20 km). Rotor speed (ESC telemetry) refines the model: the momentum
drag term scales with thrust.

**What already exists, checked in source.** ArduPilot `Copter-4.6.3`
`libraries/AP_NavEKF3/AP_NavEKF3_AirDataFusion.cpp` fuses body-frame drag
(`FuseDragForces`, bluff-body term from `EK3_DRAG_BCOEF_X/Y`, momentum term from
`EK3_DRAG_MCOEF`). `AP_NavEKF3_Control.cpp` at the same tag counts `dragUsed` as velocity
aiding and sets `doingWindRelNav` while drag has not timed out, which raises the
`dead_reckoning` status flag. `windStateIsObservable` stays false without a position or
velocity source, so wind is frozen at GNSS loss, the same mechanism the fixed-wing sample hit.
The 4.6.3 SITL multicopter frame (`libraries/SITL/SIM_Frame.cpp`) models momentum and
bluff-body drag and prints "Suggested EK3_DRAG_BCOEF_* ... EK3_DRAG_MCOEF" at start-up. PX4
has the equivalent (`EKF2_DRAG_CTRL`, `EKF2_BCOEF_X/Y`, `EKF2_MCOEF`, tuning script
`mc_wind_estimator_tuning.py`) per the [EKF2 guide](../catalog/resources/px4-ekf2-tuning-guide.md).
Not checked: whether ArduCopter's flight-mode checks accept a drag-only dead-reckoning EKF for
Loiter/Auto, and whether PX4 SIH models drag. That is the hour-1 go/no-go.

**48h build plan.**

1. Hours 0-3, go/no-go in SITL. Use [sitl-docker](../samples/sitl-docker/) ArduCopter 4.6.3
   and the [golden-demo](../samples/golden-demo/) flight script. Copy the SITL-suggested drag
   values into a `drag.parm`, cut GNSS, fly a 1-2 km survey leg with SITL wind on (0, 3, 6 m/s).
   If the start-up line does not print, the frame has no drag model and SITL numbers are
   meaningless: go straight to step 3.
2. Hours 3-10, SITL measurement. Three arms on the same seeds: GNSS-off with no aiding,
   GNSS-off with drag fusion, GNSS-off with drag fusion plus wind re-learned from one sparse
   absolute fix per N km (reuse the fix models in [golden-demo-fixedwing](../samples/golden-demo-fixedwing/)
   and the TRN fixes in [blind-flight-bench](../samples/blind-flight-bench/)). Score with the
   [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/) `drift.py` analyzer (time from GNSS
   loss to N m error).
3. Hours 10-24, real data offline. Extend the stdlib EKF in
   [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/) with a body-frame drag measurement
   `a_xy = -k_m * omega_sum * v_air_xy - (rho / 2B) * |v_air| v_air_xy` and a random-walk wind
   state. Fit `k_m`, `B` on half the [AI-IO dataset](../catalog/repos/sjtu-visys-team__ai-io.md)
   sequences (rotor speed + IMU + truth), test on the rest, simulate GNSS loss by dropping truth
   updates. Cross-check on [NeuroBEM](../catalog/resources/neurobem-dataset.md) `raw_data`
   (its processed accelerations are Vicon-fused, so they would leak truth).
4. Hours 24-36, integrity. Feed the drag velocity into the existing velocity-consistency
   monitor (`ss_fde.VelocityConsistency` in [golden-demo](../samples/golden-demo/)) so a
   spoofed GNSS that disagrees with the airframe physics is rejected.
5. Fixed-wing branch, only if the brief is fixed-wing: rerun the `dr` scenario of
   [golden-demo-fixedwing](../samples/golden-demo-fixedwing/) with wind re-estimated from each
   sparse fix instead of frozen at the switch; real-data check on [ALFA](../catalog/resources/keipour-2021-alfa-dataset.md)
   Dataflash logs (airspeed channel presence not yet checked).
6. Hours 36-48, demo and slides. Map: truth, no-aid, drag-aided tracks diverging after GNSS cut.

**The one number.** Seconds (multirotor) or km (fixed-wing) from GNSS loss until horizontal
error exceeds 50 m, drag-aided vs unaided, at 0 / 3 / 6 m/s wind. Report the wind sweep, not
only still air: still-air data (all three multirotor datasets are indoor mocap) flatters this
method.

**Pitch line.** "No camera, no map, no radio: we turned the propellers into a velocity sensor,
and it costs zero grams."

### 2.2 Learned inertial odometry with rotor speed, checked by physics

**Idea.** A network that sees IMU windows plus rotor speed regresses body velocity with an
uncertainty; an EKF fuses it as a velocity update. AI-IO reports rotor speed improves velocity
prediction by 36.9% and its transformer adds 22.4%
([paper](../catalog/resources/cui-2026-ai-io-aerodynamics-inertial-odometry.md), reported).
Related open work: [DIDO](../catalog/resources/zhang-2022-dido-quadrotor-dynamical-odometry.md),
[IMO](../catalog/resources/cioffi-2023-imo-learned-inertial-odometry-racing.md) (thrust input,
GPL-3.0), [AirIO](../catalog/repos/air-io__air-io.md), [TartanIMU](../catalog/repos/superxslam__tartanimu.md),
[HDVIO2.0](../catalog/resources/cioffi-2025-hdvio2-wind-disturbance.md) (wind estimation, AGPL/GPL).
The differentiator is not the network; it is running it next to the physics model of 2.1 and
flagging when they disagree, because a learned model fails silently outside its training data.

**48h build plan.**

1. Hours 0-6. Clone AI-IO (MIT), download the 363 MB dataset and the released checkpoint
   (`checkpoint_open.pt`, 0.9 MB), run evaluation as in its README. Record the IMU-only vs
   IMU+rotor velocity error ourselves before quoting anything.
2. Hours 6-14. Export per-step velocity + covariance to the replay contract in
   [recording-replay](../samples/recording-replay/); fuse it in the same EKF as 2.1 step 3.
3. Hours 14-24. Run the two velocity sources (physics drag, learned) through
   `VelocityConsistency`; measure false-alarm rate on clean sequences and detection on
   sequences with an injected rotor-speed fault or a payload change.
4. Hours 24-36, stretch. Fine-tune [TartanIMU](../catalog/repos/superxslam__tartanimu.md) or
   AirIO on the AI-IO data as a second learned source if AI-IO underperforms.
5. Hours 36-48. Same map and holdover plot as 2.1, plus a "learned model disagrees => fall back
   to physics" moment on screen.

**The one number.** Same as 2.1: time from GNSS loss to 50 m horizontal error, for physics
only, learned only, and both fused; plus false alarms per hour of the cross-check on clean data.

**Pitch line.** "Physics and learning provide complementary checks; shared inputs can still make both wrong."

## 3. What to check before building (unverified items)

- ArduCopter mode checks with a drag-only dead-reckoning EKF (2.1 hour-1 go/no-go).
- PX4 SIH drag modelling: not checked; the multirotor path assumes ArduPilot SITL.
- AI-IO dataset and checkpoint terms: they sit in an MIT repo, no separate data license stated.
- NeuroBEM and DIDO data: no license stated. Evaluation use only until the authors confirm.
- VID-Dataset total size and NAS availability.
- ALFA: airspeed channel presence; KiltHub metadata (CC BY 4.0) and bundled README (CC0) differ, both permissive.
- TartanIMU Hugging Face weights license and the IROS 2026 Kaggle page.
- All numbers marked "reported" are from abstracts or READMEs, not reproduced here.

## Follow-up: tested hypotheses

The [innovation laboratory](innovation-experiments.md) tests a narrow selective-calibration mechanism and two planning/scheduling hypotheses. The physics/learning cross-check proposed above is not independent redundancy: shared IMU, rotor data, calibration and environmental assumptions can cause common failures. A physics model is not automatically certifiable, and a learned model is not categorically uncertifiable. No certification or common-mode integrity claim was validated here.
