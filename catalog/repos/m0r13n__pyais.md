# pyais

`repo:m0r13n/pyais` - <https://github.com/M0r13n/pyais>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 263 | Python | MIT | 2026-11-01 | False | production | high |

Python library for decoding and encoding AIS NMEA sentences (AIVDM/AIVDO), including multi-part messages and streaming from sockets or files.

**Why it matters:** The quickest path from raw AIS sentences to typed vessel positions for maritime picture building or AIS spoofing/anomaly detection.

**Hackathon notes:** pip install pyais, point it at a public AIS TCP feed or a recorded NMEA file, and you have vessel tracks in an hour. Pair with AIS-catcher for live RF.

**Concepts:** [Maritime navigation](../concepts/maritime-nav.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Tracking and data association](../concepts/target-tracking.md)

**Tags:** `ais`, `nmea`, `decoder`, `python`

**Domains:** maritime

## Related

- integrates_with: [AIS-catcher](../repos/jvde-github__ais-catcher.md)
- alternative_to: [noaadata](../repos/schwehr__noaadata.md)
- integrates_with: [Stone Soup](../repos/dstl__stone-soup.md)

## Referenced by

- [AIS-catcher](../repos/jvde-github__ais-catcher.md) (integrates_with)
- [noaadata](../repos/schwehr__noaadata.md) (alternative_to)
- [ITU-R M.1371 - Technical characteristics for an automatic identification system using TDMA in the VHF maritime mobile band](../resources/itu-r-m1371-ais.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
