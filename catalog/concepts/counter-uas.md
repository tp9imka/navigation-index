# Counter-UAS and drone detection

`concept:counter-uas`

Detecting, tracking and identifying drones (Remote ID, RF, radar, vision) - defensive.

## Samples (1)

- [Stone Soup radar tracking of two UAVs with JPDA and OSPA](../samples/stone-soup-tracking.md) - Simulates two small UAVs observed by a noisy bearing/range radar with clutter and tracks them with Stone Soup's Extended Kalman filter and JPDA data association.

## Repositories (27)

- [Ultralytics YOLO](../repos/ultralytics__ultralytics.md) - fit: high - Widely used Python package for YOLO-family detection, segmentation and tracking with training, export to edge runtimes and built-in trackers.
- [Anti-UAV](../repos/zhaoj9014__anti-uav.md) - fit: high - Official repository of the Anti-UAV challenge and benchmark for detecting and tracking UAVs in RGB and thermal infrared video, with dataset links (Anti-UAV300/410/600) and baselines.
- [readsb](../repos/wiedehopf__readsb.md) - fit: high - ADS-B/Mode S decoder for RTL-SDR and other receivers with networking, JSON output, MLAT support and aggregation features.
- [Stone Soup](../repos/dstl__stone-soup.md) - fit: high - Open-source Python framework from UK Dstl and partners for developing, running and evaluating tracking and state estimation algorithms: Kalman variants, particle filters, JPDA, MHT, GM-PHD, track management and metrics.
- [OpenDroneID Android receiver](../repos/opendroneid__receiver-android.md) - fit: high - Example Android app that listens for Remote ID broadcasts over Bluetooth 4/5 and Wi-Fi Beacon/NaN and shows drones and operators on a map.
- [Open Drone ID Core C](../repos/opendroneid__opendroneid-core-c.md) - fit: high - Reference C library for encoding and decoding ASTM F3411 / ASD-STAN Remote ID messages (location, operator, system, auth) for Bluetooth and Wi-Fi broadcast.
- [KrakenSDR DoA DSP](../repos/krakenrf__krakensdr_doa.md) - fit: high - Direction-of-arrival processing and web UI for the five-channel coherent KrakenSDR, producing bearings to RF emitters.
- [ArduRemoteID](../repos/ardupilot__arduremoteid.md) - fit: high - ESP32-based Remote ID transmitter firmware implementing ASTM F3411 broadcast (Bluetooth and Wi-Fi) fed from MAVLink or DroneCAN.
- [drone-mesh-mapper](../repos/colonelpanichacks__drone-mesh-mapper.md) - fit: high - ESP32 firmware and tools that sniff Wi-Fi Remote ID and relay detections over Meshtastic LoRa mesh to a mapping host.
- [DragonSync](../repos/alphafox02__dragonsync.md) - fit: high - Gateway that takes drone Remote ID / DroneID detections from WarDragon-style sensors and publishes them as CoT to TAK and other outputs.
- [RID (ESP32 Remote ID receiver)](../repos/peterjburke__rid.md) - fit: high - ESP32 Remote ID receiver built on opendroneid-core-c and a fork of sxjack's electronic ID classes.
- [ADSBCOT](../repos/snstac__adsbcot.md) - fit: high - Gateway that converts ADS-B traffic from dump1090/readsb or aggregator APIs into Cursor-on-Target so aircraft show in TAK.
- [ExpressLRS](../repos/expresslrs__expresslrs.md) - fit: medium - Open-source LoRa/FLRC radio control link (2.4 GHz and sub-GHz) with high packet rates, telemetry and MAVLink passthrough modes.
- [DroneSecurity (DJI DroneID receiver)](../repos/rub-syssec__dronesecurity.md) - fit: medium - Ruhr University Bochum receiver for DJI DroneID that works live with an SDR or offline on captures, released with their NDSS 2023 security analysis.
- [VolAnti](../repos/agamrossen__volanti.md) - fit: medium - Open-source acoustic drone detector that listens for propeller noise; explicitly detection and alerting only.
- [RFUAV](../repos/kitoweeknd__rfuav.md) - fit: medium - Code for the RFUAV benchmark dataset for UAV detection and identification from RF signals, using a two-stage STFT spectrogram detection and classification model.
- [Batear](../repos/batear-io__batear.md) - fit: medium - Low-cost edge-only acoustic drone detector on ESP32-S3 with encrypted LoRa or Ethernet alerting.
- [UAV Detection and Tracking Benchmark](../repos/kostadinovshalon__uavdetectiontrackingbenchmark.md) - fit: medium - Code and configs for benchmarking drone detection and tracking across Anti-UAV, Drone-vs-Bird and MAV-VID datasets, including format converters.
- [uav_electronic_ids](../repos/sxjack__uav_electronic_ids.md) - fit: medium - Arduino classes for several UAV electronic ID formats (ASTM/EU Remote ID, French ID) and UTM interfaces, with ESP32 examples.
- [Open Drone ID Wireshark dissector](../repos/opendroneid__wireshark-dissector.md) - fit: medium - Lua Wireshark dissector that decodes Remote ID broadcast frames over Wi-Fi and Bluetooth.
- [OpenDroneID Linux transmitter](../repos/opendroneid__transmitter-linux.md) - fit: medium - Example Linux transmitter for Remote ID over Bluetooth and Wi-Fi.
- [WarDragon docs](../repos/alphafox02__wardragon.md) - fit: medium - Documentation hub for WarDragon, an SDR-based RF sensing appliance for drone detection; open components are documented here, while commercial kits add closed features.
- [samples2djidroneid](../repos/anarkiwi__samples2djidroneid.md) - fit: medium - Decodes DJI DroneID (OcuSync 2.0) frames from SDR I/Q recordings, building on proto17's reverse engineering and Kismet.
- [WarDragon FPV energy scan](../repos/alphafox02__wardragon-fpv-detect.md) - fit: medium - GNU Radio based scanner that checks known analog FPV video frequencies for energy and publishes alerts over ZMQ; the optional confirmation detector is closed source.
- [Betaflight](../repos/betaflight__betaflight.md) - fit: low - Racing/freestyle-oriented flight controller firmware focused on attitude control and low-latency filtering; GPS rescue mode is its main navigation feature.
- [dji_droneid](../repos/proto17__dji_droneid.md) - fit: low - Original reverse engineering of DJI DroneID with MATLAB scripts and a GNU Radio module to demodulate frames.
- [DroneRF](../repos/al-sad__dronerf.md) - fit: low - MATLAB and Python code for drone detection and identification from RF signals, accompanying the DroneRF dataset.

## Documents, talks, courses, datasets (15)

- [Anti-UAV Challenge](../resources/anti-uav-challenge-site.md) - competition - Site for the recurring Anti-UAV workshop and challenge with tracks for single and multiple UAV tracking in infrared video.
- [Anti-UAV: A Large Multi-Modal Benchmark for UAV Tracking](../resources/anti-uav-benchmark-paper.md) - paper - Introduces the Anti-UAV RGB and thermal infrared video benchmark for UAV tracking and an evaluation protocol.
- [Drone Security and the Mysterious Case of DJI's DroneID](../resources/ndss-2023-dji-droneid.md) - paper - Reverse-engineers DJI's DroneID broadcast, shows it is unencrypted, and builds an SDR receiver that decodes drone and pilot positions.
- [Drone Security and the Mysterious Case of DJI's DroneID](../resources/ndss2023-dji-droneid.md) - paper - Security analysis of DJI drones that reverse-engineers the DroneID broadcast and shows it is unencrypted, with an open receiver released.
- [EUDIS Defence Hackathon, 3rd edition (with BraveTech EU)](../resources/eudis-defence-hackathon-2025.md) - competition - EU defence hackathon (17-19 October 2025, eight locations) with challenges on protecting space assets, space for defence (including navigation and coordination) and sovereign aerospace including drone countermeasures; a 
- [FAA - Remote Identification of Drones](../resources/faa-remote-id.md) - doc - FAA guidance on the Remote ID rule: what drones must broadcast, standard vs broadcast-module compliance and operator obligations.
- [Meatgrinder: Russian Tactics in the Second Year of Its Invasion of Ukraine](../resources/rusi-meatgrinder-2023.md) - report - RUSI special report on Russian battlefield adaptation, including the density of Russian electronic warfare and its heavy effect on Ukrainian UAVs, with a widely cited estimate of around 10,000 drone losses per month.
- [Multi-Object Tracking for Automotive Systems (edX)](../resources/chalmers-multi-object-tracking.md) - course - edX course on single- and multi-object tracking: data association, GNN/JPDA/MHT, random finite sets and PMBM filters, with Matlab assignments.
- [Open Drone ID (MAVLink microservice)](../resources/mavlink-opendroneid-microservice.md) - doc - Defines the MAVLink messages and flow for Remote ID between flight controller, GCS and transponder.
- [Preliminary Lessons in Conventional Warfighting from Russia's Invasion of Ukraine: February-July 2022](../resources/rusi-preliminary-lessons-ukraine-2022.md) - report - RUSI analysis of the first months of the war, including the scale of Russian electronic warfare and its effect on Ukrainian UAV survival and GNSS-dependent systems.
- [Remote ID (ArduPilot)](../resources/ardupilot-remote-id-docs.md) - doc - ArduPilot wiki page on Remote ID modules, including ArduRemoteID setup and compliance notes.
- [Remote ID (Open Drone ID) in PX4](../resources/px4-remote-id-docs.md) - doc - PX4 documentation for connecting Remote ID modules over MAVLink or DroneCAN and related failsafe behaviour.
- [Stone Soup documentation and tutorials](../resources/dstl-stone-soup-docs.md) - doc - Official docs for the Stone Soup tracking framework with step-by-step tutorials from a single-target Kalman filter through data association (PDA, JPDA), multi-hypothesis tracking, GM-PHD, track initiation/deletion, senso
- [Ukraine's Brave1, NATO launch EUR 10M competition for counter-drone technology](../resources/brave1-nato-counter-drone-ew-competition.md) - blog - Coverage of a Brave1-NATO competition funding counter-drone technology and navigation that works under electronic warfare.
- [В Україні провели хакатон зі створення антидронових рішень (Anti-drone hackathon held in Ukraine)](../resources/militarnyi-anti-drone-hackathon-ukraine.md) - blog - Ukrainian-language report on a defense hackathon focused on counter-drone solutions.

