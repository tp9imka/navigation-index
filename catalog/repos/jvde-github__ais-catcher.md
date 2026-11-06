# AIS-catcher

`repo:jvde-github/ais-catcher` - <https://github.com/jvde-github/AIS-catcher>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 807 | C++ | GPL-3.0 | 2026-11-04 | False | production | high |

AIS receiver and decoder for cheap SDRs (RTL-SDR, Airspy, HackRF, SDRplay, SoapySDR) with a built-in web map, JSON/NMEA output and feed sharing.

**Why it matters:** Turns a 30-dollar dongle into a live maritime picture sensor, the cheapest real RF input for a maritime awareness build.

**Hackathon notes:** Prebuilt binaries and Docker image; plug an RTL-SDR with a VHF antenna, run with the web viewer enabled, forward NMEA to pyais or OpenCPN. Inland sites may see few ships.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [jvde-github__ais-catcher](../../docs/integration-cards/jvde-github__ais-catcher.md) (integration-cards)

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md)

**Tags:** `ais`, `sdr`, `rtl-sdr`, `receiver`

**Domains:** maritime

## Related

- integrates_with: [pyais](../../catalog/repos/m0r13n__pyais.md)
- integrates_with: [OpenCPN](../../catalog/repos/opencpn__opencpn.md)

## Referenced by

- [Export control and ethics](../../docs/export-control-and-ethics.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [pyais](../../catalog/repos/m0r13n__pyais.md) (integrates_with)
- [OpenCPN](../../catalog/repos/opencpn__opencpn.md) (integrates_with)
- [ITU-R M.1371-6 - Technical characteristics for VHF automatic identification system using time division multiple access in the maritime mobile service](../../catalog/resources/itu-r-m1371-ais.md) (explains)
- [GNSS spoofing signatures in real AIS tracks: detectors, injected ground truth, GeoJSON and CoT](../../catalog/samples/maritime-ais-spoofing.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
