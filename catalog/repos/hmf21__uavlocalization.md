# UAVLocalization (map retrieval + alignment)

`repo:hmf21/uavlocalization` - <https://github.com/hmf21/UAVLocalization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 136 | Python | ? | 2024-07-19 | False | research-prototype | high |

Geo-localization system for aerial platforms that first retrieves the right satellite map region with a deep descriptor and then aligns the drone orthophoto to it to extract coordinates; evaluated on reorganized public AgEagle datasets and a field test.

**Why it matters:** Shows the two-stage retrieve-then-align architecture end to end with field data, the design most practical systems converge on.

**Hackathon notes:** Use its pipeline layout as the backbone of a demo; datasets need a separate download. Conda env file provided.

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Place recognition and loop closure](../concepts/place-recognition.md), [Feature detection and matching](../concepts/feature-matching.md)

**Tags:** `uav`, `retrieval`, `alignment`, `pytorch`

**Domains:** air

## Related

- alternative_to: [WildNav](../repos/tiers__wildnav.md)
- alternative_to: [AnyLoc](../repos/anyloc__anyloc.md)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
