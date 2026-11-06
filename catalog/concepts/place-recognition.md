# Place recognition and loop closure

`concept:place-recognition`

Global descriptors, image retrieval, LiDAR place recognition.

## Samples (1)

- [Drone frame to orthophoto geolocalization with LightGlue](../samples/visual-geolocalization-lightglue.md) - Matches a nadir drone frame against a georeferenced satellite or orthophoto tile with SuperPoint + LightGlue, fits a MAGSAC homography with OpenCV, and maps the frame centre through the GeoTIFF geotransform to lat/lon.

## Repositories (38)

- [ORB-SLAM3](../repos/uz-slamlab__orb_slam3.md) - fit: high - Visual, visual-inertial and multi-map SLAM supporting monocular, stereo and RGB-D cameras with pinhole and fisheye models, using a map atlas to survive tracking loss.
- [hloc](../repos/cvg__hierarchical-localization.md) - fit: high - Toolbox for hierarchical visual localization: global retrieval (NetVLAD etc.) to find candidate images, then local feature matching (SuperPoint, LightGlue...) and PnP against an SfM model.
- [RTAB-Map](../repos/introlab__rtabmap.md) - fit: high - Graph-based SLAM library and app supporting RGB-D, stereo and LiDAR, with memory management for large-scale loop closure and map reuse.
- [FAST_LIO_LOCALIZATION](../repos/hviktortsoi__fast_lio_localization.md) - fit: high - Relocalization in a prebuilt map using FAST-LIO odometry plus global scan-to-map registration.
- [AnyLoc](../repos/anyloc__anyloc.md) - fit: high - Universal visual place recognition using foundation-model (DINOv2) features with VLAD/GeM aggregation, working across aerial, underwater, indoor and outdoor domains without task-specific training.
- [KISS-SLAM](../repos/prbonn__kiss-slam.md) - fit: high - LiDAR SLAM that adds loop closure and pose-graph optimization on top of KISS-ICP odometry.
- [SALAD](../repos/serizba__salad.md) - fit: high - Place recognition descriptor using optimal-transport aggregation of DINOv2 features.
- [AnyVisLoc benchmark](../repos/uav-avl__benchmark.md) - fit: high - Benchmark and code for UAV absolute visual localization under low-altitude, multi-view (oblique) observation, comparing retrieval and matching combinations against aerial and satellite reference maps.
- [VPR methods evaluation](../repos/gmberton__vpr-methods-evaluation.md) - fit: high - Wrapper exposing many state-of-the-art place recognition models behind one interface so you can switch models with one parameter.
- [UAVLocalization (map retrieval + alignment)](../repos/hmf21__uavlocalization.md) - fit: high - Geo-localization system for aerial platforms that first retrieves the right satellite map region with a deep descriptor and then aligns the drone orthophoto to it to extract coordinates; evaluated on reorganized public A
- [ORB-SLAM2](../repos/raulmur__orb_slam2.md) - fit: medium - Feature-based SLAM for monocular, stereo and RGB-D cameras using ORB features, with loop closing and relocalization against a reusable map.
- [SC-LIO-SAM](../repos/gisbi-kim__sc-lio-sam.md) - fit: medium - LIO-SAM combined with Scan Context loop closure for more reliable large-scale LiDAR-inertial SLAM.
- [STD](../repos/hku-mars__std.md) - fit: medium - Stable Triangle Descriptor for 3D point-cloud place recognition and loop closure.
- [Swarm-SLAM](../repos/mistlab__swarm-slam.md) - fit: medium - Sparse, decentralized collaborative SLAM for multi-robot systems on ROS 2, supporting lidar, stereo and RGB-D with inter-robot loop closures under limited communication.
- [University-1652 baseline](../repos/layumi__university1652-baseline.md) - fit: medium - Dataset and baseline code for drone-based geo-localization across drone, satellite and ground views of university buildings worldwide.
- [MapClosures](../repos/prbonn__mapclosures.md) - fit: medium - Loop-closure detection using bird's-eye-view density images of local LiDAR maps.
- [CosPlace](../repos/gmberton__cosplace.md) - fit: medium - CVPR 2022 large-scale visual geo-localization treating place recognition as classification over geographic cells.
- [LAMP (NeBula multi-robot SLAM)](../repos/nebula-autonomy__lamp.md) - fit: medium - Team CoSTAR's large-scale multi-robot lidar SLAM back end with robust loop closure, from the NASA JPL-led SubT entry.
- [MixVPR](../repos/amaralibey__mixvpr.md) - fit: medium - WACV 2023 place recognition descriptor built by MLP feature mixing; lightweight and fast.
- [DCL-SLAM](../repos/zhongshp__dcl-slam.md) - fit: medium - Distributed collaborative lidar SLAM for robotic swarms with lightweight LiDAR-Iris descriptors for inter-robot place recognition and minimal data exchange.
- [SelaVPR](../repos/lu-feng__selavpr.md) - fit: medium - ICLR 2024 method adapting pretrained foundation models for place recognition with lightweight adapters, producing both global and local features.
- [BoQ](../repos/amaralibey__bag-of-queries.md) - fit: medium - CVPR 2024 place recognition with a bag of learnable global queries over backbone features.
- [Sample4Geo](../repos/skyy93__sample4geo.md) - fit: medium - Cross-view geo-localization training with hard negative sampling, reporting strong results on drone-satellite and street-satellite benchmarks with a simple contrastive setup.
- [EigenPlaces](../repos/gmberton__eigenplaces.md) - fit: medium - ICCV 2023 visual place recognition training method for viewpoint-robust descriptors.
- [VPR-Bench](../repos/mubarizzaffar__vpr-bench.md) - fit: medium - Open-source visual place recognition evaluation framework from the IJCV paper, with many datasets and techniques integrated.
- [Mapillary SLS](../repos/mapillary__mapillary_sls.md) - fit: medium - Tools for the Mapillary Street-level Sequences dataset for lifelong visual place recognition.
- [Scan Context](../repos/gisbi-kim__scancontext.md) - fit: medium - LiDAR global place descriptor for loop detection and relocalization (backup of the original IRAP KAIST repo).
- [TBV Radar SLAM](../repos/dan11003__tbv_slam_public.md) - fit: medium - Radar SLAM with verified loop closures built on CFEAR radar odometry.
- [ALTO](../repos/metaslam__alto.md) - fit: medium - Aerial-view, large-scale, terrain-oriented dataset for aerial place recognition and localization.
- [Hilti SLAM Challenge 2023](../repos/hilti-research__hilti-slam-challenge-2023.md) - fit: medium - Repository for the 2023 Hilti SLAM Challenge, including multi-session sequences.
- [ReFeree](../repos/sparolab__referee.md) - fit: medium - Lightweight radar global descriptor for radar place recognition (RA-L 2024).
- [VPAIR](../repos/aervisloc__vpair.md) - fit: medium - Repo for VPAIR, an aerial visual place recognition dataset matching low-altitude flight imagery to reference orthophotos.
- [U2S-CVGL (scale-aware UAV-to-satellite)](../repos/uav-avl__u2s-cvgl.md) - fit: medium - Scale-aware cross-view geo-localization method for matching UAV views to satellite imagery when the altitude-driven scale difference is unknown.
- [rope-ladder-tracker](../repos/vohminv__rope-ladder-tracker.md) - fit: medium - Python/OpenCV return-to-home for a quadcopter with a downward camera and no GPS.
- [Visual Locator](../repos/rtwotwo__visual-locator.md) - fit: medium - Absolute drone positioning by image retrieval (SelaVPR-style ViT features) over cropped satellite tiles followed by registration with SIFT+RANSAC or SuperPoint+SuperGlue.
- [maplab](../repos/ethz-asl__maplab.md) - fit: low - Modular multi-session, multi-modal mapping framework with map merging, optimization and localization against saved maps.
- [LPN (Local Pattern Network)](../repos/wtyhub__lpn.md) - fit: low - PyTorch implementation of a cross-view geo-localization method that pools features in rings around the image center to capture contextual local patterns.
- [Open-RadVLAD](../repos/mttgdd__open-radvlad.md) - fit: low - Fast radar place recognition using VLAD-style aggregation over radar polar scans.

## Documents, talks, courses, datasets (13)

- [AnyLoc: Towards Universal Visual Place Recognition](../resources/anyloc-universal-vpr-2023.md) - paper - Shows that unsupervised aggregation of foundation-model (DINOv2) features gives place recognition that generalizes across domains including aerial imagery, without VPR-specific training.
- [DCL-SLAM: A Distributed Collaborative LiDAR SLAM Framework for a Robotic Swarm](../resources/dcl-slam-paper.md) - paper - Describes a fully distributed lidar C-SLAM using compact descriptors for inter-robot place recognition.
- [From Coarse to Fine: Robust Hierarchical Localization at Large Scale](../resources/hloc-coarse-to-fine-2018.md) - paper - The HF-Net paper and foundation of hloc: global retrieval to find candidate places, then local matching for precise pose.
- [HeLiPR: Heterogeneous LiDAR Dataset for inter-LiDAR Place Recognition](../resources/snu-helipr-dataset.md) - dataset - Same routes captured with Ouster, Aeva, Livox and Velodyne lidars to test place recognition across different lidar types.
- [Long-Term Visual Localization benchmark](../resources/visual-localization-benchmark.md) - competition - Benchmark and workshop series for 6-DoF visual localization under changing conditions (day/night, seasons), with standard datasets and an evaluation server.
- [MulRan: Multimodal Range Dataset for Urban Place Recognition](../resources/snu-mulran-dataset.md) - dataset - Urban sequences with radar and lidar for range-sensor place recognition and odometry.
- [Optimal Transport Aggregation for Visual Place Recognition](../resources/salad-vpr-2023.md) - paper - Introduces SALAD, aggregating DINOv2 local features into a global descriptor via optimal transport.
- [Oxford RobotCar Dataset](../resources/oxford-robotcar-dataset.md) - dataset - Repeated drives of the same Oxford route over a year in all weather, with cameras, lidar and GPS/INS.
- [Sample4Geo: Hard Negative Sampling For Cross-View Geo-Localisation](../resources/sample4geo-2023.md) - paper - Shows that a simple contrastive setup with careful hard-negative sampling performs strongly on cross-view geo-localization benchmarks.
- [The University of Michigan North Campus Long-Term Vision and LIDAR Dataset](../resources/umich-nclt-dataset.md) - dataset - Segway robot sessions over many months on one campus with lidar, omnidirectional camera, GPS, IMU and odometry.
- [Vision Algorithms for Mobile Robotics (UZH/ETH)](../resources/scaramuzza-vision-algorithms-mobile-robotics.md) - course - Graduate course building a monocular visual odometry pipeline step by step: image formation, calibration, feature detection, two-view geometry, P3P+RANSAC, bundle adjustment, KLT tracking, place recognition, visual-inert
- [Как я научил квадрокоптер возвращаться домой без GPS: алгоритм «верёвочной лестницы»](../resources/habr-rope-ladder-return-home-2025.md) - blog - English: 'How I taught a quadcopter to return home without GPS: the rope-ladder algorithm'.
- [Уловки, подсмотренные у медоносных пчёл, помогают дронам возвращаться домой без GPS](../resources/habr-bee-nav-translation-2026.md) - blog - English: 'Tricks borrowed from honeybees help drones return home without GPS'.

