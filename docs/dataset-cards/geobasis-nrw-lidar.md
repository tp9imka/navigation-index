# Geobasis NRW DOM1 / DGM1 (1 m airborne LiDAR surface and terrain models)

<!-- about: sample:terrain-heightmap-pf -->

North Rhine-Westphalia's survey authority publishes its 1 m digital surface model (DOM1, first-return LiDAR incl. buildings and trees) and 1 m terrain model (DGM1) for the whole state as open data, 1 x 1 km GeoTIFF tiles, no login. A real high-resolution prior map for terrain and heightmap navigation tests. No index id of its own; the marker names the sample that uses it.

| Field | Value |
|---|---|
| Platform | Airborne LiDAR survey (state survey programme) |
| Environment | NRW, Germany. Used here: 4 x 4 km around Duelmen, Muensterland (ETRS89 / UTM 32N, E 379-383 km, N 5741-5745 km): small town, farmland with hedgerows, forest; DSM 45-136 m, DTM 40-93 m |
| Sensors and rates | Gridded products, 1 m. DOM1 = surface incl. buildings and vegetation; DGM1 = bare earth |
| Ground truth | Survey product; vertical accuracy not stated in what the sample read. Metadata rows checked by the sample are dated March 2024 |
| Size | One tile pair (HEAD Content-Length, 2026-11-06): `dom1_32_379_5741_1_nw_2024.tif` 2,081,151 B, `dgm1_32_379_5741_1_nw_2024.tif` 1,690,850 B. The sample's 32 tiles (16 DOM1 + 16 DGM1) came to about 80 MB (README; 64 MiB by du) |
| License | Datenlizenz Deutschland - Zero - Version 2.0 (dl-de/zero-2.0), per the Bezirksregierung Koeln open data terms PDF (read by the sample 2026-11-06). No attribution required under that licence |
| Format | GeoTIFF, EPSG:25832, 1000 x 1000 px per tile |
| Index | [terrain-heightmap-pf sample](../../samples/terrain-heightmap-pf/) |

## Download

```bash
# tile name pattern: {product}_32_{east_km}_{north_km}_1_nw_{year}.tif
B=https://www.opengeodata.nrw.de/produkte/geobasis/hm
curl -O $B/dom1_tiff/dom1_tiff/dom1_32_379_5741_1_nw_2024.tif
curl -O $B/dgm1_tiff/dgm1_tiff/dgm1_32_379_5741_1_nw_2024.tif
# what the sample does: 4 x 4 km of both products, mosaicked to data/duelmen.npz (~100 s)
python3 samples/terrain-heightmap-pf/fetch_lidar.py
```

The year suffix differs between areas (flight year); list the directory if a name 404s.

## Used in this repo

[samples/terrain-heightmap-pf](../../samples/terrain-heightmap-pf/) `fetch_lidar.py` + `run_lidar.py`, run 2026-11-06: 1 m vs 30 m (GLO-30) reference, binary edges vs gradient magnitude. On the 1 m surface model, binary edges reached 0.6 m and continuous gradients 0.4 m median final error after a simulated 4 km loop (odometry alone: 131 m); the same methods on GLO-30 at 30 m gave 19.9 and 13.9 m. On the bare-earth DTM binary edges found nothing to match, gradients still gave 6.5 m. The onboard "local map" there is the same DSM plus noise, so treat these as best cases, not flight results.

## Loading and tooling

rasterio, one tile at a time; the sample asserts 1 m resolution and 1000 x 1000 shape and flips rows so row 0 is the south edge.

## Hackathon fit

- Idea 11 (terrain-relative navigation over a real DEM): a 1 m surface model with buildings and trees, where GLO-30 smooths them away.
- Any heightmap or LiDAR map-matching demo in a European setting.

## Pitfalls

- NRW only. Bavaria's DGM1 also answered without login (`download1.bayernwolke.de/a/dgm/dgm1/<E>_<N>.tif`, per the sample) but is terrain only; other German states vary.
- DOM1 includes vegetation, which changes with season; a summer flight vs a winter map differs.
- A real onboard LiDAR has to classify ground before comparing against DGM1.

## Sources

- HEAD on one DOM1 and one DGM1 tile, 2026-11-06
- samples/terrain-heightmap-pf/README.md (section "Real 1 m airborne LiDAR") and `fetch_lidar.py`
