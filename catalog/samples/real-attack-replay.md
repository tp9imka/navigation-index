# Sample: Real attack replay: Jammertest 2024 u-blox logs through the GNSS interference monitor, with RTKLIB SPP

`sample:real-attack-replay` - code and walkthrough in [samples/real-attack-replay](../../samples/real-attack-replay/)

Replays 7 public u-blox logs from Jammertest 2024 (University of Vaasa VAARA dataset, about 13 h, 21 labelled test slots: drive-by and convoy jamming, motorcade spoofing, time-offset and pseudorange-ramp spoofing at Bleik, jamming-then-spoofing) through the unmodified gnss-interference-monitor scorer. A stdlib adapter frames mixed UBX + NMEA (the logs have no UBX NAV messages and break pyubx2), builds epochs from GGA/RMC/GSV with L1-band C/N0 only, and reconstructs a monotonic time axis so receiver time jumps reach clock_jump. Labels come from the VAARA field log plus two tests recovered from the 2024 NPRA plan shifted by the observed 50 min offset. Reports per test detected / time to detect / detector, alarm time in quiet and unlogged spans, for the shipped scorer and four variants, and RTKLIB SPP error (Docker) with logged vs IGS broadcast ephemerides. Findings: the constant-velocity pos_drift latches on a driving car; a cn0_rise sub-alert freezes the C/N0 baseline for good and hides later drops; staircase power evades cn0_drop; spoofing mostly appeared as a C/N0 drop while the receiver kept its true fix; spoofer ephemerides poison post-processing with the logged nav file.

**Verification:** Ran 2026-11-06. replay.py (Python 3.14.7, stdlib) on 7 VAARA u-blox logs downloaded by fetch_data.sh (64 MB .xz): 21 labelled slots (20 attack, 1 quiet), shipped scorer and variants B/C/D/F; result JSON in results/. RTKLIB demo5 v2.5.1 SPP in the rtklib-demo5 Docker image (built from samples/gnss-rinex-processing/docker, 91 s) on 3 logs with logged nav and with IGS BRDC from the BKG mirror; spp_eval.py numbers in results/. 13 tests on a synthetic VAARA-shaped stream: OK (1 skipped) on /opt/homebrew/bin/python3 3.14.7 without packages, OK with pyubx2 1.4.1 on Python 3.13.15; 4 single mutations each fail 1-3 tests. Not verified: test windows beyond the VAARA field log (2.4.2/2.4.3 are plan-shifted guesses), receiver truth beyond self-referenced medians, phone logs, MON-SPAN, OSNMA on the logged Galileo data, any scorer change (the baseline fix is a runtime what-if only).

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Timing and time transfer](../../catalog/concepts/timing.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md), [GNSS positioning](../../catalog/concepts/gnss.md)

**Tags:** `jammertest`, `vaara`, `u-blox`, `nmea`, `ubx`, `rxm-rawx`, `real-data`, `replay`, `jamming`, `spoofing`, `time-offset`, `cn0`, `baseline`, `rtklib`, `spp`, `convbin`, `ephemeris-poisoning`, `labels`, `false-alarms`, `stdlib`, `docker`

## Related

- uses: [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md)
- uses: [Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py](../../catalog/samples/gnss-rinex-processing.md)
- uses: [VAARA Jammertest dataset](../../catalog/repos/univaasadigieco__vaara.md)
- uses: [Jammertest test plan](../../catalog/repos/npra__jammertest-plan.md)
- uses: [RTKLIB demo5 (rtklibexplorer)](../../catalog/repos/rtklibexplorer__rtklib.md)
- explains: [Jammertest - open GNSS jamming and spoofing test event (Andoya, Norway)](../../catalog/resources/jammertest-norway.md)
- explains: [GNSS Timing Spoofing Detection: Methods and Analysis using Jammertest data](../../catalog/resources/safi-2025-timing-spoofing-jammertest-thesis.md)
- explains: [Data-Driven Analysis of PNT Resilience: Insights and Lessons from Jammertest 2024 Vehicular Data](../../catalog/resources/jammertest-2024-vehicular-pnt-resilience.md)
- explains: [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md)

## Referenced by

- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (uses)

_Indexed by lane(s): samples_
