# KROT (Где мы, Бариста?) - terrain correlation from radar altimeter

`repo:rub1kub/where-are-we-barista` - <https://github.com/rub1kub/where-are-we-barista>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2 | TypeScript | ? | 2026-08-31 | False | research-prototype | high |

Team 'Где мы, Бариста?' solution to the 2026 'Полёт вслепую' (Blind flight) hackathon case: 'КРОТ' (Корреляционный Рельефный Определитель Траектории) turns a radar-altimeter NMEA-0183 log flown at a constant 1500 m MSL into a terrain profile, correlates it against a Copernicus GLO-30 GeoTIFF, and outputs map position, WGS-84 coordinates, ground speed, azimuth and match-quality metrics. React/Three.js operator panel plus separate C++ and Rust compute cores. README in Russian also records what the organisers' technical expert clarified (no IMU/camera, final-day validation log, bonus for speed and noise robustness).

**Why it matters:** The most complete public write-up of the TERCOM-style hackathon problem: input format, organiser constraints and a quality/confidence readout, which is exactly what a judge asks for.

**Hackathon notes:** Read the README section on expert clarifications first: it is the closest thing to a published spec of the case. The C++/Rust cores are the parts to lift; the web UI is a demo shell. Works offline against a GeoTIFF, no flight hardware needed.

## Deep dives

- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)
- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `lang:ru`, `tercom`, `radar-altimeter`, `nmea-0183`, `copernicus-dem`, `hackathon`, `typescript`, `rust`, `c++`

**Domains:** air

## Related

- alternative_to: [Hackathon-Blind-Flight (team GORIZONT)](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md)
- alternative_to: [FlyingBlind_Hakaton](../../catalog/repos/solarwarlock__flyingblind_hakaton.md)
- alternative_to: [Gagarin - TERCOM for UAVs without GNSS](../../catalog/repos/danilka88__gag27062026.md)
- alternative_to: [HackatonCODEreal - altimeter/DEM autonomous flight (SKB 'FIZ-TECH')](../../catalog/repos/eliseyavdeev__hackatoncodereal.md)
- alternative_to: [Полёт вслепую - GCS with terrain-referenced navigation](../../catalog/repos/drones-voronka__drones-backend.md)
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
- [Хакатон: трек «Робототехника и сенсорика», кейс «Полёт вслепую»](../../catalog/resources/iqarium-polet-vslepuyu-hackathon-2026.md) (has_code)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-06._
