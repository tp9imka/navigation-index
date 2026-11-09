# IPC (Integrated Planning and Control)

`repo:hku-mars/ipc` - <https://github.com/hku-mars/IPC>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C++ | ? | ? | ? | research-prototype | low |

Quadrotor navigation that merges planning and control: a light A*-style front end builds a safe flight corridor and a 100 Hz linear MPC tracks toward the goal with the corridor as hard constraints, outputting body rates and thrust. Ships a simulator.

**Why it matters:** The working example of 'MPC with obstacle constraints' for multirotors. Reacting inside the controller loop handles suddenly appearing obstacles and disturbances better than replanning at a few Hz.

**Hackathon notes:** No license file in the repo (gh api shows none): treat as read-only. Last push 2024-07-19. Ubuntu 18.04-20.04 with ROS 1. Re-implement the idea (corridor half-planes as linear MPC constraints) in OSQP or acados if the team wants an MPC story.

**Concepts:** [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `mpc`, `safe-flight-corridor`, `lidar`, `ros1`, `c++`, `no-license`

**Domains:** air

## Related

- same_org: [SUPER](../../catalog/repos/hku-mars__super.md)
- alternative_to: [DecompUtil](../../catalog/repos/sikang__decomputil.md)
- alternative_to: [acados](../../catalog/repos/acados__acados.md)

## Referenced by

- [SUPER](../../catalog/repos/hku-mars__super.md) (same_org)
- [Integrated Planning and Control for Quadrotor Navigation in Presence of Suddenly Appearing Objects and Disturbances](../../catalog/resources/liu-ipc-ral-2024.md) (has_code)

_Indexed by lane(s): close-area-planning_
