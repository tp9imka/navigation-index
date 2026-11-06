# tercom_nav - integration card
<!-- about: repo:mzahana/tercom_nav -->
One-line: a ROS 2 Humble package that turns baro + single-beam range + IMU into terrain-matching position fixes against a GeoTIFF DEM and fuses them in a 15-state ESKF - a complete GNSS-denied terrain-nav loop you can run against PX4 SITL.

| | |
|---|---|
| Install | Into a ROS 2 workspace: `cd ~/ros2_ws/src && git clone https://github.com/mzahana/tercom_nav && cd ~/ros2_ws && rosdep install --from-paths src --ignore-src -r -y && colcon build --packages-select tercom_nav && source install/setup.bash`, plus `pip install numpy scipy rasterio pyproj Pillow pandas matplotlib`. ament_python, version 0.1.0 (package.xml). No releases. The simulation side lives in [riotu-lab/gps_denied_navigation_sim](https://github.com/riotu-lab/gps_denied_navigation_sim) (its `install.sh` builds PX4 SITL on a `navsat_callback` branch, clones mavros and tercom_nav), with a Docker image `riotu-lab/gps_denied_navigation_docker`. |
| Runs on | Ubuntu 22.04 + ROS 2 Humble (README: "tested on Humble"); sim stack: Gazebo Garden + PX4 SITL + MAVROS (gps_denied_navigation_sim README). Pure Python + NumPy, CPU only; no GPU needed. Core library is ROS-free and unit-testable with `pytest test/ -v` (README: 46 tests). |
| Inputs | DEM: any GeoTIFF readable by rasterio (`dem_file`, required); geographic CRS is auto-reprojected to UTM (`core/dem_manager.py`), nodata `-9999.0` by default. Optional JSON sidecar `dem_metadata_file`. Parameter `dem_elevation_offset` (m) aligns DEM datum with sensor altitude (taif config: 134.3 m). Live topics (from launch remaps, `mavros_ns` default `target/mavros`): `mavros_msgs/Altitude` (baro AMSL), `sensor_msgs/LaserScan` on `/scan` (single-beam range, `ranges[0]`), `sensor_msgs/Imu`, `sensor_msgs/NavSatFix` (GPS, init only), `geometry_msgs/TwistStamped` velocity, `nav_msgs/Odometry`. `world_origin_lat/lon/alt` must match the Gazebo world. |
| Outputs | `/tercom/tercom_node/position_fix` (`geometry_msgs/PointStamped`, UTM easting/northing, `frame_id=utm`), `/tercom/tercom_node/match_quality` (`[MAD m, discrimination, roughness m, noise var]`), `/tercom/eskf_node/odom` (`nav_msgs/Odometry`, local ENU, 6x6 covariance, at `imu_rate_hz`), `/tercom/eskf_node/global` (`NavSatFix`, 1 Hz), filter state/health topics, RViz markers, CSV log under `/tmp/tercom_logs/`. |
| Key API / entry points | Launch: `tercom_nav.launch.py` (4 nodes), `tercom_standalone.launch.py` (tercom + eskf). Console scripts (setup.py): `dem_server`, `tercom_node`, `eskf_node`, `diagnostics_node`. Core: `core.dem_manager.DEMManager(dem_path, nodata_value=-9999.0)` with `get_elevation(...)`, `get_elevation_batch(...)`, `is_in_bounds(...)`, `get_info()`; `core.tercom_matcher.ProfileCollector(min_spacing_m, max_samples)` and `match_profile(dem_array, transform, pixel_size_x, pixel_size_y, terrain_h, dx_m, dy_m, predicted_utm, search_radius_px, discrimination_exclusion_radius=3, nodata_value=-9999.0) -> dict(utm, mad, discrimination, roughness, valid)`; `core.eskf.ESKF(config)` with `initialize`, `predict(accel, gyro, stamp_s)`, `update_position_2d`, `update_altitude`, `update_velocity`. Services: `/tercom/tercom_node/trigger_match`, `/tercom/eskf_node/reset_filter`. Log plots: `scripts/analyze_tercom_log.py`. |
| Time to first result | Estimate: 15-30 min to run the core `match_profile` on your own GeoTIFF from a Python shell (no ROS). 3-6 h to a full SITL run if you start from the riotu-lab Docker image; longer building PX4 + Gazebo Garden from scratch. |
| License | GitHub metadata: none detected - the repo has no LICENSE file, which by default means all rights reserved. However `package.xml` and `setup.py` both declare `Apache-2.0`. Treat it as unclear: fine to read and run for a hackathon, ask the author to add a LICENSE before reusing code. The companion sim repo riotu-lab/gps_denied_navigation_sim also has no license detected. |

## Minimal usage
Not run. Launch from the README; ROS-free call shape from `core/tercom_matcher.py` signatures.

```bash
ros2 launch tercom_nav tercom_nav.launch.py \
  dem_file:=/data/area_dem_utm.tif \
  world_origin_lat:=<lat> world_origin_lon:=<lon> world_origin_alt:=<alt_msl>
ros2 topic echo /tercom/tercom_node/match_quality
```

```python
from tercom_nav.core.dem_manager import DEMManager
from tercom_nav.core.tercom_matcher import match_profile
dem = DEMManager("/data/area_dem.tif")      # reprojects to UTM if geographic
info = dem.get_info()                       # pixel size, bounds, CRS
# terrain_h = baro_amsl - agl*cos(roll)*cos(pitch) - dem_elevation_offset, per sample
res = match_profile(dem.elevation, dem.transform, dem.pixel_size_x, dem.pixel_size_y,
                    terrain_h, dx_m, dy_m, predicted_utm=(e0, n0), search_radius_px=80)
# res["utm"], res["mad"], res["discrimination"], res["roughness"], res["valid"]
```
`dem.elevation`, `dem.transform`, `dem.pixel_size_x/_y` are `DEMManager` attributes set in `_load` (UTM grid after reprojection).

## Wiring it into a nav stack
- DEM acquisition: any GeoTIFF works. For real terrain fetch SRTM/Copernicus DEM with [elevation](../../catalog/repos/bopen__elevation.md) or via [rasterio](../../catalog/repos/rasterio__rasterio.md); the sim repo's `docs/generate_dem.md` builds Gazebo worlds through Blender + BlenderGIS + OpenTopography SRTM 30 m (needs a free OpenTopography API key). [terrain-nav-preprocessing](../../catalog/repos/hstm__terrain-nav-preprocessing.md) prepares DEM tiles with controlled properties. Pixel size drives everything (auto spacing = 1 x pixel, min profile length = 15 x pixel, TERCOM noise auto from pixel size).
- Autopilot side: consumes [MAVROS](../../catalog/repos/mavlink__mavros.md) topics from [PX4](../../catalog/repos/px4__px4-autopilot.md) SITL. It does not push its estimate back into PX4; closing the loop (e.g. as an external vision/odometry input) is your integration work.
- Other absolute fixes slot into the same ESKF via `update_position_2d` with their own covariance: visual fixes from [WildNav](./tiers__wildnav.md) or [satellite-thermal](./arplaboratory__satellite-thermal-geo-localization.md) can share the filter with TERCOM.
- For a no-ROS teaching version of the matcher, start from [python-tercom](./alti3__python-tercom.md) and graduate here.

## Gotchas
- README topic tables are behind the code: README lists `distance_sensor` as `sensor_msgs/Range` and `local_odom` for profile collection; `tercom_node.py` subscribes `LaserScan` on `/scan` and `/tercom/eskf_node/odom` (TROUBLESHOOT Issue 3). A real `Range` rangefinder needs a code change or relay.
- README parameter defaults are also stale: README says `discrimination_min 1.5`, `search_radius_min_pixels 10`, `roughness_min 3.0`; `config/tercom_params.yaml` ships `1.02`, `50`, `5.0`. TROUBLESHOOT Issue 4 explains why: straight-line profiles leave cross-track ambiguity, so discrimination stays near 1.0 even for good matches. Fly turns or accept weak cross-track observability.
- Search window too small => correct location never searched, matches rejected, filter drifts further (TROUBLESHOOT Issues 4-5).
- Frames: ESKF odom is local ENU from `world_origin_*`, MAVROS local odom is PX4 NED from arming point - a constant offset in RViz (Issue 6, ~324 m in their run). `world_origin_*` must match the Gazebo world SDF; docs/MAP_OFFSET.md shows how to derive it.
- MAVROS publishes BEST_EFFORT; subscribers must use sensor QoS (Issue 2, fixed in code).
- Needs GPS at startup (`WAITING_GPS` => averages `gps_init_samples` fixes). Not a cold-start localiser.
- README says fixed-wing; the sim repo's models are multirotors. Flat terrain is rejected by `roughness_min` by design - TERCOM is useless over flat ground or water.
- Open issue #2: Gazebo sim fails to fly ("PreFlight Compass Sensor 0 missing", "No valid local position estimate") and tercom stays in `WAITING_SENSORS` (linked riotu-lab/gps_denied_navigation_sim issue #3).
- TROUBLESHOOT.md reads as a development log and defaults moved during it; pin a commit.

## Alternatives
- [python-tercom](./alti3__python-tercom.md) - 260-line NumPy demo, no ROS, no filter; for explaining TERCOM in a slide or notebook.
- [TERCOM via particle filter (MATLAB)](../../catalog/repos/sotostrk__tercom-via-particle-filter-uav-state-estimation-mae6760-project-.md) and [rhymesg/particle_filter](../../catalog/repos/rhymesg__particle_filter.md) - particle-filter TRN, better for multimodal ambiguity than a single best-match fix; MATLAB.
- [tercom-python](../../catalog/repos/ayushmankumar7__tercom-python.md) - OpenCV demo combining terrain contour and scene matching.

Sources: mzahana/tercom_nav README.md, TROUBLESHOOT.md, docs/MAP_OFFSET.md, package.xml, setup.py, config/tercom_params.yaml, config/taif_test4_params.yaml, launch/tercom_nav.launch.py, tercom_nav/core/{tercom_matcher,dem_manager,eskf}.py, tercom_nav/nodes/tercom_node.py; issues #1, #2; riotu-lab/gps_denied_navigation_sim README.md, docs/generate_dem.md, issue #3; GitHub license metadata (via `gh api`, 2026-11-06).
