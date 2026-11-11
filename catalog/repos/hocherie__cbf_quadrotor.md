# cbf_quadrotor

`repo:hocherie/cbf_quadrotor` - <https://github.com/hocherie/cbf_quadrotor>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | educational | high |

Python exponential CBF for a simple 3D quadrotor model with cascaded PID, single-obstacle and two-robot examples; lecture slides from the AirLab 2020 summer school.

**Why it matters:** Smallest working Python CBF-on-quadrotor to start a 48h safety-filter build.

**Build notes:** License MIT (gh api), last push 2022-12-24. README pins Python 3.7.2 via pyenv; expect to update dependencies. Use for the barrier math; swap in RotorPy or a double integrator for dynamics.

**Concepts:** [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `control-barrier-function`, `python`, `quadrotor`, `mit`

**Domains:** air

## Related

- alternative_to: [RotorPy](../../catalog/repos/spencerfolk__rotorpy.md)

_Indexed by lane(s): close-area-innovation_
