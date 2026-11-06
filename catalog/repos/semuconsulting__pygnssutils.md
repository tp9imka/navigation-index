# pygnssutils

`repo:semuconsulting/pygnssutils` - <https://github.com/semuconsulting/pygnssutils>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 148 | Python | BSD-3-Clause | 2026-10-24 | False | production | high |

Python CLI and library utilities for reading, parsing and broadcasting GNSS streams, including an NTRIP client and caster/server and a socket server.

**Why it matters:** Glue for building correction pipelines and logging tools without writing protocol code.

**Hackathon notes:** pip install pygnssutils; gnssntripclient gets you RTCM from a caster in one command.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [semuconsulting__pygnssutils](../../docs/integration-cards/semuconsulting__pygnssutils.md) (integration-cards)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [RTK / PPP precise positioning](../../catalog/concepts/gnss-rtk-ppp.md)

**Tags:** `ntrip`, `cli`, `python`, `spartn`

**Domains:** multi

## Related

- depends_on: [pyrtcm](../../catalog/repos/semuconsulting__pyrtcm.md)
- alternative_to: [ntripcaster (BKG standard caster)](../../catalog/repos/nunojpg__ntripcaster.md)

## Referenced by

- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [PyGPSClient](../../catalog/repos/semuconsulting__pygpsclient.md) (depends_on)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (uses)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
