# ALFA dataset

`repo:castacks/alfa-dataset` - <https://github.com/castacks/alfa-dataset>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 20 |  | ? | 2020-07-23 | False | archived | medium |

Landing page for the AIR Lab Failure and Anomaly dataset: 47 processed autonomous fixed-wing flight sequences (ArduPilot on Pixhawk) with engine and control-surface faults, plus raw bags, telemetry and Dataflash logs.

**Why it matters:** Real small fixed-wing flights with full ArduPilot logs, usable to test airspeed/propulsion-aided dead reckoning against GPS truth on a real airframe, and engine-out segments test a propulsion model's failure case.

**Build notes:** KiltHub DOI 10.1184/R1/12707963: processed.zip 272 MB, dataflash.zip 541 MB. Repository metadata says CC BY 4.0 while the bundled README says CC0, both permissive. Sequences are short (most 1-4 min). Airspeed channel presence not checked.

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `fixed-wing`, `ardupilot`, `dataflash`, `fault`, `dataset`

**Domains:** air

## Related

- integrates_with: [ALFA dataset tools](../../catalog/repos/castacks__alfa-dataset-tools.md)
- evaluated_on: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)

## Referenced by

- [ALFA dataset tools](../../catalog/repos/castacks__alfa-dataset-tools.md) (integrates_with)
- [ALFA: A dataset for UAV fault and anomaly detection](../../catalog/resources/keipour-2021-alfa-dataset.md) (has_code)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-09._
