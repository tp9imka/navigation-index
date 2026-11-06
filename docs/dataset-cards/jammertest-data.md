# Jammertest data: Fraunhofer IIS 2025 IQ, VAARA 2024 receiver logs, NPRA test plan

<!-- about: res:jammertest-norway, repo:felixott94/fraunhoferiis_jammertest2025, repo:univaasadigieco/vaara, repo:npra/jammertest-plan, sample:jammer-sensor-network -->

Jammertest (Andoya, Norway) is the annual authority-run live GNSS jamming/spoofing/meaconing event. Three public pieces fit together: NPRA's test catalog and per-day transmission plans (the labels), Fraunhofer IIS's labelled raw IQ from 2025, and University of Vaasa's phone and u-blox logs from 2024.

| Field | Value |
|---|---|
| Platform | Fraunhofer: two fixed sites (Area 1 near Bleik community house, Area 2 parking-lot site). VAARA: phones and u-blox receivers in test cars / at test sites per test |
| Environment | Real over-the-air interference at Andoya: CW, sweep, PRN, chirp variants, FM, meaconing, spoofing, multi-emitter |
| Sensors and rates | Fraunhofer: "Innosense" E1/E5a front end, 8-bit IQ, 81 MHz sampling, 40.5 MHz bandwidth, no AGC (fixed VGA); 2x2 CRPA array, 100 MHz, 10 us snapshots (README). VAARA: Android GnssLogger logs (`.txt.xz`), NMEA, RINEX `.24o`, u-blox `.ubx.xz` (tree listing) |
| Ground truth | Fraunhofer: per-sample labels (jammer type 0-16, emitted power dBm, bandwidth MHz, VGA, band) inside each HDF5. VAARA: `Jammertest_metadata.md/json` with test IDs and UTC windows. Positions: NPRA Appendix H "Andoya Ground Truth" PDF |
| Size | Fraunhofer: 360.2 GB total in 230 Git LFS parts (sum of LFS pointer sizes, 2026-11-06), Area 1 253 GB, Area 2 106 GB; one chunk pair about 2.9 GB (part-aa 1,992,294,400 B confirmed by HEAD). VAARA: 1.57 GB uncompressed blobs across 3 days (git tree sizes). NPRA plan repo: Testcatalog.pdf 92 MB, JSON files under 0.4 MB |
| License | Fraunhofer: CC BY-NC-SA 4.0 (README). VAARA: none stated (no LICENSE, GitHub reports none). NPRA plan: MIT |
| Format | HDF5 (`/data` int8 interleaved IQ, `/label` 5 columns), split as `.h5.part-aa/ab/ac`; VAARA plain files; NPRA JSON + PDF |
| Index | [Jammertest](../../catalog/resources/jammertest-norway.md), [Fraunhofer IIS 2025](../../catalog/repos/felixott94__fraunhoferiis_jammertest2025.md), [VAARA](../../catalog/repos/univaasadigieco__vaara.md), [Jammertest plan](../../catalog/repos/npra__jammertest-plan.md), [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md), [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) |

## What's in it

- Fraunhofer IIS: `dataset/Sample_<Area>_<start>_<end>.h5.part-*`, 25,000 samples per logical file; `splits/` text files with train/test lists; `utilities_innosense.py`, `utilities_crpa.py`. Recommended splits: within-area random, area transfer, receiver transfer, weak-jammer filtering (README). Class balance follows the real plan, so it is imbalanced on purpose.
- VAARA: `2024-09-10`, `2024-09-11`, `2024-09-12` folders by test; each phone folder has GnssLogger raw, NMEA, RINEX obs and a `nmea.csv`. Metadata maps test codes (e.g. 1.10.6 "driving while passing three parked cars with multi-band jammer", 2.1.1 "large position and time jump") to UTC windows with field notes. Released "in few batches in autumn 2025".
- NPRA: `testcatalog.json` (all tests ever), `testcatalog2025.json`, per-day plan JSON for 2025 and 2026, appendices (test areas, spoofed routes, jammer equipment, ground truth).

## Download

```bash
# NPRA plan (small)
git clone --depth 1 https://github.com/NPRA/jammertest-plan

# VAARA, 1.6 GB plain git (no LFS)
git clone --depth 1 https://github.com/UniVaasaDigiEco/VAARA
# or one u-blox file (5.7 MB)
curl -LO "https://raw.githubusercontent.com/UniVaasaDigiEco/VAARA/main/2024-09-10/Test_2/ublox_2024-09-10T115512Z0000.ubx.xz"

# Fraunhofer: clone without LFS, then pull one chunk pair (~2.9 GB)
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/FelixOtt94/FraunhoferIIS_Jammertest2025
cd FraunhoferIIS_Jammertest2025
git lfs pull --include="dataset/Sample_Area1_0000000_0024999.h5.part-*"
cat dataset/Sample_Area1_0000000_0024999.h5.part-* > Sample_Area1_0000000_0024999.h5
```

## Loading and tooling

```python
import h5py, numpy as np
with h5py.File("Sample_Area1_0000000_0024999.h5") as f:
    print(list(f.keys()))           # README: /data and /label
    lab = f["label"][:]             # type, power_dBm, bw_MHz, vga, band
```

Map `type` with the README's `jammer_map` (0 CW ... 16 Chirp+Prn+Triang). VAARA phone logs load with `gnss_lib_py.AndroidRawGnss`; u-blox UBX with pyubx2 (not indexed) or RTKLIB `convbin`; join to the plan by UTC window. VAARA u-blox files mix NMEA and UBX in one stream; see "Used in this repo" for the parser gotchas.

## Used in this repo

- **samples/real-attack-replay** (being written in this round; on 2026-11-06 it had code but no README yet, so the facts below come from reading its code, not from a run). It replays **VAARA 2024 u-blox logs**. From its `ubx_nmea_epochs.py` docstring: those logs carry NMEA (RMC, GGA, GSA, GSV, GLL) plus UBX `RXM-RAWX`, `RXM-MEASX`, `RXM-SFRBX`, `MON-SPAN`, but **no UBX `NAV-*` messages**, so a NAV-PVT / NAV-SAT based adapter has nothing to read; pyubx2 1.4.1 raises on a `$` byte inside binary payloads, so the sample frames both protocols itself. Under time spoofing the receiver UTC jumps, so it rebuilds a monotonic time axis. Clock bias comes from an RTKLIB SPP run (`run_rtklib_spp.sh`: `convbin` => RINEX 3.04 => `rnx2rtkp`, in the `rtklib-demo5` image from [gnss-rinex-processing](../../samples/gnss-rinex-processing/)). Its `labels.json` picks 7 u-blox files across all 3 days (2024-09-10 Test_1/Test_2, 2024-09-11 Morning_Motorcade and Afternoon Test_1/Test_2, 2024-09-12 Test_1/Test_2): jamming tests 1.10.3, 1.10.4, 1.10.6a-d, 0.3.1a-f, spoofing tests 2.6.1-2.6.3 and 2.4.2, 2.4.3, 2.4.12, 2.4.13, plus one quiet window. Those 7 `.ubx.xz` blobs total about 64 MB (git tree sizes, 2026-11-06), so the replay subset is far smaller than the 1.57 GB repo. Label finding recorded there: windows not in the VAARA field log come from the NPRA 2024 plan shifted 50 min earlier, the offset between the plan and the VAARA-logged 2.4.12, cross-checked against C/N0 and receiver-time signatures. Results and run facts belong to that sample's README once written.
- [samples/jammer-sensor-network](../../samples/jammer-sensor-network/) is simulation only; it names Jammertest (Fraunhofer IQ) as where to calibrate its AGC model.
- No sample has pulled the Fraunhofer IQ yet.

## Hackathon fit

- Idea 1 (interference monitor => TAK): VAARA phone C/N0 and AGC drops time-aligned with test windows give a realistic replay feed; Fraunhofer labels give a classifier.
- Idea 4 (Android spoofing detector): VAARA spoofing tests (2.x codes) are real-world phone data under spoofing.
- Idea 9 (spoof-aware source switching): use plan JSON to script realistic attack timelines in SITL.

## Pitfalls

- Fraunhofer data is non-commercial (NC) and share-alike. LFS bandwidth quotas on GitHub can block bulk pulls; the GitLab mirror named in the README returned 404 to an anonymous request (2026-11-06).
- README says "the exact internal key structure may depend on the exported version" - print keys first.
- Power labels are emitted power, not received; jammer distance varies.
- VAARA metadata notes log errors (e.g. a test logged as 1.10.4 that was 1.10.3) and CET vs UTC; trust the corrected UTC lines.
- Transmission plans change year to year; match the plan year to the data year.

## Sources

- READMEs and git trees of the three repos (gh api, 2026-11-06); LFS pointer files read via raw.githubusercontent.com; HEAD on media.githubusercontent.com for one part
- `Jammertest_metadata.md` in VAARA
