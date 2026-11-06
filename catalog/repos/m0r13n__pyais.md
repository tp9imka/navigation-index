# pyais

`repo:m0r13n/pyais` - <https://github.com/M0r13n/pyais>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 263 | Python | MIT | 2026-11-01 | False | production | high |

Python library for decoding and encoding AIS NMEA sentences (AIVDM/AIVDO), including multi-part messages and streaming from sockets or files.

**Why it matters:** The quickest path from raw AIS sentences to typed vessel positions for maritime picture building or AIS spoofing/anomaly detection.

**Hackathon notes:** pip install pyais, point it at a public AIS TCP feed or a recorded NMEA file, and you have vessel tracks in an hour. Pair with AIS-catcher for live RF.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [m0r13n__pyais](../../docs/integration-cards/m0r13n__pyais.md) (integration-cards)
- [dma-ais](../../docs/dataset-cards/dma-ais.md) (dataset-cards)

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Tracking and data association](../../catalog/concepts/target-tracking.md)

**Tags:** `ais`, `nmea`, `decoder`, `python`

**Domains:** maritime

## Related

- integrates_with: [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md)
- alternative_to: [noaadata](../../catalog/repos/schwehr__noaadata.md)
- integrates_with: [Stone Soup](../../catalog/repos/dstl__stone-soup.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md) (integrates_with)
- [noaadata](../../catalog/repos/schwehr__noaadata.md) (alternative_to)
- [Danish Maritime Authority historical AIS data](../../catalog/resources/dma-historical-ais.md) (has_code)
- [ITU-R M.1371-6 - Technical characteristics for VHF automatic identification system using time division multiple access in the maritime mobile service](../../catalog/resources/itu-r-m1371-ais.md) (explains)
- [GNSS spoofing signatures in real AIS tracks: detectors, injected ground truth, GeoJSON and CoT](../../catalog/samples/maritime-ais-spoofing.md) (uses)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
