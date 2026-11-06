# Multi-frequency GNSS spoofing raw dataset

`repo:s7am1na/gnss-spoofing-dataset` - <https://github.com/S7AM1NA/GNSS-Spoofing-Dataset>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4 |  | MIT | 2025-12-07 | False | research-prototype | high |

Raw GNSS measurement logs from Android phones and smartwatches recorded under spoofing scenarios on L1, L5 and dual-band.

**Why it matters:** Labelled smartphone spoofing data is scarce; this enables training and testing detectors without generating signals.

**Hackathon notes:** Load logs with gnss_lib_py and build a consistency-check or ML detector. Verify labelling and scenario details in the README before trusting results.

## Deep dives

- [gnss-spoofing-s7am1na](../../docs/dataset-cards/gnss-spoofing-s7am1na.md) (dataset-cards)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `spoofing`, `dataset`, `android`, `l5`

**Domains:** dismounted

## Related

- integrates_with: [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md)
- depends_on: [GPS Measurement Tools (incl. GnssLogger)](../../catalog/repos/google__gps-measurement-tools.md)

## Referenced by

- [Export control and ethics](../../docs/export-control-and-ethics.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (explains)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
