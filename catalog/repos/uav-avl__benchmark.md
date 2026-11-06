# AnyVisLoc benchmark

`repo:uav-avl/benchmark` - <https://github.com/UAV-AVL/Benchmark>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 221 | Python | ? | 2026-10-10 | False | active-research | high |

Benchmark and code for UAV absolute visual localization under low-altitude, multi-view (oblique) observation, comparing retrieval and matching combinations against aerial and satellite reference maps.

**Why it matters:** One of the most up-to-date (2025) systematic comparisons of what actually works for low-altitude drones, which is the regime of small tactical UAVs.

**Hackathon notes:** Read its results before choosing a retrieval/matcher combo; reuse its evaluation scripts to score your own pipeline.

## Deep dives

- [anyvisloc](../../docs/dataset-cards/anyvisloc.md) (dataset-cards)

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [Feature detection and matching](../concepts/feature-matching.md), [Place recognition and loop closure](../concepts/place-recognition.md)

**Tags:** `benchmark`, `oblique-view`, `low-altitude`, `2025`

**Domains:** air

## Related

- same_org: [U2S-CVGL (scale-aware UAV-to-satellite)](../repos/uav-avl__u2s-cvgl.md)
- evaluated_on: [LightGlue](../repos/cvg__lightglue.md)
- evaluated_on: [RoMa](../repos/parskatt__roma.md)

## Referenced by

- [U2S-CVGL (scale-aware UAV-to-satellite)](../repos/uav-avl__u2s-cvgl.md) (same_org)
- [Exploring the best way for UAV visual localization under Low-altitude Multi-view Observation Condition: a Benchmark](../resources/anyvisloc-uav-localization-benchmark-2025.md) (has_code)
- [Auterion Skynode S and Auterion Visual Navigation](../resources/auterion-skynode-visual-navigation.md) (alternative_to)
- [Blue Arrow - Ukrainian visual navigation for drones (Brave1 cluster)](../resources/blue-arrow-visual-nav.md) (alternative_to)
- [Helsing HX-2 - map/landmark-based GNSS-denied navigation (navigation aspect only)](../resources/helsing-hx2-navigation.md) (alternative_to)
- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../resources/honeywell-vision-aided-navigation.md) (alternative_to)
- [Inertial Labs VINS visual-aided INS (with Maxar Raptor)](../resources/inertial-labs-vins.md) (alternative_to)
- [Theseus Visual Navigation System (YC launch)](../resources/theseus-visual-navigation-system.md) (alternative_to)
- [Twist Robotics OSCAR visual navigation module (Ukraine)](../resources/twist-robotics-oscar.md) (alternative_to)
- [UAVOS NavAI vision-based navigation module](../resources/uavos-navai.md) (alternative_to)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
