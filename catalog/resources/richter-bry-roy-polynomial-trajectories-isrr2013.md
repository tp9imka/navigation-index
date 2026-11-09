# Polynomial Trajectory Planning for Aggressive Quadrotor Flight in Dense Indoor Environments

`res:richter-bry-roy-polynomial-trajectories-isrr2013` - paper - <https://groups.csail.mit.edu/rrg/papers/Richter_ISRR13.pdf>

**By:** Charles Richter, Adam Bry, Nicholas Roy - **Year:** 2013 - **Level:** intermediate - **Access:** open

Plans a geometric path first (RRT*), then fits jointly optimised polynomial segments through it as an unconstrained, numerically stable QP. Removes the need to model the full dynamics in the sampling planner.

## Key takeaways

- Split planning: kinematic path search => polynomial smoothing
- Unconstrained QP formulation stays stable for high polynomial orders
- Segment time allocation is the knob that decides feasibility

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md)

**Tags:** `minimum-snap`, `polynomial`, `quadrotor`, `rrt-star`

## Related

- has_code: [mav_trajectory_generation](../../catalog/repos/ethz-asl__mav_trajectory_generation.md)

_Indexed by lane(s): guidance-planning_
