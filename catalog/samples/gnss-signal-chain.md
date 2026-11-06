# Sample: File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer

`sample:gnss-signal-chain` - code and walkthrough in [samples/gnss-signal-chain](../../samples/gnss-signal-chain/)

A Docker (arm64/amd64) testbed that never transmits: gps-sdr-sim synthesizes GPS L1 C/A IQ for a static receiver from the shipped 2022-01-01 broadcast ephemeris, a numpy mixer adds noise, a second spoofer stream (power offset, time offset, ramp) and/or a jamming burst, GNSS-SDR 0.0.19 processes each file into PVT, RINEX and a PVT dump, and an adapter feeds the 1 Hz epochs (position, clock, per-SV C/N0) into the gnss-interference-monitor scorer. Four scenarios: clean, unaligned overpower, jam-then-spoof, and a code/carrier-aligned drag-off that walks the fix 978 m away.

**Verification:** ran end to end on 2026-11-06 with Docker arm64 on Apple Silicon (./run.sh, 223 s): gps-sdr-sim commit 28ca29a, GNSS-SDR 0.0.19 (Ubuntu 24.04 package), RTKLIB demo5 v2.5.1 rnx2rtkp. Real outputs are in out/ and quoted in the README: clean median horizontal error 3.0 m with 0 scorer alerts; drag-off captured the PVT to 977.8 m off truth with the first scorer alert at t=67 s and a missed stretch t=87-129 s; unaligned overpower and jam-then-spoof caused a GNSS-SDR PVT outage, not a capture. GNSS-SDR runs are not bit-identical between runs. Not validated against a hardware receiver; the AGC input is a file-power proxy.

**Concepts:** [Software-defined GNSS receivers](../concepts/gnss-sdr.md), [Jamming and spoofing](../concepts/gnss-interference.md), [Simulation and HIL/SITL](../concepts/simulation.md), [GNSS positioning](../concepts/gnss.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `gps-sdr-sim`, `gnss-sdr`, `iq-file`, `spoofing`, `drag-off`, `jamming`, `cn0`, `rinex`, `rnx2rtkp`, `docker`, `arm64`, `file-based`

## Related

- uses: [GPS-SDR-SIM](../repos/osqzss__gps-sdr-sim.md)
- uses: [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md)
- uses: [RTKLIB demo5 (rtklibexplorer)](../repos/rtklibexplorer__rtklib.md)
- uses: [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../samples/gnss-interference-monitor.md)
- explains: [GNSS-SDR documentation](../resources/gnss-sdr-docs.md)
- explains: [Assessing the Spoofing Threat: Development of a Portable GPS Civilian Spoofer](../resources/humphreys-2008-assessing-spoofing-threat.md)
- explains: [GNSS Spoofing and Detection](../resources/psiaki-humphreys-2016-gnss-spoofing-detection.md)

_Indexed by lane(s): samples_
