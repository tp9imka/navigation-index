# OpenDroneID Android receiver

`repo:opendroneid/receiver-android` - <https://github.com/opendroneid/receiver-android>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 385 | Java | Apache-2.0 | 2026-07-26 | False | production | high |

Example Android app that listens for Remote ID broadcasts over Bluetooth 4/5 and Wi-Fi Beacon/NaN and shows drones and operators on a map.

**Why it matters:** Fastest way to get a working cooperative drone-detection sensor in a hackathon using only phones.

**Hackathon notes:** Sideload on a recent Android phone; Wi-Fi NaN support depends on handset. Extend to forward detections as CoT to a TAK server.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [opendroneid__receiver-android](../../docs/integration-cards/opendroneid__receiver-android.md) (integration-cards)
- [remote-id-droneid-captures](../../docs/dataset-cards/remote-id-droneid-captures.md) (dataset-cards)

**Concepts:** [Counter-UAS and drone detection](../concepts/counter-uas.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `remote-id`, `android`, `bluetooth`, `wifi-nan`, `ble`

**Domains:** air, dismounted

## Related

- depends_on: [Open Drone ID Core C](../repos/opendroneid__opendroneid-core-c.md)
- integrates_with: [ArduRemoteID](../repos/ardupilot__arduremoteid.md)
- integrates_with: [PyTAK](../repos/snstac__pytak.md)

## Referenced by

- [ArduRemoteID](../repos/ardupilot__arduremoteid.md) (integrates_with)
- [Open Drone ID Core C](../repos/opendroneid__opendroneid-core-c.md) (same_org)

_Indexed by lane(s): autopilots, defense-context, domains-swarm_

_GitHub metadata fetched 2026-11-06._
