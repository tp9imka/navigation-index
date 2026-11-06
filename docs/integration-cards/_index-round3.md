# Integration cards - round 3: TAK feeds, ROS 2 bridges, fusion, simulators

<!-- about: repo:snstac/adsbcot, repo:snstac/takproto, repo:alphafox02/dragonsync, repo:krakenrf/heimdall_daq_fw, repo:eprosima/micro-xrce-dds-agent, repo:ardupilot/ardupilot_ros, repo:locusrobotics/fuse, repo:i2nav-whu/ob_gins, repo:haiyang-wong/osnma-sdr-sim, repo:spencerfolk/rotorpy, repo:luxonis/depthai-core, repo:smroid/cedar-solve -->

What each card gives you in a hackathon. All 12 were written from READMEs, docs, source files and issues read through the GitHub API. None of these repos was installed or run for the cards, and every snippet is marked "not run".

## Situational awareness and RF (TAK picture)

- [adsbcot](snstac__adsbcot.md) - readsb/dump1090 JSON or Beast feed => CoT aircraft tracks through PyTAK. The CoT error circle comes from the NACp category number, not metres, and NIC is never read, so don't use it as a GNSS-integrity signal.
- [takproto](snstac__takproto.md) - CoT XML => TAK Protocol v1 protobuf (mesh and stream framing) and protobuf parsing (`xml2proto`, `parse_proto`). There is no protobuf => XML function. The library is MIT but the bundled `.proto` files are GPL-3.0.
- [DragonSync](alphafox02__dragonsync.md) - decoded Remote ID / DJI DroneID on ZMQ => drone, pilot and home CoT. The default upstream decoder is a closed non-commercial binary. The API port 8088 clashes with TAK server defaults.
- [Heimdall DAQ firmware](krakenrf__heimdall_daq_fw.md) - coherent IQ from the 5 KrakenSDR tuners, served over shared memory or TCP 5000/5001, under [KrakenSDR DoA](krakenrf__krakensdr_doa.md). The no-hardware synthetic mode is effectively broken (issue #16).
- Sample: [GNSS jammer geolocation to TAK](../../samples/interference-geolocation-to-tak/) - KrakenSDR-format bearings => stdlib triangulation and Stone Soup PF/UKF => CoT point plus 95% ellipse (run, with output).

## ROS 2 bridges and fusion

- [Micro XRCE-DDS Agent](eprosima__micro-xrce-dds-agent.md) - PX4 uORB and ArduPilot DDS => ROS 2. `master` is v3, while PX4 v1.18 expects an XRCE v2 agent, so pin v2.4.x. ArduPilot uses the `micro_ros_agent` wrapper on port 2019.
- [ardupilot_ros](ardupilot__ardupilot_ros.md) - Humble example of Cartographer lidar SLAM => EKF3 external odometry over DDS, plus Nav2. Odometry is read only from `/ap/tf` (open issue #24).
- [fuse](locusrobotics__fuse.md) - plugin factor-graph fusion with a fixed-lag smoother in Ceres. It has no Humble branch, and all shipped models are 2D.
- [OB_GINS](i2nav-whu__ob_gins.md) - offline sliding-window GNSS/INS optimizer on the same file formats as [KF-GINS](i2nav-whu__kf-gins.md). It has a built-in GNSS outage switch. Needs a Ceres version with `ceres::Manifold`. GPL-3.0.

## Simulation, sensors and alternative PNT

- [OSNMA-SDR-SIM](haiyang-wong__osnma-sdr-sim.md) - Galileo E1/E5b IQ file generator with OSNMA replayed from 4 recorded days. It has no licence. `usrp=0` means transmit, so file output and cabled tests only.
- [RotorPy](spencerfolk__rotorpy.md) - pure-Python multirotor sim with IMU, mocap, wind and a gymnasium env. It has no GNSS sensor model.
- [depthai-core](luxonis__depthai-core.md) - C++ core of DepthAI v3 (see also [depthai](luxonis__depthai.md)). BasaltVIO and RTAB-Map run on the host and are off by default in source builds. Telemetry is on by default.
- [cedar-solve](smroid__cedar-solve.md) - tetra3 fork for star plate solving (compare [tetra3](esa__tetra3.md)). PyPI 0.5.1 predates the NumPy 2 fix, and the `Pillow<9` pin limits it to Python 3.10 or older.
