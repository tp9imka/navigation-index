# Magnetic anomaly navigation

`concept:magnetic-nav`

MagNav: matching magnetometer readings to crustal anomaly maps; aircraft compensation.

**Parent:** [Assured / resilient PNT](../concepts/assured-pnt.md)

## Repositories (8)

- [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md) - fit: high - Julia package from the DAF-MIT AI Accelerator for airborne magnetic anomaly navigation: flight/INS data import or simulation, anomaly maps, aircraft magnetic compensation (Tolles-Lawson and neural models) and navigation 
- [MagNavPy](../repos/manasp21__magnav.py.md) - fit: high - Python port of MagNav.jl for magnetic navigation research.
- [AFIT MagNav example data](../repos/afit-eeng-magnav__example-data.md) - fit: high - Sample data for MagNav work: MIT-AIA anomaly maps, a challenge flight, North American magnetic anomaly grids and geoid files.
- [MagNav deep-learning compensation](../repos/naatyu__magnav.md) - fit: medium - Deep-learning approach to aircraft magnetic disturbance compensation built around the MagNav challenge data.
- [MagNav challenge submission (lw-kong)](../repos/lw-kong__magnav.md) - fit: medium - A public submission repository for the JuliaCon 2020 MagNav signal-enhancement challenge, implementing a learned aircraft-field compensation.
- [MAMMAL](../repos/powerbroker2__mammal.md) - fit: medium - Python package (Magnetic Anomaly Map Matching Airborne and Land) for simulating and processing aeromagnetic survey data and building anomaly maps for MagNav.
- [Rao-Blackwellized SLAM smoothing (magnetic)](../repos/manonkok__rao-blackwellized-slam-smoothing.md) - fit: medium - MATLAB code for Rao-Blackwellized particle smoothing for SLAM, including magnetic field mapping and map-matching localization with a magnetometer.
- [DroneMagNav](../repos/ajisrawi__dronemagnav.md) - fit: medium - Open hardware + firmware design for a drone magnetic-anomaly navigation board (ESP32-S3, magnetometer, IMU, baro) running particle-filter matching against a global anomaly map and feeding position to a flight controller 

## Documents, talks, courses, datasets (18)

- [Absolute Positioning Using the Earth's Magnetic Anomaly Field](../resources/canciani-afit-magnetic-anomaly-dissertation-2016.md) - report - AFIT dissertation establishing airborne magnetic anomaly navigation methods and flight-test evaluation, the basis for later AFRL/MIT MagNav work.
- [DARPA eying new quantum sensing program: Robust Quantum Sensors (RoQS)](../resources/darpa-roqs-2024.md) - blog - Report on DARPA's RoQS program to make quantum sensors robust to platform interference so they can support navigation without GPS on real vehicles.
- [Developing a Series of AI Challenges for the United States Department of the Air Force](../resources/daf-ai-challenges-arxiv.md) - paper - Describes the Air Force AI challenge series including MagNav, covering both the compensation stage and a navigation stage that turns cleaned readings into position estimates.
- [DIU solicitation: Transition of Quantum Sensing for navigation](../resources/diu-transition-quantum-sensing-2024.md) - blog - Coverage of DIU's Transition of Quantum Sensing call seeking quantum inertial sensors and magnetometers to extend navigation holdover when GPS is unavailable.
- [GAO-21-320SP: Defense Navigation Capabilities - DOD Is Developing PNT Alternatives to GPS](../resources/gao-21-320sp-gps-alternatives.md) - report - Technology assessment of DoD's alternative PNT efforts (inertial, vision, celestial, magnetic, signals of opportunity, clocks), with maturity status and challenges.
- [MagNav - MIT CSAIL open-source technologies](../resources/mit-cap-magnav-page.md) - doc - Overview page for MagNav as an open-source technology from the DAF-MIT AI Accelerator.
- [MagNav challenge flight data (Sander Geophysics, Zenodo)](../resources/magnav-sgs-flight-data.md) - dataset - Zenodo record of airborne magnetometer, INS and GNSS flight data with datasheets, collected for the MagNav challenge.
- [MagNav Challenge flight dataset (Zenodo)](../resources/magnav-zenodo-dataset.md) - dataset - Zenodo record holding the MagNav challenge flight data: magnetometer, INS, GPS truth and map data from survey flights.
- [MagNav Challenge Problem (DAF-MIT AI Accelerator)](../resources/magnav-challenge-site.md) - competition - Challenge site for airborne magnetic anomaly navigation: compensate the aircraft's own magnetic field out of magnetometer data so the remaining crustal anomaly can be map-matched for GPS-free navigation.
- [MagNav.jl documentation](../resources/magnav-jl-docs.md) - doc - Documentation and examples for MagNav.jl covering data loading, compensation models, map handling and navigation filters.
- [Magnetic Sensors in Flight Tests as Alternative PNT to GNSS](../resources/insidegnss-magnav-flight-tests-2020.md) - blog - Trade-press overview of Air Force magnetic navigation flight testing and the research path from AFIT to operational trials.
- [NATO DIANA's breakthrough solutions for secure communication and navigation](../resources/nato-diana-secure-comms-navigation.md) - blog - DIANA feature on cohort companies working on resilient navigation and secure communications, illustrating which approaches made it through selection.
- [Quantum Sensors for Navigation, From Physics to Field Deployment](../resources/ion-webinar-kealy.md) - talk - Overview of quantum sensing for navigation (atom interferometers, quantum magnetometers, clocks) and what it takes to move them from lab to field.
- [Quantum-assured magnetic navigation achieves positioning accuracy better than a strategic-grade INS in airborne and ground-based field trials](../resources/qctrl-quantum-assured-magnav-2025.md) - paper - Reports airborne and ground field trials of magnetic anomaly navigation using quantum magnetometers with map-matching, comparing against strategic-grade inertial navigation.
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../resources/afrl-magnav-challenge-2020.md) - paper - Defines the MagNav challenge from the DAF-MIT AI Accelerator: separate the Earth's magnetic anomaly signal from aircraft interference using real flight data, framed as a scientific machine-learning problem.
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../resources/afrl-mit-magnav-challenge-paper.md) - paper - Defines the AFRL/MIT MagNav challenge: remove the aircraft's own magnetic field from airborne magnetometer data so the Earth's anomaly field can be used for navigation, with released flight data and a scientific-ML basel
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../resources/magnav-signal-enhancement-arxiv.md) - paper - Paper defining the MagNav challenge: the physics of aircraft magnetic interference, the Tolles-Lawson baseline compensation, the dataset, and evaluation, framing it as a physics-informed ML problem.
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../resources/mit-magnav-challenge-data.md) - dataset - Challenge problem and airborne flight data for separating aircraft magnetic interference from the Earth's anomaly field so that magnetometers can be used for navigation against anomaly maps.

