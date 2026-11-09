# MuJoCo Menagerie

`repo:google-deepmind/mujoco_menagerie` - <https://github.com/google-deepmind/mujoco_menagerie>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | Python | ? | ? | ? | production | medium |

Curated MuJoCo MJCF models, including a Skydio X2 quadrotor and a Bitcraze Crazyflie 2. Models only, no controllers.

**Why it matters:** Gives a clean quadrotor model in a physics engine that runs natively on Apple Silicon. Useful when you want contacts and rendering without PyBullet.

**Hackathon notes:** pip install mujoco, clone the repo, load bitcraze_crazyflie_2/scene.xml. You write the controller and the planner loop; budget 1-2 h to first hover. Per-model licenses differ (repo-level NOASSERTION).

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `mujoco`, `mjcf`, `crazyflie`, `skydio-x2`, `models`

**Domains:** air

## Related

- integrates_with: [Crazyflow](../../catalog/repos/learnsyslab__crazyflow.md)

_Indexed by lane(s): close-area-sims_
