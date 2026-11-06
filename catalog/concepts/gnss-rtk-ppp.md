# RTK / PPP precise positioning

`concept:gnss-rtk-ppp`

Carrier-phase differential and precise point positioning, corrections (RTCM, SSR, NTRIP).

**Parent:** [GNSS positioning](../concepts/gnss.md)

## Samples (1)

- [Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py](../samples/gnss-rinex-processing.md) - Downloads one day of public NOAA NGS CORS RINEX for a rover/base pair 30 km apart, runs RTKLIB demo5 rnx2rtkp in single-point and kinematic RTK modes with exact CLI flags, and scores both against the stations' published 

## Repositories (20)

- [RTKLIB](../repos/tomojitakasu__rtklib.md) - fit: high - The original open-source GNSS positioning package by T.
- [RTKLIB demo5 (rtklibexplorer)](../repos/rtklibexplorer__rtklib.md) - fit: high - Actively maintained RTKLIB fork tuned for low-cost receivers (especially u-blox), with many robustness fixes to ambiguity resolution, cycle-slip handling and receiver decoders.
- [PyGPSClient](../repos/semuconsulting__pygpsclient.md) - fit: high - Cross-platform Python GUI GNSS client that displays and configures receivers over NMEA, UBX, RTCM3 and other protocols, with built-in NTRIP and SPARTN clients.
- [pygnssutils](../repos/semuconsulting__pygnssutils.md) - fit: high - Python CLI and library utilities for reading, parsing and broadcasting GNSS streams, including an NTRIP client and caster/server and a socket server.
- [ROS NTRIP client](../repos/lord-microstrain__ntrip_client.md) - fit: high - ROS/ROS 2 node that connects to an NTRIP caster and publishes RTCM corrections, forwarding NMEA position back to the caster.
- [pyrtcm](../repos/semuconsulting__pyrtcm.md) - fit: high - Python parser for RTCM 3 messages (MSM observations, station info, ephemerides, SSR).
- [SparkFun u-blox GNSS v3 Arduino library](../repos/sparkfun__sparkfun_u-blox_gnss_v3.md) - fit: high - Arduino library for u-blox GNSS modules over I2C/SPI/serial, covering configuration, high-precision fixes and RTK correction input.
- [GICI-LIB](../repos/chichengcn__gici-open.md) - fit: medium - GNSS/INS/Camera integrated navigation library supporting a range of GNSS modes (SPP, RTK, PPP and variants) tightly fused with inertial and visual data via factor graph optimization.
- [PRIDE PPP-AR](../repos/pridelab__pride-pppar.md) - fit: medium - Wuhan University's open-source multi-GNSS precise point positioning package with ambiguity resolution, aimed at geodetic-grade post-processing.
- [rtklib-py](../repos/rtklibexplorer__rtklib-py.md) - fit: medium - Python port of the demo5 RTKLIB positioning core, currently focused on post-processed kinematic (PPK) solutions.
- [ntripcaster Docker](../repos/goblimey__ntripcaster.md) - fit: medium - Dockerfile and instructions to build and run the BKG NTRIP caster in a container.
- [GSDC 2023 solution (taroz)](../repos/taroz__gsdc2023.md) - fit: medium - Winning-team code for the Google Smartphone Decimeter Challenge 2023, using factor-graph style smartphone GNSS/IMU processing in MATLAB.
- [MatRTKLIB](../repos/taroz__matrtklib.md) - fit: medium - MATLAB wrapper exposing RTKLIB functions and data structures (observations, navigation data, solutions) as MATLAB objects.
- [ntripcaster (BKG standard caster)](../repos/nunojpg__ntripcaster.md) - fit: medium - Maintained mirror of the BKG standard NTRIP broadcaster in C for distributing RTCM correction streams over HTTP.
- [go-gnss/ntrip](../repos/go-gnss__ntrip.md) - fit: medium - Go library implementing NTRIP client, server and caster components.
- [ntripbrowser](../repos/emlid__ntripbrowser.md) - fit: medium - Command-line tool that fetches and displays an NTRIP caster's source table, optionally filtered by distance from a coordinate.
- [GraphGNSSLib](../repos/weisongwen__graphgnsslib.md) - fit: low - Open-source GNSS positioning and RTK package using factor graph optimization, built on RTKLIB data handling and ROS.
- [Ginan](../repos/geoscienceaustralia__ginan.md) - fit: low - Geoscience Australia's GNSS analysis toolkit for precise orbit determination and real-time/post-processed PPP, producing and consuming correction products.
- [Node-NTRIP caster](../repos/node-ntrip__caster.md) - fit: low - TypeScript/Node.js NTRIP caster library supporting NTRIP v1 and v2.
- [gnssanalysis](../repos/geoscienceaustralia__gnssanalysis.md) - fit: low - Geoscience Australia Python module of utilities for reading and comparing GNSS products (SP3, CLK, SINEX, Ginan outputs) and computing differences/statistics.

## Documents, talks, courses, datasets (13)

- [BKG Ntrip Client (BNC)](../resources/bkg-bnc.md) - doc - Page for BNC, BKG's multi-stream NTRIP client that records, decodes, converts to RINEX, monitors and can compute real-time PPP from correction streams.
- [Galileo High Accuracy Service Signal-In-Space ICD (HAS SIS ICD) Issue 1.0](../resources/galileo-has-sis-icd.md) - standard - Defines the free Galileo High Accuracy Service: PPP orbit, clock and bias corrections broadcast on E6-B (and via internet), including message structure and Reed-Solomon encoding.
- [GNSS Data Processing, Vol. I: Fundamentals and Algorithms (ESA TM-23)](../resources/esa-gnss-data-processing-vol1.md) - book - Free ESA textbook covering GNSS measurement modelling, SPP, differential positioning and PPP algorithms with full equations.
- [GNSS Data Processing, Vol. II: Laboratory Exercises (ESA TM-23)](../resources/esa-gnss-data-processing-vol2.md) - book - Hands-on lab volume with step-by-step exercises on real data using the gLAB software, from SPP to carrier-phase PPP.
- [Google Smartphone Decimeter Challenge 2023-2024](../resources/google-gsdc-2023.md) - competition - Kaggle competition with raw GNSS and IMU logs from Android phones in cars, scored on positioning accuracy against high-grade truth.
- [IGS products](../resources/igs-products.md) - doc - Catalog of International GNSS Service precise orbits, clocks, biases and atmospheric products used by PPP and precise processing.
- [ION GNSS+ Tutorials](../resources/ion-gnss-plus-tutorials.md) - course - Pre-conference tutorial programme of ION GNSS+, the main annual GNSS technical meeting: half-day in-depth courses by field experts on topics such as GNSS signals, receivers, PPP/RTK, inertial integration and interference
- [Navipedia - ESA GNSS encyclopedia](../resources/navipedia.md) - doc - ESA's free wiki covering GNSS fundamentals, systems, signals, receivers, augmentation and applications.
- [Navipedia: RTK Standards](../resources/navipedia-rtk-standards.md) - doc - Free encyclopedia overview of the RTCM correction message families and transport (NTRIP) used for real-time kinematic positioning.
- [NTRIP: Networked Transport of RTCM via Internet Protocol (BKG)](../resources/bkg-ntrip-about.md) - doc - BKG's overview of the NTRIP protocol for streaming GNSS corrections, with links to its caster, client and server software.
- [QZSS Performance Standards and Interface Specifications (IS-QZSS)](../resources/qzss-is-qzss.md) - standard - Japan's QZSS interface specifications covering GPS-compatible signals, the L6 CLAS centimetre-level augmentation and MADOCA PPP services.
- [RTCM 10403.x Differential GNSS (DGNSS) Services - Version 3](../resources/rtcm-sc104-standards.md) - standard - The paid-access RTCM v3 standard that defines the binary messages used to stream GNSS corrections and observations (legacy RTK 1001-1012, MSM 1-7 per constellation, ephemerides, SSR).
- [rtklibexplorer blog](../resources/rtklibexplorer-blog.md) - blog - Long-running practitioner blog on getting centimetre-level RTK/PPK from low-cost u-blox receivers with the demo5 RTKLIB fork, with configuration walk-throughs and data analysis.

