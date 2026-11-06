# ntripbrowser

`repo:emlid/ntripbrowser` - <https://github.com/emlid/ntripbrowser>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 32 | Python | BSD-3-Clause | 2025-07-21 | False | production | medium |

Command-line tool that fetches and displays an NTRIP caster's source table, optionally filtered by distance from a coordinate.

**Why it matters:** Quick way to find the nearest public base station mountpoint.

**Hackathon notes:** Needs libcurl. pip install ntripbrowser still installs the 2021 release (2.2.3); the repo is at 4.0.0 (2025, Python 3.11+), so install from a clone with make install for current code. Point at rtk2go or a national caster.

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [RTK / PPP precise positioning](../../catalog/concepts/gnss-rtk-ppp.md)

**Tags:** `ntrip`, `cli`, `python`

**Domains:** multi

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
