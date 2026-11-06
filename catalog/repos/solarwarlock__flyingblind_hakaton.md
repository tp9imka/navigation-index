# FlyingBlind_Hakaton

`repo:solarwarlock/flyingblind_hakaton` - <https://github.com/SolarWarlock/FlyingBlind_Hakaton>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Python | ? | 2026-07-31 | False | research-prototype | high |

Second public solution to the same 'Полёт вслепую' hackathon task: web prototype that reads a GeoTIFF DEM and NMEA-0183 radar-altimeter messages, searches start point, speed and azimuth hypotheses by RMSE/correlation, and reports a confidence and a flat-terrain check.

**Why it matters:** Shows the practical details (UTM projection, bilinear DEM sampling, weighted scoring for informative relief, flat-terrain rejection) that a TERCOM demo needs.

**Hackathon notes:** Streamlit app on rasterio + pyproj; an optional Rust core (built automatically if cargo is installed) speeds up the hypothesis search. Includes a synthetic NMEA generator from a real DEM, which is handy for building test data fast. Small repo (about a dozen commits).

## Deep dives

- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)
- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `lang:ru`, `tercom`, `nmea`, `dem`, `rasterio`, `hackathon`

**Domains:** air

## Related

- alternative_to: [Hackathon-Blind-Flight (team GORIZONT)](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md)
- alternative_to: [tercom_nav (TERCOM + ESKF)](../../catalog/repos/mzahana__tercom_nav.md)

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
- [Hackathon-Blind-Flight (team GORIZONT)](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md) (alternative_to)
- [Хакатон: трек «Робототехника и сенсорика», кейс «Полёт вслепую»](../../catalog/resources/iqarium-polet-vslepuyu-hackathon-2026.md) (has_code)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
