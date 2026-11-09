# Planning Dynamically Feasible Trajectories for Quadrotors Using Safe Flight Corridors in 3-D Complex Environments

`res:liu-sfc-quadrotor-ral-2017` - paper - <https://doi.org/10.1109/LRA.2017.2663526>

**By:** Sikang Liu, Michael Watterson, Kartik Mohta, Ke Sun, Subhrajit Bhattacharya, Camillo J. Taylor, Vijay Kumar - **Year:** 2017 - **Level:** intermediate - **Access:** paywalled

Peer-reviewed (IEEE RA-L). Defines the safe flight corridor pipeline: 3D JPS path, convex polytopes grown around it, then a QP for a polynomial trajectory constrained to stay in the polytopes.

## Key takeaways

- Grid search => convex corridor => QP is a solid, explainable pipeline
- Corridors make collision constraints linear
- 3D JPS keeps the front end fast

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `safe-flight-corridor`, `jps`, `qp`, `peer-reviewed`

## Related

- has_code: [jps3d (MRSL Jump Point Search)](../../catalog/repos/kumarrobotics__jps3d.md)
- has_code: [DecompUtil](../../catalog/repos/sikang__decomputil.md)
- cites: [Online Graph Pruning for Pathfinding On Grid Maps](../../catalog/resources/harabor-grastien-jps-aaai-2011.md)

_Indexed by lane(s): close-area-planning_
