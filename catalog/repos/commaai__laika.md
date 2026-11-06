# laika

`repo:commaai/laika` - <https://github.com/commaai/laika>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 727 | Python | MIT | 2026-09-25 | False | active-research | high |

Python GNSS processing library from comma.ai that fetches orbits, clocks and atmospheric corrections automatically and computes corrected pseudoranges and positions from raw measurements.

**Why it matters:** Quickest way to go from raw pseudoranges to a corrected fix in Python; it powered openpilot's laikad GNSS localizer until that was removed in October 2023.

**Hackathon notes:** Install from a clone (`pip install .`); the PyPI 'laika' package is a 2018 0.0.1 stub. Correction downloads need internet, and NASA CDDIS needs an Earthdata login in a .netrc. Good backend for Android raw data experiments.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [commaai__laika](../../docs/integration-cards/commaai__laika.md) (integration-cards)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md)

**Tags:** `python`, `pseudorange`, `corrections`, `comma-ai`

**Domains:** ground

## Related

- same_org: [openpilot](../../catalog/repos/commaai__openpilot.md)
- alternative_to: [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [openpilot](../../catalog/repos/commaai__openpilot.md) (depends_on)
- [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md) (alternative_to)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
