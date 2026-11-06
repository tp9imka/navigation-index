# Photo-SLAM

`repo:huajianup/photo-slam` - <https://github.com/HuajianUP/Photo-SLAM>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 781 | C++ | GPL-3.0 | 2024-06-12 | False | research-prototype | low |

Couples ORB-SLAM3-style geometric tracking with a photorealistic Gaussian map for monocular, stereo and RGB-D cameras (CVPR 2024).

**Why it matters:** Classic robust tracking plus a nice-looking map, closer to real time than pure splatting SLAM.

**Hackathon notes:** LibTorch + CUDA build; check version pins carefully. Licence: GPL-3.0 overall, but the repo also ships the Inria Gaussian-Splatting licence (LICENSE.md), which limits that code to non-commercial research use.

**Concepts:** [Visual SLAM](../../catalog/concepts/visual-slam.md)

**Tags:** `3dgs`, `orb-slam3`, `libtorch`

**Domains:** ground

## Related

- depends_on: [ORB-SLAM3](../../catalog/repos/uz-slamlab__orb_slam3.md)
- alternative_to: [MonoGS (Gaussian Splatting SLAM)](../../catalog/repos/muskie82__monogs.md)

## Referenced by

- [MonoGS (Gaussian Splatting SLAM)](../../catalog/repos/muskie82__monogs.md) (alternative_to)

_Indexed by lane(s): slam_

_GitHub metadata fetched 2026-11-06._
