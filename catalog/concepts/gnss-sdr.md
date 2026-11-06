# Software-defined GNSS receivers

`concept:gnss-sdr`

Acquisition, tracking, navigation-message decoding in software on SDR front-ends.

**Parent:** [GNSS positioning](../concepts/gnss.md)

## Repositories (14)

- [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md) - fit: high - Full software-defined GNSS receiver built on GNU Radio: acquisition, tracking, navigation message decoding and PVT for GPS, Galileo, GLONASS and BeiDou signals from SDR front-ends or IQ files, including Galileo OSNMA sup
- [AIS-catcher](../repos/jvde-github__ais-catcher.md) - fit: high - AIS receiver and decoder for cheap SDRs (RTL-SDR, Airspy, HackRF, SDRplay, SoapySDR) with a built-in web map, JSON/NMEA output and feed sharing.
- [readsb](../repos/wiedehopf__readsb.md) - fit: high - ADS-B/Mode S decoder for RTL-SDR and other receivers with networking, JSON output, MLAT support and aggregation features.
- [GNSS-DSP-tools](../repos/pmonta__gnss-dsp-tools.md) - fit: high - Python code generators, acquisition and tracking for many GNSS signals (GPS, Galileo, GLONASS, BeiDou, NavIC and more) operating on IQ recordings.
- [Starlink LEO-PNT](../repos/przemyslawpiekarski__starlink-leo-pnt.md) - fit: high - Passive positioning using Starlink downlink signals as signals of opportunity: SDR capture, blind OFDM analysis, Doppler extraction, TDOA/FDOA solver and EKF with TLE-based orbits.
- [PocketSDR](../repos/tomojitakasu__pocketsdr.md) - fit: medium - Open hardware GNSS front-end plus a software receiver (Python and C) by the RTKLIB author, supporting a wide range of GNSS signals across L1/L2/L5/L6 bands.
- [FGI-GSRx](../repos/nlsfi__fgi-gsrx.md) - fit: medium - Multi-GNSS software receiver in MATLAB from the Finnish Geospatial Research Institute, with modular acquisition, tracking and navigation stages.
- [SoftGNSS v3.0 (maintained copy)](../repos/tmboc__softgnss.md) - fit: medium - Maintained copy of the classic Borre/Akos SoftGNSS MATLAB GPS L1 receiver with updates for several sampler front-ends.
- [CU Boulder GNSS SDR Collection](../repos/gnsscusdr__cu-sdr-collection.md) - fit: medium - University of Colorado Boulder collection of MATLAB software-defined GNSS receiver code-bases, organized per constellation (GPS, Galileo, GLONASS, BeiDou), with linked sample data sets.
- [SoftGNSS-python](../repos/perrysou__softgnss-python.md) - fit: medium - Python port of the SoftGNSS software-defined GPS receiver toolkit.
- [GNSS-SDRLIB](../repos/taroz__gnss-sdrlib.md) - fit: low - Older open-source GNSS software receiver library in C with a GUI, supporting several front-ends and real-time RTKLIB output.
- [GNSS-matlab](../repos/danipascual__gnss-matlab.md) - fit: low - MATLAB code to generate GNSS PRN and secondary codes, dataless signals and spectra, with real captures.
- [GPS L1 Direct Position Estimation module](../repos/sergio-vicenzo__gpsl1-dpemodule.md) - fit: low - Plug-in module adding Direct Position Estimation (positioning directly in the correlation domain) to MATLAB two-step software receivers such as SoftGNSS.
- [pylgrim](../repos/kirienko__pylgrim.md) - fit: low - GNSS software receiver written in Python for learning acquisition, tracking and positioning.

## Documents, talks, courses, datasets (9)

- [A Software-Defined GPS and Galileo Receiver: A Single-Frequency Approach](../resources/borre-software-defined-gps-galileo-receiver.md) - book - Classic textbook that walks through a complete MATLAB GPS software receiver: acquisition, code/carrier tracking, navigation decoding and positioning.
- [GNSS-SDR documentation](../resources/gnss-sdr-docs.md) - doc - Tutorials and reference for configuring the GNSS-SDR receiver, including signal processing blocks, front-end setup and monitoring outputs.
- [GNSS-SDR tutorials](../resources/gnss-sdr-tutorials.md) - doc - Tutorials for the open-source GNSS-SDR software receiver: signal acquisition and tracking, configuring front ends, processing recorded IQ files, and generating observables and PVT.
- [GPS: An Introduction to Satellite Navigation, with an interactive Worldwide Laboratory using Smartphones](../resources/stanford-gps-mooc-van-diggelen-enge.md) - course - Stanford MOOC (originally on Coursera) now freely available as a long video series: how GPS works, pseudoranges, orbits and signals, receiver design, assisted GPS and the future of GNSS, with smartphone-based labs.
- [LTE Receiver Design and Multipath Analysis for Navigation in Urban Environments](../resources/ion-webinar-shamaei-kassas.md) - talk - Design of a software receiver that extracts navigation observables from cellular LTE signals and analysis of multipath effects in urban settings.
- [Robust Interference Mitigation in GNSS Snapshot Receivers](../resources/ion-webinar-calatrava.md) - talk - Interference mitigation techniques adapted to snapshot (short-capture) GNSS receivers used in low-power and IoT devices.
- [SDR приемник GPS на микроконтроллере](../resources/habr-mcu-gps-sdr-2024.md) - blog - English: 'SDR GPS receiver on a microcontroller'.
- [UK DASA Early Market Engagement: PNT problem statement for uncrewed systems](../resources/uk-dasa-emp-pnt-problem-statement-2024.md) - program - Published September 2024.
- [Помехи в глобальных навигационных спутниковых системах](../resources/habr-gnss-interference-klimenko-2016.md) - blog - English: 'Interference in global navigation satellite systems'.

