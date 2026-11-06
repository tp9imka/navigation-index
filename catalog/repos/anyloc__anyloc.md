# AnyLoc

`repo:anyloc/anyloc` - <https://github.com/AnyLoc/AnyLoc>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 649 | Python | BSD-3-Clause | 2024-03-13 | False | research-prototype | high |

Universal visual place recognition using foundation-model (DINOv2) features with VLAD/GeM aggregation, working across aerial, underwater, indoor and outdoor domains without task-specific training.

**Why it matters:** Training-free retrieval that already works on aerial imagery - the fastest way to get a coarse 'which tile am I over' stage.

**Hackathon notes:** Extract descriptors for your satellite tiles offline, query with drone frames; then refine with LightGlue/RoMa.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [anyloc__anyloc](../../docs/integration-cards/anyloc__anyloc.md) (integration-cards)

**Concepts:** [Place recognition and loop closure](../concepts/place-recognition.md), [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md)

**Tags:** `dinov2`, `vlad`, `training-free`

**Domains:** multi

## Related

- integrates_with: [LightGlue](../repos/cvg__lightglue.md)
- alternative_to: [SALAD](../repos/serizba__salad.md)

## Referenced by

- [VPR methods evaluation](../repos/gmberton__vpr-methods-evaluation.md) (integrates_with)
- [UAVLocalization (map retrieval + alignment)](../repos/hmf21__uavlocalization.md) (alternative_to)
- [SALAD](../repos/serizba__salad.md) (alternative_to)
- [AnyLoc: Towards Universal Visual Place Recognition](../resources/anyloc-universal-vpr-2023.md) (has_code)
- [Auterion Skynode S and Auterion Visual Navigation](../resources/auterion-skynode-visual-navigation.md) (alternative_to)
- [Blue Arrow - Ukrainian visual navigation for drones (Brave1 cluster)](../resources/blue-arrow-visual-nav.md) (alternative_to)
- [Helsing HX-2 - map/landmark-based GNSS-denied navigation (navigation aspect only)](../resources/helsing-hx2-navigation.md) (alternative_to)
- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../resources/honeywell-vision-aided-navigation.md) (alternative_to)
- [Inertial Labs VINS visual-aided INS (with Maxar Raptor)](../resources/inertial-labs-vins.md) (alternative_to)
- [Spleenlab VISIONAIRY perception and GNSS-free navigation software](../resources/spleenlab-visionairy.md) (alternative_to)
- [Theseus Visual Navigation System (YC launch)](../resources/theseus-visual-navigation-system.md) (alternative_to)
- [Twist Robotics OSCAR visual navigation module (Ukraine)](../resources/twist-robotics-oscar.md) (alternative_to)
- [UAVOS NavAI vision-based navigation module](../resources/uavos-navai.md) (alternative_to)
- [Drone frame to orthophoto geolocalization with LightGlue](../samples/visual-geolocalization-lightglue.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
