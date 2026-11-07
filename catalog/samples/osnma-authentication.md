# Sample: Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter

`sample:osnma-authentication` - code and walkthrough in [samples/osnma-authentication](../../samples/osnma-authentication/)

Runs unmodified OSNMAlib on the real Galileo I/NAV recording bundled with it (Septentrio SBF, 2025-12-12, 76 min) clean and under 10 file-level manipulations: replay without an independent clock, meaconing at 3 s, replay at 60 s and 1 h with an independent clock, forged ephemeris from cold start and after authentication, a spoofer with random keys and tags, OSNMA stripping, a GST shift and a Merkle-only cold start. Shows which attacks OSNMA catches (forged data, keyless spoofing, GST shift, replay beyond the time bound with an independent clock) and which it misses (replay with no independent clock, meaconing inside the bound, ranging attacks with genuine data, and a same-IOD forgery after authentication that OSNMAlib keeps reporting as authenticated). A stdlib adapter subclasses the gnss-interference-monitor scorer and adds six OSNMA detectors with not-measured handling. Includes a Docker recipe for GNSS-SDR 0.0.20 decoding an OSNMA-SDR-SIM IQ file, and operational requirements (time sync, cold/warm start, u-blox and Septentrio support). File-based only, no RF.

**Verification:** Ran 2026-11-06. OSNMAlib (commit 25aa61de, Python 3.12.14) on its bundled real SBF recording: full 76 min clean = 56 KROOT, 962 TESLA keys, 4711 tags authenticated, 0 failures; 11 scenarios on 20 min: replay with no independent clock and 3 s meaconing authenticate normally; 60 s replay leaves only ADKD12; 1 h replay authenticates nothing without any failure; forged OMEGA_0 bit = 277 tag failures; random keys/tags = 97 key-chain failures; stripping = silent loss; 120 s GST shift = 590 rejected pages + 73 key failures; Merkle-only cold start never authenticates (no DSM-PKR in 76 min); a same-IOD forgery after authentication stayed 'authenticated' for 10 min (OSNMAlib freezes the authenticated stream). 15 tests pass with OSNMAlib, 14 + 1 skipped stdlib-only on Python 3.14.7; mutating each OSNMA detector or the weak-signal guard fails 1-2 tests. GNSS-SDR 0.0.20 (Debian trixie) in Docker on OSNMA-SDR-SIM E1 files (600 s, 6.2 GB): fixes computed, strict mode rejects the replayed file on time; with cross_auth_mode=1 KROOT signature and 6 TESLA keys verified but no tag or nav data authenticated (cause not found); fix lands ~3000 km from the configured sim location (not investigated). Not verified: GNSS-SDR tag/data authentication, re-tagging with disclosed keys, live receivers (u-blox/Septentrio support is from vendor and third-party pages), hot-start TTFAF.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

## Deep dives

- [osnmalib-recording](../../docs/dataset-cards/osnmalib-recording.md) (dataset-cards)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Standards and interface specs](../../catalog/concepts/standards.md), [GNSS positioning](../../catalog/concepts/gnss.md), [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md), [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `osnma`, `galileo`, `tesla`, `navigation-message-authentication`, `spoofing`, `replay`, `meaconing`, `time-sync`, `osnmalib`, `gnss-sdr`, `osnma-sdr-sim`, `docker`, `anti-spoofing`, `cold-start`

## Related

- uses: [OSNMAlib](../../catalog/repos/algafix__osnma.md)
- uses: [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md)
- uses: [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md)
- uses: [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../../catalog/samples/gnss-interference-monitor.md)
- explains: [Galileo OSNMA Signal-In-Space Interface Control Document Issue 1.1](../../catalog/resources/galileo-osnma-sis-icd.md)
- explains: [Galileo OSNMA Receiver Guidelines Issue 1.3](../../catalog/resources/galileo-osnma-receiver-guidelines.md)
- explains: [Galileo Open Service Navigation Message Authentication (OSNMA) - service page](../../catalog/resources/galileo-osnma-service-page.md)
- explains: [galileo-osnma (Rust)](../../catalog/repos/daniestevez__galileo-osnma.md)
- explains: [File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer](../../catalog/samples/gnss-signal-chain.md)

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [OSNMAlib bundled Galileo I/NAV recording (custom_run)](../../catalog/resources/osnmalib-galileo-inav-recording.md) (dataset_for)
- [Real attack replay: Jammertest 2024 u-blox logs through the GNSS interference monitor, with RTKLIB SPP](../../catalog/samples/real-attack-replay.md) (explains)

_Indexed by lane(s): samples_
