# laika

`repo:commaai/laika` - <https://github.com/commaai/laika>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 727 | Python | MIT | 2026-09-25 | False | active-research | high |

Python GNSS processing library from comma.ai that fetches orbits, clocks and atmospheric corrections automatically and computes corrected pseudoranges and positions from raw measurements.

**Why it matters:** Quickest way to go from raw pseudoranges to a corrected fix in Python; used in openpilot's localizer stack.

**Hackathon notes:** pip-installable. Correction downloads need internet (NASA CDDIS requires an Earthdata login). Good backend for Android raw data experiments.

**Concepts:** [GNSS positioning](../concepts/gnss.md)

**Tags:** `python`, `pseudorange`, `corrections`, `comma-ai`

**Domains:** ground

## Related

- same_org: [openpilot](../repos/commaai__openpilot.md)
- alternative_to: [gnss_lib_py](../repos/stanford-navlab__gnss_lib_py.md)

## Referenced by

- [openpilot](../repos/commaai__openpilot.md) (depends_on)
- [gnss_lib_py](../repos/stanford-navlab__gnss_lib_py.md) (alternative_to)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
