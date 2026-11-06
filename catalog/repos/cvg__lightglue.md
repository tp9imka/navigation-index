# LightGlue

`repo:cvg/lightglue` - <https://github.com/cvg/LightGlue>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,860 | Python | Apache-2.0 | 2026-10-25 | False | production | high |

Fast learned local feature matcher (ICCV 2023) that adapts its depth to pair difficulty; works with SuperPoint, DISK, ALIKED and SIFT features.

**Why it matters:** The default fine-matching stage for drone-to-tile registration today: accurate and fast enough for near-real-time.

**Hackathon notes:** Not on PyPI: install with `git clone https://github.com/cvg/LightGlue && pip install -e .`, or use the Hugging Face Transformers port. Use SuperPoint+LightGlue between a drone frame and top-k retrieved tiles, then RANSAC homography.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [cvg__lightglue](../../docs/integration-cards/cvg__lightglue.md) (integration-cards)
- [lightglue-2023](../../docs/paper-digests/lightglue-2023.md) (paper-digests)

**Concepts:** [Feature detection and matching](../../catalog/concepts/feature-matching.md)

**Tags:** `matcher`, `superpoint`, `fast`

**Domains:** multi

## Related

- same_org: [Glue Factory](../../catalog/repos/cvg__glue-factory.md)
- alternative_to: [SuperGlue (pretrained)](../../catalog/repos/magicleap__supergluepretrainednetwork.md)
- integrates_with: [hloc](../../catalog/repos/cvg__hierarchical-localization.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [Model weights licenses: code vs weights vs training data](../../docs/model-weights-licenses.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [AnyLoc](../../catalog/repos/anyloc__anyloc.md) (integrates_with)
- [Glue Factory](../../catalog/repos/cvg__glue-factory.md) (same_org)
- [hloc](../../catalog/repos/cvg__hierarchical-localization.md) (depends_on)
- [LightGlue-ONNX](../../catalog/repos/fabio-sim__lightglue-onnx.md) (extends)
- [vismatch (image-matching-models)](../../catalog/repos/gmberton__vismatch.md) (integrates_with)
- [SuperGlue (pretrained)](../../catalog/repos/magicleap__supergluepretrainednetwork.md) (alternative_to)
- [RoMa](../../catalog/repos/parskatt__roma.md) (alternative_to)
- [aero-vloc](../../catalog/repos/prime-slam__aero-vloc.md) (integrates_with)
- [aerial-nav - GPS-denied navigation via Siamese network](../../catalog/repos/sviridov-aleksandr__aerial-nav.md) (depends_on)
- [visual_localization (GNSS-free UAV)](../../catalog/repos/terbouchehacene__visual_localization.md) (integrates_with)
- [WildNav](../../catalog/repos/tiers__wildnav.md) (integrates_with)
- [AnyVisLoc benchmark](../../catalog/repos/uav-avl__benchmark.md) (evaluated_on)
- [XFeat](../../catalog/repos/verlab__accelerated_features.md) (alternative_to)
- [LightGlue: Local Feature Matching at Light Speed](../../catalog/resources/lightglue-2023.md) (has_code)
- [OpenAerialMap](../../catalog/resources/openaerialmap.md) (uses)
- [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md) (uses)
- [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md) (uses)
- [Golden demo: GPS drag (position-only or coherent) on an ArduCopter SITL AUTO mission, integrity monitoring with solution separation + protection level, real visual geolocalization, EKF3 switch to ExternalNav, Monte Carlo, dashboard replay](../../catalog/samples/golden-demo.md) (uses)
- [Night / thermal UAV frame to RGB satellite geolocalization with a no-false-fix gate (ALIKED / DISK / SIFT + LightGlue, SGM baseline, Thermal-UAV)](../../catalog/samples/thermal-geolocalization.md) (uses)
- [Drone frame to orthophoto geolocalization with LightGlue](../../catalog/samples/visual-geolocalization-lightglue.md) (uses)
- [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md) (uses)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
