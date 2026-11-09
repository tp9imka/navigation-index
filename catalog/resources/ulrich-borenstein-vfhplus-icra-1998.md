# VFH+: reliable obstacle avoidance for fast mobile robots

`res:ulrich-borenstein-vfhplus-icra-1998` - paper - <https://doi.org/10.1109/ROBOT.1998.677362>

**By:** Iwan Ulrich, Johann Borenstein - **Year:** 1998 - **Level:** intro - **Access:** paywalled

Peer-reviewed (ICRA 1998). Builds a polar histogram of obstacle density around the robot, enlarges obstacles by the robot radius and picks a free direction close to the goal heading, with hysteresis to stop flicker.

## Key takeaways

- Sector histogram from range data, no map needed
- Robot-size enlargement and hysteresis fix the original VFH
- Still a local method: dead ends need a global planner

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `vfh`, `reactive`, `baseline`, `peer-reviewed`

## Related

- explains: [Collision Prevention (PX4 User Guide)](../../catalog/resources/px4-collision-prevention-docs.md)

## Referenced by

- [Potential field methods and their inherent limitations for mobile robot navigation](../../catalog/resources/koren-borenstein-apf-limits-icra-1991.md) (same_author)

_Indexed by lane(s): close-area-planning_
