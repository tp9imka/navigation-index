# Geometrically Constrained Trajectory Optimization for Multicopters

`res:wang-minco-gcopter-2021` - paper - <https://arxiv.org/abs/2103.00190>

**By:** Zhepei Wang, Xin Zhou, Chao Xu, Fei Gao - **Year:** 2021 - **Level:** advanced - **Access:** open

Introduces MINCO, a minimum-control trajectory class with linear-complexity parameterisation, and GCOPTER, which optimises trajectories inside safe-corridor polytopes with spatial and temporal deformation. Basis of the later ZJU planners.

## Key takeaways

- MINCO parameterises trajectories by waypoints and durations with linear-time gradients
- Constraints become penalties, so a generic unconstrained solver (L-BFGS) works
- Year is the arXiv date; journal version not checked here

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `minco`, `trajectory-optimisation`, `safe-corridor`, `multicopter`

## Related

- has_code: [GCOPTER](../../catalog/repos/zju-fast-lab__gcopter.md)
- uses: [EGO-Planner-v2 (Swarm Playground)](../../catalog/repos/zju-fast-lab__ego-planner-v2.md)

_Indexed by lane(s): guidance-planning_
