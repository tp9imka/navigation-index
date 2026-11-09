# LSY Autonomous Drone Racing

`repo:learnsyslab/lsy_drone_racing` - <https://github.com/learnsyslab/lsy_drone_racing>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | active-research | high |

TUM LSY course project for autonomous Crazyflie racing through gates and around pole obstacles, in simulation (crazyflow) and on real hardware with Vicon. Four TOML difficulty levels add randomized inertia, obstacle and gate positions, and random tracks.

**Why it matters:** Closest open analogue to an A=>B-through-obstacles task with a scoring harness. Exact obstacle positions are only revealed within 0.7 m, which forces replanning.

**Hackathon notes:** MIT, active (push 2026-11). Pure-Python on CPU, so it should run on Apple Silicon (not run here). Copy the level-2 config idea for your own eval: randomize obstacles per episode and report success rate.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Path and motion planning](../../catalog/concepts/path-planning.md), [Obstacle avoidance and collision avoidance](../../catalog/concepts/obstacle-avoidance.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `crazyflie`, `drone-racing`, `gymnasium`, `sim2real`, `mujoco`, `mit`

**Domains:** air

## Related

- depends_on: [Crazyflow](../../catalog/repos/learnsyslab__crazyflow.md)
- integrates_with: [cflib (Crazyflie Python library)](../../catalog/repos/bitcraze__crazyflie-lib-python.md)
- same_org: [gym-pybullet-drones](../../catalog/repos/learnsyslab__gym-pybullet-drones.md)

## Referenced by

- [LSY Autonomous Drone Racing documentation](../../catalog/resources/lsy-drone-racing-docs.md) (explains)

_Indexed by lane(s): close-area-sims_
