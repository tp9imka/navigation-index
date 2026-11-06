# librtlsdr-2freq

`repo:dc9st/librtlsdr-2freq` - <https://github.com/DC9ST/librtlsdr-2freq>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 30 | C | GPL-3.0 | 2019-04-06 | False | research-prototype | medium |

Modified librtlsdr that switches between two frequencies during one recording without losing samples, so a reference transmitter and the target land in the same stream.

**Why it matters:** The trick that makes reference-transmitter synchronization of cheap TDOA receivers work.

**Hackathon notes:** Build on the Pi receivers; see the companion evaluation scripts.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [RF localization and direction finding](../concepts/rf-localization.md)

**Tags:** `rtl-sdr`, `tdoa`, `synchronization`

**Domains:** multi

## Related

- integrates_with: [TDOA evaluation with RTL-SDRs](../repos/dc9st__tdoa-evaluation-rtlsdr.md)

## Referenced by

- [TDOA evaluation with RTL-SDRs](../repos/dc9st__tdoa-evaluation-rtlsdr.md) (depends_on)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
