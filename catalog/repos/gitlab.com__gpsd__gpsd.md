# gpsd

`repo:gitlab.com/gpsd/gpsd` - <https://gitlab.com/gpsd/gpsd>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C | ? | ? | ? | production | high |

Service daemon that monitors GNSS receivers over serial/USB/network and serves decoded fixes, satellites and timing to client applications via JSON over TCP.

**Why it matters:** The standard Linux GNSS middleware; used for timing (with ntpd/chrony and PPS) and for multiplexing receivers to multiple apps.

**Hackathon notes:** apt install gpsd gpsd-clients; cgps/gpsmon give instant status. Use it for PPS timing demos.

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `daemon`, `linux`, `pps`, `ntp`

**Domains:** multi

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [1. PNT fundamentals](../../docs/primer/01-pnt-fundamentals.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md) (integrates_with)
- [pps-tools](../../catalog/repos/redlab-i__pps-tools.md) (integrates_with)
- [NMEAdesync](../../catalog/repos/zxsecurity__nmeadesync.md) (integrates_with)
- [NMEA Revealed (gpsd project)](../../catalog/resources/gpsd-nmea-revealed.md) (has_code)
- [Safran VersaPNT and Geonyx resilient PNT units](../../catalog/resources/safran-versapnt.md) (alternative_to)

_Indexed by lane(s): gnss_
