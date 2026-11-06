# Maritime navigation

`concept:maritime-nav`

Surface vessel navigation, AIS, ECDIS/charts, USVs.

## Samples (2)

- [GNSS spoofing signatures in real AIS tracks: detectors, injected ground truth, GeoJSON and CoT](../../catalog/samples/maritime-ais-spoofing.md) - Shore-side detection of GNSS spoofing from the AIS picture, on real Danish Maritime Authority AIS (partial HTTP-range download of a daily file, ~4.4 h, 1.7 M fixes, 2.5-3 k vessels).
- [USV own-ship navigation under GNSS spoofing: radar-to-chart fixes and an integrity monitor in the Oresund](../../catalog/samples/usv-gnss-denied-nav.md) - A simulated USV runs a 19.6 km transit over real geography (Lillgrund => Drogden channel => Copenhagen approach) built from OpenStreetMap coastline, Oresund bridge, wind turbines and seamarks, with 75 min of real Danish 

## Guides (1)

- [8. Maritime, underwater, ground and dismounted](../../docs/primer/08-maritime-underwater-ground.md) - After this chapter you know how navigation changes off the drone: what ships broadcast and how spoofing shows up in it, how vehicles navigate underwater where no radio reaches, how ground robots and pedestrians dead-reck

## Repositories (27)

- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [OpenCPN](../../catalog/repos/opencpn__opencpn.md) - fit: high - Cross-platform open-source chartplotter and navigation application that displays raster and S-57 vector charts, ingests GPS and AIS feeds, and runs waypoint routes.
- [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md) - fit: high - AIS receiver and decoder for cheap SDRs (RTL-SDR, Airspy, HackRF, SDRplay, SoapySDR) with a built-in web map, JSON/NMEA output and feed sharing.
- [Virtual RobotX (VRX)](../../catalog/repos/osrf__vrx.md) - fit: high - Gazebo-based simulation environment for the RobotX maritime autonomy competition, with a WAM-V USV model, waves, wind, sensors and scored tasks such as station keeping, wayfinding and perception.
- [BlueOS](../../catalog/repos/bluerobotics__blueos.md) - fit: high - Blue Robotics' onboard software platform for ROVs and USVs: web UI, ArduPilot management, MAVLink routing and a Docker extension system on a Raspberry Pi companion computer.
- [Signal K Server](../../catalog/repos/signalk__signalk-server.md) - fit: high - Node.js server implementing the Signal K open marine data standard: it ingests NMEA 0183, NMEA 2000 and other boat buses and republishes everything as a JSON data model over REST and WebSocket, with a plugin ecosystem.
- [Stonefish](../../catalog/repos/patrykcieslak__stonefish.md) - fit: high - C++ simulation library for marine robotics with hydrodynamics, underwater rendering and sensors including DVL, USBL, multibeam and forward-looking sonar; has a ROS wrapper.
- [pyais](../../catalog/repos/m0r13n__pyais.md) - fit: high - Python library for decoding and encoding AIS NMEA sentences (AIVDM/AIVDO), including multi-part messages and streaming from sockets or files.
- [MOOS-IvP](../../catalog/repos/moos-ivp__moos-ivp.md) - fit: high - Long-running autonomy middleware (MOOS) plus the IvP Helm behaviour-based multi-objective decision engine, used widely for autonomous marine vehicles, including COLREGs-aware collision avoidance behaviours.
- [NTNU colav-simulator](../../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) - fit: high - Python framework from the NTNU Autoship centre for simulating and evaluating autonomous ship collision avoidance controllers, open-sourced in autumn 2025, with scenario generation and evaluation tooling.
- [CANboat](../../catalog/repos/canboat__canboat.md) - fit: medium - Toolkit for NMEA 2000 networks: a PGN decoder/analyzer plus utilities to read, write and convert N2K and NMEA 0183 messages, used largely for reverse-engineering marine bus traffic.
- [OpenCPN radar_pi](../../catalog/repos/opencpn-radar-pi__radar_pi.md) - fit: medium - OpenCPN plugin that connects to Navico and some Garmin and Raymarine marine radars and overlays radar imagery and ARPA-style targets on the chart.
- [Signal K Specification](../../catalog/repos/signalk__specification.md) - fit: medium - The JSON schema and specification for the Signal K marine data format covering navigation, environment, propulsion and other vessel data paths.
- [MBZIRC Maritime Grand Challenge simulator](../../catalog/repos/osrf__mbzirc.md) - fit: medium - Simulator (Ignition Fortress + ROS 2) for the MBZIRC Maritime Grand Challenge where UAVs and USVs cooperate in a GNSS-denied environment.
- [MassMIND](../../catalog/repos/uml-marine-robotics__massmind.md) - fit: medium - Long-wave infrared image dataset of a harbour environment with semantic and instance segmentation masks for maritime scene understanding.
- [celnav](../../catalog/repos/ms8r__celnav.md) - fit: medium - Small Tkinter desktop app for celestial navigation on a boat: computes the Nautical Almanac daily-page data with PyEphem, reduces sights and fixes position from two LOPs, correcting for vessel motion between sights.
- [celestial-navigation toolkit](../../catalog/repos/alinnman__celestial-navigation.md) - fit: medium - Python toolkit for classic celestial navigation sight reduction, usable offline on a phone.
- [LaRS evaluator](../../catalog/repos/lojzezust__lars_evaluator.md) - fit: medium - Evaluation scripts for LaRS, a panoptic maritime obstacle detection benchmark spanning lakes, rivers and seas.
- [signalk-to-nmea0183](../../catalog/repos/signalk__signalk-to-nmea0183.md) - fit: medium - Signal K server plugin that converts Signal K data back into NMEA 0183 sentences for legacy displays and autopilots.
- [MOOS-IvP COLREGs master's research code](../../catalog/repos/d2snc__moos-ivp-masters.md) - fit: medium - MOOS-IvP applications from a 2025 master's project at Universidade de Sao Paulo implementing COLREGs-compliant collision avoidance for USVs, including a modified A* planner, a velocity-obstacle method and a virtual-conta
- [GNSS jamming detection on maritime Antarctica dataset](../../catalog/repos/fahadwebd__machine-learning-based-gnss-jamming-detection-on-antartica-dataset.md) - fit: medium - Thesis code for ML jamming detection and temporal generalisation using real maritime receiver diagnostics (u-blox MON-RF, MON-SPAN, RXM-MEASX) from a public Antarctica voyage dataset.
- [VIMMJIPDA tracker interface](../../catalog/repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md) - fit: medium - Interface that runs the VIMMJIPDA multi-target tracker (visibility, interacting multiple models, JIPDA) inside the NTNU colav-simulator; open-sourced November 2025.
- [pyMHT](../../catalog/repos/erikliland__pymht.md) - fit: low - Track-oriented multi-hypothesis multi-target tracker in Python developed for maritime radar tracking research.
- [Aeolus Ocean](../../catalog/repos/aavek__aeolus-ocean.md) - fit: low - Collision avoidance simulator for COLREG-compliant autonomous ship navigation intended for use as a digital twin under varied weather and day/night conditions.
- [noaadata](../../catalog/repos/schwehr__noaadata.md) - fit: low - Pure-Python AIS decode and encode library from a long-time AIS researcher, with message definitions and utilities for working with NOAA and coastal AIS data.
- [OpenCPN celestial navigation plugin](../../catalog/repos/seandepagnier__celestial_navigation_pi.md) - fit: low - OpenCPN plugin for entering sextant sights and plotting lines of position and fixes on the chart.
- [navalm](../../catalog/repos/kq6up__navalm.md) - fit: low - Nautical almanac and celestial sight reduction for Unix/Linux with CLI, ncurses and web interfaces.

## Documents, talks, courses, datasets (20)

- [2025 Was a Stress Test & Maritime AI™ Is the Only Way to Pass](../../catalog/resources/windward-2025-maritime-stress-test.md) - blog - Windward's quarter-by-quarter review of 2025 maritime risk: sanctions, dark fleet growth, flag-registry fraud and GNSS interference.
- [Above Us Only Stars: Exposing GPS Spoofing in Russia and Syria](../../catalog/resources/c4ads-above-us-only-stars.md) - report - Open-source investigation using AIS ship tracks, public records and ISS-based measurements to map thousands of GNSS spoofing events around Russia, Crimea and Syria, many linked to protection of VIPs and bases.
- [COLREGs - Convention on the International Regulations for Preventing Collisions at Sea, 1972](../../catalog/resources/imo-colregs.md) - standard - IMO page for the collision regulations that define give-way and stand-on duties, lights and signals; the rule set autonomous surface vessels must encode.
- [Danish Maritime Authority historical AIS data](../../catalog/resources/dma-historical-ais.md) - dataset - Daily zip files, one CSV per UTC day, holding every AIS report received by the Danish shore network across Danish waters and approaches (Skagerrak, Kattegat, the belts, western Baltic).
- [ERF26 workshop: Innovation and developments in robotic GNSS-denied localisation for inspection & maintenance](../../catalog/resources/erf26-sintef-gnss-denied-localisation-workshop.md) - talk - European Robotics Forum 2026 workshop (Stavanger) organised by SINTEF on GNSS-denied robot localisation in indoor, offshore, underground and urban-canyon settings, bringing together researchers, vendors and end users.
- [ITU-R M.1371-6 - Technical characteristics for VHF automatic identification system using time division multiple access in the maritime mobile service](../../catalog/resources/itu-r-m1371-ais.md) - standard - The ITU recommendation defining AIS radio, TDMA access and message formats that decoders such as pyais implement.
- [LaRS: A Diverse Panoptic Maritime Obstacle Detection Dataset and Benchmark](../../catalog/resources/lars-maritime-obstacle-dataset-2023.md) - dataset - ICCV 2023 panoptic obstacle detection benchmark from lakes, rivers and seas: over 4,000 per-pixel labelled key frames, each with nine preceding frames (40k+ frames), 11 classes and an online evaluation server.
- [MassMIND: Massachusetts Maritime INfrared Dataset](../../catalog/resources/massmind-paper-2022.md) - paper - Paper describing a labelled LWIR maritime dataset of 2,916 images from in and around Boston Harbor, segmented into seven classes, with UNet, PSPNet and DeepLabv3 baselines.
- [MIT 2.680 Unmanned Marine Vehicle Autonomy, Sensing and Communications](../../catalog/resources/mit-2680-marine-autonomy.md) - course - MIT course site with lectures and hands-on labs built on MOOS-IvP, covering behaviour-based autonomy, multi-vehicle coordination, collision avoidance and marine sensing.
- [MOOS-IvP documentation wiki](../../catalog/resources/moos-ivp-docs.md) - doc - Documentation hub for MOOS-IvP with install guides, the IvP Helm manual, behaviour and app references and example missions.
- [Natural Earth vector data](../../catalog/resources/natural-earth-vectors.md) - dataset - Public-domain world vector layers (land, coastline, countries) at 1:10m, 1:50m and 1:110m scales.
- [NMEA 0183 Interface Standard](../../catalog/resources/nmea-0183-standard.md) - standard - The ASCII serial sentence standard (GGA, RMC, GSA, GSV, VTG...) used by nearly all GNSS receivers and marine electronics.
- [NMEA 2000 Standard (CAN-based marine network)](../../catalog/resources/nmea-2000-standard.md) - standard - CAN bus based marine network standard that carries position, heading, AIS and engine data as PGNs between devices.
- [OpenStreetMap data via the Overpass API](../../catalog/resources/openstreetmap-overpass-api.md) - dataset - A read-only query API over the OpenStreetMap database that returns features (coastlines, bridges, wind turbines, buoys) inside a bounding box.
- [Pohang Canal Dataset: A Multimodal Maritime Dataset for Autonomous Navigation in Restricted Waters](../../catalog/resources/pohang-canal-dataset-2023.md) - dataset - Multimodal maritime dataset from a 7.5 km route through a narrow canal, port areas and near-coast waters, with LiDARs, marine radar, stereo, infrared and omnidirectional cameras, AHRS and RTK GPS.
- [PoLaRIS Dataset: A Maritime Object Detection and Tracking Dataset in Pohang Canal](../../catalog/resources/polaris-pohang-maritime-dataset-2024.md) - dataset - Inha University dataset that adds object detection and tracking labels to five Pohang Canal sequences, with annotations on RGB, thermal, LiDAR and radar data for objects as small as 10x10 pixels.
- [R-Mode Baltic and R-Mode Baltic 2](../../catalog/resources/dlr-r-mode-baltic.md) - report - DLR project page for R-Mode Baltic, which built a Baltic Sea testbed adding ranging signals to existing maritime radio beacons and AIS base stations as a terrestrial backup to GNSS, continued by R-Mode Baltic 2 and ORMOB
- [Signal K Specification](../../catalog/resources/signalk-spec.md) - standard - Published Signal K specification describing the JSON data model, REST and streaming APIs for marine data.
- [When GNSS fails, what will you do? MarRINav!](../../catalog/resources/ion-webinar-marrinav.md) - talk - UK maritime resilient navigation study (MarRINav) on backups for GNSS at sea, including eLoran and R-Mode style terrestrial systems; co-sponsored by the RNT Foundation.
- [Who cares about the Baltic Jammer? Terrestrial Navigation in the Baltic Sea Region (39C3)](../../catalog/resources/39c3-baltic-jammer-r-mode.md) - talk - 39th Chaos Communication Congress talk from DLR researchers on R-Mode, a terrestrial maritime navigation backup built on existing radio beacons and coastal infrastructure, tested in the heavily jammed Baltic.

