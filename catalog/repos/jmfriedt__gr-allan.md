# gr-allan

`repo:jmfriedt/gr-allan` - <https://github.com/jmfriedt/gr-allan>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 8 | CMake | GPL-3.0 | 2023-07-05 | False | research-prototype | low |

GNU Radio sink block that wraps allantools to plot Allan deviation in real time from a stream.

**Why it matters:** Live ADEV of an SDR-measured frequency or phase offset during a demo.

**Hackathon notes:** Tested by the author on GNU Radio 3.10.5; needs allantools installed. Build with cmake.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md)

**Tags:** `allan-deviation`, `gnu-radio`, `allantools`

**Domains:** multi

## Related

- depends_on: [allantools](../../catalog/repos/aewallin__allantools.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
