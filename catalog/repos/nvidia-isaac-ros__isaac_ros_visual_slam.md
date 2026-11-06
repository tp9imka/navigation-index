# Isaac ROS Visual SLAM

`repo:nvidia-isaac-ros/isaac_ros_visual_slam` - <https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,493 | C++ | Apache-2.0 | 2026-09-22 | False | production | high |

ROS 2 package wrapping NVIDIA's GPU-accelerated cuVSLAM for stereo visual(-inertial) odometry and SLAM on Jetson and x86 GPUs.

**Why it matters:** Real-time VIO on embedded Jetson hardware with low CPU load, a practical GNSS-denied odometry source for drones and UGVs.

**Hackathon notes:** Use the Isaac ROS dev container; RealSense or ZED stereo works out of the box. Jetson Orin recommended.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [nvidia-isaac-ros__isaac_ros_visual_slam](../../docs/integration-cards/nvidia-isaac-ros__isaac_ros_visual_slam.md) (integration-cards)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Visual SLAM](../../catalog/concepts/visual-slam.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `cuvslam`, `jetson`, `gpu`, `stereo`, `ros2`

**Domains:** air, ground

## Related

- depends_on: [cuVSLAM](../../catalog/repos/nvidia-isaac__cuvslam.md)
- integrates_with: [Isaac ROS nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md)
- integrates_with: [Isaac ROS Visual SLAM documentation](../../catalog/resources/isaac-ros-visual-slam-docs.md)

## Referenced by

- [Isaac ROS nvblox](../../catalog/repos/nvidia-isaac-ros__isaac_ros_nvblox.md) (integrates_with)
- [cuVSLAM](../../catalog/repos/nvidia-isaac__cuvslam.md) (integrates_with)
- [cuVSLAM: CUDA accelerated visual odometry and mapping](../../catalog/resources/cuvslam-2025.md) (has_code)
- [Isaac ROS Visual SLAM documentation](../../catalog/resources/isaac-ros-visual-slam-docs.md) (has_code)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
