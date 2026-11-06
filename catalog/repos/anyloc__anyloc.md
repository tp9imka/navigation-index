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
- [anyloc-universal-vpr-2023](../../docs/paper-digests/anyloc-universal-vpr-2023.md) (paper-digests)

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md)

**Tags:** `dinov2`, `vlad`, `training-free`

**Domains:** multi

## Related

- integrates_with: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- alternative_to: [SALAD](../../catalog/repos/serizba__salad.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Model weights licenses: code vs weights vs training data](../../docs/model-weights-licenses.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [VPR methods evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md) (integrates_with)
- [UAVLocalization (map retrieval + alignment)](../../catalog/repos/hmf21__uavlocalization.md) (alternative_to)
- [SALAD](../../catalog/repos/serizba__salad.md) (alternative_to)
- [AnyLoc: Towards Universal Visual Place Recognition](../../catalog/resources/anyloc-universal-vpr-2023.md) (has_code)
- [Auterion Skynode S and Auterion Visual Navigation](../../catalog/resources/auterion-skynode-visual-navigation.md) (alternative_to)
- [Blue Arrow - Ukrainian visual navigation for drones (Brave1 cluster)](../../catalog/resources/blue-arrow-visual-nav.md) (alternative_to)
- [Helsing HX-2 - map/landmark-based GNSS-denied navigation (navigation aspect only)](../../catalog/resources/helsing-hx2-navigation.md) (alternative_to)
- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../../catalog/resources/honeywell-vision-aided-navigation.md) (alternative_to)
- [Inertial Labs VINS visual-aided INS (with Maxar Raptor)](../../catalog/resources/inertial-labs-vins.md) (alternative_to)
- [Spleenlab VISIONAIRY perception and GNSS-free navigation software](../../catalog/resources/spleenlab-visionairy.md) (alternative_to)
- [Theseus Visual Navigation System (YC launch)](../../catalog/resources/theseus-visual-navigation-system.md) (alternative_to)
- [Twist Robotics OSCAR visual navigation module (Ukraine)](../../catalog/resources/twist-robotics-oscar.md) (alternative_to)
- [UAVOS NavAI vision-based navigation module](../../catalog/resources/uavos-navai.md) (alternative_to)
- [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md) (explains)
- [Drone frame to orthophoto geolocalization with LightGlue](../../catalog/samples/visual-geolocalization-lightglue.md) (explains)
- [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
