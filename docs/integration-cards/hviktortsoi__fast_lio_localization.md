# FAST-LIO-LOCALIZATION - integration card
<!-- about: repo:hviktortsoi/fast_lio_localization -->
Relocalization in a prebuilt PCD map: FAST-LIO odometry at full rate plus a 0.5 Hz Open3D ICP scan-to-map matcher that publishes the map => odom correction; a small, readable example of "map once, localize later" for LiDAR, but stuck on ROS 1 and Python 2.7.

| | |
|---|---|
| Install | No releases. ROS 1 catkin: install FAST-LIO prerequisites and `livox_ros_driver` (source it before building), then `cd ~/catkin_ws/src && git clone https://github.com/HViktorTsoi/FAST_LIO_LOCALIZATION.git && cd FAST_LIO_LOCALIZATION && git submodule update --init && cd ../.. && catkin_make`. Python side (README): Python 2.7, `sudo apt install ros-$ROS_DISTRO-ros-numpy`, `pip install pyrsistent==0.15` then `pip install open3d==0.9`. Submodule: `include/ikd-Tree` (hku-mars/ikd-Tree, branch `fast_lio`). |
| Runs on | Linux, ROS 1 only (README instructions target Melodic-era Python 2.7). CPU only. Open3D 0.9 has no arm64 wheels in practice (open issue #33 "Installation of open3d based on arm64 architecture"). No ROS 2 port in this repo (open issues #22, #28, #54). |
| Inputs | Same LiDAR/IMU topics as FAST-LIO, configured by `config/*.yaml` (Avia, Horizon, Ouster64, Velodyne launch files). Map: a PCD file passed as `map:=`, published once on `/map` by `pcl_ros pcd_to_pointcloud` in frame `map`. Initial pose: `/initialpose` (geometry_msgs/PoseWithCovarianceStamped), from RViz "2D Pose Estimate" or `publish_initial_pose.py x y z yaw pitch roll`. |
| Outputs | `/localization` (nav_msgs/Odometry, 50 Hz, map-frame pose fused from `/Odometry` and `/map_to_odom`), `/map_to_odom` (nav_msgs/Odometry, at global-localization rate), TF `map` => `camera_init` (FAST-LIO odom frame), debug clouds `/cur_scan_in_map`, `/submap`. FAST-LIO's own `/Odometry` and `/cloud_registered` continue to publish. |
| Key API / entry points | `roslaunch fast_lio_localization localization_avia.launch map:=/path/map.pcd` (also `localization_horizon.launch`, `localization_ouster64.launch`, `localization_velodyne.launch`). Nodes: `fastlio_mapping` (C++ FAST-LIO), `scripts/global_localization.py` (Open3D multiscale ICP: `registration_at_scale`, `global_localization`, `crop_global_map_in_FOV`), `scripts/transform_fusion.py`, `scripts/publish_initial_pose.py`. Tunables are module-level constants in `global_localization.py`: `MAP_VOXEL_SIZE=0.4`, `SCAN_VOXEL_SIZE=0.1`, `FREQ_LOCALIZATION=0.5`, `LOCALIZATION_TH=0.95` (ICP fitness gate), `FOV=1.6` rad, `FOV_FAR=150` m. |
| Time to first result | Estimate: half a day on an old Ubuntu/Melodic image (or Docker) with the README's underground-garage bag and map; Open3D 0.9 on Python 2.7 is the slow part. |
| License | LICENSE file: GPL-2.0 (inherited from FAST-LIO). Sample bag and map on Google Drive / Baidu with no stated licence. |

## Minimal usage
Not run. From README.

```sh
roslaunch fast_lio_localization localization_avia.launch map:=/path/to/map.pcd
# wait 3-5 s for the map to appear in RViz
rosbag play localization_test_scene_1.bag
rosrun fast_lio_localization publish_initial_pose.py 14.5 -7.5 0 -0.25 0 0
```

`14.5 -7.5 0 -0.25 0 0` is x y z yaw pitch roll in the map frame, the README's rough guess for the sample bag. Keep the sensor still (or pause the bag after ~0.5 s) until the first match succeeds.

## Wiring it into a nav stack
- Map source: a PCD from [LIO-SAM](./tixiaoshan__lio-sam.md) (`/lio_sam/save_map`) or FAST-LIO's `pcd_save_enable` ([FAST-LIO card](./hku-mars__fast_lio.md)).
- `/localization` => [MAVROS](./mavlink__mavros.md) `odometry/out` or [vision_to_mavros](./thien94__vision_to_mavros.md) for an autopilot; or the map => odom TF straight into ROS 1 move_base.
- Initial pose from GNSS or a visual place-recognition step instead of RViz: publish it on `/initialpose`.
- To port the idea to ROS 2, replace the Open3D ICP with [small_gicp](./koide3__small_gicp.md) GICP/VGICP; the node structure (cropped submap, fitness gate, map => odom publisher) carries over.

## Gotchas
- Python 2.7 + Open3D 0.9 is the main blocker on any modern OS (open issue #43 "Did anyone install open3d 0.9 successfully?"). Expect to patch `import thread` and print statements for Python 3 / Noetic (open issue #39 "update for ROS noetic and Livox Mid 360"). The map => `camera_init` TF is stamped with `rospy.Time.now()`, not the scan time.
- No relocalization from scratch: it needs a rough initial pose and only refines it. If ICP fitness stays below `LOCALIZATION_TH` it keeps waiting for a new `/initialpose`.
- `FOV=1.6` rad is tuned for Livox Avia; set it near 2*pi for 360-degree spinning LiDARs or the submap crop drops most of the map.
- README asks Livox `publish_freq` at 10 Hz so each scan has enough points for matching.
- README TODO admits the published odometry/TF timestamps are not yet sorted out, and the global fix is not fused into the FAST-LIO state (it only shifts map => odom). Last commit 2023-05.

## Alternatives
- [RTAB-Map ROS](./introlab__rtabmap_ros.md) `lidar3d.launch.py localization:=true` - maintained ROS 2 LiDAR mapping plus localization with a database, loop-closure-based relocalization.
- [LIO-SAM](./tixiaoshan__lio-sam.md) or [GLIM](../../catalog/repos/koide3__glim.md) - if you need to build the map in the same session.
- [hdl_graph_slam](../../catalog/repos/koide3__hdl_graph_slam.md) - the same author family as small_gicp for NDT/GICP-based mapping on ROS.

Sources: `README.md`, `LICENSE`, `.gitmodules`, `launch/localization_avia.launch`, `launch/` and `scripts/` listings, `scripts/global_localization.py`, `scripts/transform_fusion.py`, `scripts/publish_initial_pose.py`, issues #22 #28 #33 #39 #43 #54 (github.com/HViktorTsoi/FAST_LIO_LOCALIZATION).
