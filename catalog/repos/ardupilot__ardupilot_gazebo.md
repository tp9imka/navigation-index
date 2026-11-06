# ardupilot_gazebo

`repo:ardupilot/ardupilot_gazebo` - <https://github.com/ArduPilot/ardupilot_gazebo>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 239 | C++ | LGPL-3.0 | 2026-10-29 | False | production | high |

Gazebo Sim plugins and models that connect ArduPilot SITL to Gazebo physics for copters, rovers and boats.

**Why it matters:** Brings ArduPilot vehicles (copter, plane, rover, boat) into gz-sim with realistic sensors for nav and autonomy testing.

**Hackathon notes:** Build against your Gazebo release, run sim_vehicle.py with '-f gazebo-iris --model JSON'. Follow the README's environment variables for model paths.

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [Autopilots and flight control](../concepts/autopilot.md)

**Tags:** `gazebo`, `sitl`, `plugins`, `plugin`, `ardupilot`

**Domains:** air, ground, maritime

## Related

- integrates_with: [ArduPilot](../repos/ardupilot__ardupilot.md)
- alternative_to: [PX4 SITL Gazebo Classic](../repos/px4__px4-sitl_gazebo-classic.md)
- extends: [ArduPilot](../repos/ardupilot__ardupilot.md)
- integrates_with: [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md)
- integrates_with: [ArduPilot SITL Models](../repos/ardupilot__sitl_models.md)

## Referenced by

- [ArduPilot](../repos/ardupilot__ardupilot.md) (integrates_with)
- [ardupilot_gz](../repos/ardupilot__ardupilot_gz.md) (depends_on)
- [ArduPilot SITL Models](../repos/ardupilot__sitl_models.md) (integrates_with)
- [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md) (integrates_with)
- [ArduPilot SITL Simulator (Software in the Loop)](../resources/ardupilot-sitl-docs.md) (explains)

_Indexed by lane(s): autopilots, domains-swarm, sim-data_

_GitHub metadata fetched 2026-11-06._
