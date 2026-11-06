# Sample: Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble

`sample:timing-network-holdover` - code and walkthrough in [samples/timing-network-holdover](../../samples/timing-network-holdover/)

A stdlib-only simulation of six GNSS-disciplined sites (TCXO, OCXO, CSAC, Rb oscillators imported from timing-holdover) linked by PTP-like two-way time transfer with static path asymmetry, exponential queueing delay and a lucky-packet filter. Three scenarios: regional jamming where GNSS-less nodes hold time from peers vs alone; a 1-50 ns/s time push on one node caught by a least-squares cross-node consistency check that isolates it before GNSS-denied nodes take its time; and all GNSS lost, comparing every node alone, following the best clock, and an Allan-deviation-weighted paper-clock ensemble. Reports time error per node, time under 1 / 1.5 / 5 / 10 us budgets (G.8271 levels), detection time, false alarms, and how much uncalibrated or changed path asymmetry costs (A/2).

**Verification:** Ran with python3.14.7 stdlib on 2026-11-06, default arguments, 51 s; output pasted verbatim in README (plus a --temp-fraction 0 run of scenario c). 10 unittest tests pass under plain /opt/homebrew/bin/python3 (3.14.7) in about 3 s, including a same-seed check that an added 2 us asymmetry moves time by exactly 1 us, a no-spoof control and a planted blind-detector control. Oscillator parameters are the parent's datasheet/table values; network delays, asymmetries, PPS noise, temperature fraction, site layout and thresholds are stated assumptions. No hardware, PTP logs or real GNSS data; none of the related repos was run.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `ptp`, `two-way-time-transfer`, `path-asymmetry`, `holdover`, `clock-ensemble`, `allan-deviation`, `time-spoofing`, `consistency-check`, `bmca`, `packet-delay-variation`, `stdlib`

## Related

- uses: [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../../catalog/samples/timing-holdover.md)
- explains: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)
- explains: [clknetsim](../../catalog/repos/mlichvar__clknetsim.md)
- explains: [PTPsec](../../catalog/repos/tum-esi__ptpsec.md)
- explains: [allantools](../../catalog/repos/aewallin__allantools.md)
- uses: [IEEE 1588-2019: IEEE Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems](../../catalog/resources/ieee-1588-2019.md)
- uses: [ITU-T G.8271: Time and phase synchronization aspects of telecommunication networks](../../catalog/resources/itu-t-g8271.md)
- uses: [RFC 7384: Security Requirements of Time Protocols in Packet Switched Networks](../../catalog/resources/rfc7384-time-protocol-security.md)
- uses: [Introduction to Quartz Frequency Standards - Oscillator Comparison and Selection](../../catalog/resources/vig-intro-quartz-frequency-standards.md)
- uses: [Microchip SA65 Chip Scale Atomic Clock datasheet (DS00003478F)](../../catalog/resources/microchip-csac-sa65-datasheet.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
