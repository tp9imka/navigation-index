# GNSS-DSP-tools

`repo:pmonta/gnss-dsp-tools` - <https://github.com/pmonta/GNSS-DSP-tools>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 142 | Python | MIT | 2025-08-17 | False | active-research | high |

Python code generators, acquisition and tracking scripts for GPS, Galileo, GLONASS, BeiDou and Xona Pulsar LEO signals, operating on IQ recordings.

**Why it matters:** Broadest signal coverage among lightweight SDR toolkits; quick to test a new recording.

**Hackathon notes:** Install numpy, scipy and numba (conda is the easy route), then run acquire-<system>-<signal>.py or track-*.py on an IQ file from any SDR. No compile step beyond Numba's JIT.

**Concepts:** [Software-defined GNSS receivers](../concepts/gnss-sdr.md), [GNSS positioning](../concepts/gnss.md)

**Tags:** `acquisition`, `tracking`, `prn-codes`, `python`

**Domains:** multi

## Related

- alternative_to: [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md)
- alternative_to: [GNSS-matlab](../repos/danipascual__gnss-matlab.md)

## Referenced by

- [GNSS-matlab](../repos/danipascual__gnss-matlab.md) (alternative_to)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
