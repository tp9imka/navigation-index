# Sample: GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof

`sample:timing-holdover` - code and walkthrough in [samples/timing-holdover](../../samples/timing-holdover/)

A stdlib-only simulation of a GNSS-disciplined oscillator (type-2 PLL on a noisy 1PPS) for TCXO, OCXO, rubidium and chip-scale atomic clock grades, with ADEV, aging and temperature figures taken from Vig's oscillator comparison table and the Microchip SA65 datasheet. It reports time error after 1 min to 24 h of GNSS outage (Monte Carlo median and 95th percentile, next to an analytic estimate), then walks GNSS time off slowly and compares an internal steering-plausibility monitor with a cross-check against a second time source, including a guard that drops into holdover on alarm and no-spoof control runs.

**Verification:** ran with python3.14.7 stdlib on 2026-11-06 (default arguments, about 5 s); output pasted verbatim in README. 9 unittest tests pass, including an ADEV check of the noise model, a no-spoof negative control and a planted blind-detector control that proves the cross-source alarm can fail. Oscillator parameters are datasheet/table values; PPS noise, second-source noise/asymmetry, temperature fraction and detector thresholds are stated assumptions. No hardware or real GNSS data was used, and none of the related repos was run.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `gpsdo`, `holdover`, `allan-deviation`, `ocxo`, `rubidium`, `csac`, `tcxo`, `time-spoofing`, `pll`, `stdlib`

## Related

- explains: [allantools](../../catalog/repos/aewallin__allantools.md)
- explains: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)
- explains: [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md)
- explains: [STM32 GPSDO](../../catalog/repos/andrewbcn__stm32-gpsdo.md)
- explains: [PTPsec](../../catalog/repos/tum-esi__ptpsec.md)
- uses: [Introduction to Quartz Frequency Standards - Oscillator Comparison and Selection](../../catalog/resources/vig-intro-quartz-frequency-standards.md)
- uses: [Microchip SA65 Chip Scale Atomic Clock datasheet (DS00003478F)](../../catalog/resources/microchip-csac-sa65-datasheet.md)
- uses: [Handbook of Frequency Stability Analysis (NIST SP 1065)](../../catalog/resources/nist-sp1065-frequency-stability-handbook.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md) (uses)

_Indexed by lane(s): samples_
