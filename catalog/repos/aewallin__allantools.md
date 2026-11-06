# allantools

`repo:aewallin/allantools` - <https://github.com/aewallin/allantools>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 275 | Python | LGPL-3.0 | 2026-10-26 | False | production | high |

Python library for time and frequency stability statistics: Allan, modified Allan, overlapping, Hadamard and time deviation, plus confidence intervals and power-law noise generators.

**Why it matters:** The tool to turn a logged clock offset series into an ADEV/TDEV plot and to read holdover performance off it.

**Hackathon notes:** pip install allantools; feed phase data from chronyc tracking logs, ptp4l offsets or a TICC. Plot ADEV per oscillator and compare with datasheet curves.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Sensor calibration](../concepts/calibration.md)

**Tags:** `allan-deviation`, `tdev`, `mdev`, `python`, `frequency-stability`

**Domains:** multi

## Related

- alternative_to: [allan-variance (Python)](../repos/nmayorov__allan-variance.md)
- integrates_with: [TAPR TICC](../repos/tapr__ticc.md)
- alternative_to: [allan_variance_ros](../repos/ori-drs__allan_variance_ros.md)

## Referenced by

- [TAPR TICC](../repos/tapr__ticc.md) (integrates_with)
- [Handbook of Frequency Stability Analysis (NIST SP 1065)](../resources/nist-sp1065-frequency-stability-handbook.md) (has_code)
- [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../samples/timing-holdover.md) (explains)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
