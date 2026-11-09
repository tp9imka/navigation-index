# PX4 ROS 2 Control Interface

`res:px4-ros2-control-interface-docs` - doc - <https://docs.px4.io/main/en/ros2/px4_ros2_control_interface.html>

**By:** PX4 / Dronecode - **Year:** 2026 - **Level:** intermediate - **Access:** open

Library that lets a ROS 2 process register its own flight modes and mode executors with PX4. PX4 presents them like built-in modes and keeps them inside its failsafe state machine and arming checks.

## Key takeaways

- A ROS 2 mode can replace a built-in PX4 mode, with the original as fallback
- Modes are integrated with PX4 failsafes and arming checks
- Parts are experimental; only some setpoint types are settled

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `px4`, `ros2`, `flight-modes`, `failsafe`

## Related

- has_code: [PX4 ROS 2 Interface Library](../../catalog/repos/auterion__px4-ros2-interface-lib.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
