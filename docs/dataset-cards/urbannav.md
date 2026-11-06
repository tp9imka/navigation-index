# UrbanNav (Hong Kong and Tokyo)

<!-- about: repo:ipnl-polyu/urbannavdataset -->

Open urban-canyon positioning dataset from PolyU IPNL (Hong Kong) plus a smaller Tokyo set. Built for GNSS NLOS / multipath research with raw RINEX next to IMU,
lidar and camera. Paper: Hsu et al., NAVIGATION 70(4), 2023.

| Field | Value |
|---|---|
| Platform | Car: Honda Fit (Hong Kong), Toyota Rush (Tokyo) |
| Environment | Hong Kong medium / deep / harsh urban canyons and a sea tunnel; Tokyo Odaiba and Shinjuku |
| Sensors and rates | HK: Velodyne HDL-32E 10 Hz + 2 slant lidars (VLP-16, Lslidar C16), Xsens MTi-10 IMU 400 Hz, phone IMU (Xiaomi 8) 239 Hz, 2x u-blox F9P + EVK-M8T + NovAtel Flexpak6 GNSS at 1 Hz (RINEX 3.02), ZED2 stereo 15 Hz. Tokyo: VLP-32C 10 Hz, u-blox F9P 5 Hz, Trimble NetR9 10 Hz, Tamagawa TAG264 IMU 50 Hz, base station RINEX 1 Hz |
| Ground truth | HK: NovAtel SPAN-CPT RTK GNSS/INS post-processed with Inertial Explorer, 1 Hz, README states RMSE 5 cm. Tokyo: Applanix POS LV620, 10 Hz, README states RMSE 5 cm. Harsh-Urban-1 GT only partly verified (README) |
| Size | README table: HK Medium-Urban-1 33.7 GB, Deep-Urban-1 63.9 GB, Harsh-Urban-1 147 GB, Tunnel-1 17 GB, pilot sets 42.9 / 27.0 GB, Tokyo 4.14 GB. HEAD (2026-11-06): Medium-Urban-1 bag 35.2 GB, Tunnel-1 bag 18.0 GB, Tokyo_Data.zip 4.45 GB, Medium-Urban-1 Xsens CSV 110 MB, its GT txt 140 KB |
| License | MIT, explicitly covering the data files (README "License" section) |
| Format | ROS1 bags (sensors + `/novatel_data/inspvax`), RINEX 3.02, CSV IMU, text GT |
| Index | [UrbanNav](../../catalog/repos/ipnl-polyu__urbannavdataset.md), [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md), [evo](../../catalog/repos/michaelgrupp__evo.md) |

## What's in it

| Sequence | Duration | Path | Notes |
|---|---|---|---|
| HK-Medium-Urban-1 (TST) | 785 s | 3.64 km | F9P malfunction in one period (issue #11) |
| HK-Deep-Urban-1 (Whampoa) | 1536 s | 4.51 km | small tunnels, loops |
| HK-Harsh-Urban-1 (Mongkok) | 3367 s | 4.86 km | GT not in bag, partial |
| HK-Tunnel-1 | 398 s | 3.15 km | full GNSS loss in tunnel |
| TK-20181219 (Odaiba, Shinjuku) | - | > 10 km | GNSS + lidar + IMU; extrinsics not available |

GNSS RINEX, Xsens CSV, phone IMU CSV and GT are separate small downloads per sequence, so
GNSS-only work does not need the bags.

## Download

```bash
# GNSS/INS only, no ROS: GT + IMU CSV for Medium-Urban-1 (about 110 MB)
curl -L -o UrbanNav_TST_GT_raw.txt "https://www.dropbox.com/s/twsvwftucoytfpc/UrbanNav_TST_GT_raw.txt?dl=1"
curl -L -o xsense_imu_medium_urban1.csv "https://www.dropbox.com/s/2rh1rs15ihpf63u/xsense_imu_medium_urban1.csv?dl=1"
# RINEX for that run is a Dropbox shared folder; download the folder as zip in a browser:
#   https://www.dropbox.com/sh/2haoy68xekg95zl/AAAkcN4FwhFxkPY1lXsxbJrxa?dl=0
# Tokyo GNSS + base + IMU + Applanix truth (4.45 GB)
curl -L -o Tokyo_Data.zip "https://www.dropbox.com/s/isu1bugpgr8dpas/Tokyo_Data.zip?dl=1"
# Full sensor bag, tunnel run (18 GB)
curl -L -o UrbanNav-HK_CHTunnel-20210518_sensors.bag "https://www.dropbox.com/s/8vwkero6boujtzb/UrbanNav-HK_CHTunnel-20210518_sensors.bag?dl=1"
```

Swapping `?dl=0` for `?dl=1` on the README links gave direct downloads for single files.
Shared folders (`/sh/...`, `/scl/fo/...`) were not HEAD-checked.

## Loading and tooling

- RINEX: RTKLIB (README suggests it), or [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md)
  `glp.RinexObs(path)`; PolyU's GraphGNSSLib (linked from README, not indexed) publishes RINEX as ROS topics.
- GT text: lat/lon/height per epoch; convert to ENU and compare with `evo_ape` after writing TUM format.
- Bags: ROS1 Noetic or `rosbags` (pure Python) to read without ROS.

## Hackathon fit

- Idea 4 (Android raw GNSS spoofing detector): not Android logs, but the multi-receiver
  RINEX plus truth is a good place to build NLOS / consistency checks before switching to phone data.
- Idea 5 (INS holdover budget): Tunnel-1 is a real, labelled GNSS outage with a 400 Hz IMU and truth on both ends.
- Reference arch 4.3 (multi-sensor fusion with integrity): GNSS + IMU + lidar with 5 cm truth in deep canyons.

## Pitfalls

- Bags are 17-147 GB each; venue Wi-Fi will not carry them. Pre-download the tunnel run only if you need lidar.
- Harsh-Urban-1 truth is partial; score only where truth exists.
- Tokyo: no lidar calibration or extrinsics (README warns); use it for GNSS/IMU only.
- GT at 1 Hz in HK; interpolate carefully when scoring 400 Hz outputs.

## Sources

- https://github.com/IPNL-POLYU/UrbanNavDataset README (sensors, sizes, GT, license), read via `gh api` 2026-11-06
- HEAD on the Dropbox `?dl=1` URLs above, 2026-11-06
