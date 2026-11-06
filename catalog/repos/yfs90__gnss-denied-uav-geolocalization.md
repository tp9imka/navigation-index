# GNSS-Denied UAV Geolocalization (terrain-weighted)

`repo:yfs90/gnss-denied-uav-geolocalization` - <https://github.com/YFS90/GNSS-Denied-UAV-Geolocalization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 86 |  | ? | 2024-11-28 | False | research-prototype | medium |

Code and demos for a UAV geolocalization system that combines image matching, visual odometry and a terrain-weighted constraint optimization, intended to work day and night.

**Why it matters:** Fuses absolute map matches with relative VO and terrain constraints - the hybrid structure a real GNSS-denied nav stack needs.

**Hackathon notes:** Check what is actually released before planning around it; mainly a reference for the fusion design.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Terrain-relative navigation](../concepts/terrain-nav.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Visual(-inertial) odometry](../concepts/vio.md)

**Tags:** `uav`, `optimization`, `terrain`, `night`

**Domains:** air

## Related

- alternative_to: [GeoAnchor](../repos/yusufgunel__geoanchor.md)

## Referenced by

- [GeoAnchor](../repos/yusufgunel__geoanchor.md) (alternative_to)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
