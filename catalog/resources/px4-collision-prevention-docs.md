# Collision Prevention (PX4 User Guide)

`res:px4-collision-prevention-docs` - doc - <https://docs.px4.io/main/en/computer_vision/collision_prevention.html>

**By:** PX4 / Dronecode - **Year:** 2026 - **Level:** intro - **Access:** open

Docs. PX4's built-in collision prevention for multicopters in acceleration-based Position mode. It limits velocity toward obstacles seen by range sensors or OBSTACLE_DISTANCE MAVLink messages and can bend the commanded direction by up to CP_GUIDE_ANG. It does not plan a route.

## Key takeaways

- Position mode only, not Mission or Offboard
- Directions without sensor data are blocked by default (CP_GO_NO_DATA = 0)
- Missing range data for 0.5 s zeroes xy motion, 5 s triggers Hold

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `px4`, `collision-prevention`, `obstacle-distance`, `docs`

## Related

- explains: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

## Referenced by

- [VOXL Vision Obstacle Avoidance (VOA)](../../catalog/resources/modalai-voxl-voa-docs.md) (uses)
- [VFH+: reliable obstacle avoidance for fast mobile robots](../../catalog/resources/ulrich-borenstein-vfhplus-icra-1998.md) (explains)

_Indexed by lane(s): close-area-planning_
