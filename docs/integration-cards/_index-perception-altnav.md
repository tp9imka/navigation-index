# Integration cards - perception, visual geo-localization, odometry, alt-nav

<!-- about: repo:cvg/lightglue, repo:cvg/hierarchical-localization, repo:parskatt/roma, repo:verlab/accelerated_features, repo:fabio-sim/lightglue-onnx, repo:gmberton/vismatch, repo:anyloc/anyloc, repo:gmberton/vpr-methods-evaluation, repo:tiers/wildnav, repo:arplaboratory/satellite-thermal-geo-localization, repo:nvidia-isaac/cuvslam, repo:rpng/open_vins, repo:uz-slamlab/orb_slam3, repo:hku-mars/fast_lio, repo:prbonn/kiss-icp, repo:introlab/rtabmap, repo:michaelgrupp/evo, repo:mit-ai-accelerator/magnav.jl, repo:esa/tetra3, repo:mzahana/tercom_nav, repo:alti3/python-tercom, repo:dusty-nv/jetson-inference, repo:luxonis/depthai -->

What each card gives you in a hackathon. All 23 were written from READMEs, source files, LICENSE files and issues read through the GitHub API. None of these repos was installed or run for the cards, and every snippet is marked "not run". Throughput and resolution figures appear only where a source states them.

Read the license row before you pick a model. Code license and weights license often differ, and several defaults here are non-commercial.

## Feature matching (fine registration)

- [LightGlue](cvg__lightglue.md) - Sparse learned matcher in a few lines of PyTorch. Its default extractor is SuperPoint, whose weights are non-commercial, so use ALIKED or DISK for clean licensing.
- [hloc](cvg__hierarchical-localization.md) - Retrieval => matching => PnP against a COLMAP model, with HDF5 handoffs between stages. The `superpoint_*` and `superglue` configs pull in non-commercial Magic Leap code.
- [RoMa](parskatt__roma.md) - Dense matcher that holds up across season, lighting and sensor changes. Slow and CUDA-oriented, so use it as a verifier. The indoor weights are trained on ScanNet, which is non-commercial.
- [XFeat](verlab__accelerated_features.md) - Small detector/descriptor plus LighterGlue that runs in real time on a laptop CPU. Apache-2.0, weights included. The no-GPU option.
- [LightGlue-ONNX](fabio-sim__lightglue-onnx.md) - Exports extractor plus LightGlue to one ONNX graph for ONNX Runtime (CPU, CUDA, TensorRT, OpenVINO) or plain TensorRT. The Jetson deploy path. Use `raco_aliked` rather than the SuperPoint default.
- [vismatch](gmberton__vismatch.md) - One `get_matcher(name)` API over 82 matchers for a quick shoot-out. Licenses are mixed: MASt3R is CC BY-NC-SA, and EfficientLoFTR needs registration for organizational use. It calls Hugging Face on every `get_matcher`.

## Visual place recognition and map-relative geo-localization

- [AnyLoc](anyloc__anyloc.md) - Training-free DINOv2 + VLAD global descriptors with an aerial vocabulary, for coarse tile retrieval. Hardcoded to CUDA, and the vocabulary license is not stated.
- [VPR-methods-evaluation](gmberton__vpr-methods-evaluation.md) - One CLI that scores about 20 pretrained VPR models on your own query and database folders, with recall@k and prediction images. SALAD is GPL-3.0 and MixVPR has no license.
- [WildNav](tiers__wildnav.md) - Roughly 300 lines that match nadir drone frames to georeferenced satellite tiles and output lat/lon. It depends on SuperPoint+SuperGlue, which is non-commercial.
- [Satellite-thermal geo-localization](arplaboratory__satellite-thermal-geo-localization.md) - Thermal query => satellite RGB retrieval, plus a generator that makes synthetic thermal images from satellite RGB. Weights come from Hugging Face, and their license is not stated.

## Visual, visual-inertial and LiDAR odometry / SLAM

- [cuVSLAM](nvidia-isaac__cuvslam.md) - GPU stereo/stereo-inertial/RGB-D VO and SLAM driven from Python, with map save and relocalization. The NVIDIA Community License limits use to NVIDIA hardware, and wheels are tied to specific Python versions.
- [OpenVINS](rpng__open_vins.md) - CPU MSCKF VIO with online calibration and a built-in simulator, so you get trajectories before hardware arrives. GPL-3.0.
- [ORB-SLAM3](uz-slamlab__orb_slam3.md) - CPU feature-based SLAM for mono/stereo/RGB-D, with or without IMU. The baseline for visual drift. GPL-3.0. The ROS build script points at a directory that no longer exists.
- [FAST-LIO](hku-mars__fast_lio.md) - Tightly coupled LiDAR-inertial odometry on CPU, including ARM. GPL-2.0. Needs the Livox driver even for Velodyne or Ouster.
- [KISS-ICP](prbonn__kiss-icp.md) - LiDAR-only odometry from `pip install` on a rosbag, MCAP or KITTI folder, with almost no parameters. MIT.
- [RTAB-Map](introlab__rtabmap.md) - Graph SLAM with appearance loop closure, localization-only mode and Nav2 grids. The code is BSD, but default builds pull in TORO (CC-BY-NC-SA) and GPL components.
- [evo](michaelgrupp__evo.md) - Aligned APE/RPE metrics and plots for any trajectory against ground truth. The scoring tool for everything above. GPL-3.0.

## Non-visual alt-nav (magnetic, celestial, terrain)

- [MagNav.jl](mit-ai-accelerator__magnav.jl.md) - Aircraft magnetic compensation plus a map-matching EKF on real SGL flight data. The code is public domain with MIT-style terms. The AFRL data agreement allows only non-profit research, education or US-government use.
- [tetra3](esa__tetra3.md) - Lost-in-space star-field plate solve to RA/Dec/roll in pure Python. Breaks on NumPy 2 (issue #37). The ESA repo is dormant, and cedar-solve is the maintained fork.
- [tercom_nav](mzahana__tercom_nav.md) - ROS 2 Humble terrain matching from baro, a rangefinder and IMU against a GeoTIFF DEM, fused in an ESKF, runnable with PX4 SITL. No LICENSE file. package.xml declares Apache-2.0.
- [python-tercom](alti3__python-tercom.md) - Two-file NumPy TERCOM demo with GPGGA output, for a slide or notebook. No license, so all rights reserved.

## Edge perception hardware / runtimes

- [jetson-inference](dusty-nv__jetson-inference.md) - TensorRT detection, segmentation and mono-depth on Jetson camera streams from Python or C++. The code is MIT, but the pretrained weights come from Box links with no license stated.
- [DepthAI](luxonis__depthai.md) - OAK camera stereo depth, on-device detection, IMU and v3 VIO over USB/PoE. The real code lives in `luxonis/depthai-core`. The default `yolov6-nano` example model is GPL-3.0 upstream.
