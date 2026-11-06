# ROSflight firmware

`repo:rosflight/rosflight_firmware` - <https://github.com/rosflight/rosflight_firmware>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 157 | C | BSD-3-Clause | 2026-08-27 | False | active-research | medium |

Lean research autopilot (BYU) that keeps only attitude estimation and low-level control on the flight board and pushes everything else to a ROS companion.

**Why it matters:** Clean split between embedded and onboard autonomy; good for teams who want full control of the estimator on the companion.

**Hackathon notes:** Use with rosflight_ros_pkgs; includes a simulator so hardware is optional.

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `byu`, `research`, `fixed-wing`, `multirotor`

**Domains:** air

## Related

- integrates_with: [ROSflight ROS packages](../../catalog/repos/rosflight__rosflight_ros_pkgs.md)
- alternative_to: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

## Referenced by

- [ROSflight ROS packages](../../catalog/repos/rosflight__rosflight_ros_pkgs.md) (integrates_with)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
