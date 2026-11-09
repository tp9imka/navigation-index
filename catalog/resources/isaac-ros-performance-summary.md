# Isaac ROS Performance Summary

`res:isaac-ros-performance-summary` - report - <https://nvidia-isaac-ros.github.io/performance/index.html>

**By:** NVIDIA - **Year:** 2026 - **Level:** intro - **Access:** open

NVIDIA's table of throughput and latency for Isaac ROS nodes and graphs per platform, including Jetson Orin Nano Super 8GB and AGX Orin, with latency measured at a 30 Hz input. Vendor numbers.

## Key takeaways

- Orin Nano Super 8GB: stereo disparity graph 1080p 61.5 fps, 19 ms at 30 Hz (vendor)
- Orin Nano Super 8GB: ESS DNN stereo 576p 34.8 fps, 30 ms at 30 Hz (vendor)
- AGX Orin: stereo disparity graph 1080p 117 fps, 9.3 ms (vendor)
- No cuVSLAM row on this page as of 2026-11-09

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `jetson`, `benchmark`, `latency`, `vendor-claim`, `isaac-ros`

## Related

- has_code: [Isaac ROS Benchmark](../../catalog/repos/nvidia-isaac-ros__isaac_ros_benchmark.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
