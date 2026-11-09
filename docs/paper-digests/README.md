# Paper digests

<!-- about: concept:assured-pnt -->

Use this when you are about to build on a published method and need its real results, limits, code and license before you commit. For the close-area A=>B task (likely on Day 1) the useful rows are the VIO ones (OpenVINS, VINS-Mono, ORB-SLAM3, cuVSLAM); planners and safety filters are not digested here, they are in [close-area-nav](../research/close-area-nav/README.md) docs 01, 04, 05 and 07.

There are 46 digests, one per paper or standard, written 2026-11-06. We picked them as the papers most likely to decide what a team builds in a GNSS-denied or contested-navigation hackathon. Each digest covers the problem, the method in a few lines, sensors and data, headline results quoted with their table or figure reference, limitations (the authors' own, plus ours, labelled), code and weights with license, a labelled reproduction-effort estimate, and what a team can reuse.

**How they were read.** Each digest's header line says what was actually read: full text (arXiv HTML, ar5iv, author PDF), or abstract only. Two are abstract-only:
- [Couturier review](couturier-review-dl-uav-avl-2024.md): the MDPI site blocked automated fetch.
- [Canciani dissertation](canciani-afit-magnetic-anomaly-dissertation-2016.md): the AFIT and DTIC copies returned 403.

No code was run for any digest. Every number is the authors' own, and anything not found in the text is marked "not located". Reproduction efforts are estimates.

**Licenses at a glance.** Many "open" pipelines pull in non-commercial pieces:
- SuperPoint and SuperGlue weights are Magic Leap non-commercial. They are the default in LightGlue, hloc and WildNav.
- MASt3R code and checkpoints are CC BY-NC-SA, plus training-data terms.
- cuVSLAM is free only on NVIDIA hardware.
- TLIO data is CC BY-NC.
- Sample4Geo and UAV-VisLoc have no license at all.

Permissive picks:
- LightGlue with ALIKED or DISK
- XFeat
- RoMa
- KISS-ICP
- AnyLoc
- GTSAM

Each digest states its exact terms.

## Visual geo-localization (UAV frame => satellite / map)

| Page | Use it when | You get |
|---|---|---|
| [WildNav](wildnav-gnss-free-uav-localization-2022.md) | you want the simplest end-to-end nadir-frame-to-satellite-tile baseline | 77 of 126 photos localized (authors' number); SuperGlue license caveat |
| [AnyLoc](anyloc-universal-vpr-2023.md) | you need a coarse retrieval stage that works on aerial imagery without training | DINOv2 + VLAD universal place recognition |
| [SALAD](salad-vpr-2023.md) | you want a stronger trained global descriptor for retrieval | GPL-3.0; evaluated on street level only |
| [HF-Net / hloc](hloc-coarse-to-fine-2018.md) | you are designing a retrieve-then-match hierarchy | The HF-Net paper; cvg/hloc is the later toolbox |
| [Sample4Geo](sample4geo-2023.md) | you train a cross-view drone=>satellite retrieval model on University-1652 / SUES-200 | Training recipe; no license |
| [University-1652](university-1652-benchmark-2020.md) | you need the standard drone=>satellite retrieval benchmark | Benchmark whose drone views are synthetic Google Earth renders |
| [AnyVisLoc benchmark](anyvisloc-uav-localization-benchmark-2025.md) | you need realistic low-altitude oblique UAV localization numbers | With a satellite map instead of an aerial map, A@5m drops to 18.5 |
| [UAV-VisLoc](uav-visloc-dataset-2024.md) | you need real high-altitude UAV frames with satellite tiles | A dataset only, with no baselines or license |
| [Couturier review](couturier-review-dl-uav-avl-2024.md) | you want a map of the absolute visual localization literature | Review (abstract-only digest) |

## Thermal geo-localization and thermal odometry

| Page | Use it when | You get |
|---|---|---|
| [STGL thermal geo-localization](thermal-geolocalization-iros-2023.md) | the scenario is night-time and you must match thermal frames to RGB satellite imagery | Thermal-to-satellite retrieval method |
| [STHN](sthn-thermal-homography-2024.md) | you need a precise thermal-to-satellite alignment after coarse retrieval | Learned homography |
| [UASTHN](uasthn-uncertainty-thermal-2025.md) | you want a visual fix with an uncertainty you can gate on, or weight with, in the filter | Uncertainty-aware thermal homography |
| [ETIO](etio-thermal-inertial-odometry-2022.md) | you need relative odometry in darkness or smoke from a thermal camera + IMU | ROS1 method; its data is unreleased |

## Learned feature matching

| Page | Use it when | You get |
|---|---|---|
| [LightGlue](lightglue-2023.md) | you need the default sparse fine matcher | Fast on GPU, adaptive depth; pair it with ALIKED or DISK for a clean license |
| [LoFTR](loftr-2021.md) | the scenes are low-texture and sparse detectors starve | Detector-free matching, slower |
| [RoMa](roma-dense-matching-2023.md) | the appearance change is extreme (season, sensor) | Dense, robust, heavy; MIT |
| [XFeat](xfeat-2024.md) | you are CPU-only or on a weak edge device | Permissive lightweight extractor + matcher |
| [MASt3R](mast3r-2024.md) | you want 3D-grounded matching for extreme viewpoints in research demos only | CC BY-NC-SA code and checkpoints |

## Visual, visual-inertial and LiDAR odometry

| Page | Use it when | You get |
|---|---|---|
| [OpenVINS](openvins-2020.md) | you want a documented MSCKF VIO as the relative-nav backbone (indoor close-area drones too) | Online calibration and a simulator |
| [MINS](mins-2023.md) | you fuse IMU with camera, LiDAR, wheel and GNSS in one filter | GNSS treated as position only, so add your own outlier gate |
| [VINS-Mono](vins-mono-qin-2017.md) | you want a monocular VIO with loop closure and a well-trodden path | Monocular VIO + loop closure |
| [ORB-SLAM3](orb-slam3-campos-2020.md) | you need a multi-map visual(-inertial) SLAM that survives tracking loss | Multi-map SLAM; GPL-3.0 |
| [cuVSLAM](cuvslam-2025.md) | you deploy on Jetson and want GPU stereo VIO | EuRoC accuracy below ORB-SLAM3 (Table 2) |
| [FAST-LIO2](fast-lio2-xu-2021.md) | you have a LiDAR + IMU and need robust odometry fast | GPL-2.0; needs livox_ros_driver to build |
| [KISS-ICP](kiss-icp-vizzo-2022.md) | you need LiDAR odometry with almost no tuning | MIT, pip-installable |
| [CFEAR radar odometry](cfear-radarodometry-adolfsson-2021.md) | fog, dust or smoke rules out cameras and LiDAR, and you have a spinning radar | Radar odometry method |

## Estimation foundations and learned inertial

| Page | Use it when | You get |
|---|---|---|
| [Factor Graphs for Robot Perception](dellaert-kaess-factor-graphs-robot-perception.md) | you need to explain or design a factor-graph back end | Factor-graph foundations |
| [iSAM2](kaess-isam2.md) | you need incremental smoothing in real time | The method behind the GTSAM ISAM2 class |
| [IMU preintegration](forster-imu-preintegration.md) | you add an IMU to an optimization back end | The basis of GTSAM's ImuFactor |
| [Sola ESKF notes](sola-quaternion-kinematics-eskf.md) | you write an error-state Kalman filter by hand | Correct Jacobians |
| [TLIO](tlio-paper.md) | you do pedestrian or headset IMU-only dead reckoning | Learned displacement + EKF; no weights released |
| [AI-IMU](brossard-ai-imu-dr.md) | you do car IMU-only dead reckoning | Learned noise adaptation; KITTI uses a tactical-grade IMU, so MEMS results will differ |
| [AirIO](airio-paper.md) | you do drone IMU-only odometry | Default inference uses ground-truth orientation, so check the setup |

## Terrain-referenced navigation

| Page | Use it when | You get |
|---|---|---|
| [CTU SPRIN-D heightmap gradients](ctu-sprind-terrain-nav.md) | you fly kilometres low and without GNSS with a LiDAR and a prior elevation map | Winning SPRIN-D system: LiDAR heightmap gradients vs a prior map in a particle filter, on CPU; localization RMSE below 11 m on its real competition flights (authors' text); no code. Re-implemented in [samples/terrain-heightmap-pf](../../samples/terrain-heightmap-pf/README.md) |

## Magnetic anomaly navigation

| Page | Use it when | You get |
|---|---|---|
| [AFRL MagNav challenge](afrl-magnav-challenge-2020.md) | the problem involves airborne magnetometer data | The compensation task and data definition, no numbers |
| [Canciani dissertation](canciani-afit-magnetic-anomaly-dissertation-2016.md) | you need the original map-matching framework for airborne MagNav | Framework (abstract-only digest) |
| [Q-CTRL quantum MagNav](qctrl-quantum-assured-magnav-2025.md) | you need a flight-trial reference point for what MagNav achieves | Closed method; some text and table figures disagree |

## LEO signals of opportunity

| Page | Use it when | You get |
|---|---|---|
| [Psiaki "TRANSIT on steroids"](psiaki-transit-on-steroids-2021.md) | you design LEO Doppler positioning | Estimation math and achievable accuracy |
| [Kassas: Starlink navigation](kassas-starlink-navigation.md) | you want a first look at opportunistic Starlink Doppler positioning | Results overview |
| [Humphreys: Starlink signal structure](humphreys-2023-starlink-signal-structure.md) | you build a Starlink receiver front end | Downlink OFDM parameters and the MIT simulator |
| [Cold-start LEO Doppler (SDP)](leo-doppler-cold-start-2025.md) | you have no initial position | Evaluated on Iridium data only; one solve takes about 40 s |

## GNSS spoofing detection and authentication

| Page | Use it when | You get |
|---|---|---|
| [Humphreys 2008 spoofing threat](humphreys-2008-assessing-spoofing-threat.md) | you scope a spoofing detector | Threat taxonomy: simplistic / intermediate / sophisticated |
| [Psiaki and Humphreys 2016](psiaki-humphreys-2016-gnss-spoofing-detection.md) | you choose which detection defenses to implement | Survey of methods |
| [Kriezis ION ITM 2025](kreizis-ion-itm-2025-spoofing.md) | you build a detector on u-blox outputs | Which metrics actually fired in a real event |
| [Rados 2024 review](rados-2024-jamming-spoofing-detection-review.md) | you want a recent catalogue of jamming and spoofing detectors, including ML | Catalogue; its accuracies are not comparable across datasets |
| [Galileo OSNMA](galileo-osnma.md) | you add cryptographic navigation-message authentication | TESLA chain, time-sync needs and the receiver steps |

## Gaps (not digested, worth a next round)

- **Integrity monitoring.** The index has no RAIM / ARAIM or visual-integrity paper records yet, only repos (MAAST, a MATLAB RAIM) and talks.
- **Terrain-referenced navigation.** The [CTU SPRIN-D](ctu-sprind-terrain-nav.md) heightmap-gradient paper is digested. The classic TRN papers are indexed but not digested (`res:golden-1980-tercom`, `res:hostetler-andreas-1983-sitan`, `res:park-bang-2025-contours-seeking-pf-trn`).
- **Gnadt MagNav compensation.** The AIAA SciTech 2022 paper is paywalled with no arXiv preprint. The challenge digest cites it inline.
- **Starlink results.** The blind Doppler and carrier-phase papers (`res:kassas-starlink-blind-doppler-2023`, `res:kassas-2022-starlink-carrier-phase`) are indexed but not digested.
- **Learned VO/SLAM.** DROID-SLAM, MASt3R-SLAM and DEVO are indexed but not digested.
