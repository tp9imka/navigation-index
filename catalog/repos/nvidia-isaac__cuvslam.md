# cuVSLAM

`repo:nvidia-isaac/cuvslam` - <https://github.com/nvidia-isaac/cuVSLAM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,899 | C++ | NOASSERTION | 2026-11-05 | False | production | high |

NVIDIA's CUDA-accelerated visual odometry and SLAM library supporting mono to multi-camera rigs with optional IMU, with Python bindings.

**Why it matters:** The engine behind Isaac ROS Visual SLAM, now usable directly from Python.

**Hackathon notes:** pip install the Python wheel on Jetson or x86 with CUDA; examples for EuRoC/KITTI.

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Visual SLAM](../concepts/visual-slam.md), [Onboard / edge AI perception](../concepts/edge-ai.md)

**Tags:** `cuda`, `jetson`, `visual-odometry`, `python`

**Domains:** air, ground

## Related

- integrates_with: [Isaac ROS Visual SLAM](../repos/nvidia-isaac-ros__isaac_ros_visual_slam.md)
- integrates_with: [cuVSLAM: CUDA accelerated visual odometry and mapping](../resources/cuvslam-2025.md)

## Referenced by

- [Isaac ROS Visual SLAM](../repos/nvidia-isaac-ros__isaac_ros_visual_slam.md) (depends_on)
- [cuVSLAM: CUDA accelerated visual odometry and mapping](../resources/cuvslam-2025.md) (has_code)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
