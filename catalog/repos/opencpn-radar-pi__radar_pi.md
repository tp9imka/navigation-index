# OpenCPN radar_pi

`repo:opencpn-radar-pi/radar_pi` - <https://github.com/opencpn-radar-pi/radar_pi>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 108 | C | GPL-2.0 | 2026-08-04 | False | production | medium |

OpenCPN plugin that connects to Navico and some Garmin and Raymarine marine radars and overlays radar imagery and ARPA-style targets on the chart.

**Why it matters:** Shows how real marine radar returns are pulled into an open nav display, useful for radar-aided navigation and contact tracking demos.

**Hackathon notes:** Needs a supported radar on the network to be interesting; without hardware, study the protocol decoding and overlay code.

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Radar navigation and odometry](../../catalog/concepts/radar-nav.md), [Tracking and data association](../../catalog/concepts/target-tracking.md)

**Tags:** `opencpn-plugin`, `marine-radar`, `arpa`

**Domains:** maritime

## Related

- extends: [OpenCPN](../../catalog/repos/opencpn__opencpn.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [OpenCPN](../../catalog/repos/opencpn__opencpn.md) (integrates_with)
- [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
