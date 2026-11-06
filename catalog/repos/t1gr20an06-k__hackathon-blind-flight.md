# Hackathon-Blind-Flight (team GORIZONT)

`repo:t1gr20an06-k/hackathon-blind-flight` - <https://github.com/t1Gr20an06-k/Hackathon-Blind-Flight>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2 | Python | ? | 2026-07-15 | False | research-prototype | high |

Russian-language hackathon solution for 'Полёт вслепую' (Blind flight): estimate aircraft position, ground speed and heading without GNSS by reconstructing a terrain profile (barometric altitude minus radar altimeter) and matching it against a DEM, TERCOM style.

**Why it matters:** A compact, documented TERCOM pipeline on real DEM data; shows how a GNSS-denied hackathon problem was posed and solved in 2026.

**Hackathon notes:** Reads DEM + altimeter series; small dependency set. Useful as a baseline if a hackathon gives altimeter/DEM data. Accuracy figures are not independently checked here.

## Deep dives

- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)
- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `lang:ru`, `tercom`, `radar-altimeter`, `dem`, `hackathon`

**Domains:** air

## Related

- alternative_to: [FlyingBlind_Hakaton](../../catalog/repos/solarwarlock__flyingblind_hakaton.md)
- alternative_to: [python-tercom](../../catalog/repos/alti3__python-tercom.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [Gagarin - TERCOM for UAVs without GNSS](../../catalog/repos/danilka88__gag27062026.md) (alternative_to)
- [Полёт вслепую - GCS with terrain-referenced navigation](../../catalog/repos/drones-voronka__drones-backend.md) (alternative_to)
- [HackatonCODEreal - altimeter/DEM autonomous flight (SKB 'FIZ-TECH')](../../catalog/repos/eliseyavdeev__hackatoncodereal.md) (alternative_to)
- [KROT (Где мы, Бариста?) - terrain correlation from radar altimeter](../../catalog/repos/rub1kub__where-are-we-barista.md) (alternative_to)
- [FlyingBlind_Hakaton](../../catalog/repos/solarwarlock__flyingblind_hakaton.md) (alternative_to)
- [Хакатон: трек «Робототехника и сенсорика», кейс «Полёт вслепую»](../../catalog/resources/iqarium-polet-vslepuyu-hackathon-2026.md) (has_code)
- [Blind-flight bench: radar altimeter + Copernicus GLO-30 TRN, six navigators on one harness](../../catalog/samples/blind-flight-bench.md) (explains)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
