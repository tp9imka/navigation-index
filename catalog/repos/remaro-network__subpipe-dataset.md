# SubPipe

`repo:remaro-network/subpipe-dataset` - <https://github.com/remaro-network/SubPipe-dataset>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 68 | Jupyter Notebook | GPL-3.0 | 2024-03-28 | False | research-prototype | medium |

Underwater dataset recorded by a lightweight AUV inspecting a submarine pipeline: two cameras, side-scan sonar (10,030 images, COCO/YOLO labels), segmentation masks and navigation data, for segmentation, detection and visual-inertial localization.

**Why it matters:** One of few open AUV datasets with a pose reference (estimated from the vehicle's own navigation sensors, not an external ground truth), useful for testing underwater VIO where GNSS never reaches.

**Hackathon notes:** Full set is ~80 GB unzipped on Zenodo; start with SubPipeMini (~12 GB) and run an off-the-shelf VIO to show drift underwater. Data CC BY 4.0, repo code GPL-3.0.

**Concepts:** [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [Underwater navigation](../concepts/underwater-nav.md), [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `auv`, `pipeline`, `side-scan-sonar`, `vio`

**Domains:** underwater

## Referenced by

- [SubPipe: A Submarine Pipeline Inspection Dataset for Segmentation and Visual-inertial Localization](../resources/subpipe-paper-2024.md) (has_code)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
