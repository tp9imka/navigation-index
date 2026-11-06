# LightGlue

`repo:cvg/lightglue` - <https://github.com/cvg/LightGlue>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,860 | Python | Apache-2.0 | 2026-10-25 | False | production | high |

Fast learned local feature matcher (ICCV 2023) that adapts its depth to pair difficulty; works with SuperPoint, DISK, ALIKED and SIFT features.

**Why it matters:** The default fine-matching stage for drone-to-tile registration today: accurate and fast enough for near-real-time.

**Hackathon notes:** pip install; use SuperPoint+LightGlue between a drone frame and top-k retrieved tiles, then RANSAC homography.

**Concepts:** [Feature detection and matching](../concepts/feature-matching.md)

**Tags:** `matcher`, `superpoint`, `fast`

**Domains:** multi

## Related

- same_org: [Glue Factory](../repos/cvg__glue-factory.md)
- alternative_to: [SuperGlue (pretrained)](../repos/magicleap__supergluepretrainednetwork.md)
- integrates_with: [hloc](../repos/cvg__hierarchical-localization.md)

## Referenced by

- [AnyLoc](../repos/anyloc__anyloc.md) (integrates_with)
- [Glue Factory](../repos/cvg__glue-factory.md) (same_org)
- [hloc](../repos/cvg__hierarchical-localization.md) (depends_on)
- [LightGlue-ONNX](../repos/fabio-sim__lightglue-onnx.md) (extends)
- [vismatch (image-matching-models)](../repos/gmberton__vismatch.md) (integrates_with)
- [SuperGlue (pretrained)](../repos/magicleap__supergluepretrainednetwork.md) (alternative_to)
- [RoMa](../repos/parskatt__roma.md) (alternative_to)
- [visual_localization (GNSS-free UAV)](../repos/terbouchehacene__visual_localization.md) (integrates_with)
- [WildNav](../repos/tiers__wildnav.md) (integrates_with)
- [AnyVisLoc benchmark](../repos/uav-avl__benchmark.md) (evaluated_on)
- [XFeat](../repos/verlab__accelerated_features.md) (alternative_to)
- [LightGlue: Local Feature Matching at Light Speed](../resources/lightglue-2023.md) (has_code)
- [Drone frame to orthophoto geolocalization with LightGlue](../samples/visual-geolocalization-lightglue.md) (uses)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
