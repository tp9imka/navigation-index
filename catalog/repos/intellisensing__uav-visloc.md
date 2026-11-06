# UAV-VisLoc dataset

`repo:intellisensing/uav-visloc` - <https://github.com/IntelliSensing/UAV-VisLoc>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 300 | Python | ? | 2024-05-22 | False | active-research | high |

Large-scale dataset of real UAV flight imagery with satellite reference maps for UAV visual localization across varied terrain.

**Why it matters:** Real nadir-ish drone frames with ground truth over large, non-urban areas - the closest public match to a GNSS-denied flight test.

**Hackathon notes:** Best dataset to test a visual-GPS demo; pick one flight and its map, run your matcher, plot error vs ground truth.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md)

**Tags:** `dataset`, `uav`, `satellite`, `absolute-localization`

**Domains:** air

## Related

- evaluated_on: [GeoAnchor](../repos/yusufgunel__geoanchor.md)
- integrates_with: [WildNav](../repos/tiers__wildnav.md)

## Referenced by

- [GeoAnchor](../repos/yusufgunel__geoanchor.md) (evaluated_on)
- [UAV-VisLoc: A Large-scale Dataset for UAV Visual Localization](../resources/uav-visloc-dataset-2024.md) (has_code)
- [Drone frame to orthophoto geolocalization with LightGlue](../samples/visual-geolocalization-lightglue.md) (uses)

_Indexed by lane(s): alt-nav, sim-data_

_GitHub metadata fetched 2026-11-06._
