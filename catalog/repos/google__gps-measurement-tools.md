# GPS Measurement Tools (incl. GnssLogger)

`repo:google/gps-measurement-tools` - <https://github.com/google/gps-measurement-tools>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 842 | Java | Apache-2.0 | 2026-10-19 | False | production | high |

Google's Android raw GNSS measurement tooling: the GnssLogger app source, MATLAB analysis tools for pseudorange processing (including a RINEX nav reader), and NMEA utilities.

**Why it matters:** The canonical way to capture raw pseudoranges and carrier phase from phones, the basis for smartphone spoofing and integrity research.

**Hackathon notes:** Install GnssLogger from the Play Store and log on any recent Android phone; parse logs with gnss_lib_py.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [google__gps-measurement-tools](../../docs/integration-cards/google__gps-measurement-tools.md) (integration-cards)
- [gsdc](../../docs/dataset-cards/gsdc.md) (dataset-cards)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `android`, `gnsslogger`, `raw-measurements`, `matlab`, `raw-gnss`

**Domains:** dismounted, ground

## Related

- integrates_with: [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md)
- integrates_with: [GSDC 2023 solution (taroz)](../../catalog/repos/taroz__gsdc2023.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Multi-frequency GNSS spoofing raw dataset](../../catalog/repos/s7am1na__gnss-spoofing-dataset.md) (depends_on)
- [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md) (integrates_with)
- [GSDC 2023 solution (taroz)](../../catalog/repos/taroz__gsdc2023.md) (evaluated_on)
- [GSDC 2023 solution (taroz)](../../catalog/repos/taroz__gsdc2023.md) (integrates_with)
- [Detect GNSS jamming and spoofing (Android developer guide)](../../catalog/resources/android-gnss-spoof-jam-detection.md) (uses)
- [Raw GNSS Measurements](../../catalog/resources/android-raw-gnss-developer-guide.md) (explains)
- [Android Raw GNSS Measurement Datasets for Precise Positioning](../../catalog/resources/google-android-raw-gnss-datasets.md) (has_code)
- [Google Smartphone Decimeter Challenge 2023-2024](../../catalog/resources/google-gsdc-2023.md) (uses)
- [Detecting GNSS Jamming and Spoofing on Android Devices](../../catalog/resources/ion-webinar-akos.md) (uses)
- [GPS: An Introduction to Satellite Navigation, with an interactive Worldwide Laboratory using Smartphones](../../catalog/resources/stanford-gps-mooc-van-diggelen-enge.md) (uses)

_Indexed by lane(s): gnss, sim-data_

_GitHub metadata fetched 2026-11-06._
