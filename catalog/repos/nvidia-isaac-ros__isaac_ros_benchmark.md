# Isaac ROS Benchmark

`repo:nvidia-isaac-ros/isaac_ros_benchmark` - <https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_benchmark>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 38 | Python | Apache-2.0 | 2026-09-22 | False | production | medium |

ros2_benchmark-based scripts NVIDIA uses to produce the Isaac ROS performance tables (throughput and latency per node or graph per Jetson / dGPU platform).

**Why it matters:** Source of the cited Orin Nano Super numbers for stereo disparity and AprilTag; the same harness can measure your own node at a fixed input rate.

**Build notes:** Needs the Isaac ROS dev container. Useful for 'measured at 30 Hz input' latency the same way NVIDIA reports it.

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `jetson`, `ros2`, `benchmark`, `latency`, `isaac-ros`

**Domains:** multi

## Related

- evaluated_on: [Isaac ROS Visual SLAM](../../catalog/repos/nvidia-isaac-ros__isaac_ros_visual_slam.md)
- alternative_to: [Jetson Benchmarks](../../catalog/repos/nvidia-ai-iot__jetson_benchmarks.md)

## Referenced by

- [Jetson Benchmarks](../../catalog/repos/nvidia-ai-iot__jetson_benchmarks.md) (alternative_to)
- [Isaac ROS Performance Summary](../../catalog/resources/isaac-ros-performance-summary.md) (has_code)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-16._
