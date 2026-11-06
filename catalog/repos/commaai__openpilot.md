# openpilot

`repo:commaai/openpilot` - <https://github.com/commaai/openpilot>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 64,076 | Python | MIT | 2026-11-06 | False | production | low |

Open driver-assistance robotics stack whose localization uses GNSS (via laika) fused with IMU and vision.

**Why it matters:** Real-world example of GNSS feeding a production fusion pipeline on consumer hardware.

**Hackathon notes:** Large codebase; study locationd and its use of laika rather than running the full stack.

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md)

**Tags:** `adas`, `localization`, `comma-ai`

**Domains:** ground

## Related

- depends_on: [laika](../repos/commaai__laika.md)

## Referenced by

- [laika](../repos/commaai__laika.md) (same_org)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
