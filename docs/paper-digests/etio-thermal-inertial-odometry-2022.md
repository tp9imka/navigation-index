# ETIO - paper digest
<!-- about: res:etio-thermal-inertial-odometry-2022, repo:hitsz-nrsl/etio -->
**Edge-based Monocular Thermal-Inertial Odometry in Visually Degraded Environments** - Wang, Chen, Liu, Zhang (HIT Shenzhen, USTC), IEEE RA-L 2023 (arXiv 2022). [paper](https://arxiv.org/abs/2210.10033) | [code](https://github.com/HITSZ-NRSL/ETIO) | Read: full text, arXiv HTML v2 (22 Oct 2022) and the v2 PDF (Table II); repo README

## Problem
Visual-inertial odometry fails in darkness, glare and obscurants (smoke, dust, fog). Thermal cameras see through these but give noisy, low-contrast, texture-poor images, and flat-field correction (FFC/NUC) shutter events interrupt the stream and change image appearance. Corner trackers struggle on such images.

## Method
- Front end: extract edges from thermal images (Difference of Gaussians, gradient threshold, sub-pixel refinement => binary edge image).
- DT-KLT: track features on the distance transform of the edge image rather than raw intensity, with pyramids - robust to intensity changes between frames.
- ADT-KLT: adaptive switch between plain KLT and DT-KLT using a score combining change in edge count and IMU-preintegrated rotation angle. Threshold value not given in the text.
- Back end: VINS-style sliding-window MAP optimization (IMU preintegration + reprojection on the unit sphere + marginalization prior, Huber loss, Ceres). Inverse-depth point features.
- No explicit FFC/NUC compensation step described; edges are the robustness mechanism.

## Data and sensors
- Sensors: monocular thermal (own rig: Gobi+ 640, 640x480 @ 50 Hz) + IMU (MTi-G-710 @ 200 Hz). Ground truth from VLP-16 lidar + NovAtel GNSS.
- Public data: Khattak et al. thermal datasets (Tau2 thermal, VN-100 IMU, DJI M100) - Urban Parking Lot and Active Gold Mine; GT from FAST-LIO2. Card: [thermal datasets](../dataset-cards/thermal-datasets.md).
- Own data: four outdoor sequences of about 200 m (day, dusk, two night), plus a dark smoke-filled room (no GT; accumulated drift used).
- Metric: ATE RMSE (m).
- Note: this is a ground/handheld-scale evaluation; nothing here is flown at UAV altitudes over open terrain except the public M100 sequences.

## Headline results (as reported)
- Table II, public datasets, ATE RMSE (m), VINS-Mono / PL-VINS / ROTIO / ETIO with KLT / DT-KLT / ADT-KLT: Urban Parking Lot 4.892 / 3.594 / 2.934 / 2.136 / 1.049 / 0.648; Active Gold Mine 5.982 / 1.895 / 0.993 / 1.191 / 0.472 / 0.409. ORB-SLAM3 fails on both. The PDF table lines up: the best values 0.648 / 0.409 are full ETIO (ADT-KLT). ETIO with plain KLT is worse than ROTIO on Active Gold Mine.
- Table III, own outdoor sequences, ATE RMSE (m), VINS-Mono / PL-VINS / ROTIO / ETIO: Seq01 day 3.301 / 4.101 / fail / 2.170; Seq02 dusk 6.263 / 9.338 / 41.330 / 1.224; Seq03 night 4.296 / 2.636 / 18.058 / 1.966; Seq04 night 2.166 / 2.286 / 8.880 / 1.403.
- Table IV, smoke room, accumulated drift (m): Seq01 (73.2 m path) ROTIO 1.035 vs ETIO 0.211; Seq02 (54.3 m) ROTIO 0.746 vs ETIO 0.080. VINS-Mono and PL-VINS fail on both.
- Runtime: Intel NUC i7-10710U, CPU only, "about 25 Hz" max output (Sec. V); per-module timings only in Fig. 8.

## Limitations
- Stated by authors: no limitations section. DT-KLT assumes a stable distance field, which breaks under aggressive rotation or abrupt illumination change; solar heating saturated thermal images outdoors (ROTIO failed there); smoke-room results have no reference trajectory.
- Our read: errors of 1-2 m over about 200 m are around 1% of distance - good for a thermal VIO, but still drift. It needs an absolute fix (thermal map matching, see STHN/UASTHN) for long missions.
- Our read: small evaluation (2 public + 4 own sequences + 2 indoor), all short. No aerial-altitude sequences of its own.

## Code, weights, license
- Repo HITSZ-NRSL/ETIO: README states GPLv3, but GitHub API reports no license (no LICENSE file detected). Treat as GPLv3 per README; copyleft matters if you link it into a product.
- Classical method, no learned weights.
- Last push 2026-01-17; 12 stars; README is minimal (dependencies: OpenCV 4, PCL 1.10, Ceres 1.14; ROS1 catkin). Launch files: `mytool.launch`, `tau2.launch`.
- Their own outdoor and smoke-room sequences: not linked in the README; only the Khattak et al. datasets (autonomousrobotslab.com/ktio.html).

## Reproduction effort (estimate)
Estimate:
- Hardware: x86 Linux with ROS1 (Noetic or older); CPU only. Ceres 1.14 and PCL 1.10 suggest Ubuntu 20.04 - a Docker image is the sane path on anything newer.
- Data: download the KTIO bags from autonomousrobotslab.com (size not checked).
- Time to first result: half a day to a day to build (old ROS1/Ceres stack, thin README) and play a bag through `tau2.launch`. Score with [evo](../integration-cards/michaelgrupp__evo.md) against FAST-LIO2 GT you would have to generate yourself.
- Not reproducible: Tables III and IV (own data not released as far as we found).

## What a hackathon team can take from it
- Distance-transform KLT on edge images: a drop-in front-end trick for any VIO on thermal or low-texture imagery (smoke, night). Port it into [OpenVINS](../integration-cards/rpng__open_vins.md) or VINS-style trackers rather than adopting ETIO's ROS1 stack.
- Adaptive switching using IMU rotation as a signal of when appearance tracking will fail - a cheap, reusable gating idea.
- Role in a GNSS-denied stack: the relative-motion layer at night. Pair with a thermal absolute fix ([STHN](sthn-thermal-homography-2024.md) / [UASTHN](uasthn-uncertainty-thermal-2025.md)) to bound drift.
- Evaluation protocol for no-GT environments: closed-loop accumulated drift (start = end), as in Table IV - easy to run in a hackathon venue.
