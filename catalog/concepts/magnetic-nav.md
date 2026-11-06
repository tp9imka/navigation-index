# Magnetic anomaly navigation

`concept:magnetic-nav`

MagNav: matching magnetometer readings to crustal anomaly maps; aircraft compensation.

**Parent:** [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

## Samples (1)

- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../../catalog/samples/magnav-quickstart.md) - A Julia walkthrough with MagNav.jl that downloads the public SGL 2020 challenge flight and Ottawa anomaly maps, compensates the scalar magnetometer with Tolles-Lawson on a calibration box, and runs the MagNav EKF against

## Guides (4)

- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) - After this chapter you can explain the five main ways to get an absolute position without GNSS - image-to-map matching, terrain matching, magnetic anomaly matching, celestial fixes and signals of opportunity - pick the o
- [Landscape: what judges already know](../../docs/landscape/README.md) - Commercial products, funded programmes and 2025-2026 trends in GNSS-denied navigation, so a hackathon team can place its idea against what is already sold or funded.
- [Navigation trends 2025-2026](../../docs/landscape/trends-2025-2026.md) - Each item: what changed, the source, and what it means for a navigation hackathon project.
- [Programs, challenges and hackathons (2023-2026)](../../docs/landscape/programs-and-challenges.md) - What funders publish as navigation problem statements.

## Repositories (10)

- [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md) - fit: high - Julia package from the DAF-MIT AI Accelerator for airborne magnetic anomaly navigation: flight/INS data import or simulation, anomaly maps, aircraft magnetic compensation (Tolles-Lawson and neural models) and navigation 
- [MagNavPy](../../catalog/repos/manasp21__magnav.py.md) - fit: high - Community Python port of MIT's MagNav.jl: loads flight, INS and magnetometer data and magnetic anomaly maps (with upward continuation), runs Tolles-Lawson and neural-network aircraft compensation, and provides an EKF / M
- [AFIT MagNav example data](../../catalog/repos/afit-eeng-magnav__example-data.md) - fit: high - Sample data for MagNav work: MIT-AIA anomaly maps, a challenge flight, North American magnetic anomaly grids and geoid files.
- [MagNav deep-learning compensation](../../catalog/repos/naatyu__magnav.md) - fit: medium - Deep-learning approach to aircraft magnetic disturbance compensation built around the MagNav challenge data.
- [MAINS](../../catalog/repos/huang-chuan__mainsvsmagekf.md) - fit: medium - Magnetic-field aided inertial navigation system for indoor positioning, compared against a magnetic EKF.
- [MagNav challenge submission (lw-kong)](../../catalog/repos/lw-kong__magnav.md) - fit: medium - A public submission repository for the JuliaCon 2020 MagNav signal-enhancement challenge, implementing a learned aircraft-field compensation.
- [MAMMAL](../../catalog/repos/powerbroker2__mammal.md) - fit: medium - Python package (Magnetic Anomaly Map Matching Airborne and Land) for simulating and processing aeromagnetic survey data and building anomaly maps for MagNav.
- [Rao-Blackwellized SLAM smoothing (magnetic)](../../catalog/repos/manonkok__rao-blackwellized-slam-smoothing.md) - fit: medium - MATLAB code for Rao-Blackwellized particle smoothing for SLAM, including magnetic field mapping and map-matching localization with a magnetometer.
- [DroneMagNav](../../catalog/repos/ajisrawi__dronemagnav.md) - fit: medium - Hardware + firmware design for a drone magnetic-anomaly navigation board (ESP32-S3, magnetometer, IMU, baro) running particle-filter matching against a global anomaly map and feeding position to a flight controller over 
- [Magnetic-field odometry](../../catalog/repos/huang-chuan__magnetic-field-odometry.md) - fit: low - MATLAB simulation of a tightly-integrated magnetic-field aided INS using a magnetometer array; it generates its own trajectory and sensor data.

## Documents, talks, courses, datasets (30)

- [Absolute Positioning Using the Earth's Magnetic Anomaly Field](../../catalog/resources/canciani-afit-magnetic-anomaly-dissertation-2016.md) - report - AFIT dissertation establishing airborne magnetic anomaly navigation methods and flight-test evaluation, the basis for later AFRL/MIT MagNav work.
- [Absolute Positioning Using the Earth's Magnetic Anomaly Field](../../catalog/resources/canciani-raquet-2016-absolute-positioning-magnetic-anomaly.md) - paper - NAVIGATION 63(2) journal paper: a particle-filter framework that aids an aircraft INS with optically pumped cesium magnetometer measurements compared against an anomaly map, while estimating the temporal variations of th
- [Advanced Aeromagnetic Compensation Models for Airborne Magnetic Anomaly Navigation](../../catalog/resources/gnadt-2022-mit-phd-aeromagnetic-compensation.md) - report - MIT AeroAstro PhD thesis (advisor Alan Edelman) on removing the aircraft's own magnetic field so magnetic anomaly maps can be used for navigation.
- [Airborne Magnetic Anomaly Navigation](../../catalog/resources/canciani-raquet-2017-airborne-magnetic-anomaly-navigation.md) - paper - IEEE TAES 53(1) paper describing a passive airborne navigation system (scalar magnetometer, INS, barometer, anomaly map) with a particle filter and a full measurement equation linking magnetometer readings to the map.
- [Airborne Magnetic Anomaly Navigation with Neural-Network-Augmented Online Calibration](../../catalog/resources/hager-2026-magnav-nn-online-calibration.md) - paper - Published in the Journal of Guidance, Control, and Dynamics (2026).
- [DAF-MIT AI Accelerator MagNav real-time C-17 demonstration (2023)](../../catalog/resources/daf-mit-magnav-c17-demo-2023.md) - program - In May 2023 the Air Force and MIT flew a real-time MagNav demo on a C-17A during exercise Golden Phoenix, training the compensation network in flight on a laptop.
- [DAF-MIT AIA Open Flight Data for Magnetic Navigation Research](../../catalog/resources/magnav-sgs-flight-data.md) - dataset - Zenodo record of airborne magnetometer, INS and GNSS flight data with datasheets, collected for the MagNav challenge.
- [DARPA eyeing new quantum sensing program](../../catalog/resources/darpa-roqs-2024.md) - blog - Report on DARPA's RoQS program to make quantum sensors robust to platform interference so they can support navigation without GPS on real vehicles.
- [DARPA Robust Quantum Sensors (RoQS) - Phase 1](../../catalog/resources/darpa-roqs-program.md) - program - RoQS (solicitation DARPA-PS-25-11) aims to make quantum sensors robust to platform vibration and motion so they work on real vehicles; Phase 1 launched August 2025 with compact sensors to be tested on a government helico
- [Derivation and Extensions of the Tolles-Lawson Model for Aeromagnetic Compensation](../../catalog/resources/gnadt-2022-tolles-lawson-derivation.md) - paper - Short open reference note that re-derives the Tolles-Lawson aircraft magnetic field model (permanent, induced and eddy-current terms), states where the assumptions enter, describes the calibration procedure, and adds a s
- [Developing a Series of AI Challenges for the United States Department of the Air Force](../../catalog/resources/daf-ai-challenges-arxiv.md) - paper - Describes the Air Force AI challenge series including MagNav, covering both the compensation stage and a navigation stage that turns cleaned readings into position estimates.
- [DIU launches new emerging tech portfolio, solicits industry for quantum sensing capabilities](../../catalog/resources/diu-transition-quantum-sensing-2024.md) - blog - Coverage of DIU's Transition of Quantum Sensing call seeking quantum inertial sensors and magnetometers to extend navigation holdover when GPS is unavailable.
- [DIU Transition of Quantum Sensing (TQS)](../../catalog/resources/diu-tqs-program.md) - program - DIU programme fielding quantum sensors for PNT: lines of effort cover quantum inertial sensors, gravimeters for gravity-aided naval navigation, quantum magnetic sensing, magnetic navigation and component insertion, with 
- [European Defense Tech Hackathon series (Paris, London, Sheffield, Prague...)](../../catalog/resources/european-defense-tech-hackathon.md) - program - Independent recurring European defense hackathon series.
- [GAO-21-320SP: Defense Navigation Capabilities - DOD Is Developing Positioning, Navigation, and Timing Technologies to Complement GPS](../../catalog/resources/gao-21-320sp-gps-alternatives.md) - report - Technology assessment of DoD's alternative PNT efforts (inertial, vision, celestial, magnetic, signals of opportunity, clocks), with maturity status and challenges.
- [Honeywell Vision Aided Navigation (Alternative Navigation Suite)](../../catalog/resources/honeywell-vision-aided-navigation.md) - product - Honeywell's VAN correlates live visible or IR imagery against onboard reference maps for an absolute fix, paired with its inertial units.
- [MagNav - MIT CSAIL open-source technologies](../../catalog/resources/mit-cap-magnav-page.md) - doc - Overview page for MagNav as an open-source technology from the DAF-MIT AI Accelerator.
- [MagNav Challenge flight dataset (Zenodo)](../../catalog/resources/magnav-zenodo-dataset.md) - dataset - Zenodo record holding the MagNav challenge flight data: magnetometer, INS, GPS truth and map data from survey flights.
- [MagNav Challenge Problem (DAF-MIT AI Accelerator)](../../catalog/resources/magnav-challenge-site.md) - competition - Challenge site for airborne magnetic anomaly navigation: compensate the aircraft's own magnetic field out of magnetometer data so the remaining crustal anomaly can be map-matched for GPS-free navigation.
- [MagNav.jl documentation](../../catalog/resources/magnav-jl-docs.md) - doc - Documentation and examples for MagNav.jl covering data loading, compensation models, map handling and navigation filters.
- [Magnetic Navigation on an F-16 Aircraft Using Online Calibration](../../catalog/resources/canciani-2022-f16-magnav-online-calibration.md) - paper - IEEE TAES 58(1) paper on magnetic anomaly navigation flown on an F-16, where the platform's magnetic interference is far larger than on survey aircraft and drifts.
- [Magnetic Sensors in Flight Tests as Alternative PNT to GNSS](../../catalog/resources/insidegnss-magnav-flight-tests-2020.md) - blog - Trade-press overview of Air Force magnetic navigation flight testing and the research path from AFIT to operational trials.
- [NATO DIANA's breakthrough solutions for secure communication and navigation](../../catalog/resources/nato-diana-secure-comms-navigation.md) - blog - DIANA feature on cohort companies working on resilient navigation and secure communications, illustrating which approaches made it through selection.
- [Q-CTRL Ironstone Opal quantum-assured magnetic navigation](../../catalog/resources/qctrl-ironstone-opal.md) - product - Q-CTRL's navigation product pairs quantum magnetometers with its software to match measured crustal magnetic anomalies against maps (MagNav).
- [Quantum Sensors for Navigation - From Physics to Field Deployment](../../catalog/resources/ion-webinar-kealy.md) - talk - Overview of quantum sensing for navigation (atom interferometers, quantum magnetometers, clocks) and what it takes to move them from lab to field.
- [Quantum-assured magnetic navigation achieves positioning accuracy better than a strategic-grade INS in airborne and ground-based field trials](../../catalog/resources/qctrl-quantum-assured-magnav-2025.md) - paper - Reports airborne and ground field trials of magnetic anomaly navigation using quantum magnetometers with map-matching, comparing against strategic-grade inertial navigation.
- [SandboxAQ AQNav geomagnetic navigation](../../catalog/resources/sandboxaq-aqnav.md) - product - AQNav is SandboxAQ's magnetic anomaly navigation system: magnetometers plus learned compensation, matched against magnetic anomaly maps.
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../../catalog/resources/afrl-magnav-challenge-2020.md) - paper - Defines the AFRL/MIT MagNav challenge: remove the aircraft's own magnetic field from airborne magnetometer data so the Earth's anomaly field can be used for navigation, with released flight data and a scientific-ML basel
- [Навигация без GPS, которая уже работает](../../catalog/resources/habr-nav-without-gps-overview-2025.md) - blog - English: 'Navigation without GPS that already works'.
- [Способи навігації БПЛА у складних умовах зовнішнього середовища](../../catalog/resources/kpi-hehelskyi-avrutov-uav-nav-complex-env-2025.md) - paper - English: 'UAV navigation methods in complex environmental conditions' (Mechanics of Gyroscopic Systems, No.

