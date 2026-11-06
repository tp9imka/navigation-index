# GVINS dataset

<!-- about: repo:hkust-aerial-robotics/gvins-dataset, repo:hkust-aerial-robotics/gvins -->

Three rosbags from HKUST Aerial Robotics released with GVINS (tightly coupled
GNSS-visual-inertial fusion, T-RO 2022). Small, focused: stereo + IMU + u-blox raw
pseudorange / Doppler + RTK truth, with PPS time sync between camera and receiver.

| Field | Value |
|---|---|
| Platform | Not described in the README beyond sequence names (sports_field, complex_environment, urban_driving) |
| Environment | Sports field (open sky), complex environment (mixed blockage), urban driving |
| Sensors and rates | VI-Sensor: stereo Aptina MT9V034 20 Hz + ADIS16448 IMU 200 Hz (hardware synced). u-blox ZED-F9P: raw measurements 10 Hz, PVT 10 Hz, GPS/Galileo/BeiDou/GLONASS ephemeris, PPS time pulse |
| Ground truth | ZED-F9P internal RTK fed by an RTCM stream from a station 3 km away; README cites 1 cm in open area. Truth quality degrades wherever RTK loses fix (check `carr_soln`) |
| Size | HF API (2026-11-06): sports_field.bag 22.0 GB, complex_environment.bag 17.3 GB, urban_driving.bag 35.9 GB; total 75.2 GB |
| License | CC BY-NC-SA 4.0 (README) |
| Format | ROS1 bags with `gnss_comm` custom messages |
| Index | [GVINS-Dataset](../../catalog/repos/hkust-aerial-robotics__gvins-dataset.md), [GVINS](../../catalog/repos/hkust-aerial-robotics__gvins.md), [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md) |

## What's in it

| Bag | Duration | Size |
|---|---|---|
| sports_field | 25 min | 22.0 GB |
| complex_environment | 32 min | 17.3 GB |
| urban_driving | 41 min | 35.9 GB |

Topics: `/cam0/image_raw`, `/cam1/image_raw`, `/imu0`, `/ublox_driver/range_meas`
(raw), `/ublox_driver/receiver_pvt`, `/ublox_driver/ephem`, `/ublox_driver/glo_ephem`,
`/ublox_driver/iono_params`, `/ublox_driver/time_pulse_info`, `/external_trigger`.
GNSS ephemeris RINEX is in the repo (`data/ephemeris_rinex/`).

## Download

```bash
# Hugging Face (moved there 2026-08-29; the old OneDrive link is dead per README)
B=https://huggingface.co/datasets/Shawn202606/GVINS-Dataset/resolve/main
wget $B/complex_environment.bag     # 17.3 GB, smallest
wget $B/checksum.txt
# or: huggingface-cli download Shawn202606/GVINS-Dataset complex_environment.bag --repo-type dataset
git clone https://github.com/HKUST-Aerial-Robotics/GVINS-Dataset   # toolkit + ephemeris RINEX
```

## Loading and tooling

- [GVINS](../../catalog/repos/hkust-aerial-robotics__gvins.md) runs on these bags directly (ROS1, needs `gnss_comm`).
- Toolkit (`rosrun gvins_dataset_toolkit bag2rinex`, `bag2rtk_solution`) exports RINEX
  observations and an RTK CSV `gnss_ts_ns, ecef_xyz, enu_v, fix_type, ..., carr_soln`.
  Paths are hard-coded in the .cpp files; edit before `catkin_make`.
- Once in RINEX, use RTKLIB or [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md).

## Hackathon fit

- Idea 4 (raw GNSS spoofing / fault detector): inject a synthetic pseudorange ramp into
  `range_meas` and show the VIO-consistency check flags it. Real raw data, small enough to pre-download.
- Reference arch 4.3 (fusion with integrity): the canonical GNSS + VIO tight-coupling demo.
- Idea 10 (VIO => GPS-free flight): measure drift when GNSS is removed mid-run, using RTK as truth.

## Pitfalls

- Custom `gnss_comm` message types: plain `rosbag` tools will not decode them without the
  message definitions; `rosbags` needs the .msg files registered.
- Truth is the same receiver's RTK solution, not an independent INS. Filter on `carr_soln == 2`.
- Non-commercial license.
- PPS trigger runs at 0.2 Hz; time alignment depends on `/external_trigger` + `/time_pulse_info`.

## Sources

- https://github.com/HKUST-Aerial-Robotics/GVINS-Dataset README via `gh api`, 2026-11-06
- https://huggingface.co/api/datasets/Shawn202606/GVINS-Dataset/tree/main (file sizes), 2026-11-06
