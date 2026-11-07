# Sample: GNSS interference monitor from u-blox telemetry and ADS-B NACp

`sample:gnss-interference-monitor` - code and walkthrough in [samples/gnss-interference-monitor](../../samples/gnss-interference-monitor/)

A stdlib heuristic scorer turns per-epoch receiver telemetry (C/N0 across SVs, AGC, CW jamming indicator, clock, position and velocity, receiver spoofing/jamming flags, and the navigation data the receiver decoded) into jamming and spoofing scores. Instantaneous rules are joined by power CUSUMs on the median per-SV C/N0 deviation and on AGC that catch staircase power changes, by position consistency against the best reference available (IMU/odometry/static velocity, else the receiver's own reported velocity integrated over a 10 s window so normal driving stays consistent, else a constant-velocity prior), Doppler velocity and clock-rate CUSUMs, a velocity-jump bound, and lost fix as its own alert class. Each reference learns only while its own detector is quiet; the per-SV C/N0 baseline is robust (clipped innovations), keeps learning through spoofing sub-alerts so a recovered sky is re-learned, and can drift at a bounded rate while frozen. An ephemeris module decodes GPS LNAV subframes from UBX-RXM-SFRBX and flags SVs whose decoded orbit/clock disagrees with an independent IGS broadcast file. Alerts latch until explicit clear conditions hold and every alert carries value, threshold, unit and evidence. A pyubx2 adapter feeds it from UBX NAV-PVT/SAT/STATUS/CLOCK, MON-RF and SEC-SIG; eval_real.py scores it per slot and detector on the real Jammertest 2024 VAARA logs with a tune/holdout split. A second module applies the GPSJam percentage method to readsb aircraft.json NACp for area-level maps.

**Verification:** Ran 2026-11-06. Tests: 53 (30 scorer, 12 real-data defect regressions, 6 ephemeris, 6 area map, 1 UBX replay) OK on /opt/homebrew/bin/python3 3.14.7 without packages (1 skipped: pyubx2) and OK with pyubx2 1.4.1 on Python 3.13.15. The defect regressions fail on the previous scorer (git dae8229) for driving, position pull, velocity jump, step drop after recovery, C/N0 and AGC staircase and spoofed ephemeris. Mutation check: 10 of 12 single mutations of the new logic fail 1-3 tests; references frozen by any alarm and the power term of the clear rule are not covered. Real data: eval_real.py on the 7 VAARA u-blox logs (13 h, 20 attack slots + 1 quiet), 4 parameters chosen on 3 tuning logs, reported on all 7 with a 4-log holdout: the quiet slot went from 98 % alerting (constant-velocity pos_drift) to 0 %, pos_drift false-alert epochs 10220 => 275, driving alarm time 86 % => 28 %, and every attack slot is detected by a C/N0 detector (before, without the latched pos_drift, 4 slots incl. the 2.4.3 staircase were missed). The ephemeris check, against IGS BRDC from the BKG mirror, decoded 267 GPS sets with 0 parity failures and flagged spoofer ephemerides (276 km to 53 000 km off) in 7 of the 8 spoofing slots, never on the jamming-only days. Synthetic: 20 h soak per reference mode 0 / 0 / 17 alert epochs (cv-prior / doppler / external static); a drag that moves position and Doppler together is not detected without an external reference (by design, drag table in README). gnss-signal-chain GNSS-SDR epochs rescored: clean 0 alerts, overpower/jam-then-spoof alert at attack onset (power CUSUM), drag-off alerts at +6 s on its power step but pos_drift only with --ref-vel 0,0. Not verified: live u-blox receiver, AGC/MON-RF on real data (VAARA has none), Galileo/GLONASS/BeiDou ephemeris checking, real readsb feed, any OSNMA processing.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GNSS positioning](../../catalog/concepts/gnss.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `jamming`, `spoofing`, `u-blox`, `ubx`, `mon-rf`, `agc`, `cn0`, `spoofdetstate`, `sec-sig`, `ads-b`, `nacp`, `gpsjam`, `readsb`, `stdlib`, `cusum`, `drag-off`, `lost-fix`, `clock-drift`, `latched-alarm`, `osnma`, `ephemeris`, `sfrbx`, `lnav`, `brdc`, `jammertest`, `real-data`, `holdout`, `staircase`, `doppler-consistency`

## Related

- uses: [pyubx2](../../catalog/repos/semuconsulting__pyubx2.md)
- uses: [readsb](../../catalog/repos/wiedehopf__readsb.md)
- uses: [pygnssutils](../../catalog/repos/semuconsulting__pygnssutils.md)
- explains: [Multi-frequency GNSS spoofing raw dataset](../../catalog/repos/s7am1na__gnss-spoofing-dataset.md)
- explains: [OSNMAlib](../../catalog/repos/algafix__osnma.md)
- explains: [Galileo OSNMA Receiver Guidelines Issue 1.3](../../catalog/resources/galileo-osnma-receiver-guidelines.md)
- explains: [File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer](../../catalog/samples/gnss-signal-chain.md)
- uses: [Real attack replay: Jammertest 2024 u-blox logs through the GNSS interference monitor, with RTKLIB SPP](../../catalog/samples/real-attack-replay.md)
- uses: [VAARA Jammertest dataset](../../catalog/repos/univaasadigieco__vaara.md)
- explains: [Jammertest - open GNSS jamming and spoofing test event (Andoya, Norway)](../../catalog/resources/jammertest-norway.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer](../../catalog/samples/gnss-signal-chain.md) (uses)
- [Low-cost GNSS jammer sensor network: u-blox telemetry => localization => TAK and dashboard](../../catalog/samples/jammer-sensor-network.md) (uses)
- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md) (explains)
- [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md) (uses)
- [Real attack replay: Jammertest 2024 u-blox logs through the GNSS interference monitor, with RTKLIB SPP](../../catalog/samples/real-attack-replay.md) (uses)

_Indexed by lane(s): samples_
