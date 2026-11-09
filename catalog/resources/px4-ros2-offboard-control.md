# PX4 ROS 2 Offboard Control Example

`res:px4-ros2-offboard-control` - doc - <https://docs.px4.io/main/en/ros2/offboard_control.html>

**By:** PX4 / Dronecode - **Year:** 2026 - **Level:** intro - **Access:** open

Walkthrough of driving PX4 from a ROS 2 node in offboard mode: OffboardControlMode heartbeat, TrajectorySetpoint messages, arming and mode switching via px4_ros_com.

## Key takeaways

- Offboard needs a continuous OffboardControlMode stream or PX4 falls back
- Choose the setpoint level (position, velocity, rates) to match your guidance layer
- This is the integration point for a custom MPC or trajectory tracker

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `px4`, `offboard`, `ros2`, `setpoints`

## Related

- explains: [px4_ros_com](../../catalog/repos/px4__px4_ros_com.md)
- uses: [PX4 ROS 2 Interface Library](../../catalog/repos/auterion__px4-ros2-interface-lib.md)

_Indexed by lane(s): guidance-planning_
