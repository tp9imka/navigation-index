# Underwater navigation datasets (Aqualoc, LBL-AQUALOC, SubPipe)

<!-- about: repo:patrykcieslak/stonefish, repo:byu-holoocean/holoocean-docs, repo:jake3991/sonar-slam -->

None of these are indexed; the about marker lists the indexed simulators and sonar SLAM code
they pair with. Real underwater navigation data with good ground truth is rare, so each
of these has a caveat on GT.

| Dataset | Platform | Sensors | GT | Size | License |
|---|---|---|---|---|---|
| Aqualoc (LIRMM / ONERA, IJRR 2019) | ROVs: harbor at a few m depth, archaeological sites at 270 m and 380 m (Corsica) | Mono monochrome camera, low-cost IMU, pressure sensor in one enclosure | Offline SfM (Colmap) trajectory, not an independent sensor | Not verified (site not reachable from this machine) | Not checked |
| LBL-AQUALOC (SYSU, RA-L 2023) | Aqualoc archaeological sequences + simulated LBL acoustics | Camera 20 Hz, IMU 200 Hz, magnetometer 200 Hz, pressure 60 Hz, 4 simulated LBL beacons 1 Hz, noisy fix 1 Hz | Colmap trajectory from Aqualoc used as truth | 10 bags, 56.2 GB total (README table; 2.0-10.5 GB each) | Not stated |
| SubPipe (REMARO, 2024) | OceanScan LAUV light AUV over a submarine pipeline | GoPro Hero 10 camera, second camera, side-scan sonar, depth, pressure, altitude, accel, gyro, RPM | Vehicle `EstimatedState.csv` (onboard navigation estimate, not independent GT); segmentation and sonar box labels | Full 28.0 GB; SubPipeMini 6.1 GB; SubPipeMini2 4.9 GB (Zenodo API) | CC-BY-4.0 (Zenodo) |

## What's in them

- Aqualoc: 17 sequences (abstract), as ROS bags and raw files. Harbor sequences are shallow
  and turbid; deep archaeological ones are dark with artificial light, sediment clouds and a
  moving manipulator arm.
- LBL-AQUALOC: the 10 archaeological sequences repackaged with simulated LBL time-of-arrival
  messages (`lbl_data/LBLdata`: beacon id, beacon XYZ, arrival time, mean sound speed). Made
  for acoustic-visual-inertial fusion (Acoustic-VINS).
- SubPipe: 5 chunks of pipeline-following survey with CSV sensor logs and image folders,
  segmentation masks for the pipe, COCO/YOLO labels on side-scan sonar images (about one
  sonar image per second).

## Download

```bash
# SubPipe (Zenodo record 12666132, CC-BY-4.0); start with the mini set
curl -L -o SubPipeMini2.zip "https://zenodo.org/records/12666132/files/SubPipeMini2.zip?download=1"
curl -L -o SubPipe.zip      "https://zenodo.org/records/12666132/files/SubPipe.zip?download=1"
git clone https://github.com/remaro-network/SubPipe-dataset   # docs, camera intrinsics, configs

# Aqualoc: http://www.lirmm.fr/aqualoc/  (returned a redirect loop / block from this network,
# 2026-11-06; try from another network)
# LBL-AQUALOC: README lists the bags but gives no download link (checked 2026-11-06);
# see https://github.com/SYSU-CPNTLab/LBL-AQUALOC-Dataset issues or contact authors
```

## Loading and tooling

- SubPipe: plain CSV + JPG, readable with pandas; `EstimatedState.csv` is the reference track.
- LBL-AQUALOC: ROS1 bags; the custom `lbl_data/LBLdata` message type must be built before
  `rosbag` can deserialize those topics (definition in README).
- Sonar processing: [sonar-SLAM](../../catalog/repos/jake3991__sonar-slam.md).
- Simulation when data is thin: [Stonefish](../../catalog/repos/patrykcieslak__stonefish.md),
  [HoloOcean](../../catalog/repos/byu-holoocean__holoocean-docs.md) (both simulate DVL and
  sonar; Stonefish also USBL, per their index entries).

## Hackathon fit

- Idea 17 (UUV DVL + USBL navigation in sim): replay LBL-AQUALOC ranging + IMU + depth as the
  "real data" leg of a sim-first demo, or use SubPipe depth/attitude logs to drive a
  dead-reckoning filter and compare to `EstimatedState`.
- None of these carry a real DVL stream; for DVL work, simulate it.

## Pitfalls

- GT quality: Aqualoc / LBL-AQUALOC truth is SfM, SubPipe truth is the vehicle's own nav
  filter. Report errors as "vs reference", not "vs ground truth".
- LBL measurements are simulated, not recorded.
- Aqualoc's host was unreachable from this network; mirror before the event.

## Sources

- arXiv 1809.07076 abstract (Aqualoc: three sites, depths, sensors, 17 sequences, SfM GT).
- https://github.com/SYSU-CPNTLab/LBL-AQUALOC-Dataset README (topics, rates, bag sizes), 2026-11-06.
- https://github.com/remaro-network/SubPipe-dataset README; Zenodo API record 12666132 (file sizes, license).
