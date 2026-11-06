# VPAIR

`repo:aervisloc/vpair` - <https://github.com/AerVisLoc/vpair>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 61 | None | ? | 2026-11-01 | False | active-research | medium |

Repo for VPAIR, an aerial visual place recognition dataset matching low-altitude flight imagery to reference orthophotos.

**Why it matters:** Benchmark for UAV visual geolocalization against georeferenced maps.

**Hackathon notes:** Academic use only, commercial use prohibited (README). Full set is 20.5 GB (2,706 query/reference pairs plus 10,000 distractors); a 0.86 GB sample is on Zenodo. The repo itself holds only the README and images. Evaluate with VPR-methods-evaluation.

## Deep dives

- [vpair](../../docs/dataset-cards/vpair.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md)

**Tags:** `aerial`, `vpr`, `orthophoto`

**Domains:** air

## Related

- integrates_with: [VPR methods evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [aero-vloc](../../catalog/repos/prime-slam__aero-vloc.md) (evaluated_on)
- [VPAIR - Aerial Visual Place Recognition and Localization in Large-scale Outdoor Environments](../../catalog/resources/vpair-dataset-2022.md) (has_code)
- [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md) (uses)
- [Relative navigation benchmark on real data: KISS-ICP lidar odometry, OpenVINS VIO, mono and nadir VO, scored with evo](../../catalog/samples/relative-nav-benchmark.md) (uses)
- [Drone frame to orthophoto geolocalization with LightGlue](../../catalog/samples/visual-geolocalization-lightglue.md) (uses)

_Indexed by lane(s): sim-data_

_GitHub metadata fetched 2026-11-06._
