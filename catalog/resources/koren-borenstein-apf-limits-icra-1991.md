# Potential field methods and their inherent limitations for mobile robot navigation

`res:koren-borenstein-apf-limits-icra-1991` - paper - <https://doi.org/10.1109/ROBOT.1991.131810>

**By:** Yoram Koren, Johann Borenstein - **Year:** 1991 - **Level:** intro - **Access:** paywalled

Peer-reviewed (ICRA 1991). Lists the structural failures of potential fields: trap situations from local minima, no passage between closely spaced obstacles, oscillation near obstacles and in narrow passages.

## Key takeaways

- Local minima traps are inherent, not a tuning problem
- Closely spaced obstacles can block a gap the robot fits through
- Useful citation for why a global planner is needed

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `apf`, `local-minima`, `failure-modes`, `peer-reviewed`

## Related

- evaluates: [Real-Time Obstacle Avoidance for Manipulators and Mobile Robots](../../catalog/resources/khatib-potential-fields-ijrr-1986.md)
- same_author: [VFH+: reliable obstacle avoidance for fast mobile robots](../../catalog/resources/ulrich-borenstein-vfhplus-icra-1998.md)

## Referenced by

- [Real-Time Obstacle Avoidance for Manipulators and Mobile Robots](../../catalog/resources/khatib-potential-fields-ijrr-1986.md) (explains)
- [Close-area arena: seeded 2.5D A=>B simulator, published drone interface, truth scorer](../../catalog/samples/close-area-arena.md) (explains)
- [Close-area local planners: DWA (Nav2-style dynamic window) and Bug2 / TangentBug, range sensor only, next to APF and VFH+ on 72-beam and Crazyflie-like 4-beam fans](../../catalog/samples/close-area-planner-dwa-bug.md) (explains)
- [Close-area reactive planners: APF with wall-follow escape and VFH+, range sensor only, 72-beam vs Crazyflie-like 4-beam fan](../../catalog/samples/close-area-planner-reactive.md) (explains)

_Indexed by lane(s): close-area-planning_
