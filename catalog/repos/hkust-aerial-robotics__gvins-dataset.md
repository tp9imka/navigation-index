# GVINS dataset

`repo:hkust-aerial-robotics/gvins-dataset` - <https://github.com/HKUST-Aerial-Robotics/GVINS-Dataset>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 266 | C++ | NOASSERTION | 2026-08-29 | False | research-prototype | medium |

Dataset with synchronized visual, inertial and raw GNSS measurements released with GVINS.

**Why it matters:** One of few datasets with raw GNSS pseudoranges plus camera and IMU, needed for tightly coupled GNSS-VIO.

**Hackathon notes:** ROS bags with custom GNSS message types; install the gnss_comm package.

## Deep dives

- [gvins](../../docs/dataset-cards/gvins.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [GNSS/INS integration](../concepts/gnss-ins.md), [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `gnss-raw`, `vio`, `rosbag`

**Domains:** ground, dismounted

## Related

- evaluated_on: [GVINS](../repos/hkust-aerial-robotics__gvins.md)

## Referenced by

- [GVINS](../repos/hkust-aerial-robotics__gvins.md) (evaluated_on)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
