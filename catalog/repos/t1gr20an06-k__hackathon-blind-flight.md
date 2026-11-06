# Hackathon-Blind-Flight (team GORIZONT)

`repo:t1gr20an06-k/hackathon-blind-flight` - <https://github.com/t1Gr20an06-k/Hackathon-Blind-Flight>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2 | Python | ? | 2026-07-15 | False | research-prototype | high |

Russian-language hackathon solution for 'Полёт вслепую' (Blind flight): estimate aircraft position, ground speed and heading without GNSS by reconstructing a terrain profile (barometric altitude minus radar altimeter) and matching it against a DEM, TERCOM style.

**Why it matters:** A compact, documented TERCOM pipeline on real DEM data; shows how a GNSS-denied hackathon problem was posed and solved in 2026.

**Hackathon notes:** Reads DEM + altimeter series; small dependency set. Useful as a baseline if a hackathon gives altimeter/DEM data. Accuracy figures are not independently checked here.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `lang:ru`, `tercom`, `radar-altimeter`, `dem`, `hackathon`

**Domains:** air

## Related

- alternative_to: [FlyingBlind_Hakaton](../repos/solarwarlock__flyingblind_hakaton.md)
- alternative_to: [python-tercom](../repos/alti3__python-tercom.md)

## Referenced by

- [FlyingBlind_Hakaton](../repos/solarwarlock__flyingblind_hakaton.md) (alternative_to)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
