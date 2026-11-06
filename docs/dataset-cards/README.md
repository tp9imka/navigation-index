# Dataset cards

<!-- about: concept:datasets-benchmarks -->

There are 59 cards, one per dataset or per small family of datasets, all written or refreshed 2026-11-06. Each card gives sensors and rates, ground-truth source and stated accuracy, a verified size, the license, exact download commands, loaders from the index, the [playbook](../hackathon-playbook.md) ideas it suits, and pitfalls.

**How sizes were checked.** Each card names its method: HEAD `Content-Length`, the Zenodo / Hugging Face / S3 / DSpace APIs, or the figure stated on the download page. Data behind Google Drive, OneDrive, Baidu, Kaggle or a request form is marked "not verified". Nothing was downloaded in full by the card authors, and no loader was run unless a card says so. Cards whose data a sample in [samples/](../../samples/) actually pulled have a **Used in this repo** section with what that run measured: download method, bytes, wall time, gotchas. Cells below marked "stated" are the authors' numbers; "ran" marks a subset a sample downloaded and processed.

**Licenses.** Most sets are non-commercial research only (CC BY-NC-SA and similar). Check the terms before a demo turns into a product pitch, and before you share files inside a team: AnyVisLoc forbids redistribution, and TEXBAT and MagNav carry their own use terms.

## Comparison

### Visual-inertial, aerial and handheld SLAM

| Dataset | Platform | Sensors | GT | Size (total / smallest useful) | License | Best for |
|---|---|---|---|---|---|---|
| [EuRoC MAV](euroc-mav.md) | indoor multirotor | stereo 20 Hz, IMU 200 Hz | Vicon 6D; Leica laser tracker 3D | 29.2 GB / vicon_room1 6.04 GB (DSpace API) | personal non-commercial | first VIO check, idea 10 |
| [TUM-VI](tum-vi.md) | handheld | stereo 20 Hz, IMU 200 Hz | mocap; only at start/end outside the room | 172 GB / room1_512 1.71 GB | CC BY 4.0 | long-run drift, IMU noise (5, 10) |
| [UZH-FPV](uzh-fpv.md) | FPV racing quad | cam + IMU, events, T265 | Leica MS60 + reconstruction; some withheld | about 65 GB (summed page table) / indoor_forward_3 bag 1.61 GB (ran, OpenVINS) | CC BY-NC-SA 3.0 | aggressive-flight VIO stress test |
| [Blackbird](blackbird.md) | mocap-room quad | real IMU, motor RPM, rendered cams | mocap 360 Hz | 4.9 TB stated; host down | data not stated | IMU + dynamics dead reckoning |
| [TartanAir v1/v2](tartanair.md) | synthetic | stereo/multi-cam, depth, flow, sim IMU, lidar | perfect | v1 1.1 TB, v2 54 TB / one env 1.06 GB | CC BY 4.0 vs BSD-3 (conflict) | training learned VO, adverse conditions |
| [Mid-Air](mid-air.md) | synthetic quad | 3 RGB 25 Hz, IMU 100 Hz, GPS 1 Hz | perfect | not stated (email-gated) | CC BY-NC-SA 4.0 | GPS blanking + VO holdover |
| [NTU VIRAL](ntu-viral.md) | UAV | 2 lidars, stereo, IMU, UWB | laser tracker (prism offset) | 88.4 GB / eee_03 2.0 GB (HEAD) | CC BY-NC-SA 4.0 | UWB fusion (13, 19), aerial LIO |
| [MARS-LVIG](mars-lvig.md) | DJI M300 at 80-130 m | Livox, RGB, F9P raw GNSS | M300 RTK | not verified (Drive) | CC BY-NC-SA 4.0 | aerial raw-GNSS fusion, outage at altitude |
| [Hilti SLAM 2021-23](hilti-slam.md) | handheld, tracked robot | 5 cams, Hesai XT-32, IMU | TLS/total-station control points, mm | 198-370 GB per year / 6.26 GB bag | CC BY-NC-SA 3.0 | multi-floor indoor, multi-session (19) |
| [Newer College](newer-college.md) | handheld | Ouster, D435i/Alphasense, IMU | survey-map registration, cm stated | 610.6 GB / 1.84 GB | CC BY-NC-SA 4.0 | prior-map relocalization |
| [SubT datasets](subt-datasets.md) | UGV, Spot, UAV, handheld | lidar, cams, thermal | varies | DARPA bags 13.9-33 GB (HEAD); others not verified | mostly not stated | underground, degraded-sensor switching |
| [Event cameras](event-camera-datasets.md) | car / multi-platform | stereo events, frames, lidar, IMU | DSEC none; MVSEC files; VECtor mocap | DSEC about 450 GB stated / MVSEC 1.28 GB | CC BY-SA 4.0 / not stated / BSD-3-Clear | night and fast-motion VO |

### Ground vehicles, urban GNSS, radar

| Dataset | Platform | Sensors | GT | Size (total / smallest useful) | License | Best for |
|---|---|---|---|---|---|---|
| [KITTI](kitti.md) | car | stereo, Velodyne, OXTS | OXTS GPS/IMU | odometry 23.2 + 84.8 GB / seq 04 raw drive 1.13 GB (ran, KISS-ICP) | CC BY-NC-SA 3.0 | VO/LO baseline, IMU holdover (5, 10) |
| [UrbanNav](urbannav.md) | car, Hong Kong + Tokyo | 3 lidars, ZED2, Xsens, multi-receiver RINEX | RTK-INS, 5 cm stated | 4.45-147 GB per sequence / GT + IMU CSV 0.11 GB (HEAD) | MIT | urban NLOS, tunnel outage (4, 5) |
| [UrbanLoco](urbanloco.md) | car, HK + SF | lidar, cams, Xsens, M8T raw | SPAN RTK-INS, 5 cm stated | about 448 GB stated / 6.1 GB | CC BY-NC-SA 4.0 | raw GNSS faults (4) |
| [M2DGR](m2dgr.md) | ground robot | lidar, fisheyes, thermal, event, IMUs, M8T raw | RTK/INS, Leica, Vicon | 1220.6 GB stated / 14 GB | MIT, academic use | indoor-outdoor source switching |
| [GVINS](gvins.md) | not described | stereo 20 Hz, IMU 200 Hz, F9P raw 10 Hz | F9P RTK | 75.2 GB / 17.3 GB (HF API) | CC BY-NC-SA 4.0 | GNSS-VIO coupling, raw-GNSS fault injection (4, 10) |
| [MCD](mcd.md) | ATV + handheld | Ouster, Livox, RealSense, VN100/200, UWB | survey-map B-spline | 438.8 GB stated / UWB+IMU+GT under 100 MB | CC BY-NC-SA 4.0 | radio ranging, cooperative (13, 19) |
| [Oxford RobotCar](oxford-robotcar.md) | car | stereo, fisheyes, lidars, SPAN | INS + RTK release | about 20 TB stated; **withdrawn 2026-10-22** | CC BY-NC-SA 4.0 | long-term relocalization (if it returns) |
| [Oxford Radar RobotCar](oxford-radar-robotcar.md) | car | Navtech radar, 2 lidars, cams, INS | radar-odometry SE(2), relative | 3831.5 GB stated / 200 MB sample | non-commercial | radar odometry |
| [Boreas](boreas.md) | car, multi-season | 128-beam lidar, camera, Navtech, Applanix | POS LV + RTX, 2-4 cm stated | one sequence 118.2 GB / radar + GT about 3 GB (S3 listing) | CC BY 4.0 | all-weather radar localization |
| [MulRan + HeLiPR](mulran-helipr.md) | car | Ouster + Navtech; 4 lidar types | SE3 baseline; INS | about 243 GB stated / 0.6-3 GB samples | CC BY-NC-SA 4.0 / not stated | range-sensor place recognition |
| [NCLT](nclt.md) | Segway | HDL-32E, Ladybug3, IMU, FOG, RTK GPS | SLAM + RTK | about 3 TB / 235 MB per session (HEAD) | ODbL | INS/FOG holdover, GPS integrity (5) |
| [Complex Urban](complex-urban.md) | car | lidars, stereo, VRS GPS, IMU, FOG, encoders | graph SLAM + VRS | not stated (request form) | CC BY-NC-SA 4.0 | urban dead reckoning (5) |
| [RELLIS-3D + TartanDrive](offroad-rellis-tartandrive.md) | Warthog UGV / ATV | lidars, stereo, IMU, wheel | poses.txt / none | 7-28 GB per sequence / TartanDrive 2063 GB (HEAD) | CC BY-NC-SA 3.0 / not stated | off-road autonomy, not PNT scoring |

### GNSS, interference, magnetic, radio ranging, pedestrian

| Dataset | Platform | Sensors | GT | Size (total / smallest useful) | License | Best for |
|---|---|---|---|---|---|---|
| [Google Smartphone Decimeter Challenge](gsdc.md) | Android phones in cars | raw GNSS + IMU | NovAtel SPAN | Kaggle not verified / taroz preprocessed 2.76 GB | Kaggle rules | Android spoof baseline (4), holdover (5) |
| [TEXBAT](texbat.md) | static + dynamic receiver | GPS L1 IQ 25 MS/s | scenario definitions | about 430 GB / cleanStatic80 8.0 GB, processed ds3 0.8 GB (HEAD, listing) | UT research use, no redistribution | signal-level spoof detection (1, 8) |
| [Jammertest data](jammertest-data.md) | Andoya sites / cars | E1/E5a IQ + CRPA; phones + u-blox | per-sample labels; plan windows | Fraunhofer 360 GB / chunk pair 2.9 GB; VAARA 1.57 GB | CC BY-NC-SA 4.0 / none / MIT | interference classifier, monitor (1, 4, 9) |
| [S7AM1NA spoofing](gnss-spoofing-s7am1na.md) | 4 phones, 2 watches | GnssLogger raw L1/L5 | spoof windows only | README says about 115 MB; only 23.7 MB sample public, **not a labelled attack** | MIT | Android spoof detector (4), weak |
| [MagNav challenge data](magnav-challenge-data.md) | Cessna Grand Caravan | scalar + fluxgate mags, INS, GPS, 10 Hz | GPS | 1.16 GB + maps 0.71 GB (Zenodo API); Julia artifacts 1.8 GB on disk (ran) | public domain vs AF use agreement | MagNav sprint (16) |
| [AFIT MagNav example data](afit-magnav-example-data.md) | same aircraft | mag/INS + maps + geoid | GPS | about 277 MB | not stated | MagNav without Julia (16, 11) |
| [UTIL UWB TDoA](util-uwb-tdoa.md) | Crazyflie quad, indoor | UWB TDoA2/3, IMU, flow, ToF | Vicon, surveyed anchors | 1.86 GB (not yet used by a sample) | not stated | radio-ranging RTH (13), cooperative (19) |
| [MILUV](miluv.md) | 3 quads, indoor | UWB incl. inter-robot + CIR, D435i, IMU | mocap | 185.7 GB / 3-robot run 3.2 GB (not yet used by a sample) | CC BY 4.0 | cooperative localization (19) |
| [RoNIN](ronin.md) | pedestrians | phone IMU 200 Hz | Tango VIO | not verified | research only | learned PDR |
| [PyShoe](pyshoe.md) | foot-mounted IMU | IMU | Vicon / checkpoints | about 2.9 GB stated / hallway .mat 85 MB (ran, FTP intermittent) | not stated | ZUPT INS, dismounted |
| [OSNMAlib recording](osnmalib-recording.md) | static Septentrio receiver | Galileo I/NAV pages (SBF), 76 min | none (clean live sky) | 2.6 MB (GitHub API; ran) | EUPL-1.2 | OSNMA authenticate-or-alarm (8) |
| [ADS-B Exchange monthly sample](adsbexchange-samples.md) | crowd ADS-B / MLAT receivers | global readsb snapshots every 5 s, NACp / NIC | none | about 5 MB per snapshot; 2 h at 60 s about 0.7 GB (ran) | free, all rights reserved, ToU apply | ADS-B interference map (2) |
| [Sentinel-1 GRD + RFI annotation](sentinel-1-grd.md) | satellite C-band SAR | VV/VH COGs, ESA RFI XML | none | 0.49 GB per VH scene; 18 scenes at 1/8 about 0.44 GB (ran) | Copernicus open | C-band RF context layer (2) |
| [Indoor Location Competition 2.0](indoor-location-2020.md) | handheld phone | IMU, mag, Wi-Fi, iBeacon | surveyor waypoints | Kaggle not verified / repo sample about 2.2 GB | MIT sample / Kaggle | indoor PDR + fingerprinting |

### Absolute visual localization and cross-view

| Dataset | Platform | Sensors | GT | Size (total / smallest useful) | License | Best for |
|---|---|---|---|---|---|---|
| [UAV-VisLoc](uav-visloc.md) | fixed-wing + multirotor, 11 sites | nadir RGB, 0.3 m satellite GeoTIFF | per-image lat/lon/height/heading | 16 GB / site 03 2.0 GB | not stated | drone-to-satellite in meters (18, 20) |
| [AnyVisLoc](anyvisloc.md) | 7 DJI models, 6-500 m, oblique | RGB, aerial + satellite + DSM | 6-DoF, PnP-checked within 0.5 m | not verified (Baidu/OneDrive) | research only, **no redistribution** | low-altitude oblique 6-DoF (18) |
| [University-1652](university-1652.md) | synthetic drone + satellite + ground | RGB | building ID | not verified (email request) | research only | pretraining retrieval |
| [SUES-200](sues-200.md) | real drone, 150-300 m | RGB | scene ID | 5.3 GB | academic only | retrieval across altitudes |
| [DenseUAV](denseuav.md) | UAV, 80-100 m | RGB + 2-epoch satellite | lat/lon/height | 16.7 GB | Apache-2.0 / MIT tag | low urban self-positioning, map age |
| [VPAIR](vpair.md) | light aircraft over 300 m | nadir RGB + rendered refs | 6-DoF | 20.5 GB / sample 0.86 GB (ran, nadir VO) | academic (sample tagged CC BY, conflict) | fixed-wing VPR + PnP, nadir VO |
| [AerialVL](aerialvl.md) | UAV, about 70 km | RGB, GNSS | NovAtel SPP, 1.5 m RMS | 145.7 GB / train 11.4 GB | CC BY 4.0 | long sequences for map-aided tracking |
| [ALTO](alto.md) | helicopter | nadir RGB | NovAtel SPAN, submeter | not verified (Dropbox) | repo BSD-3, data terms unclear | high-altitude rural VPR |
| [Thermal sets](thermal-datasets.md) | night UAV / aerial robot / car | thermal + satellite; RGB+LWIR+GPS+IMU | paired crops; GPS-IMU | Boson 74-215 GB (gated); CART site 5.3 GB | non-commercial | night geolocalization (STHN) |

### Maritime, underwater, counter-UAS

| Dataset | Platform | Sensors | GT | Size (total / smallest useful) | License | Best for |
|---|---|---|---|---|---|---|
| [Maritime sets](maritime-datasets.md) | vessel / harbor boat / shore | Pohang: 3 lidars, radar, stereo, IR, AHRS, RTK; MassMIND LWIR; SMD RGB+NIR; LaRS | RTK; masks; boxes | Pohang 1.3 TB / navigation.zip 21 MB; MassMIND 414 MB; LaRS 1.0 GB | CC BY-NC(-SA) 4.0 mostly | maritime integrity (12), SA (3) |
| [Underwater sets](underwater-datasets.md) | ROVs, light AUV | mono cam, IMU, pressure, simulated LBL; side-scan | SfM; vehicle estimate (not independent) | LBL-AQUALOC 56.2 GB; SubPipe 28 GB / Mini2 4.9 GB | CC BY 4.0 (SubPipe) | UUV nav real-data leg (17) |
| [DMA AIS](dma-ais.md) | shore AIS network, Danish waters | AIS CSV, 1 s receive time | none (positions are ships' own GNSS) | 0.6 GB per day zipped (HEAD); first 100 MiB = 4.4 h (ran) | Danish PSI, attribution | AIS spoofing detector (3), maritime integrity (12) |
| [NRC radar tracks](nrc-cuas-sensing.md) | ground K-band radar (EchoGuard) | 10 Hz tracks: pos, vel, RCS | expert labels, 1,117 tracks | 201.6 MB (git tree) / labelled xlsx 59 MB (ran) | CC BY 4.0 | UAV vs bird => C2 |
| [Anti-UAV + DvB + MAV-VID](anti-uav.md) | ground cameras | RGB + thermal IR video | manual boxes | Anti-UAV300 5.6 GB; others not verified | data terms not stated | C-UAS detection/tracking => SA |
| [Drone RF datasets](drone-rf-datasets.md) | ground SDR | 2.4 GHz IQ | class labels | DroneRF 4.03 GB / 4-RAR subset 0.69 GB, 6.6 GB extracted (ran); RFUAV 299 GB; DroneDetect, CardRF behind login | CC BY 4.0 / Apache-2.0 | RF drone classifier => C2 |
| [Remote ID / DroneID captures](remote-id-droneid-captures.md) | DJI drones; ODID test captures | IQ bursts, Wi-Fi/BT pcaps | decoded payload | under 8 MB | AGPL / Apache / MIT | passive Remote ID decoder => TAK |

### Reference maps and terrain

| Dataset | Platform | Content | Accuracy | Size (unit / as used) | License | Best for |
|---|---|---|---|---|---|---|
| [NAIP on Planetary Computer](naip-planetary-computer.md) | crewed survey aircraft, US only | RGB+NIR ortho, 0.3-1 m, several epochs | not stated; 2-5 m between epochs seen | 0.43-1.37 GB per quarter-quad / 2 x 2 km windows 27-94 MB (ran) | public domain with attribution | license-clean AVL map (18, 20) |
| [OpenAerialMap](openaerialmap.md) | user drone surveys, patchy | RGB ortho COG, cm-level | own georeference | 12.7-15.1 MB per scene used (HEAD; ran) | CC BY 4.0 | non-US drone ortho, synthetic pairs (18) |
| [Geobasis NRW DOM1 / DGM1](geobasis-nrw-lidar.md) | airborne LiDAR, NRW only | 1 m DSM + DTM tiles | not stated | 1.7-2.1 MB per 1 km tile / 4 x 4 km both 80 MB (ran) | dl-de/zero-2.0 | 1 m heightmap / TRN (11) |
| [Copernicus GLO-30](copernicus-glo30.md) | TanDEM-X, global | 30 m DSM COGs | not restated | about 42 MB per 1 deg tile (HEAD) / 0.8-18 MB windows (ran) | Copernicus DEM licence | TRN, radar-altimeter benches (11) |

## Pre-download before the hackathon

Venue Wi-Fi will not carry any of this. The core list covers every playbook idea that needs recorded data, using only subsets whose size was checked against the host (HEAD or API) or measured by a sample run on 2026-11-06.

### Core shortlist (about 59 GB)

| # | Dataset subset | Size | Ideas |
|---|---|---|---|
| 1 | [EuRoC](euroc-mav.md) vicon_room1.zip | 6.04 GB | 10, 18 (VO half) |
| 2 | [TUM-VI](tum-vi.md) room1_512 | 1.71 GB | 5, 10 |
| 3 | [UZH-FPV](uzh-fpv.md) indoor_forward_3 Snapdragon bag (what OpenVINS ran on) | 1.61 GB | 10 stress |
| 4 | [NTU VIRAL](ntu-viral.md) eee_03 | 2 GB | 13, 19 |
| 5 | [KITTI](kitti.md) seq 04 raw drive 2011_09_30_drive_0016 sync + calib + odometry poses | 1.13 GB | 5, 10 |
| 6 | [UrbanNav](urbannav.md) Tokyo_Data.zip + Medium-Urban-1 GT and IMU CSV | 4.56 GB | 4, 5 |
| 7 | [Boreas](boreas.md) one sequence, radar + applanix + calib only | 3 GB | radar odometry |
| 8 | [NCLT](nclt.md) one session sensors + GT | 0.24 GB | 5 |
| 9 | [GSDC](gsdc.md) taroz preprocessed 2023 zip | 2.76 GB | 4, 5 |
| 10 | [TEXBAT](texbat.md) cleanStatic80.bin + processed/ds3 | 8.80 GB | 1, 8 |
| 11 | [Jammertest](jammertest-data.md) VAARA + one Fraunhofer chunk pair | 4.47 GB | 1, 4, 9 |
| 12 | [S7AM1NA](gnss-spoofing-s7am1na.md) public sample | 0.02 GB | 4 (format only) |
| 13 | [OSNMAlib recording](osnmalib-recording.md) (clone of Algafix/OSNMA) | 0.01 GB | 8 |
| 14 | [ADS-B Exchange](adsbexchange-samples.md) 2 h of one 1st-of-month at 60 s | 0.70 GB | 2 |
| 15 | [Sentinel-1 GRD](sentinel-1-grd.md) 18-scene VH stack at 1/8 + RFI XML (sample cache) | 0.44 GB | 2 (C-band context) |
| 16 | [DMA AIS](dma-ais.md) one full day zip | 0.62 GB | 3, 12 |
| 17 | [MagNav](magnav-challenge-data.md) Zenodo 12723700 + Ottawa maps | 1.87 GB | 16 |
| 18 | [AFIT MagNav example data](afit-magnav-example-data.md) | 0.28 GB | 16, 11 |
| 19 | [Copernicus GLO-30](copernicus-glo30.md) 4 tiles around your likely area | 0.17 GB | 11 |
| 20 | [Geobasis NRW](geobasis-nrw-lidar.md) DOM1 + DGM1, 4 x 4 km | 0.08 GB | 11 (1 m map) |
| 21 | [UTIL UWB TDoA](util-uwb-tdoa.md) | 1.86 GB | 13, 19 |
| 22 | [MILUV](miluv.md) one 3-robot run | 3.20 GB | 19 |
| 23 | [PyShoe](pyshoe.md) hallway subset (fetch_data.sh) | 0.12 GB | 5, dismounted |
| 24 | [UAV-VisLoc](uav-visloc.md) site 03 | 2 GB | 18, 20 |
| 25 | [VPAIR](vpair.md) sample | 0.86 GB | 18, nadir VO |
| 26 | [NAIP](naip-planetary-computer.md) windows via geoloc-license-clean download_data.py | 0.12 GB | 18, 20 |
| 27 | [OpenAerialMap](openaerialmap.md) Tbilisi + Batumi COGs | 0.03 GB | 18 |
| 28 | [Pohang](maritime-datasets.md) navigation.zip + one radar sequence | 0.22 GB | 12 |
| 29 | [MassMIND](maritime-datasets.md) | 0.41 GB | 3, maritime SA |
| 30 | [Anti-UAV300](anti-uav.md) | 5.60 GB | C-UAS SA |
| 31 | [DroneRF](drone-rf-datasets.md) all 23 RARs | 4.03 GB | C-UAS RF |
| 32 | [NRC radar tracks](nrc-cuas-sensing.md) whole repo | 0.20 GB | C-UAS radar |
| 33 | [Remote ID / DroneID captures](remote-id-droneid-captures.md) | 0.01 GB | Remote ID => TAK |

Total: about 59 GB (59.2 GB summed). The Boreas figure is the sum of folder sizes from the S3 listing, not one file. The ADS-B, Sentinel-1 and NAIP lines are what a sample's fetch script produced (measured on disk), not one file on the host; GLO-30 is 4 x the HEAD size of one tile. Every other line is a HEAD or API figure taken from the card. Ideas 2, 3 and 11 had no recorded data on this list before this refresh; idea 8 now has real OSNMA pages next to TEXBAT.

### Optional, if the problem leans that way (about 58 GB more)

- [GVINS](gvins.md) complex_environment.bag, 17.3 GB: raw GNSS + VIO in one bag.
- [DenseUAV](denseuav.md), 16.7 GB: low-altitude urban AVL.
- [Hilti 2022](hilti-slam.md) exp14_basement_2, 6.26 GB: indoor, multi-floor.
- [SUES-200](sues-200.md), 5.3 GB: retrieval across altitudes.
- [SubPipe](underwater-datasets.md) Mini2, 4.9 GB: real AUV data.
- [Newer College](newer-college.md) math-easy part, 1.84 GB.
- [TartanAir](tartanair.md) one environment left RGB, 1.06 GB.
- [KITTI](kitti.md) seq 07 raw drive 2011_09_30_drive_0027, 4.42 GB: urban loop with a loop closure; ran at about 1 MB/s, start it early.

### Do not plan on these without a fallback

- **Oxford RobotCar** has been withdrawn since 2026-10-22. Use [Boreas](boreas.md) instead.
- **Blackbird** and **Aqualoc**: the hosts did not answer on 2026-11-06.
- **EuRoC**: the host rate-limits (HTTP 429), and the old `robotics.ethz.ch/~asl-datasets` URL did not connect for the relative-nav-benchmark sample. Pull it days ahead, one file at a time; UZH-FPV is the tested fallback.
- **IEEE DataPort sets** (DroneDetect, CardRF): free login, downloads reported to cut off. The C-UAS sample skipped both for that reason.
- **PyShoe FTP**: plain FTP on an IP address; timed out once and worked once on the same day.
- **ADS-B Exchange free data** exists only for the 1st of each month, published about 1.5 days later.
- **NAIP** covers the US only; outside it use OpenAerialMap, a national orthophoto portal, or a dataset's own map.
- **Slow hosts**: KITTI S3, UZH and Zenodo ran at 1-2 MB/s per file in the sample runs, and Zenodo stalled once; use `curl -C -`.
- **Kaggle sets** (GSDC raw, Indoor Location) need a login and accepted competition rules.
- **Request-form and Baidu sets** (University-1652, AnyVisLoc, MulRan, Complex Urban, Mid-Air) can take days to clear.
- **S7AM1NA**: the full release that the README points to does not exist. The public sample is not a labelled attack.

## Gaps

- Ground-truth accuracy is not stated on the source pages for many sets. Each card says which.
- These datasets are not indexed but have cards: Pohang, MassMIND, SMD, Aqualoc, LBL-AQUALOC, SubPipe, CART, MS2, Drone-vs-Bird, MAV-VID, DMA AIS, NAIP, OpenAerialMap, Geobasis NRW DOM1 / DGM1, ADS-B Exchange samples, Sentinel-1 GRD, the OSNMAlib recording. Their cards name the samples (and tools) that use them in the `about` marker instead.
- MILUV and UTIL have cards and shortlist slots but no sample has run on them yet.
- No open, labelled, multi-constellation spoofing dataset with recorded raw observables (not IQ) turned up beyond Jammertest participant releases.
