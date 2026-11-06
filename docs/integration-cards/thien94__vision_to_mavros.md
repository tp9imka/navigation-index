# vision_to_mavros - integration card
<!-- about: repo:thien94/vision_to_mavros -->
One-line: the reference glue (ROS 1 node + standalone pymavlink scripts) that turns a VIO/SLAM/AprilTag pose into ArduPilot `VISION_POSITION_ESTIMATE`/`VISION_SPEED_ESTIMATE`, including the frame rotations, origin setting and camera-orientation handling that teams usually get wrong.

| | |
|---|---|
| Install | ROS 1: clone into a catkin workspace (`catkin build vision_to_mavros`) next to `mavros` and `realsense2_camera`. Non-ROS: `pip install pymavlink numpy transformations apscheduler pyrealsense2` and run `scripts/t265_to_mavlink.py`. No releases. |
| Runs on | ROS 1 (Kinetic/Melodic/Noetic era; last push 2022-10). Scripts run on any Linux with Python 3 and a RealSense; written for RPi 3B/4 companions. |
| Inputs | ROS node: `/tf` with `source_frame_id` (camera) in `target_frame_id` (world); params `roll_cam`, `pitch_cam`, `yaw_cam`, `gamma_world` (radians), `output_rate`. Script: RealSense T265 pose stream (or adapt to any pose source), `--connect`, `--baudrate`, `--camera_orientation`, message rate flags. |
| Outputs | ROS: `/mavros/vision_pose/pose` (`geometry_msgs/PoseStamped`, ENU, via MAVROS), `/body_frame/path` for rviz. Script: MAVLink `VISION_POSITION_ESTIMATE`, `VISION_POSITION_DELTA`, `VISION_SPEED_ESTIMATE`, `SET_GPS_GLOBAL_ORIGIN`, `SET_HOME_POSITION`, `TIMESYNC`, `STATUSTEXT`. |
| Key API / entry points | `src/vision_to_mavros.cpp` (node `vision_to_mavros_node`); launch files `t265_tf_to_mavros.launch`, `t265_all_nodes.launch`, `t265_downfacing_tf_to_mavros.launch`, `apriltags_to_mavros.launch`, `tf_to_mavros.launch`, `t265_precland.launch`; scripts `t265_to_mavlink.py`, `d4xx_to_mavlink.py` (obstacle distances), `t265_precland_apriltags.py`, `set_origin.py`, `rs_to_mavlink.py`. |
| Time to first result | Estimate: 1-2 h to adapt `t265_to_mavlink.py` to a non-T265 pose source and see ArduPilot SITL accept it. Assumes ArduPilot SITL with `VISO_TYPE=1` and a pose stream already available in Python. |
| License | GPL-3.0. |

## Minimal usage
ROS 1 path from README (three terminals). Not run.

```bash
roslaunch realsense2_camera rs_t265.launch
roslaunch mavros apm.launch fcu_url:=<your fcu url>
roslaunch vision_to_mavros t265_tf_to_mavros.launch
rostopic hz /mavros/vision_pose/pose     # README expects ~30 Hz
```
Hardware-free path: copy the MAVLink half of `t265_to_mavlink.py` (heartbeat as `MAV_TYPE_ONBOARD_CONTROLLER`, `set_gps_global_origin_send`, `vision_position_estimate_send` at the configured rate) and drive it from your own VIO output or from SITL ground truth.

## Wiring it into a nav stack
- Upstream pose producers: [OpenVINS](./rpng__open_vins.md), [ORB-SLAM3](./uz-slamlab__orb_slam3.md), [RTAB-Map](./introlab__rtabmap.md), AprilTag detections.
- Downstream: [MAVROS](./mavlink__mavros.md) => [ArduPilot](./ardupilot__ardupilot.md) (`VISO_TYPE=1`, `EK3_SRC1_POSXY/VELXY/POSZ/VELZ=6`, `EK3_SRC1_YAW=6` if the VIO yaw is trusted). The non-ROS script talks MAVLink directly, so it can sit behind [mavlink-router](./mavlink-router__mavlink-router.md).
- For PX4 the same frame logic applies, but feed `ODOMETRY` or ROS 2 `/fmu/in/vehicle_visual_odometry` instead ([PX4](./px4__px4-autopilot.md)).
- Catalog: [vision_to_mavros page](../../catalog/repos/thien94__vision_to_mavros.md).

## Gotchas
- Unmaintained since 2022 and ROS 1 only. For ROS 2, port the node logic or use MAVROS `vision_pose` with `tf/listen: true` directly.
- Intel RealSense T265 is discontinued; treat the T265 scripts as templates.
- Origin: without `set_origin.py` (or the script's `SET_GPS_GLOBAL_ORIGIN`), ArduPilot never gets a global position; open issue #67 reports `set_origin.py` failing to set home. #64 (pose not published, closed) and open #65-#66 (ZED Mini, D435i/T265 combos) are camera-specific setup questions.
- Angle conventions (`roll_cam`, `pitch_cam`, `yaw_cam`, `gamma_world`) are applied in a fixed order; a wrong sign shows up as the vehicle drifting in the wrong axis when you move it by hand. Test by hand before arming.
- GPL-3.0.

## Alternatives
- [MAVROS](./mavlink__mavros.md) `vision_pose_estimate` plugin alone with TF listen, when frames are already REP 103.
- [px4-ros2-interface-lib](./auterion__px4-ros2-interface-lib.md) `LocalPositionMeasurementInterface` for PX4 + ROS 2.

Sources: `README.md`, repo tree, `scripts/t265_to_mavlink.py` (argparse flags and `*_send` calls), issue search (#64-#67).
