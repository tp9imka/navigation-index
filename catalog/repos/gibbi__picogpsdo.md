# PicoGPSDO

`repo:gibbi/picogpsdo` - <https://github.com/gibbi/PicoGPSDO>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 23 | Python | ? | 2026-04-20 | False | research-prototype | medium |

RP2040-based GPS-disciplined OCXO: firmware steers the OCXO via PWM from u-blox UBX timing messages (coarse from clock bias, fine from TIM-TP quantization error) and a Flask dashboard plots telemetry.

**Why it matters:** A modern open GPSDO that uses the receiver's quantization-error correction, the step most hobby designs skip.

**Hackathon notes:** Needs Pico SDK and the board; the web dashboard is a good pattern for a demo.

**Concepts:** [Timing and time transfer](../concepts/timing.md)

**Tags:** `gpsdo`, `rp2040`, `ublox`, `ocxo`, `qerr`

**Domains:** multi

## Related

- alternative_to: [STM32 GPSDO](../repos/andrewbcn__stm32-gpsdo.md)

## Referenced by

- [STM32 GPSDO](../repos/andrewbcn__stm32-gpsdo.md) (alternative_to)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
