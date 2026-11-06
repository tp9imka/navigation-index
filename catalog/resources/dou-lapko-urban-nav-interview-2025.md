# У 17 років створив навігацію для дронів, яку не глушить РЕБ. Історія киянина, який переміг на «Олімпіаді геніїв» у США

`res:dou-lapko-urban-nav-interview-2025` - blog - <https://dou.ua/lenta/interviews/developer-of-autonomous-drone/>

**By:** Eleonora Burdina, DOU.ua - **Year:** 2025 - **Level:** intro - **Access:** open

English: 'Built EW-proof drone navigation at 17: the story of a Kyiv student who won the Genius Olympiad in the USA'. Describes an urban GNSS-free concept: an IMU dead-reckons, side-looking rangefinders measure distances to buildings at roughly 7th-floor height, and the ranges are matched to OpenStreetMap building geometry about once per second. Simulation in C#/MonoGame; hardware tests on a Betaflight FPV were at bench stage.

## Key takeaways

- Rangefinder-to-building matching against OSM is a cheap urban alternative to camera VPS
- Correction at ~1 Hz bounds IMU drift
- Status at publication: simulation plus bench tests, not flight-proven

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

**Tags:** `lang:uk`, `dou`, `osm`, `rangefinder`, `student`

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-sources_
