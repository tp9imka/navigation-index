# DroneMagNav

`repo:ajisrawi/dronemagnav` - <https://github.com/ajisrawi/dronemagnav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 11 | Python | NOASSERTION | 2026-09-13 | False | research-prototype | medium |

Hardware + firmware design for a drone magnetic-anomaly navigation board (ESP32-S3, magnetometer, IMU, baro) running particle-filter matching against a global anomaly map and feeding position to a flight controller over MAVLink. Proprietary: the LICENSE grants no rights to copy, modify or use it.

**Why it matters:** Rare example of MagNav pushed down to cheap drone hardware with an autopilot interface.

**Hackathon notes:** Very recent single-author project; the board has not been built and the firmware has not run on real hardware (README status). Proprietary licence, so read it for ideas only - do not reuse code or designs. Global anomaly maps are coarse, so expect km-level, not meter-level, results on small drones.

**Concepts:** [Magnetic anomaly navigation](../../catalog/concepts/magnetic-nav.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `esp32`, `kicad`, `mavlink`, `particle-filter`

**Domains:** air

## Related

- alternative_to: [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md)

## Referenced by

- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../../catalog/samples/magnav-quickstart.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
