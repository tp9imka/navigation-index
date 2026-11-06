# UASTHN

`repo:arplaboratory/uasthn` - <https://github.com/arplaboratory/UASTHN>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 27 | Jupyter Notebook | MIT | 2026-02-28 | False | active-research | medium |

ICRA 2025 extension of STHN that adds uncertainty estimation to satellite-thermal homography, so the system can say when a fix is unreliable.

**Why it matters:** Calibrated uncertainty is what lets a nav filter safely ingest visual fixes.

**Hackathon notes:** Feed its uncertainty into your EKF measurement covariance.

## Deep dives

- [uasthn-uncertainty-thermal-2025](../../docs/paper-digests/uasthn-uncertainty-thermal-2025.md) (paper-digests)

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md)

**Tags:** `thermal`, `uncertainty`

**Domains:** air

## Related

- extends: [STHN](../repos/arplaboratory__sthn.md)

## Referenced by

- [Satellite-thermal geo-localization](../repos/arplaboratory__satellite-thermal-geo-localization.md) (same_org)
- [STHN](../repos/arplaboratory__sthn.md) (same_org)
- [UASTHN: Uncertainty-Aware Deep Homography Estimation for UAV Satellite-Thermal Geo-localization](../resources/uasthn-uncertainty-thermal-2025.md) (has_code)
- [Integrity monitoring for alt-PNT: solution-separation FDE, protection levels and a Stanford diagram](../samples/altpnt-integrity.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
