# GIS, maps and geospatial data

`concept:gis-mapping`

Map engines, tiles, DEMs, orthophotos, coordinate systems, geodesy.

**Sub-concepts:** [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md)

## Samples (6)

- [Blind-flight bench: radar altimeter + Copernicus GLO-30 TRN, six navigators on one harness](../../catalog/samples/blind-flight-bench.md) - Benchmark harness that reproduces the 2026 'Polyot vslepuyu' (Blind flight) hackathon case on four real GLO-30 windows (Khibiny mountains, Middle Urals, Yenisei taiga, the flat Moscow-region map area): 20 km simulated fl
- [Heightmap-gradient particle filter on real DEM and 1 m LiDAR (SPRIN-D CTU method) vs TERCOM](../../catalog/samples/terrain-heightmap-pf.md) - Re-implementation of the CTU SPRIN-D winner's localization (arXiv 2510.01348): local heightmap gradients matched to a prior DEM with the unnormalized correlation coefficient, Gaussian-blurred similarity maps weighting a 
- [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md) - The coarse first stage that geoloc-license-clean lacks: no position prior, unknown heading.
- [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md) - Drone frame => NAIP orthophoto => lat/lon using only permissively licensed parts: ALIKED (BSD-3), DISK and LightGlue weights (Apache-2.0), OpenCV SIFT and MAGSAC (Apache-2.0), rasterio, public-domain NAIP from Microsoft 
- [OSINT interference map from free data: ADS-B NACp hexes and Sentinel-1 C-band RFI over Kaliningrad / the SE Baltic](../../catalog/samples/osint-jamming-map.md) - Two no-login OSINT layers for the same area and morning (2026-10-01, SE Baltic around Kaliningrad).
- [Terrain-relative navigation with a particle filter](../../catalog/samples/terrain-relative-nav-pf.md) - A stdlib-only simulation of TERCOM/TRN: an aircraft with a biased INS and a radar altimeter matches its measured terrain profile against a seeded synthetic DEM with a particle filter that also estimates the INS velocity 

## Guides (3)

- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) - The closest real precedent we have for a navigation hackathon brief: a 48-hour case (26-28 June 2026, Krasnodar, track "Robotics and sensing") where teams had to find position, ground speed and heading of an aircraft fro
- [7. Maps, geodesy and planning](../../docs/primer/07-maps-geodesy-planning.md) - After this chapter you can convert between the coordinate systems your tools disagree on, fetch free imagery and elevation data for a region, display it, and plan a path or a multi-vehicle mission over it.
- [Docs map](../../docs/README.md) - What each page under docs/ is for and the order to read them in.

## Repositories (43)

- [Leaflet](../../catalog/repos/leaflet__leaflet.md) - fit: high - Small, simple JavaScript library for interactive raster/vector maps with a huge plugin ecosystem.
- [CesiumJS](../../catalog/repos/cesiumgs__cesium.md) - fit: high - WebGL 3D globe and map library with terrain, 3D Tiles, time-dynamic data (CZML) and accurate WGS84 rendering.
- [QGIS](../../catalog/repos/qgis__qgis.md) - fit: high - Desktop open-source GIS for viewing, editing, analyzing and printing geospatial data, extensible via Python plugins.
- [deck.gl](../../catalog/repos/visgl__deck.gl.md) - fit: high - GPU-powered large-scale data visualization framework with layers for points, paths, trips, hexbins and 3D tiles, usable over MapLibre or standalone.
- [MapLibre GL JS](../../catalog/repos/maplibre__maplibre-gl-js.md) - fit: high - Open-source WebGL vector tile map renderer (fork of Mapbox GL JS v1) with styles, 3D terrain and globe view.
- [OSRM](../../catalog/repos/project-osrm__osrm-backend.md) - fit: high - High-performance road routing engine on OpenStreetMap data using contraction hierarchies or multi-level Dijkstra.
- [OpenDroneMap (ODM)](../../catalog/repos/opendronemap__odm.md) - fit: high - Photogrammetry toolkit that turns aerial images into orthophotos, point clouds, 3D models and DEMs.
- [Valhalla](../../catalog/repos/valhalla__valhalla.md) - fit: high - Tiled OSM routing engine with dynamic costing per request (auto, truck, pedestrian, bicycle), isochrones and map matching.
- [GDAL](../../catalog/repos/osgeo__gdal.md) - fit: high - Translator library and CLI tools for raster and vector geospatial formats (GeoTIFF, COG, GeoPackage, Shapefile, KML and hundreds more) with reprojection, warping and DEM utilities.
- [OSMnx](../../catalog/repos/gboeing__osmnx.md) - fit: high - Download, model and analyze street networks and other OSM features as NetworkX graphs.
- [Martin](../../catalog/repos/maplibre__martin.md) - fit: high - Fast Rust tile server for PostGIS, MBTiles and PMTiles sources, with tile generation and mbtiles tooling.
- [grid_map](../../catalog/repos/anybotics__grid_map.md) - fit: high - C++ library and ROS integration for multi-layer 2.5D grid maps, widely used for elevation and traversability mapping.
- [PMTiles](../../catalog/repos/protomaps__pmtiles.md) - fit: high - Single-file tile archive format and tooling, served by HTTP range requests from static storage, with JS/Go readers and extraction CLI.
- [TileServer GL](../../catalog/repos/maptiler__tileserver-gl.md) - fit: high - Vector and raster tile server that serves MBTiles/PMTiles with GL styles and renders raster tiles server-side with MapLibre Native.
- [Rasterio](../../catalog/repos/rasterio__rasterio.md) - fit: high - Pythonic raster I/O on top of GDAL: read/write GeoTIFF and COG, windowed reads, masks and affine georeferencing.
- [PROJ](../../catalog/repos/osgeo__proj.md) - fit: high - Cartographic projection and coordinate transformation library with datum grids, time-dependent transformations and a pipeline syntax.
- [OpenCPN](../../catalog/repos/opencpn__opencpn.md) - fit: high - Cross-platform open-source chartplotter and navigation application that displays raster and S-57 vector charts, ingests GPS and AIS feeds, and runs waypoint routes.
- [elevation_mapping_cupy](../../catalog/repos/leggedrobotics__elevation_mapping_cupy.md) - fit: high - GPU-accelerated elevation and traversability mapping from ETH Zurich, supporting semantic layers and learned traversability, used on ANYmal robots.
- [QGIS MCP](../../catalog/repos/jjsantos01__qgis_mcp.md) - fit: high - MCP server plus QGIS plugin that lets an LLM create projects, load layers, run processing algorithms and execute PyQGIS code in QGIS Desktop.
- [elevation](../../catalog/repos/bopen__elevation.md) - fit: high - CLI/Python tool to download, cache and clip global DEMs (SRTM, Copernicus DEM and others) for a bounding box.
- [pystac-client](../../catalog/repos/stac-utils__pystac-client.md) - fit: high - Python client for searching STAC APIs (Earth Search, Planetary Computer and others) by area, time and properties.
- [GIS MCP Server](../../catalog/repos/mahdin75__gis-mcp.md) - fit: high - MCP server giving LLMs geospatial operations through Shapely, PyProj, GeoPandas and Rasterio: geometry ops, CRS transforms, distances and raster analysis, without a desktop GIS.
- [mil-sym-ts](../../catalog/repos/missioncommand__mil-sym-ts.md) - fit: high - TypeScript/JavaScript renderer for MIL-STD-2525 (D and later) military symbology, producing single-point and multi-point tactical graphics for web maps.
- [Sentinel-1 RFI detection](../../catalog/repos/zephr-xyz__sentinel1-rfi-detection.md) - fit: high - Pipeline that flags radio-frequency interference in Sentinel-1 C-band SAR scenes using temporal z-scores and DEM slope masking, run over Iran, the Persian Gulf and Jammertest 2025.
- [grid_map](../../catalog/repos/leggedrobotics__grid_map.md) - fit: high - Universal multi-layer 2.5D grid map library for mobile robots with ROS/ROS 2 integration, filters, iterators and conversion to images, point clouds and costmaps.
- [Hackathon-Blind-Flight (team GORIZONT)](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md) - fit: high - Russian-language hackathon solution for 'Полёт вслепую' (Blind flight): estimate aircraft position, ground speed and heading without GNSS by reconstructing a terrain profile (barometric altitude minus radar altimeter) an
- [KROT (Где мы, Бариста?) - terrain correlation from radar altimeter](../../catalog/repos/rub1kub__where-are-we-barista.md) - fit: high - Team 'Где мы, Бариста?' solution to the 2026 'Полёт вслепую' (Blind flight) hackathon case: 'КРОТ' (Корреляционный Рельефный Определитель Траектории) turns a radar-altimeter NMEA-0183 log flown at a constant 1500 m MSL i
- [FlyingBlind_Hakaton](../../catalog/repos/solarwarlock__flyingblind_hakaton.md) - fit: high - Second public solution to the same 'Полёт вслепую' hackathon task: web prototype that reads a GeoTIFF DEM and NMEA-0183 radar-altimeter messages, searches start point, speed and azimuth hypotheses by RMSE/correlation, an
- [OpenLayers](../../catalog/repos/openlayers__openlayers.md) - fit: medium - Feature-rich web mapping library supporting many projections, WMS/WMTS, vector tiles and editing.
- [GraphHopper](../../catalog/repos/graphhopper__graphhopper.md) - fit: medium - Java OSM routing engine usable as library or server, with custom models for per-request costing and map matching.
- [Planetiler](../../catalog/repos/onthegomap__planetiler.md) - fit: medium - Fast vector tile generator that builds OpenMapTiles-compatible tilesets from OSM extracts on a single machine.
- [tar1090](../../catalog/repos/wiedehopf__tar1090.md) - fit: medium - Improved web interface for readsb/dump1090 with track history, filtering and overlays.
- [sentinelhub-py](../../catalog/repos/sentinel-hub__sentinelhub-py.md) - fit: medium - Python client for Sentinel Hub and Copernicus Data Space services to search, download and process Sentinel and other satellite imagery.
- [Cesium Terrain Builder](../../catalog/repos/geo-data__cesium-terrain-builder.md) - fit: medium - Command-line tools to convert GDAL-readable DEMs into Cesium heightmap terrain tiles; quantized-mesh output needs the ahuarte47 fork, which the tum-gis Docker image packages.
- [GTSfM](../../catalog/repos/borglab__gtsfm.md) - fit: medium - End-to-end structure-from-motion pipeline built on GTSAM, with pluggable front-ends (classical and learned matchers) and distributed execution via Dask.
- [ATAK-CIV (DoD release, archived)](../../catalog/repos/deptofdefense__androidtacticalassaultkit-civ.md) - fit: medium - The DoD's public source release of the civilian Android Team Awareness Kit: map engine, Cursor-on-Target messaging and plugin SDK.
- [LLM-Geo (Autonomous GIS)](../../catalog/repos/gladcolor__llm-geo.md) - fit: medium - Research prototype of an LLM-driven 'autonomous GIS' that turns a spatial question into a solution graph, generates code and executes the analysis to return maps and numbers.
- [qgis-mcp (nkarasiak)](../../catalog/repos/nkarasiak__qgis-mcp.md) - fit: medium - MCP bridge that lets AI agents drive QGIS Desktop: a QGIS plugin runs a TCP socket server inside QGIS and a FastMCP server exposes about 125 tools (layers, feature editing, processing, rendering, styling, layouts/atlas, 
- [ATAK-CIV (TAK Product Center)](../../catalog/repos/tak-product-center__atak-civ.md) - fit: medium - Source of the civilian Android Team Awareness Kit maintained by the TAK Product Center: map client, plugin SDK and CoT handling.
- [odc-stac](../../catalog/repos/opendatacube__odc-stac.md) - fit: medium - Loads STAC items into xarray datasets with reprojection, resampling and mosaicking.
- [CityNav](../../catalog/repos/water-cookie__citynav.md) - fit: medium - Language-goal aerial navigation dataset over real-city 3D point clouds with geographic information, plus baselines that use map-based landmark grounding.
- [MAMMAL](../../catalog/repos/powerbroker2__mammal.md) - fit: medium - Python package (Magnetic Anomaly Map Matching Airborne and Land) for simulating and processing aeromagnetic survey data and building anomaly maps for MagNav.
- [terrain-nav-preprocessing](../../catalog/repos/hstm__terrain-nav-preprocessing.md) - fit: medium - Preprocessing tools for terrain-referenced navigation, generating DEM tiles with controlled noise for training and evaluation.

## Documents, talks, courses, datasets (14)

- [CityNav: A Large-Scale Dataset for Real-World Aerial Navigation](../../catalog/resources/citynav-2024.md) - paper - Introduces a language-goal aerial navigation dataset built on real-city 3D data with geographic metadata, and baselines using map-based grounding.
- [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md) - dataset - Registry entry for the Copernicus global DEM (GLO-30/GLO-90) hosted as cloud-optimized GeoTIFFs on AWS, freely accessible without an account.
- [Geobasis NRW DOM1 / DGM1 1 m airborne LiDAR surface and terrain models](../../catalog/resources/geobasis-nrw-dom1-dgm1.md) - dataset - North Rhine-Westphalia's open-data 1 m digital surface model (DOM1, buildings and vegetation included) and 1 m bare-earth terrain model (DGM1) for the whole state, delivered as 1 x 1 km GeoTIFF tiles in ETRS89 / UTM 32N 
- [NAIP aerial imagery on Microsoft Planetary Computer](../../catalog/resources/naip-planetary-computer.md) - dataset - USDA National Agriculture Imagery Program leaf-on orthophotos (RGB + NIR) of the contiguous US, re-flown per state every few years, served as Cloud-Optimized GeoTIFFs behind a STAC API.
- [NATO Joint Military Symbology (APP-6) - overview](../../catalog/resources/app-6-joint-military-symbology.md) - doc - Overview of APP-6, the NATO standard for map symbols of units, equipment and tactical graphics, now at edition E and aligned with the US MIL-STD-2525 family.
- [Natural Earth vector data](../../catalog/resources/natural-earth-vectors.md) - dataset - Public-domain world vector layers (land, coastline, countries) at 1:10m, 1:50m and 1:110m scales.
- [OpenAerialMap](../../catalog/resources/openaerialmap.md) - dataset - An open catalogue of user-contributed aerial and drone orthomosaics, each stored as a Cloud-Optimized GeoTIFF on a public S3 bucket under CC BY 4.0.
- [OpenStreetMap data via the Overpass API](../../catalog/resources/openstreetmap-overpass-api.md) - dataset - A read-only query API over the OpenStreetMap database that returns features (coastlines, bridges, wind turbines, buoys) inside a bounding box.
- [SpatioTemporal Asset Catalog (STAC) specification](../../catalog/resources/stac-spec.md) - standard - Specification and ecosystem site for STAC, the common way to describe and search geospatial imagery and DEM assets.
- [USGS 3DEP seamless DEMs on Microsoft Planetary Computer](../../catalog/resources/usgs-3dep-planetary-computer.md) - dataset - The USGS 3D Elevation Program seamless bare-earth DEMs for the US, served as Cloud-Optimized GeoTIFFs through Planetary Computer's STAC API with the same SAS signing as NAIP.
- [«Ми почали будувати захищену екосистему для всіх військових застосунків». Архітектор DELTA - про розвиток системи](../../catalog/resources/dou-delta-architecture-interview-2024.md) - blog - English: 'We started building a secure ecosystem for all military applications.
- [Аэрофотосъемка без ГНСС!?](../../catalog/resources/gma2026-terion-aerial-survey-without-gnss.md) - talk - English: 'Aerial photography without GNSS!?' Talk at the XVII 'Geodesy.
- [Как работать без ГНСС?! Системы лазерного сканирования](../../catalog/resources/gma2024-artgeo-laser-scanning-without-gnss.md) - talk - English: 'How to work without GNSS?!
- [У 17 років створив навігацію для дронів, яку не глушить РЕБ. Історія киянина, який переміг на «Олімпіаді геніїв» у США](../../catalog/resources/dou-lapko-urban-nav-interview-2025.md) - blog - English: 'Built EW-proof drone navigation at 17: the story of a Kyiv student who won the Genius Olympiad in the USA'.

