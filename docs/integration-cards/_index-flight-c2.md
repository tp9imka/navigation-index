# Integration cards - flight stack, C2 and situational awareness

<!-- about: repo:ardupilot/ardupilot, repo:px4/px4-autopilot, repo:mavlink/mavsdk-python, repo:ardupilot/pymavlink, repo:mavlink/mavros, repo:mavlink-router/mavlink-router, repo:mavlink/qgroundcontrol, repo:ardupilot/mavproxy, repo:thien94/vision_to_mavros, repo:auterion/px4-ros2-interface-lib, repo:px4/px4_ros_com, repo:snstac/pytak, repo:brian7704/opentakserver, repo:spatialillusions/milsymbol, repo:kdudkov/goatak, repo:ardupilot/arduremoteid, repo:opendroneid/receiver-android, repo:wiedehopf/readsb, repo:dstl/stone-soup, repo:krakenrf/krakensdr_doa, repo:ion-g-ion/mavlinkmcp, repo:robotmcp/ros-mcp-server, repo:nasa-jpl/rosa -->

What each card gives you in a hackathon. All 23 were written from READMEs, docs, source files and issues read through the GitHub API (plus PyPI metadata where noted). None of these repos was installed or run for the cards, and every snippet is marked "not run". Version-sensitive names (ArduPilot SITL params, PX4 SIH target and aux-global-position params) were checked against both the default branch and the latest stable tag, and the cards say which is which.

## Autopilots and simulation

- [ArduPilot](ardupilot__ardupilot.md) - EKF3 source sets (`EK3_SRCn_*`) switchable from RC, MAVLink or Lua. Includes a SITL ExternalNav recipe taken from the autotest suite, and SITL GPS disable/jam/glitch params (`SIM_GPS1_*` on master, `SIM_GPS_*` on 4.6).
- [PX4](px4__px4-autopilot.md) - EKF2 aiding bitmasks (`EKF2_GPS_CTRL`, `EKF2_EV_CTRL`, aux global position `EKF2_AGP*`) and SIH. `failure gps off|stuck|wrong` sets up a GNSS-loss scenario. v1.17.0 and `main` differ in the target and param names.

## MAVLink tooling and GCS

- [MAVSDK-Python](mavlink__mavsdk-python.md) - asyncio scripting for PX4. The PyPI name is now `mavsdk-grpc`, because plain `mavsdk` is a different API. Covers failure injection from Python.
- [pymavlink](ardupilot__pymavlink.md) - codec, connection helper and log tools. Use it to inject `VISION_POSITION_ESTIMATE` / `GPS_INPUT`, and to pull GPS/EKF fields out of logs.
- [mavlink-router](mavlink-router__mavlink-router.md) - fans out one autopilot link. Per-endpoint msg-id filters can make an agent-facing link read-only, and it logs on the companion.
- [QGroundControl](mavlink__qgroundcontrol.md) - the demo screen: EKF/GPS status, MAVLink Inspector, PX4 shell for failure injection.
- [MAVProxy](ardupilot__mavproxy.md) - terminal GCS that ships with ArduPilot SITL. The `GPSInput` module (UDP 25100 JSON => `GPS_INPUT`) and custom modules cover GNSS alerts.

## ROS bridges and navigation inputs

- [MAVROS](mavlink__mavros.md) - ROS 2 bridge for PX4 and ArduPilot. Covers `vision_pose`, `odometry/out` and `gps_input` plugins, and the ENU/NED handling.
- [vision_to_mavros](thien94__vision_to_mavros.md) - reference VIO => ArduPilot glue covering frame rotation, origin setting and rates. ROS 1 and unmaintained, so use it as a template.
- [px4-ros2-interface-lib](auterion__px4-ros2-interface-lib.md) - `GlobalPositionMeasurementInterface` takes map-matching lat/lon into PX4 EKF2 aux global position. External modes handle GNSS-loss behaviour.
- [px4_ros_com](px4__px4_ros_com.md) - PX4 ROS 2 examples plus `frame_transforms.h` NED/ENU helpers. Watch the `px4_msgs` version and the best-effort QoS.

## Common operating picture (TAK and symbology)

- [PyTAK](snstac__pytak.md) - Python CoT sender/receiver. Puts own-ship, detections and nav uncertainty (`ce`/`le`) on ATAK/TAK maps.
- [OpenTAKServer](brian7704__opentakserver.md) - TAK server with web map, video and Meshtastic, set up by installer script. Note the open message-path issues.
- [GoATAK](kdudkov__goatak.md) - single Go binary/Docker TAK server plus web client. Fastest live map for judges (AGPL).
- [milsymbol](spatialillusions__milsymbol.md) - MIL-STD-2525/APP-6 SVG symbols for Leaflet/MapLibre/Cesium web views.

## Detection and awareness sensors (defensive)

- [ArduRemoteID](ardupilot__arduremoteid.md) - ESP32 Remote ID transmitter firmware, used as a cooperative test emitter. Do not set `LOCK_LEVEL=2` (it burns eFuses).
- [OpenDroneID receiver-android](opendroneid__receiver-android.md) - phone-based Remote ID detector with CSV logs. Reception depends on the handset.
- [readsb](wiedehopf__readsb.md) - ADS-B decoder. `aircraft.json` integrity fields (NIC/NACp/SIL, `gpsOkBefore`) turn it into a GNSS-interference monitor.
- [KrakenSDR DoA](krakenrf__krakensdr_doa.md) - 5-channel coherent DF. CSV/XML/JSON bearing outputs are documented from source, plus a remote settings API.
- [Stone Soup](dstl__stone-soup.md) - multi-target tracking framework. Uses `Cartesian2DToBearing` for DF triangulation and readers for ADS-B/AIS data.

## LLM agents on the vehicle or robot

- [MAVLinkMCP](ion-g-ion__mavlinkmcp.md) - MCP server over MAVSDK with a reviewable survey-plan pipeline. Use `uv sync`, because the unpinned `mavsdk` dependency can pull the incompatible 4.x binding.
- [ros-mcp-server](robotmcp__ros-mcp-server.md) - MCP over rosbridge for any ROS robot. It has full write access, so gate it before anything flies.
- [ROSA](nasa-jpl__rosa.md) - LangChain ROS agent you embed in your own code. `blacklist` hides ROS names but does not remove write tools.

## Suggested chains

- GNSS-denied flight demo: PX4 SIH or ArduPilot SITL => inject GPS loss (`failure gps off` / `SIM_GPS1_ENABLE 0`) => VIO via MAVROS or map-matching fix via px4-ros2-interface-lib => QGC to show the estimator state.
- Air picture with PNT awareness: readsb (NIC/NACp) + Remote ID receiver + KrakenSDR bearings => Stone Soup tracks => PyTAK => OpenTAKServer/GoATAK, with milsymbol for a custom web view.
- Operator assistant: mavlink-router (filtered endpoint) => MAVLinkMCP, or MAVROS => ros-mcp-server, kept on the read side with a human approving actions.
