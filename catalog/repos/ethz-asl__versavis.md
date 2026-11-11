# VersaVIS

`repo:ethz-asl/versavis` - <https://github.com/ethz-asl/versavis>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 291 | C++ | NOASSERTION | 2021-09-28 | False | archived | low |

Open hardware and firmware board that hardware-triggers multiple cameras and an IMU and timestamps them on one clock, with ROS drivers. Designed for visual-inertial rigs.

**Why it matters:** Shows the hardware-sync approach (trigger plus exposure-time compensation) that removes most camera-IMU timing error before any software sync is needed.

**Build notes:** Last push 2021-09, ROS 1. License file is BSD-3 text (GitHub reports NOASSERTION). Cite the design; for a hackathon, use a camera with a hardware trigger input wired to an FC camera-trigger output instead.

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Timing and time transfer](../../catalog/concepts/timing.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `time-sync`, `camera-trigger`, `imu`, `hardware`, `ros1`

**Domains:** air, ground

## Related

- integrates_with: [Kalibr](../../catalog/repos/ethz-asl__kalibr.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-09._
