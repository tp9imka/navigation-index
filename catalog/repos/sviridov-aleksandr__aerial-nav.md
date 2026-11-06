# aerial-nav - GPS-denied navigation via Siamese network

`repo:sviridov-aleksandr/aerial-nav` - <https://github.com/sviridov-aleksandr/aerial-nav>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 |  | ? | 2026-09-03 | False | research-prototype | high |

Matches onboard camera frames to a pre-built satellite map of the route: a ResNet-18 Siamese network with SAFA spatial aggregation ranks map tiles indexed at 13 altitude levels (0-1200 m), then SuperPoint/LightGlue with RANSAC homography refines position and heading. README in Russian.

**Why it matters:** A full coarse-retrieval plus fine-registration VPS pipeline, the same structure fielded visual positioning products describe.

**Hackathon notes:** Good template for a two-stage VPS demo: retrieval narrows the search, LightGlue gives the fix. Check what weights and data are shipped before relying on it.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `lang:ru`, `vps`, `siamese`, `safa`, `superpoint`, `lightglue`, `satellite-map`

**Domains:** air

## Related

- depends_on: [LightGlue](../../catalog/repos/cvg__lightglue.md)
- depends_on: [SuperPoint (pretrained)](../../catalog/repos/magicleap__superpointpretrainednetwork.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-06._
