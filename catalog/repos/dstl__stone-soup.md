# Stone Soup

`repo:dstl/stone-soup` - <https://github.com/dstl/Stone-Soup>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 678 | Python | MIT | 2026-11-05 | False | production | high |

Open-source Python framework from UK Dstl and partners for developing, running and evaluating tracking and state estimation algorithms: Kalman variants, particle filters, JPDA, MHT, GM-PHD, track management and metrics.

**Why it matters:** A government-backed, permissively developed tracking toolkit - the closest thing to a reference library for situational-awareness fusion that defense judges will recognize.

**Hackathon notes:** pip install stonesoup; tutorials run in Jupyter. Good for fusing ADS-B, Remote ID or DF bearings into tracks on a common picture within a day. Keep it to air-picture awareness, not fire control.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [dstl__stone-soup](../../docs/integration-cards/dstl__stone-soup.md) (integration-cards)
- [maritime-datasets](../../docs/dataset-cards/maritime-datasets.md) (dataset-cards)

**Concepts:** [Tracking and data association](../../catalog/concepts/target-tracking.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md)

**Tags:** `dstl`, `kalman`, `particle-filter`, `python`, `tracking`, `jpda`, `phd`, `metrics`

**Domains:** multi, air, maritime

## Related

- integrates_with: [ADSBCOT](../../catalog/repos/snstac__adsbcot.md)
- integrates_with: [KrakenSDR DoA DSP](../../catalog/repos/krakenrf__krakensdr_doa.md)
- alternative_to: [pyMHT](../../catalog/repos/erikliland__pymht.md)
- alternative_to: [VIMMJIPDA tracker interface](../../catalog/repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [6. Autopilots and C2](../../docs/primer/06-autopilots-and-c2.md) (mentions)
- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [pyMHT](../../catalog/repos/erikliland__pymht.md) (alternative_to)
- [KrakenSDR DoA DSP](../../catalog/repos/krakenrf__krakensdr_doa.md) (integrates_with)
- [pyais](../../catalog/repos/m0r13n__pyais.md) (integrates_with)
- [VIMMJIPDA tracker interface](../../catalog/repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md) (alternative_to)
- [Stone Soup: No Longer Just an Appetiser](../../catalog/resources/dstl-stone-soup-v1-fusion2023.md) (has_code)
- [Stone Soup documentation and tutorials](../../catalog/resources/stone-soup-docs.md) (explains)
- [Stone Soup documentation and tutorials](../../catalog/resources/stone-soup-docs.md) (has_code)
- [GNSS jammer geolocation from DF bearings to TAK](../../catalog/samples/interference-geolocation-to-tak.md) (uses)
- [Stone Soup radar tracking of two UAVs with JPDA and OSPA](../../catalog/samples/stone-soup-tracking.md) (uses)

_Indexed by lane(s): defense-context, domains-swarm_

_GitHub metadata fetched 2026-11-06._
