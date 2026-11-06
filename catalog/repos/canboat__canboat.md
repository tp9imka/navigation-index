# CANboat

`repo:canboat/canboat` - <https://github.com/canboat/canboat>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 666 | Rust | NOASSERTION | 2026-11-05 | False | production | medium |

Toolkit for NMEA 2000 networks: a PGN decoder/analyzer plus utilities to read, write and convert N2K and NMEA 0183 messages, used largely for reverse-engineering marine bus traffic.

**Why it matters:** Gives raw access to ship sensor buses (GNSS, heading, AIS, depth), useful for maritime nav integrity monitoring and spoofing detection research.

**Hackathon notes:** Build analyzer and pipe candump/actisense logs through it to JSON. Needs a CAN or N2K gateway for live data; sample logs work offline.

**Concepts:** [Maritime navigation](../../catalog/concepts/maritime-nav.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `nmea2000`, `nmea0183`, `can-bus`, `pgn`, `marine`

**Domains:** maritime

## Related

- integrates_with: [Signal K Server](../../catalog/repos/signalk__signalk-server.md)

## Referenced by

- [NMEA 2000 Standard (CAN-based marine network)](../../catalog/resources/nmea-2000-standard.md) (has_code)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
