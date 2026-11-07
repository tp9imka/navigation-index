# Sample: Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble

`sample:timing-network-holdover` - code and walkthrough in [samples/timing-network-holdover](../../samples/timing-network-holdover/)

A stdlib-only simulation of six GNSS-disciplined sites (TCXO, OCXO, CSAC, Rb oscillators imported from timing-holdover) linked by PTP-like two-way time transfer with static path asymmetry, exponential queueing delay and a lucky-packet filter. Three scenarios: regional jamming where GNSS-less nodes hold time from peers vs alone; a 1-50 ns/s time push on one node caught by a least-squares cross-node consistency check that isolates it before GNSS-denied nodes take its time; and all GNSS lost, comparing every node alone, following the best clock, and an Allan-deviation-weighted paper-clock ensemble. Reports time error per node, time under 1 / 1.5 / 5 / 10 us budgets (G.8271 levels), detection time, false alarms, and how much uncalibrated or changed path asymmetry costs (A/2). A separate real-data mode (fetch_data.py + real_link.py) characterises PTP over private 5G SA, public 5G NSA and 4G from the open Kalnins dataset (Zenodo 14230741: PPS-vs-PPS truth, PTPd logs, a UPF packet capture) and replays the measured time error into the jamming and spoof scenarios.

**Verification:** Synthetic: ran with python3.14.7 stdlib on 2026-11-06, default arguments, 51 s; output pasted verbatim in README (plus a --temp-fraction 0 run of scenario c). Real-data mode: fetch_data.py downloaded the Zenodo 14230741 zip (MD5 945aefa3013bc926d748f7e820275069 matched the record) and real_link.py ran on it in 19 s, output pasted verbatim. 21 unittest tests pass under plain /opt/homebrew/bin/python3 (3.14.7) in about 4 s with the data, 18 pass and 3 skip without it; they include parser tests on inline fixtures (PPS, PTPd with glued rows, a hand-built pcapng), a same-seed check that an added 2 us asymmetry moves time by exactly 1 us, a check that a replayed constant 2 us link error becomes 2 us of relay time error, a no-spoof control and a planted blind-detector control. Oscillator parameters are the parent's datasheet/table values; synthetic network delays, asymmetries, PPS noise, temperature fraction, site layout and thresholds are stated assumptions. Real data: PPS truth and PTPd logs come from different runs and PTP software (Timebeat vs PTPd), each record is 15 min and is looped for the replay. None of the related repos was run.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `ptp`, `two-way-time-transfer`, `path-asymmetry`, `holdover`, `clock-ensemble`, `allan-deviation`, `time-spoofing`, `consistency-check`, `bmca`, `packet-delay-variation`, `stdlib`, `5g`, `ptpd`, `real-data`

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
- uses: [Clock Synchronization Accuracy over Mobile Networks](../../catalog/resources/edi-ptp-mobile-network-dataset.md)
- evaluates: [PTPd](../../catalog/repos/ptpd__ptpd.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [3GPP TS 38.133 (ETSI TS 138 133): NR; Requirements for support of radio resource management - clause 7.4 Cell phase synchronization accuracy](../../catalog/resources/3gpp-ts-38-133-cell-phase-sync.md) (explains)
- [Clock Synchronization Accuracy over Mobile Networks](../../catalog/resources/edi-ptp-mobile-network-dataset.md) (dataset_for)
- [PTPsec: Securing the Precision Time Protocol Against Time Delay Attacks Using Cyclic Path Asymmetry Analysis](../../catalog/resources/finkenzeller-2024-ptpsec.md) (explains)
- [ITU-T G.8275.2: Precision time protocol telecom profile for phase/time synchronization with partial timing support from the network](../../catalog/resources/itu-t-g8275-2-ptp-partial-support.md) (explains)
- [IEC61850 SV and PTP traffic under GNSS jamming](../../catalog/resources/kit-iec61850-ptp-gnss-jamming-dataset.md) (dataset_for)
- [IEC61850 SV and PTP traffic under GNSS time synchronization attacks](../../catalog/resources/kit-iec61850-ptp-gnss-spoofing-dataset.md) (dataset_for)
- [MIKES NorduNET NTS White Rabbit link data (UTC(MIKE) - WR(RISE))](../../catalog/resources/mikes-nordunet-white-rabbit-link-data.md) (dataset_for)
- [Data for "PTP over wide area networks with offset measurement outlier filtering"](../../catalog/resources/uniri-wan-ptp-outlier-filtering-dataset.md) (dataset_for)

_Indexed by lane(s): samples_
