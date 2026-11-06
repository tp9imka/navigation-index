# 4. Vision, LiDAR and radar odometry

After this chapter you can explain how a camera, LiDAR or radar measures motion, what SLAM
adds on top of odometry, and which open stack to run on which sensor. These are
*relative* sources: they slow drift, they do not remove it. Absolute fixes are chapter 5.

Prev: [Inertial and fusion](03-inertial-and-fusion.md) | Next: [Absolute alternative PNT](05-absolute-alt-pnt.md) | [Primer index](README.md)

## Odometry vs SLAM vs relocalization

- **Odometry** - estimate motion between consecutive frames or scans. Drift accumulates.
- **SLAM** - also build a map and recognise revisited places (**loop closure**), which pulls
  accumulated drift back. Modern SLAM is MAP estimation on a factor graph with a front end
  (data association) and a back end (optimisation)
  ([Cadena et al. survey](../../catalog/resources/cadena-slam-past-present-future-2016.md)).
- **Relocalization** - estimate pose against a map you built earlier. If that map is
  georeferenced, this becomes an absolute fix (chapter 5).

## Visual and visual-inertial odometry

A camera sees features (corners, learned keypoints) that move between frames. From matched
features you recover relative pose with two-view geometry and RANSAC, then refine with
bundle adjustment (minimise reprojection error over poses and 3D points)
([Scaramuzza and Fraundorfer VO tutorial](../../catalog/resources/scaramuzza-vo-tutorial.md)).

A single camera cannot see metric scale. Adding an IMU (VIO) recovers scale and gravity
direction and bridges fast motion
([Huang, VIN concise review](../../catalog/resources/huang-vins-concise-review-2019.md)). Two
estimator families coexist:

- **Filter-based (MSCKF)** - [OpenVINS](../../catalog/repos/rpng__open_vins.md), whose docs
  double as a derivation textbook ([OpenVINS docs](../../catalog/resources/openvins-docs.md)).
- **Sliding-window optimisation** - [VINS-Mono](../../catalog/resources/vins-mono-qin-2017.md),
  [ORB-SLAM3](../../catalog/resources/orb-slam3-campos-2020.md) (adds multi-map Atlas to
  recover from tracking loss), [Kimera](../../catalog/resources/kimera-rosinol-2019.md).

Calibration decides whether VIO works at all: camera intrinsics, camera-IMU extrinsics and
time offset ([Kalibr wiki](../../catalog/resources/kalibr-wiki.md)).

Simplest GNSS-free velocity source on a drone: **optical flow plus a rangefinder** for
scale, supported natively by both autopilots
([PX4 optical flow](../../catalog/resources/px4-optical-flow-docs.md),
[ArduPilot optical flow](../../catalog/resources/ardupilot-optical-flow-setup.md)).

Learned and foundation-model approaches ([DROID-SLAM](../../catalog/resources/droid-slam-teed-2021.md),
[MASt3R-SLAM](../../catalog/resources/mast3r-slam-murai-2024.md)) are more robust on hard
sequences and GPU-heavy. Event cameras offer microsecond latency and high dynamic range,
with algorithms redesigned for asynchronous data
([event vision survey](../../catalog/resources/gallego-event-vision-survey-2019.md)).
Thermal-inertial odometry targets darkness and smoke
([ETIO](../../catalog/resources/etio-thermal-inertial-odometry-2022.md)).

## LiDAR odometry and SLAM

LiDAR gives metric 3D points directly. Odometry registers each scan against the previous
scan or a local map, typically with ICP (iterative closest point) variants:

```
find T minimising  sum_i || T * p_i - q_nn(i) ||^2     # p from new scan, q nearest map point
```

- [KISS-ICP](../../catalog/resources/kiss-icp-vizzo-2022.md) argues that well-engineered
  point-to-point ICP is a strong baseline across sensors. `pip install` and go.
- [FAST-LIO2](../../catalog/resources/fast-lio2-xu-2021.md) fuses raw points with the IMU in
  an iterated Kalman filter; [LIO-SAM](../../catalog/resources/lio-sam-shan-2020.md) uses a
  factor graph where GNSS factors can be added or dropped.
- [FAST-LIVO2](../../catalog/resources/fast-livo2-zheng-2024.md) adds a camera and stays robust
  when one modality degrades.

Known weakness: **geometric degeneracy** - long tunnels, open fields, flat water - where the
scan does not constrain all six degrees of freedom
([LiDAR odometry survey](../../catalog/resources/lee-lidar-odometry-survey-2023.md)).

## Radar odometry

Radar sees through dust, smoke, fog and darkness. Spinning FMCW radars give 2D scans;
4D mmWave radars add elevation and Doppler (radial velocity per point) but produce sparse,
noisy clouds that need radar-specific methods
([4D radar survey](../../catalog/resources/han-4d-mmwave-radar-survey-2023.md)).
[CFEAR](../../catalog/resources/cfear-radarodometry-adolfsson-2021.md) shows simple filtering
working well on spinning radar. Radar is an active emitter, which matters in an EW setting
(it can be detected).

## Place recognition and feature matching

Loop closure and map relocalization need to answer "have I seen this place?":

- **Global descriptors (retrieval)** - one vector per image; nearest neighbour search.
  Foundation-model features generalise across domains without VPR-specific training
  ([AnyLoc](../../catalog/resources/anyloc-universal-vpr-2023.md),
  [SALAD](../../catalog/resources/salad-vpr-2023.md)).
- **Local matching** - verify and refine with keypoint matches
  ([LightGlue](../../catalog/resources/lightglue-2023.md), lightweight
  [XFeat](../../catalog/resources/xfeat-2024.md), dense [RoMa](../../catalog/resources/roma-dense-matching-2023.md)).
- **Retrieve-then-match** is the scalable pattern
  ([hloc paper](../../catalog/resources/hloc-coarse-to-fine-2018.md)). Chapter 5 reuses it for
  image-to-satellite localization.

## Failure modes under EW and in the field

These sensors are hard to jam, which is why they matter. Their failure modes are physical:

- **Low texture or repetitive scenes** (water, snow, sand, fields) starve VIO of features.
- **Lighting:** night, glare, fast exposure changes. Thermal or event cameras help.
- **Obscurants:** smoke and dust blind cameras and LiDAR; radar keeps working.
- **Degenerate geometry** for LiDAR (above).
- **Dynamic scenes:** moving vehicles and people violate the static-world assumption.
- **Initialization and scale:** monocular VIO needs motion to initialise
  ([VINS-Mono](../../catalog/resources/vins-mono-qin-2017.md)).
- **Active sensors are emitters.** LiDAR and radar can be detected; passive vision cannot.
- **Drift never goes to zero** without loop closure or an absolute fix.

## Learn it

1. [Stachniss YouTube channel, "5 Minutes with Cyrill"](../../catalog/resources/stachniss-youtube-channel.md) - short explainers on ICP, RANSAC, SIFT, factor graphs.
2. [Scaramuzza VO tutorial, Parts I and II](../../catalog/resources/scaramuzza-vo-tutorial.md) - best single read on VO design.
3. [TUM Visual Navigation for Flying Robots](../../catalog/resources/tum-visual-navigation-flying-robots.md) or the lighter [AUTONAVx MOOC](../../catalog/resources/tum-autonavx.md).
4. [Vision Algorithms for Mobile Robotics (UZH/ETH)](../../catalog/resources/scaramuzza-vision-algorithms-mobile-robotics.md) - exercises end in a working mini VO pipeline.
5. [14 Lectures on Visual SLAM](../../catalog/resources/gaoxiang-14-lectures-visual-slam.md) - code-heavy bridge to ORB-SLAM-style systems.
6. [Robot Mapping course (Freiburg)](../../catalog/resources/stachniss-slam-course-2013.md) with [exercises](../../catalog/resources/freiburg-robot-mapping-course.md).
7. [Cadena et al. SLAM survey](../../catalog/resources/cadena-slam-past-present-future-2016.md) and [VIN concise review](../../catalog/resources/huang-vins-concise-review-2019.md).
8. [MIT 16.485 VNAV](../../catalog/resources/mit-vnav-16485.md) - ROS 2 labs to a quadrotor VIO stack.
9. [LiDAR odometry survey](../../catalog/resources/lee-lidar-odometry-survey-2023.md) and [4D radar survey](../../catalog/resources/han-4d-mmwave-radar-survey-2023.md).
10. [SLAM Handbook](../../catalog/resources/slam-handbook.md) - current one-stop reference, including radar chapters.

## Build with it

- [OpenVINS](../../catalog/repos/rpng__open_vins.md) - MSCKF VIO with a built-in simulator.
- [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md) ([ROS 2 wrapper](../../catalog/repos/zang09__orb_slam3_ros2.md)) - visual/VI SLAM.
- [VINS-Fusion](../../catalog/repos/hkust-aerial-robotics__vins-fusion.md) - VIO with a global-fusion node for GNSS.
- [RTAB-Map](../../catalog/repos/introlab__rtabmap.md) ([ROS](../../catalog/repos/introlab__rtabmap_ros.md)) - RGB-D/stereo/LiDAR SLAM with map save and relocalization.
- [Kalibr](../../catalog/repos/ethz-asl__kalibr.md) - camera and camera-IMU calibration.
- [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md) and [KISS-SLAM](../../catalog/repos/prbonn__kiss-slam.md) - minimal LiDAR odometry and SLAM.
- [FAST-LIO](../../catalog/repos/hku-mars__fast_lio.md) and [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md) - LiDAR-inertial.
- [small_gicp](../../catalog/repos/koide3__small_gicp.md) - scan-to-map registration for localization prototypes.
- [RIO](../../catalog/repos/christopherdoer__rio.md) and [4DRadarSLAM](../../catalog/repos/zhuge2333__4dradarslam.md) - radar-inertial odometry and SLAM.
- [LightGlue](../../catalog/repos/cvg__lightglue.md), [XFeat](../../catalog/repos/verlab__accelerated_features.md), [hloc](../../catalog/repos/cvg__hierarchical-localization.md), [AnyLoc](../../catalog/repos/anyloc__anyloc.md) - matching and retrieval.
- [evo](../../catalog/repos/michaelgrupp__evo.md) - evaluate any trajectory (chapter 9).

Samples in this hub: [`samples/vio-to-mavlink-bridge`](../../samples/vio-to-mavlink-bridge/).

Related concepts: [VIO](../../catalog/concepts/vio.md), [visual SLAM](../../catalog/concepts/visual-slam.md),
[LiDAR SLAM](../../catalog/concepts/lidar-slam.md), [radar navigation](../../catalog/concepts/radar-nav.md),
[place recognition](../../catalog/concepts/place-recognition.md), [feature matching](../../catalog/concepts/feature-matching.md).
