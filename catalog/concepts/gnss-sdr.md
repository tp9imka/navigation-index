# Software-defined GNSS receivers

`concept:gnss-sdr`

Acquisition, tracking, navigation-message decoding in software on SDR front-ends.

**Parent:** [GNSS positioning](../../catalog/concepts/gnss.md)

## Samples (2)

- [File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer](../../catalog/samples/gnss-signal-chain.md) - A Docker (arm64/amd64) testbed that never transmits: gps-sdr-sim synthesizes GPS L1 C/A IQ for a static receiver from the shipped 2022-01-01 broadcast ephemeris, a numpy mixer adds noise, a second spoofer stream (power o
- [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md) - Runs unmodified OSNMAlib on the real Galileo I/NAV recording bundled with it (Septentrio SBF, 2025-12-12, 76 min) clean and under 10 file-level manipulations: replay without an independent clock, meaconing at 3 s, replay

## Guides (1)

- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) - After this chapter you can explain how a receiver turns satellite signals into a position, read raw receiver output, pick between SPP, RTK and PPP, and build a jamming or spoofing detector that runs on recorded data.

## Repositories (18)

- [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) - fit: high - Full software-defined GNSS receiver built on GNU Radio: acquisition, tracking, navigation message decoding and PVT for GPS, Galileo, GLONASS and BeiDou signals from SDR front-ends or IQ files, including Galileo OSNMA sup
- [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md) - fit: high - AIS receiver and decoder for cheap SDRs (RTL-SDR, Airspy, HackRF, SDRplay, SoapySDR) with a built-in web map, JSON/NMEA output and feed sharing.
- [readsb](../../catalog/repos/wiedehopf__readsb.md) - fit: high - ADS-B/Mode S decoder for RTL-SDR and other receivers with networking, JSON output, MLAT support and aggregation features.
- [GNSS-DSP-tools](../../catalog/repos/pmonta__gnss-dsp-tools.md) - fit: high - Python code generators, acquisition and tracking scripts for GPS, Galileo, GLONASS, BeiDou and Xona Pulsar LEO signals, operating on IQ recordings.
- [Starlink LEO-PNT](../../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md) - fit: high - Passive positioning using Starlink downlink signals as signals of opportunity: SDR capture, blind OFDM analysis, Doppler extraction, TDOA/FDOA solver and EKF with TLE-based orbits.
- [SDRangel](../../catalog/repos/f4exb__sdrangel.md) - fit: medium - General SDR receive/transmit application with many demodulator plugins; its Radio Clock plugin decodes LF time broadcasts including MSF, DCF77, TDF, WWVB, JJY and RBU.
- [PocketSDR](../../catalog/repos/tomojitakasu__pocketsdr.md) - fit: medium - Open hardware GNSS front-end plus a software receiver (Python and C) by the RTKLIB author, supporting a wide range of GNSS signals across L1/L2/L5/L6 bands.
- [FGI-GSRx](../../catalog/repos/nlsfi__fgi-gsrx.md) - fit: medium - Multi-GNSS software receiver in MATLAB from the Finnish Geospatial Research Institute, with modular acquisition, tracking and navigation stages.
- [SoftGNSS v3.0 (maintained copy)](../../catalog/repos/tmboc__softgnss.md) - fit: medium - Maintained copy of the classic Borre/Akos SoftGNSS MATLAB GPS L1 receiver with updates for several sampler front-ends.
- [CU Boulder GNSS SDR Collection](../../catalog/repos/gnsscusdr__cu-sdr-collection.md) - fit: medium - University of Colorado Boulder collection of MATLAB software-defined GNSS receiver code-bases, organized per constellation (GPS, Galileo, GLONASS, BeiDou), with linked sample data sets.
- [SoftGNSS-python](../../catalog/repos/perrysou__softgnss-python.md) - fit: medium - Python port of the SoftGNSS software-defined GPS receiver toolkit.
- [GNSS-SDRLIB](../../catalog/repos/taroz__gnss-sdrlib.md) - fit: low - Older open-source GNSS software receiver library in C with a GUI, supporting several front-ends and real-time RTKLIB output.
- [GNSS-matlab](../../catalog/repos/danipascual__gnss-matlab.md) - fit: low - MATLAB code to generate GNSS PRN and secondary codes, dataless signals and spectra, with real captures.
- [GPS L1 Direct Position Estimation module](../../catalog/repos/sergio-vicenzo__gpsl1-dpemodule.md) - fit: low - Plug-in module adding Direct Position Estimation (positioning directly in the correlation domain) to MATLAB two-step software receivers such as SoftGNSS.
- [pylgrim](../../catalog/repos/kirienko__pylgrim.md) - fit: low - Playground GNSS positioning code in Python/numpy that computes a static GPS position (50-100 m accuracy per the README) from RINEX 2.11 observations, with parsers for RINEX nav/obs, SP3 and IONEX plus Klobuchar, IONEX an
- [gnssrecbasics2020 - GNSS receiver course labs (MPEI)](../../catalog/repos/korogodin__gnssrecbasics2020.md) - fit: low - Assignments and lab reports for the first semester of the MPEI navigation receivers course (2020): signal model, statistical correlator equivalent, positioning accuracy and further labs.
- [SRNS - GNSS course homework (GLONASS/Galileo signals)](../../catalog/repos/daryamalafeeva__srns.md) - fit: low - Python homework for a course on GPS, GLONASS, Galileo and BeiDou: GLONASS satellite position and velocity from the almanac, a GLONASS L3OCp signal generator and Galileo E1-B/C signal shaping.
- [Приемники ГНСС - GNSS receiver design handbook (MPEI)](../../catalog/repos/korogodin__gnssrec.md) - fit: low - Source of a Russian-language textbook for the MPEI course on satellite navigation user equipment by I.

## Documents, talks, courses, datasets (13)

- [A Software-Defined GPS and Galileo Receiver: A Single-Frequency Approach](../../catalog/resources/borre-software-defined-gps-galileo-receiver.md) - book - Classic textbook that walks through a complete MATLAB GPS software receiver: acquisition, code/carrier tracking, navigation decoding and positioning.
- [Clock-Shift-Aided Blind Doppler Matching in Passive SDR Monitoring Data for LEO Doppler Positioning](../../catalog/resources/park-kim-seo-2026-blind-doppler-matching.md) - paper - Associates unlabeled Doppler traces in passive SDR spectrum-monitoring scans (no raw IQ) with TLE-predicted Starlink/OneWeb satellites, using slope-consistent segments, a clock-offset search and multi-metric matching, th
- [FGI Jammer Test 2023 Repository](../../catalog/resources/fgi-jammertest-2023-repository.md) - dataset - Open raw IQ recordings (GPS L1 C/A and Galileo E1, LabSat 3 Wideband) from Jammertest 2023 in Norway covering a high-power jamming case, incoherent spoofing and coherent spoofing scenarios, under CC BY 4.0.
- [GNSS-SDR documentation](../../catalog/resources/gnss-sdr-docs.md) - doc - Tutorials and reference for configuring the GNSS-SDR receiver, including signal processing blocks, front-end setup and monitoring outputs.
- [GNSS-SDR tutorials](../../catalog/resources/gnss-sdr-tutorials.md) - doc - Tutorials for the open-source GNSS-SDR software receiver: GNSS open-service signals, running with a low-cost RTL2832U DVB-T dongle as front end, monitoring the receiver's internal status, build-time options, cross-compil
- [GPS: An Introduction to Satellite Navigation, with an interactive Worldwide Laboratory using Smartphones](../../catalog/resources/stanford-gps-mooc-van-diggelen-enge.md) - course - Stanford MOOC (originally on Coursera) now freely available as a long video series: how GPS works, pseudoranges, orbits and signals, receiver design, assisted GPS and the future of GNSS, with smartphone-based labs.
- [IGS daily merged broadcast navigation files (BKG mirror)](../../catalog/resources/igs-bkg-brdc-broadcast-ephemeris.md) - dataset - Daily multi-GNSS RINEX navigation files that merge the broadcast ephemerides collected across the IGS network, mirrored by BKG over HTTPS and organised by year and day of year.
- [LEO-PNT With Starlink: Development of a Burst Detection Algorithm Based on Signal Measurements](../../catalog/resources/stock-2023-starlink-burst-detection.md) - paper - Measures Starlink signals and builds a correlation-based burst detector, then measures burst carrier frequency (Doppler) and estimates attainable positioning accuracy.
- [LTE Receiver Design and Multipath Analysis for Navigation in Urban Environments](../../catalog/resources/ion-webinar-shamaei-kassas.md) - talk - Design of a software receiver that extracts navigation observables from cellular LTE signals and analysis of multipath effects in urban settings.
- [Robust Interference Mitigation in GNSS Snapshot Receivers](../../catalog/resources/ion-webinar-calatrava.md) - talk - Interference mitigation techniques adapted to snapshot (short-capture) GNSS receivers used in low-power and IoT devices.
- [SDR приемник GPS на микроконтроллере](../../catalog/resources/habr-mcu-gps-sdr-2024.md) - blog - English: 'SDR GPS receiver on a microcontroller'.
- [UK DASA Early Market Engagement: PNT problem statement for uncrewed systems](../../catalog/resources/uk-dasa-emp-pnt-problem-statement-2024.md) - program - Published September 2024.
- [Помехи в глобальных навигационных спутниковых системах](../../catalog/resources/habr-gnss-interference-klimenko-2016.md) - blog - English: 'Interference in global navigation satellite systems'.

