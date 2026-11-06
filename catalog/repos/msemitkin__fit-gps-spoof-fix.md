# fit-gps-spoof-fix

`repo:msemitkin/fit-gps-spoof-fix` - <https://github.com/msemitkin/fit-gps-spoof-fix>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 | Python | MIT | 2026-10-28 | False | research-prototype | medium |

Scripts (packaged as an agent skill) that repair Garmin/Strava .fit activities corrupted by GNSS spoofing or jamming: tracks that teleport to a fixed far-away location, impossible speed spikes, phantom distance. Bilingual English/Ukrainian README written from the Ukrainian civilian experience of EW.

**Why it matters:** Encodes practical spoof signatures seen by civilians in Ukraine (position jumps, speed outliers) as simple detection rules; a quick start for track-level spoof detection.

**Hackathon notes:** Tiny Python codebase; the detection heuristics can be lifted into any trajectory plausibility checker. Very new (Oct 2026).

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `lang:uk`, `spoofing-detection`, `fit`, `garmin`, `civilian`

**Domains:** dismounted

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Stone Nav - car navigation without GPS (iOS)](../../catalog/repos/foxfollow__stone-navigation-emulation.md) (alternative_to)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
