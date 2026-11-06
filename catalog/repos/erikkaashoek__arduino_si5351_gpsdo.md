# Arduino SI5351 GPSDO

`repo:erikkaashoek/arduino_si5351_gpsdo` - <https://github.com/erikkaashoek/Arduino_SI5351_GPSDO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 32 | C++ | GPL-3.0 | 2021-12-03 | False | research-prototype | medium |

Minimal GPSDO: Arduino Nano steers an SI5351 synthesizer from the GPS 1PPS, with measurement time scaled to the observed stability and an optional phase detector.

**Why it matters:** Shows that a usable disciplined reference needs only a PPS and a few dollars of parts, and why the crystal's temperature sensitivity dominates.

**Hackathon notes:** Fast to build; replace the SI5351 crystal with a TCXO as the README advises.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `gpsdo`, `arduino`, `si5351`, `pps`

**Domains:** multi

## Related

- extends: [Lars DIY GPSDO (original files)](../../catalog/repos/andrewbcn__lars-diy-gpsdo.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
