# visual_localization (GNSS-free UAV)

`repo:terbouchehacene/visual_localization` - <https://github.com/TerboucheHacene/visual_localization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 168 | Python | MIT | 2024-05-10 | False | research-prototype | high |

A cleaner reimplementation of the WildNav idea: match UAV images to satellite tiles with SuperPoint/SuperGlue-style matchers and estimate geographic position.

**Why it matters:** Packaged, modular take on the WildNav approach that is easier to extend with newer matchers.

**Hackathon notes:** Good starting skeleton if WildNav's scripts feel too ad hoc; swap the matcher for LightGlue or XFeat for speed.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Feature detection and matching](../concepts/feature-matching.md)

**Tags:** `uav`, `satellite-map`, `superpoint`

**Domains:** air

## Related

- alternative_to: [WildNav](../repos/tiers__wildnav.md)
- integrates_with: [LightGlue](../repos/cvg__lightglue.md)

## Referenced by

- [WildNav](../repos/tiers__wildnav.md) (alternative_to)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
