# M2DGR

<!-- about: repo:sjtu-visys/m2dgr -->

Multi-sensor, multi-scenario SLAM dataset from a ground robot on the SJTU campus (Yin et al.,
RA-L / ICRA 2022). Its distinguishing feature is indoor-outdoor transitions (lifts, halls,
dark rooms) with thermal, event and raw GNSS alongside lidar and cameras.

| Field | Value |
|---|---|
| Platform | Wheeled ground robot |
| Environment | SJTU campus: streets, gates, circles, halls, doors, lifts, bright and dark rooms; day and night |
| Sensors and rates | Velodyne VLP-32C 10 Hz; 6 surround fisheye + 1 sky-pointing fisheye RGB (FLIR Pointgrey, 1280x1024, 15 Hz); PLUG 617 thermal 640x512 25 Hz; Inivation DVXplorer event 640x480; Realsense D435i RGB-D 15 Hz + IMU 200 Hz; Handsfree A9 9-axis IMU 150 Hz; u-blox M8T GNSS 1 Hz (raw `rxmraw`, ephemeris in bag); Xsens MTi-680G GNSS-RTK/IMU 100 Hz |
| Ground truth | Outdoor: RTK/INS (Xsens MTi-680G, README states 2 cm RTK precision). Hall/door/lift: Leica MS60 laser scanner (stated 1 mm + 1.5 ppm). Room/dark room: Vicon Vero 2.2 mocap (stated 1 mm, 50 Hz) |
| Size | README table: 36 sequences, 1220.6 GB total; per sequence 14-86 GB (room_01 14.0 GB smallest, street_010 86.2 GB). Not HEAD-verified: OneDrive returned 403 to HEAD on 2026-11-06 |
| License | README says MIT "provided for academic purpose", commercial use by contact. Treat as academic-only in practice |
| Format | ROS1 bags (compressed images); GT TUM text files in the repo under `GT/` (Git LFS; gate_01.txt is 1.8 MB) |
| Index | [M2DGR](../../catalog/repos/sjtu-visys__m2dgr.md), [evo](../../catalog/repos/michaelgrupp__evo.md) |

## What's in it

| Scenario | # seq | Size GB | Duration s | Distance m | GT |
|---|---|---|---|---|---|
| Street | 10 | 590.7 | 7958 | 7728 | RTK/INS |
| Circle | 2 | 50.6 | 478 | 618 | RTK/INS |
| Gate | 3 | 65.9 | 782 | 248 | RTK/INS |
| Walk | 1 | 21.5 | 291 | 263 | RTK/INS |
| Hall | 5 | 117.4 | 1226 | 845 | Leica |
| Door | 2 | 46.0 | 588 | 200 | Leica |
| Lift | 4 | 112.1 | 1224 | 266 | Leica |
| Room | 3 | 45.3 | 275 | 144 | Mocap |
| Roomdark | 6 | 171.1 | 866 | 396 | Mocap |

(Figures from the README overview table.) Follow-ups M2DGR-plus and Ground-Challenge
are separate repos, not indexed here.

## Download

```bash
# GT for all sequences (small, Git LFS)
git clone https://github.com/SJTU-ViSYS/M2DGR && cd M2DGR && git lfs pull --include "GT/*"
# Bags: per-sequence OneDrive links in the README table, e.g. gate_01 (16.4 GB):
#   https://1drv.ms/u/c/3e825cd7abd6dff7/IQCJ-bCAU-oCQKCGyVUfR94lAZyvNsvenbkCjhgTJ0tN_Ho
# Browser download; OneDrive did not serve a direct HEAD.
```

Smallest useful: `room_01` (14.0 GB, mocap GT) for indoor VIO, `gate_01` (16.4 GB, RTK GT,
dark) or `walk_01` (21.5 GB) for GNSS + vision.

## Loading and tooling

- ROS1 bags; `rosbags` for ROS-free Python reading.
- Raw u-blox: README points to `TakahashiJinxu/ublox2rinex` to produce RINEX for RTKLIB or
  [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md).
- GT is TUM format (`t x y z qx qy qz qw`, 100 Hz in gate_01); the outdoor file checked holds ECEF coordinates, not a local frame. README evaluates with `evo_ape tum street_07.txt your_result.txt -vap`.
- The README lists LIO-SAM, ORB-SLAM3, LVI-SAM and others already configured for M2DGR.

## Hackathon fit

- Reference arch 4.3 (fusion with integrity): indoor-outdoor transitions where GNSS appears
  and disappears are a natural "switch sources and keep a bounded error" demo.
- Idea 10 (VIO without GNSS) on dark / lift sequences, with thermal or event as the fallback camera.

## Pitfalls

- Bags are big and OneDrive is browser-only; budget hours, not minutes.
- README notes the OneDrive migration (Oct 2025, about 1.2 TB) was ongoing; some links may move.
- Outdoor GT positions are ECEF (checked gate_01.txt): convert or align before comparing to a local-frame estimate.
- Raw GNSS is u-blox M8T at 1 Hz, GPS/BeiDou only.
- License wording mixes "MIT" and "academic purpose"; do not assume commercial rights.

## Sources

- https://github.com/SJTU-ViSYS/M2DGR README via `gh api`, 2026-11-06 (sensors, table, license, links)
- HEAD on a OneDrive link => 301 then 403, 2026-11-06
