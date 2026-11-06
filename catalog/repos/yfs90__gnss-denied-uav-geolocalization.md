# GNSS-Denied UAV Geolocalization (terrain-weighted)

`repo:yfs90/gnss-denied-uav-geolocalization` - <https://github.com/YFS90/GNSS-Denied-UAV-Geolocalization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 86 |  | ? | 2024-11-28 | False | research-prototype | low |

Project page for a UAV geolocalization system that combines image matching, visual odometry and a terrain-weighted constraint optimization, intended to work day and night. The repo holds only the README, result figures and demo video links - no code is released.

**Why it matters:** Fuses absolute map matches with relative VO and terrain constraints - the hybrid structure a real GNSS-denied nav stack needs.

**Hackathon notes:** No code, data or weights are released (README, figures and videos only); use it only as a reference for the fusion design.

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `uav`, `optimization`, `terrain`, `night`

**Domains:** air

## Related

- alternative_to: [GeoAnchor](../../catalog/repos/yusufgunel__geoanchor.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [GeoAnchor](../../catalog/repos/yusufgunel__geoanchor.md) (alternative_to)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
