# gpsd

`repo:gitlab.com/gpsd/gpsd` - <https://gitlab.com/gpsd/gpsd>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C | ? | ? | ? | production | high |

Service daemon that monitors GNSS receivers over serial/USB/network and serves decoded fixes, satellites and timing to client applications via JSON over TCP.

**Why it matters:** The standard Linux GNSS middleware; used for timing (with ntpd/chrony and PPS) and for multiplexing receivers to multiple apps.

**Hackathon notes:** apt install gpsd gpsd-clients; cgps/gpsmon give instant status. Use it for PPS timing demos.

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Timing and time transfer](../concepts/timing.md)

**Tags:** `daemon`, `linux`, `pps`, `ntp`

**Domains:** multi

## Referenced by

- [NMEA Revealed (gpsd project)](../resources/gpsd-nmea-revealed.md) (has_code)
- [Safran VersaPNT and Geonyx resilient PNT units](../resources/safran-versapnt.md) (alternative_to)

_Indexed by lane(s): gnss_
