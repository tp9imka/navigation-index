# RoMa

`repo:parskatt/roma` - <https://github.com/Parskatt/RoMa>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,331 | Python | MIT | 2026-01-23 | False | active-research | high |

Robust dense feature matcher (CVPR 2024) estimating pixel-dense warps with certainties, strong under large appearance change.

**Why it matters:** Handles season, lighting and sensor differences between drone frames and satellite imagery better than sparse matchers, at higher compute cost.

**Hackathon notes:** Use as the accurate-but-slow verifier on the top retrieval hit; GPU recommended.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [parskatt__roma](../../docs/integration-cards/parskatt__roma.md) (integration-cards)
- [roma-dense-matching-2023](../../docs/paper-digests/roma-dense-matching-2023.md) (paper-digests)

**Concepts:** [Feature detection and matching](../concepts/feature-matching.md)

**Tags:** `dense`, `dinov2`, `robust`

**Domains:** multi

## Related

- alternative_to: [LoFTR](../repos/zju3dv__loftr.md)
- alternative_to: [LightGlue](../repos/cvg__lightglue.md)

## Referenced by

- [vismatch (image-matching-models)](../repos/gmberton__vismatch.md) (integrates_with)
- [AnyVisLoc benchmark](../repos/uav-avl__benchmark.md) (evaluated_on)
- [LoFTR](../repos/zju3dv__loftr.md) (alternative_to)
- [RoMa: Robust Dense Feature Matching](../resources/roma-dense-matching-2023.md) (has_code)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
