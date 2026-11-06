# Feature detection and matching

`concept:feature-matching`

Keypoints/descriptors and learned matchers (SIFT, SuperPoint, LightGlue, LoFTR).

## Repositories (26)

- [LightGlue](../repos/cvg__lightglue.md) - fit: high - Fast learned local feature matcher (ICCV 2023) that adapts its depth to pair difficulty; works with SuperPoint, DISK, ALIKED and SIFT features.
- [hloc](../repos/cvg__hierarchical-localization.md) - fit: high - Toolbox for hierarchical visual localization: global retrieval (NetVLAD etc.) to find candidate images, then local feature matching (SuperPoint, LightGlue...) and PnP against an SfM model.
- [XFeat](../repos/verlab__accelerated_features.md) - fit: high - Lightweight local feature extractor and matcher (CVPR 2024) designed for speed on constrained hardware.
- [RoMa](../repos/parskatt__roma.md) - fit: high - Robust dense feature matcher (CVPR 2024) estimating pixel-dense warps with certainties, strong under large appearance change.
- [small_gicp](../repos/koide3__small_gicp.md) - fit: high - Efficient, parallel point-cloud registration library (GICP, ICP variants) with C++ and Python APIs.
- [vismatch (image-matching-models)](../repos/gmberton__vismatch.md) - fit: high - Wrapper exposing 50+ image matching models behind one interface (formerly image-matching-models).
- [WildNav](../repos/tiers__wildnav.md) - fit: high - Python pipeline that localizes a drone by matching its downward camera frames against georeferenced satellite map tiles with SuperGlue, then converts the best match into GPS coordinates.
- [AnyVisLoc benchmark](../repos/uav-avl__benchmark.md) - fit: high - Benchmark and code for UAV absolute visual localization under low-altitude, multi-view (oblique) observation, comparing retrieval and matching combinations against aerial and satellite reference maps.
- [visual_localization (GNSS-free UAV)](../repos/terbouchehacene__visual_localization.md) - fit: high - A cleaner reimplementation of the WildNav idea: match UAV images to satellite tiles with SuperPoint/SuperGlue-style matchers and estimate geographic position.
- [UAVLocalization (map retrieval + alignment)](../repos/hmf21__uavlocalization.md) - fit: high - Geo-localization system for aerial platforms that first retrieves the right satellite map region with a deep descriptor and then aligns the drone orthophoto to it to extract coordinates; evaluated on reorganized public A
- [VGGT](../repos/facebookresearch__vggt.md) - fit: medium - Visual Geometry Grounded Transformer: a feed-forward network predicting camera poses, depth and point maps from one or many images (CVPR 2025 best paper).
- [SuperGlue (pretrained)](../repos/magicleap__supergluepretrainednetwork.md) - fit: medium - Pretrained SuperGlue graph-neural-network matcher with SuperPoint features (CVPR 2020).
- [MASt3R-SLAM](../repos/rmurai0610__mast3r-slam.md) - fit: medium - Real-time dense monocular SLAM built on the MASt3R two-view 3D reconstruction prior, needing no fixed camera model (CVPR 2025).
- [MASt3R](../repos/naver__mast3r.md) - fit: medium - Matching grounded in 3D: predicts dense correspondences and 3D pointmaps from image pairs, building on DUSt3R.
- [LoFTR](../repos/zju3dv__loftr.md) - fit: medium - Detector-free transformer matcher producing dense-ish correspondences, good on low-texture scenes.
- [TEASER++](../repos/mit-spark__teaser-plusplus.md) - fit: medium - Certifiable, outlier-robust point-cloud registration library with C++, Python and MATLAB bindings.
- [SuperPoint (pretrained)](../repos/magicleap__superpointpretrainednetwork.md) - fit: medium - Pretrained SuperPoint keypoint detector and descriptor.
- [fast_gicp](../repos/koide3__fast_gicp.md) - fit: medium - Collection of fast GICP and VGICP point-cloud registration implementations, multithreaded and CUDA.
- [AirSLAM](../repos/sair-lab__airslam.md) - fit: medium - Point-and-line visual(-inertial) SLAM using learned features, designed for illumination-robust operation, with TensorRT acceleration; successor to AirVO.
- [vision_landing](../repos/goodrobots__vision_landing.md) - fit: medium - Precision landing using visual fiducial targets, sending LANDING_TARGET messages to ArduPilot.
- [Aerial Template Matching](../repos/m-hamza-mughal__aerial-template-matching.md) - fit: medium - Classical template-matching approach for locating an aerial image inside a larger reference image, built on OpenCV.
- [STHN](../repos/arplaboratory__sthn.md) - fit: medium - Deep homography estimation for aligning UAV thermal images to satellite maps (RA-L 2024), refining coarse geo-localization into precise alignment.
- [UAVision](../repos/arborisers__uavision.md) - fit: medium - Map-matching-based visual localization software for UAVs in GNSS-denied settings, shipped with a GUI front end and demo.
- [Visual Locator](../repos/rtwotwo__visual-locator.md) - fit: medium - Absolute drone positioning by image retrieval (SelaVPR-style ViT features) over cropped satellite tiles followed by registration with SIFT+RANSAC or SuperPoint+SuperGlue.
- [Glue Factory](../repos/cvg__glue-factory.md) - fit: low - Training library for local feature detection and matching (trains LightGlue and others).
- [Quatro](../repos/url-kaist__quatro.md) - fit: low - Fast, robust global registration for terrestrial robots that assumes near-planar motion to cut degrees of freedom.

## Documents, talks, courses, datasets (16)

- [14 Lectures on Visual SLAM: From Theory to Practice](../resources/gaoxiang-14-lectures-visual-slam.md) - book - English translation of the popular Chinese visual SLAM textbook, from rigid-body motion and Lie algebra through camera models, nonlinear optimization, feature/direct VO, backend optimization, loop closure and dense mappi
- [Cyrill Stachniss YouTube channel (incl. '5 Minutes with Cyrill')](../resources/stachniss-youtube-channel.md) - video - Channel hosting Stachniss's full lecture courses plus the '5 Minutes with Cyrill' series of short explainers on single concepts (Kalman filter, factor graphs, ICP, RANSAC, SIFT, occupancy grids).
- [Exploring the best way for UAV visual localization under Low-altitude Multi-view Observation Condition: a Benchmark](../resources/anyvisloc-uav-localization-benchmark-2025.md) - paper - Builds a benchmark for low-altitude, oblique-view UAV absolute visual localization and systematically compares retrieval, matching and refinement choices.
- [From Coarse to Fine: Robust Hierarchical Localization at Large Scale](../resources/hloc-coarse-to-fine-2018.md) - paper - Foundational paper for hierarchical localization: global retrieval to find candidate places, then local matching for precise pose.
- [Grounding Image Matching in 3D with MASt3R](../resources/mast3r-2024.md) - paper - Frames matching as a 3D problem on top of DUSt3R, producing dense matches robust to extreme viewpoint change.
- [Image Matching: Local Features & Beyond (CVPR workshop)](../resources/cvpr-image-matching-workshop.md) - talk - Recurring CVPR workshop and Kaggle challenge on feature matching and structure-from-motion, with invited talks and recordings, covering the matchers used in visual geolocalization and VIO.
- [LightGlue: Local Feature Matching at Light Speed](../resources/lightglue-2023.md) - paper - Redesigns SuperGlue-style attention matching to be faster and adaptive, stopping early on easy pairs.
- [MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction Priors](../resources/mast3r-slam-murai-2024.md) - paper - Builds a real-time dense monocular SLAM system on the MASt3R two-view reconstruction prior, without assuming a fixed parametric camera model.
- [Photogrammetry I & II](../resources/stachniss-photogrammetry-i-ii.md) - lecture-series - Recorded two-semester photogrammetry course (2015/16 playlist): camera models, direct linear transform, projective geometry, epipolar geometry, bundle adjustment, and image-based 3D reconstruction.
- [RoMa: Robust Dense Feature Matching](../resources/roma-dense-matching-2023.md) - paper - Dense matcher combining foundation-model coarse features with fine refinement, robust to large appearance change.
- [Satellite Pose Estimation Challenge: Dataset, Competition Design and Results](../resources/kelvins-spec2019-paper.md) - paper - ESA Kelvins / Stanford competition on monocular spacecraft pose estimation, analyzing 48 entries.
- [STHN: Deep Homography Estimation for UAV Thermal Geo-localization with Satellite Imagery](../resources/sthn-thermal-homography-2024.md) - paper - Refines thermal-to-satellite localization with learned homography estimation for precise alignment.
- [Vision Algorithms for Mobile Robotics (UZH/ETH)](../resources/scaramuzza-vision-algorithms-mobile-robotics.md) - course - Graduate course building a monocular visual odometry pipeline step by step: image formation, calibration, feature detection, two-view geometry, P3P+RANSAC, bundle adjustment, KLT tracking, place recognition, visual-inert
- [Vision-based GNSS-Free Localization for UAVs in the Wild](../resources/wildnav-gnss-free-uav-localization-2022.md) - paper - Proposes matching drone camera frames to open satellite imagery with learned feature matching to get absolute position without GNSS, evaluated on flights over non-urban areas.
- [Visual Odometry: Part I - The First 30 Years and Fundamentals / Part II - Matching, Robustness, Optimization, and Applications](../resources/scaramuzza-vo-tutorial.md) - paper - Two-part IEEE Robotics & Automation Magazine tutorial (Part II at rpg.ifi.uzh.ch/docs/VO_Part_II_Scaramuzza.pdf).
- [XFeat: Accelerated Features for Lightweight Image Matching](../resources/xfeat-2024.md) - paper - Lightweight feature extraction and matching architecture aimed at real-time use on constrained hardware.

