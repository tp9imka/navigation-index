# Fact check - round 4 (2026-11-06)

Round 3 ([fact-check-round3](fact-check-round3.md)) left `round3-expansion.json` unchecked. This round covers:

- `data/repos/round3-expansion.json` (49) and `data/resources/round3-expansion.json` (46). Every record got a deep check.
- The 12 round-3 integration cards (listed in `docs/integration-cards/_index-round3.md`).
- A seeded random sample (seed 20261106) of 15 of the other 71 integration cards.
- A seeded random sample of 10 of the 45 paper digests.

Scripts and raw outputs are in the session scratchpad, under `fc4/`:
- `mech.py`, `apply.py`, `brief-common.md`;
- `readmes/`, `meta/` (README and metadata for all 49 repos);
- `patches/*.json`, `applied.log` (154 JSON field edits, each with a reason);
- `logs/` (one line per record or claim, with evidence);
- `pdf/`;
- `data-backup/` and `docs-backup/`, copies taken before any edit.

## Method

1. **Mechanical, all 49 repos.** Maturity was compared with `archived` / `pushed_at` and language with the GitHub primary language, using the round-1 rules. One flag was raised: `wosdetc/challenge` was active-research with a last push in 2022-12. No round-3 repo is archived upstream. `sobu-labs/gnss-multiple-jammers-dataset` is an empty repo.
2. **README deep check, all 49 repos.** Every README was read in full via `gh api .../readme`. Where the README was thin or a claim was specific, the repo tree and source files were checked too.
3. **Licence pass, every dataset.** Each dataset's actual licence or terms were found in its LICENSE file, README or hosting page (IEEE DataPort, Zenodo, Kaggle, Hugging Face, Caltech Data). Non-commercial, research-only, no-defence-use and no-licence terms are now stated in `hackathon_notes` (repos) or in `summary` / `key_takeaways` (resources).
4. **Resources, all 46.** Title, authors, year and URL were checked against arXiv `citation_*` tags or the export API, DataCite / Crossref, and page `og:title`, byline and date. PDFs were text-extracted. Every number in `summary` and `key_takeaways` was checked against its source.
5. **Cards.** For every card, install commands were checked against PyPI, npm, apt, rosdistro and GitHub releases. Entry-point names and signatures were checked in the source file via `gh api .../contents`. Licences were checked against the LICENSE file. For each gotcha, the cited issue was checked (exists, says that, open/closed state right), or the code was read. Nothing was installed or run.
6. **Digests.** Title, authors, venue and URL were checked, and each headline number was compared with the paper's PDF or HTML, by section, table or figure.
7. **Coordinator spot-checks.** I re-verified one or more findings from each lane myself before applying:
   - the DroneAudioDataset no-defence clause (README line 11);
   - the sentinel1-rfi "L-band to C-band question remains open" line;
   - the CodyMQ fork of archived IQTLabs;
   - the Zenodo 4629685 MATLAB generator;
   - PoLaRIS at Inha University;
   - VGGT `LICENSE.txt` banning military use (vendored in ScalLoc);
   - the CopterHack Wayback URL (200);
   - the ETIO Table II row in the PDF text;
   - the gnss-ins-sim `results()` signature;
   - vision_to_mavros #64 being closed;
   - the GTSAM `python-install` target;
   - adsbcot returning 404 on PyPI;
   - rotorpy `dryden_utils.py` importing torch unconditionally.

   All held. I made two coordinator corrections. The Morgan et al. title had a venue suffix, which I dropped. The gnss-ins-sim signature was missing `extra_opt=''`, which I added.

## Results by category

### Repos (49 records, 45 edited, 102 field edits)

Each count is the number of records with at least one issue of that category.

| Category | Records | Rate |
|---|---|---|
| Licence: restriction missing or wrong | 32 | **65%** |
| Vague: rewritten from the README | 19 | 39% |
| Error: wrong when written | 8 | 16% |
| Maturity | 5 | 10% |
| Number | 3 | 6% |
| Install | 3 | 6% |
| Outdated | 3 | 6% |
| Language | 1 | 2% |
| Citation (venue year) | 1 | 2% |

40 of the 49 records (82%) had a substantive issue, meaning anything other than vague only. The rate is about four times round 3's gap-fill lane (18.9%). Licence omissions drive it: the round-3 lane was written from descriptions and never opened a LICENSE file or a dataset page.

### Resources (46 records, 36 edited, 81 field edits)

| Category | Records | Rate |
|---|---|---|
| Citation: placeholder or wrong authors, title, year or URL | 28 | **61%** |
| Vague | 19 | 41% |
| Licence | 14 | 30% |
| Error | 12 | 26% |
| Outdated | 1 | 2% |

Most citation errors were surname-only placeholder authors (for example "Kim (KAIST)"). There were 3 wrong years and 2 wrong titles.

### Cards and digests

| Check | Checked | Wrong | Rate |
|---|---|---|---|
| Round-3 cards | 12 cards, about 215 claims | 8 claims in 7 cards (install 4, error 4, vague 1; one counted twice) | about 3.7% per claim |
| Sampled older cards | 15 cards (claims not totalled) | 13 claims in 9 cards (install 5, error 8). Licence 0, issue states 1 wrong | 9/15 cards edited |
| Digests: citations | 10 | 0 | 0% |
| Digests: headline numbers | about 300 | 0 misquotes. 3 wrong hedges or notes about the paper | 0% misquoted |

## Corrections

The full list, with reasons, is in `fc4/applied.log` (JSON) and `fc4/logs/cards-*.md`, `fc4/logs/digests.md` (markdown, old => new).

**Defence-relevant licence terms now flagged**
- No military or defence use:
  - `saraalemadi/droneaudiodataset`: the README bans military, defence, intelligence, surveillance and targeting use. Not usable for a defence entry.
  - `floralhercules/scalloc`: vendors VGGT, whose licence bans military and warfare use. The VGGT-1B checkpoint is non-commercial, and ScalLoc's own licence is "pending".
- Non-commercial or research-only:
  - `massmind` (CC BY-NC-SA);
  - `lars_evaluator` / `res:lars-maritime-obstacle-dataset-2023` (CC BY-NC, research only, no redistribution, registration);
  - Caltech RGB-T / CART (non-commercial);
  - `geoveil-cn0` (PolyForm Noncommercial);
  - Pohang Canal (CC BY-NC); PoLaRIS inherits it;
  - Fraunhofer highway interference (CC BY-NC-SA);
  - PiLoT data on HF (gated, non-commercial, no redistribution);
  - Drone-vs-Bird (data usage agreement by email);
  - University-1652 (request-only, research use). This is now stated on every record that trains on it, including the UAVM 2023/2024/2026 resources.
- No licence file, so all rights reserved: 12 repos, among them `tesorrells/rf-drone-detection`, `alicmu2024`, `fahadwebd`, `josephtule`, `chance1911`, `fsra`, `pairuav` (which also ships SuperGlue code marked all rights reserved), `dpn`, `weln`, `akpozi`, `swift-nav/google-sdc-corrections` and `swarm_in_blocks`. VAARA (Jammertest 2024) has none either.
- Confirmed permissive (CC BY 4.0 or CC0): Noisy Drone RF, DroneRF, DroneDetect, SubPipe, the Antarctica UBX set, Swinney-Woods jamming IQ, CUAS-sensing and Jammertest 2025 data (CC BY-SA 4.0).
- `pilot`: notes that the authors are at NUDT (on the US Entity List). This rests on general knowledge, not a fetched source.

**Repos: wrong when written**
- `zephr-xyz/sentinel1-rfi-detection`: claimed GNSS jamming mapping. Its own README says the C-band to L-band link is unproven.
- `sobu-labs/gnss-multiple-jammers-dataset` and `chance1911/mmc-uav-dataset`: both are empty placeholders with no data.
- `fabianr-su/stanford-gnss-spoof-detection`: a single script.
- `remaro-network/subpipe-dataset`: the ground truth is the AUV's own navigation estimate.
- `z0rlord/foxhunt`: "legal to test" was overstated. The code is receive-only, but a live test needs an authorised jammer.
- `dronedetectionthesis/drone-detection-dataset`: the audio has no bird or airplane classes.
- `wtyhub/musenet`: was called "the UAVM 2024 baseline"; nothing supports that.
- `dmmm1997/fsra`: TCSVT 2022, not 2021.

**Repos: maturity and language**
- Now archived: `wosdetc/challenge`, `codymq/rfclassification` (fork of an archived repo; language set to Jupyter Notebook), `layumi/uavm2023` and `wtyhub/uavm2024` (static challenge pages).
- `lars_evaluator`: now research-prototype.

**Resources**
- `res:polaris-pohang-maritime-dataset-2024`: from Inha University, not KAIST. Tag and `related` rel fixed.
- `res:gnss-raw-iq-jamming-classification-zenodo`: the signals are simulated in MATLAB, not captured.
- `res:subpipe-paper-2024`: the sonar data has detection labels, not segmentation labels.
- Years: FGI Jammertest 2023 repository 2024 => 2025; WSU acoustic 2025 => 2026; SPRIN-D heightmap 2025 => 2024.
- `res:humphreys-fused-leo-gnss-mock-2025`: the title is "A Mock Implementation of Fused LEO GNSS", and the paper uses live Starlink signals. The authors are Morgan et al.
- `res:copterhack-2022`: the linked results page is empty, so the URL now points to a Wayback copy showing Atena / Swarm in Blocks winning with 21.6 points.
- `res:ion-smartphone-decimeter-challenge`: "ION placings differ from Kaggle" was unsupported and was removed.
- `res:jammertest-2025-multi-source-interference`: rewritten from the abstract. The old multi-emitter takeaway is not in the paper.
- Unsupported details removed: "Warsaw", "5th EUDIS", "in-car jammer", and SPRIN-D's "gradients beat raw height".
- All placeholder author lists were replaced with the real names.

**Round-3 cards**
- `snstac__adsbcot`: not on PyPI (404). The install now uses `git+https` or the release `.deb`/`.rpm`. The upstream `docs/installation.md` is still wrong.
- `spencerfolk__rotorpy`: the `Environment(...)` argument order is fixed. A new gotcha: `DrydenGust` imports torch, so the card's example likely fails after a plain `pip install rotorpy` (read from source, not run).
- `locusrobotics__fuse`: binaries also exist for Lyrical and Rolling.
- `smroid__cedar-solve`: the `CedarDetectClient` signature was missing `logger=None`.
- `alphafox02__dragonsync`: the copyright line is now quoted exactly.
- `haiyang-wong__osnma-sdr-sim`: the `<sys/shm.h>` include is in `galileo-sdr.h`, not `main.cpp`.
- `i2nav-whu__ob_gins`: the Eigen 3.3.7-3.3.9 range is now stated.

**Sampled older cards**
- `aceinna__gnss-ins-sim`:
  - the `results()` signature was wrong;
  - KML is written only with `gen_kml=True`;
  - the DMU380 demo is Windows-only;
  - the VG demo is absent;
  - `demo_ins_loose` passes a bad argument.
- `borglab__gtsam`: the build target is now `cmake --build build --target python-install`.
- `cvg__lightglue`: it has GitHub releases (`v0.1_arxiv`, `v0.2`) but is not on PyPI.
- `mit-ai-accelerator__magnav.jl`: the NN trainers are not exported; use `comp_train`.
- `algafix__osnma`: only public key 2 ships.
- `ros-navigation__navigation2`: the loopback sim is on jazzy and main, not humble.
- `rpng__mins`: `mins_bag` is built under ROS 2 too.
- `thien94__vision_to_mavros`: #64 is closed.
- `tiers__wildnav`: has one release.

**Digests**
- `etio-thermal-inertial-odometry-2022`: the "ambiguous Table II" caveat is removed. The PDF has 7 values for 7 columns, so 0.648 / 0.409 are the ADT-KLT values.
- `leo-doppler-cold-start-2025`: the "text/table mismatch" note was wrong. The note now quotes Sec. 5.5.
- `thermal-geolocalization-iros-2023`: the split numbers are confirmed and the hedge is removed.
- `afrl-magnav-challenge-2020`: Fig. 2 is now labelled as Flight 1002.

## Could not verify

- The text of the Drone-vs-Bird data agreement (not public), and whether that challenge ran after 2023.
- TEXBAT usage terms (none published).
- The Kaggle GSDC data licence.
- The terms of University-160k itself.
- The contents of the Kalit31 Google Drive folder.
- The WSU acoustic dataset's CC BY-SA 4.0: seen only in a search snippet, the page returned 403.
- The UaVirBASE dataset licence: MDPI returned 403.
- The CardRF controller-count claim.
- The URL `osuva.uwasa.fi` for the Jammertest 2024 vehicular paper (bot wall); its authors were taken from Crossref.
- The ICRA 2025 aerial-robotics workshop organizers: the workshop site is gone, so the placeholder author is kept.
- The `cvpr2026` tag on PiLoT and the `icra2026` tag on SPRIN-D, which appear only in the README bibtex.
- The ETIO RA-L 2023 venue: secondary listing only.
- Repo facts in the digests' "Code, weights, license" sections (not in scope).
- The Nav2 arm64 binaries (the card already says unchecked).

## Residual risk

- **Generated files are stale.** `catalog/`, `INDEX.md`, `graph/` and `index/` were not rebuilt, because they were out of scope. Run `python3 tools/enrich.py && python3 tools/build.py` before relying on catalog pages.
- **The licence gap is likely systemic.** The round-3 lane got 65% of repo records wrong on licence. Rounds 1-3 did not run a dedicated dataset-licence pass on the other lanes, so expect similar omissions in `sim-data`, `slam` and `alt-nav` dataset records. A licence-only sweep over every dataset record in the index is the highest-value next check.
- **Judgment fields were not changed.** Two repos are now known to be empty (`sobu-labs`, `chance1911`) but are still `hackathon_fit: medium`. One with a no-defence licence (`droneaudiodataset`) is `low`. These should be pruned or downgraded on purpose rather than by the checker.
- **Card error rates.** The sample error rate for older cards (9 of 15 edited) suggests about 34 of the 56 unsampled older cards carry at least one wrong install, signature or gotcha claim. Most are minor, but install claims age fastest: adsbcot dropped off PyPI while its own docs still say `pip install`.
- **Digests look sound.** 0 misquotes in about 300 numbers, so the digest corpus is the lowest-risk part of the index.
- **Upstream docs disagree with reality** (adsbcot docs, the gnss-ins-sim demos). Cards now follow the source, not the docs, and could diverge again when upstream fixes its docs.
