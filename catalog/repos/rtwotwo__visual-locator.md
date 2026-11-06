# Visual Locator

`repo:rtwotwo/visual-locator` - <https://github.com/Rtwotwo/Visual-Locator>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 8 | Python | MIT | 2026-06-16 | False | research-prototype | medium |

Absolute drone positioning by image retrieval (SelaVPR-style ViT features) over cropped satellite tiles followed by registration with SIFT+RANSAC or SuperPoint+SuperGlue.

**Why it matters:** Clean example of a retrieval + registration pipeline that compares classic and learned matchers side by side.

**Hackathon notes:** Training described used a multi-GPU server; for a hackathon reuse pretrained weights and the pipeline code only.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Place recognition and loop closure](../concepts/place-recognition.md), [Feature detection and matching](../concepts/feature-matching.md)

**Tags:** `retrieval`, `registration`, `selavpr`

**Domains:** air

## Related

- depends_on: [SelaVPR](../repos/lu-feng__selavpr.md)
- depends_on: [SuperGlue (pretrained)](../repos/magicleap__supergluepretrainednetwork.md)

## Referenced by

- [SelaVPR](../repos/lu-feng__selavpr.md) (integrates_with)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
