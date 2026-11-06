# BoxMOT

`repo:mikel-brostrom/boxmot` - <https://github.com/mikel-brostrom/boxmot>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 8,327 | Python | AGPL-3.0 | 2026-11-04 | False | production | high |

Pluggable collection of modern multi-object trackers (ByteTrack, BoT-SORT, OC-SORT, StrongSORT and others) for detector outputs, in Python and C++.

**Why it matters:** Drop-in visual tracking for camera-based drone detection.

**Hackathon notes:** pip install boxmot and wrap your detector; pick ByteTrack for speed.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [mikel-brostrom__boxmot](../../docs/integration-cards/mikel-brostrom__boxmot.md) (integration-cards)
- [anti-uav](../../docs/dataset-cards/anti-uav.md) (dataset-cards)

**Concepts:** [Tracking and data association](../../catalog/concepts/target-tracking.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `mot`, `bytetrack`, `yolo`, `reid`

**Domains:** multi

## Related

- depends_on: [ByteTrack](../../catalog/repos/foundationvision__bytetrack.md)
- integrates_with: [Ultralytics YOLO](../../catalog/repos/ultralytics__ultralytics.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ByteTrack](../../catalog/repos/foundationvision__bytetrack.md) (integrates_with)
- [Ultralytics YOLO](../../catalog/repos/ultralytics__ultralytics.md) (integrates_with)
- [motpy](../../catalog/repos/wmuron__motpy.md) (alternative_to)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
