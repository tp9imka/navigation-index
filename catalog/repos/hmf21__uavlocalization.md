# UAVLocalization (map retrieval + alignment)

`repo:hmf21/uavlocalization` - <https://github.com/hmf21/UAVLocalization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 136 | Python | ? | 2024-07-19 | False | research-prototype | high |

Geo-localization system for aerial platforms that first retrieves the right satellite map region with a deep descriptor and then aligns the drone orthophoto to it to extract coordinates; evaluated on reorganized public AgEagle datasets and a field test.

**Why it matters:** Shows the two-stage retrieve-then-align architecture end to end with field data, the design most practical systems converge on.

**Hackathon notes:** Use its pipeline layout as the backbone of a demo; datasets need a separate download. Conda env file provided.

## Deep dives

- [aerialvl](../../docs/dataset-cards/aerialvl.md) (dataset-cards)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md)

**Tags:** `uav`, `retrieval`, `alignment`, `pytorch`

**Domains:** air

## Related

- alternative_to: [WildNav](../../catalog/repos/tiers__wildnav.md)
- alternative_to: [AnyLoc](../../catalog/repos/anyloc__anyloc.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md) (explains)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
