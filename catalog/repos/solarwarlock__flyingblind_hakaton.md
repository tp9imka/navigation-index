# FlyingBlind_Hakaton

`repo:solarwarlock/flyingblind_hakaton` - <https://github.com/SolarWarlock/FlyingBlind_Hakaton>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Python | ? | 2026-07-31 | False | research-prototype | high |

Second public solution to the same 'Полёт вслепую' hackathon task: web prototype that reads a GeoTIFF DEM and NMEA-0183 radar-altimeter messages, searches start point, speed and azimuth hypotheses by RMSE/correlation, and reports a confidence and a flat-terrain check.

**Why it matters:** Shows the practical details (UTM projection, bilinear DEM sampling, weighted scoring for informative relief, flat-terrain rejection) that a TERCOM demo needs.

**Hackathon notes:** Streamlit app on rasterio + pyproj; an optional Rust core (built automatically if cargo is installed) speeds up the hypothesis search. Includes a synthetic NMEA generator from a real DEM, which is handy for building test data fast. Small repo (about a dozen commits).

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../concepts/terrain-nav.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `lang:ru`, `tercom`, `nmea`, `dem`, `rasterio`, `hackathon`

**Domains:** air

## Related

- alternative_to: [Hackathon-Blind-Flight (team GORIZONT)](../repos/t1gr20an06-k__hackathon-blind-flight.md)
- alternative_to: [tercom_nav (TERCOM + ESKF)](../repos/mzahana__tercom_nav.md)

## Referenced by

- [Hackathon-Blind-Flight (team GORIZONT)](../repos/t1gr20an06-k__hackathon-blind-flight.md) (alternative_to)

_Indexed by lane(s): ua-ru-sources_

_GitHub metadata fetched 2026-11-06._
