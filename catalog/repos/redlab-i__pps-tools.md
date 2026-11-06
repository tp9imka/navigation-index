# pps-tools

`repo:redlab-i/pps-tools` - <https://github.com/redlab-i/pps-tools>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 63 | C | GPL-2.0 | 2024-03-14 | False | production | medium |

User-space tools and headers for the Linux PPS API (ppstest, ppsctl, ppswatch).

**Why it matters:** First thing to run when wiring a GNSS 1PPS into a Linux box: confirms pulses arrive and shows their jitter.

**Hackathon notes:** apt install pps-tools; `ppstest /dev/pps0`.

**Concepts:** [Timing and time transfer](../concepts/timing.md)

**Tags:** `pps`, `linux`, `gpio`

**Domains:** multi

## Related

- integrates_with: [chrony](../repos/gitlab.com__chrony__chrony.md)
- integrates_with: [gpsd](../repos/gitlab.com__gpsd__gpsd.md)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
