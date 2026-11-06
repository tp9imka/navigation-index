# Situational awareness and C2 interop

`concept:situational-awareness`

TAK/CoT, MIL-STD-2525/APP-6 symbology, blue force tracking, common operating picture.

## Samples (3)

- [GNSS interference monitor from u-blox telemetry and ADS-B NACp](../samples/gnss-interference-monitor.md) - A stdlib heuristic scorer turns per-epoch receiver telemetry (C/N0 across SVs, AGC, CW jamming indicator, clock and position jumps, receiver spoofing/jamming flags) into jamming and spoofing scores with stated reasons.
- [MAVLink telemetry to TAK Cursor-on-Target](../samples/mavlink-to-tak-cot.md) - Bridges autopilot GLOBAL_POSITION_INT messages into Cursor-on-Target events so a UAV shows up as a friendly track on ATAK, WinTAK or iTAK.
- [Stone Soup radar tracking of two UAVs with JPDA and OSPA](../samples/stone-soup-tracking.md) - Simulates two small UAVs observed by a noisy bearing/range radar with clutter and tracks them with Stone Soup's Extended Kalman filter and JPDA data association.

## Repositories (51)

- [Leaflet](../repos/leaflet__leaflet.md) - fit: high - Small, simple JavaScript library for interactive raster/vector maps with a huge plugin ecosystem.
- [CesiumJS](../repos/cesiumgs__cesium.md) - fit: high - WebGL 3D globe and map library with terrain, 3D Tiles, time-dynamic data (CZML) and accurate WGS84 rendering.
- [deck.gl](../repos/visgl__deck.gl.md) - fit: high - GPU-powered large-scale data visualization framework with layers for points, paths, trips, hexbins and 3D tiles, usable over MapLibre or standalone.
- [MapLibre GL JS](../repos/maplibre__maplibre-gl-js.md) - fit: high - Open-source WebGL vector tile map renderer (fork of Mapbox GL JS v1) with styles, 3D terrain and globe view.
- [QGroundControl](../repos/mavlink__qgroundcontrol.md) - fit: high - Qt/QML cross-platform GCS (desktop, Android, iOS) for PX4 and ArduPilot: setup, mission planning, video and telemetry.
- [Martin](../repos/maplibre__martin.md) - fit: high - Fast Rust tile server for PostGIS, MBTiles and PMTiles sources, with tile generation and mbtiles tooling.
- [OpenCPN](../repos/opencpn__opencpn.md) - fit: high - Cross-platform open-source chartplotter and navigation application that displays raster and S-57 vector charts, ingests GPS and AIS feeds, and runs waypoint routes.
- [milsymbol](../repos/spatialillusions__milsymbol.md) - fit: high - Pure JavaScript library generating MIL-STD-2525 (B/C/D/E) and APP-6 (B/D/E) military symbols as SVG or canvas.
- [AIS-catcher](../repos/jvde-github__ais-catcher.md) - fit: high - AIS receiver and decoder for cheap SDRs (RTL-SDR, Airspy, HackRF, SDRplay, SoapySDR) with a built-in web map, JSON/NMEA output and feed sharing.
- [readsb](../repos/wiedehopf__readsb.md) - fit: high - ADS-B/Mode S decoder for RTL-SDR and other receivers with networking, JSON output, MLAT support and aggregation features.
- [Stone Soup](../repos/dstl__stone-soup.md) - fit: high - Open-source Python framework from UK Dstl and partners for developing, running and evaluating tracking and state estimation algorithms: Kalman variants, particle filters, JPDA, MHT, GM-PHD, track management and metrics.
- [pyModeS](../repos/junzis__pymodes.md) - fit: high - Python decoder for Mode S and ADS-B messages including Comm-B / EHS fields, with live streaming tools.
- [OpenSky API clients](../repos/openskynetwork__opensky-api.md) - fit: high - Python and Java bindings for the OpenSky Network REST API for live and recent aircraft states.
- [Signal K Server](../repos/signalk__signalk-server.md) - fit: high - Node.js server implementing the Signal K open marine data standard: it ingests NMEA 0183, NMEA 2000 and other boat buses and republishes everything as a JSON data model over REST and WebSocket, with a plugin ecosystem.
- [OpenTAKServer](../repos/brian7704__opentakserver.md) - fit: high - Actively developed open-source TAK server for ATAK, iTAK and WinTAK with web UI, video streaming integration, Meshtastic support and certificate enrollment.
- [OpenDroneID Android receiver](../repos/opendroneid__receiver-android.md) - fit: high - Example Android app that listens for Remote ID broadcasts over Bluetooth 4/5 and Wi-Fi Beacon/NaN and shows drones and operators on a map.
- [Open Drone ID Core C](../repos/opendroneid__opendroneid-core-c.md) - fit: high - Reference C library for encoding and decoding ASTM F3411 / ASD-STAN Remote ID messages (location, operator, system, auth) for Bluetooth and Wi-Fi broadcast.
- [pyais](../repos/m0r13n__pyais.md) - fit: high - Python library for decoding and encoding AIS NMEA sentences (AIVDM/AIVDO), including multi-part messages and streaming from sockets or files.
- [ArduRemoteID](../repos/ardupilot__arduremoteid.md) - fit: high - ESP32-based Remote ID transmitter firmware implementing ASTM F3411 broadcast (Bluetooth and Wi-Fi) fed from MAVLink or DroneCAN.
- [PyTAK](../repos/snstac__pytak.md) - fit: high - Python asyncio package for TAK integration: CoT send/receive over TCP, UDP, TLS and multicast, with helpers for building events.
- [drone-mesh-mapper](../repos/colonelpanichacks__drone-mesh-mapper.md) - fit: high - ESP32 firmware and tools that sniff Wi-Fi Remote ID and relay detections over Meshtastic LoRa mesh to a mapping host.
- [GoATAK](../repos/kdudkov__goatak.md) - fit: high - Go implementation of a simple ATAK-compatible server and a web client, supporting CoT over TCP/UDP/SSL.
- [DragonSync](../repos/alphafox02__dragonsync.md) - fit: high - Gateway that takes drone Remote ID / DroneID detections from WarDragon-style sensors and publishes them as CoT to TAK and other outputs.
- [RID (ESP32 Remote ID receiver)](../repos/peterjburke__rid.md) - fit: high - ESP32 Remote ID receiver built on opendroneid-core-c and a fork of sxjack's electronic ID classes.
- [node-CoT](../repos/dfpc-coe__node-cot.md) - fit: high - JavaScript/TypeScript library for parsing, building and converting Cursor-on-Target messages, including GeoJSON conversion and TAK protobuf.
- [mil-sym-ts](../repos/missioncommand__mil-sym-ts.md) - fit: high - TypeScript/JavaScript renderer for MIL-STD-2525 (D and later) military symbology, producing single-point and multi-point tactical graphics for web maps.
- [ADSBCOT](../repos/snstac__adsbcot.md) - fit: high - Gateway that converts ADS-B traffic from dump1090/readsb or aggregator APIs into Cursor-on-Target so aircraft show in TAK.
- [OpenLayers](../repos/openlayers__openlayers.md) - fit: medium - Feature-rich web mapping library supporting many projections, WMS/WMTS, vector tiles and editing.
- [Gqrx](../repos/gqrx-sdr__gqrx.md) - fit: medium - Desktop SDR receiver built on GNU Radio and Qt with FFT/waterfall and demodulators.
- [OpenHD](../repos/openhd__openhd.md) - fit: medium - Open-source long-range digital HD video and telemetry link over Wi-Fi adapters in monitor mode (wifibroadcast-style), for air and ground units.
- [tar1090](../repos/wiedehopf__tar1090.md) - fit: medium - Improved web interface for readsb/dump1090 with track history, filtering and overlays.
- [WFB-ng](../repos/svpcom__wfb-ng.md) - fit: medium - Long-range packet radio link over raw Wi-Fi injection with FEC, carrying video, MAVLink and IP tunnels.
- [OpenWebRX](../repos/jketterl__openwebrx.md) - fit: medium - Multi-user web SDR receiver with waterfall display and many built-in digital decoders.
- [DroneSecurity (DJI DroneID receiver)](../repos/rub-syssec__dronesecurity.md) - fit: medium - Ruhr University Bochum receiver for DJI DroneID that works live with an SDR or offline on captures, released with their NDSS 2023 security analysis.
- [dump1090-fa](../repos/flightaware__dump1090.md) - fit: medium - FlightAware's maintained Mode S/ADS-B decoder for RTL-SDR dongles.
- [ConceptGraphs](../repos/concept-graphs__concept-graphs.md) - fit: medium - Builds open-vocabulary 3D scene graphs from RGB-D by associating 2D foundation-model detections across views, then lets an LLM plan over the graph.
- [FreeTAKServer](../repos/freetakteam__freetakserver.md) - fit: medium - Open-source Python server compatible with TAK clients (ATAK, WinTAK, iTAK) that relays Cursor-on-Target positions, chat and data packages.
- [TAK Server (open source)](../repos/tak-product-center__server.md) - fit: medium - Open-source release of the TAK Server from the TAK Product Center: the federation and message routing server for ATAK/WinTAK/iTAK clients, handling CoT, data packages, missions and video.
- [OpenWebRX+](../repos/luarvique__openwebrx.md) - fit: medium - Actively developed fork of OpenWebRX adding decoders, bookmarks and packaging improvements.
- [traffic](../repos/xoolive__traffic.md) - fit: medium - Toolbox for processing and analyzing air traffic trajectories: OpenSky access, filtering, resampling, airspace intersection and visualization.
- [ATAK-CIV (DoD release, archived)](../repos/deptofdefense__androidtacticalassaultkit-civ.md) - fit: medium - The DoD's public source release of the civilian Android Team Awareness Kit: map engine, Cursor-on-Target messaging and plugin SDK.
- [ATAK-CIV (TAK Product Center)](../repos/tak-product-center__atak-civ.md) - fit: medium - Source of the civilian Android Team Awareness Kit maintained by the TAK Product Center: map client, plugin SDK and CoT handling.
- [galmon](../repos/berthubert__galmon.md) - fit: medium - Open-source GNSS monitoring network and software that collects navigation data from volunteer receivers worldwide and publishes live health, ephemeris and timing statistics for Galileo, GPS, BeiDou and GLONASS.
- [ASTERIX decoder (Croatia Control)](../repos/croatiacontrolltd__asterix.md) - fit: medium - C/C++ and Python decoder for EUROCONTROL ASTERIX surveillance data from files, stdin or network, with XML category definitions and JSON/XML output.
- [CloudTAK](../repos/dfpc-coe__cloudtak.md) - fit: medium - Browser-based TAK-compatible common operating picture with ETL connectors that push external data feeds into TAK.
- [WarDragon docs](../repos/alphafox02__wardragon.md) - fit: medium - Documentation hub for WarDragon, an SDR-based RF sensing appliance for drone detection; open components are documented here, while commercial kits add closed features.
- [asterix-specs](../repos/zoranbosnjak__asterix-specs.md) - fit: medium - EUROCONTROL ASTERIX category specifications in a structured machine-readable format, with generated JSON and docs.
- [takproto](../repos/snstac__takproto.md) - fit: medium - Encode and decode TAK protobuf (TAK Protocol v1) packets, including mesh and stream formats.
- [cotlib (Go)](../repos/nervsystems__cotlib.md) - fit: medium - Go library for parsing, validating and generating Cursor-on-Target XML with security-focused input limits and optional schema validation.
- [MonoGS (Gaussian Splatting SLAM)](../repos/muskie82__monogs.md) - fit: low - Gaussian-splatting SLAM for monocular, stereo and RGB-D cameras that tracks and maps directly against a 3D Gaussian representation.
- [Joint Military Symbology XML](../repos/esri__joint-military-symbology-xml.md) - fit: low - Esri data encapsulation of MIL-STD-2525D and APP-6(D) symbology: symbol IDs, entity tables and SVG assets.

## Documents, talks, courses, datasets (29)

- [Above Us Only Stars: Exposing GPS Spoofing in Russia and Syria](../resources/c4ads-above-us-only-stars.md) - report - Open-source investigation using AIS ship tracks, public records and ISS-based measurements to map thousands of GNSS spoofing events around Russia, Crimea and Syria, many linked to protection of VIPs and bases.
- [ADS-B Data Analysis for GNSS Interference Mapping](../resources/insidegnss-adsb-interference-mapping.md) - blog - Trade-press article on using ADS-B integrity data to detect and map GNSS interference regions.
- [Bellingcat OSINT Toolkit - GPSJam](../resources/bellingcat-toolkit-gpsjam.md) - doc - Bellingcat's toolkit entry on using GPSJam for open-source investigations, with notes on limitations and interpretation.
- [ConceptGraphs: Open-Vocabulary 3D Scene Graphs for Perception and Planning](../resources/conceptgraphs-2023.md) - paper - Builds object-centric 3D scene graphs with open-vocabulary labels from RGB-D and uses an LLM to plan over them.
- [cot-types: Collection of Cursor-on-Target types](../resources/cot-types-collection.md) - dataset - Community-compiled list of CoT type strings with mappings to other message formats, useful when choosing the 'type' attribute for tracks.
- [Cursor on Target (NDIA briefing)](../resources/cot-niessen-ndia-2008.md) - talk - Briefing introducing the Cursor on Target XML event schema: the minimal event/point/detail model for exchanging what-when-where of tracked entities between C2 systems.
- [Cursor-on-Target Message Router User's Guide](../resources/mitre-cot-users-guide.md) - doc - MITRE guide describing Cursor-on-Target: the base Event schema (what, where, when), its mandatory fields, sub-schema extensions and the message router used to distribute CoT.
- [DARPA Triage Challenge](../resources/darpa-triage-challenge.md) - competition - DARPA challenge for autonomous systems that find and assess casualties in mass-casualty scenes, combining drones and ground robots navigating degraded, GNSS-unreliable environments.
- [Detect GNSS jamming and spoofing (Android developer guide)](../resources/android-gnss-spoof-jam-detection.md) - doc - Android developer documentation on the platform APIs and signals that apps can use to detect GNSS jamming and spoofing on phones.
- [Developer's Guide to Cursor on Target](../resources/butler-cot-developer-guide.md) - doc - Introductory developer guide to CoT's objectives, message structure, implementation patterns and limitations.
- [EDF 2021 NAVGUARD project factsheet](../resources/edf21-navguard-factsheet.md) - doc - Factsheet for an EDF-funded project developing ground and space-based detection of illegitimate activity in GNSS bands.
- [EUDIS Defence Hackathon, 3rd edition (with BraveTech EU)](../resources/eudis-defence-hackathon-2025.md) - competition - EU defence hackathon (17-19 October 2025, eight locations) with challenges on protecting space assets, space for defence (including navigation and coordination) and sovereign aerospace including drone countermeasures; a 
- [EUROCONTROL ASTERIX](../resources/eurocontrol-asterix.md) - standard - EUROCONTROL home of the ASTERIX surveillance data exchange format, with category specifications for radar, ADS-B, MLAT and system tracks.
- [FAA - Remote Identification of Drones](../resources/faa-remote-id.md) - doc - FAA guidance on the Remote ID rule: what drones must broadcast, standard vs broadcast-module compliance and operator obligations.
- [Flightradar24 GPS jamming map](../resources/fr24-gps-jamming-map.md) - dataset - Flightradar24's map of GNSS interference, computed from navigation integrity category values broadcast by aircraft over its receiver network.
- [GNSS interference report: Russia 2024/2025 - Part 1: Kaliningrad and the Baltic Sea](../resources/spire-gnss-interference-russia-kaliningrad.md) - report - Spire analysis using satellite-received ADS-B integrity metrics and RF data to characterize persistent interference around Kaliningrad and over the Baltic.
- [GPSJam - daily GPS interference map](../resources/gpsjam-org.md) - dataset - Daily world map of likely GPS interference derived from ADS-B navigation-integrity reports (NIC/NACp) aggregated into hexagons from community flight-tracking data.
- [ITU-R M.1371 - Technical characteristics for an automatic identification system using TDMA in the VHF maritime mobile band](../resources/itu-r-m1371-ais.md) - standard - The ITU recommendation defining AIS radio, TDMA access and message formats that decoders such as pyais implement.
- [Kimera: an Open-Source Library for Real-Time Metric-Semantic Localization and Mapping](../resources/kimera-rosinol-2019.md) - paper - Describes the Kimera stack: VIO, robust pose-graph optimization, mesh reconstruction and semantic mapping in one open library.
- [MIL-STD-2525 Joint Military Symbology - overview](../resources/mil-std-2525-overview.md) - doc - Summary of the US military symbology standard and its revisions (2525B through E), including the SIDC code formats that symbol renderers and CoT type strings map onto.
- [MIL-STD-2525D Joint Military Symbology](../resources/mil-std-2525d.md) - standard - US DoD standard defining military symbology (frames, icons, modifiers and the symbol identification code) for C2 displays.
- [Multi-Object Tracking for Automotive Systems (edX)](../resources/chalmers-multi-object-tracking.md) - course - edX course on single- and multi-object tracking: data association, GNN/JPDA/MHT, random finite sets and PMBM filters, with Matlab assignments.
- [NATO Joint Military Symbology (APP-6) - overview](../resources/app-6-joint-military-symbology.md) - doc - Overview of APP-6, the NATO standard for map symbols of units, equipment and tactical graphics, now at edition E and aligned with the US MIL-STD-2525 family.
- [OpenTAKServer Documentation](../resources/opentakserver-docs.md) - doc - Installation and configuration docs for OpenTAKServer, including client enrollment, certificates and integrations.
- [PyTAK documentation](../resources/pytak-docs.md) - doc - Docs and examples for PyTAK: configuration, transports (TCP/UDP/TLS/multicast) and writing CoT producers.
- [TAK Protocol (takproto) - protobuf encoding of CoT](../resources/tak-protocol-takproto.md) - doc - Documentation of the TAK protocol used by ATAK and TAK Server: how CoT events are framed and carried as protocol buffers over mesh (UDP multicast) and streaming (TCP/TLS) transports, alongside legacy XML.
- [TAK.gov - Team Awareness Kit portal](../resources/tak-gov.md) - doc - Official TAK portal for ATAK/WinTAK/iTAK/TAK Server downloads, plugin SDKs and documentation; most materials require free registration.
- [The 1090 Megahertz Riddle: A Guide to Decoding Mode S and ADS-B Signals](../resources/junzis-1090mhz-riddle.md) - book - Open book explaining Mode S and ADS-B message structure, position decoding (CPR), Comm-B registers and Mode S surveillance, with pyModeS examples.
- [Windward - 2025 maritime stress test](../resources/windward-2025-maritime-stress-test.md) - blog - Maritime-intelligence review of 2025 including large-scale GNSS jamming and spoofing in the Gulf and Strait of Hormuz after the June 2025 Israel-Iran strikes.

