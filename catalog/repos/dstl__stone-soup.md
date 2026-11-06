# Stone Soup

`repo:dstl/stone-soup` - <https://github.com/dstl/Stone-Soup>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 678 | Python | MIT | 2026-11-05 | False | production | high |

Open-source Python framework from UK Dstl and partners for developing, running and evaluating tracking and state estimation algorithms: Kalman variants, particle filters, JPDA, MHT, GM-PHD, track management and metrics.

**Why it matters:** A government-backed, permissively developed tracking toolkit - the closest thing to a reference library for situational-awareness fusion that defense judges will recognize.

**Hackathon notes:** pip install stonesoup; tutorials run in Jupyter. Good for fusing ADS-B, Remote ID or DF bearings into tracks on a common picture within a day. Keep it to air-picture awareness, not fire control.

**Concepts:** [Tracking and data association](../concepts/target-tracking.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Counter-UAS and drone detection](../concepts/counter-uas.md)

**Tags:** `dstl`, `kalman`, `particle-filter`, `python`, `tracking`, `jpda`, `phd`, `metrics`

**Domains:** multi, air, maritime

## Related

- integrates_with: [ADSBCOT](../repos/snstac__adsbcot.md)
- integrates_with: [KrakenSDR DoA DSP](../repos/krakenrf__krakensdr_doa.md)
- alternative_to: [pyMHT](../repos/erikliland__pymht.md)
- alternative_to: [VIMMJIPDA tracker interface](../repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md)

## Referenced by

- [pyMHT](../repos/erikliland__pymht.md) (alternative_to)
- [KrakenSDR DoA DSP](../repos/krakenrf__krakensdr_doa.md) (integrates_with)
- [pyais](../repos/m0r13n__pyais.md) (integrates_with)
- [VIMMJIPDA tracker interface](../repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md) (alternative_to)
- [Stone Soup documentation and tutorials](../resources/dstl-stone-soup-docs.md) (explains)
- [Stone Soup: No Longer Just an Appetiser](../resources/dstl-stone-soup-v1-fusion2023.md) (has_code)
- [Stone Soup documentation and tutorials](../resources/stone-soup-docs.md) (has_code)
- [Stone Soup radar tracking of two UAVs with JPDA and OSPA](../samples/stone-soup-tracking.md) (uses)

_Indexed by lane(s): defense-context, domains-swarm_

_GitHub metadata fetched 2026-11-06._
