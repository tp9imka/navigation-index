# Safe Quadrotor Navigation using Composite Control Barrier Functions

`res:harms-composite-cbf-icra2025` - paper - <https://arxiv.org/abs/2502.04101>

**By:** Marvin Harms, Martin Jacquet, Kostas Alexis - **Year:** 2025 - **Level:** advanced - **Access:** open

Origin of the NTNU composite CBF: one soft-min barrier built from all position constraints, here on a third-order model of the multirotor, with an analysis showing the infeasible set is negligible. Lidar quadrotor flights indoors and outdoors against naive and adversarial commands. ICRA 2025 per the arXiv comment. Abstract read only.

## Key takeaways

- The composite barrier scales to thousands of range points in one constraint
- The PX4-CBF ICUAS 2025 paper adapts it to acceleration-level control inside PX4
- Read as abstract only

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `control-barrier-function`, `composite-cbf`, `quadrotor`, `lidar`, `safety-filter`

## Related

- same_author: [Embedded Safe Reactive Navigation for Multirotors Systems using Control Barrier Functions](../../catalog/resources/misyats-px4-cbf-icuas2025.md)
- has_code: [composite_cbf](../../catalog/repos/ntnu-arl__composite_cbf.md)

_Indexed by lane(s): cbf-baselines_
