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

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Maritime navigation](../../catalog/concepts/maritime-nav.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `gazebo`, `usv`, `wam-v`, `robotx`, `ros2`, `maritime`

**Domains:** maritime

## Related

- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- alternative_to: [MOOS-IvP](../../catalog/repos/moos-ivp__moos-ivp.md)
- depends_on: [Gazebo Sim (gz-sim)](../../catalog/repos/gazebosim__gz-sim.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [MBZIRC Maritime Grand Challenge simulator](../../catalog/repos/osrf__mbzirc.md) (alternative_to)

_Indexed by lane(s): domains-swarm, sim-data_

_GitHub metadata fetched 2026-11-06._
