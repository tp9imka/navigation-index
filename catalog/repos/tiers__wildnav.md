# WildNav

`repo:tiers/wildnav` - <https://github.com/TIERS/wildnav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 286 | Python | BSD-3-Clause | 2025-06-12 | False | research-prototype | high |

Python pipeline that localizes a drone by matching its downward camera frames against georeferenced satellite map tiles with SuperGlue, then converts the best match into GPS coordinates. Companion code to the 'Vision-based GNSS-Free Localization for UAVs in the Wild' paper.

**Why it matters:** The canonical small, readable reference for absolute visual localization over non-urban terrain - exactly the 'visual GPS' building block a GNSS-denied team needs.

**Hackathon notes:** Clone, drop in your own map tiles with corner coordinates and a few drone photos; runs on a laptop GPU. Brute-force tile search is slow - add a retrieval stage (AnyLoc/SALAD) to prune candidates.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [tiers__wildnav](../../docs/integration-cards/tiers__wildnav.md) (integration-cards)
- [wildnav-gnss-free-uav-localization-2022](../../docs/paper-digests/wildnav-gnss-free-uav-localization-2022.md) (paper-digests)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `uav`, `satellite-map`, `superglue`, `gnss-free`

**Domains:** air

## Related

- depends_on: [SuperGlue (pretrained)](../../catalog/repos/magicleap__supergluepretrainednetwork.md)
- alternative_to: [visual_localization (GNSS-free UAV)](../../catalog/repos/terbouchehacene__visual_localization.md)
- integrates_with: [LightGlue](../../catalog/repos/cvg__lightglue.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [UAVision](../../catalog/repos/arborisers__uavision.md) (alternative_to)
- [UAVLocalization (map retrieval + alignment)](../../catalog/repos/hmf21__uavlocalization.md) (alternative_to)
- [UAV-VisLoc dataset](../../catalog/repos/intellisensing__uav-visloc.md) (integrates_with)
- [visual_localization (GNSS-free UAV)](../../catalog/repos/terbouchehacene__visual_localization.md) (alternative_to)
- [Auterion Skynode S and Auterion Visual Navigation](../../catalog/resources/auterion-skynode-visual-navigation.md) (alternative_to)
- [Blue Arrow - Ukrainian visual navigation for drones (Brave1 cluster)](../../catalog/resources/blue-arrow-visual-nav.md) (alternative_to)
- [Helsing HX-2 - map/landmark-based GNSS-denied navigation (navigation aspect only)](../../catalog/resources/helsing-hx2-navigation.md) (alternative_to)
- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../../catalog/resources/honeywell-vision-aided-navigation.md) (alternative_to)
- [Inertial Labs VINS visual-aided INS (with Maxar Raptor)](../../catalog/resources/inertial-labs-vins.md) (alternative_to)
- [Theseus Visual Navigation System (YC launch)](../../catalog/resources/theseus-visual-navigation-system.md) (alternative_to)
- [Twist Robotics OSCAR visual navigation module (Ukraine)](../../catalog/resources/twist-robotics-oscar.md) (alternative_to)
- [UAVOS NavAI vision-based navigation module](../../catalog/resources/uavos-navai.md) (alternative_to)
- [Vision-based GNSS-Free Localization for UAVs in the Wild](../../catalog/resources/wildnav-gnss-free-uav-localization-2022.md) (has_code)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
