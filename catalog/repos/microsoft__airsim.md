# AirSim

`repo:microsoft/airsim` - <https://github.com/microsoft/AirSim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 18,601 | C++ | NOASSERTION | 2026-09-15 | False | archived | medium |

Unreal Engine based simulator for drones and cars with camera, depth, lidar, IMU, GPS, barometer and magnetometer models and a Python/C++ API. Microsoft wound down development and pointed users to Project AirSim.

**Why it matters:** Still the most widely used photorealistic drone sim in research papers; many visual-nav and geolocalization datasets were rendered with it.

**Hackathon notes:** Prebuilt binary environments are the quickest path. Building from source requires a matching old Unreal version. For new work prefer Colosseum or Project AirSim.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `unreal`, `airsim`, `photorealistic`, `px4`

**Domains:** air, ground

## Related

- fork_of: [Colosseum (AirSim fork)](../../catalog/repos/codexlabsllc__colosseum.md)
- alternative_to: [Project AirSim](../../catalog/repos/iamaisim__projectairsim.md)
- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Colosseum (AirSim fork)](../../catalog/repos/codexlabsllc__colosseum.md) (fork_of)
- [GRID playground (AirGen)](../../catalog/repos/genrobo__grid-playground.md) (extends)
- [Project AirSim](../../catalog/repos/iamaisim__projectairsim.md) (extends)
- [PromptCraft-Robotics](../../catalog/repos/microsoft__promptcraft-robotics.md) (depends_on)
- [ORB_SLAM3_system_local](../../catalog/repos/sasha-lobov__orb_slam3_system_local.md) (depends_on)
- [AirSim Documentation](../../catalog/resources/microsoft-airsim-docs.md) (explains)
- [Mid-Air Dataset](../../catalog/resources/midair-synthetic-drone-dataset.md) (uses)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
