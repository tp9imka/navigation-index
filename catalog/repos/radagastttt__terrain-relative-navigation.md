# Terrain-Relative Navigation (particle filter on DEM)

`repo:radagastttt/terrain-relative-navigation` - <https://github.com/radagastttt/terrain-relative-navigation>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Python | ? | 2026-11-02 | False | educational | high |

Personal Python prototype of terrain-relative navigation: matches a height profile along the route against a DEM and estimates position with a particle filter from an imprecise start. Simulates altimeter noise, bias and outliers, and was exercised on synthetic maps and Copernicus GLO-30 tiles for three Bulgarian areas from flat to mountainous. README in Russian.

**Why it matters:** Clean, self-contained particle-filter TRN with a noise model, a good teaching companion to the hackathon correlation solutions.

**Hackathon notes:** Laptop-only; load a GeoTIFF or generate a synthetic DEM. Swap its measurement model for real radar-altimeter logs to compare against NCC-based TERCOM.

## Deep dives

- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)
- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `lang:ru`, `trn`, `particle-filter`, `copernicus-dem`, `python`

**Domains:** air

## Related

- alternative_to: [Gagarin - TERCOM for UAVs without GNSS](../../catalog/repos/danilka88__gag27062026.md)
- alternative_to: [python-tercom](../../catalog/repos/alti3__python-tercom.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-06._
