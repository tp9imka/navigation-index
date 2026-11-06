# gr_DCF77_Receiver

`repo:henningm1r/gr_dcf77_receiver` - <https://github.com/henningM1r/gr_DCF77_Receiver>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 28 | Python | GPL-3.0 | 2023-08-13 | False | research-prototype | medium |

GNU Radio receiver and live decoder for the DCF77 77.5 kHz time signal, covering both the OOK and phase-modulated channels, with a simulated transmitter and channel for testing without hardware.

**Why it matters:** Time from a terrestrial LF signal of opportunity, independent of GNSS; the simulator lets a team test without an LF front end.

**Hackathon notes:** Needs an SDR that reaches 77.5 kHz (e.g. Airspy HF+, or an upconverter). Docker CI image exists. Outside Europe swap to WWVB/MSF.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Signals of opportunity](../concepts/signals-of-opportunity.md)

**Tags:** `dcf77`, `lf`, `gnu-radio`, `time-signal`, `sdr`

**Domains:** multi

## Related

- alternative_to: [DCF77Decode](../repos/1ux__dcf77decode.md)
- alternative_to: [SDRangel](../repos/f4exb__sdrangel.md)

## Referenced by

- [DCF77Decode](../repos/1ux__dcf77decode.md) (alternative_to)
- [SDRangel](../repos/f4exb__sdrangel.md) (alternative_to)
- [PTB: DCF77](../resources/ptb-dcf77.md) (has_code)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
