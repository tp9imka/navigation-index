# AirSim

`repo:microsoft/airsim` - <https://github.com/microsoft/AirSim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 18,601 | C++ | NOASSERTION | 2026-09-15 | False | archived | medium |

Unreal Engine based simulator for drones and cars with camera, depth, lidar, IMU, GPS, barometer and magnetometer models and a Python/C++ API. Microsoft wound down development and pointed users to Project AirSim.

**Why it matters:** Still the most widely used photorealistic drone sim in research papers; many visual-nav and geolocalization datasets were rendered with it.

**Hackathon notes:** Prebuilt binary environments are the quickest path. Building from source requires a matching old Unreal version. For new work prefer Colosseum or Project AirSim.

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `unreal`, `airsim`, `photorealistic`, `px4`

**Domains:** air, ground

## Related

- fork_of: [Colosseum (AirSim fork)](../repos/codexlabsllc__colosseum.md)
- alternative_to: [Project AirSim](../repos/iamaisim__projectairsim.md)
- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)

## Referenced by

- [Colosseum (AirSim fork)](../repos/codexlabsllc__colosseum.md) (fork_of)
- [GRID playground (AirGen)](../repos/genrobo__grid-playground.md) (extends)
- [Project AirSim](../repos/iamaisim__projectairsim.md) (extends)
- [AirSim Documentation](../resources/microsoft-airsim-docs.md) (explains)
- [Mid-Air Dataset](../resources/midair-synthetic-drone-dataset.md) (uses)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
