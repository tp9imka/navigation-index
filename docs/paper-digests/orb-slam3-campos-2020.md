# ORB-SLAM3 - paper digest
<!-- about: res:orb-slam3-campos-2020, repo:uz-slamlab/orb_slam3 -->
**ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial and Multi-Map SLAM** - Campos, Elvira, Gomez Rodriguez, Montiel, Tardos (Univ. Zaragoza), IEEE T-RO 2021 (DOI 10.1109/TRO.2021.3075644; arXiv 2020). [paper](https://arxiv.org/abs/2007.11898) | [code](https://github.com/UZ-SLAMLab/ORB_SLAM3) | Read: full text, ar5iv HTML (last ~7% of page text, mostly references, not read)

## Problem
One feature-based SLAM library covering monocular, stereo and RGB-D, pinhole and fisheye, with or without IMU, that survives tracking loss and reuses maps across sessions. The paper frames it as short-, mid- and long-term data association and claims the best accuracy of its time on EuRoC and TUM-VI.

## Method
- Visual-inertial SLAM with MAP estimation throughout, including IMU init: (1) 2 s vision-only SLAM at 4 Hz keyframes + BA, (2) inertial-only MAP for scale, gravity, biases, velocities, (3) joint visual-inertial refinement. Scale error ~5% after 2 s, ~1% after VI-BA at 5 s and 15 s (per text). Stereo-inertial fixes scale to 1.
- Atlas: one active map plus inactive maps sharing a DBoW2 database. On tracking loss: IMU-predicted short-term recovery (5 s window), then relocalize against all maps, else start a new map; maps are merged later when places are recognized.
- Visually lost threshold: fewer than 15 tracked map points (VI case).
- Improved-recall place recognition: geometric verification of the top-3 DBoW2 candidates instead of 3-keyframe temporal consistency; roll/pitch consistency check in VI mode; ~10 ms per keyframe.
- Map merging and loop closing via a welding window + local BA, then essential-graph optimization, then full BA in a separate thread.
- Abstract camera model: pinhole and Kannala-Brandt fisheye; MLPnP for relocalization; stereo handled without rectification.

## Data and sensors
- Camera (mono / stereo / RGB-D) + optional IMU.
- [EuRoC MAV](../dataset-cards/euroc-mav.md) (11 sequences, single and multi-session); [TUM-VI](../dataset-cards/tum-vi.md) (28 fisheye sequences; 1500 / 1000 ORB points, CLAHE, points beyond 20 m dropped outdoors). No RGB-D experiments in the paper.

## Headline results (as reported)
- Table II (EuRoC average RMS ATE, m): ORB-SLAM3 stereo-inertial 0.035 (scale err 0.6%), BASALT 0.051 (did not finish all), Kimera 0.119, VINS-Fusion 0.138; ORB-SLAM3 mono-inertial 0.043, VI-DSO 0.089, VINS-Mono 0.110, OKVIS 0.231, MSCKF 0.414.
- Table III (TUM-VI, RMS ATE m): room1 stereo-inertial 0.01; outdoors1 32.23 (stereo-inertial) vs VINS-Mono 74.96 and BASALT 255.04; outdoors2 10.42. Authors note outdoor errors of ~10-70 m on some long sequences.
- Table IV (TUM-VI rooms, avg RMS ATE m): mono 0.039, stereo 0.068, mono-inertial 0.011, stereo-inertial 0.009.
- Table V (multi-session EuRoC): stereo-inertial MH01-05 0.047 m; VINS-Mono 0.210 m on the same session set.
- Table VI (EuRoC V202, Intel i7-7700 3.6 GHz, 32 GB, CPU only): tracking 33.05 ms (stereo-IMU) / 23.22 ms (mono-IMU); local BA 152.70 / 121.09 ms. Text: realtime at 30-40 fps and 3-6 keyframes/s.
- Table VII: map merge 120-290 ms; loop full BA 1.1-4.1 s.

## Limitations
- Stated by authors: low-texture scenes are the main failure case; pure rotation blocks depth in mono-inertial exploration; slow motion or no roll/pitch excitation (car on flat ground) makes IMU init hard (use stereo); distant sky points outdoors (20 m cut is a hack); outdoor scale/bias drift gives 10-70 m errors; full BA after a loop can take seconds.
- Our read: TUM-VI outdoor numbers show it is not a long-range GNSS replacement on its own. Atlas multi-map is the strongest robustness feature but map merges only happen when a place is revisited. Upstream code activity is low.

## Code, weights, license
- [UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3), GPL-3.0 (GitHub API), last push 2024-07-24, not archived, ~9.2k stars.
- README: commercial closed-source license available from the authors; bundled modified DBoW2 and g2o are BSD. Tested on Ubuntu 16.04/18.04; ROS examples are ROS Melodic (optional).
- No learned weights; ORB vocabulary file ships with the repo.

## Reproduction effort (estimate)
Estimate:
- Hardware: desktop-class x86 CPU (README recommends i7-class for realtime).
- Data: EuRoC / TUM-VI sequences, a few GB each.
- Time-to-first-result: ~half a day; build against Pangolin, OpenCV, Eigen on a modern distro typically needs compiler/C++ standard fixes. Example scripts reproduce the EuRoC/TUM-VI runs.
- Not reproducible quickly: multi-session Table V requires chaining sequences; RGB-D claims have no paper numbers.

## What a hackathon team can take from it
- Atlas pattern: on tracking loss, start a new map instead of failing, then merge on revisit. The right behaviour for any visual nav component in a degraded environment.
- Strong EuRoC/TUM-VI baseline numbers to compare a custom VIO against (Table II, IV).
- Map save/reuse + relocalization gives "visual teach and repeat" localization without GNSS. See [integration card](../integration-cards/uz-slamlab__orb_slam3.md).
- Use stereo-inertial for ground vehicles per the authors' own init caveat.
- Compute budget in Table VI (and MINS Table 8, 328 ms total on KAIST urban38) argues for a lighter filter ([OpenVINS](openvins-2020.md)) on embedded boards.
