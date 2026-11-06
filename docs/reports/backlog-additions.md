# Backlog additions (2026-11-06)

Lane `backlog`: items other lanes flagged as missing. Written to `data/resources/backlog.json` (73 resources) and `data/repos/backlog.json` (8 repos). `tools/build.py` reports 0 dangling ids and 0 bad concepts.

## How it was verified

- Duplicates: checked against `index/records.jsonl`, every lane file's ids and URLs, and all arXiv ids already in `data/`. No id or URL collisions.
- Authors, venue, volume and year: from the arXiv API for arXiv papers, Crossref or OpenAlex by DOI for the rest. Nothing was typed from memory. Two corrections came out of this:
  - The Blanch et al. 2015 TAES ARAIM paper has 8 authors, not 3.
  - "Unveiling Starlink LEO Satellite OFDM-Like Signal Structure" (TAES 2024) is Neinavaie & Kassas, not Kozhaya. Kozhaya's paper is the separate NAVIGATION 2025 "Unveiling Starlink for PNT".
- ARAIM reports: downloaded from archive.gps.gov. Title, date and contents were read from the PDF text via PDFKit.
- Dataset licences: read from the hosting pages and APIs (Figshare, Kaggle, Zenodo, GitHub).
- Repos: checked with `gh api repos/...`.
- URLs: all probed. DOI links resolve but land on publisher bot walls (Wiley, SAGE, IEEE 202). MDPI, osuva.uwasa.fi and UPCommons also sit behind bot checks.
- `related` edges: only edges I could verify. I removed speculative `cites` edges.

## Added, by flagged item

**Covariance intersection / cooperative localization (13)**
- Julier & Uhlmann 1997 (CI)
- Carrillo-Arce et al. 2013
- Luft et al. 2018
- Roumeliotis & Bekey 2002
- Leung, Barfoot & Liu 2010
- Wymeersch, Lien & Win 2009 (open PDF)
- Fox et al. 2000
- Kia et al. 2016
- Zhu & Kia 2019
- Chang et al. 2021 (resilient CI)
- Zhu et al. 2021 (distributed VI-CL)
- Tu et al. 2025 (weighted CI)
- Pedroso et al. 2026 (ultra-large-scale CL)

**Integrity (15)**
- Classic RAIM and ARAIM papers:
  - Parkinson & Axelrad 1988
  - Brown 1992
  - Joerger, Chan & Pervan 2014
  - Blanch et al. 2015
- EU-US WG-C ARAIM reports:
  - Interim (Milestone 1) report, 2012
  - Milestone 2 report, 2015
  - Milestone 3 report, 2016
- Stanford diagram:
  - Stanford GPS Lab WAAS metrics page (primary source for the error-vs-PL histogram, with its MATLAB scripts)
  - Tossaint et al. 2006, the Stanford-ESA diagram
  - Navipedia explainer
- Urban and vision integrity:
  - Ni Zhu et al. 2018 (urban GNSS integrity review)
  - Bhamidipati & Gao 2020 (Graph-SLAM GPS + camera PLs)
  - Chen Zhu, Meurer & Gunther 2022 (integrity of visual navigation)
  - Gupta & Gao 2021 (camera/3D-map PLs)
  - Zhu et al. 2026 (LIO deterministic PL)

**Terrain navigation in English (12)**
- Historic baselines:
  - Golden 1980 (TERCOM)
  - Hostetler & Andreas 1983 (SITAN)
  - Bergman 1999 PhD thesis (free PDF)
  - Bergman, Ljung & Gustafsson 1999 (point-mass filter)
  - Nordlund & Gustafsson 2009 (marginalized PF)
- Radar-altimeter TRN:
  - Oh et al. 2019 (interferometric radar altimeter)
  - Kang & Yu 2021 (interferometric radar altimeter)
- Recent work:
  - Matousek et al. 2023 and 2026 (efficient and tensor PMF, both with code)
  - Park & Bang 2025 (TAES)
  - Sanlan et al. 2025 (point-cloud TAN)
  - Maggio et al. 2023 (vision TRN, balloon and New Shepard flights)

**MagNav (6)**
- Gnadt's MIT PhD thesis 2022 (DSpace, open)
- Gnadt et al. Tolles-Lawson derivation (arXiv)
- Canciani & Raquet 2016 (NAVIGATION; public-domain US Government work)
- Canciani & Raquet 2017 (TAES flight test)
- Canciani 2022 (F-16 online calibration)
- Hager et al. 2026 (cold-start NN online calibration)

**LEO PNT (11)**
- Kassas group:
  - Neinavaie, Khalife & Kassas 2022 (TAES first results)
  - Neinavaie & Kassas 2024 (OFDM structure)
  - Kozhaya, Saroufim & Kassas 2025 (open)
- Humphreys group:
  - Iannucci & Humphreys (fused LEO GNSS)
  - Qin et al. 2025 (Starlink timing)
  - Qin, Psiaki, Bowman & Humphreys 2026 (pilots)
  - Graff & Humphreys 2024 (OFDM bounds)
- Other groups:
  - Stock et al. 2023 (Starlink burst detection)
  - Park, Kim & Seo 2026 (blind Doppler matching on SDR monitoring data)
  - Reid et al. 2018
  - Prol et al. 2022 (survey)

**Timing spoofing detection (3)**
- Safi 2025 University of Vaasa MSc thesis on Jammertest 2024 timing spoofing
- Safi et al. IPIN 2025
- Enan et al. 2025 (zero-day time-push detection)

**UWB datasets (3 new + licences)**
- MILUV dataset record: Figshare+, CC BY 4.0 data; devkit MIT.
- RCV UWB relative-pose dataset: no licence file.
- TIERS UWB drone dataset: no licence file.
- UTIL was already indexed (`res:util-uwb-dataset`). Its record already states that no licence file exists.

**VPR training / aerial VPR (10 resources + 6 repos)**
- Resources:
  - GSV-Cities: Kaggle data is CC BY-NC-ND 4.0; the code repo has no licence.
  - CosPlace + SF-XL: SF-XL access is via a form marked "publicly available for research purposes"; there is no formal licence. Code is MIT.
  - EigenPlaces
  - MixVPR
  - Deep VG Benchmark
  - VPAIR: academic use only; the Zenodo sample is CC BY 4.0.
  - ALTO: repo is BSD-3-Clause; no separate data licence is stated.
  - Moskalenko et al. aerial VPR survey
  - LASED 2025 (multi-year Estonia aerial set)
  - Zaffar et al. 2019
- New repos:
  - `amaralibey/gsv-cities`
  - `amaralibey/openvprlab`
  - `prime-slam/aero-vloc`
  - `gmberton/deep-visual-geo-localization-benchmark`
  - `pesslovany/matlab-lagrangianpmf`
  - `idm-uwb/efficient-pmf`
  - `tiers/uwb-drone-dataset`
  - `cjhhalla/rcv_uwb_dataset`
- Glue Factory was already indexed (`repo:cvg/glue-factory`, Apache-2.0). It has no paper of its own, so no resource was added.

## Not found or left out

- **Stanford diagram origin paper.** No primary publication that introduces the "Stanford plot" was found. Stanford's own metrics page and later papers credit the Stanford WAAS lab, and that page is indexed instead. A likely candidate is Walter, Hansen & Enge 1999, "Validation of the WAAS MOPS Integrity Equation", but it was not located or verified.
- **Gnadt open preprints beyond the two added.** "Machine learning-enhanced magnetic calibration for airborne magnetic anomaly navigation" was not found on arXiv. Nothing was added without a verified copy.
- **Canciani open versions of the TAES papers.** No AFIT Scholar copy of the 2017 or 2022 TAES papers was found. Those records point to the DOI and are marked paywalled. The AFIT dissertation was already indexed.
- **Lee 1986 (range/position comparison RAIM).** Not added. I did not search for or verify it in this pass.
- **Kozhaya et al. TAES letter.** It does not exist as described in the flag. The TAES 2024 OFDM letter is by Neinavaie & Kassas.
- **Psiaki "TRANSIT on steroids".** Already indexed. Psiaki's newer Starlink work is covered by the Qin et al. 2026 pilots paper.
- **Recent open radar-altimeter TRN flight-test papers (2023-2026).** None found. The radar-altimeter entries are 2019 (with real flight data) and 2021 (simulation).
- Golden 1980 (TERCOM) is indexed only as the terrain-correlation navigation reference. Its title says "cruise missile guidance aid", but the record carries no guidance or targeting content.
- Safi's IPIN 2025 paper: the publisher record (OpenAlex) lists the first author as "Muhammad Irtaza Safi", while the university repositories list "Muhammad Safi". The record uses "Muhammad Safi".

## Side effect

I ran `tools/build.py` once to validate the lane files. That regenerated the derived catalog, index and README files in the shared checkout. Those files are generated output that the coordinator rebuilds anyway. No source data outside the two backlog lane files was edited.
