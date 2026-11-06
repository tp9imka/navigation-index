# aero-vloc

`repo:prime-slam/aero-vloc` - <https://github.com/prime-slam/aero-vloc>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 82 | Python | Apache-2.0 | 2024-11-28 | False | research-prototype | high |

Benchmark tool accompanying the aerial VPR survey by Moskalenko et al.: downloads satellite map tiles, localizes UAV imagery against them with AnyLoc, CosPlace, EigenPlaces, MixVPR, NetVLAD, SALAD or SelaVPR, and optionally re-ranks with LightGlue, SuperGlue or SelaVPR.

**Why it matters:** Ready-made drone-to-satellite VPR pipeline with many descriptors behind one interface, plus evidence on how tile zoom and overlap affect recall.

**Hackathon notes:** Start from example.ipynb (download map, localize a sequence, compute recall). Some weights come from a Google Drive link, others via TorchHub. Tested on Python 3.10. Apache-2.0.

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md)

**Tags:** `aerial-vpr`, `satellite-tiles`, `re-ranking`, `benchmark`

**Domains:** air

## Related

- evaluated_on: [VPAIR](../../catalog/repos/aervisloc__vpair.md)
- evaluated_on: [ALTO](../../catalog/repos/metaslam__alto.md)
- integrates_with: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- integrates_with: [SALAD](../../catalog/repos/serizba__salad.md)
- integrates_with: [EigenPlaces](../../catalog/repos/gmberton__eigenplaces.md)

## Referenced by

- [Visual place recognition for aerial imagery: A survey](../../catalog/resources/moskalenko-2024-aerial-vpr-survey.md) (has_code)

_Indexed by lane(s): backlog_

_GitHub metadata fetched 2026-11-06._
