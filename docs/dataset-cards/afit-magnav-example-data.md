# AFIT MagNav example data

<!-- about: repo:afit-eeng-magnav/example-data, repo:mit-ai-accelerator/magnav.jl, res:magnav-challenge-site -->

A small GitHub mirror from AFIT's MagNav group bundling one SGL challenge flight as an XYZ text export, the MIT-AIA anomaly maps, the USGS North American magnetic anomaly grid and an EGM2008 geoid. Handy when Zenodo/Dropbox are slow or a team does not use Julia.

| Field | Value |
|---|---|
| Platform | Same SGL Cessna Grand Caravan flight data as the [MagNav challenge](magnav-challenge-data.md) (Flt1002) |
| Environment | Ottawa area (flight + maps); North America (NAMAD grid) |
| Sensors and rates | Flight 1002 magnetometers, INS, aux at 10 Hz (file name) |
| Ground truth | GPS in the flight file; maps are the reference for map matching |
| Size | Git tree sizes (2026-11-06): `aia-maps.zip` 98.6 MB (also HEAD-confirmed 98,562,784 B), `10Hz_Mag_INS_Aux_Flt1002.xyz.zip` 72.2 MB, `USMAG_origmrg.gxf.zip` 41.8 MB, `egm2008-2_5.pgm.zip` 64.2 MB. Total about 277 MB |
| License | None stated in the repo. Underlying sources carry their own terms (MIT-AIA data agreement, USGS public data, GeographicLib geoids) |
| Format | Zipped XYZ (Geosoft-style text), GXF grid, PGM geoid |
| Index | [example-data](../../catalog/repos/afit-eeng-magnav__example-data.md), [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md), [challenge site](../../catalog/resources/magnav-challenge-site.md) |

## Download

```bash
R=https://github.com/AFIT-EENG-MagNav/example-data/raw/refs/heads/main
curl -LO $R/mit-aia/aia-maps.zip
curl -LO $R/mit-aia/flight1002/10Hz_Mag_INS_Aux_Flt1002.xyz.zip
curl -LO $R/namad/USMAG_origmrg.gxf.zip
curl -LO $R/geodesy/geoids/egm2008-2_5.pgm.zip
```

## Loading and tooling

- XYZ: whitespace text with a header line; `pandas.read_csv(..., sep=r"\s+")` after inspecting the header.
- GXF grid: GDAL reads GXF (`gdal_translate USMAG_origmrg.gxf usmag.tif`); MagNav.jl has GXF map readers.
- Geoid PGM: GeographicLib format (for MSL vs ellipsoid height conversion).

## Hackathon fit

Idea 16 (MagNav sprint) for non-Julia teams; Idea 11 (terrain-relative nav) borrows the map-matching particle filter pattern with a magnetic map in place of a DEM.

## Pitfalls

- The README's first `wget` uses a `/blob/<sha>/` URL, which returns an HTML page, not the zip. Use the `/raw/` URLs above.
- Flt1002 only; for more flights use the Zenodo HDF5 record.
- Redistribution terms of the MIT-AIA data still apply even though it sits on GitHub.

## Sources

- Repo README and git tree (gh api, 2026-11-06); HEAD on the raw `aia-maps.zip` URL
