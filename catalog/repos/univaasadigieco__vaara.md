# VAARA Jammertest dataset

`repo:univaasadigieco/vaara` - <https://github.com/UniVaasaDigiEco/VAARA>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 2 |  | ? | 2026-04-06 | False | active-research | medium |

University of Vaasa public GNSS dataset recorded at Jammertest 2024, released in batches from autumn 2025 under a Finland-NSF project on secure satellite navigation.

**Why it matters:** Second independent real-world interference dataset, useful for cross-dataset validation of detectors.

**Build notes:** Check README for which batches are released; pair with the Jammertest plan for labels.

## Deep dives

- [jammertest-data](../../docs/dataset-cards/jammertest-data.md) (dataset-cards)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `jammertest`, `dataset`, `spoofing`, `jamming`

**Domains:** multi

## Related

- evaluated_on: [Jammertest test plan](../../catalog/repos/npra__jammertest-plan.md)
- alternative_to: [Fraunhofer IIS Jammertest 2025 dataset](../../catalog/repos/felixott94__fraunhoferiis_jammertest2025.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Dataset cards](../../docs/dataset-cards/README.md) (mentions)
- [The first three hours](../../docs/first-three-hours.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [Fraunhofer IIS Jammertest 2025 dataset](../../catalog/repos/felixott94__fraunhoferiis_jammertest2025.md) (alternative_to)
- [Jammertest test plan](../../catalog/repos/npra__jammertest-plan.md) (integrates_with)
- [Data-Driven Analysis of PNT Resilience: Insights and Lessons from Jammertest 2024 Vehicular Data](../../catalog/resources/jammertest-2024-vehicular-pnt-resilience.md) (has_code)
- [Jammertest - open GNSS jamming and spoofing test event (Andoya, Norway)](../../catalog/resources/jammertest-norway.md) (dataset_for)
- [Most resilient GNSS receiver: results from Jammertest in Norway](../../catalog/resources/septentrio-jammertest-results.md) (dataset_for)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (uses)
- [Real attack replay: Jammertest 2024 u-blox logs through the GNSS interference monitor, with RTKLIB SPP](../../catalog/samples/real-attack-replay.md) (uses)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-23._
