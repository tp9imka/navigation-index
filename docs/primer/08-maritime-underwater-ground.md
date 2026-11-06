# 8. Maritime, underwater, ground and dismounted

After this chapter you know how navigation changes off the drone: what ships broadcast and
how spoofing shows up in it, how vehicles navigate underwater where no radio reaches, how
ground robots and pedestrians dead-reckon, and which open stacks cover each domain.

Prev: [Maps, geodesy and planning](07-maps-geodesy-planning.md) | Next: [Evaluation and datasets](09-evaluation-and-datasets.md) | [Primer index](README.md)

## Maritime surface

**Data on a ship.** Position, heading, speed and AIS flow between devices as NMEA 0183
sentences ([NMEA 0183](../../catalog/resources/nmea-0183-standard.md)) or NMEA 2000 PGNs on
a CAN bus ([NMEA 2000](../../catalog/resources/nmea-2000-standard.md)). Neither is
authenticated. Signal K wraps marine data as JSON over REST and WebSocket, easy to consume
from any language ([Signal K spec](../../catalog/resources/signalk-spec.md)).

**AIS** is a VHF TDMA broadcast where ships report identity, position, course and speed
([ITU-R M.1371](../../catalog/resources/itu-r-m1371-ais.md)). It is unauthenticated, so AIS
anomalies are the main public signal of GNSS manipulation at sea
([Windward 2025](../../catalog/resources/windward-2025-maritime-stress-test.md)). C4ADS used
impossible AIS tracks to map thousands of spoofing events around Russia, Crimea and Syria
([Above Us Only Stars](../../catalog/resources/c4ads-above-us-only-stars.md)). A practical
hackathon detector: decode AIS with an RTL-SDR, then flag ships whose reported positions
jump, cluster on one point, or violate their own speed.

**Resilient maritime PNT.** Backups at sea include eLoran and R-Mode, which reuses existing
radio beacons and coastal infrastructure and has been tested in the jammed Baltic
([39C3 talk](../../catalog/resources/39c3-baltic-jammer-r-mode.md),
[MarRINav webinar](../../catalog/resources/ion-webinar-marrinav.md)). Marine radar plus
charts is the traditional independent cross-check.

**Autonomy at sea.** Collision regulations (COLREGs) define give-way and stand-on duties;
rules 13 to 17 drive most USV avoidance logic, and they are written for human judgement,
which makes formalisation hard ([COLREGs](../../catalog/resources/imo-colregs.md)).
MOOS-IvP is the long-running behaviour-based autonomy stack, taught in MIT 2.680
([MIT 2.680](../../catalog/resources/mit-2680-marine-autonomy.md),
[MOOS-IvP docs](../../catalog/resources/moos-ivp-docs.md)).

## Underwater

GNSS does not penetrate water, so an AUV or ROV combines:

- **INS + DVL.** A Doppler velocity log measures velocity over the seabed; integrated with
  attitude, it gives dead reckoning
  ([Water Linked DVL docs](../../catalog/resources/waterlinked-docs.md)).
- **Depth sensor** - absolute in one axis.
- **Acoustic positioning** (USBL/LBL) from a surface reference that does have GNSS
  ([Water Linked Underwater GPS](../../catalog/resources/waterlinked-docs.md)).
- **Sonar odometry / SLAM** against the seabed or structures
  ([sonar-SLAM](../../catalog/repos/jake3991__sonar-slam.md), [DISO](../../catalog/repos/senseroboticslab__diso.md)).
- **Surfacing** for a GNSS fix, which exposes the vehicle.

ArduSub feeds external DVL and USBL positions into its EKF via MAVLink
([ArduSub docs](../../catalog/resources/ardusub-docs.md)). Simulate with HoloOcean, which
models sonar, DVL, IMU and depth sensors ([HoloOcean docs](../../catalog/resources/byu-holoocean-docs.md)).

## Ground vehicles

Ground robots have extra constraints a drone lacks: wheels (odometry), contact with the
ground (non-holonomic motion, zero-velocity when stopped) and terrain that decides where
they can go.

- **Fusion:** wheel odometry + IMU + GNSS with robot_localization's EKF and `navsat_transform`
  is the standard ROS 2 recipe ([Nav2 robot_localization guide](../../catalog/resources/nav2-robot-localization-setup-guide.md),
  [Nav2 GPS tutorial](../../catalog/resources/nav2-gps-navigation-tutorial.md)).
  Datum and frame setup trips people up.
- **Map-based localization:** NDT scan matching plus EKF in Autoware
  ([Autoware docs](../../catalog/resources/autoware-docs.md)).
- **Contact-aided estimation** for legged robots adds leg kinematics to an invariant EKF
  ([Hartley et al.](../../catalog/resources/hartley-contact-aided-inekf.md)).
- **Off-road** semantics differ sharply from urban data
  ([RELLIS-3D](../../catalog/resources/rellis3d-paper.md)); traversability can be learned
  online from pre-trained features ([Wild Visual Navigation](../../catalog/resources/wild-visual-navigation-paper.md)).
- **Urban canyons** degrade GNSS through blockage and multipath
  ([UrbanLoco](../../catalog/resources/polyu-urbanloco-dataset.md)).

## Dismounted and indoor

- **Foot-mounted INS** uses the moment the foot is still each step as a zero-velocity
  update (ZUPT) that resets velocity drift ([PyShoe](../../catalog/repos/utiasstars__pyshoe.md)).
- **Learned pedestrian inertial odometry** from a phone IMU
  ([RoNIN](../../catalog/resources/ronin-paper.md), [TLIO](../../catalog/resources/tlio-paper.md)).
- **UWB** anchors for indoor positioning (chapter 5).

## Space (brief)

Space navigation in this hub covers spacecraft pose estimation and star trackers
([Kelvins SPEED+](../../catalog/resources/kelvins-pose-estimation-2021.md),
[tetra3](../../catalog/repos/esa__tetra3.md)) and LEO signals (chapter 5). Space-segment
security is part of assured PNT ([Hack-A-Sat](../../catalog/resources/afrl-hack-a-sat-2022.md)).

## Failure modes under EW

- **Maritime:** spoofed GNSS propagates into AIS, ECDIS and every NMEA consumer on an
  unauthenticated bus. Cross-check with radar, compass and log speed.
- **AIS itself** can be spoofed or switched off; absence of a track is not absence of a ship.
- **Underwater:** RF-based threats barely apply, but surfacing for GNSS and acoustic
  positioning are exposure points; DVL loses bottom lock over deep water.
- **Ground:** wheel slip, GNSS multipath in streets and under trees, and spoofed GNSS
  dragging `navsat_transform`.
- **Dismounted:** consumer phones in areas with defensive spoofing get wrong location and
  time ([The Record](../../catalog/resources/therecord-ukraine-spoofing-civilian-phones.md)).

## Learn it

1. [Signal K spec](../../catalog/resources/signalk-spec.md) and [ITU-R M.1371 (AIS)](../../catalog/resources/itu-r-m1371-ais.md).
2. [C4ADS Above Us Only Stars](../../catalog/resources/c4ads-above-us-only-stars.md) - spoofing OSINT method.
3. [39C3: Terrestrial navigation in the Baltic](../../catalog/resources/39c3-baltic-jammer-r-mode.md).
4. [MIT 2.680 marine autonomy](../../catalog/resources/mit-2680-marine-autonomy.md) and [MOOS-IvP docs](../../catalog/resources/moos-ivp-docs.md).
5. [COLREGs](../../catalog/resources/imo-colregs.md).
6. [ArduSub docs](../../catalog/resources/ardusub-docs.md) and [Water Linked docs](../../catalog/resources/waterlinked-docs.md).
7. [Nav2 GPS tutorial](../../catalog/resources/nav2-gps-navigation-tutorial.md), [robot_localization docs](../../catalog/resources/robot-localization-docs.md), [ROSCon UK 2025 state estimation workshop](../../catalog/resources/nav2-roscon-uk-2025-state-estimation-workshop.md).
8. [Coursera Self-Driving Cars specialization](../../catalog/resources/coursera-self-driving-cars-specialization.md) and [Autoware docs](../../catalog/resources/autoware-docs.md).

## Build with it

- [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md) and [pyais](../../catalog/repos/m0r13n__pyais.md) - receive and decode AIS.
- [Signal K Server](../../catalog/repos/signalk__signalk-server.md) and [OpenCPN](../../catalog/repos/opencpn__opencpn.md) - marine data hub and chartplotter.
- [ArduPilot (Rover boat / ArduSub)](../../catalog/repos/ardupilot__ardupilot.md) and [BlueOS](../../catalog/repos/bluerobotics__blueos.md).
- [MOOS-IvP](../../catalog/repos/moos-ivp__moos-ivp.md), [VRX](../../catalog/repos/osrf__vrx.md), [NTNU colav-simulator](../../catalog/repos/ntnu-itk-autonomous-ship-lab__colav-simulator.md) - surface autonomy and collision avoidance.
- [Stonefish](../../catalog/repos/patrykcieslak__stonefish.md), [HoloOcean ROS](../../catalog/repos/byu-holoocean__holoocean-ros.md), [Ping Python](../../catalog/repos/bluerobotics__ping-python.md), [sonar-SLAM](../../catalog/repos/jake3991__sonar-slam.md) - underwater.
- [robot_localization](../../catalog/repos/cra-ros-pkg__robot_localization.md), [Nav2](../../catalog/repos/ros-navigation__navigation2.md), [CARLA](../../catalog/repos/carla-simulator__carla.md), [elevation_mapping_cupy](../../catalog/repos/leggedrobotics__elevation_mapping_cupy.md) - ground.
- [PyShoe](../../catalog/repos/utiasstars__pyshoe.md), [RoNIN](../../catalog/repos/sachini__ronin.md), [TLIO](../../catalog/repos/cathias__tlio.md) - pedestrian.

Related concepts: [maritime](../../catalog/concepts/maritime-nav.md), [underwater](../../catalog/concepts/underwater-nav.md),
[ground vehicle](../../catalog/concepts/ground-vehicle-nav.md), [indoor and pedestrian](../../catalog/concepts/indoor-pedestrian.md),
[space](../../catalog/concepts/space-nav.md).
