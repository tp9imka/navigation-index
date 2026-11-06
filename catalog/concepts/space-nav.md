# Space and orbital navigation

`concept:space-nav`

Orbit determination, LEO-PNT, spacecraft navigation.

## Repositories (11)

- [Skyfield](../repos/skyfielders__python-skyfield.md) - fit: high - Python library for high-accuracy positions of stars, planets and Earth satellites, with proper time scales and reference frames.
- [tetra3](../repos/esa__tetra3.md) - fit: high - Fast lost-in-space plate solver for star trackers from ESA: identifies stars in an image and returns attitude using a precomputed pattern database.
- [Starlink LEO-PNT](../repos/przemyslawpiekarski__starlink-leo-pnt.md) - fit: high - Passive positioning using Starlink downlink signals as signals of opportunity: SDR capture, blind OFDM analysis, Doppler extraction, TDOA/FDOA solver and EKF with TLE-based orbits.
- [OpenStarTracker](../repos/ubnanosatlab__openstartracker.md) - fit: medium - Open-source star tracker using a Bayesian star identification approach, developed by the University at Buffalo Nanosatellite Lab.
- [NASA COTS Star Tracker](../repos/nasa__cots-star-tracker.md) - fit: medium - NASA software for building a star tracker from commercial off-the-shelf cameras, including calibration and attitude solution.
- [LOST](../repos/uwcubesat__lost.md) - fit: medium - Open-source star tracker (C++) covering centroiding, star identification and attitude estimation, from the UW CubeSat team.
- [SPEED+ baseline](../repos/tpark94__speedplusbaseline.md) - fit: medium - PyTorch baselines and domain-bridging methods for spacecraft pose estimation on the SPEED+ dataset used in ESA Kelvins SPEC2021.
- [UT Starlink signal simulator](../repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md) - fit: medium - MATLAB-style utility functions from UT Austin's Radionavigation Lab for simulating Starlink Ku-band downlink signals, with playground examples.
- [SPEL Open Star Tracker](../repos/spel-uchile__star_tracker.md) - fit: low - Open star tracker software from the University of Chile space lab, flown on SUCHAI nanosatellites.
- [JointLoc](../repos/luoxubo__jointloc.md) - fit: low - Real-time visual localization framework for planetary UAVs that jointly uses relative and absolute pose estimation against orbital maps.
- [FederNet](../repos/sirbastiano__federnet.md) - fit: low - Terrain relative navigation for planetary landing that detects craters with a Mask R-CNN and matches them to a catalog using projective invariants.

## Documents, talks, courses, datasets (19)

- [Ad Astra: Navigation with Megaconstellation LEO Satellites (GRASP on Robotics)](../resources/kassas-ad-astra-leo-grasp-2024.md) - talk - UPenn GRASP seminar by Zak Kassas on opportunistic PNT from Starlink, OneWeb and other LEO megaconstellations, addressing unknown signal structure, poor ephemerides and clock instability with his STAN (simultaneous track
- [Enter LEO on the GNSS Stage: Navigation with Starlink Satellites](../resources/kassas-starlink-navigation.md) - paper - Opportunistic navigation using Starlink downlink signals without cooperation from the operator, describing two ways to extract navigation observables from unknown signals.
- [ESA Kelvins Satellite Pose Estimation Competition 2021 (SPEED+)](../resources/kelvins-pose-estimation-2021.md) - competition - Follow-up Kelvins challenge focused on bridging the domain gap: train on synthetic images, test on hardware-in-the-loop lightbox and sunlamp images.
- [First results from three years of GNSS interference monitoring from low Earth orbit](../resources/ion-webinar-humphreys.md) - talk - UT Radionavigation Lab results from detecting and geolocating terrestrial GNSS jammers using receivers on LEO satellites, revealing persistent interference hotspots in conflict regions.
- [From Sea to Space: Advancing Perception in Harsh Domains (ICRA 2026 workshop)](../resources/icra-2026-sea-to-space-perception-workshop.md) - talk - ICRA 2026 (Vienna) workshop on perception for underwater, space and terrestrial field robots, including localization and mapping in degraded sensing, GPS-denied global localization, novel sensors (sonar, radar, thermal, 
- [Implementation and Accuracy of Doppler Navigation with LEO Satellites](../resources/ion-webinar-baron.md) - talk - Implementation-focused talk on navigating with Doppler measurements from LEO satellites and the accuracy achieved in practice.
- [ION GNSS+ Short Courses (GPS/GNSS 101 and more)](../resources/ion-gnss-plus-short-courses.md) - course - Short courses run at ION GNSS+ for registered attendees, including a GPS/GNSS 101 course taught by John Raquet and a space applications of GNSS course by Penina Axelrad.
- [ION Webinar Series (archive and YouTube recordings)](../resources/ion-webinar-series.md) - lecture-series - Running ION webinar programme with summary pages per talk and a YouTube playlist of past recordings (youtube.com/playlist?list=PLPiP0PPIY2x4k1OemLZH8_OJPyLjGLYFY).
- [Navigation using carrier Doppler shift from a LEO constellation: TRANSIT on steroids](../resources/ion-webinar-psiaki.md) - talk - Analysis of Doppler-only positioning from large LEO constellations, revisiting the TRANSIT concept with modern megaconstellations and quantifying achievable accuracy.
- [Navigation with Multi-Constellation LEO Satellite Signals of Opportunity: Starlink, OneWeb, Orbcomm, and Iridium](../resources/kassas-multi-constellation-leo.md) - paper - Experimental multi-constellation LEO SoOP navigation combining four commercial constellations, using the simultaneous tracking and navigation (STAN) framework.
- [Satellite Pose Estimation Challenge: Dataset, Competition Design and Results](../resources/kelvins-spec2019-paper.md) - paper - ESA Kelvins / Stanford competition on monocular spacecraft pose estimation, analyzing 48 entries.
- [Should It Be TPN? Prioritizing Timing in Positioning and Navigation](../resources/ion-webinar-tpn.md) - talk - Webinar arguing for timing as the foundation of resilient PNT, covering precision terrestrial time distribution and timing/positioning from current and future LEO constellations.
- [Signal Structure of the Starlink Ku-Band Downlink](../resources/humphreys-2023-starlink-signal-structure.md) - paper - Reverse-engineers the Starlink Ku-band downlink as OFDM and identifies synchronization sequences usable for opportunistic ranging and positioning.
- [Space Security Challenge 2022: Hack-A-Sat 3](../resources/afrl-hack-a-sat-2022.md) - competition - AFRL/Space Force capture-the-flag on satellite and ground-segment security; challenge code from several editions has been released publicly.
- [Stanford NAV Lab (Grace Gao)](../resources/stanford-navlab.md) - doc - Grace Gao's lab working on robust navigation for autonomous systems: GNSS in urban environments, sensor fusion, integrity and lunar PNT.
- [Survey on positioning technology based on signal of opportunity from low earth orbit](../resources/leo-soop-positioning-survey-2025.md) - paper - Open-access survey of LEO signals-of-opportunity positioning: Doppler methods, error sources, and extracting observables from signals never designed for navigation (unknown codes, poor onboard clocks).
- [The First Carrier Phase Tracking and Positioning Results With Starlink LEO Satellite Signals](../resources/kassas-2022-starlink-carrier-phase.md) - paper - IEEE TAES letter showing carrier-phase tracking of Starlink signals with unknown structure and positioning from several satellites.
- [Unveiling Starlink for PNT](../resources/ion-webinar-kozhaya.md) - talk - Presents work on exploiting Starlink downlink signals for opportunistic positioning, including signal structure discovery and Doppler/pseudorange-based navigation results.
- [UT Austin Radionavigation Laboratory (talks, papers, news)](../resources/ut-radionavigation-lab.md) - blog - Lab site of Todd Humphreys' group, indexing talks, briefings and papers on GNSS spoofing detection, LEO interference monitoring, Starlink-based PNT and precise automotive positioning.

