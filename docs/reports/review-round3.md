# Review, round 3

Third fresh-eyes pass, 2026-11-06. Role: a hackathon team member opening the hub cold on day 0
with an unknown problem statement. Read-only except for this file. Previous pass:
[review-round2.md](review-round2.md).

**Snapshot.** The tree moved while this review ran: HEAD went from `f719109` to `1967cf0`
(autopilot-resilient-configs committed), `samples/README.md` stayed modified in the working tree,
and an untracked `samples/timing-network-holdover/` appeared near the end. Sample runs and the CI
test loop used a clean `git archive` of `1967cf0` in a scratch folder. Nothing was installed;
no venv was created. Findings about in-flight work are labelled "in flight".

Priorities: **P1** = blocks or derails a team. **P2** = misleads (wrong number, wrong page, broken
documented command). **P3** = polish.

## Prioritized findings

| # | P | File:line | Finding | Evidence |
|---|---|---|---|---|
| 1 | P1 | `tools/query.py:405-444` (`decode`), `docs/problem-statement-decoder.md:38,45,46,53` | `decode` misses the right row for some plain statements and never says it is unsure. There is no score floor: any trigger or shared word returns 1-3 rows with the same confidence formatting. README hop 1 and AGENTS.md step 1 make decode the first move and say not to paste into search, so a miss sends a team the wrong way. | "Give an infantry squad on foot a way to know where each member is inside a multi-storey building with no GPS..." => rows 10, 6 (timing), 20 at scores 1.0-1.3. Row 9 (soldier indoors) ranks 4th (0.878) and is cut. A pasted `search --kind sample` of the same text puts `dismounted-foot-ins` first, so the advice "never paste" is worse than pasting here. "Bake a chocolate cake for the team" => rows 10 and 11 ("team" trigger). "Railway convoy positioning in a long tunnel network" => rows 26, 25, 23; row 9 ("tunnel" matched) is 5th, row 14 7th. No cues exist for "infantry", "squad", "on foot", "building", "inside", "rail", "train", "vehicle", "rover". Add the cues, add a floor (for example best score < 3 or no matched wording => print "low confidence: also run search with your own keywords"), and add a decode eval set (statement => expected rows) to CI next to `search_eval.py`. |
| 2 | P1 | `tools/query.py:42` (`STOP` contains "how"), `docs/problem-statement-decoder.md:53` | The wording trigger "how long" is tokenised to just "long", so row 26 (holdover calculator) fires on any "long": "long tunnel", "long range", "long flights". Same class: "hours" (line 38) sends every multi-hour statement to row 27 (fixed-wing). | `tokens("how long") == ['long']`. Railway statement: row 26 first with `wording: how long` although the text has no "how". Timing statement "...jammed or spoofed for up to 24 hours" => row 27 "Fixed-wing long-range flight" as the second pick with `wording: hours`. Keep stop words inside quoted triggers, and drop or qualify "hours". |
| 3 | P2 | `samples/README.md:116`, `samples/multi-source-fde/` (no `requirements.txt`), install-deviation table `samples/README.md:55-71` | `multi-source-fde` first command `.venv/bin/python run_fde.py --data ../relative-nav-benchmark/data/vpair` needs a venv the folder cannot build (no `requirements.txt`; README:70 says "same venv as two-source") plus data from two other samples (`two-source-integrity-vpair/fetch_terrain.py`, `relative-nav-benchmark/fetch_data.sh aerial`, ~1 GB). The deviation table does not list it. Same pattern: `autopilot-spoof-response`, `autopilot-resilient-configs`, `golden-demo-fixedwing` use `--python <venv-with-pymavlink>/bin/python` with no `requirements.txt` and no deviation row. | Clean copy, plain `python3 run_fde.py ...` => `ModuleNotFoundError: No module named 'numpy'`. The runtime cell mentions the data; the deps cell says only `venv`. Add a one-line `requirements.txt` (`-r ../two-source-integrity-vpair/requirements.txt`) or a deviation row, and a `needs: [sample, ...]` field so the table shows the chain. |
| 4 | P2 | `README.md:26`, `docs/README.md:37`, `docs/integration-cards/` | Hop 4 "Build on cards" links a bare folder: 158 cards plus six `_index-*.md` files named after build rounds (`_index-round3`, `_index-round5-nav`, ...). No README, no capability grouping. Round-2 #19 and round-1 #22, still open. | `ls docs/integration-cards` => 164 files, no `README.md`. A team on day 0 cannot tell which `_index` file to open. |
| 5 | P2 | `README.md:10-14`, `README.md:19`, `docs/README.md:27-28` | Hard-coded counts are stale again, as round 2 predicted (#12). The new caveat says the line lags but the numbers are still the first thing read. "1-3 of 26 rows" is wrong: the decoder has 27. | README: 1558 nodes, 38 samples, 28 guides. `index/records.jsonl`: 1565 lines; `INDEX.md:5`: 43 samples, 30 guides; 44 sample folders with `sample.json` at HEAD. `decoder_rows()` parses 27 rows. Delete the numbers or generate the line in `build.py`; replace "26" with "the" rows. |
| 6 | P2 | `docs/autopilot-gnss-fault-handling.md` (not linked from `README.md`, `docs/README.md`, decoder rows 4 / 20 / 27, `docs/day0-runbook.md`) | The source-cited guide to what PX4 EKF2 and ArduPilot EKF3 do under spoofing (45 SITL flights) is reachable only from catalog pages, two cards and two sample READMEs. For a spoofing brief it is the page that explains why the vehicle ends up on the spoofed position. | `grep -rl autopilot-gnss-fault-handling` outside `catalog/`: only `docs/integration-cards/{px4__px4-autopilot,ardupilot__ardupilot}.md` and `samples/autopilot-{spoof-response,resilient-configs}/README.md`. Add it to README "Where else to look", the docs map "While building", and the stack cell of rows 4, 20, 27. |
| 7 | P2 | `samples/osint-jamming-map/README.md:55-56` | Broken documented command, open since round 1 (#9) and round 2 (#15): serving `templates/demo-dashboard` puts `../../samples/...` outside the server root. | Lines unchanged: `cd ../../templates/demo-dashboard && python3 -m http.server 8000` then `?manifest=../../samples/osint-jamming-map/out/manifest.json`. Serve the repo root and open `/templates/demo-dashboard/index.html?manifest=...`. |
| 8 | P2 | `samples/gnss-ins-ekf-outage/`, `samples/terrain-relative-nav-pf/`, `.github/workflows/check.yml:27-36` | Round-2 #17 is fully open: both stdlib samples still have no test file; CI has no smoke step for stdlib first commands; nothing fails when a sample with tests is missing from `tools/stdlib-sample-tests.txt`. These two samples are named in decoder rows 4, 15, 17 and 26. | `ls samples/gnss-ins-ekf-outage/test_*.py` => none (same for terrain-relative-nav-pf). Row 17 (underwater) starts only from `gnss-ins-ekf-outage`. |
| 9 | P2 | `docs/problem-statement-decoder.md:72` (row 14), `:75` (row 17), `:82` (row 24) | Gaps a day-0 team hits that the decoder does not flag as gaps: ground vehicles have no stdlib sample (row 14 starts from `relative-nav-benchmark`, venv + 1.13 GB KITTI + Python 3.12 pins; no wheel-odometry + GNSS-FDE loop); underwater has a pattern sample only. The "Gaps" section lists underwater and LEO but not UGV. Most of the 44 samples are airborne or autopilot SITL. | Statement 1 (urban ground robot) and statement 6 (AUV under ice) below. Add row 14 to "Gaps"; a stdlib UGV sample (wheel odometry + IMU + GNSS gate on a KITTI or UrbanNav subset) would close the commonest non-UAV brief. |
| 10 | P2 | `samples/dismounted-foot-ins/README.md:116,124` | Round-2 #13 is half done. The matrix (`docs/evidence-matrix.md:170`) and `samples/README.md` now say a fresh download gives 2.21 m vs 2.35 m and "quote 2.2-2.35 m". The sample's own result 1 still states 2.35 m with no note. A team reads the sample README when it builds on it. | `grep 2.21 samples/dismounted-foot-ins/README.md` => only an unrelated table cell at line 223. |
| 11 | P3 | `tools/query.py` ranker, `tools/search_queries.json` | Round-2 #7 root cause is still there: `usv-gnss-denied-nav` (23 tags, ~1,300-character summary) ranks first among samples for a pasted timing statement. Less harmful now that the docs route statements to `decode`, but finding 1 shows teams will still paste. | `search "Provide resilient timing for a sensor network under GNSS spoofing" --kind sample` => usv-gnss-denied-nav, osnma-authentication, maritime-ais-spoofing, then timing-holdover 4th. `search_eval.py`: `problem` split now n = 11 (was 5), bm25f MRR 0.790. |
| 12 | P3 | `samples/README.md:76-78` | "all 30 listed samples pass, 26 s" is stale: the list has 35 entries. The claim still holds: on the clean `1967cf0` copy all 35 pass with plain `python3` 3.14 in 27 s. | Loop from `check.yml:33-36`, 0 failures. Update the count and commit. |
| 13 | P3 | `samples/README.md:174` (swarm-coop-real-uwb runtime) vs `samples/swarm-coop-real-uwb/README.md:23` | Table says "download ~55 MB in ~3 min"; the README says the first-command fetch is 31 MB in 1-2 min. 55 MB is all three experiments. | Measured: `fetch_miluv.py` => "fetched 31.4 MB over HTTP", 53 s. |
| 14 | P3 | `samples/README.md:154` (remote-id-to-tak input `real`) | The first command (`rid_to_cot.py --sim --offline`) runs a synthetic scenario; "real" applies to the decoder validation (real captures + generated vectors, as `evidence-matrix.md:201` says). By the column definition (`samples/README.md:36-38`) this is `mixed`. | Ran it: 148 payloads => 256 CoT events, all `SIM*` serials. |
| 15 | P3 | `index/records.jsonl`, `tools/test_mcp_server.py:252` | On a clean checkout of a feature commit, before the bot's regenerate commit lands, `test_mcp_server.py` fails and `show sample:autopilot-resilient-configs` cannot resolve: the decoder already names the sample but the committed index does not. CI passes because it builds first. A team that clones in that window sees a red test. The working-tree `samples/README.md` row for that sample also shows input `-`. | Clean `1967cf0`: `FAIL: test_ids_resolve_and_paths_exist ... 'sample:autopilot-resilient-configs' not found`. Either make the test build the index first or say "run `tools/build.py` after cloning" in README Tools. |
| 16 | P3 | `docs/problem-statement-decoder.md:95` (in flight) | "Still missing: ... a multi-node sample". `samples/timing-network-holdover/` is being written now; when it lands, this line, row 6 "Start from" and runbook section 6 Timing need the update in the same change (`build.py` warns only for the matrix and decoder). | Untracked folder appeared during this review; no `sample.json` yet. |
| 17 | P3 | `docs/integration-cards/*.md` | Cards have no maintenance line (last push, last release). The catalog pages do, and are accurate. A card alone does not show that `krakensdr_doa`'s last release is V1.8.0 of 2024-03 or that `tercom_nav` has no release. | Spot-check table below: catalog last-push dates equal the GitHub API for all 10. |
| 18 | P3 | `docs/problem-statement-decoder.md:62` (row 4 "Start from") | Row 4 lists 11 samples, all airborne or SITL, so a maritime spoofing statement that hits row 4 first gets no vessel-relevant sample until row 7. Decode cannot filter by platform. | Statement 2 below. Either order row 7 above row 4 when a maritime cue fires, or print the platform next to each sample. |

Still-open round-2 items not repeated above: #18 (`templates/offline-kit/build_manifest.py:366,398,415`
still use `glob`), #20 (four `fact-check-*.md` files; `cold-start-review.md` has no status column),
#21 (`docs/hackathon-playbook.md` is 805 lines), #22 (`docs/SCHEMA.md:56` still
`res:afrl-magnav-challenge`).

## Round-2 status (each checked against the files, not the commit messages)

| R2 # | Item | Status | Evidence |
|---|---|---|---|
| 1 | CI: build before manifest | Fixed | `check.yml:20-21`; last 3 `check` runs on `main` green (`gh run list`), plus earlier reds on unrelated commits |
| 2 | altpnt calibration reads git-ignored files | Fixed | `geoloc-license-clean/out/results*.json` tracked; `test_altpnt_v2.py:15` `skipUnless`; altpnt tests OK on clean copy |
| 3 | scorer change vs replay tests | Fixed | No modified scorer; `real-attack-replay` and `gnss-interference-monitor` tests OK on clean copy |
| 4 | altpnt v1 41.7 % headline in matrix | Fixed | `evidence-matrix.md:78-94` says "Quote v2", v1 row marked "Withdrawn by v2"; `samples/README.md` key_result is v2 |
| 5 | samples missing from matrix / decoder; build check | Fixed (warn only) | All 44 samples with `sample.json` linked from both pages; `build.py:66-82` warns, does not fail |
| 6 | one rule for statements | Fixed | `llms.txt:5`, `docs/README.md:4-7`, `mcp_server.py:43`, `query.py:9` all say decode first |
| 7 | ranker: drill statements, usv dominance | Partial | `problem` split n = 11; usv-gnss-denied-nav still #1 for a pasted timing statement (finding 11) |
| 8 | MCP cannot read the decoder | Fixed | `mcp_server.py:69` `decode`, `:105` `read`; tests cover both |
| 9 | decoder rows 25, night, time push, swarm-real, row 15 risk | Fixed | Row 25 => celestial-star-tracker; night cue => 25, 15, 18, 16, 14; row 6 names Jammertest 2.4.2; rows 9-11 list swarm-coop-real-uwb; row 15 risk has the 80-100 % turn divergence |
| 10 | playbook picker / runbook section 6 | Partial | Content fixed (`hackathon-playbook.md:187,191`; `day0-runbook.md:184,194-196`); still hand-kept, not generated |
| 11 | vpr-large-area, golden-demo-px4 sample.json fields | Fixed | All seven fields present in both |
| 12 | README counts line | Open | Still hard-coded and stale again (finding 5) |
| 13 | dismounted numbers do not reproduce | Partial | Disclosed in matrix and samples table, not in the sample README (finding 10) |
| 14 | row 9 "honest error circle" | Fixed | Row 9 risk names 31 % coverage and `ins15_py_yrw` |
| 15 | osint-jamming-map server command | Open | Finding 7 |
| 16 | upstream findings tracker | Fixed | `docs/upstream-findings.md` exists; nothing filed, stated |
| 17 | stdlib tests, smoke step, list enforcement | Open | Finding 8 |
| 18 | manifest uses `glob` | Open | `build_manifest.py:366,398,415` |
| 19 | `_index-*.md` => one README | Open | Finding 4 |
| 20 | merge fact checks, status in cold-start | Open | Four files, no status column |
| 21 | split the playbook | Open | 805 lines |
| 22 | SCHEMA example id | Open | `SCHEMA.md:56` |
| 23 | real-attack-replay caveats in matrix | Fixed | `evidence-matrix.md:53` carries all three caveats |

Score: 12 fixed, 4 partial, 7 open. Every P0 from round 2 is fixed. What is still open is
mostly hand-kept indexes and the polish items.

## Decode quality

`python3 tools/query.py decode "<statement>"`, HEAD `1967cf0`. "Right row" = the row a team
should land on, judged from the decoder table itself.

| # | Statement (abridged) | Rows returned (score) | Right row | Verdict | Do the samples and searches help? |
|---|---|---|---|---|---|
| 1 | Ground robot patrols a dense urban area, keeps position when GPS is jammed between tall buildings and in underground parking | 9 soldier (5.4, "underground"), 23 urban canyons (5.4), 14 UGV (4.9) | 14, then 23 | Partial: right rows present, soldier row first | Row 14 starts from `relative-nav-benchmark` (venv, KITTI 1.13 GB, Python 3.12). No stdlib UGV sample. Search keywords (KISS-ICP FAST-LIO) are good |
| 2 | Patrol vessel in the Baltic, GNSS spoofed near the coast; detect it, back up position from radar and AIS | 4 spoofing (12.5), 7 maritime USV (8.9), 8 AIS zones (6.4) | 7, 8 | Good | Row 7 => `usv-gnss-denied-nav` (stdlib, ran it, numbers match) and `maritime-ais-spoofing`. Row 4's 11 samples are all airborne (finding 18) |
| 3 | Resilient time sync for radio base stations, GPS timing jammed or spoofed up to 24 hours | 6 timing (12.1), 27 fixed-wing (6.4, "hours") | 6 | Good, one spurious row | `timing-holdover` (stdlib), `real-attack-replay` (real +900 s push), OSNMA. Row 27 is noise (finding 2) |
| 4 | Detect, track and classify small hostile drones approaching a FOB, cheap sensors, alert operators | 13 C-UAS (6.9), 12 COP (4.6), 1 navigate 10 km (4.5) | 13, 12 | Good | `remote-id-to-tak` (stdlib, ran), `cuas-classifiers`, `stone-soup-tracking`. "drone detection" cue did not fire (words too far apart); row 1 is noise. Stays on detection, in scope |
| 5 | Infantry squad on foot, where each member is inside a multi-storey building, no GPS, share with platoon leader | 10 swarm (1.3), 6 timing (1.0), 20 COTS autopilot (1.0) | 9 | Miss | Row 9 (rank 4) is cut. Pasted search finds `dismounted-foot-ins` first (finding 1) |
| 6 | AUV returns to dock after 6 h under ice, no surface access | 17 underwater (7.0), 12 COP (3.8), 4 spoofing (3.0) | 17 | Right row, thin assets | Only `gnss-ins-ekf-outage` as a pattern; no card. The decoder says so honestly. Rows 12 and 4 are noise |
| 7 | (unusual) Railway convoy positioning in a long tunnel network | 26 holdover (4.1, "how long"), 25 celestial (3.7), 23 urban canyons (3.0) | None fits well; 14 (odometry + IMU) is closest | Miss, no "not covered" signal | Row 26 fires for the wrong reason (finding 2); celestial in a tunnel is wrong |
| 8 | (control) Bake a chocolate cake for the team | 10 swarm (2.0), 11 swarm coordination (1.3) | none | Should say "no match" | No floor (finding 1) |

Overall: 4 of 6 real statements land on a usable row first or second. The two misses
(dismounted wording, rail / tunnel) and the control show the same gap: no floor and missing cues.

## Samples exercised (clean copy, plain `python3` 3.14, no venv)

| Sample | Group | First command from clean state | README vs matrix vs table | Input label |
|---|---|---|---|---|
| `usv-gnss-denied-nav` | Maritime | Works, stdlib. 15 tests OK; `run.py` 1 min 42 s (README "about 2 min"). Seed 1 coastal: monitor max 10 m, detection 130 s; open water 82 m / 207 s; 1.5 km radar 1024 m | Match: README 125-131 s / 10-25 m, matrix:56,162 same, table same | `synthetic` (simulated sensors over real OSM and real AIS): honest by the column definition |
| `remote-id-to-tak` | C-UAS | Works, stdlib, 0.09 s; flags fire as documented. Tests 16 OK, 5 skip without captures | Match: 500 + 500 + 81 vectors in README, matrix:201, table | Labelled `real`; first command is synthetic (finding 14) |
| `swarm-coop-real-uwb` | Swarm | Works, stdlib, but downloads: fetch 31.4 MB in 53 s, `stats` 1.4 s, `fault` 2 min 31 s. Centralized SS 30/30 detected, median 42.0 s, 1 wrong, 0 false in 30 clean | Match: README, matrix:179-182, table (except the download size, finding 13) | `mixed` (real ranges, synthetic odometry): honest, and the matrix says which half is which |
| `multi-source-fde` | Integrity | Fails from clean state: no `requirements.txt`, needs a venv and two other samples' data (~1 GB). Not run further | Matrix:100 and table:116 agree with each other | `mixed` (real flight, simulated GNSS and TRN): honest |

## Integration card spot-check (10 cards vs `gh api repos/OWNER/REPO` and its README)

| Card | License card / API | Install card vs upstream README | Maintenance (API) | Verdict |
|---|---|---|---|---|
| snstac/pytak | Apache-2.0 / Apache-2.0 | `python3 -m pip install pytak`, v7.6.1 2026-08-23: match | pushed 2026-11-02 | OK |
| rlabbe/filterpy | MIT / MIT | `pip install filterpy`, 2.0.0 2026-10-26, "advises against git": match (README "strongly advise not installing from git") | pushed 2026-10-27 | OK |
| semuconsulting/pyubx2 | BSD-3-Clause / BSD-3-Clause | `python3 -m pip install --upgrade pyubx2`, v1.4.1: match | pushed 2026-11-06 | OK |
| PRBonn/kiss-icp | MIT / MIT | `pip install kiss-icp`, colcon line, v1.3.0 2026-04-26: match | pushed 2026-06-09 | OK |
| hku-mars/FAST_LIO | GPL-2.0 / GPL-2.0 | catkin_make path and Docker: match; no releases (API 404) | pushed 2026-10-25 | OK |
| Algafix/OSNMA | EUPL-1.2 / EUPL-1.2 | clone + `pip install -r requirements.txt`; dep list matches `requirements.txt` | pushed and v3.2.5 2026-10-14 | OK |
| dstl/Stone-Soup | MIT / MIT | `pip install stonesoup`, v1.9.1 2026-06-24, `requires-python >=3.11`: match (`pyproject.toml:21`) | pushed 2026-11-06 | OK |
| krakenrf/krakensdr_doa | GPL-3.0 / GPL-3.0 | Heimdall first, pinned conda deps: match | pushed 2025-12-13, last release V1.8.0 2024-03-01 | OK; card does not show release age (finding 17) |
| kdudkov/goatak | AGPL-3.0 / AGPL-3.0 | `docker run ... goatak_server:latest`, v0.23.0 2025-08-06: match | pushed 2026-06-30 | OK |
| mzahana/tercom_nav | "no LICENSE, package.xml says Apache-2.0, treat as unclear" / API none | colcon + `pip install numpy scipy rasterio pyproj Pillow pandas matplotlib`: match | pushed 2026-04-26, no releases | OK; the license caveat is exactly right |

10 of 10 match on license and install. The cards are the most reliable layer of the hub.

## What a day-0 team still lacks

- A decode that says "I am not sure" (findings 1-2). Today the only way to notice a miss is to
  read all 27 rows.
- An integration-card index by capability (finding 4).
- A ground-vehicle sample that runs in minutes with stdlib (finding 9).
- A "no row fits" path in `day0-runbook.md` section 1: what to do when the statement is
  outside the 27 rows (fall back to concept pages and `search` with nouns from the decode sheet).
