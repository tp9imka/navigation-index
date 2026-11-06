# MAVLink Camera Manager

`repo:mavlink/mavlink-camera-manager` - <https://github.com/mavlink/mavlink-camera-manager>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 183 | Rust | MIT | 2026-11-03 | False | production | medium |

Rust service that exposes cameras as MAVLink camera components and streams video (RTSP/UDP) to GCS.

**Why it matters:** Makes onboard cameras discoverable to QGC and BlueOS without custom code.

**Hackathon notes:** Runs standalone or inside BlueOS.

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `rust`, `video`, `camera-protocol`

**Domains:** multi

## Related

- integrates_with: [BlueOS](../../catalog/repos/bluerobotics__blueos.md)
- integrates_with: [QGroundControl](../../catalog/repos/mavlink__qgroundcontrol.md)

## Referenced by

- [BlueOS](../../catalog/repos/bluerobotics__blueos.md) (depends_on)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
