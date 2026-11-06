# Paper digests

<!-- about: concept:assured-pnt -->

There are 45 digests, one per paper or standard, written 2026-11-06. We picked them as the papers most likely to decide what a team builds in a GNSS-denied or contested-navigation hackathon. Each digest covers the problem, the method in a few lines, sensors and data, headline results quoted with their table or figure reference, limitations (the authors' own, plus ours, labelled), code and weights with license, a labelled reproduction-effort estimate, and what a team can reuse.

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

| Digest | Use when |
|---|---|
| [WildNav](wildnav-gnss-free-uav-localization-2022.md) | You want the simplest end-to-end nadir-frame-to-satellite-tile baseline. It reports 77 of 126 photos localized; note the SuperGlue license. |
| [AnyLoc](anyloc-universal-vpr-2023.md) | You need a coarse retrieval stage that works on aerial imagery without training (DINOv2 + VLAD). |
| [SALAD](salad-vpr-2023.md) | You want a stronger trained global descriptor for retrieval. It is GPL-3.0 and evaluated on street level only. |
| [HF-Net / hloc](hloc-coarse-to-fine-2018.md) | You are designing a retrieve-then-match hierarchy. The paper is HF-Net, and cvg/hloc is the later toolbox. |
| [Sample4Geo](sample4geo-2023.md) | You train a cross-view drone=>satellite retrieval model on University-1652 / SUES-200. It has no license. |
| [University-1652](university-1652-benchmark-2020.md) | You need the standard drone=>satellite retrieval benchmark. Its drone views are synthetic Google Earth renders. |
| [AnyVisLoc benchmark](anyvisloc-uav-localization-benchmark-2025.md) | You need realistic low-altitude oblique UAV localization numbers. With a satellite map instead of an aerial map, A@5m drops to 18.5. |
| [UAV-VisLoc](uav-visloc-dataset-2024.md) | You need real high-altitude UAV frames with satellite tiles. It is a dataset only, with no baselines or license. |
| [Couturier review](couturier-review-dl-uav-avl-2024.md) | You want a map of the absolute visual localization literature (abstract-only digest). |

## Thermal geo-localization and thermal odometry

| Digest | Use when |
|---|---|
| [STGL thermal geo-localization](thermal-geolocalization-iros-2023.md) | The scenario is night-time and you must match thermal frames to RGB satellite imagery. |
| [STHN](sthn-thermal-homography-2024.md) | You need a precise thermal-to-satellite alignment after coarse retrieval (learned homography). |
| [UASTHN](uasthn-uncertainty-thermal-2025.md) | You want a visual fix with an uncertainty you can gate on, or weight with, in the filter. |
| [ETIO](etio-thermal-inertial-odometry-2022.md) | You need relative odometry in darkness or smoke from a thermal camera + IMU. It is ROS1 and its data is unreleased. |

## Learned feature matching

| Digest | Use when |
|---|---|
| [LightGlue](lightglue-2023.md) | This is the default sparse fine matcher. It runs fast on GPU and has an adaptive depth; pair it with ALIKED or DISK for a clean license. |
| [LoFTR](loftr-2021.md) | The scenes are low-texture and sparse detectors starve. It is detector-free but slower. |
| [RoMa](roma-dense-matching-2023.md) | The appearance change is extreme (season, sensor). It is dense and robust but heavy; MIT. |
| [XFeat](xfeat-2024.md) | You are CPU-only or on a weak edge device and need a permissive lightweight extractor + matcher. |
| [MASt3R](mast3r-2024.md) | You want 3D-grounded matching for extreme viewpoints in research demos only (CC BY-NC-SA). |

## Visual, visual-inertial and LiDAR odometry

| Digest | Use when |
|---|---|
| [OpenVINS](openvins-2020.md) | You want a documented MSCKF VIO with online calibration and a simulator as the relative-nav backbone. |
| [MINS](mins-2023.md) | You fuse IMU with camera, LiDAR, wheel and GNSS in one filter. It treats GNSS as position only, so add your own outlier gate. |
| [VINS-Mono](vins-mono-qin-2017.md) | You want a monocular VIO with loop closure and a well-trodden path. |
| [ORB-SLAM3](orb-slam3-campos-2020.md) | You need a multi-map visual(-inertial) SLAM that survives tracking loss. It is GPL-3.0. |
| [cuVSLAM](cuvslam-2025.md) | You deploy on Jetson and want GPU stereo VIO. Its EuRoC accuracy is below ORB-SLAM3 (Table 2). |
| [FAST-LIO2](fast-lio2-xu-2021.md) | You have a LiDAR + IMU and need robust odometry fast. It is GPL-2.0 and needs livox_ros_driver to build. |
| [KISS-ICP](kiss-icp-vizzo-2022.md) | You need LiDAR odometry with almost no tuning. It is MIT and pip-installable. |
| [CFEAR radar odometry](cfear-radarodometry-adolfsson-2021.md) | Fog, dust or smoke rules out cameras and LiDAR, and you have a spinning radar. |

## Estimation foundations and learned inertial

| Digest | Use when |
|---|---|
| [Factor Graphs for Robot Perception](dellaert-kaess-factor-graphs-robot-perception.md) | You need to explain or design a factor-graph back end. |
| [iSAM2](kaess-isam2.md) | You need incremental smoothing in real time (the GTSAM ISAM2 class). |
| [IMU preintegration](forster-imu-preintegration.md) | You add an IMU to an optimization back end. It is the basis of GTSAM's ImuFactor. |
| [Sola ESKF notes](sola-quaternion-kinematics-eskf.md) | You write an error-state Kalman filter by hand and need correct Jacobians. |
| [TLIO](tlio-paper.md) | You do pedestrian or headset IMU-only dead reckoning with a learned displacement + EKF. No weights are released. |
| [AI-IMU](brossard-ai-imu-dr.md) | You do car IMU-only dead reckoning with learned noise adaptation. KITTI uses a tactical-grade IMU, so MEMS results will differ. |
| [AirIO](airio-paper.md) | You do drone IMU-only odometry. Its default inference uses ground-truth orientation, so check the setup. |

## Magnetic anomaly navigation

| Digest | Use when |
|---|---|
| [AFRL MagNav challenge](afrl-magnav-challenge-2020.md) | The problem involves airborne magnetometer data. It defines the compensation task and data, but reports no numbers. |
| [Canciani dissertation](canciani-afit-magnetic-anomaly-dissertation-2016.md) | You need the original map-matching framework for airborne MagNav (abstract-only digest). |
| [Q-CTRL quantum MagNav](qctrl-quantum-assured-magnav-2025.md) | You need a flight-trial reference point for what MagNav achieves. The method is closed, and some text and table figures disagree. |

## LEO signals of opportunity

| Digest | Use when |
|---|---|
| [Psiaki "TRANSIT on steroids"](psiaki-transit-on-steroids-2021.md) | You design LEO Doppler positioning and need the estimation math and achievable accuracy. |
| [Kassas: Starlink navigation](kassas-starlink-navigation.md) | You want a first look at opportunistic Starlink Doppler positioning results. |
| [Humphreys: Starlink signal structure](humphreys-2023-starlink-signal-structure.md) | You need the Starlink downlink OFDM parameters, or the MIT simulator, to build a receiver front end. |
| [Cold-start LEO Doppler (SDP)](leo-doppler-cold-start-2025.md) | You have no initial position. It is evaluated on Iridium data only, and one solve takes about 40 s. |

## GNSS spoofing detection and authentication

| Digest | Use when |
|---|---|
| [Humphreys 2008 spoofing threat](humphreys-2008-assessing-spoofing-threat.md) | You need the threat taxonomy (simplistic / intermediate / sophisticated) to scope a detector. |
| [Psiaki and Humphreys 2016](psiaki-humphreys-2016-gnss-spoofing-detection.md) | You choose which detection defenses to implement (the survey of methods). |
| [Kriezis ION ITM 2025](kreizis-ion-itm-2025-spoofing.md) | You build a detector on u-blox outputs and want to know which metrics actually fired in a real event. |
| [Rados 2024 review](rados-2024-jamming-spoofing-detection-review.md) | You want a recent catalogue of jamming and spoofing detectors, including ML. Its accuracies are not comparable across datasets. |
| [Galileo OSNMA](galileo-osnma.md) | You add cryptographic navigation-message authentication. It covers the TESLA chain, time-sync needs and the receiver steps. |

## Gaps (not digested, worth a next round)

- **Integrity monitoring.** The index has no RAIM / ARAIM or visual-integrity paper records yet, only repos (MAAST, a MATLAB RAIM) and talks.
- **Terrain-referenced navigation.** There is no English TERCOM / TRN paper record. Only repos and a Belarusian-language paper are indexed.
- **Gnadt MagNav compensation.** The AIAA SciTech 2022 paper is paywalled with no arXiv preprint. The challenge digest cites it inline.
- **Starlink results.** The blind Doppler and carrier-phase papers (`res:kassas-starlink-blind-doppler-2023`, `res:kassas-2022-starlink-carrier-phase`) are indexed but not digested.
- **Learned VO/SLAM.** DROID-SLAM, MASt3R-SLAM and DEVO are indexed but not digested.
