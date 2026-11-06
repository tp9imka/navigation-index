# hloc

`repo:cvg/hierarchical-localization` - <https://github.com/cvg/Hierarchical-Localization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 4,261 | Python | Apache-2.0 | 2025-12-10 | False | production | high |

Toolbox for hierarchical visual localization: global retrieval (NetVLAD etc.) to find candidate images, then local feature matching (SuperPoint, LightGlue...) and PnP against an SfM model.

**Why it matters:** The standard plumbing for coarse-to-fine localization; ready-made wrappers for most retrieval and matching models.

**Hackathon notes:** Use its retrieval + matching APIs even without the SfM part; pip-installable.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [cvg__hierarchical-localization](../../docs/integration-cards/cvg__hierarchical-localization.md) (integration-cards)

**Concepts:** [Place recognition and loop closure](../concepts/place-recognition.md), [Feature detection and matching](../concepts/feature-matching.md), [Visual SLAM](../concepts/visual-slam.md)

**Tags:** `sfm`, `colmap`, `retrieval`, `pnp`

**Domains:** multi

## Related

- depends_on: [LightGlue](../repos/cvg__lightglue.md)
- integrates_with: [SuperGlue (pretrained)](../repos/magicleap__supergluepretrainednetwork.md)

## Referenced by

- [LightGlue](../repos/cvg__lightglue.md) (integrates_with)
- [Image Matching: Local Features & Beyond (CVPR workshop)](../resources/cvpr-image-matching-workshop.md) (uses)
- [From Coarse to Fine: Robust Hierarchical Localization at Large Scale](../resources/hloc-coarse-to-fine-2018.md) (has_code)
- [Long-Term Visual Localization benchmark](../resources/visual-localization-benchmark.md) (evaluates)
- [Drone frame to orthophoto geolocalization with LightGlue](../samples/visual-geolocalization-lightglue.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
