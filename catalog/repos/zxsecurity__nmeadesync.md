# NMEAdesync

`repo:zxsecurity/nmeadesync` - <https://github.com/zxsecurity/NMEAdesync>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 26 | Python | ? | 2017-06-24 | False | archived | medium |

Proof-of-concept that feeds crafted NMEA sentences to a GPS-referenced NTP server to move its time; a red-team tool, inactive since 2017.

**Why it matters:** A ready-made test input for a time-spoofing detector: it reproduces the 'trusted serial GNSS time' weakness without RF.

**Hackathon notes:** Only for a closed lab against your own time server; no RF needed. Use it to show the detector alarm, not to attack anything.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `ntp`, `nmea`, `spoofing`, `red-team`

**Domains:** multi

## Related

- integrates_with: [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
