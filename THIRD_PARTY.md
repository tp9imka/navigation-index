# Third-party material

Navigation Index code is Apache-2.0 ([LICENSE](LICENSE)); docs and data are CC BY 4.0
([LICENSE-docs](LICENSE-docs)). The items below are not ours. They keep their own licence, and
their attribution string travels with them. If you copy one of these files, copy its line here too.

Status words: **redistributed** = the file is in this repo; **derived** = the repo holds results,
maps or images computed from the item, not the item itself; **runtime** = a browser page loads it
from a CDN or tile server and the repo holds no copy; **fetch on demand** = the repo holds a script
that downloads it, and the item is git-ignored.

## Data and imagery in the repo

| Item | Where | Status | Licence | Attribution string |
|---|---|---|---|---|
| OpenDroneMap `odm_data_aukerman` eBee frames | `samples/geoloc-license-clean/thumbs/real_DSC00255.jpg` (and the frame inside `real_DSC00255_naip2019_fix.jpg`) | redistributed (thumbnail) | CC0-1.0 (repo `license.txt`) | none required; credit "OpenDroneMap odm_data_aukerman" |
| USDA NAIP orthophotos 2019 / 2023, via Microsoft Planetary Computer | `samples/geoloc-license-clean/thumbs/*` (NAIP crops and synthetic frames cut from NAIP); `samples/golden-demo/data/vgeo_table.json` (fixes matched against NAIP) | redistributed (thumbnails), derived | Public domain (US Government work); AWS registry: "Public Domain with Attribution" | "Imagery: USDA Farm Service Agency, National Agriculture Imagery Program (NAIP)" |
| OpenStreetMap data (coastline, bridge, wind turbines, seamarks) | `samples/usv-gnss-denied-nav/fixtures/oresund_chart.json.gz` | redistributed (extract, 100 KB) | ODbL 1.0 | "(c) OpenStreetMap contributors, ODbL 1.0, https://www.openstreetmap.org/copyright" |
| Danish Maritime Authority AIS | `samples/usv-gnss-denied-nav/fixtures/oresund_ais_window.csv.gz`; `samples/maritime-ais-spoofing/fixtures/dma_excerpts.csv`, `samples/maritime-ais-spoofing/example_output/real_alerts.*` | redistributed (excerpts), derived | Danish public data, free reuse under the Danish PSI act with attribution | "Contains data from the Danish Maritime Authority that is used in accordance with the conditions for the use of Danish public data" |
| Copernicus DEM GLO-30 | `samples/terrain-heightmap-pf/out/*` (maps, error plots, results), `samples/two-source-integrity-vpair/results/*`, `samples/osint-jamming-map/out/*` (slope mask) | derived | Copernicus DEM licence (free, attribution required) | "Produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved" |
| Copernicus Sentinel-1 GRD and RFI annotation, via Microsoft Planetary Computer | `samples/osint-jamming-map/out/s1_cells.geojson`, `s1_summary.json`, `zones.geojson`, `map.png`, `dashboard.png` | derived | Copernicus Sentinel data policy (free and open); Planetary Computer terms apply to the hosting | "Contains modified Copernicus Sentinel data 2026" |
| Geobasis NRW DOM1 / DGM1 | `samples/terrain-heightmap-pf/out/lidar*`, `samples/two-source-integrity-vpair/results/*` | derived | Datenlizenz Deutschland - Zero - Version 2.0 | none required; credit "Geobasis NRW" |
| ADS-B Exchange free `readsb-hist` sample, 2026-10-01 | `samples/osint-jamming-map/out/adsb_cells.geojson`, `adsb_summary.json`, `control_adsb_summary.json`, `map.png`, `dashboard.png`; raw reports `out/adsb-*.jsonl` are **fetch on demand** (`.venv/bin/python adsb_hexmap.py`) | derived (per-hex counts) | no open licence named; ADS-B Exchange Terms of Use apply | "Data: ADS-B Exchange (adsbexchange.com)" |
| Natural Earth 10m / 50m land | map background and land/sea test in `samples/osint-jamming-map/out/*`; land mask behind `samples/maritime-ais-spoofing/example_output/*` | derived | Public domain | none required; credit "Natural Earth" |
| OpenStreetMap standard tiles | dashboard screenshots: `samples/*/results/screenshots/*.jpg`, `samples/usv-gnss-denied-nav/example_output/dashboard-*.jpg`, `samples/osint-jamming-map/out/dashboard.png`, `templates/demo-dashboard/screenshots/` | derived (screenshots; attribution visible in each image) | ODbL 1.0 (data); tile terms at https://www.openstreetmap.org/copyright | "(c) OpenStreetMap contributors" |
| Galileo OSNMA public key, PKID 2 (European GNSS Service Centre) | `samples/osnma-authentication/gnss-sdr/OSNMA_PublicKey_PKID2.pem` | redistributed (public key, converted to PEM) | published by the GSC for receiver use; no licence text checked | "Galileo OSNMA public key, European GNSS Service Centre" |

## Code in the repo

| Item | Where | Licence | Notice |
|---|---|---|---|
| MILUV devkit `config/` values (UWB anchor positions, tag lever arms, height biases, experiment table) | `samples/swarm-coop-real-uwb/miluv_io.py` (constants block) | MIT, "Copyright (c) 2024 DECAR" | full MIT text above the copied block |
| zephr-xyz/sentinel1-rfi-detection (`temporal_rfi.py`, `rfi_pipeline.py`) | `samples/osint-jamming-map/s1_rfi.py` (a port: same constants and method, rewritten) | MIT | rewritten port; upstream and licence named in the module docstring |

## Fetched on demand (never committed)

| Item | Licence | Fetch command (from the sample folder) | Writes |
|---|---|---|---|
| KITTI raw drive 2011_09_30_drive_0016 + odometry poses | CC BY-NC-SA 3.0 | `.venv/bin/python fetch_truth.py lidar` in `samples/relative-nav-benchmark` | `results/lidar/kitti04_gt.tum`, `kitti04_oxts.tum`, `results/navdash/kitti04/truth.jsonl` |
| UZH-FPV indoor_forward_3 (Snapdragon bag) | CC BY-NC-SA 3.0 | `.venv/bin/python fetch_truth.py vio` | `results/vio/uzhfpv_indoor_forward_3_gt.tum`, `results/navdash/uzhfpv_indoor_forward_3/truth.jsonl` |
| VPAIR sample (Zenodo 6473989) | README: academic use only, commercial use prohibited (Zenodo record tagged CC BY 4.0; the stricter term is followed) | `.venv/bin/python fetch_truth.py aerial`; `.venv/bin/python fetch_truth.py` in `samples/e2e-visual-nav-vpair` and in `samples/two-source-integrity-vpair` | `results/aerial/vpair_gt.tum`, `results/navdash/vpair/truth.jsonl`; `results/navdash/truth.jsonl` in the two VPAIR samples |
| ADS-B Exchange raw reports | see above | `.venv/bin/python adsb_hexmap.py` in `samples/osint-jamming-map` | `out/adsb-bad.jsonl`, `out/adsb-good.jsonl` |

The trajectories this repo computed on these datasets (KISS-ICP, OpenVINS, mono VO, nadir VO,
fused tracks, metrics JSON) stay in the repo as our own outputs. Every other sample downloads its
datasets at run time; their licences are in each sample README and in `docs/dataset-cards/`.

## Libraries loaded at runtime by the site (no copy in the repo)

| Library | Version | Loaded by | From | Licence |
|---|---|---|---|---|
| marked | 12.0.2 | `site/index.html` | cdnjs.cloudflare.com | MIT |
| DOMPurify | 3.1.6 | `site/index.html` | cdnjs.cloudflare.com | MPL-2.0 OR Apache-2.0 |
| vis-network | 9.1.9 | `graph/index.html` | cdnjs.cloudflare.com | Apache-2.0 OR MIT |
| MapLibre GL JS | 4.7.1 | `templates/demo-dashboard/index.html` | unpkg.com (`fetch-vendor.sh` copies it to a git-ignored `vendor/`) | BSD-3-Clause |
| milsymbol | 3.0.4 | `templates/demo-dashboard/index.html` | unpkg.com | MIT |
| PMTiles | 4.4.1 | `templates/demo-dashboard/index.html` | unpkg.com | BSD-3-Clause |
| Pyodide | 314.0.7 (`site/playground/manifest.json`) | `site/playground/` worker | cdn.jsdelivr.net, or a local copy the user fills | MPL-2.0; the bundled Python packages (numpy, scipy, ...) keep their own licences |
| OpenStreetMap tile server | - | `templates/demo-dashboard` default basemap | tile.openstreetmap.org | ODbL 1.0 data; OSMF tile usage policy applies |

## Open items (not settled by this file)

- `samples/e2e-visual-nav-vpair/results/frontend.json` and `frontend_yaw2.json` hold the VPAIR
  reference-tile positions (`tiles.en`, local East/North metres) next to our match results. Those
  positions are the dataset's poses in another frame, so they may fall under VPAIR's academic-use
  term too.
- `samples/dismounted-foot-ins/dash/walk1/truth.jsonl` holds surveyed floor markers from the UTIAS
  pyshoe hallway dataset; its terms were not checked beyond "open access" on IEEE DataPort.
- `samples/real-attack-replay/labels.json` copies UTC attack windows from VAARA's
  `Jammertest_metadata.md`; VAARA states no licence.
- `samples/osint-jamming-map/s1_rfi.py` is a port of MIT code and does not carry the MIT notice yet.
