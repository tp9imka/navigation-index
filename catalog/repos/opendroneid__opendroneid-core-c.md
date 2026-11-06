# Open Drone ID Core C

`repo:opendroneid/opendroneid-core-c` - <https://github.com/opendroneid/opendroneid-core-c>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 383 | C | Apache-2.0 | 2026-10-07 | False | production | high |

Reference C library for encoding and decoding ASTM F3411 / ASD-STAN Remote ID messages (location, operator, system, auth) for Bluetooth and Wi-Fi broadcast.

**Why it matters:** Remote ID is the cooperative layer of airspace awareness and counter-UAS; this library is the canonical message implementation.

**Hackathon notes:** Builds with CMake in minutes; pair with an ESP32 or phone receiver to decode drone broadcasts and push them to a map or TAK.

**Concepts:** [Standards and interface specs](../concepts/standards.md), [Counter-UAS and drone detection](../concepts/counter-uas.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md)

**Tags:** `remote-id`, `astm-f3411`, `en4709`, `bluetooth`, `wifi`, `uas`

**Domains:** air

## Related

- integrates_with: [ArduRemoteID](../repos/ardupilot__arduremoteid.md)
- same_org: [OpenDroneID Android receiver](../repos/opendroneid__receiver-android.md)
- same_org: [OpenDroneID Linux transmitter](../repos/opendroneid__transmitter-linux.md)
- alternative_to: [DragonSync](../repos/alphafox02__dragonsync.md)
- alternative_to: [drone-mesh-mapper](../repos/colonelpanichacks__drone-mesh-mapper.md)
- same_org: [Open Drone ID Wireshark dissector](../repos/opendroneid__wireshark-dissector.md)

## Referenced by

- [DragonSync](../repos/alphafox02__dragonsync.md) (integrates_with)
- [ArduRemoteID](../repos/ardupilot__arduremoteid.md) (depends_on)
- [drone-mesh-mapper](../repos/colonelpanichacks__drone-mesh-mapper.md) (alternative_to)
- [OpenDroneID Android receiver](../repos/opendroneid__receiver-android.md) (depends_on)
- [OpenDroneID Linux transmitter](../repos/opendroneid__transmitter-linux.md) (depends_on)
- [Open Drone ID Wireshark dissector](../repos/opendroneid__wireshark-dissector.md) (same_org)
- [RID (ESP32 Remote ID receiver)](../repos/peterjburke__rid.md) (depends_on)
- [uav_electronic_ids](../repos/sxjack__uav_electronic_ids.md) (alternative_to)
- [FAA - Remote Identification of Drones](../resources/faa-remote-id.md) (explains)
- [FAA - Remote Identification of Drones](../resources/faa-remote-id.md) (has_code)
- [Open Drone ID (MAVLink microservice)](../resources/mavlink-opendroneid-microservice.md) (uses)

_Indexed by lane(s): autopilots, defense-context, domains-swarm_

_GitHub metadata fetched 2026-11-06._
