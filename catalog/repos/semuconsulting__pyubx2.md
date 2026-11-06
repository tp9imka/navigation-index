# pyubx2

`repo:semuconsulting/pyubx2` - <https://github.com/semuconsulting/pyubx2>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 256 | Python | BSD-3-Clause | 2026-10-29 | False | production | high |

Python library for parsing and generating u-blox UBX protocol messages, including configuration (CFG-VALSET) and raw measurement (RXM-RAWX) messages.

**Why it matters:** Standard way to talk to u-blox receivers from Python: configure, log raw data and read jamming/spoofing status fields (MON-HW, NAV-STATUS).

**Hackathon notes:** pip install pyubx2. Read MON-RF jamming indicators and NAV-STATUS spoof flags to build a live interference monitor quickly.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [semuconsulting__pyubx2](../../docs/integration-cards/semuconsulting__pyubx2.md) (integration-cards)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `ubx`, `u-blox`, `python`, `parser`

**Domains:** multi

## Related

- same_org: [pyrtcm](../../catalog/repos/semuconsulting__pyrtcm.md)
- integrates_with: [PyGPSClient](../../catalog/repos/semuconsulting__pygpsclient.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [GPSSpy](../../catalog/repos/hoverflyhampton__gpsspy.md) (integrates_with)
- [PyGPSClient](../../catalog/repos/semuconsulting__pygpsclient.md) (depends_on)
- [pynmeagps](../../catalog/repos/semuconsulting__pynmeagps.md) (same_org)
- [pyrtcm](../../catalog/repos/semuconsulting__pyrtcm.md) (same_org)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (uses)
- [Low-cost GNSS jammer sensor network: u-blox telemetry => localization => TAK and dashboard](../../catalog/samples/jammer-sensor-network.md) (explains)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
