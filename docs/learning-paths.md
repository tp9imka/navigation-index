# Learning paths

Three study tracks built from the courses, talks, books and docs in this index. Pick one
by how much time you have before the hackathon.

**About the times.** A time marked **(source)** is stated by the resource itself or by its
index record. Every other time is a **planning estimate** - our budget for the slice you
need, not the length of the full course. Adjust to your pace.

Background chapters live in the [navigation primer](primer/README.md). Read
[export control and ethics](export-control-and-ethics.md) before any work with RF,
flight or defense end uses, whichever track you pick.

## Track 1: one-day crash course (the day before)

Goal: every teammate can explain GNSS failure modes, a Kalman filter and the
dead-reckon-plus-fix pattern, and has run one tool. Split the team by role after the
morning block.

### Morning, everyone (about 4 hours, planning estimate)

| # | Resource | Time | Why |
|---|----------|------|-----|
| 1 | [How to fool a GPS (TEDx, Humphreys)](../catalog/resources/ted-humphreys-how-to-fool-a-gps.md) | short talk | The threat in plain words |
| 2 | [ION Online Tutorial: Basics of Satellite Navigation](../catalog/resources/ion-online-tutorial-basics-satnav.md) | 45 min | Pseudoranges, clocks, error sources |
| 3 | [SKYbrary: GNSS jamming and spoofing](../catalog/resources/skybrary-gnss-jamming-spoofing.md) | 20 min | What interference does to real systems |
| 4 | [Understanding Sensor Fusion and Tracking (MATLAB Tech Talks)](../catalog/resources/mathworks-understanding-sensor-fusion-tracking.md) | 10-15 min per video **(source)**; watch the intro and GPS+IMU episodes | Fusion intuition |
| 5 | [Udacity AI for Robotics](../catalog/resources/udacity-ai-for-robotics-cs373.md), particle filter lesson | 1 hour **(source)** | The estimator behind most map matching |
| 6 | [Primer chapter 1](primer/01-pnt-fundamentals.md) | 30 min | Frames, integrity, assured PNT vocabulary |

### Afternoon, by role (about 4 hours, planning estimate)

- **Estimation lead:** [Kalman and Bayesian Filters in Python](../catalog/resources/labbe-kalman-bayesian-filters-python.md),
  chapters on the multivariate KF and EKF; then the [GTSAM tutorial](../catalog/resources/gtsam-intro-tutorial.md)
  ("best first hour with GTSAM" per its record). Run [`samples/gnss-ins-ekf-outage`](../samples/gnss-ins-ekf-outage/).
- **GNSS / EW lead:** [ION webinar: jamming and spoofing on Android](../catalog/resources/ion-webinar-akos.md)
  (hour-long ION webinar format **(source)**), the [Android raw GNSS guide](../catalog/resources/android-raw-gnss-developer-guide.md),
  then log a few minutes with GnssLogger and load it in
  [gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md).
- **Vision lead:** [Scaramuzza VO tutorial, Part I](../catalog/resources/scaramuzza-vo-tutorial.md), then run
  [LightGlue](../catalog/repos/cvg__lightglue.md) on one drone frame and one satellite tile
  ([`samples/visual-geolocalization-lightglue`](../samples/visual-geolocalization-lightglue/)).
- **Vehicle / integration lead:** [PX4 simulation docs](../catalog/resources/px4-simulation-docs.md)
  or [ArduPilot SITL](../catalog/resources/ardupilot-sitl-docs.md) to a flying SITL vehicle, then
  [ArduPilot Non-GPS navigation](../catalog/resources/ardupilot-non-gps-navigation-docs.md).
- **SA / C2 lead:** [CoT developer guide](../catalog/resources/butler-cot-developer-guide.md) and
  [PyTAK docs](../catalog/resources/pytak-docs.md); run [`samples/mavlink-to-tak-cot`](../samples/mavlink-to-tak-cot/).
- **Pitch lead:** [NIST IR 8323r1](../catalog/resources/nist-ir-8323r1-pnt-profile.md) summary,
  [DHS conformance framework](../catalog/resources/dhs-resilient-pnt-conformance-framework.md), and
  [NATO DIANA challenge statements](../catalog/resources/nato-diana-10-challenges-2025.md) for vocabulary.

**Done when:** each role has one tool running on sample data and can state the main
failure mode of their component.

## Track 2: one week

Goal: build a small end-to-end GNSS-denied navigation demo yourself before the event.
About 2 to 3 hours per day (planning estimate).

| Day | Theme | Resources | Hands-on |
|-----|-------|-----------|----------|
| 1 | GNSS | [Stanford GPS MOOC](../catalog/resources/stanford-gps-mooc-van-diggelen-enge.md) (selected lectures), [Navipedia](../catalog/resources/navipedia.md), [primer ch. 2](primer/02-gnss-and-threats.md) | Least-squares SPP on a RINEX or Android log ([georinex](../catalog/repos/geospace-code__georinex.md), [gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md)) |
| 2 | Filtering | [Labbe](../catalog/resources/labbe-kalman-bayesian-filters-python.md) KF/EKF/UKF chapters, [kalmanfilter.net](../catalog/resources/kalmanfilter-net-tutorial.md), [Stachniss Mobile Robotics online training](../catalog/resources/stachniss-mobile-robotics-online-training.md) (Bayes filter, EKF, particle filter blocks) | Write a 2D EKF from scratch with [FilterPy](../catalog/repos/rlabbe__filterpy.md) as reference |
| 3 | INS and GNSS/INS | [Sola, quaternion kinematics for the ESKF](../catalog/resources/sola-quaternion-kinematics-eskf.md), [Kalibr IMU noise model](../catalog/resources/kalibr-imu-noise-model-wiki.md), [primer ch. 3](primer/03-inertial-and-fusion.md) | Run [KF-GINS](../catalog/repos/i2nav-whu__kf-gins.md), mask GNSS, plot drift |
| 4 | Interference | [White paper: protecting GNSS](../catalog/resources/protecting-gnss-intentional-interference-arxiv.md), [ION webinar Rothmaier](../catalog/resources/ion-webinar-rothmaier.md), [ION webinar Hendeby](../catalog/resources/ion-webinar-hendeby.md) (hour-long format **(source)**) | Detector on [TEXBAT](../catalog/resources/ut-texbat.md) or GPS-SDR-SIM **files** through [GNSS-SDR](../catalog/repos/gnss-sdr__gnss-sdr.md); or ADS-B NIC/NACp map from [readsb](../catalog/repos/wiedehopf__readsb.md) |
| 5 | Visual odometry | [Scaramuzza VO tutorial I and II](../catalog/resources/scaramuzza-vo-tutorial.md), [VIN concise review](../catalog/resources/huang-vins-concise-review-2019.md) | [OpenVINS](../catalog/repos/rpng__open_vins.md) simulator or [EuRoC](../catalog/resources/ethz-euroc-mav-dataset.md); score with [evo](../catalog/repos/michaelgrupp__evo.md) |
| 6 | Absolute alt-PNT | [Couturier review](../catalog/resources/couturier-review-dl-uav-avl-2024.md), [WildNav paper](../catalog/resources/wildnav-gnss-free-uav-localization-2022.md), [MagNav.jl docs](../catalog/resources/magnav-jl-docs.md), [primer ch. 5](primer/05-absolute-alt-pnt.md) | [`samples/terrain-relative-nav-pf`](../samples/terrain-relative-nav-pf/) or [WildNav](../catalog/repos/tiers__wildnav.md) on a few frames |
| 7 | Integration | [PX4 EKF2 guide](../catalog/resources/px4-ekf2-tuning-guide.md) or [ArduPilot GPS/non-GPS transitions](../catalog/resources/ardupilot-gps-non-gps-transitions.md), [MAVLink common messages](../catalog/resources/mavlink-common-messages.md) | Feed your day-5 or day-6 output into SITL over MAVLink ([`samples/vio-to-mavlink-bridge`](../samples/vio-to-mavlink-bridge/)); run the outage test from [primer ch. 9](primer/09-evaluation-and-datasets.md) |

**Done when:** you have a plot of position error vs time through a GNSS outage, with and
without your extra source.

## Track 3: one month, deep

Goal: real understanding of estimation, GNSS receivers and one perception modality, enough
to contribute to the open projects in this index. About 8 to 10 hours per week (planning
estimate). Each week picks a slice of a longer course; the full courses are much longer.

### Week 1: estimation foundations

- [Chalmers Sensor Fusion and Non-linear Filtering (edX)](../catalog/resources/chalmers-sensor-fusion-nonlinear-filtering.md) - self-paced; do the KF, EKF/UKF and particle filter modules with assignments.
- [Coursera State Estimation and Localization for Self-Driving Cars](../catalog/resources/coursera-state-estimation-localization-sdc.md) - the final ES-EKF fusing IMU, GNSS and LiDAR is a ready template.
- [micro Lie theory](../catalog/resources/sola-micro-lie-theory.md) with [manif](../catalog/repos/artivis__manif.md).
- Reference: [Barfoot, State Estimation for Robotics](../catalog/resources/barfoot-state-estimation-robotics-2e.md) chapters on nonlinear estimation and matrix Lie groups.

### Week 2: GNSS in depth

- [ESA GNSS Data Processing Vol. I](../catalog/resources/esa-gnss-data-processing-vol1.md) with [Vol. II labs](../catalog/resources/esa-gnss-data-processing-vol2.md) - SPP through PPP on real RINEX.
- [Borre, Software-Defined GPS and Galileo Receiver](../catalog/resources/borre-software-defined-gps-galileo-receiver.md) with [SoftGNSS](../catalog/repos/tmboc__softgnss.md) - acquisition and tracking loops.
- [GNSS-SDR tutorials](../catalog/resources/gnss-sdr-tutorials.md); then [OSNMA receiver guidelines](../catalog/resources/galileo-osnma-receiver-guidelines.md) with [OSNMAlib](../catalog/repos/algafix__osnma.md).
- [Psiaki and Humphreys, GNSS spoofing and detection](../catalog/resources/psiaki-humphreys-2016-gnss-spoofing-detection.md).
- Optional paid: [ION GNSS+ tutorials](../catalog/resources/ion-gnss-plus-tutorials.md), half-day courses **(source)**.

### Week 3: one perception modality

Choose one:

- **Vision:** [Vision Algorithms for Mobile Robotics (UZH/ETH)](../catalog/resources/scaramuzza-vision-algorithms-mobile-robotics.md) exercises to a mini VO pipeline; [14 Lectures on Visual SLAM](../catalog/resources/gaoxiang-14-lectures-visual-slam.md); [OpenVINS docs](../catalog/resources/openvins-docs.md).
- **SLAM / LiDAR:** [Robot Mapping course](../catalog/resources/stachniss-slam-course-2013.md) (full semester recording **(source)**; take the graph-SLAM lectures) with [exercises](../catalog/resources/freiburg-robot-mapping-course.md) (described as a template for a 1-day SLAM crash course **(source)**); [LiDAR odometry survey](../catalog/resources/lee-lidar-odometry-survey-2023.md); run [KISS-ICP](../catalog/repos/prbonn__kiss-icp.md) and [FAST-LIO](../catalog/repos/hku-mars__fast_lio.md).
- **Aerial image-to-map:** [Photogrammetry I and II](../catalog/resources/stachniss-photogrammetry-i-ii.md) (two-semester course **(source)**; take camera models, orientation and bundle adjustment); [hloc paper](../catalog/resources/hloc-coarse-to-fine-2018.md); [CVPR image matching workshop](../catalog/resources/cvpr-image-matching-workshop.md).
- **Quadrotor navigation end to end:** [MIT 16.485 VNAV](../catalog/resources/mit-vnav-16485.md) labs.

### Week 4: factor graphs, alt-PNT and the defense context

- [Factor Graphs for Robot Perception](../catalog/resources/dellaert-kaess-factor-graphs-robot-perception.md), [iSAM2](../catalog/resources/kaess-isam2.md), [IMU preintegration](../catalog/resources/forster-imu-preintegration.md); build a GTSAM graph with IMU, VO and intermittent absolute fixes.
- [ROSCon UK 2025 state estimation workshop](../catalog/resources/nav2-roscon-uk-2025-state-estimation-workshop.md) - filter vs smoother with runnable exercises.
- Alt-PNT talks (hour-long ION webinar format **(source)**): [Kassas GRASP seminar](../catalog/resources/kassas-ad-astra-leo-grasp-2024.md), [Unveiling Starlink for PNT](../catalog/resources/ion-webinar-kozhaya.md), [Vision-based terrain-aided localization](../catalog/resources/ion-webinar-navon.md), [Quantum sensors for navigation](../catalog/resources/ion-webinar-kealy.md), [Resilience monitoring for all-source navigation](../catalog/resources/ion-webinar-gipson.md).
- Current research snapshot: [Stanford PNT Symposium 2025](../catalog/resources/stanford-pnt-symposium-2025.md) talk recordings.
- Defense context: [GAO-21-320SP](../catalog/resources/gao-21-320sp-gps-alternatives.md), [RUSI Meatgrinder](../catalog/resources/rusi-meatgrinder-2023.md), [Jammertest](../catalog/resources/jammertest-norway.md) test catalogue.
- Reference shelf: [Groves](../catalog/resources/groves-pnt-book-2e.md), [SLAM Handbook](../catalog/resources/slam-handbook.md).

**Done when:** you can derive and implement an ESKF, explain a receiver's tracking loops,
and have one contribution-sized change or benchmark result on an indexed repo.

## Podcasts and background listening

For commutes, not for study time: [From the Crows' Nest, Dana Goward](../catalog/resources/crows-nest-goward-gps-threats-podcast.md),
[PolicyTracker GNSS vulnerabilities](../catalog/resources/policytracker-gnss-vulnerabilities-podcast.md),
[39C3 Baltic jammer talk](../catalog/resources/39c3-baltic-jammer-r-mode.md).
