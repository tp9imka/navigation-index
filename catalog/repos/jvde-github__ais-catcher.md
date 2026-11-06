# AIS-catcher

`repo:jvde-github/ais-catcher` - <https://github.com/jvde-github/AIS-catcher>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 807 | C++ | GPL-3.0 | 2026-11-04 | False | production | high |

AIS receiver and decoder for cheap SDRs (RTL-SDR, Airspy, HackRF, SDRplay, SoapySDR) with a built-in web map, JSON/NMEA output and feed sharing.

**Why it matters:** Turns a 30-dollar dongle into a live maritime picture sensor, the cheapest real RF input for a maritime awareness build.

**Hackathon notes:** Prebuilt binaries and Docker image; plug an RTL-SDR with a VHF antenna, run with the web viewer enabled, forward NMEA to pyais or OpenCPN. Inland sites may see few ships.

**Concepts:** [Maritime navigation](../concepts/maritime-nav.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Software-defined GNSS receivers](../concepts/gnss-sdr.md)

**Tags:** `ais`, `sdr`, `rtl-sdr`, `receiver`

**Domains:** maritime

## Related

- integrates_with: [pyais](../repos/m0r13n__pyais.md)
- integrates_with: [OpenCPN](../repos/opencpn__opencpn.md)

## Referenced by

- [pyais](../repos/m0r13n__pyais.md) (integrates_with)
- [OpenCPN](../repos/opencpn__opencpn.md) (integrates_with)
- [ITU-R M.1371 - Technical characteristics for an automatic identification system using TDMA in the VHF maritime mobile band](../resources/itu-r-m1371-ais.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
