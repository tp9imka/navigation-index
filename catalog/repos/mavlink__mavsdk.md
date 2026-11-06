# MAVSDK

`repo:mavlink/mavsdk` - <https://github.com/mavlink/MAVSDK>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 962 | C++ | BSD-3-Clause | 2026-11-05 | False | production | high |

C++ SDK exposing high-level MAVLink plugins (action, mission, offboard, telemetry, camera) with a gRPC server for other languages.

**Why it matters:** Clean API for companion-side autonomy against PX4 (and to a degree ArduPilot) without ROS.

**Hackathon notes:** Use MAVSDK-Python for hackathon speed; mavsdk_server is bundled.

**Concepts:** [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md), [Autopilots and flight control](../concepts/autopilot.md)

**Tags:** `sdk`, `grpc`, `offboard`, `c++`

**Domains:** air

## Related

- integrates_with: [MAVSDK-Python](../repos/mavlink__mavsdk-python.md)
- integrates_with: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- alternative_to: [MAVROS](../repos/mavlink__mavros.md)

## Referenced by

- [MAVSDK-Python](../repos/mavlink__mavsdk-python.md) (depends_on)
- [PX4 Autopilot](../repos/px4__px4-autopilot.md) (integrates_with)
- [MAVLink 2 and Message Signing](../resources/mavlink-2-signing.md) (has_code)
- [MAVLink Common Message Set (common.xml)](../resources/mavlink-common-messages.md) (has_code)
- [MAVLink Developer Guide](../resources/mavlink-developer-guide.md) (has_code)
- [MAVLink Mission Protocol](../resources/mavlink-mission-protocol.md) (has_code)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
