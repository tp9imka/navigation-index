# UrbanLoco

<!-- about: res:polyu-urbanloco-dataset -->

Urban driving dataset from PolyU IPNL and UC Berkeley MSC Lab (ICRA 2020), recorded in
Hong Kong and San Francisco to stress GNSS outliers and non-Gaussian errors. Predecessor
of [UrbanNav](urbannav.md) from the same Hong Kong group.

| Field | Value |
|---|---|
| Platform | Car: Honda Fit (Hong Kong), Toyota Prius (California) per the project site |
| Environment | Hong Kong urban canyons (Whampoa, Ma Tau Kok); San Francisco (Bay Bridge, Market St, Russian Hill, Chinatown, Coit Tower, Lombard St) |
| Sensors and rates | HK: Velodyne HDL-32E 10 Hz, Xsens MTi-10 IMU 100 Hz, u-blox M8T 1 Hz (raw pseudorange/Doppler in bag), sky-pointing fisheye camera 10 Hz. CA: RoboSense RS-LiDAR-32 10 Hz, Xsens MTi-10 100 Hz, u-blox M8T 1 Hz, 6 cameras 10 Hz |
| Ground truth | NovAtel SPAN-CPT RTK GNSS/INS. GitHub README states RMSE 5 cm at 1 Hz; site's platform page says SPAN-CPT 20 Hz (HK) and lists a NovAtel FlexPak6 RTK GNSS at 10 Hz for CA. The two pages disagree; check the bag |
| Size | Stated per sequence on README and site: CA 44.6, 60.6, 67.2, 54.3, 9.73, 9.83, 40.1 GB (sum 286 GB); HK 41.6, 24.0, 62.3, 27.9, 6.11 GB (sum 162 GB). Total about 448 GB stated. Not HEAD-verified: all sequences sit in one Dropbox shared folder |
| License | CC BY-NC-SA 4.0, non-commercial academic use (project site) |
| Format | ROS bags. README says "majority Hong Kong data is provided in ROS2 format" |
| Index | [UrbanLoco](../../catalog/resources/polyu-urbanloco-dataset.md), [evo](../../catalog/repos/michaelgrupp__evo.md), [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md) |

## What's in it

12 sequences (7 California, 5 Hong Kong), each one ROS bag with GNSS fix
(`/ublox_node/fix`), lidar, camera(s), IMU and `/novatel_data/inspvax` truth. HK data also
holds u-blox raw measurements (`/ublox_/...`) and a post-processed `/GNSS` raw topic; some
sequences ship RINEX. The fisheye sky camera is meant for NLOS satellite classification.

## Download

```bash
# All sequences: Dropbox shared folder (open in a browser, pick single files)
#   https://www.dropbox.com/scl/fo/zrsmoddbq96t4go1wbxwp/AJw_DGVXng06DmLx9j9iQMs?rlkey=rk11n8tt62ejbg8mbixrm6quz&dl=0
# Smallest useful subset: HK-Data20190117 (6.11 GB) or CAColiTower (9.73 GB)
# Helper ROS package (GT and u-blox => KML)
git clone https://github.com/weisongwen/UrbanLoco
```

No per-file direct links are published, so there is no one-line `curl` for a single bag.
Baidu mirror links are in the README for mainland China users.

## Loading and tooling

- ROS1 / ROS2 bag tools, or the pure-Python `rosbags` package to read without a ROS install.
- `weisongwen/UrbanLoco` (not in the index) has a catkin package to export truth and
  u-blox solutions to KML for a quick visual check.
- Score with [evo](../../catalog/repos/michaelgrupp__evo.md) after converting INSPVAX lat/lon/h to a local ENU TUM file.

## Hackathon fit

- Idea 4 (raw GNSS spoofing/fault detector) and reference arch 4.3 (fusion with integrity):
  u-blox raw pseudoranges in deep canyons with a truth trajectory to label faulty epochs.
- Sky fisheye + raw GNSS is a ready-made NLOS exclusion demo.
- For a fresh GNSS/INS/lidar build, [UrbanNav](urbannav.md) is the newer, better documented, MIT-licensed choice.

## Pitfalls

- Sensor descriptions differ between the website and the GitHub README (GT rate, GNSS
  receiver "M8T or F9P (to be updated)"); verify by inspecting the bag.
- Mixed ROS1/ROS2 formats.
- Non-commercial license, unlike UrbanNav.
- Bag timestamps are Ubuntu time; SPAN truth is in GPS time (site's data-format page).

## Sources

- https://advdataset2019.wixsite.com/urbanloco (+ /data-collection-platform, /data-format, /california), fetched 2026-11-06
- https://github.com/weisongwen/UrbanLoco README via `gh api`, 2026-11-06
