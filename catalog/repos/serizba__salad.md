# SALAD

`repo:serizba/salad` - <https://github.com/serizba/salad>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 386 | Python | GPL-3.0 | 2025-10-27 | False | research-prototype | high |

Place recognition descriptor using optimal-transport aggregation of DINOv2 features.

**Why it matters:** Among the strongest off-the-shelf retrieval descriptors; good drop-in for the coarse stage.

**Hackathon notes:** Load via torch.hub, compare with AnyLoc on your tiles.

## Deep dives

- [salad-vpr-2023](../../docs/paper-digests/salad-vpr-2023.md) (paper-digests)

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md)

**Tags:** `dinov2`, `optimal-transport`

**Domains:** multi

## Related

- alternative_to: [AnyLoc](../../catalog/repos/anyloc__anyloc.md)
- alternative_to: [BoQ](../../catalog/repos/amaralibey__bag-of-queries.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Model weights licenses: code vs weights vs training data](../../docs/model-weights-licenses.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [AnyLoc](../../catalog/repos/anyloc__anyloc.md) (alternative_to)
- [VPR methods evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md) (integrates_with)
- [aero-vloc](../../catalog/repos/prime-slam__aero-vloc.md) (integrates_with)
- [Optimal Transport Aggregation for Visual Place Recognition](../../catalog/resources/salad-vpr-2023.md) (has_code)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
