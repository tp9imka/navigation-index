# EGO-Planner: An ESDF-free Gradient-based Local Planner for Quadrotors

`res:zhou-ego-planner-paper` - paper - <https://arxiv.org/abs/2008.08835>

**By:** Xin Zhou, Zhepei Wang, Hongkai Ye, Chao Xu, Fei Gao - **Year:** 2020 - **Level:** advanced - **Access:** open

Introduces a local planner that avoids building a full Euclidean signed distance field, computing collision penalties only from obstacles the trajectory intersects, cutting onboard compute.

## Key takeaways

- ESDF-free collision cost reduces mapping overhead
- Fits small onboard computers for agile flight

**Concepts:** [Path and motion planning](../concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../concepts/obstacle-avoidance.md)

**Tags:** `quadrotor`, `b-spline`

## Related

- has_code: [EGO-Planner](../repos/zju-fast-lab__ego-planner.md)

_Indexed by lane(s): planning-gis-c2_
