# Handbook of Frequency Stability Analysis (NIST SP 1065)

`res:nist-sp1065-frequency-stability-handbook` - book - <https://www.nist.gov/publications/handbook-frequency-stability-analysis>

**By:** W. J. Riley, D. A. Howe - **Year:** 2008 - **Level:** advanced - **Access:** open

NIST tutorial and reference on characterizing clocks and oscillators: Allan, modified Allan, Hadamard and time deviation, power-law noise types, drift removal and confidence intervals.

## Key takeaways

- Identify the noise type from the ADEV slope before extrapolating
- Remove drift separately; ADEV alone does not show aging
- TDEV is the time-domain statistic for time error over an interval

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `allan-deviation`, `tdev`, `frequency-stability`, `nist`

## Related

- has_code: [allantools](../../catalog/repos/aewallin__allantools.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [BIPM Circular T](../../catalog/resources/bipm-circular-t.md) (uses)
- [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../../catalog/samples/timing-holdover.md) (uses)

_Indexed by lane(s): timing_
