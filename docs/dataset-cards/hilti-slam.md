# Hilti SLAM Challenge datasets (2021, 2022, 2023)

<!-- about: res:hilti-slam-challenge, repo:hilti-research/hilti-slam-challenge-2022, repo:hilti-research/hilti-slam-challenge-2023 -->

Handheld (and in 2023 robot-mounted) multi-sensor SLAM datasets from Hilti with ETH/UZH/Oxford partners, recorded on construction sites and historic buildings. Ground truth is survey-grade: sparse control points from a terrestrial laser scanner / total station, scored to millimetres. All three years are now on Hugging Face.

| Field | Value |
|---|---|
| Platform | 2021: handheld rig. 2022: handheld "Phasma". 2023: Phasma handheld + sensor suite on a tracked drilling robot |
| Environment | Offices, labs, basements, parking deck, campus, construction sites (2021); construction site in Schaan, Liechtenstein and the Sheldonian Theatre, Oxford (2022); three active construction sites, multi-session (2023) |
| Sensors and rates | 2022: 5 synchronized global-shutter cameras (Sevensense Alphasense, frames C0-C4), Hesai PandarXT-32 lidar, Bosch BMI085 IMU (HF card). 2021 includes a Livox lidar (custom msg). Rates not stated on the cards read |
| Ground truth | 2022: sparse 3-DoF control points for most sequences plus dense 6-DoF IMU-frame trajectories for selected `_imu` ones; high-accuracy laser scans. 2023: control points from a terrestrial laser scanner. Paper title for 2022: "A Millimeter-Accurate Benchmark" |
| Size | HF API usedStorage: 2021 198.2 GB, 2022 349.8 GB, 2023 369.5 GB. 2022 bags 6.3-35.4 GB each (smallest exp14_basement_2.bag 6.26 GB); 2023 smallest site2_handheld_4.bag 10.04 GB (HF tree API, 2026-11-06) |
| License | CC BY-NC-SA 3.0 (HF cards, all three years) |
| Format | ROS1 bags; ground truth TXT (TUM-style); calibration YAML + Kalibr reports; CAD of the rig |
| Index | [Hilti SLAM Challenge](../../catalog/resources/hilti-slam-challenge.md), [2022 repo](../../catalog/repos/hilti-research__hilti-slam-challenge-2022.md), [2023 repo](../../catalog/repos/hilti-research__hilti-slam-challenge-2023.md) |

## What's in it

- 2021: 12 sequences, sparse 3-DoF or continuous 6-DoF reference per sequence.
- 2022: 16 sequences (exp01..exp23), multi-level, stairs, long corridors, outdoor, a three-part Sheldonian loop; ~336 GB of bags, 7.1 GB calibration.
- 2023: 12 challenge sequences over 3 sites + 3 extra handheld Site 2 sequences; multi-session (align all runs of a site to its `_1` run). Site 3 has intentional frame drops.

## Download

```bash
HF=https://huggingface.co/datasets/Hilti-Research/hilti-slam-challenge-2022/resolve/main
# Smallest 2022 bag with dense 6-DoF GT (6.3 GB)
wget $HF/rosbags/exp14_basement_2.bag
wget $HF/ground_truth/exp14_basement_2_imu.txt
# Whole year with the HF CLI (venv)
huggingface-cli download Hilti-Research/hilti-slam-challenge-2022 --repo-type dataset \
  --include "rosbags/exp14*" "ground_truth/*" "calibration/calibration_files/*" --local-dir hilti22
```

Use `huggingface-cli --include` for directories; plain wget only works per file.

## Loading and tooling

- URDF of the rig: `phasma_description`, `hesai_description`, `alphasense_description` (Hilti-Research GitHub).
- Hesai driver stores one timestamp per scan; the 2022 FAQ explains how to recover per-point times before using deskewing LIO.
- LIO/VIO: [FAST-LIO](../../catalog/repos/hku-mars__fast_lio.md), [LIO-SAM](../../catalog/repos/tixiaoshan__lio-sam.md), [KISS-ICP](../../catalog/repos/prbonn__kiss-icp.md), [OpenVINS](../../catalog/repos/rpng__open_vins.md), [OKVIS2](../../catalog/repos/ethz-mrl__okvis2.md).
- Scoring: submissions in TUM format; [evo](../../catalog/repos/michaelgrupp__evo.md) against the dense `_imu` GT. 2023 points table: <0.5 cm => 20 points ... >40 cm => 0.

## Hackathon fit

- Dismounted / indoor GNSS-denied navigation (stairs, multi-floor): the closest public match to a soldier or responder carrying a sensor rig through a building.
- Idea 19 (cooperative localization): 2023 multi-session, multi-platform data is a ready "two agents map the same site" scenario.
- Idea 10 for handheld VIO/LIO with survey-grade truth.

## Pitfalls

- Big bags (6-35 GB each); decide one sequence per team member.
- Most GT is sparse control points, not continuous trajectories; ATE over the whole run is only possible on `_imu` sequences.
- Hesai per-point timestamps need fixing for deskewing.
- 2023 Site 2 extra handheld sequences contain rapidly flashing lights (photosensitivity warning on HF card).
- Non-commercial license.

## Sources

- HF API and README for Hilti-Research/hilti-slam-challenge-2021, -2022, -2023 (sizes, contents, license, sensors 2022)
- `gh api repos/Hilti-Research/hilti-slam-challenge-2022/readme` and `-2023/readme` (FAQ: GT, frames, Hesai timestamps, scoring, frame drops)
