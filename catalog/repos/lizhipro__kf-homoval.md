# KF-HomoVAL

`repo:lizhipro/kf-homoval` - <https://github.com/lizhipro/KF-HomoVAL>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 6 | Python | MIT | 2026-08-17 | False | research-prototype | medium |

6-DoF absolute visual localization for UAVs built on deep homography estimation between the drone view and a reference map, smoothed with a Kalman filter.

**Why it matters:** Homography-based registration gives full pose, not just a location, which helps when the camera is not nadir.

**Hackathon notes:** Pair with the STHN family for comparison; expect to retrain on your imagery.

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `homography`, `kalman`, `6dof`

**Domains:** air

## Related

- alternative_to: [STHN](../../catalog/repos/arplaboratory__sthn.md)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
