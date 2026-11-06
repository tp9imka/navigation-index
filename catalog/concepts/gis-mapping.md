# GIS, maps and geospatial data

`concept:gis-mapping`

Map engines, tiles, DEMs, orthophotos, coordinate systems, geodesy.

**Sub-concepts:** [Geodesy and coordinate frames](../concepts/geodesy.md)

## Samples (1)

- [Terrain-relative navigation with a particle filter](../samples/terrain-relative-nav-pf.md) - A stdlib-only simulation of TERCOM/TRN: an aircraft with a biased INS and a radar altimeter matches its measured terrain profile against a seeded synthetic DEM with a particle filter that also estimates the INS velocity 

## Repositories (41)

- [Leaflet](../repos/leaflet__leaflet.md) - fit: high - Small, simple JavaScript library for interactive raster/vector maps with a huge plugin ecosystem.
- [CesiumJS](../repos/cesiumgs__cesium.md) - fit: high - WebGL 3D globe and map library with terrain, 3D Tiles, time-dynamic data (CZML) and accurate WGS84 rendering.
- [QGIS](../repos/qgis__qgis.md) - fit: high - Desktop open-source GIS for viewing, editing, analyzing and printing geospatial data, extensible via Python plugins.
- [deck.gl](../repos/visgl__deck.gl.md) - fit: high - GPU-powered large-scale data visualization framework with layers for points, paths, trips, hexbins and 3D tiles, usable over MapLibre or standalone.
- [MapLibre GL JS](../repos/maplibre__maplibre-gl-js.md) - fit: high - Open-source WebGL vector tile map renderer (fork of Mapbox GL JS v1) with styles, 3D terrain and globe view.
- [OSRM](../repos/project-osrm__osrm-backend.md) - fit: high - High-performance road routing engine on OpenStreetMap data using contraction hierarchies or multi-level Dijkstra.
- [OpenDroneMap (ODM)](../repos/opendronemap__odm.md) - fit: high - Photogrammetry toolkit that turns aerial images into orthophotos, point clouds, 3D models and DEMs.
- [Valhalla](../repos/valhalla__valhalla.md) - fit: high - Tiled OSM routing engine with dynamic costing per request (auto, truck, pedestrian, bicycle), isochrones and map matching.
- [GDAL](../repos/osgeo__gdal.md) - fit: high - Translator library and CLI tools for raster and vector geospatial formats (GeoTIFF, COG, GeoPackage, Shapefile, KML and hundreds more) with reprojection, warping and DEM utilities.
- [OSMnx](../repos/gboeing__osmnx.md) - fit: high - Download, model and analyze street networks and other OSM features as NetworkX graphs.
- [Martin](../repos/maplibre__martin.md) - fit: high - Fast Rust tile server for PostGIS, MBTiles and PMTiles sources, with tile generation and mbtiles tooling.
- [grid_map](../repos/anybotics__grid_map.md) - fit: high - C++ library and ROS integration for multi-layer 2.5D grid maps, widely used for elevation and traversability mapping.
- [PMTiles](../repos/protomaps__pmtiles.md) - fit: high - Single-file tile archive format and tooling, served by HTTP range requests from static storage, with JS/Go readers and extraction CLI.
- [TileServer GL](../repos/maptiler__tileserver-gl.md) - fit: high - Vector and raster tile server that serves MBTiles/PMTiles with GL styles and renders raster tiles server-side with MapLibre Native.
- [Rasterio](../repos/rasterio__rasterio.md) - fit: high - Pythonic raster I/O on top of GDAL: read/write GeoTIFF and COG, windowed reads, masks and affine georeferencing.
- [PROJ](../repos/osgeo__proj.md) - fit: high - Cartographic projection and coordinate transformation library with datum grids, time-dependent transformations and a pipeline syntax.
- [OpenCPN](../repos/opencpn__opencpn.md) - fit: high - Cross-platform open-source chartplotter and navigation application that displays raster and S-57 vector charts, ingests GPS and AIS feeds, and runs waypoint routes.
- [elevation_mapping_cupy](../repos/leggedrobotics__elevation_mapping_cupy.md) - fit: high - GPU-accelerated elevation and traversability mapping from ETH Zurich, supporting semantic layers and learned traversability, used on ANYmal robots.
- [QGIS MCP](../repos/jjsantos01__qgis_mcp.md) - fit: high - MCP server plus QGIS plugin that lets an LLM create projects, load layers, run processing algorithms and execute PyQGIS code in QGIS Desktop.
- [elevation](../repos/bopen__elevation.md) - fit: high - CLI/Python tool to download, cache and clip global DEMs (SRTM, Copernicus DEM and others) for a bounding box.
- [pystac-client](../repos/stac-utils__pystac-client.md) - fit: high - Python client for searching STAC APIs (Earth Search, Planetary Computer and others) by area, time and properties.
- [GIS MCP Server](../repos/mahdin75__gis-mcp.md) - fit: high - MCP server giving LLMs geospatial operations through Shapely, PyProj, GeoPandas and Rasterio: geometry ops, CRS transforms, distances and raster analysis, without a desktop GIS.
- [mil-sym-ts](../repos/missioncommand__mil-sym-ts.md) - fit: high - TypeScript/JavaScript renderer for MIL-STD-2525 (D and later) military symbology, producing single-point and multi-point tactical graphics for web maps.
- [grid_map](../repos/leggedrobotics__grid_map.md) - fit: high - Universal multi-layer 2.5D grid map library for mobile robots with ROS/ROS 2 integration, filters, iterators and conversion to images, point clouds and costmaps.
- [Hackathon-Blind-Flight (team GORIZONT)](../repos/t1gr20an06-k__hackathon-blind-flight.md) - fit: high - Russian-language hackathon solution for 'Полёт вслепую' (Blind flight): estimate aircraft position, ground speed and heading without GNSS by reconstructing a terrain profile (barometric altitude minus radar altimeter) an
- [FlyingBlind_Hakaton](../repos/solarwarlock__flyingblind_hakaton.md) - fit: high - Second public solution to the same 'Полёт вслепую' hackathon task: web prototype that reads a GeoTIFF DEM and NMEA-0183 radar-altimeter messages, searches start point, speed and azimuth hypotheses by RMSE/correlation, an
- [OpenLayers](../repos/openlayers__openlayers.md) - fit: medium - Feature-rich web mapping library supporting many projections, WMS/WMTS, vector tiles and editing.
- [GraphHopper](../repos/graphhopper__graphhopper.md) - fit: medium - Java OSM routing engine usable as library or server, with custom models for per-request costing and map matching.
- [Planetiler](../repos/onthegomap__planetiler.md) - fit: medium - Fast vector tile generator that builds OpenMapTiles-compatible tilesets from OSM extracts on a single machine.
- [tar1090](../repos/wiedehopf__tar1090.md) - fit: medium - Improved web interface for readsb/dump1090 with track history, filtering and overlays.
- [sentinelhub-py](../repos/sentinel-hub__sentinelhub-py.md) - fit: medium - Python client for Sentinel Hub and Copernicus Data Space services to search, download and process Sentinel and other satellite imagery.
- [Cesium Terrain Builder](../repos/geo-data__cesium-terrain-builder.md) - fit: medium - Command-line tools to convert GDAL-readable DEMs into Cesium terrain tiles (heightmap and quantized-mesh with the docker variant).
- [GTSfM](../repos/borglab__gtsfm.md) - fit: medium - End-to-end structure-from-motion pipeline built on GTSAM, with pluggable front-ends (classical and learned matchers) and distributed execution via Dask.
- [ATAK-CIV (DoD release, archived)](../repos/deptofdefense__androidtacticalassaultkit-civ.md) - fit: medium - The DoD's public source release of the civilian Android Team Awareness Kit: map engine, Cursor-on-Target messaging and plugin SDK.
- [LLM-Geo (Autonomous GIS)](../repos/gladcolor__llm-geo.md) - fit: medium - Research prototype of an LLM-driven 'autonomous GIS' that turns a spatial question into a solution graph, generates code and executes the analysis to return maps and numbers.
- [qgis-mcp (nkarasiak)](../repos/nkarasiak__qgis-mcp.md) - fit: medium - Actively maintained MCP bridge connecting AI agents to QGIS Desktop, with a broader tool set than the original qgis_mcp.
- [ATAK-CIV (TAK Product Center)](../repos/tak-product-center__atak-civ.md) - fit: medium - Source of the civilian Android Team Awareness Kit maintained by the TAK Product Center: map client, plugin SDK and CoT handling.
- [odc-stac](../repos/opendatacube__odc-stac.md) - fit: medium - Loads STAC items into xarray datasets with reprojection, resampling and mosaicking.
- [CityNav](../repos/water-cookie__citynav.md) - fit: medium - Language-goal aerial navigation dataset over real-city 3D point clouds with geographic information, plus baselines that use map-based landmark grounding.
- [MAMMAL](../repos/powerbroker2__mammal.md) - fit: medium - Python package (Magnetic Anomaly Map Matching Airborne and Land) for simulating and processing aeromagnetic survey data and building anomaly maps for MagNav.
- [terrain-nav-preprocessing](../repos/hstm__terrain-nav-preprocessing.md) - fit: medium - Preprocessing tools for terrain-referenced navigation, generating DEM tiles with controlled noise for training and evaluation.

## Documents, talks, courses, datasets (6)

- [CityNav: A Large-Scale Dataset for Real-World Aerial Navigation](../resources/citynav-2024.md) - paper - Introduces a language-goal aerial navigation dataset built on real-city 3D data with geographic metadata, and baselines using map-based grounding.
- [Copernicus DEM on AWS Open Data](../resources/copernicus-dem-aws.md) - dataset - Registry entry for the Copernicus global DEM (GLO-30/GLO-90) hosted as cloud-optimized GeoTIFFs on AWS, freely accessible without an account.
- [NATO Joint Military Symbology (APP-6) - overview](../resources/app-6-joint-military-symbology.md) - doc - Overview of APP-6, the NATO standard for map symbols of units, equipment and tactical graphics, now at edition E and aligned with the US MIL-STD-2525 family.
- [SpatioTemporal Asset Catalog (STAC) specification](../resources/stac-spec.md) - standard - Specification and ecosystem site for STAC, the common way to describe and search geospatial imagery and DEM assets.
- [«Ми почали будувати захищену екосистему для всіх військових застосунків». Архітектор DELTA - про розвиток системи](../resources/dou-delta-architecture-interview-2024.md) - blog - English: 'We started building a secure ecosystem for all military applications.
- [У 17 років створив навігацію для дронів, яку не глушить РЕБ. Історія киянина, який переміг на «Олімпіаді геніїв» у США](../resources/dou-lapko-urban-nav-interview-2025.md) - blog - English: 'Built EW-proof drone navigation at 17: the story of a Kyiv student who won the Genius Olympiad in the USA'.

