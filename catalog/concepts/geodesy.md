# Geodesy and coordinate frames

`concept:geodesy`

Datums, projections, ECEF/ENU/NED, MGRS, geoid models.

**Parent:** [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md)

## Samples (2)

- [Drone frame to orthophoto geolocalization with LightGlue](../../catalog/samples/visual-geolocalization-lightglue.md) - Matches a nadir drone frame against a georeferenced satellite or orthophoto tile with SuperPoint + LightGlue, fits a MAGSAC homography with OpenCV, and maps the frame centre through the GeoTIFF geotransform to lat/lon.
- [Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py](../../catalog/samples/gnss-rinex-processing.md) - Downloads one day of public NOAA NGS CORS RINEX for a rover/base pair 30 km apart, runs RTKLIB demo5 rnx2rtkp in single-point and kinematic RTK modes with exact CLI flags, and scores both against the stations' published 

## Guides (1)

- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) - After this chapter you can convert between the coordinate systems your tools disagree on, fetch free imagery and elevation data for a region, display it, and plan a path or a multi-vehicle mission over it.

## Repositories (15)

- [GDAL](../../catalog/repos/osgeo__gdal.md) - fit: high - Translator library and CLI tools for raster and vector geospatial formats (GeoTIFF, COG, GeoPackage, Shapefile, KML and hundreds more) with reprojection, warping and DEM utilities.
- [PROJ](../../catalog/repos/osgeo__proj.md) - fit: high - Cartographic projection and coordinate transformation library with datum grids, time-dependent transformations and a pipeline syntax.
- [Skyfield](../../catalog/repos/skyfielders__python-skyfield.md) - fit: high - Python library for high-accuracy positions of stars, planets and Earth satellites, with proper time scales and reference frames.
- [pyproj](../../catalog/repos/pyproj4__pyproj.md) - fit: high - Python interface to PROJ for CRS definitions, coordinate transformations and geodesic computations.
- [AHRS (Python)](../../catalog/repos/mayitzin__ahrs.md) - fit: high - Python collection of attitude estimation algorithms (Madgwick, Mahony, complementary, EKF, QUEST, TRIAD and more) plus utilities such as the World Magnetic Model and WGS84.
- [GeographicLib](../../catalog/repos/geographiclib__geographiclib.md) - fit: high - C++ library for accurate geodesic problems, UTM/UPS/MGRS conversions, geoid heights, gravity and magnetic field models.
- [pymap3d](../../catalog/repos/geospace-code__pymap3d.md) - fit: high - Pure-Python 3D coordinate conversions: geodetic, ECEF, ENU, NED, AER, ECI, with optional NumPy vectorization.
- [georinex](../../catalog/repos/geospace-code__georinex.md) - fit: high - Fast Python reader for RINEX 2/3/4 observation and navigation files (plain, gzip/Z/bz2/zip or Hatanaka-compressed) and SP3 orbits into xarray, with batch conversion to NetCDF4/HDF5.
- [GIS MCP Server](../../catalog/repos/mahdin75__gis-mcp.md) - fit: high - MCP server giving LLMs geospatial operations through Shapely, PyProj, GeoPandas and Rasterio: geometry ops, CRS transforms, distances and raster analysis, without a desktop GIS.
- [mgrs (Python)](../../catalog/repos/hobuinc__mgrs.md) - fit: high - Python library converting between latitude/longitude and MGRS grid references, built on NGA GEOTRANS 3.10 (now a Rust port exposed through a pybind11 extension).
- [PRIDE PPP-AR](../../catalog/repos/pridelab__pride-pppar.md) - fit: medium - Wuhan University's open-source multi-GNSS precise point positioning package with ambiguity resolution, aimed at geodetic-grade post-processing.
- [Ginan](../../catalog/repos/geoscienceaustralia__ginan.md) - fit: low - Geoscience Australia's GNSS analysis toolkit for precise orbit determination and real-time/post-processed PPP, producing and consuming correction products.
- [GNSSTk](../../catalog/repos/sgl-ut__gnsstk.md) - fit: low - C++ library (successor to GPSTk) from UT Austin ARL for GNSS data formats, time systems, ephemeris handling and positioning algorithms, with Python bindings.
- [gnssanalysis](../../catalog/repos/geoscienceaustralia__gnssanalysis.md) - fit: low - Geoscience Australia Python module of utilities for reading and comparing GNSS products (SP3, CLK, SINEX, Ginan outputs) and computing differences/statistics.
- [glnephexercise - GLONASS satellite position exercise](../../catalog/repos/korogodin__glnephexercise.md) - fit: low - MPEI student project template for computing GLONASS satellite positions from broadcast ephemerides.

## Documents, talks, courses, datasets (6)

- [GeographicLib documentation](../../catalog/resources/geographiclib-docs.md) - doc - Documentation and background on geodesics, map projections, geoid and gravity models implemented in GeographicLib, plus online calculators.
- [GNSS Data Processing, Vol. I: Fundamentals and Algorithms (ESA TM-23)](../../catalog/resources/esa-gnss-data-processing-vol1.md) - book - Free ESA textbook covering GNSS measurement modelling, SPP, differential positioning and PPP algorithms with full equations.
- [IGS products](../../catalog/resources/igs-products.md) - doc - Catalog of International GNSS Service precise orbits, clocks, biases and atmospheric products used by PPP and precise processing.
- [Navipedia - ESA GNSS encyclopedia](../../catalog/resources/navipedia.md) - doc - ESA's free wiki covering GNSS fundamentals, systems, signals, receivers, augmentation and applications.
- [NOAA NGS CORS network RINEX data archive](../../catalog/resources/noaa-ngs-cors-rinex.md) - dataset - Public archive of RINEX observation and navigation files from the US Continuously Operating Reference Station network, organised by year and day of year.
- [Photogrammetry I & II](../../catalog/resources/stachniss-photogrammetry-i-ii.md) - lecture-series - Recorded two-semester photogrammetry course (2015/16 playlist): camera models, direct linear transform, projective geometry, epipolar geometry, bundle adjustment, and image-based 3D reconstruction.

