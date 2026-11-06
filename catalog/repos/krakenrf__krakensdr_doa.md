# KrakenSDR DoA DSP

`repo:krakenrf/krakensdr_doa` - <https://github.com/krakenrf/krakensdr_doa>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 323 | Python | GPL-3.0 | 2025-12-13 | False | active-research | high |

Direction-of-arrival processing and web UI for the five-channel coherent KrakenSDR, producing bearings to RF emitters.

**Why it matters:** Passive DF of interference sources (or drone control links) is a core defensive-EW capability and maps well to a hackathon demo.

**Hackathon notes:** Needs KrakenSDR hardware (or recorded IQ). Prebuilt Raspberry Pi images exist (check the KrakenRF docs). Multiple stations plus Stone Soup gives triangulated emitter tracks.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [krakenrf__krakensdr_doa](../../docs/integration-cards/krakenrf__krakensdr_doa.md) (integration-cards)

**Concepts:** [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md)

**Tags:** `direction-finding`, `doa`, `music`, `sdr`, `krakensdr`

**Domains:** ground, multi

## Related

- depends_on: [Heimdall DAQ firmware](../../catalog/repos/krakenrf__heimdall_daq_fw.md)
- integrates_with: [Stone Soup](../../catalog/repos/dstl__stone-soup.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Stone Soup](../../catalog/repos/dstl__stone-soup.md) (integrates_with)
- [Heimdall DAQ firmware](../../catalog/repos/krakenrf__heimdall_daq_fw.md) (same_org)
- [Researchers home in on origins of Russia's Baltic GPS jamming](../../catalog/resources/defensenews-baltic-jamming-origins-2025.md) (uses)
- [infiniDome GPSdome / GPSdome 2 small-UAS anti-jam module](../../catalog/resources/infinidome-gpsdome.md) (alternative_to)
- [GNSS jammer geolocation from DF bearings to TAK](../../catalog/samples/interference-geolocation-to-tak.md) (uses)
- [Low-cost GNSS jammer sensor network: u-blox telemetry => localization => TAK and dashboard](../../catalog/samples/jammer-sensor-network.md) (explains)

_Indexed by lane(s): defense-context_

_GitHub metadata fetched 2026-11-06._
