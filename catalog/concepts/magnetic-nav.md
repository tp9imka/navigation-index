# Magnetic anomaly navigation

`concept:magnetic-nav`

MagNav: matching magnetometer readings to crustal anomaly maps; aircraft compensation.

**Parent:** [Assured / resilient PNT](../concepts/assured-pnt.md)

## Samples (1)

- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../samples/magnav-quickstart.md) - A Julia walkthrough with MagNav.jl that downloads the public SGL 2020 challenge flight and Ottawa anomaly maps, compensates the scalar magnetometer with Tolles-Lawson on a calibration box, and runs the MagNav EKF against

## Repositories (8)

- [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md) - fit: high - Julia package from the DAF-MIT AI Accelerator for airborne magnetic anomaly navigation: flight/INS data import or simulation, anomaly maps, aircraft magnetic compensation (Tolles-Lawson and neural models) and navigation 
- [MagNavPy](../repos/manasp21__magnav.py.md) - fit: high - Python port of MagNav.jl for magnetic navigation research.
- [AFIT MagNav example data](../repos/afit-eeng-magnav__example-data.md) - fit: high - Sample data for MagNav work: MIT-AIA anomaly maps, a challenge flight, North American magnetic anomaly grids and geoid files.
- [MagNav deep-learning compensation](../repos/naatyu__magnav.md) - fit: medium - Deep-learning approach to aircraft magnetic disturbance compensation built around the MagNav challenge data.
- [MagNav challenge submission (lw-kong)](../repos/lw-kong__magnav.md) - fit: medium - A public submission repository for the JuliaCon 2020 MagNav signal-enhancement challenge, implementing a learned aircraft-field compensation.
- [MAMMAL](../repos/powerbroker2__mammal.md) - fit: medium - Python package (Magnetic Anomaly Map Matching Airborne and Land) for simulating and processing aeromagnetic survey data and building anomaly maps for MagNav.
- [Rao-Blackwellized SLAM smoothing (magnetic)](../repos/manonkok__rao-blackwellized-slam-smoothing.md) - fit: medium - MATLAB code for Rao-Blackwellized particle smoothing for SLAM, including magnetic field mapping and map-matching localization with a magnetometer.
- [DroneMagNav](../repos/ajisrawi__dronemagnav.md) - fit: medium - Open hardware + firmware design for a drone magnetic-anomaly navigation board (ESP32-S3, magnetometer, IMU, baro) running particle-filter matching against a global anomaly map and feeding position to a flight controller 

## Documents, talks, courses, datasets (23)

- [Absolute Positioning Using the Earth's Magnetic Anomaly Field](../resources/canciani-afit-magnetic-anomaly-dissertation-2016.md) - report - AFIT dissertation establishing airborne magnetic anomaly navigation methods and flight-test evaluation, the basis for later AFRL/MIT MagNav work.
- [DAF-MIT AI Accelerator MagNav real-time C-17 demonstration (2023)](../resources/daf-mit-magnav-c17-demo-2023.md) - program - In May 2023 the Air Force and MIT flew a real-time MagNav demo on a C-17A during exercise Golden Phoenix, training the compensation network in flight on a laptop.
- [DARPA eying new quantum sensing program: Robust Quantum Sensors (RoQS)](../resources/darpa-roqs-2024.md) - blog - Report on DARPA's RoQS program to make quantum sensors robust to platform interference so they can support navigation without GPS on real vehicles.
- [DARPA Robust Quantum Sensors (RoQS) - Phase 1](../resources/darpa-roqs-program.md) - program - RoQS (solicitation DARPA-PS-25-11) aims to make quantum sensors robust to platform vibration and motion so they work on real vehicles; Phase 1 launched August 2025 with compact sensors to be tested on a government helico
- [Developing a Series of AI Challenges for the United States Department of the Air Force](../resources/daf-ai-challenges-arxiv.md) - paper - Describes the Air Force AI challenge series including MagNav, covering both the compensation stage and a navigation stage that turns cleaned readings into position estimates.
- [DIU solicitation: Transition of Quantum Sensing for navigation](../resources/diu-transition-quantum-sensing-2024.md) - blog - Coverage of DIU's Transition of Quantum Sensing call seeking quantum inertial sensors and magnetometers to extend navigation holdover when GPS is unavailable.
- [DIU Transition of Quantum Sensing (TQS)](../resources/diu-tqs-program.md) - program - DIU programme fielding quantum sensors for PNT: lines of effort cover quantum inertial sensors, gravimeters for gravity-aided naval navigation, quantum magnetic sensing, magnetic navigation and component insertion, with 
- [European Defense Tech Hackathon series (Paris, London, Sheffield, Prague...)](../resources/european-defense-tech-hackathon.md) - program - Independent recurring European defense hackathon series.
- [GAO-21-320SP: Defense Navigation Capabilities - DOD Is Developing Positioning, Navigation, and Timing Technologies to Complement GPS](../resources/gao-21-320sp-gps-alternatives.md) - report - Technology assessment of DoD's alternative PNT efforts (inertial, vision, celestial, magnetic, signals of opportunity, clocks), with maturity status and challenges.
- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../resources/honeywell-vision-aided-navigation.md) - product - Honeywell's VAN correlates live visible or IR imagery against onboard reference maps for an absolute fix, paired with its inertial units.
- [MagNav - MIT CSAIL open-source technologies](../resources/mit-cap-magnav-page.md) - doc - Overview page for MagNav as an open-source technology from the DAF-MIT AI Accelerator.
- [MagNav challenge flight data (Sander Geophysics, Zenodo)](../resources/magnav-sgs-flight-data.md) - dataset - Zenodo record of airborne magnetometer, INS and GNSS flight data with datasheets, collected for the MagNav challenge.
- [MagNav Challenge flight dataset (Zenodo)](../resources/magnav-zenodo-dataset.md) - dataset - Zenodo record holding the MagNav challenge flight data: magnetometer, INS, GPS truth and map data from survey flights.
- [MagNav Challenge Problem (DAF-MIT AI Accelerator)](../resources/magnav-challenge-site.md) - competition - Challenge site for airborne magnetic anomaly navigation: compensate the aircraft's own magnetic field out of magnetometer data so the remaining crustal anomaly can be map-matched for GPS-free navigation.
- [MagNav.jl documentation](../resources/magnav-jl-docs.md) - doc - Documentation and examples for MagNav.jl covering data loading, compensation models, map handling and navigation filters.
- [Magnetic Sensors in Flight Tests as Alternative PNT to GNSS](../resources/insidegnss-magnav-flight-tests-2020.md) - blog - Trade-press overview of Air Force magnetic navigation flight testing and the research path from AFIT to operational trials.
- [NATO DIANA's breakthrough solutions for secure communication and navigation](../resources/nato-diana-secure-comms-navigation.md) - blog - DIANA feature on cohort companies working on resilient navigation and secure communications, illustrating which approaches made it through selection.
- [Q-CTRL Ironstone Opal quantum-assured magnetic navigation](../resources/qctrl-ironstone-opal.md) - product - Q-CTRL's navigation product pairs quantum magnetometers with its software to match measured crustal magnetic anomalies against maps (MagNav).
- [Quantum Sensors for Navigation, From Physics to Field Deployment](../resources/ion-webinar-kealy.md) - talk - Overview of quantum sensing for navigation (atom interferometers, quantum magnetometers, clocks) and what it takes to move them from lab to field.
- [Quantum-assured magnetic navigation achieves positioning accuracy better than a strategic-grade INS in airborne and ground-based field trials](../resources/qctrl-quantum-assured-magnav-2025.md) - paper - Reports airborne and ground field trials of magnetic anomaly navigation using quantum magnetometers with map-matching, comparing against strategic-grade inertial navigation.
- [SandboxAQ AQNav geomagnetic navigation](../resources/sandboxaq-aqnav.md) - product - AQNav is SandboxAQ's magnetic anomaly navigation system: magnetometers plus learned compensation, matched against magnetic anomaly maps.
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../resources/afrl-magnav-challenge-2020.md) - paper - Defines the AFRL/MIT MagNav challenge: remove the aircraft's own magnetic field from airborne magnetometer data so the Earth's anomaly field can be used for navigation, with released flight data and a scientific-ML basel
- [Навигация без GPS, которая уже работает](../resources/habr-nav-without-gps-overview-2025.md) - blog - English: 'Navigation without GPS that already works'.

