# Crazyflow

`repo:learnsyslab/crazyflow` - <https://github.com/learnsyslab/crazyflow>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | active-research | medium |

JAX-based batched, differentiable quadrotor simulator from TUM LSY with first-principles and identified Crazyflie models, plus MuJoCo/MJX rendering, raycasting and contacts.

**Why it matters:** Light, pip-installable Crazyflie sim with sim-to-real tuned dynamics. Runs on CPU, so usable on a Mac.

**Hackathon notes:** MIT. CPU wheel is py3-none-any; the GPU extra is Linux x86-64 CUDA only. Lower-level than gym-pybullet-drones; use it through lsy_drone_racing unless you need batched rollouts.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `jax`, `crazyflie`, `differentiable`, `mujoco`, `mit`

**Domains:** air

## Related

- alternative_to: [gym-pybullet-drones](../../catalog/repos/learnsyslab__gym-pybullet-drones.md)
- alternative_to: [RotorPy](../../catalog/repos/spencerfolk__rotorpy.md)

## Referenced by

- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)
- [MuJoCo Menagerie](../../catalog/repos/google-deepmind__mujoco_menagerie.md) (integrates_with)
- [LSY Autonomous Drone Racing](../../catalog/repos/learnsyslab__lsy_drone_racing.md) (depends_on)

_Indexed by lane(s): close-area-sims_
