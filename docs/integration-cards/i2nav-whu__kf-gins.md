# KF-GINS - integration card
<!-- about: repo:i2nav-whu/kf-gins -->
One-line: a small, readable C++ 21-state error-state EKF for loosely coupled GNSS/INS with a bundled real dataset, the quickest credible baseline for "what happens to INS when GNSS drops".

| | |
|---|---|
| Install | `git clone https://github.com/i2Nav-WHU/KF-GINS.git && cd KF-GINS && mkdir build && cd build && cmake ../ -DCMAKE_BUILD_TYPE=Release && make -j8` (README). Eigen3, abseil-cpp, yaml-cpp are vendored in `ThirdParty/`. Needs only cmake + a C++ compiler. |
| Runs on | Linux (recommended, Ubuntu 18.04/20.04 per README), macOS (incl. Apple M-series per the VSCode debug notes), Windows MSVC. CPU only, no ROS. |
| Inputs | Text files. IMU: GNSS seconds of week, X-Y-Z incremental angles (rad), X-Y-Z incremental velocity (m/s), IMU frame forward-right-down. GNSS: seconds of week, lat (deg), lon (deg), ellipsoid height (m), position STD N-E-D (m). YAML config with full initial state, IMU noise (ARW, VRW, bias/scale std, correlation time) and antenna lever arm. |
| Outputs | Text files in `outputpath`: nav result (week, SOW, lat, lon, h, vel NED, roll-pitch-yaw deg), IMU error estimates (gyro bias deg/h, accel bias mGal, scale factors ppm), state STD. `scripts/plot_navresult.py` plots them. |
| Key API / entry points | CLI `./bin/KF-GINS <config.yaml>`. Library class `GIEngine` (`src/kf-gins/gi_engine.h`): `addImuData(const IMU&, bool compensate=false)`, `addGnssData(const GNSS&)`, `newImuProcess()`, `getNavState()`, `getCovariance()`, plus internals `insPropagation`, `gnssUpdate`, `EKFPredict`, `EKFUpdate`, `stateFeedback`. Mechanization in `insmech.cpp`. |
| Time to first result | Estimate: 15-30 min to build and run the demo dataset (clone is large, see gotchas). 2-4 h to convert your own IMU/GNSS log into the column formats and tune the noise block. Assumes Linux/macOS with cmake installed. |
| License | GPL-3.0 (GitHub and README). README: commercial use => contact Prof. Xiaoji Niu. |

## Minimal usage
From README sections 1.3 and 3.1. Not run.

```bash
git clone https://github.com/i2Nav-WHU/KF-GINS.git && cd KF-GINS
mkdir build && cd build && cmake ../ -DCMAKE_BUILD_TYPE=Release && make -j8 && cd ..
./bin/KF-GINS ./dataset/kf-gins.yaml          # demo: Leador-A15 IMU at 200 Hz + GNSS-RTK
python3 scripts/plot_navresult.py              # plots against dataset/truth.nav
```

Outage experiment: copy `dataset/GNSS-RTK.txt`, delete rows in a time window (e.g. 60-120 s), point `gnsspath` at the copy, rerun, diff the result against `truth.nav`. There is no built-in outage switch in `kf-gins.yaml`.

## Wiring it into a nav stack
- Data prep: decode a u-blox log with [pyubx2](./semuconsulting__pyubx2.md) or post-process to RTK with [RTKLIB](./rtklibexplorer__rtklib.md), then write the 7-column GNSS file. IMU rates must be integrated to increments (multiply by dt).
- Synthetic input: [gnss-ins-sim](./aceinna__gnss-ins-sim.md) generates IMU and GNSS with per-segment GNSS visibility; convert units (rad/s => rad increments, LLA rad => deg).
- Datasets in the same format: i2Nav awesome-gins-datasets (linked from README).
- Side-by-side: [OB_GINS](../../catalog/repos/i2nav-whu__ob_gins.md) (same formats, optimization-based) and [GTSAM](./borglab__gtsam.md); Python stdlib version of the idea in [samples/gnss-ins-ekf-outage](../../samples/gnss-ins-ekf-outage).
- No ROS or MAVLink interface: for live use wrap `GIEngine` in your own node and publish NavSatFix/Odometry; convert LLA to local frames with [pymap3d](./geospace-code__pymap3d.md).
- Catalog: [KF-GINS page](../../catalog/repos/i2nav-whu__kf-gins.md).

## Gotchas
- IMU input is increments (rad, m/s per sample), not rates. Feeding rates is the commonest mistake; closed issues #23 and #25 ask about the conversion and gravity.
- No coarse alignment: README 2.3 says all initial states, including attitude, must be given in the config. Closed issue #28 asks about computing initial yaw. Without a good initial heading the filter diverges.
- Clone is heavy: `dataset/Leador-A15.txt` is about 67 MB and `dataset/truth.nav` about 95 MB (GitHub contents API sizes), stored as normal git blobs.
- Units are mixed on purpose: gyro bias deg/h, accel bias mGal, scale factor ppm, ARW deg/sqrt(h). Consumer MEMS needs much larger values than the navigation-grade demo IMU.
- Windows: no Chinese characters in file paths (config comment); executable may land in `bin/Release`.
- Loosely coupled position only: no pseudorange, no velocity/heading measurements (closed issue #22 asks about dual-antenna yaw).
- GPL-3.0: linking it into a product forces GPL; fine for a hackathon demo, check before shipping.

## Alternatives
- [OB_GINS](../../catalog/repos/i2nav-whu__ob_gins.md): same group and formats, sliding-window optimization; better through outages, heavier (Ceres).
- [NaveGo](../../catalog/repos/rodralez__navego.md): MATLAB GNSS/INS toolbox if the team lives in MATLAB.
- [pyins](../../catalog/repos/nmayorov__pyins.md) or [FilterPy](./rlabbe__filterpy.md): stay in Python for fast iteration.

Sources: `README.md`, `dataset/kf-gins.yaml`, `src/kf-gins/gi_engine.h`, repo and `src/`, `scripts/`, `dataset/` listings, issue search (all issues, sorted by recency).
