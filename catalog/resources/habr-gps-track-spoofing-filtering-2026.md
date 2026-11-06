# Как фильтровать GPS-треки от ложных точек: спуфинг, заморозка координат, подмена времени

`res:habr-gps-track-spoofing-filtering-2026` - blog - <https://habr.com/ru/articles/1060790/>

**By:** Habr author - **Year:** 2026 - **Level:** intermediate - **Access:** open

English: 'How to filter GPS tracks for false points: spoofing, frozen coordinates, time spoofing' (July 2026). A fleet-telematics backend developer's rule set: a reachability envelope instead of a fixed speed cutoff, altitude-gradient checks against a terrain database, teleport-segment boundaries, frozen-series detection, a longest-non-decreasing-odometer filter against timestamp spoofing, GPS-path vs odometer ratio with hysteresis, and cell-tower fallback. Trust order: CAN, then cell, then GPS.

## Key takeaways

- Use an independent odometer to expose spoofed GPS (honest path/odometer ratio ~1.6-1.8x, a spoofed track hit 3.3x)
- Judge frozen coordinates as series, not points
- Store raw, filter at read time, regression-test on clean days

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `lang:ru`, `habr`, `spoofing-detection`, `telematics`, `typescript`

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_
