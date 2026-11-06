# 6. Autopilots and C2

After this chapter you can run PX4 or ArduPilot in simulation, inject your own position
source over MAVLink, configure the estimator to switch away from GNSS, and push your
vehicle's position and detections onto a TAK common operating picture.

Prev: [Absolute alternative PNT](05-absolute-alt-pnt.md) | Next: [Maps, geodesy and planning](07-maps-geodesy-planning.md) | [Primer index](README.md)

## The two open autopilots

- **[PX4](../../catalog/repos/px4__px4-autopilot.md)** - Dronecode flight stack on NuttX with
  a uORB pub/sub bus. Its estimator is EKF2, which fuses IMU, GNSS, baro, magnetometer,
  optical flow, external vision and range
  ([EKF2 guide](../../catalog/resources/px4-ekf2-tuning-guide.md)).
- **[ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)** - Copter, Plane, Rover (incl.
  boats) and Sub. Its estimator is EKF3, with one core per IMU and automatic lane switching
  ([EKF overview](../../catalog/resources/ardupilot-ekf-overview.md)).

Both run in software-in-the-loop (SITL) with Gazebo, which is where you should spend the
whole hackathon unless you have flight approval
([PX4 simulation](../../catalog/resources/px4-simulation-docs.md),
[ArduPilot SITL](../../catalog/resources/ardupilot-sitl-docs.md)).

Typical architecture for an alt-nav build:

```
camera / IMU / SDR  =>  companion computer (your VIO, map matching, detector)
                    =>  MAVLink or ROS 2  =>  autopilot EKF  =>  controller
                    =>  telemetry  =>  GCS (QGroundControl / Mission Planner) and TAK
```

## Getting your position into the autopilot

MAVLink is the lightweight binary protocol between autopilots, ground stations and
companion computers ([MAVLink guide](../../catalog/resources/mavlink-developer-guide.md)).
The hooks for alternative PNT are in the common message set
([common.xml reference](../../catalog/resources/mavlink-common-messages.md)):

| Message | Use |
|---------|-----|
| `VISION_POSITION_ESTIMATE` | Pose from VIO/SLAM in a local frame |
| `ODOMETRY` | Full pose and velocity with covariance (preferred) |
| `VISION_SPEED_ESTIMATE` | Velocity only |
| `GPS_INPUT` | Present your fix as if it were a GNSS receiver (e.g. absolute map-matching output) |

ArduPilot documents the accepted messages and frames
([non-GPS position via MAVLink](../../catalog/resources/ardupilot-dev-mavlink-nongps-position.md));
PX4 documents EKF2_EV_* parameters and ENU vs NED handling
([external position](../../catalog/resources/px4-external-position-estimation.md)). Frame
transforms are the usual failure point
([ArduPilot ROS VIO tutorial](../../catalog/resources/ardupilot-ros-vio-tracking-camera.md)).

## Switching sources when GNSS goes bad

- **ArduPilot EKF3** supports up to three source sets (`EK3_SRCn_*`) with per-axis choice of
  position, velocity and yaw source, switchable in flight by RC switch, Lua script or
  MAVLink ([source selection](../../catalog/resources/ardupilot-ekf3-sources.md),
  [GPS / non-GPS transitions](../../catalog/resources/ardupilot-gps-non-gps-transitions.md)).
  A Lua script that watches GNSS health and your detector, then switches sets, is a solid
  hackathon deliverable.
- **PX4 EKF2** uses innovation tests to reject inconsistent aiding and documents aiding
  modes; recent summit talks cover non-GNSS aiding and "reset by fusion"
  ([EKF2 tuning guide](../../catalog/resources/px4-ekf2-tuning-guide.md),
  [Riseborough 2020](../../catalog/resources/riseborough-px4-state-estimation-2020.md),
  [PX4 Developer Summit](../../catalog/resources/px4-developer-summit.md)).
- Full menu of ArduPilot GPS-free sources: optical flow, beacons, wheel encoders, VIO,
  motion capture, external nav
  ([Non-GPS navigation](../../catalog/resources/ardupilot-non-gps-navigation-docs.md)).

## C2 links and their security

- **MAVLink 2 signing** adds a SHA-256 based signature and timestamp to resist injection and
  replay. It authenticates, it does not encrypt, and key distribution is up to you
  ([MAVLink 2 signing](../../catalog/resources/mavlink-2-signing.md)).
- **Mission protocol** uploads waypoints, geofences and rally points
  ([mission protocol](../../catalog/resources/mavlink-mission-protocol.md)).
- **NATO interoperability**: STANAG 4586 defines five levels of interoperability from
  receiving payload data up to full flight control
  ([STANAG 4586 overview](../../catalog/resources/stanag-4586-overview.md)).
- **Cyber-resilience of autopilots** is treated as part of autonomy in Navy challenges
  ([HACKtheMACHINE](../../catalog/resources/onr-hackthemachine-unmanned-2021.md)).

## Situational awareness: CoT and TAK

Cursor on Target (CoT) is a small XML event schema: what (a hierarchical `type` string
derived from military symbology), where (point with error estimates), when
([CoT NDIA briefing](../../catalog/resources/cot-niessen-ndia-2008.md),
[MITRE CoT guide](../../catalog/resources/mitre-cot-users-guide.md)). TAK (ATAK, WinTAK,
TAK Server) carries CoT as XML or protobuf over UDP multicast (mesh) or TCP/TLS
(streaming) ([TAK protocol](../../catalog/resources/tak-protocol-takproto.md)). Pick type
codes from [cot-types](../../catalog/resources/cot-types-collection.md); render symbols per
[MIL-STD-2525](../../catalog/resources/mil-std-2525-overview.md) /
[APP-6](../../catalog/resources/app-6-joint-military-symbology.md). Register on
[TAK.gov](../../catalog/resources/tak-gov.md) early; SDK downloads are behind an account.

A useful honesty point for any SA display: CoT points carry circular and linear error
fields. Fill them from your filter covariance instead of leaving defaults, so an operator
can see when your position is degraded.

## Defensive counter-UAS detection

Within this hub's scope: detecting and tracking drones, not defeating them.

- **Cooperative:** Remote ID broadcasts drone and control-station position under ASTM F3411
  ([FAA Remote ID](../../catalog/resources/faa-remote-id.md),
  [MAVLink Open Drone ID](../../catalog/resources/mavlink-opendroneid-microservice.md)).
- **Protocol analysis:** DJI DroneID was shown to be unencrypted and decodable with an SDR
  ([NDSS 2023](../../catalog/resources/ndss-2023-dji-droneid.md)).
- **Vision/thermal tracking:** [Anti-UAV benchmark](../../catalog/resources/anti-uav-benchmark-paper.md).
- **Track fusion:** [Stone Soup](../../catalog/resources/stone-soup-docs.md) for multi-target
  tracking with defensible metrics.

## Failure modes under EW

- **Link loss:** the vehicle must have a sane onboard behaviour (hold, return on dead
  reckoning, land). Do not assume the GCS can intervene.
- **GNSS failsafe triggers on spoofed-but-healthy-looking data:** failsafes key on fix loss,
  which spoofing does not cause. Add your own plausibility check.
- **Source switching transients:** switching EKF source sets can jump the estimate; test it in
  SITL with a scripted outage.
- **Unsigned MAVLink** accepts injected commands from anyone on the link.
- **TAK displays** show whatever position they receive; a spoofed vehicle position propagates
  to every operator.

## Learn it

1. [PX4 simulation docs](../../catalog/resources/px4-simulation-docs.md) or [ArduPilot SITL](../../catalog/resources/ardupilot-sitl-docs.md) - get a vehicle flying in Gazebo.
2. [MAVLink developer guide](../../catalog/resources/mavlink-developer-guide.md) and [common messages](../../catalog/resources/mavlink-common-messages.md).
3. [ArduPilot Non-GPS navigation](../../catalog/resources/ardupilot-non-gps-navigation-docs.md) and [GPS / Non-GPS transitions](../../catalog/resources/ardupilot-gps-non-gps-transitions.md).
4. [PX4 EKF2 guide](../../catalog/resources/px4-ekf2-tuning-guide.md) and [PX4 VIO](../../catalog/resources/px4-visual-inertial-odometry.md).
5. [MAVLink 2 signing](../../catalog/resources/mavlink-2-signing.md).
6. [CoT developer guide](../../catalog/resources/butler-cot-developer-guide.md), [TAK protocol](../../catalog/resources/tak-protocol-takproto.md), [PyTAK docs](../../catalog/resources/pytak-docs.md).
7. [Riseborough PX4 state estimation 2020](../../catalog/resources/riseborough-px4-state-estimation-2020.md) and [ArduPilot DevCon 2024](../../catalog/resources/ardupilot-devcon-kaga-2024.md) - estimator design from the authors.
8. [STANAG 4586 overview](../../catalog/resources/stanag-4586-overview.md) for NATO framing.

## Build with it

- [PX4](../../catalog/repos/px4__px4-autopilot.md) with [px4_ros_com](../../catalog/repos/px4__px4_ros_com.md) / [px4_msgs](../../catalog/repos/px4__px4_msgs.md).
- [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md) with [ardupilot_gazebo](../../catalog/repos/ardupilot__ardupilot_gazebo.md) and [ardupilot_ros](../../catalog/repos/ardupilot__ardupilot_ros.md).
- [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md) and [pymavlink](../../catalog/repos/ardupilot__pymavlink.md) - script the vehicle and send position messages.
- [vision_to_mavros](../../catalog/repos/thien94__vision_to_mavros.md) - external pose to MAVLink.
- [mavlink-router](../../catalog/repos/mavlink-router__mavlink-router.md) - fan telemetry out to several consumers.
- [QGroundControl](../../catalog/repos/mavlink__qgroundcontrol.md) and [Mission Planner](../../catalog/repos/ardupilot__missionplanner.md) - ground stations.
- [PyTAK](../../catalog/repos/snstac__pytak.md), [takproto](../../catalog/repos/snstac__takproto.md), [OpenTAKServer](../../catalog/repos/brian7704__opentakserver.md), [FreeTAKServer](../../catalog/repos/freetakteam__freetakserver.md) - TAK side.
- [milsymbol](../../catalog/repos/spatialillusions__milsymbol.md) - MIL-STD-2525 / APP-6 symbols in JS.
- [Open Drone ID receiver (Android)](../../catalog/repos/opendroneid__receiver-android.md) and [opendroneid-core-c](../../catalog/repos/opendroneid__opendroneid-core-c.md) - Remote ID.
- [Stone Soup](../../catalog/repos/dstl__stone-soup.md) - tracking and data association.

Samples in this hub: [`samples/mavlink-to-tak-cot`](../../samples/mavlink-to-tak-cot/),
[`samples/vio-to-mavlink-bridge`](../../samples/vio-to-mavlink-bridge/),
[`samples/stone-soup-tracking`](../../samples/stone-soup-tracking/).

Related concepts: [autopilot](../../catalog/concepts/autopilot.md), [MAVLink and GCS](../../catalog/concepts/mavlink-gcs.md),
[situational awareness](../../catalog/concepts/situational-awareness.md), [counter-UAS](../../catalog/concepts/counter-uas.md),
[tracking](../../catalog/concepts/target-tracking.md).
