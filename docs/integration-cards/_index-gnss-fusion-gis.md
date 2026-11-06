# Integration cards - GNSS, fusion, GIS, simulation

<!-- about: repo:rtklibexplorer/rtklib, repo:gnss-sdr/gnss-sdr, repo:osqzss/gps-sdr-sim, repo:stanford-navlab/gnss_lib_py, repo:commaai/laika, repo:semuconsulting/pyubx2, repo:semuconsulting/pygnssutils, repo:algafix/osnma, repo:geospace-code/pymap3d, repo:rlabbe/filterpy, repo:borglab/gtsam, repo:cra-ros-pkg/robot_localization, repo:i2nav-whu/kf-gins, repo:aceinna/gnss-ins-sim, repo:rpng/mins, repo:xiotechnologies/fusion, repo:ros-navigation/navigation2, repo:gazebosim/gz-sim, repo:learnsyslab/gym-pybullet-drones, repo:cesiumgs/cesium, repo:osgeo/gdal, repo:rasterio/rasterio, repo:bopen/elevation, repo:protomaps/pmtiles, repo:maplibre/maplibre-gl-js -->

What each card gives you in a hackathon. All 25 were written from READMEs, source files and issues read through the GitHub API. None of these repos was installed or run for the cards, and every snippet is marked "not run".

## GNSS processing and receivers

- [RTKLIB (demo5)](rtklibexplorer__rtklib.md) - Takes logs or RINEX and writes SPP/RTK/PPK/PPP `.pos` files. `str2str` and `rtkrcv` handle live NTRIP corrections.
- [GNSS-SDR](gnss-sdr__gnss-sdr.md) - Software receiver: IQ file or SDR in, RINEX/NMEA/RTCM/PVT out. Streams per-channel C/N0 telemetry over UDP and has built-in Galileo OSNMA.
- [GPS-SDR-SIM](osqzss__gps-sdr-sim.md) - Generates GPS L1 IQ test files for offline receiver testing. Covers file generation only, because over-the-air transmission is illegal. The repo is archived.
- [gnss_lib_py](stanford-navlab__gnss_lib_py.md) - Python toolkit: Android/RINEX 3/GSDC parsers, WLS, EKF and fault detection/exclusion, all on one `NavData` table.
- [laika](commaai__laika.md) - `AstroDog` computes satellite states and tropo/iono/DCB delays and returns corrected pseudoranges for your own filter.
- [pyubx2](semuconsulting__pyubx2.md) - Pure-Python UBX/NMEA/RTCM reader and writer. The card reads the jamming and spoofing flags from MON-RF, NAV-STATUS and NAV-PVT.
- [pygnssutils](semuconsulting__pygnssutils.md) - CLIs `gnssstreamer`, `gnssntripclient`, `gnssserver` and `pyrinexconv` for logging, NTRIP corrections, running your own caster, and converting raw logs to RINEX.
- [OSNMAlib](algafix__osnma.md) - Authenticates the Galileo OSNMA navigation message. Reads u-blox, Septentrio SBF, GNSS-SDR or galmon input and writes a JSON trust log.

## Estimation and sensor fusion

- [GTSAM](borglab__gtsam.md) - Pip-installable factor graph with ImuFactor/CombinedImuFactor plus GPSFactor/PseudorangeFactor. Build a GNSS/INS smoother and cut its GNSS to show outage behaviour.
- [FilterPy](rlabbe__filterpy.md) - NumPy KF/EKF/UKF/IMM filters and smoothers for quick prototypes. Note that 2.0.0 changes the API.
- [robot_localization](cra-ros-pkg__robot_localization.md) - ROS 2 EKF/UKF configured in YAML. Pair it with navsat_transform for dual-EKF GNSS + odometry + IMU fusion.
- [KF-GINS](i2nav-whu__kf-gins.md) - Small C++ loosely coupled GNSS/INS error-state EKF with a real dataset. The fastest outage baseline. GPL-3.0.
- [gnss-ins-sim](aceinna__gnss-ins-sim.md) - Python generator of trajectories with IMU, GNSS and magnetometer data, including per-segment GNSS visibility for outage scenarios.
- [MINS](rpng__mins.md) - Tightly coupled IMU/camera/LiDAR/wheel/GNSS filter with a built-in simulator and ROS-free CLIs. GPL-3.0.
- [Fusion (x-io)](xiotechnologies__fusion.md) - Embedded C AHRS that turns gyro + accel (+ mag) into a quaternion. The Python package `imufusion` has the same API.
- [pymap3d](geospace-code__pymap3d.md) - Converts between geodetic, ECEF, ENU, NED, AER and ECI frames, for example to move GNSS fixes into a filter's local frame. Watch ellipsoid vs MSL height.

## Autonomy and simulation

- [Nav2](ros-navigation__navigation2.md) - ROS 2 ground navigation stack driven from Python through `BasicNavigator`. Localization plugs in through the `map => odom` TF, and it can follow GPS waypoints.
- [Gazebo Sim](gazebosim__gz-sim.md) - Physics and sensor simulator (IMU, NavSat, mag, baro, cameras) used by PX4/ArduPilot SITL and the Nav2 demos.
- [gym-pybullet-drones](learnsyslab__gym-pybullet-drones.md) - PyBullet quadrotor sim with Gymnasium/PettingZoo environments for swarm and control logic. Ground-truth state only, with no sensor models.

## GIS, terrain and visualization

- [GDAL](osgeo__gdal.md) - Clip, reproject, hillshade, viewshed and point-sample DEMs and orthophotos. The Docker image is the least painful install.
- [Rasterio](rasterio__rasterio.md) - Pip-installable GeoTIFF/DEM reader that returns an array plus its affine transform, for TRN map lookups and orthophoto crops.
- [elevation](bopen__elevation.md) - `eio clip --bounds` downloads a cached 30/90 m DEM GeoTIFF for an AOI. Version 2.0 breaks 1.x commands, and products use different vertical datums.
- [PMTiles](protomaps__pmtiles.md) - Single-file tile archive cut to an AOI, for an offline basemap with no tile server. The CLI is in a separate repo, go-pmtiles.
- [MapLibre GL JS](maplibre__maplibre-gl-js.md) - WebGL2 browser map for the operator view: offline basemap, live track, 3D terrain. v6 is ESM-only.
- [CesiumJS](cesiumgs__cesium.md) - Browser 3D globe for replaying true vs estimated tracks on terrain (CZML, 3D Tiles). It can run offline, but the default viewer calls Cesium ion.
