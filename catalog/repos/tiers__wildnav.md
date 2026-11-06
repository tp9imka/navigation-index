# WildNav

`repo:tiers/wildnav` - <https://github.com/TIERS/wildnav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 286 | Python | BSD-3-Clause | 2025-06-12 | False | research-prototype | high |

Python pipeline that localizes a drone by matching its downward camera frames against georeferenced satellite map tiles with SuperGlue, then converts the best match into GPS coordinates. Companion code to the 'Vision-based GNSS-Free Localization for UAVs in the Wild' paper.

**Why it matters:** The canonical small, readable reference for absolute visual localization over non-urban terrain - exactly the 'visual GPS' building block a GNSS-denied team needs.

**Hackathon notes:** Clone, drop in your own map tiles with corner coordinates and a few drone photos; runs on a laptop GPU. Brute-force tile search is slow - add a retrieval stage (AnyLoc/SALAD) to prune candidates.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Feature detection and matching](../concepts/feature-matching.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `uav`, `satellite-map`, `superglue`, `gnss-free`

**Domains:** air

## Related

- depends_on: [SuperGlue (pretrained)](../repos/magicleap__supergluepretrainednetwork.md)
- alternative_to: [visual_localization (GNSS-free UAV)](../repos/terbouchehacene__visual_localization.md)
- integrates_with: [LightGlue](../repos/cvg__lightglue.md)

## Referenced by

- [UAVision](../repos/arborisers__uavision.md) (alternative_to)
- [UAVLocalization (map retrieval + alignment)](../repos/hmf21__uavlocalization.md) (alternative_to)
- [UAV-VisLoc dataset](../repos/intellisensing__uav-visloc.md) (integrates_with)
- [visual_localization (GNSS-free UAV)](../repos/terbouchehacene__visual_localization.md) (alternative_to)
- [Vision-based GNSS-Free Localization for UAVs in the Wild](../resources/wildnav-gnss-free-uav-localization-2022.md) (has_code)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
