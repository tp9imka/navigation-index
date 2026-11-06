# Reference stacks: if you only have X, use Y

Opinionated picks for a 24-48h build. One default per capability, one alternative, and
what to avoid with the reason. "Avoid" means avoid under hackathon time pressure, not
that the project is bad. Reasons come from each repo's catalog page (hackathon notes,
maturity, archive status). Check the page for install lines before the event.

Companion doc: [hackathon-playbook.md](hackathon-playbook.md).

## Quick picks by what you have

| If you only have... | Build on | Because |
|---|---|---|
| Laptops, no hardware | [ArduPilot SITL](../catalog/resources/ardupilot-sitl-docs.md) + [pymavlink](../catalog/repos/ardupilot__pymavlink.md) + recorded datasets; start from the [ardupilot-ekf3-source-switch](../samples/ardupilot-ekf3-source-switch/) or [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/) samples | SITL in minutes, scripted GPS cuts, logs you can analyse |
| One u-blox receiver | [pyubx2](../catalog/repos/semuconsulting__pyubx2.md) + [PyTAK](../catalog/repos/snstac__pytak.md) | MON-RF and NAV-STATUS give jamming and spoof indicators directly |
| Android phones | [GnssLogger](../catalog/repos/google__gps-measurement-tools.md) + [gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md) | Raw measurements without extra hardware |
| An RTL-SDR | [readsb](../catalog/repos/wiedehopf__readsb.md) (1090 MHz) or [AIS-catcher](../catalog/repos/jvde-github__ais-catcher.md) (VHF) | Free sensor networks for interference awareness |
| A laptop GPU | [AnyLoc](../catalog/repos/anyloc__anyloc.md) + [LightGlue](../catalog/repos/cvg__lightglue.md) on [UAV-VisLoc](../catalog/repos/intellisensing__uav-visloc.md) | Visual geolocalization demo with ground truth |
| A Jetson | [XFeat](../catalog/repos/verlab__accelerated_features.md) + [Isaac ROS Visual SLAM](../catalog/resources/isaac-ros-visual-slam-docs.md) | Built for constrained hardware |
| Crazyflies | [cflib](../catalog/repos/bitcraze__crazyflie-lib-python.md) + [Loco Positioning](../catalog/resources/bitcraze-loco-positioning.md) | Indoor GNSS-denied testbed with UWB in a day |
| A BlueROV-class vehicle | [BlueOS](../catalog/repos/bluerobotics__blueos.md) + [dvl-python](../catalog/repos/waterlinked__dvl-python.md) | Extensions are Docker images; DVL protocol is simple |
| Only a DEM and Python | [TRN PF sample](../samples/terrain-relative-nav-pf/) + [Rasterio](../catalog/repos/rasterio__rasterio.md) | Stdlib simulation plus real terrain |
| Only Python and a filter book | [Kalman and Bayesian Filters in Python](../catalog/repos/rlabbe__kalman-and-bayesian-filters-in-python.md) + [FilterPy](../catalog/repos/rlabbe__filterpy.md) | Fastest onboarding to estimation |

## By capability

### Autopilot, SITL and vehicle link

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| Autopilot for GNSS-loss experiments | [ArduPilot](../catalog/repos/ardupilot__ardupilot.md) - EKF3 source switching ([docs](../catalog/resources/ardupilot-ekf3-sources.md)), Lua scripting without a fork | [PX4](../catalog/repos/px4__px4-autopilot.md) - EKF2 external vision and flow, BSD license | [Paparazzi](../catalog/repos/paparazzi__paparazzi.md) - fit marked low; smaller ecosystem for this use |
| Simulator for UAS | [Gazebo Sim](../catalog/repos/gazebosim__gz-sim.md) with PX4 or [ardupilot_gazebo](../catalog/repos/ardupilot__ardupilot_gazebo.md) | [gym-pybullet-drones](../catalog/repos/learnsyslab__gym-pybullet-drones.md) for control and swarm logic without photorealism | [AirSim](../catalog/repos/microsoft__airsim.md) - archived; source builds need an old Unreal. [Isaac Sim](../catalog/repos/isaac-sim__isaacsim.md) - RTX GPU and a lot of disk |
| MAVLink scripting | [pymavlink](../catalog/repos/ardupilot__pymavlink.md) | [MAVSDK-Python](../catalog/repos/mavlink__mavsdk-python.md) for missions and offboard | [DroneKit](../catalog/repos/dronekit__dronekit-python.md) - archived, breaks on recent Python |
| Link sharing between GCS and tools | [mavlink-router](../catalog/repos/mavlink-router__mavlink-router.md) | [mavp2p](../catalog/repos/bluenviron__mavp2p.md) - single binary, no build | Pointing several clients at one UDP port without a router |
| GCS | [QGroundControl](../catalog/repos/mavlink__qgroundcontrol.md) prebuilt | [MAVProxy](../catalog/repos/ardupilot__mavproxy.md) - write a module for custom alerts | QGC custom builds - Qt setup takes hours. [Mission Planner](../catalog/repos/ardupilot__missionplanner.md) on Linux/mac - Mono caveats |
| Custom nav-health messages | [MAVLink](../catalog/repos/mavlink__mavlink.md) dialect XML + regenerated bindings | STATUSTEXT with a fixed prefix for a quick hack | Repurposing unrelated common messages - confuses GCS and judges |
| ROS 2 bridge to PX4 | [px4_ros_com](../catalog/repos/px4__px4_ros_com.md) + [px4_msgs](../catalog/repos/px4__px4_msgs.md) (matching branch) | [MAVROS](../catalog/repos/mavlink__mavros.md) - mind ENU/NED | Mismatched px4_msgs branch - messages silently mismatch |

### GNSS, integrity and interference

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| Live receiver monitoring | [pyubx2](../catalog/repos/semuconsulting__pyubx2.md) | [gpsd](../catalog/repos/gitlab.com__gpsd__gpsd.md) for NMEA and PPS timing | Parsing NMEA only - loses MON-RF and spoof flags |
| Bench view of C/N0 | [PyGPSClient](../catalog/repos/semuconsulting__pygpsclient.md) | [u-blox ubxlib](../catalog/repos/u-blox__ubxlib.md) for embedded | - |
| GNSS data analysis in Python | [gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md) | [georinex](../catalog/repos/geospace-code__georinex.md) for RINEX; [laika](../catalog/repos/commaai__laika.md) for corrections | [GNSSTk](../catalog/repos/sgl-ut__gnsstk.md) - C++, fit marked low for a hackathon |
| RTK / post-processing | [RTKLIB demo5](../catalog/repos/rtklibexplorer__rtklib.md) | [pygnssutils](../catalog/repos/semuconsulting__pygnssutils.md) NTRIP client + [pyrtcm](../catalog/repos/semuconsulting__pyrtcm.md) | Upstream [RTKLIB](../catalog/repos/tomojitakasu__rtklib.md) - quiet since 2024; demo5 handles current receivers |
| Software receiver | [GNSS-SDR](../catalog/repos/gnss-sdr__gnss-sdr.md) from distro packages | [SoftGNSS Python](../catalog/repos/perrysou__softgnss-python.md) for offline IQ learning | Building GNSS-SDR from source on day one - long build |
| GPS signal simulation (cabled/file only) | [multi-sdr-gps-sim](../catalog/repos/mictronics__multi-sdr-gps-sim.md) - maintained, streams to several SDRs | [GPS-SDR-SIM](../catalog/repos/osqzss__gps-sdr-sim.md) to file, straight into GNSS-SDR | Any over-the-air transmission - illegal in most jurisdictions. GPS-SDR-SIM is archived |
| Navigation message authentication | [OSNMAlib](../catalog/repos/algafix__osnma.md) | [galileo-osnma](../catalog/repos/daniestevez__galileo-osnma.md) (Rust, embedded no_std) | [osnma_ublox](../catalog/repos/axelbjork__osnma_ublox.md) - archived, predates the public service |
| OSNMA test signals | [OSNMA-SDR-SIM](../catalog/repos/haiyang-wong__osnma-sdr-sim.md) file sink | Live u-blox SFRBX | - |
| Jamming detection from C/N0 | Own detector on pyubx2 data, using [GPSSpy](../catalog/repos/hoverflyhampton__gpsspy.md) as the method reference | [Android APIs](../catalog/resources/android-gnss-spoof-jam-detection.md) | Taking GPSSpy as a dependency - small 2021 codebase, GPL |
| RAIM / fault detection | gnss_lib_py fault detection examples | [RAIM (MATLAB)](../catalog/repos/michaelbeechan__raim.md) as reference | [MAAST for ARAIM](../catalog/repos/stanford-gps-lab__maast_for_araim_2.md) - service-area availability tool, not a receiver-side detector |
| Interference awareness from aircraft | [readsb](../catalog/repos/wiedehopf__readsb.md) + [pyModeS](../catalog/repos/junzis__pymodes.md) | [OpenSky API](../catalog/repos/openskynetwork__opensky-api.md) | Running both readsb and [dump1090](../catalog/repos/flightaware__dump1090.md) - pick one |
| Direction finding | [KrakenSDR DoA](../catalog/repos/krakenrf__krakensdr_doa.md) | [heimdall DAQ](../catalog/repos/krakenrf__heimdall_daq_fw.md) underneath for custom work | Hand-rolled coherent multi-SDR sync in 48h |

### Inertial and fusion

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| INS simulation / what-if | [pyins](../catalog/repos/nmayorov__pyins.md) | [gnss-ins-sim](../catalog/repos/aceinna__gnss-ins-sim.md) | - |
| GNSS/INS loosely coupled on real data | [KF-GINS](../catalog/repos/i2nav-whu__kf-gins.md) | [OB_GINS](../catalog/repos/i2nav-whu__ob_gins.md) same formats, side-by-side | [IC-GVINS](../catalog/repos/i2nav-whu__ic-gvins.md) - heavier ROS setup |
| Factor graph fusion | [GTSAM](../catalog/repos/borglab__gtsam.md) (pip, ImuFactor examples) | [navlie](../catalog/repos/decargroup__navlie.md) | [gtsam_gnss](../catalog/repos/taroz__gtsam_gnss.md) - needs author's GTSAM fork and MATLAB |
| Simple EKF/UKF in Python | [FilterPy](../catalog/repos/rlabbe__filterpy.md) | [manif](../catalog/repos/artivis__manif.md) for Lie-group states | FilterPy for 3D attitude states - not Lie-group aware |
| ROS 2 localization | [robot_localization](../catalog/repos/cra-ros-pkg__robot_localization.md) | [MINS](../catalog/repos/rpng__mins.md) for multi-sensor with GNSS dropout demos | Double-counting velocities and REP-103/105 frame mistakes |
| Sensor dropout / plug-in fusion | [MaRS](../catalog/repos/aau-cns__mars_lib.md) | MINS | - |
| AHRS | [x-io Fusion](../catalog/repos/xiotechnologies__fusion.md) | [AHRS (Python)](../catalog/repos/mayitzin__ahrs.md) | - |
| IMU noise calibration | [allan_variance_ros](../catalog/repos/ori-drs__allan_variance_ros.md) | [allan-variance (Python)](../catalog/repos/nmayorov__allan-variance.md) | [kalibr_allan](../catalog/repos/rpng__kalibr_allan.md) - archived |
| Camera-IMU calibration | [Kalibr](../catalog/repos/ethz-asl__kalibr.md) via Docker, print AprilGrid ahead | [iKalibr](../catalog/repos/unsigned-long__ikalibr.md) | Building Kalibr natively - ROS 1 build pain |

### Vision, lidar, radar odometry

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| VIO | [OpenVINS](../catalog/repos/rpng__open_vins.md) - built-in simulator, ROS 1 and 2 | [Basalt](../catalog/repos/vladyslavusenko__basalt.md) - builds cleanly | [ORB-SLAM3](../catalog/repos/uz-slamlab__orb_slam3.md) if nobody has built it before - expect compile fixes. [SVO Pro](../catalog/repos/uzh-rpg__rpg_svo_pro_open.md) - ROS 1, dormant |
| Visual SLAM with map reuse | [RTAB-Map](../catalog/repos/introlab__rtabmap.md) - apt binaries, localization mode | ORB-SLAM3 | [VINS-Fusion](../catalog/repos/hkust-aerial-robotics__vins-fusion.md) without Docker - ROS 1 |
| VIO on Jetson | [Isaac ROS Visual SLAM](../catalog/resources/isaac-ros-visual-slam-docs.md) | OpenVINS | - |
| LiDAR odometry | [KISS-ICP](../catalog/repos/prbonn__kiss-icp.md) - pip, runs on a bag in minutes | [FAST-LIO](../catalog/repos/hku-mars__fast_lio.md) with IMU | [LIO-SAM](../catalog/repos/tixiaoshan__lio-sam.md) unless you have a 9-axis IMU and good extrinsics |
| LiDAR loop closure / relocalization | [KISS-SLAM](../catalog/repos/prbonn__kiss-slam.md) | [small_gicp](../catalog/repos/koide3__small_gicp.md) scan-to-map | FAST-LIO alone - no loop closure |
| Radar odometry | [RIO](../catalog/repos/christopherdoer__rio.md) (4D mmWave) | [CFEAR](../catalog/repos/dan11003__cfear_radarodometry.md) (spinning radar) | Expecting ROS 2 - most radar tools here are ROS 1 |
| Trajectory evaluation | [evo](../catalog/repos/michaelgrupp__evo.md) | [rpg_trajectory_evaluation](../catalog/repos/uzh-rpg__rpg_trajectory_evaluation.md) | Reporting error without alignment flags stated |

### Absolute alt-PNT

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| Visual place retrieval (tiles) | [AnyLoc](../catalog/repos/anyloc__anyloc.md) | [SALAD](../catalog/repos/serizba__salad.md) via torch.hub; [MixVPR](../catalog/repos/amaralibey__mixvpr.md) for lightweight | Skipping retrieval - [WildNav](../catalog/repos/tiers__wildnav.md) brute-force tile search is slow |
| Feature matching | [LightGlue](../catalog/repos/cvg__lightglue.md) | [XFeat](../catalog/repos/verlab__accelerated_features.md) on CPU / edge | [RoMa](../catalog/repos/parskatt__roma.md) as the main matcher - accurate but slow; use as top-1 verifier only |
| Matcher shoot-out | [vismatch](../catalog/repos/gmberton__vismatch.md) | [VPR methods evaluation](../catalog/repos/gmberton__vpr-methods-evaluation.md) for retrieval | - |
| Visual geolocalization pipeline skeleton | [visual-geolocalization-lightglue sample](../samples/visual-geolocalization-lightglue/) | [UAVLocalization](../catalog/repos/hmf21__uavlocalization.md) | [gnss-denied-uav-geolocalization](../catalog/repos/yfs90__gnss-denied-uav-geolocalization.md) - check what is actually released first |
| Night / thermal geolocalization | [satellite-thermal geo-localization](../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md) | - | Planning around it without gated dataset access approved |
| Reference map building | [OpenDroneMap](../catalog/repos/opendronemap__odm.md) | [pystac-client](../catalog/repos/stac-utils__pystac-client.md) for open imagery | - |
| Terrain-relative navigation | [TRN PF sample](../samples/terrain-relative-nav-pf/) + [Rasterio](../catalog/repos/rasterio__rasterio.md) | [tercom_nav](../catalog/repos/mzahana__tercom_nav.md) for ROS 2 + SITL; [python-tercom](../catalog/repos/alti3__python-tercom.md) | MATLAB-only [TERCOM PF](../catalog/repos/sotostrk__tercom-via-particle-filter-uav-state-estimation-mae6760-project-.md) if the team is Python |
| DEM download | [elevation](../catalog/repos/bopen__elevation.md) | [Copernicus DEM on AWS](../catalog/resources/copernicus-dem-aws.md) direct COG reads | - |
| Magnetic anomaly navigation | [MagNav.jl](../catalog/repos/mit-ai-accelerator__magnav.jl.md) | [MagNavPy](../catalog/repos/manasp21__magnav.py.md) (verify against MagNav.jl) | Small multirotor MagNav without compensation - platform noise dominates |
| Celestial | [tetra3](../catalog/repos/esa__tetra3.md) | [cedar-solve](../catalog/repos/smroid__cedar-solve.md) | [deep_learning_celnav](../catalog/repos/gregtozzi__deep_learning_celnav.md) - exploratory, fit low |
| LEO signals of opportunity | [LEOSPINE](../catalog/repos/xyangll__leospine.md) simulation | [UT Starlink signal simulator](../catalog/repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md) | Live Ku-band reception in 48h - needs LNB hardware; [Starlink LEO-PNT](../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md) claims unverified |
| UWB ranging | [Crazyflie firmware](../catalog/repos/bitcraze__crazyflie-firmware.md) + Loco | [UWB software library](../catalog/repos/vladniculescu__uwb-software-library.md) | [uwb-localization](../catalog/repos/lijx10__uwb-localization.md) - ROS 1, fit low |
| Pedestrian / dismounted | [PyShoe](../catalog/repos/utiasstars__pyshoe.md) | [RoNIN](../catalog/repos/sachini__ronin.md) / [TLIO](../catalog/repos/cathias__tlio.md) | [zupt-aided-ins](../catalog/repos/hcarlsso__zupt-aided-ins.md) as a dependency - archived since 2021 (fine as reading) |

### Situational awareness and C2

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| TAK server | [OpenTAKServer](../catalog/repos/brian7704__opentakserver.md) | [GoATAK](../catalog/repos/kdudkov__goatak.md) - web client for judges without ATAK | [FreeTAKServer](../catalog/repos/freetakteam__freetakserver.md) - activity slowed since 2024 |
| CoT from Python | [PyTAK](../catalog/repos/snstac__pytak.md) | [takproto](../catalog/repos/snstac__takproto.md) for protobuf | Writing an ATAK plugin - [ATAK-CIV](../catalog/repos/tak-product-center__atak-civ.md) SDK toolchain takes half a day |
| CoT from Node | [node-CoT](../catalog/repos/dfpc-coe__node-cot.md) | - | [CloudTAK](../catalog/repos/dfpc-coe__cloudtak.md) full deploy - AWS-oriented, AGPL |
| Vehicle to TAK | [mavlink-to-tak-cot sample](../samples/mavlink-to-tak-cot/) | [ADSBCOT](../catalog/repos/snstac__adsbcot.md) for aircraft | - |
| Military symbology | [milsymbol](../catalog/repos/spatialillusions__milsymbol.md) | [MIL-STD-2525D](../catalog/resources/mil-std-2525d.md) reference | Hand-drawn icons - judges notice |
| 2D web map (offline) | [MapLibre GL JS](../catalog/repos/maplibre__maplibre-gl-js.md) + [PMTiles](../catalog/repos/protomaps__pmtiles.md) | [Leaflet](../catalog/repos/leaflet__leaflet.md) | Online tile services at a venue with bad Wi-Fi |
| Many tracks / heatmaps | [deck.gl](../catalog/repos/visgl__deck.gl.md) | [tar1090](../catalog/repos/wiedehopf__tar1090.md) for ADS-B | - |
| 3D picture | [CesiumJS](../catalog/repos/cesiumgs__cesium.md) | - | Default Cesium ion assets when offline - serve your own terrain ([cesium-terrain-builder](../catalog/repos/geo-data__cesium-terrain-builder.md)) |
| Multi-target tracking / fusion | [Stone Soup](../catalog/repos/dstl__stone-soup.md) ([sample](../samples/stone-soup-tracking/)) | [BoxMOT](../catalog/repos/mikel-brostrom__boxmot.md) for camera tracks | [pymht](../catalog/repos/erikliland__pymht.md) - fit low |
| Geodesy and grids | [pyproj](../catalog/repos/pyproj4__pyproj.md) + [pymap3d](../catalog/repos/geospace-code__pymap3d.md) | [GeographicLib](../catalog/repos/geographiclib__geographiclib.md); [mgrs](../catalog/repos/hobuinc__mgrs.md) for MGRS | Hand-rolled ECEF/ENU conversions |
| Raster and DEM processing | [GDAL](../catalog/repos/osgeo__gdal.md) via conda or Docker | [QGIS](../catalog/repos/qgis__qgis.md) for analyst work | Mixing pip GDAL bindings with a system GDAL |

### Planning and multi-agent

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| Air path planning | [OMPL](../catalog/repos/ompl__ompl.md) | [PythonRobotics](../catalog/repos/atsushisakai__pythonrobotics.md) grid planners over a rasterized DEM | - |
| Road routing (offline) | [Valhalla](../catalog/repos/valhalla__valhalla.md) - request-time costing | [OSRM](../catalog/repos/project-osrm__osrm-backend.md) | [OSMnx](../catalog/repos/gboeing__osmnx.md) offline - needs Overpass unless you load a local file |
| Area coverage / survey | [Fields2Cover](../catalog/repos/fields2cover__fields2cover.md) | - | - |
| Mission logic | [BehaviorTree.CPP](../catalog/repos/behaviortree__behaviortree.cpp.md) | [PlanSys2](../catalog/repos/plansys2__ros2_planning_system.md) | - |
| Task allocation | [CBBA (Python)](../catalog/repos/inmo-jang__consensus-based-bundle-algorithm.md) | [rmf_task](../catalog/repos/open-rmf__rmf_task.md) | - |
| UGV navigation | [Nav2](../catalog/repos/ros-navigation__navigation2.md) | [CMU exploration env](../catalog/repos/hongbiaoz__autonomous_exploration_development_environment.md) | [CARLA](../catalog/repos/carla-simulator__carla.md) without a decent GPU |
| Multi-UAV framework | [Aerostack2](../catalog/repos/aerostack2__aerostack2.md) | [MRS UAV system](../catalog/repos/ctu-mrs__mrs_uav_system.md) | - |
| Swarm sim | [Crazyswarm2](../catalog/repos/imrclab__crazyswarm2.md) | [gym-pybullet-drones](../catalog/repos/learnsyslab__gym-pybullet-drones.md) | [EGO-Swarm](../catalog/repos/zju-fast-lab__ego-planner-swarm.md) as a localization demo - assumes reliable comms (interesting to degrade, though) |
| Multi-robot SLAM | [Swarm-SLAM](../catalog/repos/mistlab__swarm-slam.md) | [CSLAM](../catalog/repos/lajoiepy__cslam.md) | [Kimera-Multi](../catalog/repos/mit-spark__kimera-multi.md) - index repo, heavy, fit low |

### Maritime and underwater

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| AIS decode | [pyais](../catalog/repos/m0r13n__pyais.md) | [noaadata](../catalog/repos/schwehr__noaadata.md) | - |
| Live AIS from RF | [AIS-catcher](../catalog/repos/jvde-github__ais-catcher.md) | - | - |
| Marine data bus | [Signal K Server](../catalog/repos/signalk__signalk-server.md) | NMEA over UDP with [pynmeagps](../catalog/repos/semuconsulting__pynmeagps.md) | - |
| Chart display | [OpenCPN](../catalog/repos/opencpn__opencpn.md) | MapLibre web map | Writing an OpenCPN plugin in 48h - feed it NMEA instead |
| USV simulation | [VRX](../catalog/repos/osrf__vrx.md) | [MOOS-IvP](../catalog/repos/moos-ivp__moos-ivp.md) with pMarineViewer | [Aeolus Ocean](../catalog/repos/aavek__aeolus-ocean.md) - fit low |
| Collision avoidance sim | [NTNU colav-simulator](../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) | - | - |
| UUV simulation | [Stonefish](../catalog/repos/patrykcieslak__stonefish.md) | [HoloOcean ROS](../catalog/repos/byu-holoocean__holoocean-ros.md) (needs GPU) | [UUV Simulator](../catalog/repos/uuvsimulator__uuv_simulator.md) - archived. [DAVE](../catalog/repos/field-robotics-lab__dave.md) - ROS 1, half-day setup |
| DVL / acoustic positioning | [dvl-python](../catalog/repos/waterlinked__dvl-python.md) + [USBL simulator](../catalog/repos/maximilian-nitsch__usbl-simulator.md) | [AUV estimator](../catalog/repos/alliwong__auvestimator.md) as a template only | [dvl-a50-ros-driver](../catalog/repos/waterlinked__dvl-a50-ros-driver.md) - archived, ROS 1 |

### LLM agents

| Capability | Default | Alternative | Avoid because |
|---|---|---|---|
| MCP server pattern | The hub's stdlib server ([llm-agent-usage](../samples/llm-agent-usage/)) as a template for your own MAVLink / GIS tools | - | Letting an agent call vehicle commands without a human confirmation step and an allowlist |
| Vehicle tools for the agent | [pymavlink](../catalog/repos/ardupilot__pymavlink.md) against SITL | [MAVSDK-Python](../catalog/repos/mavlink__mavsdk-python.md) | Running against real hardware during the event |
| Sim plus foundation models | [GRID playground](../catalog/repos/genrobo__grid-playground.md) | Gazebo + your own tool layer | Relying on GRID's hosted sim without checking account requirements first |
| Querying this hub from an agent | `claude mcp add navigation-index -- python3 /abs/path/tools/mcp_server.py` | `python3 tools/query.py` | - |
