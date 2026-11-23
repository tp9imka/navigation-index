# HackatonCODEreal - altimeter/DEM autonomous flight (SKB 'FIZ-TECH')

`repo:eliseyavdeev/hackatoncodereal` - <https://github.com/EliseyAvdeev/HackatonCODEreal>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 0 | Python | ? | 2026-06-28 | False | research-prototype | medium |

Hackathon code from team SKB 'ФИЗ-ТЕХ' for the June 2026 blind-flight case: takes NMEA, sample rate, barometric altitude and a height map, and estimates track by profile correlation. Post-processing is the stable mode (multithreaded, vectorised); a sliding-window real-time mode adds Kalman filtering. Outputs include true vs estimated tracks over the map, profile comparisons and speed/azimuth correlation heatmaps; a Webots simulation was used to generate test data.

**Why it matters:** A compact Python baseline with heatmaps over speed and azimuth, handy for visualising why altimeter matching is ambiguous.

**Build notes:** Run gui.py. README says post-processing is more stable than real time and that a 10 m altimeter error was tested. Demo videos are on Yandex Disk links.

## Deep dives

- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)
- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `lang:ru`, `tercom`, `nmea`, `barometric-altitude`, `webots`, `hackathon`, `python`

**Domains:** air

## Related

- alternative_to: [Hackathon-Blind-Flight (team GORIZONT)](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md)
- alternative_to: [FlyingBlind_Hakaton](../../catalog/repos/solarwarlock__flyingblind_hakaton.md)
- alternative_to: [KROT (Где мы, Бариста?) - terrain correlation from radar altimeter](../../catalog/repos/rub1kub__where-are-we-barista.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [The first three hours](../../docs/first-three-hours.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [Landscape: what reviewers already know](../../docs/landscape/README.md) (mentions)
- [Sources in Ukrainian and Russian](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [KROT (Где мы, Бариста?) - terrain correlation from radar altimeter](../../catalog/repos/rub1kub__where-are-we-barista.md) (alternative_to)
- [Хакатон: трек «Робототехника и сенсорика», кейс «Полёт вслепую»](../../catalog/resources/iqarium-polet-vslepuyu-hackathon-2026.md) (has_code)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-23._
