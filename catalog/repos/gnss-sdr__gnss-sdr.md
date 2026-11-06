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

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `gnu-radio`, `receiver`, `osnma`, `iq`, `c++`

**Domains:** multi

## Related

- integrates_with: [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md)
- integrates_with: [OSNMAlib](../../catalog/repos/algafix__osnma.md)
- integrates_with: [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Export control and ethics](../../docs/export-control-and-ethics.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [OSNMAlib](../../catalog/repos/algafix__osnma.md) (integrates_with)
- [CU Boulder GNSS SDR Collection](../../catalog/repos/gnsscusdr__cu-sdr-collection.md) (alternative_to)
- [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md) (integrates_with)
- [Приемники ГНСС - GNSS receiver design handbook (MPEI)](../../catalog/repos/korogodin__gnssrec.md) (integrates_with)
- [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md) (integrates_with)
- [GNSS-DSP-tools](../../catalog/repos/pmonta__gnss-dsp-tools.md) (alternative_to)
- [PocketSDR](../../catalog/repos/tomojitakasu__pocketsdr.md) (alternative_to)
- [BeiDou Navigation Satellite System Signal-In-Space ICDs (B1I, B3I, B1C, B2a, B2b)](../../catalog/resources/beidou-icd-library.md) (has_code)
- [A Software-Defined GPS and Galileo Receiver: A Single-Frequency Approach](../../catalog/resources/borre-software-defined-gps-galileo-receiver.md) (has_code)
- [Galileo Open Service Signal-In-Space Interface Control Document (OS SIS ICD) Issue 2.1](../../catalog/resources/galileo-os-sis-icd-2-1.md) (explains)
- [Galileo Open Service Signal-In-Space Interface Control Document (OS SIS ICD) Issue 2.1](../../catalog/resources/galileo-os-sis-icd-2-1.md) (has_code)
- [GNSS-SDR documentation](../../catalog/resources/gnss-sdr-docs.md) (explains)
- [GNSS-SDR tutorials](../../catalog/resources/gnss-sdr-tutorials.md) (has_code)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../../catalog/resources/gps-is-gps-200n.md) (explains)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../../catalog/resources/gps-is-gps-200n.md) (has_code)
- [IS-GPS-705J: NAVSTAR GPS Space Segment / User Segment L5 Interfaces](../../catalog/resources/gps-is-gps-705j.md) (has_code)
- [IS-GPS-800J: NAVSTAR GPS Space Segment / User Segment L1C Interfaces](../../catalog/resources/gps-is-gps-800j.md) (has_code)
- [infiniDome GPSdome / GPSdome 2 small-UAS anti-jam module](../../catalog/resources/infinidome-gpsdome.md) (alternative_to)
- [Safran VersaPNT and Geonyx resilient PNT units](../../catalog/resources/safran-versapnt.md) (alternative_to)
- [File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer](../../catalog/samples/gnss-signal-chain.md) (uses)
- [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md) (uses)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
