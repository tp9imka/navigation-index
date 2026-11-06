# Terrain-relative navigation

`concept:terrain-nav`

TERCOM/TRN/DSMAC-style matching of altimetry or imagery against DEM/terrain databases.

**Parent:** [Assured / resilient PNT](../concepts/assured-pnt.md)

## Samples (1)

- [Terrain-relative navigation with a particle filter](../samples/terrain-relative-nav-pf.md) - A stdlib-only simulation of TERCOM/TRN: an aircraft with a biased INS and a radar altimeter matches its measured terrain profile against a seeded synthetic DEM with a particle filter that also estimates the INS velocity 

## Repositories (20)

- [OpenDroneMap (ODM)](../repos/opendronemap__odm.md) - fit: high - Photogrammetry toolkit that turns aerial images into orthophotos, point clouds, 3D models and DEMs.
- [Rasterio](../repos/rasterio__rasterio.md) - fit: high - Pythonic raster I/O on top of GDAL: read/write GeoTIFF and COG, windowed reads, masks and affine georeferencing.
- [elevation_mapping_cupy](../repos/leggedrobotics__elevation_mapping_cupy.md) - fit: high - GPU-accelerated elevation and traversability mapping from ETH Zurich, supporting semantic layers and learned traversability, used on ANYmal robots.
- [elevation](../repos/bopen__elevation.md) - fit: high - CLI/Python tool to download, cache and clip global DEMs (SRTM, Copernicus DEM and others) for a bounding box.
- [tercom_nav (TERCOM + ESKF)](../repos/mzahana__tercom_nav.md) - fit: high - ROS 2 package combining TERCOM-style terrain matching with an error-state Kalman filter for UAV navigation.
- [python-tercom](../repos/alti3__python-tercom.md) - fit: high - Python demo of TERCOM terrain contour matching: simulate a radar-altimeter profile over a DEM and correlate it against the map to recover position.
- [Cesium Terrain Builder](../repos/geo-data__cesium-terrain-builder.md) - fit: medium - Command-line tools to convert GDAL-readable DEMs into Cesium terrain tiles (heightmap and quantized-mesh with the docker variant).
- [Wild Visual Navigation](../repos/leggedrobotics__wild_visual_navigation.md) - fit: medium - System that learns visual traversability online from pre-trained vision features and robot self-supervision, deployed on legged robots in forests.
- [ALTO](../repos/metaslam__alto.md) - fit: medium - Aerial-view, large-scale, terrain-oriented dataset for aerial place recognition and localization.
- [GNSS-Denied UAV Geolocalization (terrain-weighted)](../repos/yfs90__gnss-denied-uav-geolocalization.md) - fit: medium - Code and demos for a UAV geolocalization system that combines image matching, visual odometry and a terrain-weighted constraint optimization, intended to work day and night.
- [TRN particle filter examples](../repos/rhymesg__particle_filter.md) - fit: medium - MATLAB particle filtering examples for terrain-referenced navigation, comparing standard, auxiliary, mixture and out-of-sequence measurement particle filters (accompanies an IEEE TAES 2018 paper).
- [TERCOM-python (TERCOM + DSMAC)](../repos/ayushmankumar7__tercom-python.md) - fit: medium - OpenCV-based demo of map-based navigation combining terrain contour matching with scene-matching area correlation.
- [terrain-nav-preprocessing](../repos/hstm__terrain-nav-preprocessing.md) - fit: medium - Preprocessing tools for terrain-referenced navigation, generating DEM tiles with controlled noise for training and evaluation.
- [TERCOM via particle filter](../repos/sotostrk__tercom-via-particle-filter-uav-state-estimation-mae6760-project-.md) - fit: medium - MATLAB SIR particle filter estimating UAV position from terrain contour matching in GPS-denied flight.
- [traversability_estimation](../repos/leggedrobotics__traversability_estimation.md) - fit: low - ETH package that computes traversability from elevation maps using slope, roughness and step-height filters.
- [elevation_mapping](../repos/leggedrobotics__elevation_mapping.md) - fit: low - ETH Zurich robot-centric elevation mapping for rough terrain navigation that fuses range data into a probabilistic 2.5D map.
- [Seasonally invariant transform (visual TRN)](../repos/connorlee77__seasonally-invariant-image-transform.md) - fit: low - Training code for a learned image transform that makes aerial imagery robust to seasonal appearance change for visual terrain-relative navigation.
- [FederNet](../repos/sirbastiano__federnet.md) - fit: low - Terrain relative navigation for planetary landing that detects craters with a Mask R-CNN and matches them to a catalog using projective invariants.
- [Deep-TERNALOC](../repos/deep-ternaloc__deep-ternaloc.md) - fit: low - Deep-learning-based terrain-referenced navigation and localization project from ITU Aerospace Research Center, with particle filter baselines.
- [SMARC navigation](../repos/halajun__smarc_navigation.md) - fit: low - Localization and SLAM components for the SMARC AUVs (KTH), including EKF localization with IMU, DVL and multibeam sonar against a feature map.

## Documents, talks, courses, datasets (2)

- [A Robust Approach to Vision-Based Terrain-Aided Localization](../resources/ion-webinar-navon.md) - talk - Vision-based terrain-aided localization for aircraft, matching onboard imagery against terrain/map references as a GNSS-independent position source.
- [Copernicus DEM on AWS Open Data](../resources/copernicus-dem-aws.md) - dataset - Registry entry for the Copernicus global DEM (GLO-30/GLO-90) hosted as cloud-optimized GeoTIFFs on AWS, freely accessible without an account.

