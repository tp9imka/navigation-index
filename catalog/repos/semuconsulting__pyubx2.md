# pyubx2

`repo:semuconsulting/pyubx2` - <https://github.com/semuconsulting/pyubx2>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 256 | Python | BSD-3-Clause | 2026-10-29 | False | production | high |

Python library for parsing and generating u-blox UBX protocol messages, including configuration (CFG-VALSET) and raw measurement (RXM-RAWX) messages.

**Why it matters:** Standard way to talk to u-blox receivers from Python: configure, log raw data and read jamming/spoofing status fields (MON-HW, NAV-STATUS).

**Hackathon notes:** pip install pyubx2. Read MON-RF jamming indicators and NAV-STATUS spoof flags to build a live interference monitor quickly.

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `ubx`, `u-blox`, `python`, `parser`

**Domains:** multi

## Related

- same_org: [pyrtcm](../repos/semuconsulting__pyrtcm.md)
- integrates_with: [PyGPSClient](../repos/semuconsulting__pygpsclient.md)

## Referenced by

- [GPSSpy](../repos/hoverflyhampton__gpsspy.md) (integrates_with)
- [PyGPSClient](../repos/semuconsulting__pygpsclient.md) (depends_on)
- [pynmeagps](../repos/semuconsulting__pynmeagps.md) (same_org)
- [pyrtcm](../repos/semuconsulting__pyrtcm.md) (same_org)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
