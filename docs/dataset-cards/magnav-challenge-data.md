# MagNav challenge flight data (DAF-MIT AIA / SGL, Zenodo)

<!-- about: res:magnav-zenodo-dataset, res:magnav-sgs-flight-data, res:magnav-challenge-site, res:afrl-magnav-challenge-2020, repo:mit-ai-accelerator/magnav.jl, repo:lw-kong/magnav, sample:magnav-quickstart -->

Airborne magnetic anomaly navigation flight data collected by Sander Geophysics (SGL) near Ottawa for the DAF-MIT AI Accelerator MagNav challenge. Two Zenodo records: the original 2020 challenge release and the later "Open Flight Data" record (v3) that adds the 2021 flights.

| Field | Value |
|---|---|
| Platform | Cessna Grand Caravan survey aircraft (record 12723700 description) |
| Environment | Near Ottawa, Ontario; survey lines and transits at varied altitudes; deliberate disturbances (flaps, fuel pump, radio, moving magnetic material) |
| Sensors and rates | 5 optically pumped cesium scalar magnetometers (one on tail stinger = near-clean reference, four in cabin = noisy), 4 fluxgate vector magnetometers, INS, GPS, voltages/currents. 10 Hz (file name `10Hz_Mag_INS_Aux_Flt1002` in AFIT mirror; MagNav docs) |
| Ground truth | GPS position; tail-stinger magnetometer as compensation truth. Map: Ottawa-area anomaly maps (MagNav.jl artifact) |
| Size | Zenodo API (2026-11-06): record 4271804 = 0.39 GB (Flt1002-1005, 4 HDF5); record 12723700 = 1.16 GB (Flt1002-1007 + 10 of Flt2001-2017, 16 HDF5 in all, datasheets, readme zips). MagNav.jl artifacts via Dropbox HEAD: `sgl_2020_train_v3.tar.gz` 182.6 MB, `ottawa_area_maps_v3.tar.gz` 710.5 MB |
| License | Mixed: `LICENSE.md` says public domain (17 U.S.C. 105); record 12723700 also ships an Air Force Acceptable Use Agreement limiting use to non-profit research, education or government purposes and restricting redistribution. Zenodo license field: "other-at" |
| Format | HDF5 per flight (`FltNNNN_train.h5`), PDF datasheets |
| Index | [Zenodo 2020](../../catalog/resources/magnav-zenodo-dataset.md), [Zenodo open flight data](../../catalog/resources/magnav-sgs-flight-data.md), [challenge site](../../catalog/resources/magnav-challenge-site.md), [challenge paper](../../catalog/resources/afrl-magnav-challenge-2020.md), [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md), [lw-kong submission](../../catalog/repos/lw-kong__magnav.md), [quickstart sample](../../catalog/samples/magnav-quickstart.md) |

## What's in it

| Record | Files (bytes from Zenodo API) |
|---|---|
| 4271804 (2020-11-13, v1) | Flt1002 152.8 MB, Flt1003 117.8 MB, Flt1004 60.0 MB, Flt1005 60.2 MB |
| 12723700 (v3) | 2020: Flt1002-1007 (smallest Flt1004 62.7 MB); 2021: Flt2001, 2002, 2004-2008, 2015-2017 (smallest Flt2005 3.2 MB, Flt2017 9.2 MB); `datasheet_sgl_2020_train.pdf`, `datasheet_sgl_2021_train.pdf`, per-flight readme zips |

Use record 12723700; it supersedes the 2020 one and has the datasheets.

## Download

```bash
Z=https://zenodo.org/api/records/12723700/files
curl -L -o Flt1006_train.h5 $Z/Flt1006_train.h5/content        # 83 MB, used by the quickstart
curl -L -o datasheet_sgl_2020_train.pdf $Z/datasheet_sgl_2020_train.pdf/content
# all files
curl -s https://zenodo.org/api/records/12723700 | python3 -c \
 "import json,sys;[print(f['links']['self']) for f in json.load(sys.stdin)['files']]" | xargs -n1 curl -LO
```

## Loading and tooling

- Julia: [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md) downloads `sgl_2020_train`, `sgl_2021_train` and the Ottawa maps as lazy artifacts and has Tolles-Lawson, NN compensation and an EKF. Walkthrough: [magnav-quickstart](../../catalog/samples/magnav-quickstart.md) (unverified sketch, Julia not run).
- Python: `h5py.File("Flt1006_train.h5")` then list keys; field names are in the datasheet PDF.

## Hackathon fit

Idea 16 (MagNav compensation sprint): Tolles-Lawson on a calibration box, then compensate a cabin magnetometer and compare to the stinger; stretch goal is the EKF map-matching run. Also a jam-proof alt-PNT story for any pitch.

## Pitfalls

- License tension: public-domain notice plus an Air Force AUA that forbids redistribution and limits purpose. Do not re-host the files; link to Zenodo.
- MagNav.jl artifact hash mismatches happen; README explains manual folder renaming. Dropbox-hosted artifacts depend on Dropbox links staying alive.
- Ottawa maps are 0.7 GB; download before the event.
- Flights differ in which sensors are valid; read the per-flight readme before choosing a line.

## Sources

- Zenodo API for records 4271804 and 12723700 (titles, descriptions, file sizes, LICENSE.md, DATA_SHARING_AGREEMENT.md), 2026-11-06
- MagNav.jl README and `Artifacts.toml`; HEAD on two Dropbox artifact URLs
