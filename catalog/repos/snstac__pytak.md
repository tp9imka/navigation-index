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

**Concepts:** [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `tak`, `cot`, `python`, `asyncio`

**Domains:** multi

## Related

- same_org: [ADSBCOT](../repos/snstac__adsbcot.md)
- integrates_with: [OpenTAKServer](../repos/brian7704__opentakserver.md)
- integrates_with: [takproto](../repos/snstac__takproto.md)

## Referenced by

- [DragonSync](../repos/alphafox02__dragonsync.md) (integrates_with)
- [OpenTAKServer](../repos/brian7704__opentakserver.md) (integrates_with)
- [node-CoT](../repos/dfpc-coe__node-cot.md) (alternative_to)
- [FreeTAKServer](../repos/freetakteam__freetakserver.md) (integrates_with)
- [OpenDroneID Android receiver](../repos/opendroneid__receiver-android.md) (integrates_with)
- [ADSBCOT](../repos/snstac__adsbcot.md) (depends_on)
- [takproto](../repos/snstac__takproto.md) (integrates_with)
- [ATAK-CIV (TAK Product Center)](../repos/tak-product-center__atak-civ.md) (integrates_with)
- [Cursor on Target (NDIA briefing)](../resources/cot-niessen-ndia-2008.md) (has_code)
- [Cursor-on-Target Message Router User's Guide](../resources/mitre-cot-users-guide.md) (explains)
- [PyTAK documentation](../resources/pytak-docs.md) (explains)
- [TAK Protocol (takproto) - protobuf encoding of CoT](../resources/tak-protocol-takproto.md) (has_code)
- [GNSS jammer geolocation from DF bearings to TAK](../samples/interference-geolocation-to-tak.md) (explains)
- [MAVLink telemetry to TAK Cursor-on-Target](../samples/mavlink-to-tak-cot.md) (uses)

_Indexed by lane(s): defense-context, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
