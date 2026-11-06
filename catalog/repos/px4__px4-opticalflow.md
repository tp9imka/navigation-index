# PX4 OpticalFlow

`repo:px4/px4-opticalflow` - <https://github.com/PX4/PX4-OpticalFlow>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 201 | C++ | BSD-3-Clause | 2026-09-21 | False | research-prototype | medium |

Algorithms for computing optical flow from a downward camera to produce velocity inputs for a position estimator.

**Why it matters:** Optical flow plus range finder is the cheapest GNSS-free velocity source for low-altitude hover and drift control.

**Hackathon notes:** Library only (PX4Flow SAD block matching and an OpenCV KLT variant behind calcFlow()); there is no executable or MAVLink output, so you write the camera capture and OPTICAL_FLOW_RAD publishing yourself. The Gazebo Classic flow plugin is the reference user. Light maintenance commits in 2026.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `optical-flow`, `px4flow`, `camera`

**Domains:** air

## Related

- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- integrates_with: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)

## Referenced by

- [Optical Flow](../../catalog/resources/px4-optical-flow-docs.md) (has_code)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
