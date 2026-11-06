# Stone Nav - car navigation without GPS (iOS)

`repo:foxfollow/stone-navigation-emulation` - <https://github.com/foxfollow/stone-navigation-emulation>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Swift | MIT | 2026-10-29 | False | research-prototype | medium |

Ukrainian iPhone (Swift) car navigator that keeps guiding along a stored route when GPS disappears or is spoofed: it advances the position along the route by itself, and the driver corrects it by changing speed, pausing, nudging the point or tapping a landmark. Apple Maps, offline route storage, Ukrainian voice prompts. README in Ukrainian.

**Why it matters:** A pragmatic human-in-the-loop answer to spoofing: route-constrained dead reckoning with landmark resets.

**Hackathon notes:** Not on the App Store; sideload via Xcode. Useful idea for a dismounted or vehicle demo: snap to route and let the user re-anchor.

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `lang:uk`, `ios`, `swift`, `spoofing`, `dead-reckoning`, `route-constrained`

**Domains:** ground

## Related

- alternative_to: [fit-gps-spoof-fix](../../catalog/repos/msemitkin__fit-gps-spoof-fix.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-06._
