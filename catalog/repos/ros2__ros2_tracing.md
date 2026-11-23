# ros2_tracing

`repo:ros2/ros2_tracing` - <https://github.com/ros2/ros2_tracing>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 273 | Python | Apache-2.0 | 2026-11-22 | False | production | high |

LTTng-based instrumentation for ROS 2: tracepoints in rclcpp/rcl/rmw plus tools to record and analyse callback durations and message flow end to end.

**Why it matters:** The way to measure, not guess, the camera-to-setpoint latency of a ROS 2 nav pipeline. That number goes straight into EKF2_EV_DELAY / VISO_DELAY_MS and onto the latency-budget slide.

**Build notes:** Linux only (LTTng kernel/userspace packages). Trace a 60 s replay, then report p50/p99 callback latency per node. Pairs with tracetools_analysis notebooks.

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `ros2`, `tracing`, `lttng`, `latency`, `profiling`

**Domains:** multi

## Related

- integrates_with: [ROS 2 reference-system](../../catalog/repos/ros-realtime__reference-system.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [ROS 2 reference-system](../../catalog/repos/ros-realtime__reference-system.md) (integrates_with)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-23._
