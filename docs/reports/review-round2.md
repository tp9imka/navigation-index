# Review, round 2

Second fresh-eyes pass, 2026-11-06, at HEAD `c915dae`. Commands ran on a clean `git archive HEAD`
copy unless noted, so a dirty working tree could not hide anything. The working tree changed
while this review ran: `scorer.py` was modified, and `thermal-geolocalization`,
`autopilot-spoof-response` and `e2e-visual-nav-vpair` appeared untracked. Findings about those
are labelled "working tree". Four drills were worked twice: once as a team member 30 minutes
after the statement drops (README => decoder => samples => evidence matrix), and once as an LLM
agent (AGENTS.md, llms.txt, `tools/query.py`, `tools/mcp_server.py` over stdin JSON-RPC).
Previous pass: [cold-start-review.md](cold-start-review.md).

Priorities: **P0** = CI is red, or a newcomer quotes a wrong number or misses the best asset.
**P1** = costs real time, a broken documented command, or drift that will recur. **P2** = polish.

## Prioritized fixes

| # | P | File | What | Why |
|---|---|---|---|---|
| 1 | P0 | `.github/workflows/check.yml` "Build from the committed tree" | Run `tools/build.py` **before** `templates/offline-kit/build_manifest.py`. | CI on `main` has failed on every push for 30 runs (`gh run list`). Failing test: `test_manifest.ManifestTests.test_committed_manifest_is_current`. Cause: `build_manifest.rank_repos()` reads `index/records.jsonl`. CI builds the manifest from the stale committed index, then `build.py` rewrites the index, then the test rebuilds and gets a different repo order. Checked on a clean HEAD copy: the CI order fails, the swapped order passes. Side effect: the "Commit regenerated catalog" step has never run, so `main` serves stale generated files. `samples/README.md` has no `swarm-coop-real-uwb` row, 13 `catalog/samples/*.md` pages are missing, and `llms.txt` says 36 samples. AGENTS.md forbids hand-regeneration, so nothing else can fix this. |
| 2 | P0 | `samples/altpnt-integrity/test_altpnt_v2.py`, `calibration.py`; `samples/geoloc-license-clean/.gitignore` | `test_committed_calibration_matches_sources` opens `samples/geoloc-license-clean/out/results.json` and `results_real_tight.json`. Both are git-ignored (`out/`). Commit the two JSONs (or a trimmed copy under `altpnt-integrity/inputs/`), or `skipIf` they are missing. | It is the second CI failure, hidden behind #1: on a clean clone the stdlib loop shows `altpnt-integrity: FAILED (errors=1)`. The other 27 listed samples pass in 26 s. It also falsifies `samples/README.md`: "Checked on 2026-11-06 with plain Homebrew python3 for all listed samples" only held on the author's tree. The geoloc numbers in the evidence matrix rest on files nobody else can see. |
| 3 | P0 (working tree) | `samples/gnss-interference-monitor/scorer.py` (modified, uncommitted), `samples/real-attack-replay/test_real_attack_replay.py` | Land the scorer fix together with updated replay tests, re-run `replay.py`, and refresh `real-attack-replay` and `gnss-interference-monitor` `key_result` (`_meta_overrides.json`), README findings 2-3 and the matrix. | With the working-tree scorer, `real-attack-replay` fails 2 tests: `test_baseline_lockout_hides_step_drop` and `test_staircase_evades_cn0_drop`. They assert the old defects. Committing `scorer.py` alone turns CI red again, and every published "shipped scorer" number goes stale. `gnss-interference-monitor` itself passes 50 tests with the new scorer. |
| 4 | P0 | `docs/evidence-matrix.md` section 3; `_meta_overrides.json` `altpnt-integrity.key_result` (=> `samples/README.md`) | Replace the v1 headline "full monitor 0 MI / 0 HMI at 41.7 % availability" with the v2 result, and add v2 rows (L2 / L2p / L3k). Change the caveat "Pessimistic noise models on purpose". | The sample's own README, "v2 section 4: What changed vs v1, honestly", says v1's zero-MI "does not survive measured errors" (MI* 8901 epochs, 74 %). It says honest availability at AL 50 m is 13-26 %, not 41.7 %. v1's heading model was optimistic, not pessimistic. Drill 1 says "demonstrate integrity", and the matrix is the page a team quotes from. Today it hands them the number the sample withdrew. |
| 5 | P0 | `docs/evidence-matrix.md`, `docs/problem-statement-decoder.md`; `tools/build.py` | Add matrix rows and decoder "Start from" entries for `celestial-star-tracker`, `real-attack-replay`, `swarm-coop-real-uwb` and `golden-demo-px4`; add `vpr-large-area` to the matrix. Add a `build.py` check that warns (later fails) when a sample with `sample.json` is not linked from both pages. | These are the best real-data samples in the hub (real Jammertest attacks, real MILUV UWB, 40 real star fields). Neither page links them. AGENTS.md requires both links for every new sample, but nothing enforces it. In round 1 the decoder had drifted the same way, and it has drifted again. |
| 6 | P1 | `llms.txt` line 5 (from `build.py`), `docs/README.md` line 4, `tools/mcp_server.py` `instructions` and `search` description, `tools/query.py` docstring | Pick one rule and state it everywhere. Recommended: "for a statement, read the decoder; search with the row's keywords". | AGENTS.md, README and runbook section 5 say not to paste a statement. llms.txt, docs/README, the MCP `initialize` instructions and the search tool description say to paste it. Measured on the drills: pasting statements 1 (fixed-wing) and 3 (timing) puts `usv-gnss-denied-nav` at #1; statements 2 and 4 work. An agent reads the MCP instructions first. |
| 7 | P1 | `tools/query.py` ranker, `tools/search_queries.json` | Add the four drill statements to the `problem` split (n = 5 today). Then fix why `usv-gnss-denied-nav` wins unrelated queries: its summary is about 1,300 characters and it has 23 tags, including "spoofing", "jamming", "integrity" and "fde". Cap the summary length that gets indexed, or tune the summary-field length normalisation. | It ranks #1 on "fixed-wing at night" and on "timing for a sensor network". `timing-holdover` is only 5th among samples for the timing statement. `celestial-star-tracker` never shows for "night". `cuas-classifiers` is missing from the top 6 samples for "detect, classify ... drones". |
| 8 | P1 | `tools/mcp_server.py` `show` for `guide:*` | Return the page body (or a `section` argument), or add a `decode {"statement"}` tool that returns the matching decoder rows. | `show guide:problem-statement-decoder` returns name, path, summary and 30 `related` ids, not the table. An MCP-only client (Claude Desktop, no file access) cannot read the one page every instruction points at. This is the unfinished half of round-1 #4. |
| 9 | P1 | `docs/problem-statement-decoder.md` | (a) Row 25 says "none - project-repo", and "Gaps" says celestial has "no sample and no integration cards yet". Both are false: `celestial-star-tracker` and the tetra3 card exist. (b) The wording row "night" maps only to rows 16 and 14. Add 25, 15 and 18: celestial, TRN and MagNav do not care about light. Add "fixed-wing" as a wording cue. (c) Row 6 and "Gaps" say a recorded log with a known time push is still missing. `real-attack-replay` has one: Jammertest 2.4.2 jumped receiver UTC by +900 s, and `clock_jump` fired. List it in rows 3, 4, 6 and 19. (d) Row 9 / 10: add `swarm-coop-real-uwb`. Row 1 / 20: add `golden-demo-px4`. (e) Row 15 risk: add "turns without a heading sensor: 80-100 % of flights diverge (blind-flight-bench)". | Drill 1 (fixed-wing, night, 30 km) lands on rows 1, 15, 16 and 18. Through them a team never meets the night-capable absolute fix the hub actually has (celestial), and never learns that TRN breaks in turns. Drill 3 is told real timing-attack data does not exist, but the hub has it. |
| 10 | P1 | `docs/hackathon-playbook.md` quick picker; `docs/day0-runbook.md` section 6 | Idea 15 (celestial) "none" => `celestial-star-tracker`; idea 19 => add `swarm-coop-real-uwb`. Runbook section 6 has no timing, dismounted or celestial rows. Its "Receiver jamming / spoofing" row lists VAARA as data but not `real-attack-replay`, the sample that replays it. Better: add `decoder_rows` and `playbook_ideas` to `sample.json`, and generate the "Start from" column and the quick-picker column in `build.py`. | Three hand-kept "where to start" tables plus the generated one have drifted again in one day. Generation is the only fix that holds. |
| 11 | P1 | `samples/vpr-large-area/sample.json`, `samples/golden-demo-px4/sample.json`; `tools/build.py` | Add `verified_status`, `deps`, `first_command`, `group`, `key_result`, `input` and `runtime`. Make `build.py` fail when a sample has none of the required fields. | `samples/README.md` shows them under "Other" with "ran (derived)", "see README" and "-" in every number column. These are two strong samples: the VPR coarse stage over 49 km2, and the PX4 port of the flagship. `golden-demo-px4` has a full result table: 3.0 s TTD, 7.8 m vs 75.0 m. |
| 12 | P1 | `README.md` "Counts on 2026-11-06" | Delete the hard-coded counts line; keep the pointer to INDEX.md and llms.txt. If the line stays, generate it. | It says 1507 records, 51 datasets, 50 dataset cards and "33 sample folders (32 with a sample.json)". A HEAD build gives 1557 nodes, 68 datasets, 59 dataset cards (per `dataset-cards/README.md`) and 37 samples. The integration-card (158) and paper-digest (46) counts are right. |
| 13 | P1 | `samples/dismounted-foot-ins/README.md` result 1, `docs/evidence-matrix.md` section 8 | Re-run and refresh, or explain the gap. | On a clean HEAD copy with the 36 trials fetched today, `run_hallway.py data/hallway --tables filter --jobs 8` gave `ins15_py_T200` all = **2.21 m / 1.33 % / 3.68 m**. README and matrix say 2.35 / 1.30 % / 3.63. `pyshoe9` gave 2.37 vs 2.51, and `ins15` 2.76 vs 2.90. Every config is off by the same ~0.14 m, which points at the data or a code change, not noise. Runtime note: the fetch took about 15 min over FTP, and the README's "~12 min" excludes it. The filter table alone took 163 s. The pyshoe columns stay "-" without the separate Python 3.11 venv (documented). |
| 14 | P1 | `docs/problem-statement-decoder.md` row 9 pitch / risk | The pitch promises "an honest error circle". The sample's default filter has a 95 % radius that covers the true error at 31 % of markers (59 % with the `yrw` variant). Put that in the risk column and point at `ins15_py_yrw`. | The pitch claims what the sample measures as false. A judge who reads the README will notice. |
| 15 | P1 | `samples/osint-jamming-map/README.md` lines 55-56 | Still `cd ../../templates/demo-dashboard && python3 -m http.server` with `?manifest=../../samples/...` (round-1 #9). Serve the repo root and open `/templates/demo-dashboard/index.html?manifest=../../samples/osint-jamming-map/out/manifest.json`. | Broken documented command: the manifest is outside the server root. |
| 16 | P1 | new `docs/reports/upstream-findings.md` | One table: repo, finding, evidence link, severity, status (not filed / filed #N / fixed in vX), route. Start with: opendroneid-core-c `decodeHorizontalAccuracy(ODID_HOR_ACC_4NM)` = 7808 m (should be 7408), 21-byte copy from a 20-byte UUID, pack decode trusts `MsgPackSize`, no range checks; OSNMAlib same-IOD forged words stay authenticated (10 min on E23), and file mode trusts signal GST; gnss_lib_py 1.1.0 `RinexObs` treats GPST as UTC; PX4 v1.17.0 SIH GPS failure injection gets no ACK; GNSS-SDR 0.0.20 segfaults on a short-form key XML; osnma-sdr-sim needs `-include bitset` on GCC 14, and `cross_auth_mode=3` never completes KROOT; pyshoe breaks on numpy >= 1.24 and has no licence file; MAVLinkMCP has unpinned `mavsdk`; Stone Soup 1.9.1 set-order nondeterminism. | These findings live in 25 cards (via `card-sample-crosscheck.md`) and in sample READMEs. The core-c card says "not fixed upstream by the hub". Nothing tracks whether anything was reported. The OSNMA same-IOD gap is security-relevant: report it privately to the maintainer (and GSC), not as a public issue. The hub's own scorer defects are tracked in `real-attack-replay` and in the working-tree `test_real_data_defects.py`. |
| 17 | P1 | `tools/stdlib-sample-tests.txt`, `.github/workflows/check.yml` | (a) `gnss-ins-ekf-outage` and `terrain-relative-nav-pf` are stdlib with zero tests (round-1 #20 still open). Add one regression test each. (b) Add a CI smoke step for fast stdlib `first_command`s: `altpnt_integrity.py --runs 1`, `trn_pf.py`, `ekf_outage.py`, `timing_holdover.py`, `locate.py`, `coop_loc.py`, `rid_to_cot.py --sim --offline --quiet`, and `llm-agent-usage`'s piped session (all under 30 s here). (c) Fail when a sample folder with `test_*.py` is neither in the list nor in an explicit exclusion list (`relative-nav-benchmark` is excluded on purpose). | Today a new sample silently skips CI unless someone edits the list by hand. Unit tests do not prove the documented first command still runs. |
| 18 | P1 (working tree) | `templates/offline-kit/build_manifest.py` | Enumerate `samples/*/requirements*.txt`, Dockerfiles and `*.sh` from `git ls-files`, not `glob`. | Untracked `samples/thermal-geolocalization/requirements.txt` is picked up locally, by code reading. A local manifest then differs from CI's, and `test_committed_manifest_is_current` flips with the working tree. Round 1 (#3) asked for the same in `build.py`. |
| 19 | P2 | `docs/integration-cards/_index-*.md` (6 files) | Replace them with one generated `docs/integration-cards/README.md`, grouped by capability, and delete the six. | The names leak build rounds (`_index-round3`, `_index-round5-nav`, ...). README and the docs map link the bare folder. Round-1 #22 is still open. |
| 20 | P2 | `docs/reports/` | Merge the four fact-check files into one `fact-checks.md` (a table of rounds with scope, sample size and error rate, then per-round detail). Add a status column (fixed / open) to `cold-start-review.md` and link this report from it. | README links the cold-start review as "a fresh-eyes review of the whole hub". Read today, about half its rows are fixed and the page does not say which half. |
| 21 | P2 | `docs/hackathon-playbook.md` (795 lines) | Move section 4 (reference architectures) next to `reference-stacks.md`, and point section 6 (prep checklist) at `templates/offline-kit`. | Same overlap as round 1; less urgent now that the docs map gives a reading order. |
| 22 | P2 | `docs/SCHEMA.md` line 56 | The example id `res:afrl-magnav-challenge` does not exist; use `res:afrl-magnav-challenge-2020`. | An agent copies examples. |
| 23 | P2 | `docs/evidence-matrix.md` (when adding `real-attack-replay`) | Carry the sample's own caveats into the row: alerts up to 300 s before a logged slot count as detections (e.g. 0.3.1b `-256 s`); variant D's threshold (0.3) was set on the same days; unlogged periods had 1-5 alarm raises per hour (possibly real tests). | The README discloses all three. A matrix row without them would read as "19/20 detected, 0 false alarms". |

## Drill 1: fixed-wing UAV, 30 km at night without GNSS, demonstrate integrity

**Human path, about 12 min to a plan.** README hop 1 => decoder wording table. "Without GNSS +
distance" gives rows 1, 2, 15, 16, 18. "night" gives 16 (thermal: "no thermal sample") and 14 (UGV).
"integrity" gives 4, 7, 19, 20, 23. "fixed-wing" is not a cue. Row 15 => `terrain-heightmap-pf`,
`blind-flight-bench`, `terrain-relative-nav-pf`. Row 18 => `magnav-quickstart`. Row 1 sends you to visual
geoloc samples that do not work at night. Integrity numbers come from the matrix section 3:
`altpnt-integrity` "0 MI / 0 HMI at 41.7 %", which the sample has withdrawn (fix 4).
`celestial-star-tracker` is reached only by reading `samples/README.md` top to bottom.

**Agent path, about 6 calls.** Pasted statement => `usv-gnss-denied-nav` first among samples, then
`golden-demo`, `altpnt-integrity`, `terrain-heightmap-pf`, `blind-flight-bench`. With keywords ("fixed-wing
night terrain navigation integrity") => `tercom_nav`, an AFRL talk, JSBSim, Paparazzi. `celestial-star-tracker`
never appeared.

**Credible plan.** TRN (`blind-flight-bench` harness, `terrain-heightmap-pf` filter) + MagNav
(`magnav-quickstart`, real SGL data) + celestial heading and coarse fix (`celestial-star-tracker`). These
are the three night-independent absolute sources. Fuse them in `altpnt-integrity` v2, with TRN
particle spread as R (its README: availability 12.9 => 16.7 % at AL 50 m, no MI). Quote honestly:
blind-flight straight 20 km gives a beam-aware PF median of 148 m (18 % diverged). With turns, every
navigator diverges in 80-100 % of flights, so heading (celestial or compass) is the load-bearing piece.
30 km is beyond every measured run (blind-flight 20 km, altpnt 18 km, terrain-heightmap 10 km).
Missing: no fixed-wing SITL (sitl-docker has Copter and PX4 quad only), no thermal sample (one
is being written, untracked).

**Ran.** `altpnt-integrity`: `python3 altpnt_integrity.py --runs 20`, stdlib, 13.9 s; table
matches the README (none 90.9 % / 5127 MI / 3217 HMI, full 41.7 % / 0 / 0). `terrain-relative-nav-pf`:
`python3 trn_pf.py`, stdlib, 1.5 s; INS 380.3 m and PF 13.0 m at 200 s, inside the README's 4-25 m.
Venv samples (`blind-flight-bench`, `terrain-heightmap-pf`, `celestial-star-tracker`) not run: no venvs on this
machine, and the house rule is no unrequested installs. Their numbers were cross-checked README
vs matrix vs `samples/README.md`. Terrain v1 at 10 km: hilly 26 / 32 / 311, mixed 32 / 123 / 404,
flat 41 / 210 / 334, smooth 539 / 334 / 334. Blind-flight: 148 / 983 m, DR 1582 / 3659 m, turns 3908 m. All
consistent.

## Drill 2: detect, classify and localize drones and GNSS jammers around a base, show on TAK

**Human path, about 8 min.** Wording => rows 13 (C-UAS), 3 and 5 (jamming), 12 (COP). Samples:
`remote-id-to-tak`, `cuas-classifiers`, `stone-soup-tracking`, `jammer-sensor-network`,
`interference-geolocation-to-tak`, `mavlink-to-tak-cot`. The clearest of the four drills.

**Agent path, 2 calls.** Pasted statement => `jammer-sensor-network`, `interference-geolocation-to-tak`, then
`mavlink-to-tak-cot`; `remote-id-to-tak` is 5th among samples and `cuas-classifiers` is absent. Keywords
"drone detection remote id radar classify TAK" => `remote-id-to-tak`, `cuas-classifiers` first.

**Credible plan.** Cooperative drones: `remote-id-to-tak` (decoder bit-exact against core-c, plausibility
flags, CoT). Non-cooperative: `cuas-classifiers` (real NRC radar, 0.928 balanced accuracy; DroneRF
detection 0.977-0.994, "do not quote as field performance"), then Stone Soup tracks. Jammers:
`jammer-sensor-network` (u-blox C/N0 + AGC => grid / RSS / DF => CoT), sized by the matrix (16 nodes
on 4 x 4 km: 313 m grid, 40 m with 3 DF stations, synthetic). Missing: no glue that puts all three
CoT streams on one picture (each sample writes its own), and non-cooperative drone *localization*
exists only as synthetic Stone Soup tracks.

**Ran (all stdlib).** `python3 locate.py` 0.14 s: ls 14 m, ellipse 49 x 33 m, matching the README.
`python3 demo.py` (jammer-sensor-network) 24 s (README "~40 s"): static scenario grid 599.3 m,
DF 23.4 m, grid+DF 56.9 m, exact README values. `python3 rid_to_cot.py --sim --offline --quiet` 0.1 s;
flags fire. `python3 -m unittest -v test_cot && python3 cot.py` OK. `cuas-classifiers` is a venv
with Python 3.12 and not run.

## Drill 3: resilient timing for a sensor network under GNSS spoofing

**Human path, about 6 min.** Wording => rows 6 and 19 => `timing-holdover`, `osnma-authentication`,
`gnss-interference-monitor`, guide `timing-resilience.md`. Good guide. Row 6's dataset cell and "Gaps" say
no recorded time-push data exists; `real-attack-replay` (real Jammertest 2.4.2, UTC +900 s) is not
linked from any timing page (fix 9c).

**Agent path, 3 calls.** Pasted statement => `usv-gnss-denied-nav` #1, `guide:timing-resilience` #2.
Among samples `timing-holdover` is 5th. Keywords "timing holdover oscillator spoofing time push"
=> `timing-holdover` #1.

**Credible plan.** Per node: GNSS-disciplined clock with holdover budget (`timing-holdover`), OSNMA
authentication state (`osnma-authentication` adapter => scorer), and clock-jump / drift features
(`gnss-interference-monitor`). Across nodes: the cross-source monitor from `timing-holdover` (alarm 120-660 s
for 0.5-10 ns/s walks), extended to N nodes. Missing: a multi-node sample (today it is one clock
plus one "second source"), and any PTP / chrony piece in code (cards only). Validate the clock-jump
path on `real-attack-replay` day 12.

**Ran (stdlib).** `python3 timing_holdover.py` 4.3 s: 24 h medians TCXO 59.58 us, CSAC
1.27 us, OCXO 610.0 ns, Rb 43.8 ns, exactly as matrix section 10; walk-spoof table matches.
`osnma-authentication`: tests + `demo_adapter.py` 0.7 s, OK. `real-attack-replay`: tests OK,
`./fetch_data.sh` 25 s (64 MB), replay 14 s. 19 of 20 slots detected and 2.4.3 missed, matching
the README.

## Drill 4: indoor / underground navigation for a dismounted team

**Human path, about 5 min.** Wording => row 9 => `dismounted-foot-ins` (real pyshoe trials, CoT out),
`mavlink-to-tak-cot`. "team" => rows 10 and 11 => `swarm-coop-localization`. The real-UWB sibling
`swarm-coop-real-uwb` is linked from neither row.

**Agent path, 1 call.** Pasted statement => `concept:indoor-pedestrian`, `dismounted-foot-ins`, primer
chapter 8. Good.

**Credible plan.** `dismounted-foot-ins` ZUPT EKF + corridor heading + UWB (aided 1.07 m ARMSE, UWB
simulated) for each member. Inter-member ranging from `swarm-coop-real-uwb` (real MILUV: centralized
0.20 m vs DR 0.48 m). TAK via the sample's CoT export. Two honesty traps for the pitch: the
default 95 % radius covers the truth at only 31 % of markers (fix 14), and the magnetometer
indoors makes position 2-9x worse. Missing: floor plan / map matching, and real UWB on foot.

**Ran.** `python3 -m unittest discover` 0.45 s OK. `sh fetch_data.sh` about 15 min (36 trials +
5 magnetometer logs, 108 MB, FTP). `run_hallway.py data/hallway --tables filter --jobs 8` 163 s.
Numbers are about 0.14 m better than published in every row (fix 13).

## Agent tooling notes

- MCP over stdin: `initialize`, `tools/list` (search, show, concept, neighbors), `tools/call` all fine.
  An unknown `kind` now returns an error listing the valid kinds (round-1 note fixed).
  `show sample:*` now returns `readme`, `status`, `deps`, `first_command` (round-1 #18 fixed).
  `llm-agent-usage` piped session: 7 responses.
- `search_eval.py`: BM25F MRR 0.846 overall, 0.700 on the 5-query `problem` split; parity with
  the site JS 35/35. The `problem` split is too small to catch the drill regressions in fix 7.
- The second MCP server (`llm-mission-agent`) was not exercised; it needs pymavlink and SITL.

## Consistency audit

- Matrix vs sample READMEs, spot-checked: golden-demo, altpnt-integrity v1, terrain-heightmap-pf
  v1/v2, blind-flight-bench, terrain-relative-nav-pf (decoder row 15), usv-gnss-denied-nav (1391-1395 /
  2255-2261 m, 125-131 s), jammer-sensor-network, interference-geolocation, timing-holdover,
  dismounted-foot-ins. All copy their README correctly. The two problems are which result is
  quoted (altpnt v1 vs v2, fix 4) and a result that no longer reproduces (dismounted, fix 13).
- `samples/README.md` vs matrix: consistent where both exist. Five committed samples are in
  neither the matrix nor the decoder (fix 5).
- Round-1 fixes confirmed: README four-hop entry, decoder refresh, `samples/README.md` generated,
  docs map, single install convention with a deviation table, `golden-demo/run.sh` no longer
  overwrites committed `data/` (writes to `runs/` unless `--update-reference`), AGENTS.md id
  fixed, INDEX pluralisation (only "masterclasses" left, correct), maritime synonyms, USV sample
  added (round-1 #11), jammer sensor network added (#12). Still open: #9 (fix 15), #20 (fix 17a),
  #22 (fixes 19-20).

## What's strong

- **Honest samples.** Almost every README separates what ran from what did not, names the
  interpreter and data, and keeps its negative results (altpnt v2 retracting v1, osint's
  Sentinel-1 layer not agreeing, 1 of 5 real eBee frames fixed, "no real spoofing found in 8.8 h").
  The problem is only that some summaries (matrix, `key_result`) lag the READMEs.
- **Stdlib reproducibility.** Every stdlib first command I ran (9 samples) finished in 0.1-25 s
  with no installs and matched the published numbers, most to the last digit.
- **Real-data samples.** Jammertest replay, OSNMA on a real recording, MILUV UWB, pyshoe,
  NRC radar, DMA AIS, CORS RINEX, real star fields. Rare for a hackathon kit, and they found real
  defects in the hub's own scorer and in upstream code.
- **The decoder + samples table + matrix chain** works for drills 2-4 in under 10 minutes. The
  wording table is a good idea and is the right fix for free-text search.
- **Agent surface.** Stdlib MCP server with clear errors, a prompt-injection notice in its
  instructions, ranker parity tested against the site JS, and a guarded vehicle MCP server with
  a dry-run mode.
