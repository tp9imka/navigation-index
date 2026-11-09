# PAMPC: Perception-Aware Model Predictive Control for Quadrotors

`res:falanga-pampc-2018` - paper - <https://arxiv.org/abs/1804.04811>

**By:** Davide Falanga, Philipp Foehn, Peng Lu, Davide Scaramuzza - **Year:** 2018 - **Level:** advanced - **Access:** open

Adds perception objectives (keep a point of interest visible, low image-plane velocity) to a quadrotor NMPC cost, so the controller trades tracking accuracy against what the camera sees.

## Key takeaways

- Perception terms live in the MPC cost, not in a separate planner
- Under-actuation means attitude, and so camera pointing, is coupled to translation
- Pattern transfers to keeping a nadir camera on matchable terrain

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `perception-aware`, `nmpc`, `quadrotor`

## Related

- has_code: [rpg_mpc (PAMPC)](../../catalog/repos/uzh-rpg__rpg_mpc.md)

_Indexed by lane(s): guidance-planning_
