# OB_GINS - integration card
<!-- about: repo:i2nav-whu/ob_gins -->
One-line: offline sliding-window factor-graph GNSS/INS(/odometer) integrator with IMU preintegration and a built-in periodic GNSS outage switch; the smoother counterpart to KF-GINS on the same file formats, so you can show filter vs optimization drift through outages from one config edit.

| | |
|---|---|
| Install | `git clone https://github.com/i2Nav-WHU/OB_GINS.git && cd OB_GINS && mkdir build && cd build && cmake ../ -DCMAKE_BUILD_TYPE=Release && make -j8` (README; README pins gcc-8 on Ubuntu 18.04). System deps: Ceres, Eigen3 (`libeigen3-dev`), yaml-cpp (`libyaml-cpp-dev`); abseil-cpp is vendored in `src/thirdparty/`. C++17 (`CMakeLists.txt`). |
| Runs on | Linux (README recommends Ubuntu 18.04/20.04, gcc>=8 or clang>=6). CPU only, batch over files, no ROS, no real-time interface. Last push 2024-03-27. |
| Inputs | Same formats as KF-GINS / awesome-gins-datasets. IMU text (`imufile`, `imudatalen` 7 or 8 columns): GNSS seconds of week (s), incremental angle x y z (rad), incremental velocity x y z (m/s), optional column 8 = odometer speed (m/s; `ImuFileLoader` multiplies by dt; 9 columns are averaged as two wheels). IMU frame forward-right-down. GNSS text (`gnssfile`, `.pos`, 7 columns): seconds of week, lat (deg), lon (deg), ellipsoid height (m), position STD N E D (m); a 13-column variant reads STD from columns 8-10. YAML (`dataset/ob_gins.yaml`): `starttime`/`endtime` (SOW), `windows` (s), `num_iterations`, `initvel` NED (m/s), `initatt` roll-pitch-yaw (deg), `initgb` (deg/h), `initab` (mGal), `imudatarate` (Hz), `isearth`, `antlever` and `odolever` (m, IMU front-right-down), `bodyangle` (deg), `odometer.isuseodo/std (m/s)/srw (PPM)`, `imumodel.arw (deg/sqrt(h)) vrw (m/s/sqrt(h)) gbstd (deg/h) abstd (mGal) corrtime (h)`, `isuseoutage/outagetime/outagelen/outageperiod`, `gnssthreshold` (m), `is_outlier_culling`. |
| Outputs | In `outputpath`: `OB_GINS_TXT.nav` text, 11 columns: 0 (week placeholder), SOW, lat (deg), lon (deg), h (m), vel N E D (m/s), roll pitch yaw (deg). `OB_GINS_IMU_ERR.bin` binary doubles: SOW, gyro bias x y z (deg/h), accel bias x y z (mGal), odometer scale (`writeNavResult` in `src/ob_gins.cc`). Demo `dataset/truth.nav` for comparison. |
| Key API / entry points | CLI `./bin/ob_gins <config.yaml>` (`src/ob_gins.cc`, `main`). Preintegration factory `Preintegration::createPreintegration(parameters, imu, state, options)` with `Preintegration::getOptions(isuseodo, isearth)` selecting `preintegration_normal`, `preintegration_odo`, `preintegration_earth`, `preintegration_earth_odo`. Factors: `src/factors/gnss_factor.h`, `preintegration/preintegration_factor.h`, `preintegration/imu_error_factor.h`, marginalization in `factors/marginalization_factor.h` / `marginalization_info.h`, `PoseManifold` (`factors/pose_manifold.h`, a `ceres::Manifold`). File IO `ImuFileLoader`, `GnssFileLoader`, `FileSaver`. |
| Time to first result | Estimate: 30-60 min to build and run the demo (ADIS16465 IMU at 200 Hz + 1 Hz RTK, about 1617 s of data) if a compatible Ceres is present; add 1-2 h if Ceres must be built from source. 2-4 h to convert your own log. Assumes Linux with cmake. |
| License | GPL-3.0 (GitHub, README, source headers). README: commercial use => contact Prof. Xiaoji Niu; academic use => cite the listed papers. |

## Minimal usage
From README section 2 and `dataset/ob_gins.yaml`. Not run.

```bash
git clone https://github.com/i2Nav-WHU/OB_GINS.git && cd OB_GINS
mkdir build && cd build && cmake ../ -DCMAKE_BUILD_TYPE=Release && make -j8 && cd ..
./bin/ob_gins ./dataset/ob_gins.yaml    # writes dataset/OB_GINS_TXT.nav and OB_GINS_IMU_ERR.bin
```

Outage experiment, config only: the shipped demo already has `isuseoutage: true`, `outagetime: 357900`, `outagelen: 60`, `outageperiod: 150`, i.e. starting at SOW 357900, skip 60 GNSS records every 150 s. Set `isuseoutage: false` for the GNSS-always baseline, then diff both `.nav` files against `dataset/truth.nav`. Toggle `odometer.isuseodo` to show how much a wheel-speed constraint helps during the gaps. Run [KF-GINS](./i2nav-whu__kf-gins.md) on the same IMU/GNSS files (with matching gaps cut by hand, since KF-GINS has no outage switch) for the filter-vs-smoother plot.

## Wiring it into a nav stack
- Data prep is the same as [KF-GINS](./i2nav-whu__kf-gins.md): decode u-blox with [pyubx2](./semuconsulting__pyubx2.md), post-process RTK with [RTKLIB](./rtklibexplorer__rtklib.md), integrate IMU rates to increments. Synthetic IMU/GNSS with outages from [gnss-ins-sim](./aceinna__gnss-ins-sim.md).
- Scoring: convert the `.nav` LLA to local ENU with [pymap3d](./geospace-code__pymap3d.md) and compute drift vs time-since-outage, or write TUM files for [evo](./michaelgrupp__evo.md).
- Visual/GNSS/INS extension from the same group: [IC-GVINS](../../catalog/repos/i2nav-whu__ic-gvins.md). Generic factor-graph library with IMU preintegration: [GTSAM](./borglab__gtsam.md).
- No ROS or MAVLink: for live use you would wrap the sliding-window loop in `ob_gins.cc` yourself; for an on-robot smoother look at [fuse](./locusrobotics__fuse.md) or GTSAM instead.
- Catalog: [OB_GINS page](../../catalog/repos/i2nav-whu__ob_gins.md).

## Gotchas
- Ceres version: README says Ceres 2.0.0 or 2.1.0, but the code uses `ceres::Manifold` (`pose_manifold.h`). Open issue #22: build fails with Ceres 2.0.0 + Eigen 3.3.7; switching to Ceres 2.2.0 fixed it (Ubuntu 22.04 commenter set `Ceres_DIR` in `CMakeLists.txt`). Check your Ceres before planning the hackathon around it.
- GNSS must be 1 Hz (maintainer reply in closed #19) and STD must be non-zero (same thread: zero STD breaks the solve with "Residual and Jacobian evaluation failed").
- `gnssthreshold` (demo 0.2 m) silently skips every GNSS record whose N, E or D STD exceeds it (`ob_gins.cc` read loop). With single-point or float GNSS (metre-level STD) almost nothing gets fused; raise it to match your receiver.
- Outage counts records, not seconds, and triggers on `lround(gnss.time) == outagetime`; with non-integer or missing epochs the outage may never fire.
- No alignment: position starts at the first GNSS fix, but `initatt` (including yaw, deg) and `initvel` must come from the config.
- Mixed units as in KF-GINS: gyro bias deg/h, accel bias mGal, odometer scale PPM. Consumer MEMS needs much larger `imumodel` values than the ADIS16465 demo.
- Heavy clone: `dataset/ADIS16465.txt` about 47 MB and `dataset/truth.nav` about 39 MB (GitHub tree sizes).
- Issues are mostly in Chinese (#13 how to add wheel odometer to the IMU file, #21 `NUM_STATE`); README offers a QQ group.
- GPL-3.0.

## Alternatives
- [KF-GINS](./i2nav-whu__kf-gins.md): same group and formats, error-state EKF, simpler to build (all deps vendored); prefer as the first baseline.
- [GTSAM](./borglab__gtsam.md): `CombinedImuFactor` + GPS factors, Python bindings, iSAM2 for live use.
- [IC-GVINS](../../catalog/repos/i2nav-whu__ic-gvins.md): when a camera is available and you want vision to carry the outage.

Sources: `README.md`, `CMakeLists.txt`, `dataset/ob_gins.yaml`, `dataset/GNSS_RTK.pos` (first rows), `src/ob_gins.cc` (main, outage and threshold loop, `writeNavResult`), `src/fileio/imufileloader.h`, `src/fileio/gnssfileloader.h`, `src/common/types.h`, `src/factors/pose_manifold.h`, repo tree with sizes; i2Nav-WHU/awesome-gins-datasets `README.md` (format tables); issue search (all issues; read #19, #22).
