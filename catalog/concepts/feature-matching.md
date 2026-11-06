# Feature detection and matching

`concept:feature-matching`

Keypoints/descriptors and learned matchers (SIFT, SuperPoint, LightGlue, LoFTR).

## Samples (3)

- [Drone frame to orthophoto geolocalization with LightGlue](../../catalog/samples/visual-geolocalization-lightglue.md) - Matches a nadir drone frame against a georeferenced satellite or orthophoto tile with SuperPoint + LightGlue, fits a MAGSAC homography with OpenCV, and maps the frame centre through the GeoTIFF geotransform to lat/lon.
- [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md) - The coarse first stage that geoloc-license-clean lacks: no position prior, unknown heading.
- [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md) - Drone frame => NAIP orthophoto => lat/lon using only permissively licensed parts: ALIKED (BSD-3), DISK and LightGlue weights (Apache-2.0), OpenCV SIFT and MAGSAC (Apache-2.0), rasterio, public-domain NAIP from Microsoft 

## Guides (3)

- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) - After this chapter you can explain how a camera, LiDAR or radar measures motion, what SLAM adds on top of odometry, and which open stack to run on which sensor.
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) - After this chapter you can explain the five main ways to get an absolute position without GNSS - image-to-map matching, terrain matching, magnetic anomaly matching, celestial fixes and signals of opportunity - pick the o
- [Model weights licenses: code vs weights vs training data](../../docs/model-weights-licenses.md) - Learned models in navigation pipelines carry three separate sets of terms:

## Repositories (34)

- [LightGlue](../../catalog/repos/cvg__lightglue.md) - fit: high - Fast learned local feature matcher (ICCV 2023) that adapts its depth to pair difficulty; works with SuperPoint, DISK, ALIKED and SIFT features.
- [hloc](../../catalog/repos/cvg__hierarchical-localization.md) - fit: high - Toolbox for hierarchical visual localization: global retrieval (NetVLAD etc.) to find candidate images, then local feature matching (SuperPoint, LightGlue...) and PnP against an SfM model.
- [XFeat](../../catalog/repos/verlab__accelerated_features.md) - fit: high - Lightweight local feature extractor and matcher (CVPR 2024) designed for speed on constrained hardware.
- [RoMa](../../catalog/repos/parskatt__roma.md) - fit: high - Robust dense feature matcher (CVPR 2024) estimating pixel-dense warps with certainties, strong under large appearance change.
- [small_gicp](../../catalog/repos/koide3__small_gicp.md) - fit: high - Efficient, parallel point-cloud registration library (GICP, ICP variants) with C++ and Python APIs.
- [vismatch (image-matching-models)](../../catalog/repos/gmberton__vismatch.md) - fit: high - Wrapper exposing 50+ image matching models behind one interface (formerly image-matching-models).
- [LightGlue-ONNX](../../catalog/repos/fabio-sim__lightglue-onnx.md) - fit: high - ONNX export and inference of LightGlue matching with SuperPoint, DISK and ALIKED extractors (including RaCo-ALIKED-LightGlue+), with TensorRT, OpenVINO and FP8 quantization workflows.
- [WildNav](../../catalog/repos/tiers__wildnav.md) - fit: high - Python pipeline that localizes a drone by matching its downward camera frames against georeferenced satellite map tiles with SuperGlue, then converts the best match into GPS coordinates.
- [AnyVisLoc benchmark](../../catalog/repos/uav-avl__benchmark.md) - fit: high - Benchmark and code for UAV absolute visual localization under low-altitude, multi-view (oblique) observation, comparing retrieval and matching combinations against aerial and satellite reference maps.
- [visual_localization (GNSS-free UAV)](../../catalog/repos/terbouchehacene__visual_localization.md) - fit: high - A cleaner reimplementation of the WildNav idea: match UAV images to satellite tiles with SuperPoint/SuperGlue-style matchers and estimate geographic position.
- [UAVLocalization (map retrieval + alignment)](../../catalog/repos/hmf21__uavlocalization.md) - fit: high - Geo-localization system for aerial platforms that first retrieves the right satellite map region with a deep descriptor and then aligns the drone orthophoto to it to extract coordinates; evaluated on reorganized public A
- [aerial-nav - GPS-denied navigation via Siamese network](../../catalog/repos/sviridov-aleksandr__aerial-nav.md) - fit: high - Matches onboard camera frames to a pre-built satellite map of the route: a ResNet-18 Siamese network with SAFA spatial aggregation ranks map tiles indexed at 13 altitude levels (0-1200 m), then SuperPoint/LightGlue with 
- [14 Lectures on Visual SLAM (2nd ed.) code](../../catalog/repos/gaoxiang12__slambook2.md) - fit: medium - Companion code for the second edition of Gao Xiang's visual SLAM textbook: Lie groups, nonlinear optimization, feature VO, direct methods, back-end and loop closure examples in C++.
- [SuperGlue (pretrained)](../../catalog/repos/magicleap__supergluepretrainednetwork.md) - fit: medium - Pretrained SuperGlue graph-neural-network matcher with SuperPoint features (CVPR 2020).
- [MASt3R-SLAM](../../catalog/repos/rmurai0610__mast3r-slam.md) - fit: medium - Real-time dense monocular SLAM built on the MASt3R two-view 3D reconstruction prior, needing no fixed camera model (CVPR 2025).
- [MASt3R](../../catalog/repos/naver__mast3r.md) - fit: medium - Matching grounded in 3D: predicts dense correspondences and 3D pointmaps from image pairs, building on DUSt3R.
- [LoFTR](../../catalog/repos/zju3dv__loftr.md) - fit: medium - Detector-free transformer matcher producing dense-ish correspondences, good on low-texture scenes.
- [TEASER++](../../catalog/repos/mit-spark__teaser-plusplus.md) - fit: medium - Certifiable, outlier-robust point-cloud registration library with C++, Python and MATLAB bindings.
- [SuperPoint (pretrained)](../../catalog/repos/magicleap__superpointpretrainednetwork.md) - fit: medium - Pretrained SuperPoint keypoint detector and descriptor.
- [fast_gicp](../../catalog/repos/koide3__fast_gicp.md) - fit: medium - Collection of fast GICP and VGICP point-cloud registration implementations, multithreaded and CUDA.
- [AirSLAM](../../catalog/repos/sair-lab__airslam.md) - fit: medium - Point-and-line visual(-inertial) SLAM using learned features, designed for illumination-robust operation, with TensorRT acceleration; successor to AirVO.
- [GTSfM](../../catalog/repos/borglab__gtsfm.md) - fit: medium - End-to-end structure-from-motion pipeline built on GTSAM, with pluggable front-ends (classical and learned matchers) and distributed execution via Dask.
- [vision_landing](../../catalog/repos/goodrobots__vision_landing.md) - fit: medium - Precision landing using visual fiducial targets, sending LANDING_TARGET messages to ArduPilot.
- [Aerial Template Matching](../../catalog/repos/m-hamza-mughal__aerial-template-matching.md) - fit: medium - Code for the paper 'Assisting UAV Localization via Deep Contextual Image Matching': locates an aerial template inside a larger georeferenced map with a SIFT pipeline and a deep variant built on Neighbourhood Consensus Ne
- [STHN](../../catalog/repos/arplaboratory__sthn.md) - fit: medium - Deep homography estimation for aligning UAV thermal images to satellite maps (RA-L 2024), refining coarse geo-localization into precise alignment.
- [rope-ladder-tracker](../../catalog/repos/vohminv__rope-ladder-tracker.md) - fit: medium - Python/OpenCV return-to-home for a quadcopter with a downward camera and no GPS.
- [UAVision](../../catalog/repos/arborisers__uavision.md) - fit: medium - Map-matching-based visual localization software for UAVs in GNSS-denied settings, shipped with a GUI front end and demo.
- [Visual Locator](../../catalog/repos/rtwotwo__visual-locator.md) - fit: medium - Absolute drone positioning by image retrieval (SelaVPR-style ViT features) over cropped satellite tiles followed by registration with SIFT+RANSAC or SuperPoint+SuperGlue.
- [VGGT](../../catalog/repos/facebookresearch__vggt.md) - fit: low - Visual Geometry Grounded Transformer: a feed-forward network predicting camera poses, depth and point maps from one or many images (CVPR 2025 best paper).
- [Glue Factory](../../catalog/repos/cvg__glue-factory.md) - fit: low - Training library for local feature detection and matching (trains LightGlue and others).
- [Quatro](../../catalog/repos/url-kaist__quatro.md) - fit: low - Fast, robust global registration for terrestrial robots that assumes near-planar motion to cut degrees of freedom.
- [EKLT](../../catalog/repos/uzh-rpg__rpg_eklt.md) - fit: low - Asynchronous photometric feature tracking that combines events and frames (IJCV 2019).
- [Event feature tracking (EM-ICP)](../../catalog/repos/daniilidis-group__event_feature_tracking.md) - fit: low - MATLAB implementations of event-based feature tracking methods from the Penn GRASP lab.
- [bsu-science - BSU diploma on camera-based UAV navigation](../../catalog/repos/drapegnik__bsu-science.md) - fit: low - LaTeX sources of science reports from BSU (Belarus, FAMCS), including a diploma 'Разработка алгоритмов навигации БПЛА' that compares SIFT/SURF/ORB, surveys SLAM and SfM 3D mapping, and demonstrates SLAM + ROS + webcam + 

## Documents, talks, courses, datasets (23)

- [14 Lectures on Visual SLAM: From Theory to Practice](../../catalog/resources/gaoxiang-14-lectures-visual-slam.md) - book - English translation of the popular Chinese visual SLAM textbook, from rigid-body motion and Lie algebra through camera models, nonlinear optimization, feature/direct VO, backend optimization, loop closure and dense mappi
- [Cyrill Stachniss YouTube channel (incl. '5 Minutes with Cyrill')](../../catalog/resources/stachniss-youtube-channel.md) - video - Channel hosting Stachniss's full lecture courses plus the '5 Minutes with Cyrill' series of short explainers on single concepts (Kalman filter, factor graphs, ICP, RANSAC, SIFT, occupancy grids).
- [Exploring the best way for UAV visual localization under Low-altitude Multi-view Observation Condition: a Benchmark](../../catalog/resources/anyvisloc-uav-localization-benchmark-2025.md) - paper - Builds a benchmark for low-altitude, oblique-view UAV absolute visual localization and systematically compares retrieval, matching and refinement choices.
- [From Coarse to Fine: Robust Hierarchical Localization at Large Scale](../../catalog/resources/hloc-coarse-to-fine-2018.md) - paper - The HF-Net paper and foundation of hloc: global retrieval to find candidate places, then local matching for precise pose.
- [Grounding Image Matching in 3D with MASt3R](../../catalog/resources/mast3r-2024.md) - paper - Frames matching as a 3D problem on top of DUSt3R, producing dense matches robust to extreme viewpoint change.
- [Image Matching: Local Features & Beyond (CVPR workshop)](../../catalog/resources/cvpr-image-matching-workshop.md) - talk - Recurring CVPR workshop and Kaggle challenge on feature matching and structure-from-motion, with invited talks and recordings, covering the matchers used in visual geolocalization and VIO.
- [LightGlue: Local Feature Matching at Light Speed](../../catalog/resources/lightglue-2023.md) - paper - Redesigns SuperGlue-style attention matching to be faster and adaptive, stopping early on easy pairs.
- [MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction Priors](../../catalog/resources/mast3r-slam-murai-2024.md) - paper - Builds a real-time dense monocular SLAM system on the MASt3R two-view reconstruction prior, without assuming a fixed parametric camera model.
- [Photogrammetry I & II](../../catalog/resources/stachniss-photogrammetry-i-ii.md) - lecture-series - Recorded two-semester photogrammetry course (2015/16 playlist): camera models, direct linear transform, projective geometry, epipolar geometry, bundle adjustment, and image-based 3D reconstruction.
- [RoMa: Robust Dense Feature Matching](../../catalog/resources/roma-dense-matching-2023.md) - paper - Dense matcher combining foundation-model coarse features with fine refinement, robust to large appearance change.
- [Satellite Pose Estimation Challenge: Dataset, Competition Design and Results](../../catalog/resources/kelvins-spec2019-paper.md) - paper - ESA Kelvins / Stanford competition on monocular spacecraft pose estimation, analyzing 48 entries.
- [STHN: Deep Homography Estimation for UAV Thermal Geo-localization with Satellite Imagery](../../catalog/resources/sthn-thermal-homography-2024.md) - paper - Refines thermal-to-satellite localization with learned homography estimation for precise alignment.
- [Vision Algorithms for Mobile Robotics (UZH/ETH)](../../catalog/resources/scaramuzza-vision-algorithms-mobile-robotics.md) - course - Graduate course building a monocular visual odometry pipeline step by step: image formation, calibration, feature detection, two-view geometry, P3P+RANSAC, bundle adjustment, KLT tracking, place recognition, visual-inert
- [Vision-based GNSS-Free Localization for UAVs in the Wild](../../catalog/resources/wildnav-gnss-free-uav-localization-2022.md) - paper - Proposes matching drone camera frames to open satellite imagery with learned feature matching to get absolute position without GNSS, evaluated on flights over non-urban areas.
- [Visual Odometry: Part I - The First 30 Years and Fundamentals / Part II - Matching, Robustness, Optimization, and Applications](../../catalog/resources/scaramuzza-vo-tutorial.md) - paper - Two-part IEEE Robotics & Automation Magazine tutorial (Part II at rpg.ifi.uzh.ch/docs/VO_Part_II_Scaramuzza.pdf).
- [XFeat: Accelerated Features for Lightweight Image Matching](../../catalog/resources/xfeat-2024.md) - paper - Lightweight feature extraction and matching architecture aimed at real-time use on constrained hardware.
- [Алгоритм оптичної навігації дрона](../../catalog/resources/kma-boiko-optical-nav-thesis-2025.md) - report - English: 'Drone optical navigation algorithm'.
- [Метод навігації БПЛА в умовах відсутності GPS-сигналу на основі візуальної одометрії](../../catalog/resources/zp-baranov-vo-gps-denied-2024.md) - paper - English: 'UAV navigation method in GPS-denied conditions based on visual odometry'.
- [Навигация по снимкам местности на основе сопоставления глубоких признаков и визуальной одометрии](../../catalog/resources/bntu-rulko-terrain-nav-deep-features-2025.md) - paper - English: 'Terrain relative navigation based on deep feature template matching and visual odometry'.
- [Разработка алгоритма абсолютной визуально-инерциальной навигации беспилотных воздушных судов](../../catalog/resources/preprints-lazareva-absolute-vi-nav.md) - paper - English: 'Development of an absolute visual-inertial navigation algorithm for unmanned aircraft'.
- [Разработка алгоритмов навигации БПЛА](../../catalog/resources/bsu-pazhitnykh-uav-nav-diploma-slides.md) - report - English: 'Development of UAV navigation algorithms'.
- [Разработка метода навигации беспилотных летательных аппаратов по изображению подстилающей поверхности в условиях отсутствия сигналов внешних навигационных систем](../../catalog/resources/itmo-litvinenko-underlying-surface-nav-2025.md) - paper - English: 'A method for UAV navigation by images of the underlying surface without external navigation signals'.
- [Формування вирішальної функції кореляційно-екстремальних систем навігації за критерієм максимуму узагальненого коефіцієнта взаємної кореляції](../../catalog/resources/khpi-yeriomina-sotnikov-cens-decision-function-2016.md) - paper - English: 'Forming the decision function of correlation-extremal navigation systems by the maximum generalised cross-correlation criterion' (Bulletin of NTU KhPI, No.

