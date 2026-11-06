# GeoAnchor

`repo:yusufgunel/geoanchor` - <https://github.com/YusufGUNEL/GeoAnchor>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 7 | Python | NOASSERTION | 2026-10-27 | False | research-prototype | high |

Recent project fusing visual odometry with satellite-map matching in a particle filter for GNSS-denied UAV flight, with an explicit notion of when the map match should not be trusted; evaluated on UAV-VisLoc flights and with a browser demo.

**Why it matters:** Directly addresses the practical problem that per-frame map matching often fails (water, farmland, repetitive texture), and shows how to bridge with VO.

**Hackathon notes:** Very recent single-author project; good blueprint for a 48h demo combining VO drift with intermittent absolute fixes. Verify numbers yourself.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Visual(-inertial) odometry](../concepts/vio.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `particle-filter`, `uav-visloc`, `2026`

**Domains:** air

## Related

- evaluated_on: [UAV-VisLoc dataset](../repos/intellisensing__uav-visloc.md)
- alternative_to: [GNSS-Denied UAV Geolocalization (terrain-weighted)](../repos/yfs90__gnss-denied-uav-geolocalization.md)

## Referenced by

- [UAV-VisLoc dataset](../repos/intellisensing__uav-visloc.md) (evaluated_on)
- [GNSS-Denied UAV Geolocalization (terrain-weighted)](../repos/yfs90__gnss-denied-uav-geolocalization.md) (alternative_to)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
