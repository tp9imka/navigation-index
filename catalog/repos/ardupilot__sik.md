# SiK radio firmware

`repo:ardupilot/sik` - <https://github.com/ArduPilot/SiK>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 346 | C | BSD-2-Clause | 2026-10-04 | False | production | low |

Firmware and tools for Si1000-based telemetry radios (3DR/RFD900 class) carrying MAVLink.

**Why it matters:** Classic serial telemetry radio stack; frequency-hopping config is relevant to link robustness.

**Hackathon notes:** Mostly use stock firmware; configure via AT commands or Mission Planner.

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md)

**Tags:** `telemetry`, `fhss`, `rfd900`, `si1000`

**Domains:** air, ground

## Related

- alternative_to: [mLRS](../../catalog/repos/olliw42__mlrs.md)

## Referenced by

- [mLRS](../../catalog/repos/olliw42__mlrs.md) (alternative_to)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
