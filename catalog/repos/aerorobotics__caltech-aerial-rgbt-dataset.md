# CART - Caltech Aerial RGB-Thermal

`repo:aerorobotics/caltech-aerial-rgbt-dataset` - <https://github.com/aerorobotics/caltech-aerial-rgbt-dataset>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 94 | Python | NOASSERTION | 2025-01-10 | False | active-research | medium |

Aerial RGB plus thermal dataset from natural terrain (rivers, coasts, deserts, forests) with GPS and inertial data, plus benchmarks for segmentation, RGB-to-thermal translation and VIO.

**Why it matters:** Thermal-aerial data with GPS/IMU is rare; it supports night-time visual and thermal navigation research without flying your own sensor rig.

**Hackathon notes:** Use the VIO benchmark to test thermal-inertial odometry, or train RGB-to-thermal translation to build synthetic thermal maps. The labelled subset downloads directly; raw data are ROS1 bags from an S3 bucket. Non-commercial only: data.caltech.edu lists CC BY-NC 4.0 (README says CC BY-SA 4.0, non-commercial).

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md)

**Tags:** `thermal`, `rgbt`, `aerial`, `caltech`

**Domains:** air

## Related

- alternative_to: [Satellite-thermal geo-localization](../../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md)

## Referenced by

- [Caltech Aerial RGB-Thermal Dataset in the Wild](../../catalog/resources/cart-caltech-aerial-rgbt-2024.md) (has_code)
- [Night / thermal UAV frame to RGB satellite geolocalization with a no-false-fix gate (ALIKED / DISK / SIFT + LightGlue, SGM baseline, Thermal-UAV)](../../catalog/samples/thermal-geolocalization.md) (explains)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
