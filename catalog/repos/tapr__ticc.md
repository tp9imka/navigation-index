# TAPR TICC

`repo:tapr/ticc` - <https://github.com/TAPR/TICC>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 51 | C++ | MIT | 2026-11-02 | False | production | medium |

Firmware and design files for TAPR's Arduino-based sub-nanosecond time interval counter, used to compare 1PPS outputs.

**Why it matters:** Cheap way to measure a GPSDO or GNSS receiver PPS against a reference and get the phase data ADEV tools need.

**Hackathon notes:** Needs the board; output is a text stream of timestamps that pipes into allantools.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `time-interval-counter`, `pps`, `measurement`, `arduino`

**Domains:** multi

## Related

- integrates_with: [allantools](../../catalog/repos/aewallin__allantools.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [allantools](../../catalog/repos/aewallin__allantools.md) (integrates_with)
- [LeapSecond.com (Tom Van Baak time and frequency pages)](../../catalog/resources/leapsecond-tvb.md) (explains)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
