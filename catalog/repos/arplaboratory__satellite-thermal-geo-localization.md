# Satellite-thermal geo-localization

`repo:arplaboratory/satellite-thermal-geo-localization` - <https://github.com/arplaboratory/satellite-thermal-geo-localization>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 103 | Python | MIT | 2026-05-16 | False | active-research | high |

IROS 2023 code for long-range UAV thermal geo-localization against satellite RGB imagery, using domain adaptation to bridge thermal and visible imagery; comes with the Boson-nighttime dataset.

**Why it matters:** Night flight is when GNSS-denied UAVs are most exposed; this is the main open line of work for thermal-to-satellite matching.

**Hackathon notes:** Dataset on Hugging Face (gated). Use the pretrained model to show night-time matching in a demo.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [arplaboratory__satellite-thermal-geo-localization](../../docs/integration-cards/arplaboratory__satellite-thermal-geo-localization.md) (integration-cards)
- [thermal-datasets](../../docs/dataset-cards/thermal-datasets.md) (dataset-cards)
- [thermal-geolocalization-iros-2023](../../docs/paper-digests/thermal-geolocalization-iros-2023.md) (paper-digests)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `thermal`, `night`, `domain-adaptation`

**Domains:** air

## Related

- same_org: [STHN](../../catalog/repos/arplaboratory__sthn.md)
- same_org: [UASTHN](../../catalog/repos/arplaboratory__uasthn.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [CART - Caltech Aerial RGB-Thermal](../../catalog/repos/aerorobotics__caltech-aerial-rgbt-dataset.md) (alternative_to)
- [STHN](../../catalog/repos/arplaboratory__sthn.md) (extends)
- [SCC-Loc](../../catalog/repos/floralhercules__scc-loc.md) (alternative_to)
- [Long-range UAV Thermal Geo-localization with Satellite Imagery](../../catalog/resources/thermal-geolocalization-iros-2023.md) (has_code)

_Indexed by lane(s): alt-nav_

_GitHub metadata fetched 2026-11-06._
