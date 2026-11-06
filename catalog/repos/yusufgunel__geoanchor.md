# GeoAnchor

`repo:yusufgunel/geoanchor` - <https://github.com/YusufGUNEL/GeoAnchor>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 7 | Python | NOASSERTION | 2026-10-27 | False | research-prototype | high |

Recent project fusing visual odometry with satellite-map matching in a particle filter for GNSS-denied UAV flight, with an explicit notion of when the map match should not be trusted; evaluated on UAV-VisLoc flights and with a browser demo.

**Why it matters:** Directly addresses the practical problem that per-frame map matching often fails (water, farmland, repetitive texture), and shows how to bridge with VO.

**Hackathon notes:** Very recent single-author project; good blueprint for a 48h demo combining VO drift with intermittent absolute fixes. Verify numbers yourself.

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `particle-filter`, `uav-visloc`, `2026`

**Domains:** air

## Related

- evaluated_on: [UAV-VisLoc dataset](../../catalog/repos/intellisensing__uav-visloc.md)
- alternative_to: [GNSS-Denied UAV Geolocalization (terrain-weighted)](../../catalog/repos/yfs90__gnss-denied-uav-geolocalization.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [UAV-VisLoc dataset](../../catalog/repos/intellisensing__uav-visloc.md) (evaluated_on)
- [GNSS-Denied UAV Geolocalization (terrain-weighted)](../../catalog/repos/yfs90__gnss-denied-uav-geolocalization.md) (alternative_to)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
