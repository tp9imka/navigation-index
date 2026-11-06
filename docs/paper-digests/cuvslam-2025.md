# cuVSLAM - paper digest
<!-- about: res:cuvslam-2025, repo:nvidia-isaac/cuvslam -->
**cuVSLAM: CUDA accelerated visual odometry and mapping** - Korovko, Slepichev, Efitorov et al. (NVIDIA), arXiv technical report 2025. [paper](https://arxiv.org/abs/2506.04359) | [code](https://github.com/nvidia-isaac/cuVSLAM) | Read: full text incl. appendices, arXiv HTML v3

## Problem
Robots need real-time pose on low-power edge GPUs, with whatever camera rig they carry (1 to many cameras, optional IMU or depth). Most open VSLAM systems target one sensor configuration and use the CPU. cuVSLAM is NVIDIA's CUDA-accelerated VO/SLAM library, used in Isaac ROS.

## Method
- Classical feature-based pipeline, not learned. Frontend for low-latency local pose, asynchronous backend for loop closure and pose graph optimization (Sec. 2).
- 2D module: Shi-Tomasi "Good Features to Track" on an NxM grid for uniform coverage, pyramidal Lucas-Kanade tracking with an NCC check per step, keyframe when tracked count drops below a threshold (Sec. 2.1).
- Stereo (default): track left camera, PnP against local-map landmarks, left-to-right tracking + triangulation on keyframes, async CUDA sparse bundle adjustment (Schur complement).
- Multi-camera (up to 32 cameras): a Frustum Intersection Graph auto-detects overlapping camera pairs from extrinsics; all observations go into one pose solve. Requires hardware-synchronized cameras.
- Visual-inertial: 15-DoF state (pose, velocity, accel and gyro bias) with IMU preintegration factors, gravity estimation from an initial visual-only window, VI bundle adjustment (after Forster et al. and ORB-SLAM3).
- RGB-D: dense photometric + depth factors (after Kerl et al.) plus point-to-point factors, Levenberg-Marquardt on GPU. Mono: fundamental-matrix init, up to scale.
- Backend: keyframe poses + landmarks + 9x9 multi-level patches; loop candidates by kd-tree radius search over poses, landmark re-tracking, then PGO.

## Data and sensors
Mono, stereo, multi-stereo, stereo + IMU, RGB-D. Evaluated on [EuRoC](../dataset-cards/euroc-mav.md), [KITTI](../dataset-cards/kitti.md), [TUM-VI](../dataset-cards/tum-vi.md) Room, TUM RGB-D, ICL-NUIM, AR-table, [TartanAir](../dataset-cards/tartanair.md) V2, TartanGround, and a proprietary 4-stereo wheeled-robot set (R2B, Nova Carter). Live tests with RealSense D435/D455 and Hawk cameras.

## Headline results (as reported)
- Table 1, track call time per frame (768x480): Stereo 0.4 ms desktop (RTX 4090) / 1.8 ms Jetson AGX Orin 64GB; Stereo-Inertial 1.3 / 3.8 ms; Mono 0.9 / 2.7 ms; Mono-Depth (640x480) 5.9 / 15.1 ms; 3-stereo 1.4 / 2.3 ms. Live Orin net load for Stereo: CPU 5.5%, GPU 1.7%.
- Table 2, KITTI stereo: cuVSLAM SLAM avgRTE 0.27%, avgRE 0.93 deg, APE 1.98 m; ORB-SLAM3 0.31% / 1.20 deg / 2.98 m. Fig. 10, KITTI leaderboard-style segments 00-10: 0.85% translation, 0.0025 deg/m.
- Table 2, EuRoC stereo: cuVSLAM SLAM APE 0.054 m (odometry 0.13 m); ORB-SLAM3 0.068 m. EuRoC stereo-inertial: cuVSLAM SLAM APE 0.13 m vs ORB-SLAM3 0.066 m.
- Table 3, multi-stereo: R2B real robot SLAM avgRTE 0.11%, APE 0.18 m; TartanAir V2 Hard SLAM avgRTE 2.26%, avgRE 12.76 deg, APE 4.99 m.
- Sec. 4.2: on R2B, SLAM improves accuracy metrics by about 40% over odometry only, attributed to more loop closures with 4 stereo pairs.
- Appendix A.2: Mono-Depth at 720p on Orin AGX averages 37.7 ms per call, over the 33.3 ms budget at 30 FPS, about half the frames skipped. On Orin Nano Super (25 W), Mono-Depth at 30 FPS was only stable at 424x240 (31 ms call time, about 30% frames dropped with acquisition overhead).

## Limitations
- Stated by authors: Table 2 uses scale-corrected trajectories, so "translation results may not be meaningful for some datasets" and rotation error is the primary metric. TartanAir V2 Hard shows "room for improvement". Multi-camera mode needs hardware sync; no suitable public real multi-camera dataset, so real-world multi-stereo validation is on their own proprietary data. For UAVs and handheld, they recommend 60 FPS with RealSense.
- Our read: the abstract claims EuRoC position errors under 5 cm, but Table 2 shows 0.054 m for stereo SLAM and 0.13 m for stereo odometry, so check which row a claim refers to. Stereo-inertial does not beat ORB-SLAM3 on EuRoC APE (0.13 vs 0.066 m). The ORB-SLAM3 EuRoC stereo-inertial avgRE of 72.23 deg looks like a failed run, not a fair baseline. No comparison with OpenVINS, VINS-Fusion or Kimera, and no aerial-altitude dataset (EuRoC is indoor MAV). Pure geometric front-end: expect the usual failures on low texture, water, and fast rotation without IMU.

## Code, weights, license
- At paper time the library shipped as binaries via Isaac ROS and NVlabs/PyCuVSLAM. Today's repo nvidia-isaac/cuVSLAM contains source (C++/CUDA, Python bindings), release v17.0.1 (2026-10-13), last push 2026-11-05, very active.
- License: NVIDIA Community License (GitHub API reports NOASSERTION). Commercial use and derivatives allowed, but only "solely on systems with NVIDIA GPUs or CPUs" (LICENSE section 2). Not usable on non-NVIDIA hardware.
- No learned weights in the core tracker. Optional visual place recognition (current README, not in paper) runs AnyLoc (DINOv2 + VLAD) via a TensorRT engine built from `models/anyloc`; DINOv2 terms then apply.
- The newer README modes (`Multisensor`, place recognition, `LocalizeInMap`) postdate the paper.

## Reproduction effort (estimate)
Estimate: 1-2 h to a first trajectory on an x86 CUDA box or Jetson Orin with prebuilt wheels and EuRoC MH_01, then score with [evo](../integration-cards/michaelgrupp__evo.md). Reproducing Table 2 rows on public sets is a day. Not reproducible: R2B results (proprietary dataset). The exact paper-era version is not pinned in the paper; numbers from v17 may differ.

## What a hackathon team can take from it
- Fastest path to GPU stereo or stereo-inertial VO on a Jetson: about 2 ms per stereo frame on Orin (Table 1), leaving the GPU free for a learned matcher doing map-relative fixes. See [cuVSLAM card](../integration-cards/nvidia-isaac__cuvslam.md).
- Architecture to copy: smooth odometry frontend separate from loop-closure backend, so GNSS-denied relative pose never jumps; fuse absolute visual fixes (LightGlue/RoMa vs map tiles) in your own filter rather than inside SLAM.
- Multi-camera occlusion resilience (Sec. 4.1): with at least one stereo pair unobstructed, tracking held through 20-60 s occlusions. Useful if the vehicle can carry 2+ synced stereo pairs.
- Budget rule from Appendix A.2: check per-call time against the frame interval at your resolution; on Orin Nano, prefer stereo modes over Mono-Depth.
- Baselines to compare in the same harness: [ORB-SLAM3](../integration-cards/uz-slamlab__orb_slam3.md), [OpenVINS](../integration-cards/rpng__open_vins.md).
