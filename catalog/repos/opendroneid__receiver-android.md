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

**Concepts:** [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `remote-id`, `android`, `bluetooth`, `wifi-nan`, `ble`

**Domains:** air, dismounted

## Related

- depends_on: [Open Drone ID Core C](../../catalog/repos/opendroneid__opendroneid-core-c.md)
- integrates_with: [ArduRemoteID](../../catalog/repos/ardupilot__arduremoteid.md)
- integrates_with: [PyTAK](../../catalog/repos/snstac__pytak.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ArduRemoteID](../../catalog/repos/ardupilot__arduremoteid.md) (integrates_with)
- [Open Drone ID Core C](../../catalog/repos/opendroneid__opendroneid-core-c.md) (same_org)
- [Drone Remote ID decoder, track table and TAK output](../../catalog/samples/remote-id-to-tak.md) (integrates_with)

_Indexed by lane(s): autopilots, defense-context, domains-swarm_

_GitHub metadata fetched 2026-11-06._
