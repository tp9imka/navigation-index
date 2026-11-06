# 7. Maps, geodesy and planning

After this chapter you can convert between the coordinate systems your tools disagree on,
fetch free imagery and elevation data for a region, display it, and plan a path or a
multi-vehicle mission over it.

Prev: [Autopilots and C2](06-autopilots-and-c2.md) | Next: [Maritime, underwater and ground](08-maritime-underwater-ground.md) | [Primer index](README.md)

## Geodesy you actually need

- **Datum and ellipsoid.** GNSS works in WGS84 (in practice an ITRF realisation). Other
  datasets may use national datums; PROJ handles datum transforms, including
  time-dependent ones, given its grid files
  ([PROJ](../../catalog/repos/osgeo__proj.md)).
- **Heights.** Ellipsoidal height (GNSS) vs orthometric height (DEMs, maps). The difference
  is the geoid undulation, and it matters whenever you compare GNSS altitude with terrain
  ([GeographicLib docs](../../catalog/resources/geographiclib-docs.md)). Barometric altitude
  is a third reference with its own drift.
- **Projections.** UTM gives metric x/y in zones; local ENU/NED is best for a filter
  (chapter 1). Do math in a local metric frame, store and exchange in lat/lon.
- **Military grid.** MGRS strings are what operators read and type
  ([mgrs](../../catalog/repos/hobuinc__mgrs.md)); mind the precision argument.
- **Geodesics.** Distance and bearing on the ellipsoid, not on a sphere, for anything beyond
  a few kilometres ([GeographicLib](../../catalog/repos/geographiclib__geographiclib.md)).

```python
import pymap3d as pm
e, n, u = pm.geodetic2enu(lat, lon, h, lat0, lon0, h0)   # ellipsoidal heights in, metres out
```

## Data you can get without an account

- **Elevation:** Copernicus GLO-30/GLO-90 DEM as cloud-optimised GeoTIFFs on AWS, sampled
  directly with rasterio ([Copernicus DEM](../../catalog/resources/copernicus-dem-aws.md)).
- **Imagery:** public STAC APIs give key-free access to Sentinel-2 and Copernicus DEM
  ([STAC spec](../../catalog/resources/stac-spec.md),
  [pystac-client](../../catalog/repos/stac-utils__pystac-client.md)).
- **Roads and features:** OpenStreetMap via [OSMnx](../../catalog/repos/gboeing__osmnx.md).
- **Your own orthophoto:** fly (or simulate), then build one with
  [OpenDroneMap](../../catalog/repos/opendronemap__odm.md). A fresh map of the area is often
  the best reference for chapter 5 visual matching.

Tooling: [GDAL](../../catalog/repos/osgeo__gdal.md) for format conversion (use conda or
Docker to avoid binding mismatches), [rasterio](../../catalog/repos/rasterio__rasterio.md)
for Python raster access, [QGIS](../../catalog/repos/qgis__qgis.md) to look at everything.

## Displaying it

- 2D web maps: [Leaflet](../../catalog/repos/leaflet__leaflet.md), [MapLibre GL JS](../../catalog/repos/maplibre__maplibre-gl-js.md),
  served by [Martin](../../catalog/repos/maplibre__martin.md) for vector tiles.
- 3D globe with terrain and time-dynamic tracks: [CesiumJS](../../catalog/repos/cesiumgs__cesium.md).
- Large point/track layers: [deck.gl](../../catalog/repos/visgl__deck.gl.md).
- Military symbology: [milsymbol](../../catalog/repos/spatialillusions__milsymbol.md) (chapter 6).

## Planning

Three levels, from fast to slow:

| Level | Question | Typical tools |
|-------|----------|---------------|
| **Mission / task** | Which vehicle does what, in which order? | Behaviour trees ([BehaviorTree.CPP](../../catalog/repos/behaviortree__behaviortree.cpp.md)), PDDL ([PlanSys2](../../catalog/resources/plansys2-paper.md)), auction-style allocation ([CBBA](../../catalog/repos/inmo-jang__consensus-based-bundle-algorithm.md)), coverage ([Fields2Cover](../../catalog/resources/fields2cover-paper.md)) |
| **Global path** | Which route through the map? | Graph search (A*, Dijkstra) on a grid or road graph ([OSRM](../../catalog/repos/project-osrm__osrm-backend.md), [Valhalla](../../catalog/repos/valhalla__valhalla.md)), sampling planners ([OMPL](../../catalog/resources/ompl-site.md)) |
| **Local / trajectory** | How to move the next few seconds without hitting things? | Nav2 controllers ([Nav2 docs](../../catalog/resources/nav2-docs.md)), quadrotor planners ([Fast-Planner](../../catalog/resources/zhou-fast-planner-paper.md), [EGO-Planner](../../catalog/resources/zhou-ego-planner-paper.md)) |

Navigation-aware planning is a good defense-hackathon angle: cost a route not only by
distance and terrain but by **expected navigation quality** - texture for visual matching,
terrain roughness for TERCOM, known interference areas from
[GPSJam](../../catalog/resources/gpsjam-org.md). Reasoning over localization uncertainty
improved mission decisions in DARPA SubT
([NeBula](../../catalog/resources/nebula-costar-subt-paper.md)).

## Multi-agent

- Swarm planning: [EGO-Swarm](../../catalog/repos/zju-fast-lab__ego-planner-swarm.md).
- Multi-robot frameworks: [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md)
  (same mission across autopilots and simulators, [paper](../../catalog/resources/aerostack2-paper.md)),
  [Crazyswarm2](../../catalog/repos/imrclab__crazyswarm2.md).
- Collaborative SLAM under limited bandwidth: [Swarm-SLAM](../../catalog/resources/swarm-slam-paper.md),
  [Kimera-Multi](../../catalog/resources/kimera-multi-tian-2021.md).
- Relative localization between agents by UWB ranging needs no anchors, but observability
  depends on relative motion ([Li et al.](../../catalog/resources/li-onboard-relative-localization-swarms.md)).
- Cooperative ranging reduced drift in UAV-UGV teams underground
  ([Gross webinar](../../catalog/resources/ion-webinar-gross.md)).

## Failure modes under EW

- **Planner trusts a spoofed position:** the path is correct for the wrong place. Feed the
  planner the covariance and refuse aggressive plans when it is large.
- **Geofences** enforced on GNSS position fail with GNSS; enforce on the fused estimate.
- **Comms-denied multi-agent:** decentralised allocation (CBBA) and budgeted map sharing
  (Swarm-SLAM) degrade more gracefully than a central server.
- **Map mismatch:** stale imagery, wrong datum or height reference shift every downstream
  computation silently.

## Learn it

1. [GeographicLib docs](../../catalog/resources/geographiclib-docs.md) - geodesics, geoid, projections.
2. [STAC spec](../../catalog/resources/stac-spec.md) and [Copernicus DEM on AWS](../../catalog/resources/copernicus-dem-aws.md) - data access.
3. [Udacity AI for Robotics](../../catalog/resources/udacity-ai-for-robotics-cs373.md) - search and planning basics.
4. [Survey of ROS 2 algorithms by maintainers](../../catalog/resources/macenski-ros2-algorithms-survey.md) - what is production-ready.
5. [Nav2 docs](../../catalog/resources/nav2-docs.md), [Marathon 2 paper](../../catalog/resources/macenski-marathon2-nav2.md), [Nav2 GPS tutorial](../../catalog/resources/nav2-gps-navigation-tutorial.md).
6. [OMPL site](../../catalog/resources/ompl-site.md) - define state spaces, benchmark planners.
7. [Fast-Planner](../../catalog/resources/zhou-fast-planner-paper.md) and [EGO-Planner](../../catalog/resources/zhou-ego-planner-paper.md) papers.
8. [Aerostack2](../../catalog/resources/aerostack2-paper.md), [PlanSys2](../../catalog/resources/plansys2-paper.md), [Fields2Cover](../../catalog/resources/fields2cover-paper.md).

## Build with it

- [pyproj](../../catalog/repos/pyproj4__pyproj.md), [pymap3d](../../catalog/repos/geospace-code__pymap3d.md), [GeographicLib](../../catalog/repos/geographiclib__geographiclib.md), [mgrs](../../catalog/repos/hobuinc__mgrs.md).
- [GDAL](../../catalog/repos/osgeo__gdal.md), [rasterio](../../catalog/repos/rasterio__rasterio.md), [pystac-client](../../catalog/repos/stac-utils__pystac-client.md), [elevation](../../catalog/repos/bopen__elevation.md), [OpenDroneMap](../../catalog/repos/opendronemap__odm.md).
- [Leaflet](../../catalog/repos/leaflet__leaflet.md), [MapLibre](../../catalog/repos/maplibre__maplibre-gl-js.md), [CesiumJS](../../catalog/repos/cesiumgs__cesium.md), [QGIS](../../catalog/repos/qgis__qgis.md).
- [PythonRobotics](../../catalog/repos/atsushisakai__pythonrobotics.md) - readable planners, e.g. over a rasterised DEM.
- [Nav2](../../catalog/repos/ros-navigation__navigation2.md), [OMPL](../../catalog/repos/ompl__ompl.md), [grid_map](../../catalog/repos/anybotics__grid_map.md).
- [EGO-Swarm](../../catalog/repos/zju-fast-lab__ego-planner-swarm.md), [Aerostack2](../../catalog/repos/aerostack2__aerostack2.md), [CBBA](../../catalog/repos/inmo-jang__consensus-based-bundle-algorithm.md), [Fields2Cover](../../catalog/repos/fields2cover__fields2cover.md).
- [OSRM](../../catalog/repos/project-osrm__osrm-backend.md), [Valhalla](../../catalog/repos/valhalla__valhalla.md), [OSMnx](../../catalog/repos/gboeing__osmnx.md) - road routing.

Related concepts: [geodesy](../../catalog/concepts/geodesy.md), [GIS and mapping](../../catalog/concepts/gis-mapping.md),
[path planning](../../catalog/concepts/path-planning.md), [mission planning](../../catalog/concepts/mission-planning.md),
[obstacle avoidance](../../catalog/concepts/obstacle-avoidance.md), [multi-agent](../../catalog/concepts/multi-agent.md).
