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

## Used in this repo

[samples/magnav-quickstart](../../samples/magnav-quickstart/), run 2026-11-06 in the official `julia:1.11` Docker image (Julia 1.11.9, linux/arm64):

- Data came through MagNav.jl's artifacts, not the Zenodo URLs: `MagNav.sgl_2020_train(:Flt1006)` and `MagNav.ottawa_area_maps(:Eastern_395)`. On disk: `sgl_2020_train` about 563 MB, `ottawa_area_maps` about 1.2 GB (Eastern_395.h5 alone 275 MB), plus EMAG2 about 0.5 GB that MagNav fetches. The Julia depot ended at 5.8 GB (4.1 GB artifacts, 1.3 GB precompile cache). The script also needs `examples/dataframes/*.csv` from a MagNav.jl clone (19 MB).
- Flt1006, line 1006.08 on Eastern_395, 8391 samples at 10 Hz (14 min): INS-only error grew to 219 m; the MagNav EKF stayed at 15-55 m, DRMS 31 m (CRLB DRMS 13 m). Two runs identical with `seed!(33)`.
- Tolles-Lawson on the tail-stinger mag did not lower the map residual on this line (4.63 nT uncompensated vs 5.84 nT); compensation matters for the in-cabin mags.
- First attempt was OOM-killed (exit 137) in a 7.7 GB Docker VM shared with other containers; `--heap-size-hint=2500M` and `JULIA_NUM_THREADS=1` fixed it.
- FFTA 0.3.2 broke precompilation (`plan_rfft` method ambiguity, so `using MagNav` failed); pinning `FFTA` to 0.2 fixed it.

## Loading and tooling

- Julia: [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md) downloads `sgl_2020_train`, `sgl_2021_train` and the Ottawa maps as lazy artifacts and has Tolles-Lawson, NN compensation and an EKF. Walkthrough: [magnav-quickstart](../../catalog/samples/magnav-quickstart.md) (ran, see below).
- Python: `h5py.File("Flt1006_train.h5")` then list keys; field names are in the datasheet PDF.

## Hackathon fit

Idea 16 (MagNav compensation sprint): Tolles-Lawson on a calibration box, then compensate a cabin magnetometer and compare to the stinger; stretch goal is the EKF map-matching run. Also a jam-proof alt-PNT story for any pitch.

## Pitfalls

- License tension: public-domain notice plus an Air Force AUA that forbids redistribution and limits purpose. Do not re-host the files; link to Zenodo.
- MagNav.jl artifact hash mismatches happen; README explains manual folder renaming. Dropbox-hosted artifacts depend on Dropbox links staying alive.
- Ottawa maps are 0.7 GB compressed, about 1.2 GB unpacked, and the Julia depot reaches about 6 GB with precompile; download and precompile before the event.
- Flights differ in which sensors are valid; read the per-flight readme before choosing a line.

## Sources

- Zenodo API for records 4271804 and 12723700 (titles, descriptions, file sizes, LICENSE.md, DATA_SHARING_AGREEMENT.md), 2026-11-06
- MagNav.jl README and `Artifacts.toml`; HEAD on two Dropbox artifact URLs
- samples/magnav-quickstart/README.md (artifact sizes on disk, memory, run results)
