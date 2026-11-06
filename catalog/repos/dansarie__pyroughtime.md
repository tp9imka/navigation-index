# pyroughtime

`repo:dansarie/pyroughtime` - <https://github.com/dansarie/pyroughtime>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 11 | Python | GPL-3.0 | 2026-10-19 | False | active-research | medium |

Python Roughtime library and CLI implementing RFC 10049; validates signatures against server long-term keys, queries several servers to catch a misbehaving one, and includes a small test server.

**Why it matters:** Python is the fastest route to put Roughtime into a hackathon notebook or detector.

**Hackathon notes:** pip install pycryptodome in the venv. Query several servers, then run the bundled test server with a wrong clock to show detection.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `roughtime`, `rfc10049`, `python`

**Domains:** multi

## Related

- alternative_to: [Roughenough](../../catalog/repos/int08h__roughenough.md)

## Referenced by

- [Roughenough](../../catalog/repos/int08h__roughenough.md) (alternative_to)
- [RFC 10049: Roughtime: A Protocol for Rough Time Synchronization](../../catalog/resources/rfc10049-roughtime.md) (has_code)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
