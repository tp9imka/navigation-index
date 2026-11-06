# ardupilot_gazebo

`repo:ardupilot/ardupilot_gazebo` - <https://github.com/ArduPilot/ardupilot_gazebo>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 239 | C++ | LGPL-3.0 | 2026-10-29 | False | production | high |

Gazebo Sim plugins that connect ArduPilot SITL to Gazebo physics, with example Iris copter and Zephyr plane models and worlds.

**Why it matters:** Brings ArduPilot vehicles (copter, plane, rover, boat) into gz-sim with realistic sensors for nav and autonomy testing.

**Hackathon notes:** Follow the ArduPilot wiki Gazebo guide; works best on Ubuntu (macOS also supported). No rover or boat models ship here, so a USV/rover test needs a model from elsewhere, such as ardupilot/SITL_Models.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `gazebo`, `sitl`, `plugins`, `plugin`, `ardupilot`

**Domains:** air, ground, maritime

## Related

- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- alternative_to: [PX4 SITL Gazebo Classic](../../catalog/repos/px4__px4-sitl_gazebo-classic.md)
- extends: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- integrates_with: [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md)
- integrates_with: [ArduPilot SITL Models](../../catalog/repos/ardupilot__sitl_models.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) (integrates_with)
- [ardupilot_gz](../../catalog/repos/ardupilot__ardupilot_gz.md) (depends_on)
- [ArduPilot SITL Models](../../catalog/repos/ardupilot__sitl_models.md) (integrates_with)
- [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md) (integrates_with)
- [SITL Simulator (Software in the Loop)](../../catalog/resources/ardupilot-sitl-docs.md) (explains)

_Indexed by lane(s): autopilots, domains-swarm, sim-data_

_GitHub metadata fetched 2026-11-06._
