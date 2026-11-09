# realsense-ros

`repo:realsenseai/realsense-ros` - <https://github.com/realsenseai/realsense-ros>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | production | high |

ROS 2 wrapper for RealSense depth cameras (D400 series), publishing stereo IR, depth, colour and IMU topics. The ROS 1 wrapper and the T265 tracking camera support live on legacy branches.

**Why it matters:** The D435i / D455 are the common stereo + IMU input for VIO (OpenVINS, cuVSLAM) and depth for obstacle mapping on small indoor drones. Intel named them as the T265 successor when tracking cameras were discontinued.

**Hackathon notes:** License Apache-2.0 (gh api); repo moved from IntelRealSense to realsenseai, last push 2026-11. T265 is end of life (Intel EOL notice, sales stopped 2022), so do not plan on one unless the organisers hand it out. For VIO, turn the IR emitter off or use the IR stream with emitter off, otherwise the dot pattern corrupts feature tracking. IMU on D435i is unsynchronised with images by default; check unite_imu and timestamps.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `realsense`, `d435i`, `d455`, `t265-legacy`, `stereo`, `imu`, `apache-2.0`

**Domains:** air

## Related

- integrates_with: [OpenVINS](../../catalog/repos/rpng__open_vins.md)
- integrates_with: [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md)

## Referenced by

- [End-of-Life (EOL) Announcement for some Intel RealSense products](../../catalog/resources/intel-realsense-tracking-eol.md) (explains)

_Indexed by lane(s): close-area-localization_
