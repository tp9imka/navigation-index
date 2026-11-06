# TDOA evaluation with RTL-SDRs

`repo:dc9st/tdoa-evaluation-rtlsdr` - <https://github.com/DC9ST/tdoa-evaluation-rtlsdr>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 104 | MATLAB | ? | 2020-10-30 | False | research-prototype | high |

MATLAB scripts that localize a transmitter by TDOA from three RTL-SDR receivers, synchronizing them on a known reference transmitter instead of GNSS time.

**Why it matters:** Shows that distributed RF sensing needs nanosecond-level relative timing and one way to get it without GNSS disciplining.

**Hackathon notes:** Three Pis with RTL-SDRs plus the modified librtlsdr; MATLAB or port to Octave/NumPy.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [RF localization and direction finding](../concepts/rf-localization.md)

**Tags:** `tdoa`, `rtl-sdr`, `synchronization`, `matlab`

**Domains:** multi

## Related

- depends_on: [librtlsdr-2freq](../repos/dc9st__librtlsdr-2freq.md)
- alternative_to: [Heimdall DAQ firmware](../repos/krakenrf__heimdall_daq_fw.md)

## Referenced by

- [librtlsdr-2freq](../repos/dc9st__librtlsdr-2freq.md) (integrates_with)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
