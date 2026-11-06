# Integration cards - C2, GIS, maritime, receivers, Remote ID, perception

<!-- about: repo:leaflet/leaflet, repo:visgl/deck.gl, repo:maplibre/martin, repo:maptiler/tileserver-gl, repo:gboeing/osmnx, repo:valhalla/valhalla, repo:project-osrm/osrm-backend, repo:pyproj4/pyproj, repo:geographiclib/geographiclib, repo:jjsantos01/qgis_mcp, repo:mahdin75/gis-mcp, repo:typefly/typefly, repo:openskynetwork/opensky-api, repo:junzis/pymodes, repo:jvde-github/ais-catcher, repo:m0r13n/pyais, repo:signalk/signalk-server, repo:opencpn/opencpn, repo:moos-ivp/moos-ivp, repo:ntnu-itk-autonomous-ship-lab/colav-simulator, repo:bluerobotics/blueos, repo:stephendade/rpanion-server, repo:bluenviron/mavp2p, repo:semuconsulting/pygpsclient, repo:semuconsulting/pyrtcm, repo:semuconsulting/pynmeagps, repo:lord-microstrain/ntrip_client, repo:kumarrobotics/ublox, repo:google/gps-measurement-tools, repo:geospace-code/georinex, repo:opendroneid/opendroneid-core-c, repo:peterjburke/rid, repo:colonelpanichacks/drone-mesh-mapper, repo:dfpc-coe/node-cot, repo:missioncommand/mil-sym-ts, repo:ultralytics/ultralytics, repo:mikel-brostrom/boxmot, repo:zhaoj9014/anti-uav, repo:dusty-nv/jetson-containers, repo:nvidia-ai-iot/torch2trt, repo:copterexpress/clover -->

What each card gives you in a hackathon. All 41 were written from READMEs, manifests (pyproject, setup.py, package.json, CMake), source files and issues read through the GitHub API, with PyPI and npm versions checked against registry JSON on 2026-11-06. None of these repos was installed or run, and every snippet is marked "not run". The one exception is a small NMEA-formatting helper in the OpenCPN card, which was run locally.

## Licence traps first

- **AGPL-3.0:** [Ultralytics](ultralytics__ultralytics.md) (code *and* pretrained weights; Enterprise licence otherwise), [BoxMOT](mikel-brostrom__boxmot.md), and [BlueOS](bluerobotics__blueos.md) (AGPL-3.0-only or a custom BlueOS licence). AGPL applies on network use, so a hosted dashboard counts. Per Ultralytics' own answer in issue #26703, the whole project that includes YOLO must be open, and wrapping YOLO in a separate process does not exempt the rest. [TypeFly](typefly__typefly.md) is Apache-2.0 but depends on ultralytics.
- **GPL:** [OpenSky API client](openskynetwork__opensky-api.md) (GPL-3.0; data under OpenSky terms), [pyModeS](junzis__pymodes.md) (GPL-3.0), [AIS-catcher](jvde-github__ais-catcher.md) (GPL-3.0), [Rpanion-server](stephendade__rpanion-server.md) (GPL-3.0), [OpenCPN](opencpn__opencpn.md) (GPL-2.0+), [MOOS-IvP](moos-ivp__moos-ivp.md) (mixed GPLv3/LGPLv3 plus a commercial option).
- **No licence:** [QGIS MCP](jjsantos01__qgis_mcp.md) has no LICENSE file. [drone-mesh-mapper](colonelpanichacks__drone-mesh-mapper.md) is MIT but forked from an unlicensed repo.
- **Data and docs:** OSM-derived routing and tiles are ODbL ([OSMnx](gboeing__osmnx.md), [Valhalla](valhalla__valhalla.md), [OSRM](project-osrm__osrm-backend.md), [TileServer GL](maptiler__tileserver-gl.md); its default styles have a separate CC BY 3.0 design licence). Anti-UAV data has no stated licence. BoxMOT's person-ReID weights come from research-only datasets. [Clover](copterexpress__clover.md) docs are CC BY-NC-SA. Container images from [jetson-containers](dusty-nv__jetson-containers.md) include NVIDIA EULA components.

## Web maps, tiles and geodesy

- [Leaflet](leaflet__leaflet.md) - Minimal 2D web map for operator views, with no WebGL. Stable is still 1.9.4. Coordinates are `[lat, lng]`, and OSM tiles need a referrer policy.
- [deck.gl](visgl__deck.gl.md) - GPU layers for a common operating picture: thousands of live tracks, TripsLayer trails, hexbins, 3D tiles over MapLibre. MIT. pydeck is Apache-2.0.
- [Martin](maplibre__martin.md) - Rust tile server for PostGIS/PMTiles/MBTiles with fonts, sprites and bulk MBTiles export. Stable 1.16.1. Docs on `main` describe 2.0 beta. x86 builds need AVX2 unless you use `-legacycpu`.
- [TileServer GL](maptiler__tileserver-gl.md) - Serves MBTiles/PMTiles with GL styles and renders raster tiles, WMTS and static images for raster-only clients. Set `--public_url`.
- [pyproj](pyproj4__pyproj.md) - PROJ from Python for datum, UTM, ECEF and geoid transforms. Use `always_xy=True`. Grids are not in the wheels, so vertical transforms can silently return 0.
- [GeographicLib](geographiclib__geographiclib.md) - Karney geodesics, UTM/UPS/MGRS, LocalCartesian ENU, EGM geoid and WMM in C++ (MAVROS depends on it). The PyPI package covers geodesics only.

## Routing and GIS agents

- [OSMnx](gboeing__osmnx.md) - OSM area => NetworkX road graph with speeds and travel times. Python >=3.11, Overpass by default. Watch the argument orders.
- [Valhalla](valhalla__valhalla.md) - Offline routing with dynamic costing, isochrones and `trace_route` map matching. PyPI name is `pyvalhalla`, not `valhalla`.
- [OSRM](project-osrm__osrm-backend.md) - Fastest OSM router (route/table/trip/match). npm is `@project-osrm/osrm`. Docker tags are `v26.x-debian`. Pass `algorithm: 'MLD'` in Node when the data is MLD.
- [QGIS MCP](jjsantos01__qgis_mcp.md) - LLM drives QGIS Desktop through a plugin plus MCP server. `execute_code` runs arbitrary PyQGIS over an unauthenticated socket. Breaks on QGIS 4.
- [GIS MCP](mahdin75__gis-mcp.md) - pip MCP server exposing Shapely/PyProj/GeoPandas/Rasterio to LLMs. Hard pins (numpy<2, rasterio 1.3.9), and #45 reports a silent 74 m reprojection error.
- [TypeFly](typefly__typefly.md) - Typed instruction => GPT plan => Tello/Go2 skills, with YOLO scene grounding. Needs an OpenAI key. The Tello is indoor-only with no GNSS.

## Air and maritime picture

- [OpenSky API](openskynetwork__opensky-api.md) - Python client for OpenSky state vectors, flights and tracks. Not on PyPI. OAuth2 only since 2026-03. Credit-limited.
- [pyModeS](junzis__pymodes.md) - Mode S/ADS-B decoder with NIC/NACp/SIL, and `modes live` from a Beast feed. v3 removed the v2 API.
- [AIS-catcher](jvde-github__ais-catcher.md) - SDR => AIS with a web map and NMEA/JSON out. Not for navigation use (README). Local reception legality varies.
- [pyais](m0r13n__pyais.md) - AIS decode/encode plus a tracker. "Not available" values arrive as numbers (lat 91). The tracker's ms/seconds mix-up was found in `tracker.py`.
- [Signal K server](signalk__signalk-server.md) - Marine data hub: NMEA 0183/2000 and AIS => one SI-unit JSON model over REST/WS. m/s and radians. The Docker quickstart runs with security off.
- [OpenCPN](opencpn__opencpn.md) - Chartplotter with own-ship from NMEA or Signal K, plus AIS. Charts are not bundled, and many ENCs are S-63 encrypted.
- [MOOS-IvP](moos-ivp__moos-ivp.md) - Marine autonomy helm with COLREGs behaviours. Nav input is `NAV_X/NAV_Y/NAV_HEADING/NAV_SPEED`. Has a UTM zone bug (#72).
- [colav-simulator](ntnu-itk-autonomous-ship-lab__colav-simulator.md) - Python COLREGs scenario sim on Norwegian ENCs with a pluggable planner and a Gymnasium env. Python 3.10-3.11. ENCs are in Git LFS.

## Companion computers and MAVLink routing

- [BlueOS](bluerobotics__blueos.md) - Docker onboard OS for ArduPilot, with MAVLink routers, mavlink2rest and NMEA => `GPS_INPUT` injection. AGPL. `install.sh` defaults to `master`.
- [Rpanion-server](stephendade__rpanion-server.md) - Web-configured companion: mavlink-router, RTSP video, NTRIP => `GPS_RTCM_DATA`. Default login admin/admin.
- [mavp2p](bluenviron__mavp2p.md) - Single static Go binary routing MAVLink across serial/UDP/TCP. No macOS build.
- [Clover](copterexpress__clover.md) - ROS Noetic + PX4 with Python `navigate()` services and ArUco-map GNSS-free flight, plus a simulator VM. Noetic is EOL.

## GNSS receivers, corrections and logs

- [PyGPSClient](semuconsulting__pygpsclient.md) - tkinter GNSS GUI: C/N0, sky view, MON-SPAN spectrum, NTRIP client/caster. Entry point `pygpsclient`. Needs system Tk.
- [pyrtcm](semuconsulting__pyrtcm.md) - RTCM3 parse and serialize with scaled fields. The reader drops non-RTCM bytes, so use `GNSSReader` for mixed streams.
- [pynmeagps](semuconsulting__pynmeagps.md) - Zero-dependency NMEA 0183 parser and generator, including GST sigmas. pyserial is not a dependency.
- [ntrip_client (MicroStrain)](lord-microstrain__ntrip_client.md) - ROS 1/2 NTRIP => `/rtcm` with GGA back-feed. RTCM message type defaults differ between node and launch file.
- [ublox (KumarRobotics)](kumarrobotics__ublox.md) - ROS u-blox driver with NavSatFix and raw UBX. Use the `ros2` branch. The F9 AID NACK has a workaround.
- [GPS Measurement Tools](google__gps-measurement-tools.md) - GnssLogger app plus MATLAB tools for Android raw GNSS. Mostly MATLAB. Expect manual ephemeris download.
- [georinex](geospace-code__georinex.md) - RINEX 2/3/4 + SP3 => xarray. The PyPI release is from 2023. Open bugs on mixed BRDC nav.

## Remote ID, TAK and symbology (receive and display only)

- [opendroneid-core-c](opendroneid__opendroneid-core-c.md) - Reference ASTM F3411 codec for decoding captured BLE/Wi-Fi Remote ID. Build from `master` for the 2026 bounds-check fixes.
- [RID (Burke)](peterjburke__rid.md) - ESP32 BLE Remote ID receiver => JSON over serial. Unmaintained, BLE4 only.
- [drone-mesh-mapper](colonelpanichacks__drone-mesh-mapper.md) - ESP32 Remote ID sniffers + Meshtastic relay + Flask map. No auth, binds 0.0.0.0.
- [node-cot](dfpc-coe__node-cot.md) - `@tak-ps/node-cot`: CoT XML/protobuf/GeoJSON conversion. ESM, Node >=22. The README `new CoT(xml)` is stale.
- [mil-sym-ts](missioncommand__mil-sym-ts.md) - MIL-STD-2525D/E / APP-6D renderer in TypeScript: SVG icons and tactical graphics as GeoJSON/KML.

## Perception, C-UAS detection and edge

- [Ultralytics YOLO](ultralytics__ultralytics.md) - Quickest detector/tracker with export to ONNX/TensorRT. **AGPL, including weights.** Permissive options: RF-DETR (Apache base models), RT-DETR, YOLOX, jetson-inference.
- [BoxMOT](mikel-brostrom__boxmot.md) - Pluggable MOT trackers over any detector's boxes. AGPL. Its ReID weights are person-only, so use motion-only trackers for drones.
- [Anti-UAV](zhaoj9014__anti-uav.md) - RGB+IR drone tracking benchmark with an `exist`-aware metric. The repo evaluator's `not_exist()` mis-scores list predictions (from reading the code).
- [jetson-containers](dusty-nv__jetson-containers.md) - JetPack-matched Docker images (PyTorch, ROS 2, OpenCV-CUDA). Only JP 6.2 / 7 are supported. Orin Nano builds need NVMe and swap.
- [torch2trt](nvidia-ai-iot__torch2trt.md) - PyTorch => TensorRT in one call. Not on PyPI, unmaintained since 2024, and breaks on the TensorRT 10 API.

## Not verified across this batch

- OpenSky terms-of-use page (it refused automated fetch).
- Kartverket ENC terms.
- PROJ grid and geoid/WMM data licences.
- Font licences for TileServer GL styles.
- Docker tags for mavp2p, Martin 2.0 beta and BlueOS per release.
- Current Tello firmware compatibility.
- Any runtime behaviour.
