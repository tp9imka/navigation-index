# hloc

`repo:cvg/hierarchical-localization` - <https://github.com/cvg/Hierarchical-Localization>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 4,263 | Python | Apache-2.0 | 2025-12-10 | False | production | high |

Toolbox for hierarchical visual localization: global retrieval (NetVLAD etc.) to find candidate images, then local feature matching (SuperPoint, LightGlue...) and PnP against an SfM model.

**Why it matters:** The standard plumbing for coarse-to-fine localization; ready-made wrappers for most retrieval and matching models.

**Build notes:** Use its retrieval + matching APIs even without the SfM part; pip-installable.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [cvg__hierarchical-localization](../../docs/integration-cards/cvg__hierarchical-localization.md) (integration-cards)
- [hloc-coarse-to-fine-2018](../../docs/paper-digests/hloc-coarse-to-fine-2018.md) (paper-digests)

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Visual SLAM](../../catalog/concepts/visual-slam.md)

**Tags:** `sfm`, `colmap`, `retrieval`, `pnp`

**Domains:** multi

## Related

- depends_on: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- integrates_with: [SuperGlue (pretrained)](../../catalog/repos/magicleap__supergluepretrainednetwork.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Integration cards](../../docs/integration-cards/README.md) (mentions)
- [Model weights licenses: code vs weights vs training data](../../docs/model-weights-licenses.md) (mentions)
- [Paper digests](../../docs/paper-digests/README.md) (mentions)
- [4. Vision, LiDAR and radar odometry](../../docs/primer/04-vision-lidar-radar-odometry.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [LightGlue](../../catalog/repos/cvg__lightglue.md) (integrates_with)
- [Image Matching: Local Features & Beyond (CVPR workshop)](../../catalog/resources/cvpr-image-matching-workshop.md) (uses)
- [From Coarse to Fine: Robust Hierarchical Localization at Large Scale](../../catalog/resources/hloc-coarse-to-fine-2018.md) (has_code)
- [Long-Term Visual Localization benchmark](../../catalog/resources/visual-localization-benchmark.md) (evaluates)
- [Drone frame to orthophoto geolocalization with LightGlue](../../catalog/samples/visual-geolocalization-lightglue.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-09._
