# Fact check - round 3 (2026-11-06)

This round covers what the first check ([fact-check-2026-11-06](fact-check-2026-11-06.md)) skipped:

- `data/repos/gap-fill.json` (106) and `data/repos/ua-ru-sources.json` (12);
- every `hackathon_fit: high` repo in the other lanes that the first check did not deep-check (155);
- `data/resources/gap-fill.json` (19), `data/resources/ua-ru-sources.json` (38) and `data/resources/landscape.json` (35).

That is 273 repo records and 92 resource records. Every one of them got a deep read, not a sample. `round3-expansion.json` was not touched.

Scripts and raw outputs are in the session scratchpad, under `fc3/`:
- `scope.py`, `digest.py`, `apply.py`, `mine.py`;
- `patches/b0-b4.json`, `applied.log`;
- `readmes/`, `web/`, `pdf/`;
- `data-backup/`, a copy of `data/` taken before any edit.

## Method

1. **Mechanical, all 273 repos.** I compared maturity with `archived` / `pushed_at` and language with the GitHub primary language. I used the same rules as the first check, and confirmed language flags with per-language byte counts.
2. **README deep check, all 273 repos.** I fetched every README with `gh api repos/<o>/<n>/readme`. I compared `summary`, `why_it_matters` and `hackathon_notes` with it. Where a claim was specific and the README was silent, I checked the repo tree, PyPI or conda-forge. Generic summaries were rewritten from the README. The work ran in five parallel batches. I spot-checked the batch findings myself before applying them: the PyPI 404s for `lightglue`, `v2e`, `pyins`, `manifpy` and `magnavpy`, `python-ins` 1.0.1, `mavsdk` 4.1.0, `pyModeS` 3.6.1, and the trees of `romavis/LoranC` and `MPU6050_ZUPT`.
3. **Resources.**
   - **arXiv (14 gap-fill papers):** title, year and authors checked against the `citation_*` meta tags on arxiv.org/abs.
   - **Web pages (all others):** title checked against the page's `og:title` / `citation_title` / `<h1>`, year against the publish date, and authors against the byline or JSON-LD.
   - **PDFs (7):** text extracted with PDFKit.
   - **Pages blocked by 403 or Cloudflare:** checked by web search where possible.
4. **Landscape.** Every number in the summary and takeaways was searched for in the linked source. A number missing from the source was traced to a public source and attributed in the text, or removed if no source exists.

## Results by category

| Check | Checked | Records wrong | Rate |
|---|---|---|---|
| Maturity vs metadata | 273 | 1 flagged, 1 real (`geoscan_pioneer_max` archived upstream). The README pass found 3 more (`aureliencousin/pdr`, `ms8r/celnav`, both unmaintained; `kirienko/pylgrim` was already archived) | - |
| Language vs GitHub | 273 | 6 flagged, 1 real (`pajaraca/iez`: MATLAB => Python). The README pass found 2 more (`romavis/loranc` IDL => KiCad, `christopherdoer/reve` Fortran => C++) | - |
| README deep check, gap-fill repos | 106 | 13 error, 7 outdated only, 6 vague only | **18.9%** wrong or outdated |
| README deep check, ua-ru repos | 12 | 2 error | 16.7% |
| README deep check, other high-fit repos | 155 | 9 error, 5 outdated only, 2 vague only | **9.0%** wrong or outdated |
| arXiv resources (gap-fill) | 14 | 0 wrong titles or years; 3 placeholder author fields | 0% substantive |
| Non-arXiv gap-fill resources | 5 | 1 paraphrased title (FAA eLoran), 1 dead URL (OpenShoe) | 2/5 |
| ua-ru resources: original-language title | 38 | 0 mismatches (37 matched the page; 1, Habr rope-ladder, is behind a 403) | 0% |
| ua-ru resources: year / author | 38 | 1 interviewee listed as the author (DOU DELTA), 1 missing byline | 1 substantive |
| Landscape: year | 35 | 2 (UAVOS 2025 => 2026, Spleenlab 2024 => 2022) | 5.7% |
| Landscape: numbers vs source | 35 | 2 unsupported claims removed, 8 records re-sourced or scoped | 10/35 needed edits |

Overall, 26 of 273 repo records (9.5%) had a factual error, and 12 more (4.4%) had only an outdated claim. The gap-fill lane is about twice as error-prone as the high-fit records of the established lanes. Its errors run in one direction: the record describes what the README promises, not what the repo contains.

I found no fabricated record. Every repo and every resource exists.

## Corrections

88 field edits. The full list, with reasons, is in `fc3/applied.log`.

**Repos: wrong when written**
- `romavis/loranc`: the repo holds KiCad hardware only, with no DSP code. Summary, notes and language fixed.
- `wuzhiguocarter/openpdr`: no PDR algorithms in the repo, only calibration scripts and papers.
- `mtahakoroglu/mpu6050_zupt`: an MPU6050 reader only. ZUPT and INS support are "planned".
- `kirienko/pylgrim`: positioning from RINEX files only, with no acquisition or tracking.
- `pajaraca/iez`: a Python script plus ESP32 firmware, not MATLAB.
- `pmonta/gnss-dsp-tools`: no NavIC support; the Numba dependency was missing from the notes.
- `lcas/ros2_mcp`: it does not call services or actions.
- `xuefanfu/3dg-vln`: "3D directional guidance", not "3D grounding".
- `colonelpanichacks/drone-mesh-mapper`: captures BLE as well as Wi-Fi.
- `peterjburke/rid`: built with PlatformIO, and it shows positions on the LCD.
- `mzahana/tercom_nav`: only PX4 SITL is documented, not ArduPilot.
- `felixott94/fraunhoferiis_jammertest2025`: it has no Python loaders.
- `aureliencousin/pdr`: an Eclipse ADT project, not an Android Studio one.
- `smroid/cedar-solve`: not "drop-in" for tetra3.
- `solarwarlock/flyingblind_hakaton`: 12 commits, not one; it also has a Streamlit UI and a Rust core.
- `christopherdoer/reve`: language Fortran => C++.
- `geoscan/geoscan_pioneer_max`: maturity => archived.

**Repos: install claims**
- Not on PyPI, so the notes now say to install from git: `cvg/lightglue`, `sensorsini/v2e`, `manasp21/magnav.py`. For `commaai/laika`, the PyPI entry is a 2018 stub.
- `nmayorov/pyins` is published on PyPI as `python-ins`.
- `artivis/manif`: `manifpy` is on conda-forge only.
- `nvidia-isaac/cuvslam`: the wheels come from GitHub releases, for a fixed CUDA/platform list.

**Repos: outdated (upstream changed)**
- `mavlink/mavsdk`: `pip install mavsdk` is now the v4 native binding.
- `junzis/pymodes`: v3 is a rewrite with a new API and needs Python 3.11+.
- `borglab/gtsfm`: installs with uv/pip, no longer with conda.
- `fabio-sim/lightglue-onnx`: now uv plus a CLI, and supports ALIKED.
- `wise-vision/ros2_mcp`: the quickstart is a Docker image.
- `luxonis/depthai`: the default branch is now only a pointer; the v3 API lives in depthai-core.
- `typefly/typefly`: plans are Python now, not MiniSpec. Go2 and Petoi wrappers added.
- `commaai/laika`: openpilot dropped laikad in October 2023.
- `ark-electronics/ros2_px4_offboard_example`: moved to a C++ successor.
- Maintenance status noted for `mit-ai-accelerator/magnav.jl` (concluded) and `neuromorphs/tonic` (looking for a maintainer).
- Maturity => archived for `ms8r/celnav` and `aureliencousin/pdr`.
- `georinex`: RINEX 4 support.

**Repos: vague summaries rewritten from the README**
- `internrobotics/internnav`;
- `ms8r/celnav`;
- `mzahana/tercom_nav`;
- `joansola/slamtb`;
- `robotmcp/demos-ros-mcp-server`;
- `yangsc4063/rino`;
- `nkarasiak/qgis-mcp`;
- `manasp21/magnav.py`;
- plus concrete notes for `prbonn/rko_lio`, `hviktortsoi/fast_lio_localization` (Python 2.7 + open3d 0.9 gotcha) and `rmeadomavic/ardupilot-mcp`.

**Resources**
- `res:faa-eloran-iat-2014`:
  - title set to the slide title, "The Global Loran / eLoran Infrastructure Evolution: A Robust and Resilient PNT Backup for GNSS";
  - author is Mitch Narins;
  - summary and takeaway made concrete (NPA / RNP 0.3, HEA 10-20 m, Stratum 1).
- `res:openshoe-foot-mounted-ins-2012`:
  - openshoe.org does not resolve, so the URL now points to the 2026-03-11 Wayback copy;
  - authors given as full names.
- Placeholder authors replaced with the arXiv authors: `res:jpl-rosa-paper-2024`, `res:openfly-aerial-vln-2025`, `res:cuvslam-2025`.
- `res:dou-delta-architecture-interview-2024`: the author is Eleonora Burdina; Martynenko is the interviewee.
- `res:dou-lapko-urban-nav-interview-2025`: byline added.

**Landscape**
- Removed as unsupported:
  - DAF-MIT MagNav "about 1 km accuracy": no public source; the official releases defer accuracy to a government technical report.
  - infiniDome "400% in Israeli-government trials": not in the linked article or any other source.
- Year: `res:uavos-navai` => 2026 (article dated 27 July 2026). `res:spleenlab-visionairy` => 2022 (the linked page is the April 2022 Auterion announcement). Spleenlab's "used by Blueflite" was dropped as unfound, and its module list is now marked as a vendor description.
- Re-sourced or scoped:
  - Q-CTRL: the linked page says 50x / 11x. RNP 0.3 and DO-160 come from Q-CTRL releases, and DO-160 is environmental qualification, not an approval.
  - SandboxAQ: RNP 2 100% / RNP 1 95% from the July 2025 Acubed campaign; the C-17 and Lumberjack items are attributed to later announcements.
  - Boreas: the mine figure is attributed to the BHP Callio case study.
  - Iridium: ASIC size from the October 2025 fact sheet.
  - ESA NAVISP: EUR 950k from the ALL.SPACE announcement.
  - Xona: FCC approval dated August 2026, initially for 16 satellites.
  - Theseus: the 30 minutes figure is a press-relayed company statement.

## Reviewed and kept

- Language flags kept:
  - `px4/px4_msgs`: record says CMake, GitHub says Shell. It is a message-definition package.
  - `gtsfm`, `lm_nav`, `gtsam`, `allan-variance`: GitHub reports Jupyter Notebook because of the notebooks; the code is Python or C++.
- `osqzss/gps-sdr-sim`: archived upstream and last pushed January 2025. The year in "archived in 2025" is unconfirmed but plausible.
- `isaac_ros_dnn_inference`: the "dev container required" note may be stale, but the README does not settle it.

## Could not verify

- `res:habr-rope-ladder-return-home-2025`: Habr returns 403. The article exists; the batch check found it at habr.com/en. The author field already says "not verified".
- `res:spirent-gss7000-pntx`, `res:safran-skydel-gsg8`, `res:iridium-pnt-stl-asic` (linked page), `res:twist-robotics-oscar` (pravda.com.ua): all blocked by 403 or Cloudflare. For OSCAR, the 500,000 km claim is confirmed in the Militarnyi twin. The Spirent and Skydel product claims are unchecked.
- `res:diu-tqs-program`: "Honeywell flew a quantum MagNav test on an Embraer 170 under TQS" is labelled press but has no source. The same goes for the Honeywell VAN "GPS-like on E170 / AW139" claim. Both are left as press claims.
- `repo:gitlab.com/gpsd/gpsd`: no GitHub metadata or README fetch, so it got no mechanical check.

## Duplicates

- The `mit-ai-accelerator/magnav.jl` and `manasp21/magnav.py` twins in `defense-context` and `sim-data` carry different notes text. None of them repeats the corrected claims, but they lack the maintenance and PyPI caveats added in `alt-nav`.
- The OSCAR product appears in both `landscape` and `ua-ru-sources`.
- The duplicate-URL lint suggested in the first report is still worth adding.

## Residual risk

- Every in-scope record got a full README or source read, but each read covered the first 3,500 characters of the README plus targeted lookups. Claims about deep features (a specific CLI flag, a dataset split) may still be off.
- `why_it_matters` and `hackathon_fit` are judgments and were not scored. Several gap-fill repos now read as near-empty (`openpdr`, `loranc`, `mpu6050_zupt`). Their fit is already low or medium, but the lane would benefit from a pruning pass.
- Install and packaging notes age fastest: 13 of the 38 wrong or outdated records were install or packaging claims. Expect new drift within months.
- Landscape records are vendor-driven. Numbers now carry attribution, but none is independently verified.
