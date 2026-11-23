# LA-Planner

`repo:robotics-star-lab/la-planner` - <https://github.com/Robotics-STAR-Lab/LA-Planner>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 68 | C++ | GPL-3.0 | 2025-07-21 | False | research-prototype | low |

Localisation-aware quadrotor planner for unknown, feature-poor environments (IROS 2025): it allocates camera attention between exploration and feature-rich regions so VIO keeps tracking during navigation.

**Why it matters:** Recent, maintained example of planning that explicitly protects the estimator, which is the bridge between this hub's estimation focus and guidance.

**Build notes:** License GPL-3.0 (gh api). Last push 2025-07-21. Ubuntu 20.04 + ROS Noetic + nlopt 2.7.1 from source. Too much setup for 48h; useful as the citation for 'localisation-aware planning is current research'.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `perception-aware`, `localization-aware`, `feature-limited`, `quadrotor`, `gpl-3.0`

**Domains:** air

## Related

- alternative_to: [Fisher Information Field (rpg_information_field)](../../catalog/repos/uzh-rpg__rpg_information_field.md)
- alternative_to: [PANTHER](../../catalog/repos/mit-acl__panther.md)

## Referenced by

- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Fisher Information Field (rpg_information_field)](../../catalog/repos/uzh-rpg__rpg_information_field.md) (alternative_to)
- [Perception-aware Planning for Quadrotor Flight in Unknown and Feature-limited Environments](../../catalog/resources/yu-la-planner-perception-aware-2025.md) (has_code)

_Indexed by lane(s): guidance-planning_

_GitHub metadata fetched 2026-11-23._
