# ArduRemoteID

`repo:ardupilot/arduremoteid` - <https://github.com/ArduPilot/ArduRemoteID>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 257 | C++ | GPL-2.0 | 2025-07-04 | False | production | high |

ESP32-based Remote ID transmitter firmware implementing ASTM F3411 broadcast (Bluetooth and Wi-Fi) fed from MAVLink or DroneCAN.

**Why it matters:** Cheap compliant Remote ID broadcasting, and the transmitter side of any Remote ID-based C-UAS awareness demo.

**Hackathon notes:** Flash an ESP32-S3/C3 dev board; pair with opendroneid receiver-android to show detection end to end.

**Concepts:** [Standards and interface specs](../concepts/standards.md), [Counter-UAS and drone detection](../concepts/counter-uas.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `remote-id`, `astm-f3411`, `esp32`, `opendroneid`, `dronecan`

**Domains:** air

## Related

- depends_on: [Open Drone ID Core C](../repos/opendroneid__opendroneid-core-c.md)
- integrates_with: [ArduPilot](../repos/ardupilot__ardupilot.md)
- integrates_with: [OpenDroneID Android receiver](../repos/opendroneid__receiver-android.md)

## Referenced by

- [ArduPilot](../repos/ardupilot__ardupilot.md) (integrates_with)
- [Open Drone ID Core C](../repos/opendroneid__opendroneid-core-c.md) (integrates_with)
- [OpenDroneID Android receiver](../repos/opendroneid__receiver-android.md) (integrates_with)
- [uav_electronic_ids](../repos/sxjack__uav_electronic_ids.md) (alternative_to)
- [Remote ID (ArduPilot)](../resources/ardupilot-remote-id-docs.md) (has_code)
- [Remote ID (Open Drone ID) in PX4](../resources/px4-remote-id-docs.md) (uses)

_Indexed by lane(s): autopilots_

_GitHub metadata fetched 2026-11-06._
