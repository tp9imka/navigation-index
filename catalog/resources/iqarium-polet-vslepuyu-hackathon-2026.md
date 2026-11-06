# Хакатон: трек «Робототехника и сенсорика», кейс «Полёт вслепую»

`res:iqarium-polet-vslepuyu-hackathon-2026` - competition - <https://iqarium.ru/hakatontime>

**By:** ООО «ИННОКУБ», ИЦ «Аквариум» (Krasnodar) - **Year:** 2026 - **Level:** intro - **Access:** open

English: 'Hackathon: Robotics and sensing track, case Blind flight'. Problem-statement page of the 48-hour hackathon held 26-28 June 2026 in Krasnodar. A commercial operator of light unmanned and optionally piloted aircraft delivering cargo to taiga, Arctic and mountain sites asks teams to build a prototype that determines coordinates, speed and heading from onboard data when GNSS degrades (high latitudes, narrow sky in gorges, jamming/spoofing near industrial zones, storms). The page itself does not name the sensors; public team repos show the case data were a radar-altimeter log (NMEA-0183 or TXT), a constant 1500 m MSL altitude and a DEM (Copernicus GLO-30 / GeoTIFF).

## Key takeaways

- Civil framing: cargo delivery to remote areas, GNSS loss from geometry, latitude and interference
- Input data (radar altimeter + DEM) are documented in team READMEs, not on the page
- Prize fund listed as 250k/150k/100k RUB; scoring criteria not published
- At least six public solution repos exist; compare them before designing a TERCOM entry

## Deep dives

- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)
- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `lang:ru`, `hackathon`, `tercom`, `radar-altimeter`, `dem`, `2026`

## Related

- has_code: [KROT (Где мы, Бариста?) - terrain correlation from radar altimeter](../../catalog/repos/rub1kub__where-are-we-barista.md)
- has_code: [Gagarin - TERCOM for UAVs without GNSS](../../catalog/repos/danilka88__gag27062026.md)
- has_code: [Полёт вслепую - GCS with terrain-referenced navigation](../../catalog/repos/drones-voronka__drones-backend.md)
- has_code: [HackatonCODEreal - altimeter/DEM autonomous flight (SKB 'FIZ-TECH')](../../catalog/repos/eliseyavdeev__hackatoncodereal.md)
- has_code: [Hackathon-Blind-Flight (team GORIZONT)](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md)
- has_code: [FlyingBlind_Hakaton](../../catalog/repos/solarwarlock__flyingblind_hakaton.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [Blind-flight bench: radar altimeter + Copernicus GLO-30 TRN, six navigators on one harness](../../catalog/samples/blind-flight-bench.md) (explains)

_Indexed by lane(s): ua-ru-round2_
