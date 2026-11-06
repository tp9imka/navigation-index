# Virtual RobotX (VRX)

`repo:osrf/vrx` - <https://github.com/osrf/vrx>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 762 | C++ | Apache-2.0 | 2026-08-02 | False | production | high |

Gazebo-based simulation environment for the RobotX maritime autonomy competition, with a WAM-V USV model, waves, wind, sensors and scored tasks such as station keeping, wayfinding and perception.

**Why it matters:** Ready-made surface-vessel sim with nav and perception tasks; good for maritime autonomy demos.

**Hackathon notes:** Current branch targets gz-sim and ROS 2. Task worlds (station keeping, wayfinding) work as hackathon challenges out of the box.

## Deep dives

- [maritime-datasets](../../docs/dataset-cards/maritime-datasets.md) (dataset-cards)

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [Maritime navigation](../concepts/maritime-nav.md), [ROS / ROS 2 robotics middleware](../concepts/ros.md)

**Tags:** `gazebo`, `usv`, `wam-v`, `robotx`, `ros2`, `maritime`

**Domains:** maritime

## Related

- integrates_with: [ArduPilot](../repos/ardupilot__ardupilot.md)
- alternative_to: [MOOS-IvP](../repos/moos-ivp__moos-ivp.md)
- depends_on: [Gazebo Sim (gz-sim)](../repos/gazebosim__gz-sim.md)

## Referenced by

- [MBZIRC Maritime Grand Challenge simulator](../repos/osrf__mbzirc.md) (alternative_to)

_Indexed by lane(s): domains-swarm, sim-data_

_GitHub metadata fetched 2026-11-06._
