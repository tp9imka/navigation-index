# Lars DIY GPSDO (original files)

`repo:andrewbcn/lars-diy-gpsdo` - <https://github.com/AndrewBCN/Lars-DIY-GPSDO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 13 | C++ | GPL-3.0 | 2022-01-24 | False | educational | medium |

Archive of Lars Walenius' Arduino GPSDO from the EEVblog forum: a PI loop with a simple 1 ns resolution time-interval phase detector between the GPS 1PPS and the divided OCXO.

**Why it matters:** The design many hobby GPSDOs copy; its loop and time-interval counter trick are a compact reference.

**Hackathon notes:** Reference files only; derivatives such as paulvee/Lars-GPSDO-V4.2 and W3AXL/Simple-GPSDO are maintained builds.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `gpsdo`, `arduino`, `pi-loop`, `ocxo`

**Domains:** multi

## Related

- alternative_to: [STM32 GPSDO](../../catalog/repos/andrewbcn__stm32-gpsdo.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [STM32 GPSDO](../../catalog/repos/andrewbcn__stm32-gpsdo.md) (alternative_to)
- [Arduino SI5351 GPSDO](../../catalog/repos/erikkaashoek__arduino_si5351_gpsdo.md) (extends)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
