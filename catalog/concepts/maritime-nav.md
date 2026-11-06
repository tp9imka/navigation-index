# Maritime navigation

`concept:maritime-nav`

Surface vessel navigation, AIS, ECDIS/charts, USVs.

## Repositories (19)

- [ArduPilot](../repos/ardupilot__ardupilot.md) - fit: high - GPL autopilot covering Copter, Plane (incl.
- [OpenCPN](../repos/opencpn__opencpn.md) - fit: high - Cross-platform open-source chartplotter and navigation application that displays raster and S-57 vector charts, ingests GPS and AIS feeds, and runs waypoint routes.
- [AIS-catcher](../repos/jvde-github__ais-catcher.md) - fit: high - AIS receiver and decoder for cheap SDRs (RTL-SDR, Airspy, HackRF, SDRplay, SoapySDR) with a built-in web map, JSON/NMEA output and feed sharing.
- [Virtual RobotX (VRX)](../repos/osrf__vrx.md) - fit: high - Gazebo-based simulation environment for the RobotX maritime autonomy competition, with a WAM-V USV model, waves, wind, sensors and scored tasks such as station keeping, wayfinding and perception.
- [BlueOS](../repos/bluerobotics__blueos.md) - fit: high - Blue Robotics' onboard software platform for ROVs and USVs: web UI, ArduPilot management, MAVLink routing and a Docker extension system on a Raspberry Pi companion computer.
- [Signal K Server](../repos/signalk__signalk-server.md) - fit: high - Node.js server implementing the Signal K open marine data standard: it ingests NMEA 0183, NMEA 2000 and other boat buses and republishes everything as a JSON data model over REST and WebSocket, with a plugin ecosystem.
- [Stonefish](../repos/patrykcieslak__stonefish.md) - fit: high - C++ simulation library for marine robotics with hydrodynamics, underwater rendering and sensors including DVL, USBL, multibeam and forward-looking sonar; has a ROS wrapper.
- [pyais](../repos/m0r13n__pyais.md) - fit: high - Python library for decoding and encoding AIS NMEA sentences (AIVDM/AIVDO), including multi-part messages and streaming from sockets or files.
- [MOOS-IvP](../repos/moos-ivp__moos-ivp.md) - fit: high - Long-running autonomy middleware (MOOS) plus the IvP Helm behaviour-based multi-objective decision engine, used widely for autonomous marine vehicles, including COLREGs-aware collision avoidance behaviours.
- [NTNU colav-simulator](../repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) - fit: high - Python framework from the NTNU Autoship centre for simulating and evaluating autonomous ship collision avoidance controllers, open-sourced in autumn 2025, with scenario generation and evaluation tooling.
- [OpenCPN radar_pi](../repos/opencpn-radar-pi__radar_pi.md) - fit: medium - OpenCPN plugin that connects to Navico and some Garmin and Raymarine marine radars and overlays radar imagery and ARPA-style targets on the chart.
- [Signal K Specification](../repos/signalk__specification.md) - fit: medium - The JSON schema and specification for the Signal K marine data format covering navigation, environment, propulsion and other vessel data paths.
- [celestial-navigation toolkit](../repos/alinnman__celestial-navigation.md) - fit: medium - Python toolkit for classic celestial navigation sight reduction, usable offline on a phone.
- [signalk-to-nmea0183](../repos/signalk__signalk-to-nmea0183.md) - fit: medium - Signal K server plugin that converts Signal K data back into NMEA 0183 sentences for legacy displays and autopilots.
- [MOOS-IvP COLREGs master's research code](../repos/d2snc__moos-ivp-masters.md) - fit: medium - MOOS-IvP applications from a 2025 master's project at Universidade de Sao Paulo implementing COLREGs-compliant collision avoidance for USVs, including a modified A* planner, a velocity-obstacle method and a virtual-conta
- [VIMMJIPDA tracker interface](../repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md) - fit: medium - Interface that runs the VIMMJIPDA multi-target tracker (visibility, interacting multiple models, JIPDA) inside the NTNU colav-simulator; open-sourced November 2025.
- [pyMHT](../repos/erikliland__pymht.md) - fit: low - Track-oriented multi-hypothesis multi-target tracker in Python developed for maritime radar tracking research.
- [Aeolus Ocean](../repos/aavek__aeolus-ocean.md) - fit: low - Collision avoidance simulator for COLREG-compliant autonomous ship navigation intended for use as a digital twin under varied weather and day/night conditions.
- [noaadata](../repos/schwehr__noaadata.md) - fit: low - Pure-Python AIS decode and encode library from a long-time AIS researcher, with message definitions and utilities for working with NOAA and coastal AIS data.

## Documents, talks, courses, datasets (12)

- [Above Us Only Stars: Exposing GPS Spoofing in Russia and Syria](../resources/c4ads-above-us-only-stars.md) - report - Open-source investigation using AIS ship tracks, public records and ISS-based measurements to map thousands of GNSS spoofing events around Russia, Crimea and Syria, many linked to protection of VIPs and bases.
- [COLREGs - Convention on the International Regulations for Preventing Collisions at Sea, 1972](../resources/imo-colregs.md) - standard - IMO page for the collision regulations that define give-way and stand-on duties, lights and signals; the rule set autonomous surface vessels must encode.
- [ERF26 workshop: Innovation and developments in robotic GNSS-denied localisation for inspection & maintenance](../resources/erf26-sintef-gnss-denied-localisation-workshop.md) - talk - European Robotics Forum 2026 workshop (Stavanger) organised by SINTEF on GNSS-denied robot localisation in indoor, offshore, underground and urban-canyon settings, bringing together researchers, vendors and end users.
- [ITU-R M.1371 - Technical characteristics for an automatic identification system using TDMA in the VHF maritime mobile band](../resources/itu-r-m1371-ais.md) - standard - The ITU recommendation defining AIS radio, TDMA access and message formats that decoders such as pyais implement.
- [MIT 2.680 Unmanned Marine Vehicle Autonomy, Sensing and Communications](../resources/mit-2680-marine-autonomy.md) - course - MIT course site with lectures and hands-on labs built on MOOS-IvP, covering behaviour-based autonomy, multi-vehicle coordination, collision avoidance and marine sensing.
- [MOOS-IvP documentation wiki](../resources/moos-ivp-docs.md) - doc - Documentation hub for MOOS-IvP with install guides, the IvP Helm manual, behaviour and app references and example missions.
- [NMEA 0183 Interface Standard](../resources/nmea-0183-standard.md) - standard - The ASCII serial sentence standard (GGA, RMC, GSA, GSV, VTG...) used by nearly all GNSS receivers and marine electronics.
- [NMEA 2000 Standard (CAN-based marine network)](../resources/nmea-2000-standard.md) - standard - CAN bus based marine network standard that carries position, heading, AIS and engine data as PGNs between devices.
- [Signal K Specification](../resources/signalk-spec.md) - standard - Published Signal K specification describing the JSON data model, REST and streaming APIs for marine data.
- [When GNSS fails, what will you do? MarRINav!](../resources/ion-webinar-marrinav.md) - talk - UK maritime resilient navigation study (MarRINav) on backups for GNSS at sea, including eLoran and R-Mode style terrestrial systems; co-sponsored by the RNT Foundation.
- [Who cares about the Baltic Jammer? Terrestrial Navigation in the Baltic Sea Region (39C3)](../resources/39c3-baltic-jammer-r-mode.md) - talk - 39th Chaos Communication Congress talk from DLR researchers on R-Mode, a terrestrial maritime navigation backup built on existing radio beacons and coastal infrastructure, tested in the heavily jammed Baltic.
- [Windward - 2025 maritime stress test](../resources/windward-2025-maritime-stress-test.md) - blog - Maritime-intelligence review of 2025 including large-scale GNSS jamming and spoofing in the Gulf and Strait of Hormuz after the June 2025 Israel-Iran strikes.

