# uav_electronic_ids

`repo:sxjack/uav_electronic_ids` - <https://github.com/sxjack/uav_electronic_ids>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 136 | C | MIT | 2024-01-04 | False | research-prototype | medium |

Arduino classes for several UAV electronic ID formats (ASTM/EU Remote ID, French ID) and UTM interfaces, with ESP32 examples.

**Why it matters:** Small, readable alternative Remote ID implementation, including receiver-side sketches.

**Hackathon notes:** Arduino IDE; the id_open examples are transmitters (ESP32, ESP8266, nRF52) and id_scanner is a receiver sketch.

**Concepts:** [Standards and interface specs](../../catalog/concepts/standards.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md)

**Tags:** `remote-id`, `arduino`, `esp32`

**Domains:** air

## Related

- alternative_to: [Open Drone ID Core C](../../catalog/repos/opendroneid__opendroneid-core-c.md)
- alternative_to: [ArduRemoteID](../../catalog/repos/ardupilot__arduremoteid.md)

## Referenced by

- [RID (ESP32 Remote ID receiver)](../../catalog/repos/peterjburke__rid.md) (fork_of)
- [Drone Remote ID decoder, track table and TAK output](../../catalog/samples/remote-id-to-tak.md) (integrates_with)

_Indexed by lane(s): autopilots, domains-swarm_

_GitHub metadata fetched 2026-11-06._
