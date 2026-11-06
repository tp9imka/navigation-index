# GNSS-SDR

`repo:gnss-sdr/gnss-sdr` - <https://github.com/gnss-sdr/gnss-sdr>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 2,324 | C++ | GPL-3.0 | 2026-11-05 | False | production | high |

Full software-defined GNSS receiver built on GNU Radio: acquisition, tracking, navigation message decoding and PVT for GPS, Galileo, GLONASS and BeiDou signals from SDR front-ends or IQ files, including Galileo OSNMA support.

**Why it matters:** The most complete open receiver for experimenting with signal-level defenses (tracking monitors, authentication, interference) on real or simulated IQ.

**Hackathon notes:** Install from distro packages (apt install gnss-sdr) to skip a long build. Feed it GPS-SDR-SIM or recorded IQ files; works with HackRF/USRP/RTL-SDR front-ends.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [gnss-sdr__gnss-sdr](../../docs/integration-cards/gnss-sdr__gnss-sdr.md) (integration-cards)
- [texbat](../../docs/dataset-cards/texbat.md) (dataset-cards)

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Software-defined GNSS receivers](../concepts/gnss-sdr.md), [Jamming and spoofing](../concepts/gnss-interference.md)

**Tags:** `gnu-radio`, `receiver`, `osnma`, `iq`, `c++`

**Domains:** multi

## Related

- integrates_with: [GPS-SDR-SIM](../repos/osqzss__gps-sdr-sim.md)
- integrates_with: [OSNMAlib](../repos/algafix__osnma.md)
- integrates_with: [OSNMA-SDR-SIM](../repos/haiyang-wong__osnma-sdr-sim.md)

## Referenced by

- [OSNMAlib](../repos/algafix__osnma.md) (integrates_with)
- [CU Boulder GNSS SDR Collection](../repos/gnsscusdr__cu-sdr-collection.md) (alternative_to)
- [OSNMA-SDR-SIM](../repos/haiyang-wong__osnma-sdr-sim.md) (integrates_with)
- [GPS-SDR-SIM](../repos/osqzss__gps-sdr-sim.md) (integrates_with)
- [GNSS-DSP-tools](../repos/pmonta__gnss-dsp-tools.md) (alternative_to)
- [PocketSDR](../repos/tomojitakasu__pocketsdr.md) (alternative_to)
- [BeiDou Navigation Satellite System Signal-In-Space ICDs (B1I, B3I, B1C, B2a, B2b)](../resources/beidou-icd-library.md) (has_code)
- [A Software-Defined GPS and Galileo Receiver: A Single-Frequency Approach](../resources/borre-software-defined-gps-galileo-receiver.md) (has_code)
- [Galileo Open Service Signal-In-Space Interface Control Document (OS SIS ICD) Issue 2.1](../resources/galileo-os-sis-icd-2-1.md) (explains)
- [Galileo Open Service Signal-In-Space Interface Control Document (OS SIS ICD) Issue 2.1](../resources/galileo-os-sis-icd-2-1.md) (has_code)
- [GNSS-SDR documentation](../resources/gnss-sdr-docs.md) (explains)
- [GNSS-SDR tutorials](../resources/gnss-sdr-tutorials.md) (has_code)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../resources/gps-is-gps-200n.md) (explains)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../resources/gps-is-gps-200n.md) (has_code)
- [IS-GPS-705J: NAVSTAR GPS Space Segment / User Segment L5 Interfaces](../resources/gps-is-gps-705j.md) (has_code)
- [IS-GPS-800J: NAVSTAR GPS Space Segment / User Segment L1C Interfaces](../resources/gps-is-gps-800j.md) (has_code)
- [infiniDome GPSdome / GPSdome 2 small-UAS anti-jam module](../resources/infinidome-gpsdome.md) (alternative_to)
- [Safran VersaPNT and Geonyx resilient PNT units](../resources/safran-versapnt.md) (alternative_to)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
