# STM32 GPSDO

`repo:andrewbcn/stm32-gpsdo` - <https://github.com/AndrewBCN/STM32-GPSDO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 106 | C++ | GPL-3.0 | 2022-04-22 | False | research-prototype | medium |

Experimental GPS-disciplined oscillator: STM32 Black Pill, u-blox NEO-M8, a DAC and a used 10 MHz OCXO, with Arduino-framework firmware counting the OCXO against the 1PPS.

**Why it matters:** Low-cost build that shows the full GPSDO loop on hobby parts; a starting point for adding holdover and spoof-detection logic.

**Hackathon notes:** Parts are cheap and available; the loop is frequency-counting with long averaging, so expect hours to settle. felixd/STM32-GPSDO is a fork.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `gpsdo`, `ocxo`, `stm32`, `ublox`, `firmware`

**Domains:** multi

## Related

- alternative_to: [Lars DIY GPSDO (original files)](../repos/andrewbcn__lars-diy-gpsdo.md)
- alternative_to: [gpsdo-fw (BH3SAP alternative firmware)](../repos/dankar__gpsdo-fw.md)
- alternative_to: [PicoGPSDO](../repos/gibbi__picogpsdo.md)

## Referenced by

- [Lars DIY GPSDO (original files)](../repos/andrewbcn__lars-diy-gpsdo.md) (alternative_to)
- [gpsdo-fw (BH3SAP alternative firmware)](../repos/dankar__gpsdo-fw.md) (alternative_to)
- [PicoGPSDO](../repos/gibbi__picogpsdo.md) (alternative_to)
- [The Use of GPS Disciplined Oscillators as Primary Frequency Standards for Calibration and Metrology Laboratories](../resources/nist-lombardi-gpsdo-calibration.md) (explains)
- [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../samples/timing-holdover.md) (explains)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
