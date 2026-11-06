# openpilot

`repo:commaai/openpilot` - <https://github.com/commaai/openpilot>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 64,076 | Python | MIT | 2026-11-06 | False | production | low |

Open driver-assistance robotics stack. Its current locationd fuses IMU and camera odometry in a pose Kalman filter; GNSS is still read and logged (ubloxd, qcomgpsd) but the laika-based GNSS fusion has been removed.

**Why it matters:** Real-world example of a production fusion pipeline on consumer hardware, and of a stack that dropped GNSS from its localizer in favour of vision and IMU.

**Hackathon notes:** Large codebase; study locationd (pose_kf) and the ubloxd GNSS parsing rather than running the full stack. For laika-style GNSS processing, look at the standalone commaai/laika repo or older openpilot releases.

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md)

**Tags:** `adas`, `localization`, `comma-ai`

**Domains:** ground

## Related

- depends_on: [laika](../../catalog/repos/commaai__laika.md)

## Referenced by

- [laika](../../catalog/repos/commaai__laika.md) (same_org)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
