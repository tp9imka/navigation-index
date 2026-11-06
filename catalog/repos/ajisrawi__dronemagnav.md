# DroneMagNav

`repo:ajisrawi/dronemagnav` - <https://github.com/ajisrawi/dronemagnav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 11 | Python | NOASSERTION | 2026-09-13 | False | research-prototype | medium |

Open hardware + firmware design for a drone magnetic-anomaly navigation board (ESP32-S3, magnetometer, IMU, baro) running particle-filter matching against a global anomaly map and feeding position to a flight controller over MAVLink.

**Why it matters:** Rare example of MagNav pushed down to cheap drone hardware with an autopilot interface.

**Hackathon notes:** Very recent single-author project; hardware not validated in flight per what we could see. Global anomaly maps are coarse, so expect km-level, not meter-level, results on small drones.

**Concepts:** [Magnetic anomaly navigation](../concepts/magnetic-nav.md), [Autopilots and flight control](../concepts/autopilot.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `esp32`, `kicad`, `mavlink`, `particle-filter`

**Domains:** air

## Related

- alternative_to: [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md)

## Referenced by

- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../samples/magnav-quickstart.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
