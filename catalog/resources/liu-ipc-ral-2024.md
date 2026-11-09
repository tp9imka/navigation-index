# Integrated Planning and Control for Quadrotor Navigation in Presence of Suddenly Appearing Objects and Disturbances

`res:liu-ipc-ral-2024` - paper - <https://doi.org/10.1109/LRA.2023.3311358>

**By:** Wenyi Liu, Yunfan Ren, Fu Zhang - **Year:** 2024 - **Level:** advanced - **Access:** paywalled

Peer-reviewed (IEEE RA-L). A light front end builds a safe flight corridor and a 100 Hz linear MPC on jerk with corridor constraints drives the vehicle, converting the output to body rates and thrust through differential flatness.

## Key takeaways

- Folding planning into a fast MPC loop reacts to sudden obstacles
- Corridor half-planes become linear MPC constraints
- Also rejects disturbances that break plan-then-track pipelines

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md)

**Tags:** `mpc`, `safe-flight-corridor`, `peer-reviewed`

## Related

- has_code: [IPC (Integrated Planning and Control)](../../catalog/repos/hku-mars__ipc.md)

## Referenced by

- [Bubble Planner: Planning High-speed Smooth Quadrotor Trajectories using Receding Corridors](../../catalog/resources/ren-bubble-planner-2022.md) (same_author)

_Indexed by lane(s): close-area-planning_
