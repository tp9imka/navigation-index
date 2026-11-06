# NRC UAV vs bird radar tracks

`repo:nrc-cnrc/cuas-sensing-dataset` - <https://github.com/nrc-cnrc/CUAS-sensing-dataset>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 |  | CC-BY-4.0 | 2026-10-02 | False | active-research | high |

Labelled real-world radar tracks of small UAVs, birds, humans and vehicles from an Echodyne EchoGuard radar over several Canadian field trials.

**Why it matters:** Radar track classification (drone vs bird) is central to C-UAS beyond micro-Doppler range; open labelled radar data is scarce.

**Hackathon notes:** Train a kinematic-feature classifier on the tracks; no RF hardware needed.

## Deep dives

- [nrc-cuas-sensing](../../docs/dataset-cards/nrc-cuas-sensing.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Tracking and data association](../../catalog/concepts/target-tracking.md)

**Tags:** `radar`, `tracks`, `echodyne`, `drone-vs-bird`

**Domains:** air

## Related

- alternative_to: [Drone-vs-Bird Detection Challenge](../../catalog/repos/wosdetc__challenge.md)

## Referenced by

- [DroneRF dataset: A dataset of drones for RF-based detection, classification, and identification](../../catalog/resources/dronerf-mendeley-dataset.md) (uses)
- [C-UAS classifiers on public data: radar tracks (UAV vs bird) and DroneRF spectra](../../catalog/samples/cuas-classifiers.md) (uses)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
