# ORB_SLAM3_system_local

`repo:sasha-lobov/orb_slam3_system_local` - <https://github.com/sasha-lobov/ORB_SLAM3_system_local>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Python | ? | 2026-05-31 | False | research-prototype | medium |

Pet project for local UAV navigation without GNSS: AirSim video streamed over ZeroMQ into monocular ORB-SLAM3, a ROS node converts NED/ENU frames, IMU data corrects monocular scale, and a PID controller tracks a trajectory. Russian README.

**Why it matters:** A minimal end-to-end sim loop (simulator => SLAM => control) that a team can copy to test VO under GNSS loss.

**Hackathon notes:** Needs ORB-SLAM3 built separately and AirSim (archived upstream). Useful mainly as an architecture reference.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual SLAM](../../catalog/concepts/visual-slam.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `lang:ru`, `orb-slam3`, `airsim`, `zeromq`, `monocular`

**Domains:** air

## Related

- depends_on: [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md)
- depends_on: [AirSim](../../catalog/repos/microsoft__airsim.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [ViNet_AirSim_drone - learned VIO in AirSim](../../catalog/repos/sasha-lobov__vinet_airsim_drone.md) (same_org)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
