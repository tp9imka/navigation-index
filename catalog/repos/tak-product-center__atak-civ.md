# ATAK-CIV (TAK Product Center)

`repo:tak-product-center/atak-civ` - <https://github.com/TAK-Product-Center/atak-civ>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 297 | Java | NOASSERTION | 2026-02-06 | False | active-research | medium |

Source of the civilian Android Team Awareness Kit maintained by the TAK Product Center: map client, plugin SDK and CoT handling.

**Why it matters:** The most widely used open tactical map client; plugins let you inject nav and sensor data into a fielded UI.

**Hackathon notes:** Plugin builds need the matching SDK version; budget half a day for toolchain. Many teams instead feed CoT from Python and just use stock ATAK/iTAK.

**Concepts:** [Situational awareness and C2 interop](../concepts/situational-awareness.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `atak`, `tak`, `plugin`, `android`, `plugin-sdk`, `cot`

**Domains:** dismounted, multi

## Related

- fork_of: [ATAK-CIV (DoD release, archived)](../repos/deptofdefense__androidtacticalassaultkit-civ.md)
- integrates_with: [OpenTAKServer](../repos/brian7704__opentakserver.md)
- integrates_with: [FreeTAKServer](../repos/freetakteam__freetakserver.md)
- integrates_with: [PyTAK](../repos/snstac__pytak.md)

## Referenced by

- [ATAK-CIV (DoD release, archived)](../repos/deptofdefense__androidtacticalassaultkit-civ.md) (alternative_to)
- [TAK Server (open source)](../repos/tak-product-center__server.md) (same_org)
- [Cursor on Target (NDIA briefing)](../resources/cot-niessen-ndia-2008.md) (has_code)
- [TAK.gov - Team Awareness Kit portal](../resources/tak-gov.md) (explains)
- [TAK Protocol (takproto) - protobuf encoding of CoT](../resources/tak-protocol-takproto.md) (has_code)
- [MAVLink telemetry to TAK Cursor-on-Target](../samples/mavlink-to-tak-cot.md) (uses)

_Indexed by lane(s): defense-context, planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
