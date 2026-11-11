# ROS 2 real-time examples

`repo:ros-realtime/ros2-realtime-examples` - <https://github.com/ros-realtime/ros2-realtime-examples>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 87 | C++ | Apache-2.0 | 2024-01-29 | False | educational | medium |

Minimal recipes for real-time ROS 2: memory locking, thread priorities, CPU pinning and callback-group separation.

**Why it matters:** Short, copyable patterns for keeping the nav callback off the same thread as logging and image I/O.

**Build notes:** Last push 2024-01. Apply two recipes (mlockall, SCHED_FIFO on the estimator thread) and show the latency histogram before and after.

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `ros2`, `real-time`, `rt-preempt`, `threads`

**Domains:** multi

## Related

- same_org: [ROS 2 reference-system](../../catalog/repos/ros-realtime__reference-system.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [ROS 2 reference-system](../../catalog/repos/ros-realtime__reference-system.md) (same_org)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-09._
