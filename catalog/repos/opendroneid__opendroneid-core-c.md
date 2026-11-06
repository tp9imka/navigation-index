# Open Drone ID Core C

`repo:opendroneid/opendroneid-core-c` - <https://github.com/opendroneid/opendroneid-core-c>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 383 | C | Apache-2.0 | 2026-10-07 | False | production | high |

Reference C library for encoding and decoding ASTM F3411 / ASD-STAN Remote ID messages (location, operator, system, auth) for Bluetooth and Wi-Fi broadcast.

**Why it matters:** Remote ID is the cooperative layer of airspace awareness and counter-UAS; this library is the canonical message implementation.

**Hackathon notes:** Builds with CMake in minutes; pair with an ESP32 or phone receiver to decode drone broadcasts and push them to a map or TAK.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [opendroneid__opendroneid-core-c](../../docs/integration-cards/opendroneid__opendroneid-core-c.md) (integration-cards)
- [remote-id-droneid-captures](../../docs/dataset-cards/remote-id-droneid-captures.md) (dataset-cards)

**Concepts:** [Standards and interface specs](../../catalog/concepts/standards.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `remote-id`, `astm-f3411`, `en4709`, `bluetooth`, `wifi`, `uas`

**Domains:** air

## Related

- integrates_with: [ArduRemoteID](../../catalog/repos/ardupilot__arduremoteid.md)
- same_org: [OpenDroneID Android receiver](../../catalog/repos/opendroneid__receiver-android.md)
- same_org: [OpenDroneID Linux transmitter](../../catalog/repos/opendroneid__transmitter-linux.md)
- alternative_to: [DragonSync](../../catalog/repos/alphafox02__dragonsync.md)
- alternative_to: [drone-mesh-mapper](../../catalog/repos/colonelpanichacks__drone-mesh-mapper.md)
- same_org: [Open Drone ID Wireshark dissector](../../catalog/repos/opendroneid__wireshark-dissector.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [DragonSync](../../catalog/repos/alphafox02__dragonsync.md) (integrates_with)
- [ArduRemoteID](../../catalog/repos/ardupilot__arduremoteid.md) (depends_on)
- [drone-mesh-mapper](../../catalog/repos/colonelpanichacks__drone-mesh-mapper.md) (alternative_to)
- [OpenDroneID Android receiver](../../catalog/repos/opendroneid__receiver-android.md) (depends_on)
- [OpenDroneID Linux transmitter](../../catalog/repos/opendroneid__transmitter-linux.md) (depends_on)
- [Open Drone ID Wireshark dissector](../../catalog/repos/opendroneid__wireshark-dissector.md) (same_org)
- [RID (ESP32 Remote ID receiver)](../../catalog/repos/peterjburke__rid.md) (depends_on)
- [uav_electronic_ids](../../catalog/repos/sxjack__uav_electronic_ids.md) (alternative_to)
- [FAA - Remote Identification of Drones](../../catalog/resources/faa-remote-id.md) (explains)
- [FAA - Remote Identification of Drones](../../catalog/resources/faa-remote-id.md) (has_code)
- [Open Drone ID](../../catalog/resources/mavlink-opendroneid-microservice.md) (uses)
- [Drone Remote ID decoder, track table and TAK output](../../catalog/samples/remote-id-to-tak.md) (evaluated_on)

_Indexed by lane(s): autopilots, defense-context, domains-swarm_

_GitHub metadata fetched 2026-11-06._
