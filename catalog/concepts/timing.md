# Timing and time transfer

`concept:timing`

Clocks, holdover, PTP/NTP, GNSS-disciplined oscillators, chip-scale atomic clocks.

**Parent:** [Assured / resilient PNT](../concepts/assured-pnt.md)

## Repositories (4)

- [gpsd](../repos/gitlab.com__gpsd__gpsd.md) - fit: high - Service daemon that monitors GNSS receivers over serial/USB/network and serves decoded fixes, satellites and timing to client applications via JSON over TCP.
- [galmon](../repos/berthubert__galmon.md) - fit: medium - Open-source GNSS monitoring network and software that collects navigation data from volunteer receivers worldwide and publishes live health, ephemeris and timing statistics for Galileo, GPS, BeiDou and GLONASS.
- [GNSSTk](../repos/sgl-ut__gnsstk.md) - fit: low - C++ library (successor to GPSTk) from UT Austin ARL for GNSS data formats, time systems, ephemeris handling and positioning algorithms, with Python bindings.
- [KiwiSDR](../repos/jks-prv__kiwisdr.md) - fit: low - Web-accessible shortwave SDR receiver (10 kHz - 30 MHz) with built-in software GPS and a Loran-C/eLoran monitor extension.

## Documents, talks, courses, datasets (21)

- [Assessing Alternative Positioning, Navigation and Timing Technologies for Potential Deployment in the EU](../resources/jrc-assessing-apnt-2023.md) - report - JRC test campaign at Ispra of commercial alternative PNT systems (terrestrial beacons, LEO, eLoran-like, fibre timing and others) for DG DEFIS.
- [Complementary PNT and GPS Backup Technologies Demonstration Report](../resources/dot-complementary-pnt-report-2021.md) - report - Field demonstration of 11 GPS-backup technologies (including eLoran, terrestrial beacons, LEO and fiber timing) against defined scenarios, delivered to Congress.
- [Dana A. Goward on Geospatial FM podcast (RNT Foundation)](../resources/geospatial-fm-goward-podcast.md) - podcast - RNT Foundation post linking Dana Goward's Geospatial FM podcast appearance on GPS vulnerability and national PNT resilience policy.
- [DARPA Robust Optical Clock Network (ROCkN)](../resources/darpa-rockn.md) - doc - Program to field low-SWaP optical atomic clocks with timing holdover beyond GPS satellite clocks, in a portable airborne variant and a transportable land/sea variant, to keep precise time without GNSS.
- [DARPA's ROCkN Program Targets GNSS-Free Precision Timing in Contested Environments](../resources/darpa-rockn-insidegnss.md) - blog - Progress report on ROCkN field tests, including optical clock hardware flown on aircraft and deployed aboard a ship.
- [DHS S&T Positioning, Navigation, and Timing Program](../resources/dhs-st-pnt-program.md) - doc - Program hub for DHS PNT work: conformance framework, reference architecture, timing guidance and test events for critical infrastructure.
- [DOT Complementary PNT Action Plan](../resources/dot-complementary-pnt-action-plan-2023.md) - report - US DOT plan to drive adoption of complementary PNT for transportation and critical infrastructure via stakeholder engagement, specifications, field trials and test ranges.
- [eLoran Independent Assessment Team findings (PNT Advisory Board briefing)](../resources/faa-eloran-iat-2014.md) - talk - Briefing to the US Space-Based PNT Advisory Board summarizing the 2006-2008 independent assessment of eLoran as a GPS backup, its accuracy and its independent failure modes.
- [Executive Order 13905: Strengthening National Resilience Through Responsible Use of PNT Services](../resources/eo-13905-responsible-pnt.md) - standard - US executive order that defines 'responsible use of PNT' and tasks Commerce/NIST, DHS and others to produce PNT profiles, identify critical infrastructure dependencies and pilot-test resilience.
- [GPS: An Introduction to Satellite Navigation, with an interactive Worldwide Laboratory using Smartphones](../resources/stanford-gps-mooc-van-diggelen-enge.md) - course - Stanford MOOC (originally on Coursera) now freely available as a long video series: how GPS works, pseudoranges, orbits and signals, receiver design, assisted GPS and the future of GNSS, with smartphone-based labs.
- [ION Online Tutorial: The Basics of Satellite Navigation](../resources/ion-online-tutorial-basics-satnav.md) - course - ION's free online tutorial introducing satellite navigation fundamentals: trilateration with pseudoranges, clocks, signals, error sources and augmentation.
- [National Positioning, Navigation, and Timing Resilience R&D Plan](../resources/us-national-pnt-rd-plan-2021.md) - report - Federal R&D plan responding to EO 13905, laying out research priorities for resilient PNT: threat detection, alternative sources, timing distribution and integrity.
- [NIST IR 8323r1: Foundational PNT Profile - Applying the Cybersecurity Framework for the Responsible Use of PNT Services](../resources/nist-ir-8323r1-pnt-profile.md) - standard - Maps the NIST Cybersecurity Framework functions (identify, protect, detect, respond, recover) onto systems that produce or consume PNT data.
- [Quantum Sensors for Navigation, From Physics to Field Deployment](../resources/ion-webinar-kealy.md) - talk - Overview of quantum sensing for navigation (atom interferometers, quantum magnetometers, clocks) and what it takes to move them from lab to field.
- [Resilient PNT Conformance Framework](../resources/dhs-resilient-pnt-conformance-framework.md) - standard - Defines four cumulative resilience levels for PNT user equipment based on prevent, respond and recover behaviours, so buyers and vendors can describe how a receiver behaves under jamming or spoofing.
- [Resilient PNT Reference Architecture](../resources/dhs-resilient-pnt-reference-architecture.md) - standard - Companion to the conformance framework describing architectural patterns (source diversity, integrity checking, holdover) that map to its resilience levels.
- [SCPNT Photo and Video Gallery (PNT Symposium recordings archive)](../resources/stanford-scpnt-video-gallery.md) - video - Archive index of Stanford PNT Symposium recordings going back to 2007, organised by year into student and invited-speaker albums.
- [Should It Be TPN? Prioritizing Timing in Positioning and Navigation](../resources/ion-webinar-tpn.md) - talk - Webinar arguing for timing as the foundation of resilient PNT, covering precision terrestrial time distribution and timing/positioning from current and future LEO constellations.
- [Stanford PNT Symposium 2024 (18th annual)](../resources/stanford-pnt-symposium-2024.md) - talk - Page for the 28-29 October 2024 symposium with agenda, student and invited-speaker video albums, and slides; topics span GNSS, inertial sensing, timing and alternative navigation.
- [Stanford PNT Symposium 2025 (19th annual)](../resources/stanford-pnt-symposium-2025.md) - talk - Annual Stanford SCPNT symposium page (8-9 October 2025) with the agenda and links to recorded student talks (Day 1) and invited speaker talks (Day 2), plus downloadable slides for many presentations.
- [Ukrainian military's anti-drone GPS spoofing spills into civilians' phones](../resources/therecord-ukraine-spoofing-civilian-phones.md) - blog - Report on Ukraine's nationwide defensive spoofing against incoming drones and missiles, and its side effects on civilian devices' location and time.

