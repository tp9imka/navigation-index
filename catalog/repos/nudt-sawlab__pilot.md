# PiLoT

`repo:nudt-sawlab/pilot` - <https://github.com/nudt-sawlab/PiLoT>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 125 | Python | MIT | 2026-07-04 | False | active-research | medium |

Neural pixel-to-3D registration for UAV ego-localization and target geo-localization against a geo-referenced 3D map; release uses 3D Gaussian Splatting map backends (CVPR 2026).

**Why it matters:** Absolute 6-DoF pose from a 3D map is a strong GNSS-denied fix for low-altitude drones.

**Hackathon notes:** GPU-heavy (CUDA extension build, CityGaussian conda env); demo data is about 15 GB. Code is MIT, but PiLoT-data on HF is gated: non-commercial research or education only, no redistribution. From NUDT, which is on the US Entity List - check your programme's rules.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Visual SLAM](../concepts/visual-slam.md)

**Tags:** `3dgs`, `6dof`, `cvpr2026`, `map-based`

**Domains:** air

## Referenced by

- [PiLoT: Neural Pixel-to-3D Registration for UAV-based Ego and Target Geo-localization](../resources/pilot-pixel-to-3d-2026.md) (has_code)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
