# composite_cbf

`repo:ntnu-arl/composite_cbf` - <https://github.com/ntnu-arl/composite_cbf>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 15 | C++ | BSD-3-Clause | 2026-05-26 | False | active-research | medium |

ROS implementation of the composite CBF safety filter that combines many range points into one barrier.

**Why it matters:** Companion-computer version of PX4-CBF; easier to run next to a planner over MAVROS.

**Build notes:** License BSD-3-Clause (gh api), last push 2026-05-26. ROS-based; read the barrier construction and port the math to Python for the sim.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `control-barrier-function`, `ros`, `safety-filter`, `bsd-3`

**Domains:** air

## Related

- same_org: [PX4-CBF](../../catalog/repos/ntnu-arl__px4-cbf.md)

## Referenced by

- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [cbf_pc_selector](../../catalog/repos/ntnu-arl__cbf_pc_selector.md) (integrates_with)
- [PX4-Autopilot (NTNU fork, cbf branch)](../../catalog/repos/ntnu-arl__px4-autopilot.md) (same_org)
- [PX4-CBF](../../catalog/repos/ntnu-arl__px4-cbf.md) (same_org)
- [Safe Quadrotor Navigation using Composite Control Barrier Functions](../../catalog/resources/harms-composite-cbf-icra2025.md) (has_code)
- [Embedded Safe Reactive Navigation for Multirotors Systems using Control Barrier Functions](../../catalog/resources/misyats-px4-cbf-icuas2025.md) (has_code)

_Indexed by lane(s): close-area-innovation_

_GitHub metadata fetched 2026-11-23._
