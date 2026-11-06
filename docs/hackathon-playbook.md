# Hackathon playbook: navigation and PNT under GNSS denial

For a team going into a navigation-themed hackathon that may have a military or defense
track. Everything here is framed as defensive: keeping position, navigation and timing
trustworthy, detecting interference, and giving operators an honest picture. Weapon
terminal guidance and targeting are out of scope (see
[DoDD 3000.09](../catalog/resources/dodd-3000-09-autonomy-weapons-2023.md) for where that
line sits, and [Policy, export control and ethics](../catalog/concepts/policy-ethics.md)).

Companion doc: [reference-stacks.md](reference-stacks.md) - "if you only have X, use Y".

Contents:

1. [What judges reward](#1-what-judges-reward)
2. [Problem space map](#2-problem-space-map)
3. [Project ideas (24-48h)](#3-project-ideas-24-48h)
4. [Reference architectures](#4-reference-architectures)
5. [48h execution plan template](#5-48h-execution-plan-template)
6. [Pre-hackathon prep checklist](#6-pre-hackathon-prep-checklist)

---

## 1. What judges reward

Pulled from past challenge designs, funder problem statements and post-mortems in the hub.
The common thread: a working, measured, honest prototype on a realistic scenario beats a
clever slide.

| Judges reward | Evidence in the hub | What it means for your demo |
|---|---|---|
| A working prototype on a realistic simulated system | [ONR HACKtheMACHINE Unmanned](../catalog/resources/onr-hackthemachine-unmanned-2021.md) - Navy judges reward working prototypes on realistic simulated systems | Run against PX4 or ArduPilot SITL, real recorded data, or real hardware. Not a notebook with synthetic sine waves. |
| Measured accuracy, not coverage | [DARPA SubT](../catalog/resources/darpa-subt-challenge.md) scored accurate localization of reported artifacts; [Kelvins SPEC2019](../catalog/resources/kelvins-spec2019-paper.md) shows how ESA scores a nav competition | Show one number with ground truth: ATE in metres via [evo](../catalog/repos/michaelgrupp__evo.md), OSPA via [Stone Soup](../catalog/resources/stone-soup-docs.md), error vs time during an outage. |
| Multi-sensor fusion, not one magic sensor | [EDF-2024 drone navigation challenge](../catalog/resources/edf-2024-drone-navigation-challenge.md) - "multi-sensor fusion, not a single sensor, is the ask"; DARPA [ASPN](../catalog/resources/darpa-aspn-briefing-2019.md) pushes plug-and-play all-source fusion | Architect for sensor dropout and plug-in sources even if you only finish two. Show the filter surviving one source going away. |
| Integrity and plausibility over raw accuracy | [OPSGROUP 2024 report](../catalog/resources/opsgroup-gps-spoofing-final-report-2024.md) - "is my position plausible?" checks matter more than accuracy; [FAA SAFO 24002](../catalog/resources/faa-safo-24002-gnss-disruptions.md) - hybrid GPS/INS can also be corrupted by spoofing | Detect and flag before you fuse. A spoofing alarm that fires and a filter that refuses the bad fix is the strongest 30-second demo moment. |
| Detect, respond, recover vocabulary | [DHS Resilient PNT Conformance Framework](../catalog/resources/dhs-resilient-pnt-conformance-framework.md) (four resilience levels), [NISTIR 8323](../catalog/resources/nist-ir-8323-pnt-profile.md) (identify/protect/detect/respond/recover, GNSS as untrusted input) | Put your features on a slide mapped to these words. Judges from government recognise them. |
| Holdover time as the value metric | [DIU Transition of Quantum Sensing](../catalog/resources/diu-transition-quantum-sensing-2024.md) - value is reduced drift and longer holdover without GPS | Report "minutes until error exceeds N metres" with and without your aid. |
| Deployable, testable, dual-use | [NATO DIANA challenges](../catalog/resources/nato-diana-10-challenges-2025.md), [DIANA cohort feature](../catalog/resources/nato-diana-secure-comms-navigation.md) - selection favors deployable, testable dual-use products | Name the civil use (aviation, shipping, timing) next to the defense one. Show it runs on hardware a unit could buy. |
| Rapid field relevance, frontline users | [Brave1-NATO competition](../catalog/resources/brave1-nato-counter-drone-ew-competition.md), [Ukrainian anti-drone hackathon](../catalog/resources/militarnyi-anti-drone-hackathon-ukraine.md), [Kyiv Independent on EW cycles](../catalog/resources/kyiv-independent-invisible-war-ew.md) - adaptation cycles measured in weeks | Show reconfigurability: config-driven sources, thresholds, frequency plans. Say how a field user retunes it. |
| Sim-to-real honesty | [Kelvins SPEED+](../catalog/resources/kelvins-pose-estimation-2021.md) scored the synthetic-to-hardware gap; [Swift](../catalog/resources/swift-champion-drone-racing-nature.md) used residual models from real data | If you only ran in sim, say so and show what breaks on real data. |
| Operator workflow and interop | [CERBERUS SubT win](../catalog/resources/cerberus-subt-final-paper.md) - field-hardening and operator workflow mattered as much as algorithms; [NeBula](../catalog/resources/nebula-costar-subt-paper.md) - reasoning over localization uncertainty improves decisions | Put the output on a map operators already use (TAK via CoT). Show uncertainty, not just a dot. |
| Lightweight onboard beats heavy | [MAVLab AlphaPilot win](../catalog/resources/mavlab-alphapilot-win-2019.md), [A2RL 2025](../catalog/resources/a2rl-2025-season.md) - university labs beat well-funded teams | Measure latency and compute. A CPU-real-time pipeline is a feature. |
| Governable, traceable AI | [DoD AI principles](../catalog/resources/dod-ai-ethical-principles-2020.md), [NATO AI principles](../catalog/resources/nato-ai-strategy-principles-2021.md) - judges ask how an AI component can be disengaged | Any learned or LLM component needs a log, a confidence, and an off switch with a safe fallback. |
| Compliance awareness | [Stony Brook ITAR/EAR guide](../catalog/resources/stonybrook-export-publicly-available.md), [EAR and open source](../catalog/resources/linux-foundation-ear-open-source.md), [EU 2021/821](../catalog/resources/eu-dual-use-regulation-2021-821.md) | Stay on public civil signals and published methods. Never radiate GNSS signals; cabled or shielded only. One slide line on this pre-empts the question. |
| Skepticism toward unverified claims | [Vermeer optical navigation report](../catalog/resources/militarnyi-vermeer-optical-navigation.md) - vendor claims not independently tested; [RUSI Meatgrinder](../catalog/resources/rusi-meatgrinder-2023.md) - loss figures are contested | Cite numbers with their caveat. Overclaiming in front of practitioners loses points. |

Pitch framing sources: [CSIS Space Threat Assessment 2025](../catalog/resources/csis-space-threat-assessment-2025.md),
[EASA SIB 2022-02](../catalog/resources/easa-sib-2022-02-gnss-outages.md),
[EASA/IATA plan 2025](../catalog/resources/easa-iata-gnss-interference-plan-2025.md),
[UK PNT growth response](../catalog/resources/uk-pnt-growth-government-response-2025.md),
[GAO-21-320SP](../catalog/resources/gao-21-320sp-gps-alternatives.md). Recent hackathon
framing: [EUDIS Defence Hackathon 2025](../catalog/resources/eudis-defence-hackathon-2025.md),
[DASA RF sensing and PNT](../catalog/resources/dasa-advanced-rf-sensing-pnt-2022.md).

---

## 2. Problem space map

### 2.1 Threat model: GNSS denial and deception

| Threat | What happens | Observable symptoms | Detection cues you can compute in a hackathon | Sources |
|---|---|---|---|---|
| Jamming (denial) | Noise swamps the signal; receiver loses lock | C/N0 drops across all satellites, AGC changes, fix lost, ADS-B NIC/NACp falls | u-blox MON-RF jamming indicator via [pyubx2](../catalog/repos/semuconsulting__pyubx2.md); C/N0 statistics ([GPSSpy](../catalog/repos/hoverflyhampton__gpsspy.md)); ADS-B integrity ([GPSJam](../catalog/resources/gpsjam-org.md)) | [SKYbrary](../catalog/resources/skybrary-gnss-jamming-spoofing.md), [EASA SIB](../catalog/resources/easa-sib-2022-02-gnss-outages.md) |
| Spoofing (deception) | Counterfeit signals capture the receiver; position or time is pushed | Fix stays "good" but is wrong; jumps; time offsets; all satellites with similar C/N0; disagreement with INS or second receiver | Pseudorange residual / RAIM checks ([gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md), [RAIM](../catalog/repos/michaelbeechan__raim.md)); INS innovation gating; OSNMA auth failure ([OSNMAlib](../catalog/repos/algafix__osnma.md)); u-blox NAV-STATUS spoof flag | [Psiaki and Humphreys survey](../catalog/resources/psiaki-humphreys-2016-gnss-spoofing-detection.md), [Rados 2024 review](../catalog/resources/rados-2024-jamming-spoofing-detection-review.md), [Kreizis ION ITM 2025](../catalog/resources/kreizis-ion-itm-2025-spoofing.md) |
| Meaconing (rebroadcast) | Real signals re-transmitted with delay | Consistent but offset position/time | Same as spoofing; multi-receiver geometry ([Hendeby talk](../catalog/resources/ion-webinar-hendeby.md), [Rothmaier talk](../catalog/resources/ion-webinar-rothmaier.md)) | [Jammertest](../catalog/resources/jammertest-norway.md) test catalogue |
| Hybrid-solution corruption | GPS/INS blend absorbs spoofed fixes | INS "agrees" with spoofer after slow drag-off | Innovation tests with tight gates, independent heading/velocity source | [FAA SAFO 24002](../catalog/resources/faa-safo-24002-gnss-disruptions.md) |
| After-effects | Downstream functions stay wrong after GNSS returns | Terrain warning, clocks, logs remain corrupted | Re-validation logic on GNSS recovery, not just on loss | [OPSGROUP 2024](../catalog/resources/opsgroup-gps-spoofing-final-report-2024.md) |
| Collateral from defensive spoofing | Own-side protection spoofing hits civilian devices | Phones show wrong location and time | Any consumer-grade stack must tolerate wrong GNSS | [The Record](../catalog/resources/therecord-ukraine-spoofing-civilian-phones.md) |
| Timing attacks | Time push breaks networks and crypto that depend on GNSS time | Clock steps, PPS jumps | Holdover clock comparison, [gpsd](../catalog/repos/gitlab.com__gpsd__gpsd.md) PPS monitoring | [Timing concept](../catalog/concepts/timing.md), [TPN talk](../catalog/resources/ion-webinar-tpn.md) |

Geography and scale for the pitch: Baltic / Kaliningrad ([Spire](../catalog/resources/spire-gnss-interference-russia-kaliningrad.md),
[Defense News](../catalog/resources/defensenews-baltic-jamming-origins-2025.md), [39C3 talk](../catalog/resources/39c3-baltic-jammer-r-mode.md)),
Gulf and Hormuz at sea ([Windward 2025](../catalog/resources/windward-2025-maritime-stress-test.md)),
Russia and Syria via AIS ([C4ADS](../catalog/resources/c4ads-above-us-only-stars.md)),
Ukraine front ([RUSI](../catalog/resources/rusi-meatgrinder-2023.md), [IEEE Spectrum 2025](../catalog/resources/ieee-spectrum-ukraine-drones-ew-2025.md)).

### 2.2 Platforms

| Platform | Typical constraints | Best alt-PNT fits | Weak fits | Sim / test bed |
|---|---|---|---|---|
| Small UAS (multirotor, low altitude) | Low SWaP, MEMS IMU drifts in seconds, camera available, short flights | VIO, optical flow + rangefinder, visual geolocalization against orthophoto, radio ranging to beacons | MagNav (platform noise), TRN (flat terrain at low altitude, no radar altimeter) | [PX4](../catalog/repos/px4__px4-autopilot.md) / [ArduPilot](../catalog/repos/ardupilot__ardupilot.md) SITL + [Gazebo](../catalog/repos/gazebosim__gz-sim.md) |
| Fixed-wing (medium/high altitude, long range) | Long legs, higher speed, better IMU possible, altitude for imagery | Visual geolocalization, TRN with radar/laser altimeter, MagNav, celestial, LEO SoOp | VIO alone (scale and drift over long distance), UWB (range) | ArduPlane SITL, [terrain PF sample](../samples/terrain-relative-nav-pf/) |
| UGV | Wheel odometry, lidar, slow, cluttered | Wheel+IMU dead reckoning ([DRIFT](../catalog/repos/umich-curly__drift.md)), LiDAR SLAM / LIO, radar odometry in dust, map-matching to roads | Visual geolocalization from nadir (no nadir view), MagNav from vehicle noise | [Nav2](../catalog/repos/ros-navigation__navigation2.md), [CARLA](../catalog/repos/carla-simulator__carla.md), [CMU exploration env](../catalog/repos/hongbiaoz__autonomous_exploration_development_environment.md) |
| USV (surface) | GNSS spoofing heavy at sea, AIS is the public signal, radar common | Radar + chart matching, celestial, IMU + speed log dead reckoning, eLoran / R-Mode where available | Visual features over open water | [VRX](../catalog/repos/osrf__vrx.md), [MOOS-IvP](../catalog/repos/moos-ivp__moos-ivp.md), [OpenCPN](../catalog/repos/opencpn__opencpn.md) |
| UUV (underwater) | No GNSS at all below surface, acoustic comms only | DVL + IMU + depth, USBL/LBL acoustic fixes, sonar SLAM, terrain (bathymetry) matching | Anything RF or optical over range | [Stonefish](../catalog/repos/patrykcieslak__stonefish.md), [HoloOcean ROS](../catalog/repos/byu-holoocean__holoocean-ros.md), [DAVE](../catalog/repos/field-robotics-lab__dave.md) |
| Dismounted (person) | Phone or body-worn IMU, irregular motion, indoor/outdoor | Foot-mounted ZUPT INS ([PyShoe](../catalog/repos/utiasstars__pyshoe.md)), learned inertial odometry ([RoNIN](../catalog/repos/sachini__ronin.md), [TLIO](../catalog/repos/cathias__tlio.md)), UWB ranging, phone GNSS integrity checks | High-grade INS, camera-only (pocket) | [Android raw GNSS](../catalog/resources/android-raw-gnss-developer-guide.md), [GnssLogger](../catalog/repos/google__gps-measurement-tools.md) |
| Team / swarm | Many low-cost agents, intermittent comms | Inter-agent ranging (UWB), shared maps, one well-localized "anchor" agent | Anything needing reliable high-bandwidth comms | [Crazyswarm2](../catalog/repos/imrclab__crazyswarm2.md), [gym-pybullet-drones](../catalog/repos/learnsyslab__gym-pybullet-drones.md) |

### 2.3 Alt-PNT methods: which fits when

Maturity uses the hub's own labels (production / active-research / research-prototype /
educational) for the best open implementation, not the field as a whole.

| Method | Works when | Fails when | Sensors | Open maturity | Repos |
|---|---|---|---|---|---|
| INS dead reckoning (holdover) | Short outages; good IMU; fresh calibration | Long outages with MEMS IMU (error grows fast); poor bias estimate | IMU (+ baro, magnetometer) | production | [pyins](../catalog/repos/nmayorov__pyins.md), [gnss-ins-sim](../catalog/repos/aceinna__gnss-ins-sim.md), [KF-GINS](../catalog/repos/i2nav-whu__kf-gins.md), [allan_variance_ros](../catalog/repos/ori-drs__allan_variance_ros.md) |
| Visual(-inertial) odometry | Textured scenes, good light, low-medium altitude | Night, fog, smoke, water, featureless terrain, fast rotation; drifts over km | Camera + IMU | production / active-research | [OpenVINS](../catalog/repos/rpng__open_vins.md), [ORB-SLAM3](../catalog/repos/uz-slamlab__orb_slam3.md), [VINS-Fusion](../catalog/repos/hkust-aerial-robotics__vins-fusion.md), [Basalt](../catalog/repos/vladyslavusenko__basalt.md) |
| Optical flow + rangefinder | Low altitude hover and slow flight over ground | Above rangefinder range, over water, low light | Flow sensor, lidar rangefinder | production (in autopilots) | [ArduPilot optical flow](../catalog/resources/ardupilot-optical-flow-setup.md), [PX4 optical flow](../catalog/resources/px4-optical-flow-docs.md) |
| Visual geolocalization (image-to-map) | Nadir/oblique camera, up-to-date reference imagery, distinctive terrain | Seasonal change, night (unless thermal), clouds, repetitive terrain, stale maps | Camera (RGB or thermal), reference orthophoto | research-prototype / active-research | [WildNav](../catalog/repos/tiers__wildnav.md), [AnyLoc](../catalog/repos/anyloc__anyloc.md), [LightGlue](../catalog/repos/cvg__lightglue.md), [UAV-VisLoc](../catalog/repos/intellisensing__uav-visloc.md), [satellite-thermal](../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md) |
| Terrain-relative navigation (TERCOM/TRN) | Rough terrain, altitude above ground available, good DEM | Flat terrain or sea, poor DEM resolution, altimeter noise over forest canopy | Radar/laser altimeter + baro + DEM | educational / research-prototype | [python-tercom](../catalog/repos/alti3__python-tercom.md), [tercom_nav](../catalog/repos/mzahana__tercom_nav.md), [TRN PF sample](../samples/terrain-relative-nav-pf/) |
| Magnetic anomaly navigation | Aircraft with compensated magnetometer, anomaly map coverage, higher altitude flight lines | Uncompensated platform noise, small drones near motors, poor map | Magnetometer(s) + INS | active-research | [MagNav.jl](../catalog/repos/mit-ai-accelerator__magnav.jl.md), [MagNavPy](../catalog/repos/manasp21__magnav.py.md), [AFIT data](../catalog/repos/afit-eeng-magnav__example-data.md) |
| LiDAR odometry / SLAM | Structured environments, UGV, low-altitude UAS | Open fields, fog/dust (degrades), long featureless corridors | Lidar + IMU | production | [FAST-LIO](../catalog/repos/hku-mars__fast_lio.md), [KISS-ICP](../catalog/repos/prbonn__kiss-icp.md), [LIO-SAM](../catalog/repos/tixiaoshan__lio-sam.md) |
| Radar odometry | Dust, smoke, fog, darkness | Sparse returns, multipath in clutter; fewer open tools | FMCW / 4D mmWave radar + IMU | research-prototype | [RIO](../catalog/repos/christopherdoer__rio.md), [CFEAR](../catalog/repos/dan11003__cfear_radarodometry.md), [MIMOSA](../catalog/repos/ntnu-arl__mimosa.md) |
| Celestial / star tracker | Clear night sky (or sky polarization by day), stable platform | Cloud cover, daylight for star cameras, vibration | Camera + level sensor + clock | production (attitude) | [tetra3](../catalog/repos/esa__tetra3.md), [cedar-solve](../catalog/repos/smroid__cedar-solve.md), [ccompass](../catalog/repos/benjaminpotter__ccompass.md) |
| Signals of opportunity (LEO Doppler, cellular) | Receiver can see LEO downlinks or cell towers; good ephemeris (TLE) | Hardware for Ku-band; signal structure unknown; TLE errors | SDR + antenna/LNB | research-prototype | [Starlink LEO-PNT](../catalog/repos/przemyslawpiekarski__starlink-leo-pnt.md), [LEOSPINE](../catalog/repos/xyangll__leospine.md), [UT Starlink sim](../catalog/repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md) |
| Radio ranging to beacons (UWB, LoRa) | You control the area: base, landing zone, indoor | Beacons jammed or not deployed; geometry poor with one beacon | UWB / LoRa radios | production (UWB indoor) | [Crazyflie firmware](../catalog/repos/bitcraze__crazyflie-firmware.md), [LPS node firmware](../catalog/repos/bitcraze__lps-node-firmware.md), [Hyams LoRa RTH](../catalog/resources/hyams-gps-denied-rth-lora-ranging.md) |
| GNSS authentication (OSNMA) | Galileo E1 visible; receiver outputs nav bits | Jamming (no signal at all); replay within key latency | Galileo-capable receiver | active-research | [OSNMAlib](../catalog/repos/algafix__osnma.md), [galileo-osnma (Rust)](../catalog/repos/daniestevez__galileo-osnma.md), [OSNMA-SDR-SIM](../catalog/repos/haiyang-wong__osnma-sdr-sim.md) |
| Cooperative localization | Several agents, inter-agent ranging or shared landmarks, some comms | Comms denied, all agents lose absolute reference at once | UWB / camera / lidar on each agent | research-prototype / active-research | [Swarm-SLAM](../catalog/repos/mistlab__swarm-slam.md), [CSLAM](../catalog/repos/lajoiepy__cslam.md), [swarm relative localization](../catalog/repos/eth-pbl__swarm-relative-localization.md), [UVDAR](../catalog/repos/ctu-mrs__uvdar_core.md) |
| Underwater DVL + acoustic fixes | Seabed in DVL range; USBL from surface vessel | Mid-water column (no bottom lock); acoustic multipath | DVL, IMU, depth, USBL | research-prototype | [dvl-python](../catalog/repos/waterlinked__dvl-python.md), [USBL simulator](../catalog/repos/maximilian-nitsch__usbl-simulator.md), [Stonefish](../catalog/repos/patrykcieslak__stonefish.md) |

Fusion frameworks underneath most of these: [GTSAM](../catalog/repos/borglab__gtsam.md),
[robot_localization](../catalog/repos/cra-ros-pkg__robot_localization.md),
[MINS](../catalog/repos/rpng__mins.md), [MaRS](../catalog/repos/aau-cns__mars_lib.md),
autopilot EKFs ([ArduPilot EKF3 source switching](../catalog/resources/ardupilot-ekf3-sources.md),
[PX4 EKF2](../catalog/resources/px4-ekf2-tuning-guide.md)).

---

## 3. Project ideas (24-48h)

Ordered roughly from safe to ambitious. Each idea says what runs, what you measure, and
what could sink it. "Cabled only" means any GNSS signal generation goes into a receiver
through a cable or shielded enclosure, never over the air.

### Quick picker

| # | Idea | Risk | Hardware needed | Platform |
|---|---|---|---|---|
| 1 | GNSS interference monitor => TAK overlay | low | u-blox receiver or Android phone | any |
| 2 | ADS-B-derived interference map for your region | low | RTL-SDR (optional) | air picture |
| 3 | AIS track-plausibility spoofing detector | low | none (RTL-SDR optional) | USV / maritime |
| 4 | Android raw GNSS spoofing detector | low-medium | Android phone (optional) | dismounted |
| 5 | INS holdover budget calculator | low | none | any |
| 6 | Nav-integrity incident reporter (LLM over flight logs) | low | none | UAS |
| 7 | MAVLink MCP server with guardrails | low-medium | none (SITL) | UAS |
| 8 | Authenticate-or-alarm pipeline with OSNMA | medium | none (u-blox optional) | any |
| 9 | Spoof-aware source switching in ArduPilot SITL | medium | none (SITL) | small UAS |
| 10 | VIO => PX4 GPS-free flight with measured drift | medium | none (SITL) | small UAS |
| 11 | Terrain-relative navigation over a real DEM | medium | none | fixed-wing |
| 12 | Maritime multi-source position integrity in Signal K | medium | none | USV |
| 13 | Radio-ranging return-to-home | medium | UWB or LoRa radios (optional) | small UAS |
| 14 | LLM agent that plans GNSS-denied routes | medium | none | UAS / UGV |
| 15 | Celestial heading and attitude backup | medium | camera (optional) | USV / fixed-wing |
| 16 | MagNav compensation sprint | medium-high | none | fixed-wing |
| 17 | UUV DVL + USBL navigation in sim | medium-high | none | UUV |
| 18 | Visual geolocalization fused with VO | high | laptop GPU | fixed-wing / UAS |
| 19 | Cooperative localization for a small team | high | none (sim) or Crazyflies | swarm |
| 20 | Real-time visual geolocalization on Jetson | high | Jetson + camera | UAS |

---

### 1. GNSS interference monitor => TAK overlay (safe)

- **Pitch:** A low-cost box (receiver + Pi) that watches GNSS health and drops a jamming/spoofing alert onto the team's TAK map within seconds.
- **Why it matters:** Interference awareness is the first layer of resilience ([NAVGUARD](../catalog/resources/edf21-navguard-factsheet.md) funds exactly this; [EASA/IATA plan](../catalog/resources/easa-iata-gnss-interference-plan-2025.md) calls for better civil-military sharing of interference data). Units need to know "GNSS here is not trustworthy" before they rely on it.
- **Stack:** [pyubx2](../catalog/repos/semuconsulting__pyubx2.md) (MON-RF jamming indicator, NAV-STATUS spoof flags, C/N0), [PyGPSClient](../catalog/repos/semuconsulting__pygpsclient.md) for bench viewing, [PyTAK](../catalog/repos/snstac__pytak.md) for CoT, [OpenTAKServer](../catalog/repos/brian7704__opentakserver.md) or [GoATAK](../catalog/repos/kdudkov__goatak.md) web client, [milsymbol](../catalog/repos/spatialillusions__milsymbol.md). Phone alternative: [Android detection APIs](../catalog/resources/android-gnss-spoof-jam-detection.md). Sample: [gnss-interference-monitor](../samples/gnss-interference-monitor/) (`ubx_monitor.py`, plus a scorer); CoT plumbing: [mavlink-to-tak-cot](../samples/mavlink-to-tak-cot/).
- **Data:** [Jammertest](../catalog/resources/jammertest-norway.md) participant recordings for replay; [multi-frequency spoofing dataset](../catalog/repos/s7am1na__gnss-spoofing-dataset.md).
- **Demo plan:** Replay a Jammertest log (or cabled GPS-SDR-SIM into the receiver) => monitor flags jamming, then spoofing => a hazard polygon with timestamp and confidence appears in TAK.
- **Stretch:** Several monitors => coarse emitter area by intersecting affected regions ([Defense News](../catalog/resources/defensenews-baltic-jamming-origins-2025.md) shows distributed monitors work).
- **Risk:** Live jamming not available at the venue; mitigate with replay. Thresholds tuned on one receiver model do not transfer.

### 2. ADS-B-derived interference map for your region

- **Pitch:** Reproduce [GPSJam](../catalog/resources/gpsjam-org.md) for a local area in near real time from your own 1090 MHz receiver plus open feeds, and push degraded cells to TAK.
- **Why it matters:** ADS-B is a free, existing sensor network for interference awareness ([Inside GNSS](../catalog/resources/insidegnss-adsb-interference-mapping.md), [Bellingcat toolkit](../catalog/resources/bellingcat-toolkit-gpsjam.md)); aircraft integrity reports reveal denial areas around conflict zones.
- **Stack:** [readsb](../catalog/repos/wiedehopf__readsb.md) on an RTL-SDR, [pyModeS](../catalog/repos/junzis__pymodes.md) for NIC/NACp, [OpenSky API](../catalog/repos/openskynetwork__opensky-api.md) for wider coverage, [ADSBCOT](../catalog/repos/snstac__adsbcot.md), [deck.gl](../catalog/repos/visgl__deck.gl.md) hex layer or [tar1090](../catalog/repos/wiedehopf__tar1090.md) colored by NIC. Sample: `adsb_area_map.py` in [gnss-interference-monitor](../samples/gnss-interference-monitor/) bins readsb snapshots with the GPSJam formula.
- **Data:** OpenSky historical state vectors; [Flightradar24 jamming map](../catalog/resources/fr24-gps-jamming-map.md) and GPSJam as cross-check.
- **Demo plan:** Pick a known day of Baltic interference ([Spire report](../catalog/resources/spire-gnss-interference-russia-kaliningrad.md)) => your map vs GPSJam side by side => live local feed running at the table.
- **Stretch:** Distinguish jamming (NIC drops) from spoofing (position jumps, impossible velocities) per aircraft.
- **Risk:** Empty cells mean no data, not no jamming (GPSJam FAQ point). Say so on the map legend. OpenSky anonymous access is rate-limited.

### 3. AIS track-plausibility spoofing detector

- **Pitch:** Flag ships whose AIS tracks are physically impossible (teleports, circles, many vessels at one point) as likely GNSS manipulation zones.
- **Why it matters:** At sea, AIS anomalies are the main public signal of GNSS manipulation ([Windward 2025](../catalog/resources/windward-2025-maritime-stress-test.md)); [C4ADS](../catalog/resources/c4ads-above-us-only-stars.md) mapped thousands of spoofing events this way.
- **Stack:** [pyais](../catalog/repos/m0r13n__pyais.md), [AIS-catcher](../catalog/repos/jvde-github__ais-catcher.md) for live RF, [Stone Soup](../catalog/repos/dstl__stone-soup.md) gating for "impossible given motion model", [OpenCPN](../catalog/repos/opencpn__opencpn.md) or [MapLibre](../catalog/repos/maplibre__maplibre-gl-js.md) display, [PyTAK](../catalog/repos/snstac__pytak.md) for CoT.
- **Data:** Public AIS TCP feeds or recorded NMEA; message definitions in [ITU-R M.1371](../catalog/resources/itu-r-m1371-ais.md).
- **Demo plan:** Replay a recorded feed => rule-based and motion-model detectors fire => clustered "suspected interference area" polygons with counts.
- **Stretch:** Separate AIS falsification by the vessel from GNSS spoofing of many vessels (clusters with common displacement point to spoofing).
- **Risk:** Finding a public feed with a known event inside 48h; pre-download one before the event.

### 4. Android raw GNSS spoofing detector

- **Pitch:** A notebook-then-app that flags spoofing on a phone from raw measurements: pseudorange residuals, clock jumps, C/N0 uniformity, GNSS vs IMU disagreement.
- **Why it matters:** Dismounted users carry phones; defensive spoofing already affects civilian devices ([The Record](../catalog/resources/therecord-ukraine-spoofing-civilian-phones.md)). Phone sensing needs no custom hardware ([Akos ION talk](../catalog/resources/ion-webinar-akos.md)).
- **Stack:** [gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md) (fault detection examples), [GnssLogger](../catalog/repos/google__gps-measurement-tools.md), [laika](../catalog/repos/commaai__laika.md) for corrections, [RAIM](../catalog/repos/michaelbeechan__raim.md) as reference logic. Sample for the RINEX/SPP baseline: [gnss-rinex-processing](../samples/gnss-rinex-processing/).
- **Data:** [Multi-frequency spoofing dataset](../catalog/repos/s7am1na__gnss-spoofing-dataset.md) (Android phones and watches under spoofing), [GSDC 2023](../catalog/resources/google-gsdc-2023.md) for clean baselines.
- **Demo plan:** Clean drive log => no alarms; spoofed log => alarm at the onset with time-to-detect and false-alarm rate on a plot.
- **Stretch:** Run live on a phone via the Android APIs and post an alert to TAK.
- **Risk:** Dataset labelling - verify scenario details in its README before trusting results. Phone raw-measurement quality varies by handset.

### 5. INS holdover budget calculator

- **Pitch:** "How long can we fly after GNSS goes away?" A tool that takes an IMU's noise figures and a mission profile and gives minutes-until-error-exceeds-N metres, with and without an aid (flow, baro, magnetometer, visual fixes every K seconds).
- **Why it matters:** Holdover time is the stated value metric for alt-PNT funding ([DIU quantum sensing](../catalog/resources/diu-transition-quantum-sensing-2024.md)). Planners need an honest number per IMU grade.
- **Stack:** [pyins](../catalog/repos/nmayorov__pyins.md), [gnss-ins-sim](../catalog/repos/aceinna__gnss-ins-sim.md), [allan-variance](../catalog/repos/nmayorov__allan-variance.md) for your own IMU, [KF-GINS](../catalog/repos/i2nav-whu__kf-gins.md) for real-data comparison. Sample: [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/).
- **Data:** KF-GINS bundled demo dataset; your own static IMU recording (record hours before the event).
- **Demo plan:** Pick MEMS vs tactical-grade profile => sliders for outage length and aiding rate => error envelope plot; validate one curve against KF-GINS with masked GNSS epochs.
- **Stretch:** Export the result as a mission-planning constraint ("re-acquire an absolute fix every X km").
- **Risk:** Low. Main trap is presenting simulated numbers as measured; label them.

### 6. Nav-integrity incident reporter (LLM over flight logs)

- **Pitch:** Feed an ArduPilot/PX4 log in; get a plain-language incident report: when GNSS degraded, what the EKF did, which sources it switched to, and a timeline mapped to NIST IR 8323 detect/respond/recover.
- **Why it matters:** Post-incident analysis is slow and expert-bound; reporting is the first pillar of the [EASA/IATA plan](../catalog/resources/easa-iata-gnss-interference-plan-2025.md). Traceability is a stated AI principle ([DoD](../catalog/resources/dod-ai-ethical-principles-2020.md)).
- **Stack:** [pymavlink](../catalog/repos/ardupilot__pymavlink.md) for DataFlash/tlog parsing, deterministic extractors for GPS status, EKF innovations and source changes, then an LLM that only narrates extracted facts with citations to log timestamps. Hub MCP template: [llm-agent-usage](../samples/llm-agent-usage/).
- **Data:** Logs from SITL runs with injected GPS faults (ideas 9 and 10 produce them; the [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/) and [ardupilot-ekf3-source-switch](../samples/ardupilot-ekf3-source-switch/) samples log GPS cuts).
- **Demo plan:** Two logs (clean, spoofed) => two reports; every claim links to a log line; a plot generated from the same extracted events.
- **Stretch:** Aggregate many logs into a fleet-level "where and when did we lose GNSS" map.
- **Risk:** LLM inventing events. Mitigate by making the LLM summarise a structured event list only, and checking every timestamp it cites exists.

### 7. MAVLink MCP server with guardrails

- **Pitch:** An MCP server that lets an LLM agent read vehicle state (position, EKF status, GNSS health, active nav sources) and propose missions, while any command that moves the vehicle requires explicit human confirmation and passes a geofence check.
- **Why it matters:** Operators will use language interfaces to C2 tools; governability ([NATO AI principles](../catalog/resources/nato-ai-strategy-principles-2021.md)) means the agent can be disengaged and cannot act on its own. Showing the guardrails is the point.
- **Stack:** [pymavlink](../catalog/repos/ardupilot__pymavlink.md) or [MAVSDK-Python](../catalog/repos/mavlink__mavsdk-python.md), [mavlink-router](../catalog/repos/mavlink-router__mavlink-router.md) to share the link with a GCS, [MAVLink signing](../catalog/resources/mavlink-2-signing.md), [mission protocol](../catalog/resources/mavlink-mission-protocol.md). MCP server pattern: the hub's own stdlib server in [llm-agent-usage](../samples/llm-agent-usage/).
- **Data:** ArduPilot SITL ([docs](../catalog/resources/ardupilot-sitl-docs.md)).
- **Demo plan:** In Claude Code or another MCP client: "what is the nav health?" => tool reads EKF/GNSS => agent proposes a return-to-launch on degraded GNSS => human approves in [QGroundControl](../catalog/repos/mavlink__qgroundcontrol.md) or a confirm prompt => vehicle executes in SITL. Show a refused command outside the geofence.
- **Stretch:** Tool that explains nav source configuration (EK3_SRC sets) in plain language and suggests a safer config, applied only on approval.
- **Risk:** Scope creep into autonomy. Keep write tools to an allowlist (mission upload, RTL, mode change) and log every tool call.

### 8. Authenticate-or-alarm pipeline with Galileo OSNMA

- **Pitch:** A receiver-side pipeline that marks each fix as authenticated, unauthenticated or failed, and refuses to pass failed fixes downstream.
- **Why it matters:** Authentication turns "trust GNSS" into "trust authenticated GNSS"; [NISTIR 8323](../catalog/resources/nist-ir-8323-pnt-profile.md) treats GNSS as an untrusted input.
- **Stack:** [OSNMA-SDR-SIM](../catalog/repos/haiyang-wong__osnma-sdr-sim.md) (file sink) => [GNSS-SDR](../catalog/repos/gnss-sdr__gnss-sdr.md) => [OSNMAlib](../catalog/repos/algafix__osnma.md). Live path: u-blox SFRBX into OSNMAlib. Specs: [OSNMA receiver guidelines](../catalog/resources/galileo-osnma-receiver-guidelines.md), [OSNMA SIS ICD](../catalog/resources/galileo-osnma-sis-icd.md).
- **Data:** Simulated IQ files; GSC public key and Merkle root ([GSC documents](../catalog/resources/gsc-programme-reference-documents.md)).
- **Demo plan:** Authentic file => green; tampered navigation message file => MAC failure => red alarm and downstream fix dropped.
- **Stretch:** Combine with a C/N0 jamming detector so the output distinguishes "denied" from "deceived".
- **Risk:** Toolchain plumbing (GNSS-SDR configs). Cabled or file-only: radiating GNSS signals is illegal in most jurisdictions. OSNMA does not help against jamming or all forms of replay; say so.

### 9. Spoof-aware source switching in ArduPilot SITL

- **Pitch:** A Lua script or companion process that detects spoofing (GNSS vs IMU/flow innovation, position jump vs plausible velocity) and switches EKF3 to a non-GNSS source set, then re-validates GNSS before switching back.
- **Why it matters:** Hybrid GPS/INS can be dragged off by a spoofer ([FAA SAFO 24002](../catalog/resources/faa-safo-24002-gnss-disruptions.md)); after-effects persist when GNSS returns ([OPSGROUP](../catalog/resources/opsgroup-gps-spoofing-final-report-2024.md)). Detect, respond and recover in one demo.
- **Stack:** [ArduPilot](../catalog/repos/ardupilot__ardupilot.md) with [EKF3 source selection](../catalog/resources/ardupilot-ekf3-sources.md) and [GPS / non-GPS transitions](../catalog/resources/ardupilot-gps-non-gps-transitions.md), [MAVProxy](../catalog/repos/ardupilot__mavproxy.md) module for operator alert, [pymavlink](../catalog/repos/ardupilot__pymavlink.md). Optionally a custom [MAVLink](../catalog/repos/mavlink__mavlink.md) dialect message for "spoofing detected". Sample: [ardupilot-ekf3-source-switch](../samples/ardupilot-ekf3-source-switch/) already flies a SITL source-set switch around a GPS cut - add the detector in front of it.
- **Data:** SITL with injected GPS position offsets or drift (use SITL's simulated GPS fault options; check current parameter names in the SITL docs).
- **Demo plan:** Mission in progress => slow position drag starts => detector fires within N seconds => source switch => vehicle holds course on flow/VIO => GNSS re-validated => switch back. Plot true vs estimated vs spoofed track.
- **Stretch:** Run the same detector against PX4 EKF2 ([tuning guide](../catalog/resources/px4-ekf2-tuning-guide.md)) to show it is autopilot-agnostic.
- **Risk:** Tuning thresholds so slow drag-offs are caught without false alarms. Pre-record a few fault scenarios before the event.

### 10. VIO => PX4 GPS-free flight with measured drift

- **Pitch:** Fly a PX4 SITL quad on a VIO pose feed with GPS disabled and report the drift per 100 m flown, versus GPS-aided baseline.
- **Why it matters:** VIO is the workhorse for small UAS in denied areas; vision-inertial estimation won GPS-free racing ([AlphaPilot UZH](../catalog/resources/alphapilot-uzh-paper.md)).
- **Stack:** [PX4](../catalog/repos/px4__px4-autopilot.md) + [Gazebo](../catalog/repos/gazebosim__gz-sim.md), [OpenVINS](../catalog/repos/rpng__open_vins.md) (has its own simulator), [MAVROS](../catalog/repos/mavlink__mavros.md) or the uXRCE-DDS bridge, [evo](../catalog/repos/michaelgrupp__evo.md). Docs: [PX4 external position](../catalog/resources/px4-external-position-estimation.md), [PX4 VIO](../catalog/resources/px4-visual-inertial-odometry.md). Samples: [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/) gives the no-aiding drift baseline (GPS cut via MAVSDK failure injection, drift numbers per phase); [vio-to-mavlink-bridge](../samples/vio-to-mavlink-bridge/) handles ENU/NED frames.
- **Data:** [EuRoC](../catalog/resources/ethz-euroc-mav-dataset.md) to validate VIO before closing the loop; [UZH-FPV](../catalog/resources/uzh-fpv-drone-racing-dataset.md) for aggressive motion.
- **Demo plan:** Square mission with GPS => same mission with GPS off and VIO in => ATE plot and number, plus a failure case (low texture world).
- **Stretch:** Add periodic absolute fixes (idea 18) to bound drift.
- **Risk:** Frame conventions (ENU/NED, body frames) eat hours. Use the sample's frame tests.

### 11. Terrain-relative navigation over a real DEM

- **Pitch:** Particle-filter TRN for a fixed-wing over real Copernicus terrain: biased INS plus radar altimeter profile => corrected position with uncertainty.
- **Why it matters:** Terrain does not jam. TRN is a classic aviation answer for long legs where imagery may fail (night, cloud).
- **Stack:** [TRN PF sample](../samples/terrain-relative-nav-pf/) (stdlib simulation, rasterio DEM loader), [Rasterio](../catalog/repos/rasterio__rasterio.md), [elevation](../catalog/repos/bopen__elevation.md) for tiles, [python-tercom](../catalog/repos/alti3__python-tercom.md) for batch correlation comparison, [tercom_nav](../catalog/repos/mzahana__tercom_nav.md) for ROS 2 + SITL.
- **Data:** [Copernicus DEM on AWS](../catalog/resources/copernicus-dem-aws.md) (no account needed).
- **Demo plan:** Fly the same route over rough and flat terrain => error stays bounded over rough, diverges over flat => show the correlation surface. The failure case is part of the honest pitch.
- **Stretch:** Feed the TRN fix into ArduPlane SITL as an external position.
- **Risk:** Low for the sim; moderate for the SITL integration. Altimeter noise model choice changes results a lot; state it.

### 12. Maritime multi-source position integrity in Signal K

- **Pitch:** A Signal K plugin that compares GNSS position against dead reckoning (heading + speed log), radar/chart cues or celestial fixes and raises a "GNSS suspect" alarm on the chart display.
- **Why it matters:** Hundreds of ships per day affected at peak in the Gulf ([Windward](../catalog/resources/windward-2025-maritime-stress-test.md)); terrestrial backups like R-Mode are being revived in the Baltic ([39C3 talk](../catalog/resources/39c3-baltic-jammer-r-mode.md), [MarRINav talk](../catalog/resources/ion-webinar-marrinav.md)).
- **Stack:** [Signal K Server](../catalog/repos/signalk__signalk-server.md) (sample data playback), [OpenCPN](../catalog/repos/opencpn__opencpn.md), [radar_pi](../catalog/repos/opencpn-radar-pi__radar_pi.md) for radar overlay, [pynmeagps](../catalog/repos/semuconsulting__pynmeagps.md) to inject a spoofed NMEA stream, [VRX](../catalog/repos/osrf__vrx.md) or [MOOS-IvP](../catalog/repos/moos-ivp__moos-ivp.md) for a simulated vessel.
- **Data:** Signal K sample data; your own spoofed NMEA generated with pynmeagps.
- **Demo plan:** Normal voyage => spoofed position drift injected => divergence from DR grows => alarm and DR position shown as the trusted one on the chart.
- **Stretch:** Add a celestial fix from [tetra3](../catalog/repos/esa__tetra3.md) (idea 15) as an independent absolute check.
- **Risk:** Low; the integration is mostly JSON plumbing. DR quality depends on the current/leeway model; keep it simple and say so.

### 13. Radio-ranging return-to-home

- **Pitch:** Two or three ground beacons and range measurements let a UAS get home when GNSS is jammed.
- **Why it matters:** Getting the platform back is the minimum resilience requirement; radio ranging is a cheap GNSS backup ([Hyams LoRa RTH](../catalog/resources/hyams-gps-denied-rth-lora-ranging.md)).
- **Stack:** ArduPilot EKF3 range-beacon fusion ([ArduPilot](../catalog/repos/ardupilot__ardupilot.md), [non-GPS navigation docs](../catalog/resources/ardupilot-non-gps-navigation-docs.md)) or Crazyflie UWB ([firmware](../catalog/repos/bitcraze__crazyflie-firmware.md), [Loco Positioning](../catalog/resources/bitcraze-loco-positioning.md)); [FilterPy](../catalog/repos/rlabbe__filterpy.md) for a standalone multilateration EKF.
- **Data:** [UTIL UWB TDoA dataset](../catalog/resources/util-uwb-dataset.md) with [tools](../catalog/repos/williamwenda__uwb_tdoa_dataset.md).
- **Demo plan:** Offline: multilateration EKF on UTIL with error vs ground truth. Online: SITL with simulated beacons => GPS off => RTH lands within X m.
- **Stretch:** Beacon geometry planner that tells the team where to place beacons for best accuracy along the return corridor.
- **Risk:** Beacons are RF and can be jammed too; frame it as one layer, not the answer.

### 14. LLM agent that plans GNSS-denied routes

- **Pitch:** An agent that takes an area, a known interference map and terrain, and proposes a route that keeps the vehicle where its alt-PNT works: textured ground for VIO and visual fixes, rough terrain for TRN, beacon coverage for ranging. It explains each choice and hands a MAVLink mission to a human for approval.
- **Why it matters:** Reasoning over localization uncertainty improves mission decisions ([NeBula](../catalog/resources/nebula-costar-subt-paper.md)). Planners today route for distance and threat; few route for navigability.
- **Stack:** Deterministic tools the agent calls: [Rasterio](../catalog/repos/rasterio__rasterio.md) terrain roughness, image texture score from orthophoto tiles ([pystac-client](../catalog/repos/stac-utils__pystac-client.md)), interference cells (idea 2 output or [GPSJam](../catalog/resources/gpsjam-org.md)), [OMPL](../catalog/repos/ompl__ompl.md) or a grid A* from [PythonRobotics](../catalog/repos/atsushisakai__pythonrobotics.md) for air, [Valhalla](../catalog/repos/valhalla__valhalla.md) / [OSMnx](../catalog/repos/gboeing__osmnx.md) for ground; output via [pymavlink](../catalog/repos/ardupilot__pymavlink.md) mission upload. MCP plumbing: [llm-agent-usage](../samples/llm-agent-usage/).
- **Data:** [Copernicus DEM](../catalog/resources/copernicus-dem-aws.md), Sentinel-2 or other open imagery via STAC.
- **Demo plan:** Same start/goal => shortest route vs navigability-aware route => fly both in SITL with GNSS off => compare position error at the goal.
- **Stretch:** Replan in flight when the monitor (idea 1) reports a new interference area.
- **Risk:** The LLM is decoration if the cost map does the work. Make the cost map the core, let the agent compose tools and explain, and keep the planner deterministic and testable.

### 15. Celestial heading and attitude backup

- **Pitch:** A sky camera plus [tetra3](../catalog/repos/esa__tetra3.md) gives jam-proof attitude and heading at night; with a level sensor and clock, a coarse position fix.
- **Why it matters:** No RF dependency at all; useful for ships and long-endurance aircraft as a cross-check on spoofed GNSS heading and position.
- **Stack:** [tetra3](../catalog/repos/esa__tetra3.md) ([docs](../catalog/resources/tetra3-docs.md)) or [cedar-solve](../catalog/repos/smroid__cedar-solve.md), [celestial-navigation](../catalog/repos/alinnman__celestial-navigation.md) for sight reduction, [ccompass](../catalog/repos/benjaminpotter__ccompass.md) for daytime polarization heading.
- **Data:** tetra3 sample images; your own night sky photos.
- **Demo plan:** Solve sample images => attitude; combine with timestamp and level => fix with error ellipse vs truth.
- **Stretch:** Feed heading into the Signal K integrity check (idea 12).
- **Risk:** Cloudy venue; bring pre-shot images. Position accuracy from a phone-grade level sensor is coarse; quote it honestly.

### 16. MagNav compensation sprint

- **Pitch:** Remove the aircraft's own magnetic field from magnetometer data (Tolles-Lawson plus a small learned residual) and show the improvement in map-matched navigation error.
- **Why it matters:** Magnetic anomaly navigation is a funded transition path ([DIU](../catalog/resources/diu-transition-quantum-sensing-2024.md)), and platform noise is the barrier ([DARPA RoQS](../catalog/resources/darpa-roqs-2024.md)). The challenge problem is compensation ([AFRL/MIT paper](../catalog/resources/afrl-magnav-challenge-2020.md)).
- **Stack:** [MagNav.jl](../catalog/repos/mit-ai-accelerator__magnav.jl.md) ([docs](../catalog/resources/magnav-jl-docs.md)), [MagNavPy](../catalog/repos/manasp21__magnav.py.md) for Python teams (verify against MagNav.jl), [lw-kong submission](../catalog/repos/lw-kong__magnav.md) as a reference. Sample: [magnav-quickstart](../samples/magnav-quickstart/).
- **Data:** [MagNav challenge data](../catalog/resources/magnav-challenge-site.md), [SGS flight data on Zenodo](../catalog/resources/magnav-sgs-flight-data.md), [AFIT example data](../catalog/repos/afit-eeng-magnav__example-data.md).
- **Demo plan:** Baseline Tolles-Lawson => + residual model => compensation RMSE and navigation error along a held-out flight line.
- **Stretch:** Explain why this does not transfer to a small multirotor (motor currents) and what sensor placement would change.
- **Risk:** Julia compile time and data download; do both before the event. Physics plus ML beats either alone, so do not skip the physics baseline.

### 17. UUV DVL + USBL navigation in sim

- **Pitch:** An EKF fusing DVL velocity, IMU and depth with sparse USBL fixes from a surface vessel; show drift growth between fixes and the effect of losing bottom lock.
- **Why it matters:** Underwater there is no GNSS at all; the same holdover-and-correct pattern applies to every denied domain.
- **Stack:** [Stonefish](../catalog/repos/patrykcieslak__stonefish.md), [USBL simulator](../catalog/repos/maximilian-nitsch__usbl-simulator.md), [dvl-python](../catalog/repos/waterlinked__dvl-python.md) message formats, [FilterPy](../catalog/repos/rlabbe__filterpy.md) or [GTSAM](../catalog/repos/borglab__gtsam.md); [ArduSub docs](../catalog/resources/ardusub-docs.md) and [BlueOS](../catalog/repos/bluerobotics__blueos.md) if you want an autopilot in the loop.
- **Data:** Simulated; [Water Linked docs](../catalog/resources/waterlinked-docs.md) for realistic noise and rates.
- **Demo plan:** Lawnmower survey => error vs time with fixes every N seconds => same with bottom-lock loss mid-run.
- **Stretch:** USBL fix scheduling: when should the surface vessel ping to keep error under X m.
- **Risk:** Simulator setup time (GPL build of Stonefish, or heavy HoloOcean install). Pick one before the event.

### 18. Visual geolocalization fused with VO

- **Pitch:** "Visual GPS": match downward camera frames against satellite tiles to get absolute fixes, and fuse them with visual odometry so drift stays bounded between fixes.
- **Why it matters:** Vision-based absolute positioning against reference imagery is being fielded on drones under jamming ([Militarnyi on Vermeer](../catalog/resources/militarnyi-vermeer-optical-nav-2025.md), with the caveat that vendor claims are untested).
- **Stack:** Retrieval with [AnyLoc](../catalog/repos/anyloc__anyloc.md) or [SALAD](../catalog/repos/serizba__salad.md) => verification with [LightGlue](../catalog/repos/cvg__lightglue.md) + RANSAC homography => fusion with VO, following [GeoAnchor](../catalog/repos/yusufgunel__geoanchor.md) as a blueprint. Compare matchers fast with [vismatch](../catalog/repos/gmberton__vismatch.md). Sample: [visual-geolocalization-lightglue](../samples/visual-geolocalization-lightglue/). Background: [WildNav paper](../catalog/resources/wildnav-gnss-free-uav-localization-2022.md), [AnyVisLoc benchmark](../catalog/repos/uav-avl__benchmark.md).
- **Data:** [UAV-VisLoc](../catalog/repos/intellisensing__uav-visloc.md) (pick one flight and its map), [VPAIR](../catalog/repos/aervisloc__vpair.md), [ALTO](../catalog/repos/metaslam__alto.md).
- **Demo plan:** VO-only track drifts => add geolocalization fixes => error vs ground truth plot drops and stays bounded; show one rejected bad match.
- **Stretch:** Night mode with [satellite-thermal geo-localization](../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md) (gated Hugging Face dataset; request access early).
- **Risk:** Brute-force tile search is slow - use retrieval to prune. Seasonal and altitude mismatch between drone frames and tiles; pick a flight with a matching map.

### 19. Cooperative localization for a small team

- **Pitch:** Three to five agents share inter-agent ranges and odometry; one agent with a good fix (or a known start) anchors the rest. Show team error stays bounded while individual dead reckoning drifts.
- **Why it matters:** Heterogeneous teams won SubT ([SubT](../catalog/resources/darpa-subt-challenge.md)); cooperative ranging reduces drift in UAV-UGV teams ([Gross ION talk](../catalog/resources/ion-webinar-gross.md)).
- **Stack:** [Crazyswarm2](../catalog/repos/imrclab__crazyswarm2.md) (sim works without hardware) or [gym-pybullet-drones](../catalog/repos/learnsyslab__gym-pybullet-drones.md); [swarm relative localization](../catalog/repos/eth-pbl__swarm-relative-localization.md) and [UWB software library](../catalog/repos/vladniculescu__uwb-software-library.md) for ranging; [GTSAM](../catalog/repos/borglab__gtsam.md) for a shared factor graph; [Swarm-SLAM](../catalog/repos/mistlab__swarm-slam.md) or [CSLAM](../catalog/repos/lajoiepy__cslam.md) if you have lidar/camera agents.
- **Data:** [NTU VIRAL](../catalog/repos/ntu-aris__ntu_viral_dataset.md) (drone with UWB), [MCD](../catalog/resources/mcd-multi-campus-dataset.md) (UWB + lidar), [SubT-MRS](../catalog/resources/cmu-subt-mrs-dataset.md) for multi-robot.
- **Demo plan:** Sim swarm with GNSS off => independent DR vs cooperative estimate => error per agent over time; then cut comms to one agent and show graceful degradation.
- **Stretch:** Comms-aware: degrade the link (packet loss) and show which agents to keep within range.
- **Risk:** Multi-robot SLAM stacks are heavy; a 2D range-plus-odometry factor graph in GTSAM is enough for 48h.

### 20. Real-time visual geolocalization on Jetson (ambitious)

- **Pitch:** Idea 18 running onboard: Jetson-class board, nadir camera, CPU/GPU-light matcher, fixes at a usable rate into the autopilot as an external position.
- **Why it matters:** Onboard and lightweight is what fields ([MAVLab](../catalog/resources/mavlab-alphapilot-win-2019.md) lesson); dependence on a datalink is itself a vulnerability under EW.
- **Stack:** [XFeat](../catalog/repos/verlab__accelerated_features.md) (real time on CPU) or [LightGlue](../catalog/repos/cvg__lightglue.md) exported for the edge, tiles pre-cut with [GDAL](../catalog/repos/osgeo__gdal.md) and [PMTiles](../catalog/repos/protomaps__pmtiles.md), retrieval with a small descriptor ([MixVPR](../catalog/repos/amaralibey__mixvpr.md)), VIO from [Isaac ROS Visual SLAM](../catalog/resources/isaac-ros-visual-slam-docs.md), injection via [MAVROS](../catalog/repos/mavlink__mavros.md) or the [ArduPilot non-GPS MAVLink messages](../catalog/resources/ardupilot-dev-mavlink-nongps-position.md).
- **Data:** [UAV-VisLoc](../catalog/repos/intellisensing__uav-visloc.md) replayed from disk as a fake camera; [OpenDroneMap](../catalog/repos/opendronemap__odm.md) to build your own reference orthophoto if you fly a survey.
- **Demo plan:** Board on the table running replayed frames => fixes per second, latency and error on screen => fixes feeding PX4/ArduPilot SITL over serial or UDP.
- **Stretch:** Hardware flight with a pre-surveyed reference map.
- **Risk:** Highest. JetPack/CUDA/ROS version mismatches can eat a day. Flash and test the board image before the event, or fall back to laptop.

---

## 4. Reference architectures

### 4.1 GNSS-denied UAV navigation stack

```mermaid
flowchart LR
  subgraph Sensors
    IMU[IMU]
    CAM[Nadir / forward camera]
    BARO[Baro + rangefinder]
    GNSS[GNSS receiver]
  end
  subgraph Companion["Companion computer"]
    VIO["VIO<br/>OpenVINS / ORB-SLAM3"]
    VGL["Visual geolocalization<br/>retrieval + LightGlue"]
    INTEG["GNSS integrity<br/>RAIM, C/N0, OSNMA"]
    GATE["Fix gating<br/>innovation + plausibility"]
  end
  subgraph FC["Flight controller"]
    EKF["EKF3 / EKF2<br/>source switching"]
    CTRL[Position control]
  end
  MAP[("Reference tiles<br/>+ DEM")]
  GCS["GCS / TAK<br/>nav health + alerts"]

  CAM --> VIO
  IMU --> VIO
  CAM --> VGL
  MAP --> VGL
  GNSS --> INTEG
  VIO -->|relative pose| EKF
  VGL -->|absolute fix + covariance| GATE
  INTEG -->|trusted / suspect| GATE
  GNSS --> GATE
  GATE -->|accepted fixes| EKF
  IMU --> EKF
  BARO --> EKF
  EKF --> CTRL
  EKF -->|EKF status, source in use| GCS
  INTEG -->|alarm| GCS
```

Repos: [PX4](../catalog/repos/px4__px4-autopilot.md) / [ArduPilot](../catalog/repos/ardupilot__ardupilot.md),
[OpenVINS](../catalog/repos/rpng__open_vins.md), [LightGlue](../catalog/repos/cvg__lightglue.md),
[MAVROS](../catalog/repos/mavlink__mavros.md), [gnss_lib_py](../catalog/repos/stanford-navlab__gnss_lib_py.md).
Key design rule: integrity checks sit before the EKF, not after.

### 4.2 Interference detection to C2 picture

```mermaid
flowchart LR
  subgraph Edge["Edge sensors"]
    UBX["u-blox receiver<br/>MON-RF, NAV-STATUS"]
    PHONE["Android phones<br/>raw GNSS"]
    ADSB["1090 MHz RTL-SDR<br/>readsb"]
    AIS["VHF RTL-SDR<br/>AIS-catcher"]
  end
  subgraph Detect["Detectors"]
    D1["Jamming: C/N0, AGC,<br/>NIC/NACp drop"]
    D2["Spoofing: residuals,<br/>jumps, impossible tracks"]
  end
  AGG["Aggregator<br/>hex cells, time windows,<br/>confidence"]
  STORE[("Event store")]
  COT["CoT generator<br/>PyTAK"]
  TAK["TAK server<br/>OpenTAKServer"]
  CLIENTS["ATAK / WinTAK /<br/>GoATAK web"]
  WEB["Web map<br/>deck.gl / MapLibre"]

  UBX --> D1
  UBX --> D2
  PHONE --> D2
  ADSB --> D1
  ADSB --> D2
  AIS --> D2
  D1 --> AGG
  D2 --> AGG
  AGG --> STORE
  AGG --> COT
  COT --> TAK
  TAK --> CLIENTS
  STORE --> WEB
```

Repos: [pyubx2](../catalog/repos/semuconsulting__pyubx2.md), [readsb](../catalog/repos/wiedehopf__readsb.md),
[pyModeS](../catalog/repos/junzis__pymodes.md), [AIS-catcher](../catalog/repos/jvde-github__ais-catcher.md),
[PyTAK](../catalog/repos/snstac__pytak.md), [OpenTAKServer](../catalog/repos/brian7704__opentakserver.md),
[deck.gl](../catalog/repos/visgl__deck.gl.md). Label "no data" cells differently from "no interference".

### 4.3 Multi-sensor fusion with integrity monitoring

```mermaid
flowchart TB
  subgraph Sources
    S1[GNSS]
    S2[VIO]
    S3[Visual geolocalization]
    S4[TRN / MagNav]
    S5[Baro, magnetometer]
  end
  IMU[IMU propagation]
  subgraph Monitor["Integrity layer"]
    M1["Per-source checks<br/>chi-square innovation"]
    M2["Cross-source consistency<br/>bank of filters, leave-one-out"]
    M3["Source health state<br/>trusted / suspect / excluded"]
  end
  FUSE["Main estimator<br/>EKF or factor graph"]
  OUT["Position + protection level<br/>+ which sources are in use"]
  LOG[("Audit log")]

  S1 --> M1
  S2 --> M1
  S3 --> M1
  S4 --> M1
  S5 --> M1
  IMU --> FUSE
  M1 --> M2
  M2 --> M3
  M3 -->|only trusted sources| FUSE
  FUSE -->|predicted measurements| M1
  FUSE --> OUT
  M3 --> LOG
  OUT --> LOG
```

Repos: [GTSAM](../catalog/repos/borglab__gtsam.md), [MaRS](../catalog/repos/aau-cns__mars_lib.md),
[MINS](../catalog/repos/rpng__mins.md), [navlie](../catalog/repos/decargroup__navlie.md),
[RAIM](../catalog/repos/michaelbeechan__raim.md). Background: [Gipson ION talk on multi-filter all-source monitoring](../catalog/resources/ion-webinar-gipson.md),
[Groves textbook](../catalog/resources/groves-pnt-book-2e.md).

### 4.4 Maritime GNSS-denied navigation

```mermaid
flowchart LR
  subgraph Ship["Vessel sensors"]
    G[GNSS]
    HDG[Gyro / compass heading]
    LOG2[Speed log]
    RAD[Marine radar]
    SKY[Sky camera]
    AISR[AIS receiver]
  end
  DR["Dead reckoning<br/>heading + speed + current"]
  RADM["Radar to chart<br/>coastline matching"]
  CEL["Celestial fix<br/>tetra3"]
  CHK["Integrity check<br/>GNSS vs DR vs radar vs celestial"]
  AISCHK["AIS plausibility<br/>neighbour vessels"]
  SK["Signal K server"]
  DISP["OpenCPN chart<br/>trusted position + alarm"]
  SHORE["Shore / C2<br/>CoT or NMEA"]

  HDG --> DR
  LOG2 --> DR
  RAD --> RADM
  SKY --> CEL
  G --> CHK
  DR --> CHK
  RADM --> CHK
  CEL --> CHK
  AISR --> AISCHK
  AISCHK --> CHK
  CHK --> SK
  SK --> DISP
  SK --> SHORE
```

Repos: [Signal K Server](../catalog/repos/signalk__signalk-server.md), [OpenCPN](../catalog/repos/opencpn__opencpn.md),
[radar_pi](../catalog/repos/opencpn-radar-pi__radar_pi.md), [tetra3](../catalog/repos/esa__tetra3.md),
[pyais](../catalog/repos/m0r13n__pyais.md), [MOOS-IvP](../catalog/repos/moos-ivp__moos-ivp.md). Context: [Maritime navigation](../catalog/concepts/maritime-nav.md), [NMEA 0183](../catalog/resources/nmea-0183-standard.md).

### 4.5 Team / swarm cooperative localization

```mermaid
flowchart TB
  subgraph A1["Agent 1 (anchor: good fix)"]
    A1O[Odometry]
    A1G[Trusted absolute fix]
  end
  subgraph A2["Agent 2"]
    A2O[Odometry]
    A2R[UWB ranges]
  end
  subgraph A3["Agent 3"]
    A3O[Odometry]
    A3R[UWB ranges]
  end
  NET["Mesh link<br/>lossy, intermittent"]
  FG["Shared factor graph<br/>odometry + range + anchor factors<br/>(central or distributed)"]
  EST["Per-agent pose + covariance"]
  COP["Team picture<br/>TAK / web map"]

  A1O --> NET
  A1G --> NET
  A2O --> NET
  A2R --> NET
  A3O --> NET
  A3R --> NET
  NET --> FG
  FG --> EST
  EST -->|corrections| NET
  EST --> COP
```

Repos: [GTSAM](../catalog/repos/borglab__gtsam.md), [Crazyswarm2](../catalog/repos/imrclab__crazyswarm2.md),
[swarm relative localization](../catalog/repos/eth-pbl__swarm-relative-localization.md),
[Swarm-SLAM](../catalog/repos/mistlab__swarm-slam.md), [Kimera-RPGO](../catalog/repos/mit-spark__kimera-rpgo.md) for robust outlier rejection,
[DPGO](../catalog/repos/mit-acl__dpgo.md) for distributed optimisation.

---

## 5. 48h execution plan template

Assumes 4-5 people. For a 24h event, compress each block by half and cut the stretch goal
at H+0.

Roles: **Lead/integrator** (owns the demo path and the repo), **Nav/estimation** (filter,
detector, metrics), **Platform** (SITL, autopilot, hardware), **Viz/C2** (TAK, map, UI),
**Pitch/evidence** (slides, plots, judge questions; also tests).

| Window | Goal | Exit criterion |
|---|---|---|
| H+0 to H+2 | Lock the problem statement against the challenge text. Pick one idea and one fallback. Write the demo script in five lines. | Demo script agreed; one metric named (ATE, time-to-detect, holdover minutes, false-alarm rate). |
| H+2 to H+6 | Walking skeleton: data in => dumb algorithm => output on the map. Everything end to end, nothing good. | A fake detection or a raw position shows up in TAK / the web map. |
| H+6 to H+12 | Real core algorithm on real or recorded data. Metric computed automatically. | First honest number on a plot, committed with the script that made it. |
| H+12 to H+14 | Checkpoint: is the core working? If not, switch to the fallback idea now. | Go / switch decision written down. |
| H+14 to H+22 | Sleep in shifts. Integration into SITL or hardware. Failure case found and recorded. | Full demo runs once without manual fixes. |
| H+22 to H+30 | Improve the metric; add the integrity/alarm layer; add the "what we did not verify" list. | Before/after comparison plot. |
| H+30 to H+36 | Feature freeze. Record a backup demo video. Rehearse the live run three times. | Video saved locally and on a second laptop. |
| H+36 to H+42 | Pitch: problem (cite one incident source), approach, live demo, number, limits, next steps, compliance line. | 3-minute pitch timed. |
| H+42 to H+48 | Buffer, judge Q&A prep, clean README with run instructions. | README reproduces the demo on a clean machine. |

Pitch skeleton (map to Section 1):

1. Threat in one sentence with a real source.
2. Who uses this and on what platform.
3. What it does, mapped to detect / respond / recover.
4. Live demo or video, with the failure case.
5. The number, with ground truth and how it was measured.
6. What is not verified yet. What breaks it.
7. Dual-use line and compliance line (civil signals, cabled-only signal generation, human in the loop for any AI action).

Judge questions to rehearse: How is it tested? What happens when your sensor fails too?
How does a field user retune it? How do you turn the AI part off? What is the hardware
class and power draw? What data did you train or tune on, and does it transfer?

---

## 6. Pre-hackathon prep checklist

### 6.1 Accounts and access (request a week ahead)

- [ ] GitHub org or shared repo, with branch protection off for speed.
- [ ] Kaggle account (GSDC data: [2023](../catalog/resources/google-gsdc-2023.md), [2022](../catalog/resources/google-gsdc-2022.md)).
- [ ] NASA Earthdata login (CDDIS corrections used by [laika](../catalog/repos/commaai__laika.md)).
- [ ] Hugging Face account; request the gated [satellite-thermal dataset](../catalog/repos/arplaboratory__satellite-thermal-geo-localization.md) early.
- [ ] OpenSky Network registration ([API clients](../catalog/repos/openskynetwork__opensky-api.md); anonymous access is rate-limited).
- [ ] KITTI and Oxford RobotCar registration if you plan to use them ([KITTI odometry](../catalog/resources/kitti-odometry-benchmark.md), [RobotCar](../catalog/resources/oxford-robotcar-dataset.md)).
- [ ] Cesium ion token, or plan offline terrain ([CesiumJS](../catalog/repos/cesiumgs__cesium.md)).
- [ ] [TAK.gov](../catalog/resources/tak-gov.md) account for ATAK-CIV and plugin SDK, if you go beyond stock clients.
- [ ] Galileo OSNMA public key and Merkle root from [GSC](../catalog/resources/gsc-programme-reference-documents.md).
- [ ] An LLM API key or Claude Code / MCP client set up, if doing ideas 6, 7 or 14. Register the hub as an MCP server ([llm-agent-usage](../samples/llm-agent-usage/)).

### 6.2 Software images to build and test before the event

- [ ] PX4 SITL with Gazebo (`make px4_sitl gz_x500`) - [PX4](../catalog/repos/px4__px4-autopilot.md), [PX4 simulation docs](../catalog/resources/px4-simulation-docs.md).
- [ ] ArduPilot SITL (`sim_vehicle.py`) with MAVProxy - [ArduPilot SITL docs](../catalog/resources/ardupilot-sitl-docs.md), [ardupilot_gazebo](../catalog/repos/ardupilot__ardupilot_gazebo.md).
- [ ] ROS 2 Docker image matching your Gazebo release and [ros_gz](../catalog/repos/gazebosim__ros_gz.md) branch.
- [ ] [OpenTAKServer](../catalog/repos/brian7704__opentakserver.md) on a laptop or Pi, with one ATAK/iTAK/GoATAK client connected.
- [ ] [GNSS-SDR](../catalog/repos/gnss-sdr__gnss-sdr.md) from distro packages; one IQ file processed end to end.
- [ ] Python venv with `pyubx2 pynmeagps pytak pymavlink mavsdk gnss-lib-py georinex rasterio pyproj filterpy gtsam evo stonesoup pyais lightglue` (check each install line in its catalog page).
- [ ] Julia + MagNav.jl precompiled, if doing MagNav (first run compiles slowly).
- [ ] Jetson flashed, CUDA and your matcher tested on one image, if doing idea 20.
- [ ] Offline basemap: [PMTiles](../catalog/repos/protomaps__pmtiles.md) extract of the venue region + [Martin](../catalog/repos/maplibre__martin.md) or [TileServer GL](../catalog/repos/maptiler__tileserver-gl.md).
- [ ] Run each sample you plan to use: [samples/](../samples/) (each sample states whether it was run or is a sketch).

### 6.3 Datasets to pre-download

The hub does not record download sizes. Imagery datasets and raw IQ recordings are the
large ones; check the host page and budget disk and time. Venue Wi-Fi will not carry them.

| Dataset | Used by ideas | Notes |
|---|---|---|
| [Jammertest](../catalog/resources/jammertest-norway.md) participant datasets and test plan | 1, 9 | Real over-the-air jamming/spoofing; datasets released on GitHub by participants |
| [TEXBAT](../catalog/resources/ut-texbat.md) | 1, 8 | High-rate IQ files - large; take one or two scenarios |
| [Multi-frequency spoofing dataset](../catalog/repos/s7am1na__gnss-spoofing-dataset.md) | 1, 4 | Android/smartwatch raw logs |
| [GSDC 2023](../catalog/resources/google-gsdc-2023.md) | 4 | Kaggle login |
| [UrbanNav](../catalog/repos/ipnl-polyu__urbannavdataset.md) | 4, 5 | Urban GNSS degradation with IMU/lidar |
| [KF-GINS demo data](../catalog/repos/i2nav-whu__kf-gins.md) | 5 | Bundled with the repo |
| [EuRoC MAV](../catalog/resources/ethz-euroc-mav-dataset.md) | 10 | Standard VIO baseline; take 2-3 sequences |
| [UAV-VisLoc](../catalog/repos/intellisensing__uav-visloc.md) | 18, 20 | Take one flight and its map |
| [VPAIR](../catalog/repos/aervisloc__vpair.md) / [ALTO](../catalog/repos/metaslam__alto.md) | 18 | Aerial place recognition alternatives |
| [Copernicus DEM tiles](../catalog/resources/copernicus-dem-aws.md) for your AOI | 11, 14 | No account; cloud-optimized GeoTIFF |
| [MagNav challenge data](../catalog/resources/magnav-challenge-site.md) / [Zenodo](../catalog/resources/magnav-zenodo-dataset.md) | 16 | Plus [AFIT example data](../catalog/repos/afit-eeng-magnav__example-data.md) |
| [UTIL UWB TDoA](../catalog/resources/util-uwb-dataset.md) | 13 | Has EKF baseline |
| [NTU VIRAL](../catalog/repos/ntu-aris__ntu_viral_dataset.md) / [MCD](../catalog/resources/mcd-multi-campus-dataset.md) | 19 | UWB + lidar |
| A recorded AIS NMEA file from a public feed | 3, 12 | Record a day before the event |
| OpenSky historical states for one known interference day | 2 | Rate limits - fetch in advance |
| [tetra3](../catalog/repos/esa__tetra3.md) sample images + your own night sky shots | 15 | Venue may be cloudy |

### 6.4 Hardware shopping list (cost class only)

| Item | Cost class | Used by ideas | Notes |
|---|---|---|---|
| RTL-SDR dongle + 1090 MHz antenna | low-cost | 2 | Receive only |
| RTL-SDR + VHF marine antenna | low-cost | 3 | Receive only; [AIS-catcher](../catalog/repos/jvde-github__ais-catcher.md) |
| u-blox GNSS receiver with raw/MON-RF output (M8/M9 class), multi-band (F9P class) better | low-cost to mid | 1, 8 | F9P class also outputs Galileo nav bits for OSNMA |
| Android phone with raw GNSS measurements | existing | 4 | Check handset support for raw measurements |
| Raspberry Pi 4/5 class | low-cost | 1, 2, 3 | Runs readsb, monitor, OpenTAKServer |
| Coax cables, SMA attenuators, DC block, small shielded enclosure | low-cost | 1, 8 | Mandatory for any simulated GNSS signal into a receiver |
| HackRF / ADALM-Pluto class SDR | mid | 1, 8 | Cabled or shielded only for signal generation; never radiate |
| IMU breakout board | low-cost | 5 | For your own Allan variance recording |
| Pixhawk-class flight controller | mid | 9, 10, 13 | Optional; SITL covers the demo |
| Global-shutter or stereo camera | mid | 10, 18, 20 | Optional; datasets cover the demo |
| Jetson Orin class board | mid to high | 20 | Flash and test before the event |
| UWB modules (DW1000/DW3000 class) or Crazyflie + Loco deck kit | mid | 13, 19 | Optional; sim and UTIL dataset cover the demo |
| LoRa modules (ESP32 class) | low-cost | 13 | For ranging experiments |
| KrakenSDR | mid | 1 stretch | Direction finding; [KrakenSDR DoA](../catalog/repos/krakenrf__krakensdr_doa.md) |
| USB hub, spare SD cards, power banks, HDMI capture | low-cost | all | Demo-day failures are usually here |

### 6.5 Rules and safety to settle before day one

- [ ] Read the event's own rules on RF transmission and drones; assume no transmission.
- [ ] GNSS signal generation (GPS-SDR-SIM, OSNMA-SDR-SIM, multi-sdr-gps-sim) only into a file, a cable or a shielded box. Radiating is illegal in most jurisdictions.
- [ ] Keep code on public civil signals and published methods ([Stony Brook guide](../catalog/resources/stonybrook-export-publicly-available.md), [EU research recommendation](../catalog/resources/eu-recommendation-2021-1700-research.md)).
- [ ] If your repo is private and the team is international, read [EAR and open source](../catalog/resources/linux-foundation-ear-open-source.md) - private sharing can count as export.
- [ ] Any AI that can command a vehicle: human confirmation, allowlisted actions, logged decisions, a documented off switch.
- [ ] Scope stays on navigation, integrity and awareness. No targeting, no terminal guidance.
