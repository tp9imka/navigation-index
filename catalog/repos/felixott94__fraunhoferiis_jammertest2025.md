# Fraunhofer IIS Jammertest 2025 dataset

`repo:felixott94/fraunhoferiis_jammertest2025` - <https://github.com/FelixOtt94/FraunhoferIIS_Jammertest2025>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 5 | Python | ? | 2026-08-26 | False | active-research | high |

Real-world GNSS interference recordings from Jammertest 2025 at Andoya, Norway, covering jamming, spoofing, meaconing and multi-emitter scenarios, with metadata for classification, characterization and direction finding.

**Why it matters:** Rare open real-world interference data from live jamming trials, suited to training and testing interference detectors and classifiers.

**Hackathon notes:** Data is chunked HDF5 under dataset/ (Git LFS; the README points to an identical GitLab mirror for the full download) plus train/test split lists. There are no loader modules - the README only gives an h5py inspection snippet, so budget time to write your own loader before building a jamming/spoofing classifier on one scenario class.

## Deep dives

- [jammertest-data](../../docs/dataset-cards/jammertest-data.md) (dataset-cards)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md)

**Tags:** `jammertest`, `spoofing`, `jamming`, `meaconing`, `dataset`

**Domains:** multi

## Related

- evaluated_on: [Jammertest test plan](../../catalog/repos/npra__jammertest-plan.md)
- alternative_to: [VAARA Jammertest dataset](../../catalog/repos/univaasadigieco__vaara.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Towards Jammer Fingerprinting](../../catalog/repos/helsinki-sda-group__towards-jammer-fingerprinting.md) (integrates_with)
- [Jammertest test plan](../../catalog/repos/npra__jammertest-plan.md) (integrates_with)
- [VAARA Jammertest dataset](../../catalog/repos/univaasadigieco__vaara.md) (alternative_to)
- [GNSS Interference Spectrum Highway Dataset 1](../../catalog/resources/fraunhofer-gnss-interference-highway-dataset.md) (same_author)
- [Analyzing and Characterizing Multi-Source Interference Effects at Jammertest Norway 2025](../../catalog/resources/jammertest-2025-multi-source-interference.md) (uses)
- [Jammertest - open GNSS jamming and spoofing test event (Andoya, Norway)](../../catalog/resources/jammertest-norway.md) (dataset_for)
- [Most resilient GNSS receiver: results from Jammertest in Norway](../../catalog/resources/septentrio-jammertest-results.md) (dataset_for)
- [Low-cost GNSS jammer sensor network: u-blox telemetry => localization => TAK and dashboard](../../catalog/samples/jammer-sensor-network.md) (explains)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
