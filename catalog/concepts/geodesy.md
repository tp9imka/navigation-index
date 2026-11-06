# Geodesy and coordinate frames

`concept:geodesy`

Datums, projections, ECEF/ENU/NED, MGRS, geoid models.

**Parent:** [GIS, maps and geospatial data](../concepts/gis-mapping.md)

## Samples (2)

- [Drone frame to orthophoto geolocalization with LightGlue](../samples/visual-geolocalization-lightglue.md) - Matches a nadir drone frame against a georeferenced satellite or orthophoto tile with SuperPoint + LightGlue, fits a MAGSAC homography with OpenCV, and maps the frame centre through the GeoTIFF geotransform to lat/lon.
- [Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py](../samples/gnss-rinex-processing.md) - Downloads one day of public NOAA NGS CORS RINEX for a rover/base pair 30 km apart, runs RTKLIB demo5 rnx2rtkp in single-point and kinematic RTK modes with exact CLI flags, and scores both against the stations' published 

## Repositories (14)

- [GDAL](../repos/osgeo__gdal.md) - fit: high - Translator library and CLI tools for raster and vector geospatial formats (GeoTIFF, COG, GeoPackage, Shapefile, KML and hundreds more) with reprojection, warping and DEM utilities.
- [PROJ](../repos/osgeo__proj.md) - fit: high - Cartographic projection and coordinate transformation library with datum grids, time-dependent transformations and a pipeline syntax.
- [Skyfield](../repos/skyfielders__python-skyfield.md) - fit: high - Python library for high-accuracy positions of stars, planets and Earth satellites, with proper time scales and reference frames.
- [pyproj](../repos/pyproj4__pyproj.md) - fit: high - Python interface to PROJ for CRS definitions, coordinate transformations and geodesic computations.
- [AHRS (Python)](../repos/mayitzin__ahrs.md) - fit: high - Python collection of attitude estimation algorithms (Madgwick, Mahony, complementary, EKF, QUEST, TRIAD and more) plus utilities such as the World Magnetic Model and WGS84.
- [GeographicLib](../repos/geographiclib__geographiclib.md) - fit: high - C++ library for accurate geodesic problems, UTM/UPS/MGRS conversions, geoid heights, gravity and magnetic field models.
- [pymap3d](../repos/geospace-code__pymap3d.md) - fit: high - Pure-Python 3D coordinate conversions: geodetic, ECEF, ENU, NED, AER, ECI, with optional NumPy vectorization.
- [georinex](../repos/geospace-code__georinex.md) - fit: high - Fast Python reader for RINEX 2/3 observation and navigation files and SP3 orbits into xarray, with batch conversion to HDF5/NetCDF.
- [GIS MCP Server](../repos/mahdin75__gis-mcp.md) - fit: high - MCP server giving LLMs geospatial operations through Shapely, PyProj, GeoPandas and Rasterio: geometry ops, CRS transforms, distances and raster analysis, without a desktop GIS.
- [mgrs (Python)](../repos/hobuinc__mgrs.md) - fit: high - Python library converting between latitude/longitude and MGRS grid references, built on NGA GEOTRANS 3.10 (now a Rust port exposed through a pybind11 extension).
- [PRIDE PPP-AR](../repos/pridelab__pride-pppar.md) - fit: medium - Wuhan University's open-source multi-GNSS precise point positioning package with ambiguity resolution, aimed at geodetic-grade post-processing.
- [Ginan](../repos/geoscienceaustralia__ginan.md) - fit: low - Geoscience Australia's GNSS analysis toolkit for precise orbit determination and real-time/post-processed PPP, producing and consuming correction products.
- [GNSSTk](../repos/sgl-ut__gnsstk.md) - fit: low - C++ library (successor to GPSTk) from UT Austin ARL for GNSS data formats, time systems, ephemeris handling and positioning algorithms, with Python bindings.
- [gnssanalysis](../repos/geoscienceaustralia__gnssanalysis.md) - fit: low - Geoscience Australia Python module of utilities for reading and comparing GNSS products (SP3, CLK, SINEX, Ginan outputs) and computing differences/statistics.

## Documents, talks, courses, datasets (5)

- [GeographicLib documentation](../resources/geographiclib-docs.md) - doc - Documentation and background on geodesics, map projections, geoid and gravity models implemented in GeographicLib, plus online calculators.
- [GNSS Data Processing, Vol. I: Fundamentals and Algorithms (ESA TM-23)](../resources/esa-gnss-data-processing-vol1.md) - book - Free ESA textbook covering GNSS measurement modelling, SPP, differential positioning and PPP algorithms with full equations.
- [IGS products](../resources/igs-products.md) - doc - Catalog of International GNSS Service precise orbits, clocks, biases and atmospheric products used by PPP and precise processing.
- [Navipedia - ESA GNSS encyclopedia](../resources/navipedia.md) - doc - ESA's free wiki covering GNSS fundamentals, systems, signals, receivers, augmentation and applications.
- [Photogrammetry I & II](../resources/stachniss-photogrammetry-i-ii.md) - lecture-series - Recorded two-semester photogrammetry course (2015/16 playlist): camera models, direct linear transform, projective geometry, epipolar geometry, bundle adjustment, and image-based 3D reconstruction.

