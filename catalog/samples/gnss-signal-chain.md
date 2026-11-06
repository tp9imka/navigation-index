# Sample: File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer

`sample:gnss-signal-chain` - code and walkthrough in [samples/gnss-signal-chain](../../samples/gnss-signal-chain/)

A Docker (arm64/amd64) testbed that never transmits: gps-sdr-sim synthesizes GPS L1 C/A IQ for a static receiver from the shipped 2022-01-01 broadcast ephemeris, a numpy mixer adds noise, a second spoofer stream (power offset, time offset, ramp) and/or a jamming burst, GNSS-SDR 0.0.19 processes each file into PVT, RINEX and a PVT dump, and an adapter feeds 1 Hz epochs (position, Doppler velocity, HDOP, clock, per-SV C/N0, plus no-fix epochs when PVT stops) into the gnss-interference-monitor scorer, with and without a static velocity reference, and reports time-to-detect, silent windows and false alarms. Four scenarios: clean, unaligned overpower, jam-then-spoof, and a code/carrier-aligned drag-off that walks the fix 978 m away.

**Verification:** Ran end to end twice on 2026-11-06 with Docker arm64 on Apple Silicon (second run: image rebuilt, ./run.sh 319 s): gps-sdr-sim commit 28ca29a, GNSS-SDR 0.0.19 (Ubuntu 24.04 package), RTKLIB demo5 v2.5.1 rnx2rtkp. Real outputs of the second run are in out/ and quoted in the README. Clean: median horizontal error 2.9 m, 0 alarm epochs in both reference modes. Drag-off: PVT captured to 977.8 m off truth; the old scorer alerted at t=138 (run 1: t=67 with a 43 s silent stretch), the new scorer at t=89 (constant-velocity prior) / t=86 (static reference), 9 / 6 s after the drag began, with no silent epoch after the first alert. Unaligned overpower and jam-then-spoof caused a GNSS-SDR PVT outage, not a capture; the old scorer gave 1 and 0 alert epochs, the new one latched a lost-fix alarm at t=81 and t=76 and held it to the end. GNSS-SDR runs are not bit-identical. Not validated against a hardware receiver; the AGC input is a file-power proxy; the static velocity reference is ideal.

**Concepts:** [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [GNSS positioning](../../catalog/concepts/gnss.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `gps-sdr-sim`, `gnss-sdr`, `iq-file`, `spoofing`, `drag-off`, `jamming`, `cn0`, `rinex`, `rnx2rtkp`, `docker`, `arm64`, `file-based`, `cusum`, `lost-fix`, `time-to-detect`

## Related

- uses: [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md)
- uses: [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md)
- uses: [RTKLIB demo5 (rtklibexplorer)](../../catalog/repos/rtklibexplorer__rtklib.md)
- uses: [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md)
- explains: [GNSS-SDR documentation](../../catalog/resources/gnss-sdr-docs.md)
- explains: [Assessing the Spoofing Threat: Development of a Portable GPS Civilian Spoofer](../../catalog/resources/humphreys-2008-assessing-spoofing-threat.md)
- explains: [GNSS Spoofing and Detection](../../catalog/resources/psiaki-humphreys-2016-gnss-spoofing-detection.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [IGS daily merged broadcast navigation files (BKG mirror)](../../catalog/resources/igs-bkg-brdc-broadcast-ephemeris.md) (dataset_for)
- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md) (explains)
- [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md) (explains)

_Indexed by lane(s): samples_
