# ViNet_AirSim_drone - learned VIO in AirSim

`repo:sasha-lobov/vinet_airsim_drone` - <https://github.com/sasha-lobov/ViNet_AirSim_drone>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 | Jupyter Notebook | ? | 2026-04-08 | False | educational | low |

PyTorch CNN+RNN network that predicts relative pose between frames from a monocular camera and 6-axis IMU, trained on data collected in Microsoft AirSim with ground-truth poses and a composite loss to limit drift. README in Russian.

**Why it matters:** A learned-VIO baseline with a simulator data loop, relevant if the team wants to compare deep and geometric odometry.

**Hackathon notes:** Needs AirSim to regenerate data; notebooks otherwise. Expect sim-to-real gaps.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `lang:ru`, `learned-vio`, `airsim`, `pytorch`, `cnn-rnn`

**Domains:** air

## Related

- same_org: [ORB_SLAM3_system_local](../../catalog/repos/sasha-lobov__orb_slam3_system_local.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-06._
