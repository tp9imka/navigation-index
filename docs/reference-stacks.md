# Reference stacks: if you only have X, use Y

Opinionated picks for a 24-48h build. One default per capability, one alternative, and
what to avoid with the reason. "Avoid" means avoid under hackathon time pressure, not
that the project is bad. Reasons come from each repo's catalog page (hackathon notes,
maturity, archive status). Check the page for install lines before the event.

Updated 2026-11-06 (v2): every pick that has an [integration card](integration-cards/) links
it as "card" - install line, inputs/outputs, minimal usage, wiring, gotchas and license, all
read from source and docs (no card was run). Card indexes:
[flight stack and C2](integration-cards/_index-flight-c2.md),
[GNSS, fusion, GIS](integration-cards/_index-gnss-fusion-gis.md),
[perception and alt-nav](integration-cards/_index-perception-altnav.md).
Datasets: [dataset cards](dataset-cards/README.md) with checked sizes and licenses.

Updated 2026-11-06 (v2.1): picks that a sample already runs now link that sample (status, deps
and first command in [samples/README.md](../samples/README.md); measured numbers in
[evidence-matrix.md](evidence-matrix.md)).

Companion docs: [hackathon-playbook.md](hackathon-playbook.md),
[day0-runbook.md](day0-runbook.md), [problem-statement-decoder.md](problem-statement-decoder.md).

**License column.** First linked repo in the Default and Alternative cells. Where a card
exists the note is the card's reading of LICENSE files and weight terms; otherwise it is the
GitHub license field (`unclear (NOASSERTION)` means GitHub could not classify it - read the
LICENSE file; `not stated` means GitHub found none). Code license is not weights license:
"NC" marks non-commercial weights or data. Fine for a hackathon demo; it matters the moment
the pitch says "product". Weights terms per model, read from source:
[model-weights-licenses.md](model-weights-licenses.md).

### License traps (from the cards)

| Trap | Where | What to do |
|---|---|---|
| SuperPoint / SuperGlue weights are Magic Leap non-commercial | LightGlue default extractor ([card](integration-cards/cvg__lightglue.md)), hloc `superpoint_*` configs ([card](integration-cards/cvg__hierarchical-localization.md)), WildNav ([card](integration-cards/tiers__wildnav.md)), LightGlue-ONNX SuperPoint export ([card](integration-cards/fabio-sim__lightglue-onnx.md)) | Use ALIKED or DISK with LightGlue, `raco_aliked` for ONNX, or XFeat (Apache-2.0 incl. weights, [card](integration-cards/verlab__accelerated_features.md)) |
| Wrapped models carry their own licenses | vismatch ([card](integration-cards/gmberton__vismatch.md): MASt3R CC BY-NC-SA), VPR-methods-evaluation ([card](integration-cards/gmberton__vpr-methods-evaluation.md): SALAD GPL-3.0, MixVPR no license) | Pick the winner of the shoot-out, then read its own license |
| Dense matcher indoor weights trained on ScanNet (NC) | RoMa ([card](integration-cards/parskatt__roma.md)) | Use the outdoor weights for aerial work |
| Hardware-locked license | cuVSLAM ([card](integration-cards/nvidia-isaac__cuvslam.md)) - NVIDIA platforms only | Fine on a Jetson demo; not a portable dependency |
| No LICENSE file = all rights reserved | python-tercom ([card](integration-cards/alti3__python-tercom.md)); tercom_nav has none but declares Apache-2.0 in package.xml ([card](integration-cards/mzahana__tercom_nav.md)) | Read, do not copy; reimplement the small parts |
| Data agreements stricter than the code | MagNav.jl data (AFRL agreement, [card](integration-cards/mit-ai-accelerator__magnav.jl.md)); most dataset cards are CC BY-NC-SA; AnyVisLoc forbids redistribution | Keep data out of the team repo; link to the host |
| Copyleft at link time | GNSS-SDR, OpenVINS, ORB-SLAM3, MINS, KF-GINS, evo (GPL-3.0), GoATAK (AGPL-3.0), OSNMAlib (EUPL-1.2) | Run them as separate processes (UDP, files) if the pitch mentions a closed product |

### Version traps (from the cards)

- **MAVSDK-Python**: `pip install mavsdk` now pulls a different native binding. Use
  `pip install mavsdk-grpc` / `import mavsdk_grpc`, or pin `mavsdk<4` for old tutorials
  ([card](integration-cards/mavlink__mavsdk-python.md)). MAVLinkMCP's unpinned dependency hits
  the same trap - use `uv sync` ([card](integration-cards/ion-g-ion__mavlinkmcp.md)).
- **PX4 v1.17.0 vs `main`**: SIH target (`make px4_sitl sihsim_quadx` vs
  `make px4_sitl_sih sihsim_quadx`), aux global position params (`EKF2_AGP_*` vs
  `EKF2_AGP0..3_*`), `GLOBAL_POSITION_SENSOR` ingress only on `main`
  ([card](integration-cards/px4__px4-autopilot.md)). Pin one, read docs for that tag.
- **ArduPilot 4.6 vs 4.7 / master**: SITL GPS params moved from `SIM_GPS_*`
  (`SIM_GPS_DISABLE 1`) to `SIM_GPS1_*` (`SIM_GPS1_ENABLE 0`)
  ([card](integration-cards/ardupilot__ardupilot.md)). The
  [sitl-docker](../samples/sitl-docker/) compose pins Copter 4.6.3 and PX4 v1.17.0.
- **FilterPy 2.0.0** changes the API ([card](integration-cards/rlabbe__filterpy.md));
  **elevation 2.0** breaks 1.x commands ([card](integration-cards/bopen__elevation.md));
  **MapLibre v6** is ESM-only ([card](integration-cards/maplibre__maplibre-gl-js.md));
  **tetra3** breaks on NumPy 2 and is not on PyPI ([card](integration-cards/esa__tetra3.md));
  **cedar-solve** git tag v0.6.0 runs on NumPy 2 when installed with `--no-deps` (its
  pyproject still pins `numpy<2`; [card](integration-cards/smroid__cedar-solve.md)).

## Quick picks by what you have

| If you only have... | Build on | Because |
|---|---|---|
| Laptops, no hardware | [ArduPilot SITL](../catalog/resources/ardupilot-sitl-docs.md) + [pymavlink](../catalog/repos/ardupilot__pymavlink.md) ([card](integration-cards/ardupilot__pymavlink.md)) + recorded datasets; start from [golden-demo](../samples/golden-demo/) (spoof => integrity => source switch => dashboard), [ardupilot-ekf3-source-switch](../samples/ardupilot-ekf3-source-switch/) or [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/) | SITL in minutes, scripted GPS cuts, logs you can analyse |
| One u-blox receiver | [pyubx2](../catalog/repos/semuconsulting__pyubx2.md) ([card](integration-cards/semuconsulting__pyubx2.md)) + [PyTAK](../catalog/repos/snstac__pytak.md) ([card](integration-cards/snstac__pytak.md)); [gnss-interference-monitor](../samples/gnss-interference-monitor/) for one node, [jammer-sensor-network](../samples/jammer-sensor-network/) for many | MON-RF and NAV-STATUS give jamming and spoof indicators directly |
| Android phones | [GnssLogger](../catalog/repos/google__gps-measurement-tools.md) + [gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md) ([card](integration-cards/stanford-navlab__gnss_lib_py.md)) | Raw measurements without extra hardware |
| An RTL-SDR | [readsb](../catalog/repos/wiedehopf__readsb.md) ([card](integration-cards/wiedehopf__readsb.md)) (1090 MHz) or [AIS-catcher](../catalog/repos/jvde-github__ais-catcher.md) (VHF) | Free sensor networks for interference awareness |
| A laptop GPU | [AnyLoc](../catalog/repos/anyloc__anyloc.md) ([card](integration-cards/anyloc__anyloc.md)) + [LightGlue](../catalog/repos/cvg__lightglue.md) ([card](integration-cards/cvg__lightglue.md)) on [UAV-VisLoc](../catalog/repos/intellisensing__uav-visloc.md); [geoloc-license-clean](../samples/geoloc-license-clean/) runs on CPU too | Visual geolocalization demo with ground truth |
| A Jetson | [XFeat](../catalog/repos/verlab__accelerated_features.md) ([card](integration-cards/verlab__accelerated_features.md)) + [Isaac ROS Visual SLAM](../catalog/resources/isaac-ros-visual-slam-docs.md) | Built for constrained hardware |
| Crazyflies | [cflib](../catalog/repos/bitcraze__crazyflie-lib-python.md) + [Loco Positioning](../catalog/resources/bitcraze-loco-positioning.md) | Indoor GNSS-denied testbed with UWB in a day |
| A BlueROV-class vehicle | [BlueOS](../catalog/repos/bluerobotics__blueos.md) + [dvl-python](../catalog/repos/waterlinked__dvl-python.md) | Extensions are Docker images; DVL protocol is simple |
| Only a DEM and Python | [terrain-heightmap-pf](../samples/terrain-heightmap-pf/) (numpy, real GLO-30) or the stdlib [TRN PF sample](../samples/terrain-relative-nav-pf/) + [Rasterio](../catalog/repos/rasterio__rasterio.md) ([card](integration-cards/rasterio__rasterio.md)) | Real terrain, measured error vs distance |
| Only Python and a filter book | [Kalman and Bayesian Filters in Python](../catalog/repos/rlabbe__kalman-and-bayesian-filters-in-python.md) + [FilterPy](../catalog/repos/rlabbe__filterpy.md) ([card](integration-cards/rlabbe__filterpy.md)) | Fastest onboarding to estimation |

## By capability

### Autopilot, SITL and vehicle link

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| Autopilot for GNSS-loss experiments | [ArduPilot](../catalog/repos/ardupilot__ardupilot.md) ([card](integration-cards/ardupilot__ardupilot.md)) - EKF3 source switching ([docs](../catalog/resources/ardupilot-ekf3-sources.md)), Lua scripting without a fork | [PX4](../catalog/repos/px4__px4-autopilot.md) ([card](integration-cards/px4__px4-autopilot.md)) - EKF2 external vision and flow, BSD license | [Paparazzi](../catalog/repos/paparazzi__paparazzi.md) - fit marked low; smaller ecosystem for this use | GPL-3.0; alt: BSD-3 |
| Simulator for UAS | [Gazebo Sim](../catalog/repos/gazebosim__gz-sim.md) ([card](integration-cards/gazebosim__gz-sim.md)) with PX4 or [ardupilot_gazebo](../catalog/repos/ardupilot__ardupilot_gazebo.md) | [gym-pybullet-drones](../catalog/repos/learnsyslab__gym-pybullet-drones.md) ([card](integration-cards/learnsyslab__gym-pybullet-drones.md)) for control and swarm logic without photorealism | [AirSim](../catalog/repos/microsoft__airsim.md) - archived; source builds need an old Unreal. [Isaac Sim](../catalog/repos/isaac-sim__isaacsim.md) - RTX GPU and a lot of disk | Apache-2.0; alt: MIT |
| MAVLink scripting | [pymavlink](../catalog/repos/ardupilot__pymavlink.md) ([card](integration-cards/ardupilot__pymavlink.md)) | [MAVSDK-Python](../catalog/repos/mavlink__mavsdk-python.md) ([card](integration-cards/mavlink__mavsdk-python.md)) for missions and offboard (`pip install mavsdk-grpc`) | [DroneKit](../catalog/repos/dronekit__dronekit-python.md) - archived, breaks on recent Python | LGPL-3.0, generated code MIT; alt: BSD-3 |
| Link sharing between GCS and tools | [mavlink-router](../catalog/repos/mavlink-router__mavlink-router.md) ([card](integration-cards/mavlink-router__mavlink-router.md)) | [mavp2p](../catalog/repos/bluenviron__mavp2p.md) - single binary, no build | Pointing several clients at one UDP port without a router | Apache-2.0; alt: MIT |
| GCS | [QGroundControl](../catalog/repos/mavlink__qgroundcontrol.md) ([card](integration-cards/mavlink__qgroundcontrol.md)) prebuilt | [MAVProxy](../catalog/repos/ardupilot__mavproxy.md) ([card](integration-cards/ardupilot__mavproxy.md)) - write a module for custom alerts | QGC custom builds - Qt setup takes hours. [Mission Planner](../catalog/repos/ardupilot__missionplanner.md) on Linux/mac - Mono caveats | Apache-2.0 / GPL-3.0 dual; alt: GPL-3.0 |
| Custom nav-health messages | [MAVLink](../catalog/repos/mavlink__mavlink.md) dialect XML + regenerated bindings | STATUSTEXT with a fixed prefix for a quick hack | Repurposing unrelated common messages - confuses GCS and judges | unclear (NOASSERTION); alt: - |
| ROS 2 bridge to PX4 | [px4_ros_com](../catalog/repos/px4__px4_ros_com.md) ([card](integration-cards/px4__px4_ros_com.md)) + [px4_msgs](../catalog/repos/px4__px4_msgs.md) (matching branch) | [MAVROS](../catalog/repos/mavlink__mavros.md) ([card](integration-cards/mavlink__mavros.md)) - mind ENU/NED | Mismatched px4_msgs branch - messages silently mismatch | BSD-3; alt: BSD / GPL-3.0 / LGPL-3.0 |

### GNSS, integrity and interference

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| Live receiver monitoring | [pyubx2](../catalog/repos/semuconsulting__pyubx2.md) ([card](integration-cards/semuconsulting__pyubx2.md)) | [gpsd](../catalog/repos/gitlab.com__gpsd__gpsd.md) for NMEA and PPS timing | Parsing NMEA only - loses MON-RF and spoof flags | BSD-3; alt: no GitHub metadata (GitLab) |
| Bench view of C/N0 | [PyGPSClient](../catalog/repos/semuconsulting__pygpsclient.md) | [u-blox ubxlib](../catalog/repos/u-blox__ubxlib.md) for embedded | - | BSD-3-Clause; alt: Apache-2.0 |
| GNSS data analysis in Python | [gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md) ([card](integration-cards/stanford-navlab__gnss_lib_py.md)) | [georinex](../catalog/repos/geospace-code__georinex.md) for RINEX; [laika](../catalog/repos/commaai__laika.md) ([card](integration-cards/commaai__laika.md)) for corrections | [GNSSTk](../catalog/repos/sgl-ut__gnsstk.md) - C++, fit marked low for a hackathon | MIT; alt: MIT |
| RTK / post-processing | [RTKLIB demo5](../catalog/repos/rtklibexplorer__rtklib.md) ([card](integration-cards/rtklibexplorer__rtklib.md)) | [pygnssutils](../catalog/repos/semuconsulting__pygnssutils.md) ([card](integration-cards/semuconsulting__pygnssutils.md)) NTRIP client + [pyrtcm](../catalog/repos/semuconsulting__pyrtcm.md) | Upstream [RTKLIB](../catalog/repos/tomojitakasu__rtklib.md) - quiet since 2024; demo5 handles current receivers | BSD-2; alt: BSD-3 |
| Software receiver | [GNSS-SDR](../catalog/repos/gnss-sdr__gnss-sdr.md) ([card](integration-cards/gnss-sdr__gnss-sdr.md)) from distro packages | [SoftGNSS Python](../catalog/repos/perrysou__softgnss-python.md) for offline IQ learning | Building GNSS-SDR from source on day one - long build | GPL-3.0; alt: not stated |
| GPS signal simulation (cabled/file only) | [multi-sdr-gps-sim](../catalog/repos/mictronics__multi-sdr-gps-sim.md) - maintained, streams to several SDRs | [GPS-SDR-SIM](../catalog/repos/osqzss__gps-sdr-sim.md) ([card](integration-cards/osqzss__gps-sdr-sim.md)) to file, straight into GNSS-SDR | Any over-the-air transmission - illegal in most jurisdictions. GPS-SDR-SIM is archived | MIT; alt: MIT |
| Navigation message authentication | [OSNMAlib](../catalog/repos/algafix__osnma.md) ([card](integration-cards/algafix__osnma.md)); [osnma-authentication](../samples/osnma-authentication/) runs it on a real recording | [galileo-osnma](../catalog/repos/daniestevez__galileo-osnma.md) (Rust, embedded no_std) | [osnma_ublox](../catalog/repos/axelbjork__osnma_ublox.md) - archived, predates the public service | EUPL-1.2 (copyleft); alt: Apache-2.0 |
| OSNMA test signals | [OSNMA-SDR-SIM](../catalog/repos/haiyang-wong__osnma-sdr-sim.md) file sink | Live u-blox SFRBX | - | not stated; alt: - |
| Jamming detection from C/N0 | [gnss-interference-monitor](../samples/gnss-interference-monitor/) scorer on pyubx2 data (all 20 Jammertest 2024 attack slots alerted in [real-attack-replay](../samples/real-attack-replay/)); [GPSSpy](../catalog/repos/hoverflyhampton__gpsspy.md) as a method reference | [Android APIs](../catalog/resources/android-gnss-spoof-jam-detection.md) | Taking GPSSpy as a dependency - small 2021 codebase, GPL | GPL-3.0; alt: - |
| RAIM / fault detection | gnss_lib_py fault detection examples; solution separation + PL in [altpnt-integrity](../samples/altpnt-integrity/) (use v2: calibrated on measured error models) | [RAIM (MATLAB)](../catalog/repos/michaelbeechan__raim.md) as reference | [MAAST for ARAIM](../catalog/repos/stanford-gps-lab__maast_for_araim_2.md) - service-area availability tool, not a receiver-side detector | -; alt: not stated |
| Interference awareness from aircraft | [readsb](../catalog/repos/wiedehopf__readsb.md) ([card](integration-cards/wiedehopf__readsb.md)) + [pyModeS](../catalog/repos/junzis__pymodes.md) | [OpenSky API](../catalog/repos/openskynetwork__opensky-api.md) | Running both readsb and [dump1090](../catalog/repos/flightaware__dump1090.md) - pick one | GPL-3.0; alt: GPL-3.0 |
| Clock holdover and time monitoring | [linuxptp](../catalog/repos/nwtime__linuxptp.md) ([card](integration-cards/nwtime__linuxptp.md)), [chrony](../catalog/repos/gitlab.com__chrony__chrony.md) ([card](integration-cards/gitlab.com__chrony__chrony.md)); holdover what-if in [timing-holdover](../samples/timing-holdover/); guide [timing-resilience.md](timing-resilience.md) | [gpsd](../catalog/repos/gitlab.com__gpsd__gpsd.md) for PPS | Trusting GNSS time without a second source | GPL-2.0; alt: GPL-2.0 |
| Direction finding | [KrakenSDR DoA](../catalog/repos/krakenrf__krakensdr_doa.md) ([card](integration-cards/krakenrf__krakensdr_doa.md)) + [interference-geolocation-to-tak](../samples/interference-geolocation-to-tak/) | Power-based localization from many cheap receivers: [jammer-sensor-network](../samples/jammer-sensor-network/); [heimdall DAQ](../catalog/repos/krakenrf__heimdall_daq_fw.md) for custom DF | Hand-rolled coherent multi-SDR sync in 48h | GPL-3.0; alt: GPL-3.0 |

### Inertial and fusion

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| INS simulation / what-if | [pyins](../catalog/repos/nmayorov__pyins.md) | [gnss-ins-sim](../catalog/repos/aceinna__gnss-ins-sim.md) ([card](integration-cards/aceinna__gnss-ins-sim.md)) | - | MIT; alt: MIT |
| GNSS/INS loosely coupled on real data | [KF-GINS](../catalog/repos/i2nav-whu__kf-gins.md) ([card](integration-cards/i2nav-whu__kf-gins.md)) | [OB_GINS](../catalog/repos/i2nav-whu__ob_gins.md) same formats, side-by-side | [IC-GVINS](../catalog/repos/i2nav-whu__ic-gvins.md) - heavier ROS setup | GPL-3.0; alt: GPL-3.0 |
| Factor graph fusion | [GTSAM](../catalog/repos/borglab__gtsam.md) ([card](integration-cards/borglab__gtsam.md)) (pip, ImuFactor examples) | [navlie](../catalog/repos/decargroup__navlie.md) | [gtsam_gnss](../catalog/repos/taroz__gtsam_gnss.md) - needs author's GTSAM fork and MATLAB | BSD; alt: MIT |
| Simple EKF/UKF in Python | [FilterPy](../catalog/repos/rlabbe__filterpy.md) ([card](integration-cards/rlabbe__filterpy.md)) | [manif](../catalog/repos/artivis__manif.md) for Lie-group states | FilterPy for 3D attitude states - not Lie-group aware | MIT; alt: MIT |
| ROS 2 localization | [robot_localization](../catalog/repos/cra-ros-pkg__robot_localization.md) ([card](integration-cards/cra-ros-pkg__robot_localization.md)) | [MINS](../catalog/repos/rpng__mins.md) ([card](integration-cards/rpng__mins.md)) for multi-sensor with GNSS dropout demos | Double-counting velocities and REP-103/105 frame mistakes | Apache-2.0 (package.xml); alt: GPL-3.0 |
| Sensor dropout / plug-in fusion | [MaRS](../catalog/repos/aau-cns__mars_lib.md) | MINS | - | unclear (NOASSERTION); alt: - |
| AHRS | [x-io Fusion](../catalog/repos/xiotechnologies__fusion.md) ([card](integration-cards/xiotechnologies__fusion.md)) | [AHRS (Python)](../catalog/repos/mayitzin__ahrs.md) | - | MIT; alt: MIT |
| IMU noise calibration | [allan_variance_ros](../catalog/repos/ori-drs__allan_variance_ros.md) | [allan-variance (Python)](../catalog/repos/nmayorov__allan-variance.md) | [kalibr_allan](../catalog/repos/rpng__kalibr_allan.md) - archived | BSD-3-Clause; alt: MIT |
| Camera-IMU calibration | [Kalibr](../catalog/repos/ethz-asl__kalibr.md) via Docker, print AprilGrid ahead | [iKalibr](../catalog/repos/unsigned-long__ikalibr.md) | Building Kalibr natively - ROS 1 build pain | unclear (NOASSERTION); alt: unclear (NOASSERTION) |

### Vision, lidar, radar odometry

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| VIO | [OpenVINS](../catalog/repos/rpng__open_vins.md) ([card](integration-cards/rpng__open_vins.md)) - built-in simulator, ROS 1 and 2 | [Basalt](../catalog/repos/vladyslavusenko__basalt.md) - builds cleanly | [ORB-SLAM3](../catalog/repos/uz-slamlab__orb_slam3.md) ([card](integration-cards/uz-slamlab__orb_slam3.md)) if nobody has built it before - expect compile fixes. [SVO Pro](../catalog/repos/uzh-rpg__rpg_svo_pro_open.md) - ROS 1, dormant | GPL-3.0; alt: BSD-3-Clause |
| Visual SLAM with map reuse | [RTAB-Map](../catalog/repos/introlab__rtabmap.md) ([card](integration-cards/introlab__rtabmap.md)) - apt binaries, localization mode | ORB-SLAM3 | [VINS-Fusion](../catalog/repos/hkust-aerial-robotics__vins-fusion.md) without Docker - ROS 1 | BSD-3, default builds pull NC/GPL deps; alt: - |
| VIO on Jetson | [Isaac ROS Visual SLAM](../catalog/resources/isaac-ros-visual-slam-docs.md) | OpenVINS | - | -; alt: - |
| LiDAR odometry | [KISS-ICP](../catalog/repos/prbonn__kiss-icp.md) ([card](integration-cards/prbonn__kiss-icp.md)) - pip, runs on a bag in minutes | [FAST-LIO](../catalog/repos/hku-mars__fast_lio.md) ([card](integration-cards/hku-mars__fast_lio.md)) with IMU | [LIO-SAM](../catalog/repos/tixiaoshan__lio-sam.md) unless you have a 9-axis IMU and good extrinsics | MIT; alt: GPL-2.0 |
| LiDAR loop closure / relocalization | [KISS-SLAM](../catalog/repos/prbonn__kiss-slam.md) | [small_gicp](../catalog/repos/koide3__small_gicp.md) scan-to-map | FAST-LIO alone - no loop closure | MIT; alt: MIT |
| Radar odometry | [RIO](../catalog/repos/christopherdoer__rio.md) (4D mmWave) | [CFEAR](../catalog/repos/dan11003__cfear_radarodometry.md) (spinning radar) | Expecting ROS 2 - most radar tools here are ROS 1 | GPL-3.0; alt: GPL-3.0 |
| Trajectory evaluation | [evo](../catalog/repos/michaelgrupp__evo.md) ([card](integration-cards/michaelgrupp__evo.md)), as used in [relative-nav-benchmark](../samples/relative-nav-benchmark/) | [rpg_trajectory_evaluation](../catalog/repos/uzh-rpg__rpg_trajectory_evaluation.md) | Reporting error without alignment flags stated | GPL-3.0; alt: MIT |

### Absolute alt-PNT

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| Visual place retrieval (tiles) | [AnyLoc](../catalog/repos/anyloc__anyloc.md) ([card](integration-cards/anyloc__anyloc.md)); measured in [vpr-large-area](../samples/vpr-large-area/) (DINOv2 GeM averaged over 8 rotations beat AnyLoc-style VLAD on synthetic queries at 1/16 the index size) | [SALAD](../catalog/repos/serizba__salad.md) via torch.hub; [MixVPR](../catalog/repos/amaralibey__mixvpr.md) for lightweight | Skipping retrieval - [WildNav](../catalog/repos/tiers__wildnav.md) ([card](integration-cards/tiers__wildnav.md)) brute-force tile search is slow, and its SuperGlue dependency is non-commercial | BSD-3 code, VLAD vocab not stated; alt: GPL-3.0 |
| Feature matching | [LightGlue](../catalog/repos/cvg__lightglue.md) ([card](integration-cards/cvg__lightglue.md)) with ALIKED or DISK, not the SuperPoint default (NC weights) | [XFeat](../catalog/repos/verlab__accelerated_features.md) ([card](integration-cards/verlab__accelerated_features.md)) on CPU / edge | [RoMa](../catalog/repos/parskatt__roma.md) ([card](integration-cards/parskatt__roma.md)) as the main matcher - accurate but slow; use as top-1 verifier only | Apache-2.0, SuperPoint weights NC; alt: Apache-2.0 incl. weights |
| Matcher shoot-out | [vismatch](../catalog/repos/gmberton__vismatch.md) ([card](integration-cards/gmberton__vismatch.md)) | [VPR methods evaluation](../catalog/repos/gmberton__vpr-methods-evaluation.md) ([card](integration-cards/gmberton__vpr-methods-evaluation.md)) for retrieval | - | BSD-3 wrapper, per-matcher mixed, some NC; alt: MIT wrapper, per-model mixed |
| Visual geolocalization pipeline skeleton | [geoloc-license-clean](../samples/geoloc-license-clean/) (permissive weights; real frames fixed 1 of 5) or [visual-geolocalization-lightglue sample](../samples/visual-geolocalization-lightglue/) (SuperPoint, NC) | [UAVLocalization](../catalog/repos/hmf21__uavlocalization.md) | [gnss-denied-uav-geolocalization](../catalog/repos/yfs90__gnss-denied-uav-geolocalization.md) - check what is actually released first | -; alt: not stated |
| Night / thermal geolocalization | [thermal-geolocalization](../samples/thermal-geolocalization/) (ALIKED + LightGlue on real thermal frames vs RGB satellite, gated: 18 of 111 fixed, 0 false) | [satellite-thermal geo-localization](../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md) ([card](integration-cards/arplaboratory__satellite-thermal-geo-localization.md)) for learned retrieval; light-independent sources: celestial, terrain, MagNav rows below | Planning around satellite-thermal without gated dataset access approved; SGM weights are research-only | per the sample's licence table; alt: MIT code, HF weights not stated |
| Reference map building | [OpenDroneMap](../catalog/repos/opendronemap__odm.md) | [pystac-client](../catalog/repos/stac-utils__pystac-client.md) for open imagery | - | AGPL-3.0; alt: unclear (NOASSERTION) |
| Terrain-relative navigation | [terrain-heightmap-pf](../samples/terrain-heightmap-pf/) (heightmap PF + TERCOM on real GLO-30), [blind-flight-bench](../samples/blind-flight-bench/) for radar-altimeter-only; [Rasterio](../catalog/repos/rasterio__rasterio.md) ([card](integration-cards/rasterio__rasterio.md)) | [tercom_nav](../catalog/repos/mzahana__tercom_nav.md) ([card](integration-cards/mzahana__tercom_nav.md)) for ROS 2 + SITL; [python-tercom](../catalog/repos/alti3__python-tercom.md) ([card](integration-cards/alti3__python-tercom.md)) | MATLAB-only [TERCOM PF](../catalog/repos/sotostrk__tercom-via-particle-filter-uav-state-estimation-mae6760-project-.md) if the team is Python | BSD-3; alt: unclear (no LICENSE, package.xml Apache-2.0) |
| DEM download | [elevation](../catalog/repos/bopen__elevation.md) ([card](integration-cards/bopen__elevation.md)) | [Copernicus DEM on AWS](../catalog/resources/copernicus-dem-aws.md) direct COG reads | - | Apache-2.0, DEM terms per product; alt: - |
| Magnetic anomaly navigation | [MagNav.jl](../catalog/repos/mit-ai-accelerator__magnav.jl.md) ([card](integration-cards/mit-ai-accelerator__magnav.jl.md)) | [MagNavPy](../catalog/repos/manasp21__magnav.py.md) (verify against MagNav.jl) | Small multirotor MagNav without compensation - platform noise dominates | public domain code, data restricted; alt: not stated |
| Celestial | [cedar-solve](../catalog/repos/smroid__cedar-solve.md) ([card](integration-cards/smroid__cedar-solve.md)) git tag v0.6.0, the maintained tetra3 fork; [celestial-star-tracker](../samples/celestial-star-tracker/) (40 / 40 real star images solved, position error budget) | [tetra3](../catalog/repos/esa__tetra3.md) ([card](integration-cards/esa__tetra3.md)) - install from git, pin NumPy < 2 | [deep_learning_celnav](../catalog/repos/gregtozzi__deep_learning_celnav.md) - exploratory, fit low | Apache-2.0; alt: Apache-2.0 |
| LEO signals of opportunity | [LEOSPINE](../catalog/repos/xyangll__leospine.md) simulation | [UT Starlink signal simulator](../catalog/repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md) | Live Ku-band reception in 48h - needs LNB hardware; [Starlink LEO-PNT](../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md) claims unverified | MIT; alt: no GitHub metadata (GitLab) |
| UWB ranging | [Crazyflie firmware](../catalog/repos/bitcraze__crazyflie-firmware.md) + Loco; real-range filters in [swarm-coop-real-uwb](../samples/swarm-coop-real-uwb/) (MILUV) | [UWB software library](../catalog/repos/vladniculescu__uwb-software-library.md) | [uwb-localization](../catalog/repos/lijx10__uwb-localization.md) - ROS 1, fit low | GPL-3.0; alt: not stated |
| Pedestrian / dismounted | [dismounted-foot-ins](../samples/dismounted-foot-ins/) (stdlib; 2.35 m vs PyShoe's 2.51 m ARMSE on PyShoe's 36 hallway trials, one tuning; a fresh download gave 2.21 m, see the [evidence matrix](evidence-matrix.md#8-dismounted)) or [PyShoe](../catalog/repos/utiasstars__pyshoe.md) | [RoNIN](../catalog/repos/sachini__ronin.md) / [TLIO](../catalog/repos/cathias__tlio.md) | [zupt-aided-ins](../catalog/repos/hcarlsso__zupt-aided-ins.md) as a dependency - archived since 2021 (fine as reading) | not stated; alt: GPL-3.0 |

### Situational awareness and C2

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| TAK server | [OpenTAKServer](../catalog/repos/brian7704__opentakserver.md) ([card](integration-cards/brian7704__opentakserver.md)) | [GoATAK](../catalog/repos/kdudkov__goatak.md) ([card](integration-cards/kdudkov__goatak.md)) - web client for judges without ATAK | [FreeTAKServer](../catalog/repos/freetakteam__freetakserver.md) - activity slowed since 2024 | GPL-3.0; alt: AGPL-3.0 |
| CoT from Python | [PyTAK](../catalog/repos/snstac__pytak.md) ([card](integration-cards/snstac__pytak.md)) | [takproto](../catalog/repos/snstac__takproto.md) for protobuf | Writing an ATAK plugin - [ATAK-CIV](../catalog/repos/tak-product-center__atak-civ.md) SDK toolchain takes half a day | Apache-2.0; alt: MIT |
| CoT from Node | [node-CoT](../catalog/repos/dfpc-coe__node-cot.md) | - | [CloudTAK](../catalog/repos/dfpc-coe__cloudtak.md) full deploy - AWS-oriented, AGPL | MIT; alt: - |
| Vehicle to TAK | [mavlink-to-tak-cot sample](../samples/mavlink-to-tak-cot/) | [ADSBCOT](../catalog/repos/snstac__adsbcot.md) for aircraft | - | -; alt: Apache-2.0 |
| Drone detection (C-UAS, detect only) | [remote-id-to-tak](../samples/remote-id-to-tak/) (Remote ID decoder validated against opendroneid-core-c) | [cuas-classifiers](../samples/cuas-classifiers/) (radar UAV vs bird, DroneRF) | Interception or effector logic - out of scope | -; alt: - |
| Military symbology | [milsymbol](../catalog/repos/spatialillusions__milsymbol.md) ([card](integration-cards/spatialillusions__milsymbol.md)) | [MIL-STD-2525D](../catalog/resources/mil-std-2525d.md) reference | Hand-drawn icons - judges notice | MIT; alt: - |
| 2D web map (offline) | [MapLibre GL JS](../catalog/repos/maplibre__maplibre-gl-js.md) ([card](integration-cards/maplibre__maplibre-gl-js.md)) + [PMTiles](../catalog/repos/protomaps__pmtiles.md) ([card](integration-cards/protomaps__pmtiles.md)) | [Leaflet](../catalog/repos/leaflet__leaflet.md) | Online tile services at a venue with bad Wi-Fi | BSD-3; alt: BSD-2-Clause |
| Many tracks / heatmaps | [deck.gl](../catalog/repos/visgl__deck.gl.md) | [tar1090](../catalog/repos/wiedehopf__tar1090.md) for ADS-B | - | MIT; alt: unclear (NOASSERTION) |
| 3D picture | [CesiumJS](../catalog/repos/cesiumgs__cesium.md) ([card](integration-cards/cesiumgs__cesium.md)) | - | Default Cesium ion assets when offline - serve your own terrain ([cesium-terrain-builder](../catalog/repos/geo-data__cesium-terrain-builder.md)) | Apache-2.0, ion content separate terms; alt: - |
| Multi-target tracking / fusion | [Stone Soup](../catalog/repos/dstl__stone-soup.md) ([card](integration-cards/dstl__stone-soup.md)) ([sample](../samples/stone-soup-tracking/)) | [BoxMOT](../catalog/repos/mikel-brostrom__boxmot.md) for camera tracks | [pymht](../catalog/repos/erikliland__pymht.md) - fit low | MIT; alt: AGPL-3.0 |
| Geodesy and grids | [pyproj](../catalog/repos/pyproj4__pyproj.md) + [pymap3d](../catalog/repos/geospace-code__pymap3d.md) ([card](integration-cards/geospace-code__pymap3d.md)) | [GeographicLib](../catalog/repos/geographiclib__geographiclib.md); [mgrs](../catalog/repos/hobuinc__mgrs.md) for MGRS | Hand-rolled ECEF/ENU conversions | MIT; alt: MIT |
| Raster and DEM processing | [GDAL](../catalog/repos/osgeo__gdal.md) ([card](integration-cards/osgeo__gdal.md)) via conda or Docker | [QGIS](../catalog/repos/qgis__qgis.md) for analyst work | Mixing pip GDAL bindings with a system GDAL | MIT, GPL-linked builds copyleft; alt: GPL-2.0 |

### Planning and multi-agent

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| Air path planning | [OMPL](../catalog/repos/ompl__ompl.md) | [PythonRobotics](../catalog/repos/atsushisakai__pythonrobotics.md) grid planners over a rasterized DEM | - | unclear (NOASSERTION); alt: unclear (NOASSERTION) |
| Road routing (offline) | [Valhalla](../catalog/repos/valhalla__valhalla.md) - request-time costing | [OSRM](../catalog/repos/project-osrm__osrm-backend.md) | [OSMnx](../catalog/repos/gboeing__osmnx.md) offline - needs Overpass unless you load a local file | unclear (NOASSERTION); alt: BSD-2-Clause |
| Area coverage / survey | [Fields2Cover](../catalog/repos/fields2cover__fields2cover.md) | - | - | BSD-3-Clause; alt: - |
| Mission logic | [BehaviorTree.CPP](../catalog/repos/behaviortree__behaviortree.cpp.md) | [PlanSys2](../catalog/repos/plansys2__ros2_planning_system.md) | - | MIT; alt: Apache-2.0 |
| Task allocation | [CBBA (Python)](../catalog/repos/inmo-jang__consensus-based-bundle-algorithm.md) | [rmf_task](../catalog/repos/open-rmf__rmf_task.md) | - | MIT; alt: Apache-2.0 |
| UGV navigation | [Nav2](../catalog/repos/ros-navigation__navigation2.md) ([card](integration-cards/ros-navigation__navigation2.md)) | [CMU exploration env](../catalog/repos/hongbiaoz__autonomous_exploration_development_environment.md) | [CARLA](../catalog/repos/carla-simulator__carla.md) without a decent GPU | mixed LGPL-2.1 / Apache / BSD; alt: not stated |
| Multi-UAV framework | [Aerostack2](../catalog/repos/aerostack2__aerostack2.md) | [MRS UAV system](../catalog/repos/ctu-mrs__mrs_uav_system.md) | - | BSD-3-Clause; alt: BSD-3-Clause |
| Swarm sim | [Crazyswarm2](../catalog/repos/imrclab__crazyswarm2.md) | [gym-pybullet-drones](../catalog/repos/learnsyslab__gym-pybullet-drones.md) ([card](integration-cards/learnsyslab__gym-pybullet-drones.md)) | [EGO-Swarm](../catalog/repos/zju-fast-lab__ego-planner-swarm.md) as a localization demo - assumes reliable comms (interesting to degrade, though) | MIT; alt: MIT |
| Multi-robot SLAM | [Swarm-SLAM](../catalog/repos/mistlab__swarm-slam.md) | [CSLAM](../catalog/repos/lajoiepy__cslam.md) | [Kimera-Multi](../catalog/repos/mit-spark__kimera-multi.md) - index repo, heavy, fit low | MIT; alt: MIT |

### Maritime and underwater

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| AIS decode | [pyais](../catalog/repos/m0r13n__pyais.md); spoofing detectors in [maritime-ais-spoofing](../samples/maritime-ais-spoofing/) | [noaadata](../catalog/repos/schwehr__noaadata.md) | - | MIT; alt: unclear (NOASSERTION) |
| Live AIS from RF | [AIS-catcher](../catalog/repos/jvde-github__ais-catcher.md) | - | - | GPL-3.0; alt: - |
| Marine data bus | [Signal K Server](../catalog/repos/signalk__signalk-server.md) | NMEA over UDP with [pynmeagps](../catalog/repos/semuconsulting__pynmeagps.md) | - | Apache-2.0; alt: BSD-3-Clause |
| Chart display | [OpenCPN](../catalog/repos/opencpn__opencpn.md) | MapLibre web map | Writing an OpenCPN plugin in 48h - feed it NMEA instead | GPL-2.0; alt: - |
| USV simulation | [VRX](../catalog/repos/osrf__vrx.md); stdlib own-ship nav + radar-chart matching in [usv-gnss-denied-nav](../samples/usv-gnss-denied-nav/) | [MOOS-IvP](../catalog/repos/moos-ivp__moos-ivp.md) with pMarineViewer | [Aeolus Ocean](../catalog/repos/aavek__aeolus-ocean.md) - fit low | Apache-2.0; alt: unclear (NOASSERTION) |
| Collision avoidance sim | [NTNU colav-simulator](../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) | - | - | MIT; alt: - |
| UUV simulation | [Stonefish](../catalog/repos/patrykcieslak__stonefish.md) | [HoloOcean ROS](../catalog/repos/byu-holoocean__holoocean-ros.md) (needs GPU) | [UUV Simulator](../catalog/repos/uuvsimulator__uuv_simulator.md) - archived. [DAVE](../catalog/repos/field-robotics-lab__dave.md) - ROS 1, half-day setup | GPL-3.0; alt: MIT |
| DVL / acoustic positioning | [dvl-python](../catalog/repos/waterlinked__dvl-python.md) + [USBL simulator](../catalog/repos/maximilian-nitsch__usbl-simulator.md) | [AUV estimator](../catalog/repos/alliwong__auvestimator.md) as a template only | [dvl-a50-ros-driver](../catalog/repos/waterlinked__dvl-a50-ros-driver.md) - archived, ROS 1 | not stated; alt: not stated |

### LLM agents

| Capability | Default | Alternative | Avoid because | License (default; alt) |
|---|---|---|---|---|
| MCP server pattern | The hub's stdlib server ([llm-agent-usage](../samples/llm-agent-usage/)); for vehicle tools with a geofence and dry run, [llm-mission-agent](../samples/llm-mission-agent/) | - | Letting an agent call vehicle commands without a human confirmation step and an allowlist | -; alt: - |
| Vehicle tools for the agent | [pymavlink](../catalog/repos/ardupilot__pymavlink.md) ([card](integration-cards/ardupilot__pymavlink.md)) against SITL | [MAVSDK-Python](../catalog/repos/mavlink__mavsdk-python.md) ([card](integration-cards/mavlink__mavsdk-python.md)) | Running against real hardware during the event | LGPL-3.0, generated code MIT; alt: BSD-3 |
| Sim plus foundation models | [GRID playground](../catalog/repos/genrobo__grid-playground.md) | Gazebo + your own tool layer | Relying on GRID's hosted sim without checking account requirements first | unclear (NOASSERTION); alt: - |
| Querying this hub from an agent | `claude mcp add navigation-index -- python3 /abs/path/tools/mcp_server.py` | `python3 tools/query.py` | - | -; alt: - |
