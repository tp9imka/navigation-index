# MAVSDK

`repo:mavlink/mavsdk` - <https://github.com/mavlink/MAVSDK>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 962 | C++ | BSD-3-Clause | 2026-11-05 | False | production | high |

C++ SDK exposing high-level MAVLink plugins (action, mission, offboard, telemetry, camera) with a gRPC server for other languages.

**Why it matters:** Clean API for companion-side autonomy against PX4 (and to a degree ArduPilot) without ROS.

**Hackathon notes:** For hackathon speed use the Python binding: since MAVSDK v4, `pip install mavsdk` installs a native binding built in this repo (sync API in `mavsdk`, asyncio in `mavsdk.asyncio`), with no mavsdk_server process. The older gRPC-based MAVSDK-Python with a bundled mavsdk_server lives on as `mavsdk-grpc`.

## Deep dives

- [_index-round5-nav](../../docs/integration-cards/_index-round5-nav.md) (integration-cards)
- [mavlink__mavsdk](../../docs/integration-cards/mavlink__mavsdk.md) (integration-cards)

**Concepts:** [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `sdk`, `grpc`, `offboard`, `c++`

**Domains:** air

## Related

- integrates_with: [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md)
- integrates_with: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- alternative_to: [MAVROS](../../catalog/repos/mavlink__mavros.md)

## Referenced by

- [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md) (depends_on)
- [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md) (integrates_with)
- [MAVLink 2 and Message Signing](../../catalog/resources/mavlink-2-signing.md) (has_code)
- [MAVLink Common Message Set (common.xml)](../../catalog/resources/mavlink-common-messages.md) (has_code)
- [MAVLink Developer Guide](../../catalog/resources/mavlink-developer-guide.md) (has_code)
- [MAVLink Mission Protocol](../../catalog/resources/mavlink-mission-protocol.md) (has_code)
- [PX4 SITL GPS denial: inject, measure drift, recover](../../catalog/samples/px4-sitl-gps-denial.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
