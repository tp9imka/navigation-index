# PyTAK

`repo:snstac/pytak` - <https://github.com/snstac/pytak>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 257 | Python | Apache-2.0 | 2026-11-02 | False | production | high |

Python asyncio package for TAK integration: CoT send/receive over TCP, UDP, TLS and multicast, with helpers for building events.

**Why it matters:** The glue that turns any sensor script (GNSS monitor, Remote ID sniffer, DF array) into a TAK layer in a few lines.

**Hackathon notes:** pip install pytak; write a CoT generator for your detections. Lowest-friction way into the TAK ecosystem.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [snstac__pytak](../../docs/integration-cards/snstac__pytak.md) (integration-cards)

**Concepts:** [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `tak`, `cot`, `python`, `asyncio`

**Domains:** multi

## Related

- same_org: [ADSBCOT](../../catalog/repos/snstac__adsbcot.md)
- integrates_with: [OpenTAKServer](../../catalog/repos/brian7704__opentakserver.md)
- integrates_with: [takproto](../../catalog/repos/snstac__takproto.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [DragonSync](../../catalog/repos/alphafox02__dragonsync.md) (integrates_with)
- [OpenTAKServer](../../catalog/repos/brian7704__opentakserver.md) (integrates_with)
- [node-CoT](../../catalog/repos/dfpc-coe__node-cot.md) (alternative_to)
- [FreeTAKServer](../../catalog/repos/freetakteam__freetakserver.md) (integrates_with)
- [OpenDroneID Android receiver](../../catalog/repos/opendroneid__receiver-android.md) (integrates_with)
- [ADSBCOT](../../catalog/repos/snstac__adsbcot.md) (depends_on)
- [takproto](../../catalog/repos/snstac__takproto.md) (integrates_with)
- [ATAK-CIV (TAK Product Center)](../../catalog/repos/tak-product-center__atak-civ.md) (integrates_with)
- [Cursor on Target (NDIA briefing)](../../catalog/resources/cot-niessen-ndia-2008.md) (has_code)
- [Cursor-on-Target Message Router User's Guide](../../catalog/resources/mitre-cot-users-guide.md) (explains)
- [PyTAK documentation](../../catalog/resources/pytak-docs.md) (explains)
- [TAK Protocol (takproto) - protobuf encoding of CoT](../../catalog/resources/tak-protocol-takproto.md) (has_code)
- [GNSS jammer geolocation from DF bearings to TAK](../../catalog/samples/interference-geolocation-to-tak.md) (explains)
- [Low-cost GNSS jammer sensor network: u-blox telemetry => localization => TAK and dashboard](../../catalog/samples/jammer-sensor-network.md) (explains)
- [GNSS spoofing signatures in real AIS tracks: detectors, injected ground truth, GeoJSON and CoT](../../catalog/samples/maritime-ais-spoofing.md) (explains)
- [MAVLink telemetry to TAK Cursor-on-Target](../../catalog/samples/mavlink-to-tak-cot.md) (uses)
- [Drone Remote ID decoder, track table and TAK output](../../catalog/samples/remote-id-to-tak.md) (uses)

_Indexed by lane(s): defense-context, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
