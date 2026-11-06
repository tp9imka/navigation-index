# Fact check - round 5 (2026-11-06)

Rounds 1-4 deep-checked the `hackathon_fit: high` repos, the gap-fill, ua-ru, landscape and round-3 lanes, and a sample of the rest ([round 1](fact-check-2026-11-06.md), [round 3](fact-check-round3.md), [round 4](fact-check-round4.md)). This round covers what was left in the nine established lanes:

- **Repos:** every `hackathon_fit: medium` or `low` record in `autopilots`, `gnss`, `ins-fusion`, `slam`, `alt-nav`, `planning-gis-c2`, `sim-data`, `domains-swarm` and `defense-context`. That is 389 records. 25 of them were already deep-checked in the round-1 sample, so **364** were checked here.
- **Resources:** every record in those nine lanes plus `docs-standards` and `learning` that round 1 did not check (round 1 checked 74 arXiv records automatically and 42 by hand). That is **313** records. None of them links to arXiv.

Every in-scope record got a deep check. No sampling.

Scripts and raw outputs are in the session scratchpad, under `fc5/`:
- `scope.py`, `mech.py`, `mechanical.txt`, `apply.py`, `mkpatch.py`, `brief-common.md`;
- `lanes/` (the record list for each lane), `readmes/` and `meta/` (README and live `gh api` metadata for 363 GitHub repos);
- `work/urlprobe/` (HTTP status, final URL and page title for all 313 resource URLs);
- `patches/*.json`, `applied.log` (323 field edits, each with a reason), and `logs/*.md` (one line per record, with evidence);
- `data-backup/`, a copy of `data/` taken before any edit.

## Method

1. **Mechanical pass, all 364 repos.** I compared maturity with live `archived` / `pushed_at` and language with the GitHub primary language, using the round-1 rules. I also flagged forks, renamed repos and repos with a README under 300 bytes or a size of 0. The pass raised:
   - 1 maturity flag (`microsoft/airsim`, kept as `archived` per the round-1 decision);
   - 6 language flags (5 are known linguist misreads; `kimera-distributed` had an empty language field);
   - 9 forks;
   - 14 thin or missing READMEs.
2. **README deep check, all 364 repos, in 5 parallel lanes.** For each repo, `summary`, `why_it_matters` and `hackathon_notes` were compared with the full README. Where a claim was specific or the README was thin, the tree and source files were read. Install claims were checked against PyPI, crates.io, apt and rosdistro. Licences were checked against the LICENSE file. For datasets and weights, the actual terms were found on the hosting page.
3. **Resources, all 313, in 4 lanes.** One lane (`res-b`) I did myself, because the subagent limit was full at the start.
   - Every URL was probed; dead URLs were repointed to the canonical page or a Wayback copy.
   - Titles were checked against `og:title`, `citation_title` or `<h1>`.
   - Authors and years were checked against bylines, JSON-LD, Crossref, DataCite, Zenodo or the PDF text (via PDFKit).
   - Dataset terms were checked on the hosting page.
   - Pages behind 403s or bot walls were checked by web search where possible and were never deleted.
4. **Coordinator spot-checks.** Before applying, I re-verified one or more findings from each lane:
   - the PX4 commit "feat(simulation)!: remove jMAVSim" (2026-09-26);
   - `msckf_vio`'s Penn non-profit-research licence;
   - the Kimera-Distributed README ("distributed front-end module");
   - ITU-R M.1371-6 (02/2026);
   - the hilti-challenge.com CC BY-NC-SA 3.0 statement;
   - the kalmanfilter.net page title;
   - the new EuRoC URL (200).

   All held.
5. **Validation.** Before writing, every patch was checked: in scope, the field exists, the type is unchanged, no field is patched twice, and no em/en dashes or arrows. All data files pass `json.tool` and keep their original indentation.

## Results

### Repos (364 checked, 118 with at least one issue, 151 field edits)

| Lane | Checked | With issue | Rate |
|---|---|---|---|
| domains-swarm | 66 | 28 | **42%** |
| alt-nav + planning-gis-c2 | 69 | 22 | 32% |
| sim-data + gnss | 79 | 26 | 33% |
| slam + defense-context | 77 | 23 | 30% |
| ins-fusion + autopilots | 73 | 19 | 26% |
| **All** | **364** | **118** | **32.4%** |

Each count is the number of records with at least one issue of that category:

| Category | Records | Share of checked |
|---|---|---|
| Licence: restriction missing or wrong | 46 | 12.6% |
| Error: wrong when written | 44 | 12.1% |
| Outdated (upstream changed) | 18 | 4.9% |
| Install / packaging | 12 | 3.3% |
| Empty or placeholder repo not disclosed | 8 | 2.2% |
| Language | 5 | 1.4% |
| Maturity | 5 | 1.4% |
| Vague only | 5 | 1.4% |

115 of the 364 records (31.6%) had a substantive issue, meaning anything other than vague only. That is about three times round 3's rate for the high-fit records of the same lanes (9.0%). Medium- and low-fit records were written with less care, and licence terms were never checked for them.

### Resources (313 checked, 112 with at least one issue, 174 field edits)

| Lane | Checked | With issue | Rate |
|---|---|---|---|
| sim-data + gnss + autopilots | 75 | 51 | **68%** |
| defense-context + alt-nav + ins-fusion + slam + domains-swarm | 83 | 30 | 36% |
| learning | 77 | 20 | 26% |
| docs-standards + planning-gis-c2 | 78 | 9 | 12% (see note) |
| **All** | **313** | **112** | **35.8%** |

| Category | Records | Share of checked |
|---|---|---|
| Citation: title, authors, year or URL | 85 | 27.2% |
| Licence: dataset terms missing | 22 | 7.0% |
| Outdated | 14 | 4.5% |
| Error | 13 | 4.2% |
| Number | 2 | 0.6% |

The sim-data lane rate is driven by dataset licences: 20 of its 51 records were missing non-commercial terms. Citation errors elsewhere are mostly paraphrased titles and org-only author fields on bylined articles.

Note on the docs-standards lane: I checked it by hand, and its low rate is partly method. I did not re-check every document title against its PDF the way the agent lanes did; titles that matched the page probe were accepted. Treat 12% as a floor.

No fabricated record turned up. Every repo and every resource exists.

## Corrections

The full list, with a reason for each edit, is in `fc5/applied.log` (323 edits). Per-record evidence is in `fc5/logs/*.md`.

**Repos: wrong when written (selected)**
- `dronemagnav`: the record said "open hardware", but the LICENSE is proprietary with all rights reserved, and the board has never been built.
- `ayushmankumar7/tercom-python`: one SIFT scene-matching script, with no TERCOM code.
- `ardupilot/uavlogviewer`: no PX4 ULog parser; it reads only `.tlog`, `.bin` and DJI logs.
- `ardupilot_gazebo`: ships no rover or boat models.
- `shelfcol/gps_imu_fusion`: the UKF is a TODO; the `ukf` tag was removed.
- `px4/px4-opticalflow`: a C++ library with no MAVLink output.
- `kimera-distributed`: it is the distributed front end, not the back end.
- `fast-planner`: the perception-aware planner was never released.
- `taroz/gsdc2023`: 2nd on the private leaderboard and 1st only on the public one, so not the winner.
- `multi-sdr-gps-sim`: no bladeRF support.
- `pride ppp-ar`: not Linux-only; it also runs on macOS and has a Windows GUI.
- `aerostack2`: only the Gazebo and multirotor-simulator platforms are in-tree; Pixhawk, Crazyflie and DJI are separate repos.
- `jaffarrell/av-matlab-sw`: also ships Python tools, so "MATLAB required" is wrong.
- `methodicconfigurator`: Copter only; Plane, Heli and Rover support is "very incomplete".
- Undisclosed forks: `halajun/smarc_navigation`, `leggedrobotics/elevation_mapping`, `flightaware/dump1090` (a fork of dump1090-mutability).

**Repos: licence terms now stated**
- Bans or limits military use:
  - `vggt` bans military use;
  - `gbplanner`'s README says civilian use only (the LICENSE itself is BSD-3);
  - `wfb-ng` is GPL-3.0, but its author's paid support excludes military use.
- Non-commercial or research-only:
  - code: `msckf_vio` and `kr_autonomous_flight` (Penn non-profit research licence), `mars_lib` (BSD-2 with a no-sale clause);
  - CC BY-NC-SA: `mast3r-slam`, `rellis-3d`, the SPEED+ data, Hilti 2022/2023, MCD, NTU VIRAL, GVINS, M2DGR, RobotCar, UZH-FPV;
  - CC BY-NC: `awsim` assets, TLIO data (and `eqnio`, which uses it);
  - research-only or custom terms: RoNIN, University-1652, SUES-200, VPAIR;
  - MagNav (US Air Force data agreement).
- No licence file, where the record implied free use: 7 repos in domains-swarm, plus `eqnio`, `sample4geo` and `mixvpr` (both link released weights) and the NeBula dataset.

**Repos: empty or near-empty, now disclosed**
- `pengyu-team/co-lrio`: README-only; it redirects to `zhongshp/Co-LRIO`.
- `yfs90`: no code.
- `cfear`: README and LICENSE only.
- `alto`: README-only placeholder.
- `aeolus-ocean`: a Windows binary release with no source.
- `wayfast` and `eth-pbl/swarm-relative-localization` contain much less than claimed.

**Repos: outdated or install**
- `px4/jmavsim`: removed from PX4 main on 2026-09-26. `make px4_sitl jmavsim` works only up to v1.17, and SIH replaces it.
- `commaai/openpilot`: the localizer no longer uses GNSS, and laika is gone.
- `betaflight`: release 2026.6 has position hold, altitude hold and waypoints, so "GPS Rescue only" no longer holds.
- `autoware_universe`: NDT and EKF localization moved to `autoware_core`.
- `gbplanner`: main is now OmniPlanner.
- Fields2Cover now has apt binaries. Planetiler needs `--download` and Java 25+. GraphHopper no longer officially supports offline Android routing.
- `ntripbrowser`: PyPI serves 2.2.3 (2021), while the repo is at 4.0.0.
- `dronekit`: the 2.9.2 PyPI build breaks on Python 3.10+.
- `rpg_trajectory_evaluation`: Python 2 only.
- `dump1090-fa`: not in Debian.
- `holoocean-ros`: needs a GitHub account linked to Epic Games.
- `benchnav`: not on PyPI.
- Maturity => archived: `dvl-python`, `ros2swarm`, `vision_landing` (README says discontinued), `liegroups` (superseded by PyMLG).

**Resources (selected)**
- Dead or moved URLs:
  - EuRoC => `projects.asl.ethz.ch/datasets/euroc-mav/`;
  - Kriezis ION ITM 2025 => the `Kreizis_...` filename (200);
  - the Linux Foundation EAR page => new path;
  - UTIL => learnsyslab;
  - DASA => GOV.UK;
  - Udacity CS373 and the ION SatNav tutorial => Wayback (the tutorial is now mostly paid, so access is `paywalled`);
  - the GPS.gov Burke deck and the ONR HACKtheMACHINE page => Wayback;
  - Militarnyi Vermeer => canonical article.
- Wrong source: `res:icao-gnss-rfi-workshop-presentation`. The PDF at the URL is a 2026 ICAO WRC-27 workshop deck by Mathieu Hussong (DGAC), not a 2024 FSMP presentation. Title, author, year and summary were fixed.
- Years:
  - Brave1 / NATO competition => 2026;
  - Inside GNSS ADS-B => 2026;
  - Inside GNSS ROCkN => 2026;
  - u-blox jamming blog => 2019;
  - Crows' Nest podcast => 2026;
  - GTSAM tutorial => 2019;
  - ITU-R M.1371 => revision 6 (02/2026).
- Placeholder or org-only authors replaced with real names:
  - news bylines: Defense News x2, Windward, DefenseScoop x2, Kyiv Independent, The Record, Kyiv Post, Militarnyi x3, IEEE Spectrum, EFF;
  - papers: Lu et al., the Frontiers LEO survey, Kriezis et al., NDSS DroneID, Stone Soup, MCD, EuRoC (Burri et al.), the Google raw GNSS dataset paper;
  - other documents: the MITRE CoT router guide (Kristan et al.), Niessen (MITRE), slambook (4 authors).
- Numbers: Windward's "hundreds of ships per day" is not in the source, which gives 24,000 vessels in Q1-Q3 2025. The Starlink carrier-phase paper reports 7.7 m horizontal error with known altitude.
- Content: TartanAir v1 has no IMU. GTSAM tutorial code is C++/MATLAB, not Python. The SLAM Handbook is "to be published" by CUP. The Riseborough deck summary was rewritten.
- Dataset terms now stated:
  - CC BY-NC-SA: KITTI-360, UZH-FPV, Newer College, Mid-Air, Radar RobotCar, MulRan, HeLiPR, Complex Urban, UrbanLoco, MCD, Hilti (two records), MARS-LVIG;
  - EuRoC: InC-NC (non-commercial use permitted);
  - MagNav: Air Force agreement;
  - TEXBAT: research use, no redistribution;
  - SubT-MRS and DARPA SubT: no terms stated anywhere;
  - UTIL repo: no licence.

## Could not verify

- **Dataset terms:**
  - TartanDrive (the theairlab.org page returns 404);
  - Boreas, Mapillary SLS and Blackbird (JavaScript-only sites; nothing definitive found);
  - Kaggle GSDC 2022 (login wall);
  - the denoise-imu-gyro weights;
  - the MagNav terms as they apply to `naatyu/magnav`.
- **Pages behind a 403 or bot wall:** 23 resources, left unchanged and logged as `note-403`. Among them: Septentrio x3, NovAtel GAJT-710ML, MIL-STD-2525D (jcs.mil), the DOT CPNT action plan, Artech (Groves), OSU Kassas PDFs x3, RIN, NATO DIANA x2, grantbite (EDF), AFRL, army.mil, EUR-Lex x2, eCFR, Flightradar24 and MathWorks. Where Crossref or web search could confirm a title or year, it is noted in the log.
- **EASA's SIB tool** (ad.easa.europa.eu) shows a maintenance page. R4's 3 July 2026 date was confirmed via EASA news, R3's via search only.
- **`res:butler-cot-developer-guide`:** DTIC shows a maintenance page, so it was not re-checked.
- **`res:nato-diana-secure-comms-navigation`:** a search snippet suggests the page is dated June 2026, not 2025. Not patched.
- Single claims: ping-viewer "logs replayed into ping-python", RIO "TI mmWave-class sensors", and Mid-Air "built on AirSim".
- Nothing was built or run, so claims like "invariant-ekf still compiles" are unchecked.

## Left for an editorial decision (not changed)

- **Judgment fields untouched.** Several records are now known to be empty or restricted but keep `hackathon_fit: medium`: `yfs90`, `co-lrio`, `cfear`, `alto`, `aeolus-ocean`, and `vggt` (bans military use). Downgrade or prune them on purpose.
- **`co-lrio`:** should `url` point to `zhongshp/Co-LRIO`, where the code lives?
- **`dave`:** still `active-research`, last pushed 2024-08. That is inside the rule threshold, and the ROS 2 port lives in the IOES-Lab fork.
- **No LICENSE file, record silent:** code repos such as Go-RIO, far_planner, Kimera-Multi and SC-LIO-SAM have no LICENSE file, and their records don't mention a licence. They are logged only. All rights reserved applies by default.
- **Duplicates:**
  - DARPA ANS has year 2010 in `docs-standards` and 2014 in another lane.
  - The Defense News Baltic, Militarnyi Vermeer and Hilti twins were fixed in both places. They still carry different text.
  - The duplicate-URL lint suggested in round 1 is still not built.

## Residual risk

- **Generated files are stale.** `catalog/`, `INDEX.md`, `graph/` and `index/` were not rebuilt. Run `python3 tools/enrich.py && python3 tools/build.py` before relying on catalog pages.
- **Medium/low-fit records were the least reliable part of the index.** 32% had an issue, against 9% for high-fit in round 3. With this round, every repo record in the nine lanes has now had a README read.
- **Licence is still the biggest exposure.** The 46 repo and 22 resource licence fixes cover what was found, but 7 datasets remain unverified (listed above). Code repos without a LICENSE file were noted, not patched, unless the record implied free use.
- **Install and "outdated" claims keep drifting.** jMAVSim was removed six weeks ago, and Betaflight gained waypoints this year. Expect new drift within months, mostly in `hackathon_notes`.
- **The hand-checked docs-standards lane got a lighter title pass** than the agent lanes (see the note under Results). A second title-vs-PDF pass over its standards records would close that gap.
- **Agent findings were spot-checked, not re-done.** About 7 of 323 edits were independently re-verified, and all held. The rest rely on the lane logs' evidence, which is recorded per edit.
