# Integration cards - round 5: LIO/SLAM, inertial tooling, timing, planning, flight links

<!-- about: repo:tixiaoshan/lio-sam, repo:koide3/small_gicp, repo:hviktortsoi/fast_lio_localization, repo:prbonn/rko_lio, repo:prbonn/kiss-slam, repo:introlab/rtabmap_ros, repo:zang09/orb_slam3_ros2, repo:nvidia-isaac-ros/isaac_ros_visual_slam, repo:artivis/manif, repo:ccnyroboticslab/imu_tools, repo:mbrossar/ai-imu-dr, repo:ori-drs/allan_variance_ros, repo:aewallin/allantools, repo:decargroup/navlie, repo:umich-curly/drift, repo:nmayorov/pyins, repo:utiasstars/pyshoe, repo:nwtime/linuxptp, repo:gitlab.com/chrony/chrony, repo:jclark/satpulse, repo:osgeo/proj, repo:skyfielders/python-skyfield, repo:mavlink/mavlink, repo:mavlink/mavsdk, repo:bitcraze/crazyflie-firmware, repo:gazebosim/ros_gz, repo:patrykcieslak/stonefish, repo:tomojitakasu/rtklib, repo:ompl/ompl, repo:zju-fast-lab/ego-planner-swarm, repo:caochao39/tare_planner, repo:anybotics/grid_map, repo:leggedrobotics/elevation_mapping_cupy, repo:robodhruv/visualnav-transformer -->

What each card gives you in a hackathon. All 34 were written from READMEs, source files, PyPI JSON, rosdistro and issues. None of these repos was installed or run for the cards, and every snippet is marked "not run".

## LiDAR / visual odometry and SLAM

- [LIO-SAM](tixiaoshan__lio-sam.md) - LiDAR-inertial SLAM on GTSAM with GPS factor and loop closure (ROS 1 and ROS 2 branches). Needs a 9-axis IMU and per-point `time` + `ring`. GPS is effectively off by default (`gpsTopic` defaults to `odometry/gpsz`).
- [RKO-LIO](prbonn__rko_lio.md) - pip (`rko-lio`) or apt (Humble..Rolling) LiDAR-inertial odometry. Extrinsics are mandatory, and the `<from>2<to>` naming is easy to invert. No GNSS input.
- [KISS-SLAM](prbonn__kiss-slam.md) - offline LiDAR SLAM with loop closure and Nav2-style `map.png/.yaml`. `--refuse-scans` is broken in PyPI 0.0.2 (#59). No Linux aarch64 wheels.
- [small_gicp](koide3__small_gicp.md) - MIT ICP/GICP/VGICP library with aarch64 and macOS arm64 wheels. Library only, no ROS node, and Python defaults to `num_threads=1`.
- [FAST_LIO_LOCALIZATION](hviktortsoi__fast_lio_localization.md) - prior-PCD-map relocalization on FAST-LIO via 0.5 Hz Open3D ICP. ROS 1 + Python 2.7 + Open3D 0.9 makes it close to uninstallable today. Needs a rough initial pose.
- [rtabmap_ros](introlab__rtabmap_ros.md) - apt ROS 2 RTAB-Map with localization-only mode and Nav2 outputs. Fast DDS with `qos=0` silently drops large messages. The `-d` arg wipes the map DB on start.
- [orb_slam3_ros2](zang09__orb_slam3_ros2.md) - thin ROS 2 wrapper over ORB-SLAM3. Publishes no pose and no TF, only `KeyFrameTrajectory.txt` on shutdown. No licence file, and it links GPL-3.0 ORB-SLAM3.
- [isaac_ros_visual_slam](nvidia-isaac-ros__isaac_ros_visual_slam.md) - GPU stereo VIO/SLAM => odometry + TF (see also [cuVSLAM](nvidia-isaac__cuvslam.md)). Renamed to `isaac_ros_cuvslam` on 2026-09-21. v5.0 targets ROS 2 Lyrical / JetPack 7.2, so older launch and apt names no longer match.

## Inertial math, calibration and dead reckoning

- [manif](artivis__manif.md) - header-only Lie groups (SO3, SE3, SE_2(3), ...) with analytic Jacobians. `manifpy` is not on PyPI: use conda-forge or build from source.
- [imu_tools](ccnyroboticslab__imu_tools.md) - Madgwick and complementary filters, `imu/data_raw` => `imu/data`. Madgwick defaults to `use_mag: true` and publishes nothing without `imu/mag`. Madgwick is GPL-3.0.
- [allan_variance_ros](ori-drs__allan_variance_ros.md) - static IMU bag (3 h+) => Kalibr `imu.yaml`. ROS 1. Short bags give NaN and `analysis.py` crashes (#43). The licence file says BSD-3 but `package.xml` says "Proprietary".
- [allantools](aewallin__allantools.md) - ADEV/MDEV/TDEV/MTIE for clocks and IMUs. `data_type` defaults to phase, so frequency data silently gives wrong curves. LGPL-3.0.
- [navlie](decargroup__navlie.md) - pure-Python on-manifold EKF/IEKF/UKF/IMM/batch with NEES tools. PyPI 0.0.1 misses its `pymlg` dependency, so install from git.
- [DRIFT](umich-curly__drift.md) - C++ invariant EKF for IMU + wheel/leg/DVL dead reckoning. ROS 1 Noetic only. Config paths are fixed at compile time.
- [AI-IMU dead reckoning](mbrossar__ai-imu-dr.md) - IMU-only car DR (IEKF + CNN-adapted noise), KITTI only. The weights link is reported dead. The data is KITTI-derived (CC BY-NC-SA).
- [pyins](nmayorov__pyins.md) - Python GNSS/INS error-state EKF and IMU simulator. The PyPI name is `python-ins` (`pyins` does not exist), and PyPI 1.0.1 lags master.
- [pyshoe](utiasstars__pyshoe.md) - foot-mounted ZUPT INS with classical and learned zero-velocity detectors. No LICENSE file, and `sklearn.externals.joblib` breaks it on current scikit-learn.

## Time sync and holdover

- [linuxptp](nwtime__linuxptp.md) - `ptp4l` / `phc2sys` / `ts2phc` (GNSS PPS + NMEA into the NIC clock). GPL-2.0, or GPL-3 when built with OpenSSL. Some NICs timestamp both PPS edges.
- [chrony](gitlab.com__chrony__chrony.md) - PPS/SOCK/SHM/PHC refclocks. `minsources`/`maxchange` let a spoofed GNSS become a falseticker instead of moving the clock. PPS needs `lock` to a coarse source. Prefer SOCK over SHM.
- [SatPulse](jclark__satpulse.md) - GNSS receiver daemon feeding chrony, ptp4l and NTRIP, with a web workbench. Young 0.x project. `satpulsewb` binds all interfaces.

## Geodesy and celestial

- [PROJ](osgeo__proj.md) - CRS transforms and geoids. pyproj wheels ship no grids and network access is off, so it can silently fall back to "ballpark" transforms (hundreds of metres horizontally). Watch EPSG:4326 axis order.
- [Skyfield](skyfielders__python-skyfield.md) - star, Sun and TLE/SGP4 satellite positions for celestial / LEO nav. Ephemerides download to the CWD. No refraction unless you pass `temperature_C`.

## Flight links, vehicles and simulators

- [MAVLink](mavlink__mavlink.md) - XML dialects + mavgen (GPS_INPUT 232, ODOMETRY 331, VISION_POSITION_ESTIMATE 102). Custom messages need the same dialect on every hop. Generated code is MIT, the generator is LGPL-3.0. See also [pymavlink](ardupilot__pymavlink.md).
- [MAVSDK](mavlink__mavsdk.md) - C++ API + `mavsdk_server`. `pip install mavsdk` 4.x is now a native binding with a different API, so old gRPC code needs `mavsdk-grpc`. See also [MAVSDK-Python](mavlink__mavsdk-python.md).
- [Crazyflie firmware](bitcraze__crazyflie-firmware.md) - onboard EKF/UKF with UWB, Lighthouse, flow and external pose. The README says LGPL-3.0 but `LICENSE.txt` is GPL-3.0. The flow deck diverges over dark floors (#617).
- [ros_gz](gazebosim__ros_gz.md) - `parameter_bridge` for NavSat/IMU/mag/clock (see [gz-sim](gazebosim__gz-sim.md)). One Gazebo release per ROS distro. NavSat has no covariance or fix-status control (#542, #695).
- [Stonefish](patrykcieslak__stonefish.md) - marine sim with IMU/INS/DVL/sonar. Linux + OpenGL 4.3 GPU. GPL-3.0. Library and ROS 2 package versions must match.
- [RTKLIB (upstream)](tomojitakasu__rtklib.md) - frozen since 2020, with open security reports #799 (RTCM 1033 OOB write) and #803. Prefer [RTKLIB demo5](rtklibexplorer__rtklib.md).

## Planning and mapping

- [OMPL](ompl__ompl.md) - `pip install ompl` 2.0.1 sampling planners, you supply the validity check. The 2.0 bindings dropped some planners (#1419), and ROS ships 1.7.0.
- [EGO-Planner-Swarm](zju-fast-lab__ego-planner-swarm.md) - multi-drone local planner + its own sim. Outputs `quadrotor_msgs/PositionCommand` with no PX4/MAVROS bridge. GPL-3.0.
- [TARE planner](caochao39__tare_planner.md) - CMU exploration planner => `/way_point`. Needs the CMU dev environment and targets ground vehicles. There is no LICENSE file (issue #27), so treat it as unlicensed.
- [grid_map](anybotics__grid_map.md) - 2.5D multi-layer maps. ROS 2 binaries exist in rosdistro despite the README. No PointCloud2 => GridMap conversion and no Nav2 plugin.
- [elevation_mapping_cupy](leggedrobotics__elevation_mapping_cupy.md) - GPU elevation/traversability => GridMap. `main` is ROS 1, so use `-b ros2` for Jazzy. Jetson issues are reported.
- [visualnav-transformer](robodhruv__visualnav-transformer.md) - GNM/ViNT/NoMaD image-route following, ROS 1. `navigate.py` effectively supports only `nomad`. No weights licence is stated.
