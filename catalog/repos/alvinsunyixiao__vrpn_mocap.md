# vrpn_mocap

`repo:alvinsunyixiao/vrpn_mocap` - <https://github.com/alvinsunyixiao/vrpn_mocap>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | active-research | medium |

ROS 2 VRPN client that turns motion-capture rigid bodies (VICON, OptiTrack and other VRPN devices) into pose topics.

**Why it matters:** If the venue has motion capture, this is the shortest path from mocap to a ROS 2 pose that MAVROS can forward to EKF2 / EKF3 as external vision, which turns localization into a solved problem and frees time for planning.

**Hackathon notes:** License MIT (gh api), last push 2026-09, CI for Humble through Rolling. Remap the pose to /mavros/vision_pose/pose, and convert ENU to NED once (MAVROS does it for vision_pose). Mocap latency is low but check EKF2_EV_DELAY anyway.

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `mocap`, `vicon`, `optitrack`, `vrpn`, `ros2`, `mit`

**Domains:** air

## Related

- integrates_with: [MAVROS](../../catalog/repos/mavlink__mavros.md)
- alternative_to: [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md)

_Indexed by lane(s): close-area-localization_
