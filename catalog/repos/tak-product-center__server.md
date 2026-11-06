# TAK Server (open source)

`repo:tak-product-center/server` - <https://github.com/tak-product-center/server>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 710 | Java | NOASSERTION | 2026-04-03 | False | production | medium |

Open-source release of the TAK Server from the TAK Product Center: the federation and message routing server for ATAK/WinTAK/iTAK clients, handling CoT, data packages, missions and video.

**Why it matters:** Reference C2 backend used by many government users; integrating with it makes a demo interoperable with fielded TAK clients.

**Hackathon notes:** Java + PostgreSQL + certificate setup is the main hurdle; use a docker recipe and allow several hours.

**Concepts:** [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `tak`, `cot`, `federation`, `java`

**Domains:** multi, dismounted

## Related

- same_org: [ATAK-CIV (TAK Product Center)](../repos/tak-product-center__atak-civ.md)
- alternative_to: [FreeTAKServer](../repos/freetakteam__freetakserver.md)
- alternative_to: [OpenTAKServer](../repos/brian7704__opentakserver.md)

## Referenced by

- [OpenTAKServer](../repos/brian7704__opentakserver.md) (alternative_to)
- [CloudTAK](../repos/dfpc-coe__cloudtak.md) (integrates_with)
- [FreeTAKServer](../repos/freetakteam__freetakserver.md) (alternative_to)
- [TAK.gov - Team Awareness Kit portal](../resources/tak-gov.md) (explains)

_Indexed by lane(s): planning-gis-c2_

_GitHub metadata fetched 2026-11-06._
