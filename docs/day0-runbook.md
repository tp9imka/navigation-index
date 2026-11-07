# Day-0 runbook: the first 3 hours

What a 4-5 person team does from the moment the problem statement drops until H+3, when a
walking skeleton should run end to end. It assumes the
[prep checklist](hackathon-playbook.md#6-pre-hackathon-prep-checklist) is done: datasets on
disk, SITL images built, the [project-repo template](../templates/project-repo/) green on
every laptop, the hub registered as an MCP server.

Companions: [problem-statement-decoder.md](problem-statement-decoder.md) (statement => approach;
the single source for "where to start"), [samples/README.md](../samples/README.md) (status and
first command per sample), [evidence-matrix.md](evidence-matrix.md) (numbers you can cite),
[hackathon-playbook.md](hackathon-playbook.md) (ideas, differentiators, 48h plan),
[reference-stacks.md](reference-stacks.md) (what to build on, licenses),
[templates/](../templates/README.md) (fill-in files).

Brief family known? Read its [cheat sheet](cheatsheets/README.md) first (3 minutes each).

Times are a plan, not a measurement. If a block overruns by more than 10 minutes, the Lead
cuts scope, not the next block.

## Timeline

| Clock | Who | Do | Output |
|---|---|---|---|
| 0:00-0:10 | All | Read the statement twice, silently. Then the judging criteria, rules, provided data and hardware. Highlight nouns: platform, threat, deliverable, constraints. | Highlighted statement |
| 0:10-0:20 | Lead + Pitch | Fill the decode sheet ([section 1](#1-decode-the-statement)). Match it to 1-3 rows of the [decoder](problem-statement-decoder.md). | Decode sheet, 3 candidates |
| 0:10-0:20 | Nav, Platform, Viz | For each candidate row: open its samples in [samples/README.md](../samples/README.md) (status, deps, first command) and its numbers in [evidence-matrix.md](evidence-matrix.md); then the linked integration and dataset cards; MCP queries with the row's keywords ([section 5](#5-find-components-fast-with-the-hub-via-mcp)). | One stack and one starting sample per candidate |
| 0:20-0:25 | Lead | Send organisers the open questions (data provided? RF allowed? hardware on site? scoring weights? submission format?). | Questions sent |
| 0:25-0:40 | All | Score the 3 candidates independently with the rubric ([section 2](#2-pick-the-idea-scoring-rubric)), then compare. Discuss only the criteria where scores differ by 2 or more. | Scores table |
| 0:40-0:50 | Lead | Decide idea + fallback. Name the one metric. Write the five-line demo script ([demo-script](../templates/demo-script.md)). Record the decision in ADR-001 ([adr](../templates/adr.md)). | ADR-001, demo script v0 |
| 0:50-1:00 | Lead | Assign roles and stage owners ([section 3](#3-assign-roles)). | Roles table filled |
| 1:00-1:15 | Platform | Bootstrap the repo from the template ([section 4](#4-bootstrap-from-templatesproject-repo)); push; everyone clones and runs `make test eval`. | Team repo green |
| 1:00-1:15 | Viz | Start the TAK side: GoATAK or OpenTAKServer locally; point `make demo` CoT at it. | Synthetic track visible on a map |
| 1:00-1:15 | Pitch | Threat model v0 ([threat-model](../templates/threat-model.md)), risk register v0 ([risk-register](../templates/risk-register.md)). | Two files committed |
| 1:15-1:45 | Platform | Start the SITL or load the dataset subset picked in [section 6](#6-which-sitl-or-dataset-to-start). | Raw data or telemetry flowing |
| 1:15-1:45 | Nav | Read the 2-3 integration cards for the chosen core; write the real `PoseSource` adapter interface against the template's `Epoch`. | Adapter stub + test |
| 1:15-1:45 | Viz | Map the metric and the integrity state onto the operator view (colour, `ce`/`le`, alert text). | Mock operator view |
| 1:45-2:30 | Platform + Nav | Real input => template filter => template monitor => publisher. Dumb algorithm on purpose. | Real data on the map |
| 1:45-2:30 | Pitch | Write the evaluation plan: baseline vs ours, which ground truth, which alert limit. Check dataset and model licenses ([reference-stacks](reference-stacks.md#license-traps-from-the-cards)). | `docs/eval-plan.md` |
| 2:30-2:50 | All | Fix whatever blocks the end-to-end run. No new features. | `make demo` on real input |
| 2:50-3:00 | Lead | H+3 checkpoint ([section 7](#7-h3-checkpoint)). | Go, or switch to the fallback now |

## 1. Decode the statement

Answer each line from the statement text, not from what you hoped it would say. "Not stated"
is an answer; turn it into a question for the organisers.

| Question | Why it matters |
|---|---|
| Platform (UAS multirotor / fixed-wing / UGV / USV / UUV / person / team / fixed site)? | Picks the [platform row](hackathon-playbook.md#22-platforms) and the simulator |
| Threat (jamming / spoofing / both / link loss / no GNSS at all / timing)? | Detect-only vs navigate-through |
| Deliverable (vehicle that navigates / monitor or map / C2 picture / analysis tool)? | Vehicle demos need SITL by H+6 |
| Scoring (accuracy / robustness / time to detect / operator value / business case)? | Picks the one metric |
| Distance, duration or area named? | Sets the drift budget and whether absolute aiding is needed |
| Data or hardware provided? Any provided log format? | A provided format beats any pre-downloaded set |
| RF rules (receive-only? transmission banned?) and drone rules | Assume no transmission; GNSS generation to file or cable only |
| Words like "AI", "plug-in", "low-cost", "swarm", "operator" | Funders' words: reuse them in the pitch ([programs](landscape/programs-and-challenges.md)) |

Then use the [decoder's wording table](problem-statement-decoder.md#decode-the-wording-first)
to get candidate rows.

If no row fits (decode returns rows that do not match the platform or the threat, or matches
only on one generic word), do not force one. Take two or three nouns from the answers above
(platform, sensor, threat) and run `python3 tools/query.py search "<nouns>" --kind sample`, then
the same with `--kind repo`; open the matching concept page (listed in
[INDEX.md](../INDEX.md)) for the cards and datasets around it. Check the decoder's
[gaps](problem-statement-decoder.md#gaps-this-table-exposed) before you promise a result:
ground vehicles on recorded data, underwater and LEO have no runnable sample.

## 2. Pick the idea: scoring rubric

Use [practical readiness](practical-readiness.md) to filter candidates by the laptop,
hardware and download budget available. Unknown setup/download values do not satisfy a
budget. Prefer a [starter bundle](starter-bundles.md) your teammate already rehearsed offline;
a `ran` sample by itself does not prove this machine has its data, weights and dependencies.

Hard gates first. Drop a candidate if any is true:

- It needs RF transmission, a GNSS signal over the air, or flying a real drone the rules do not allow.
- It needs data that is not on disk and cannot be fetched in under an hour at the venue
  (assume venue Wi-Fi will not carry multi-GB downloads).
- It needs hardware that is not in the room.
- It drifts into targeting, terminal guidance or offensive EW ([scope](export-control-and-ethics.md)).

Then score 1-5 on each criterion. The weights are this runbook's suggestion; change them if
the judging criteria say otherwise, and write the change in ADR-001.

| Criterion | Weight | 1 | 5 |
|---|---|---|---|
| Fit to the statement and its judging criteria | x3 | Tangential; needs re-framing | Uses the statement's own words; hits the main scoring line |
| Skeleton by H+6 with what is on disk | x3 | New toolchain, nothing built, no data local | A sample marked `ran` that already does half of it, + a shortlisted dataset or a built SITL image |
| Measurable with ground truth | x2 | Only "it looks right" | ATE / time-to-detect / false alarms vs ground truth, automated in `eval/` |
| Differentiation ([playbook 1.1](hackathon-playbook.md#11-differentiators-judges-have-not-seen)) | x2 | The demo every team brings | Integrity, honest uncertainty or a hard condition, measured |
| Team skill match | x2 | Nobody has used the core library | Someone shipped with it before |
| Risk (version traps, gated data, GPU, licenses) | x1 | Several red flags in the cards | Cards show a clean install and permissive licenses |

Total = sum of score x weight (max 65). Pick the highest; the runner-up that shares the most
components becomes the fallback. On a tie, take the candidate where an integrity layer is
natural - it is the hardest thing for other teams to copy in 48h.

## 3. Assign roles

From [team roles and 48h plan](../templates/team-roles-and-48h-plan.md). One owner per
template stage; interface changes need an ADR.

| Role | Owns in the template | First task at H+1 |
|---|---|---|
| Lead / integrator | Repo, `main` green, go/switch call | Bootstrap review, merge order |
| Nav / estimation | `NavFilter`, `IntegrityMonitor`, `eval/metrics.py` | Card reading, adapter interface, baseline numbers |
| Platform | `PoseSource` adapters, SITL, docker, hardware | SITL or dataset loader |
| Viz / C2 | `Publisher`s, TAK / web map | Map on screen with synthetic data |
| Pitch / evidence | Threat model, risk register, eval plan, deck, tests | Threat model v0, licenses, questions to organisers |

With 3 people: Lead also owns Pitch, Platform also owns Viz.

## 4. Bootstrap from templates/project-repo

The template's stdlib core needs only `python3`. `make test` (21 tests) and `make eval` were
run on a copy of the template on 2026-11-06 and passed; the eval table matched the one in the
[templates README](../templates/README.md).

```sh
cp -r /abs/path/navigation-index/templates/project-repo ~/team-repo
cd ~/team-repo && git init && git add -A && git commit -m "chore: bootstrap from navigation-index template"
make test          # unit tests
make eval          # synthetic clean / jam / spoof => runs/results.md
make demo          # spoof scenario: CoT to 127.0.0.1:6969, STATUSTEXT to 127.0.0.1:14550
```

Then, in this order:

1. Replace `TODO` lines in `README.md`: one-line pitch, problem, threat-model table.
2. Copy the fill-in files you will use from `templates/` into `docs/`
   (threat model, ADR, risk register, demo script).
3. Write the real input as a new `PoseSource` (UBX replay, GnssLogger CSV, SITL telemetry,
   dataset reader). Keep `sim.py` for tests.
4. Leave the template `NavFilter` and `IntegrityMonitor` in place until the real input flows.
   Swap one stage at a time.
5. Optional deps go behind extras in `pyproject.toml`; `make setup` creates `.venv`.

`AGENTS.md` / `CLAUDE.md` in the template already point coding agents at this hub.

## 5. Find components fast with the hub via MCP

Register once (the server is stdlib Python):

```sh
claude mcp add navigation-index -- python3 /abs/path/navigation-index/tools/mcp_server.py
```

Tools: `search` (keywords, optional `kind`, `fit`, `domain`, `concept`), `concept` (everything
tagged with a concept, high fit first), `neighbors` (graph walk from an id), `show` (full
record), `read` (MCP only: full markdown of a guide or sample README, e.g. the decoder).
Without MCP, `python3 tools/query.py <tool> ...` takes the same arguments for the first four;
open the file instead of `read`.

Every result is an id. Turn it into a file: `repo:owner/name` => integration card
`docs/integration-cards/owner__name.md` if it exists, else `catalog/repos/owner__name.md`.
Datasets => [dataset cards](dataset-cards/README.md). Samples => `samples/<name>/`.

Tips: `concept` with `fit: high` beats free-text search; `neighbors` from one repo you trust
finds its alternatives and integrations; free-text search on common words ("spoofing
detection") returns noise from other domains, so add a concept or `kind` filter.

Do not paste the problem statement into `search`: free text ranks poorly (a cold-start test
on 2026-11-06 got ION courses and an unrelated loitering munition for full-sentence queries).
Take the keywords from the matching [decoder](problem-statement-decoder.md) row instead.
Keyword queries that ranked the right sample first (re-checked with `tools/query.py` on 2026-11-06,
after review round 2):

```
search {"query":"ArduCopter spoof EKF3 dashboard"}            => golden-demo
search {"query":"jammer localization sensor network TAK"}     => jammer-sensor-network, then interference-geolocation-to-tak
search {"query":"spoofing integrity uav","kind":"sample"}     => altpnt-integrity
search {"query":"star tracker celestial night heading","kind":"sample"}       => celestial-star-tracker
search {"query":"timing holdover oscillator spoofing time push","kind":"sample"} => timing-holdover
search {"query":"jammertest real attack replay u-blox","kind":"sample"}      => real-attack-replay
search {"query":"PX4 SIH GPS spoof external vision","kind":"sample"}         => golden-demo-px4
concept {"id":"concept:maritime-nav","fit":"high"}            => maritime repos, high fit first
```

Rankings shift when the index is rebuilt. `show sample:<name>` returns the sample record; its
README is `samples/<name>/README.md`.

## 6. Which SITL or dataset to start

The decoder's "Start from" column is the source of truth for which sample fits a statement;
this table adds the data to have on disk and the version trap for each class.
Start from what is already on disk. Sizes are from the [dataset cards](dataset-cards/README.md).
The [sitl-docker](../samples/sitl-docker/) compose file pins ArduCopter 4.6.3 and PX4 v1.17.0 SIH
(check its README for what was run).

| Problem class | Start with | First command / file | Version trap |
|---|---|---|---|
| UAS navigates through GNSS loss (ArduPilot) | ArduPilot SITL from sitl-docker + [ardupilot-ekf3-source-switch](../samples/ardupilot-ekf3-source-switch/) | `docker compose up -d ardupilot` | 4.6.x: `SIM_GPS_DISABLE 1`; 4.7 / master: `SIM_GPS1_ENABLE 0` ([card](integration-cards/ardupilot__ardupilot.md)) |
| UAS with VIO or map-matching into PX4 | PX4 SIH from sitl-docker + [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/) | `docker compose up -d px4`; GPS loss via `param set SIM_GPS_USED 0` as in the sample; for a spoof plus switch to external vision, [golden-demo-px4](../samples/golden-demo-px4/) `./run.sh` | On v1.17.0 SIH `failure gps off` / MAVSDK GPS failure injection gets no ACK and does nothing; v1.17.0 has no `GPS_INPUT` handler (golden-demo-px4 uses `HIL_GPS`); SIH target and `EKF2_AGP*` params differ between v1.17.0 and `main` ([card](integration-cards/px4__px4-autopilot.md)); `mavsdk-grpc` (in the sitl-docker client image, or a `.venv`) |
| Visual geolocalization | NAIP via [geoloc-license-clean](../samples/geoloc-license-clean/) `download_data.py` (121 MB); [UAV-VisLoc](dataset-cards/uav-visloc.md) site 03 (2.0 GB) | [geoloc-license-clean](../samples/geoloc-license-clean/) (known prior), [vpr-large-area](../samples/vpr-large-area/) (no prior: retrieval over 49 km2 of NAIP first), [e2e-visual-nav-vpair](../samples/e2e-visual-nav-vpair/) (whole chain on a real flight), [thermal-geolocalization](../samples/thermal-geolocalization/) (night, thermal frames), [visual-geolocalization-lightglue](../samples/visual-geolocalization-lightglue/) | LightGlue with ALIKED, not SuperPoint (NC weights, [weights licenses](model-weights-licenses.md)); real frames fixed 1 of 5 in geoloc-license-clean and 1 of 23 in the vpr chain; FAISS and torch in one process abort on macOS arm64 |
| VIO / LiDAR drift | [UZH-FPV](dataset-cards/uzh-fpv.md) (0.84 GB), [KITTI](dataset-cards/kitti.md) 04, VPAIR sample (0.86 GB) | [relative-nav-benchmark](../samples/relative-nav-benchmark/) `./run.sh lidar` / `vio` / `aerial` | EuRoC host rate-limits (HTTP 429 in the sample run); OpenVINS image build ~20 min |
| Receiver jamming / spoofing | [Jammertest](dataset-cards/jammertest-data.md) VAARA: the 7 u-blox logs are 64 MB via real-attack-replay's `./fetch_data.sh` (the full repo is 1.57 GB); [TEXBAT](dataset-cards/texbat.md) subset (8.8 GB), or simulated IQ | [real-attack-replay](../samples/real-attack-replay/) (real attacks through the scorer), [gnss-interference-monitor](../samples/gnss-interference-monitor/), [gnss-signal-chain](../samples/gnss-signal-chain/) `./run.sh` (file only, ~600 MB per scenario) | VAARA logs have no UBX NAV or MON-RF and break pyubx2 1.4.1 (use the sample's framer); VAARA states no licence, so do not redistribute it; S7AM1NA public sample is not a labelled attack |
| UAS spoof + integrity demo | ArduCopter or PX4 SITL from sitl-docker | [golden-demo](../samples/golden-demo/) `./run.sh --v2`, [golden-demo-px4](../samples/golden-demo-px4/) `./run.sh`, [altpnt-integrity](../samples/altpnt-integrity/) for PL (quote v2: `altpnt_v2.py`), [two-source-integrity-vpair](../samples/two-source-integrity-vpair/) for PL with two absolute sources on a real flight, [autopilot-spoof-response](../samples/autopilot-spoof-response/) `python3 spoof_sweep.py` for what the stock EKF2 / EKF3 do without a monitor; why, from source: [autopilot-gnss-fault-handling](autopilot-gnss-fault-handling.md) | Copter 4.6.3 and PX4 v1.17.0 SIH only tested; both fly a ~950 m survey with no jamming phase; altpnt v1's 41.7 % availability does not hold under measured error models |
| Fixed-wing long route (ArduPlane) | Plane image built by [golden-demo-fixedwing](../samples/golden-demo-fixedwing/) `run.sh` on top of the sitl-docker copter image (40 s here) | [golden-demo-fixedwing](../samples/golden-demo-fixedwing/) `PYTHON=.venv/bin/python ./run.sh` (4 flights in parallel, ~5 min wall at speedup 5) | Plane 4.6.3 only tested; ExternalNav NE must use ArduPilot's spherical `LATLON_TO_M`, not WGS84 ENU (34 m off at 11 km); `AHRS_OPTIONS` bit 0 or DCM falls back to the spoofed GPS; `EK3_SRC2_VELXY 6` needs VisualOdom to arm |
| Phone / raw GNSS | [GSDC](dataset-cards/gsdc.md) taroz zip (2.76 GB), [UrbanNav](dataset-cards/urbannav.md) | [gnss-rinex-processing](../samples/gnss-rinex-processing/) (RTKLIB in Docker, ran on CORS data) | gnss-lib-py needs Python below 3.15 |
| INS holdover | [KITTI](dataset-cards/kitti.md) raw drive (1.2 GB), [NCLT](dataset-cards/nclt.md) (0.24 GB) | [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/) | FilterPy 2.0.0 API change |
| Terrain navigation | Copernicus GLO-30 windows (`fetch_dem.py`, ~0.8 MB each) | [terrain-heightmap-pf](../samples/terrain-heightmap-pf/), [blind-flight-bench](../samples/blind-flight-bench/) (radar altimeter only, see [teardown](landscape/blind-flight-teardown.md)), [two-source-integrity-vpair](../samples/two-source-integrity-vpair/) (TRN from real NRW 1 m LiDAR along a real flight, `fetch_terrain.py` ~120 MB) | elevation 2.0 breaks 1.x commands; GLO-30 is a DSM, not bare earth |
| Radio ranging / swarm | [UTIL](dataset-cards/util-uwb-tdoa.md) (1.86 GB), [MILUV](dataset-cards/miluv.md) (3.2 GB) | [swarm-coop-localization](../samples/swarm-coop-localization/) (stdlib sim), [swarm-coop-real-uwb](../samples/swarm-coop-real-uwb/) (`fetch_miluv.py` pulls 31.4 MB of CSVs for the main experiment, 54.6 MB for all three, from the 3-11 GB zips by HTTP range), [GTSAM card](integration-cards/borglab__gtsam.md) | MILUV odometry is not used: the sample's odometry is synthetic |
| Maritime | Committed OSM chart + DMA AIS fixtures; [Pohang](dataset-cards/maritime-datasets.md) navigation.zip (about 20 MB) for real radar | [usv-gnss-denied-nav](../samples/usv-gnss-denied-nav/) (own ship), [maritime-ais-spoofing](../samples/maritime-ais-spoofing/) (AIS) | Simulated radar sees the same chart: fix errors optimistic |
| C-UAS awareness | [Remote ID captures](dataset-cards/remote-id-droneid-captures.md), [DroneRF](dataset-cards/drone-rf-datasets.md) (692 MB RAR), NRC radar tracks (~59 MB) | [remote-id-to-tak](../samples/remote-id-to-tak/), [cuas-classifiers](../samples/cuas-classifiers/), [stone-soup-tracking](../samples/stone-soup-tracking/) | Stone Soup needs Python 3.11+; DroneRF is one session per class |
| MagNav | [MagNav challenge data](dataset-cards/magnav-challenge-data.md) (1.87 GB) | [magnav-quickstart](../samples/magnav-quickstart/) (ran in the `julia:1.11` Docker image) | ~10 min install + precompile, 5.8 GB Julia depot; pin FFTA 0.2; AFRL data agreement |
| Timing | Nothing to download for the sim; VAARA logs (above) for a real +900 s time push | [timing-holdover](../samples/timing-holdover/) `python3 timing_holdover.py` (stdlib, ~5 s); [timing-network-holdover](../samples/timing-network-holdover/) `python3 timing_network.py` (stdlib, ~50 s; several sites over PTP-like links, cross-node check for a time push); [real-attack-replay](../samples/real-attack-replay/) for 2.4.2; guide [timing-resilience](timing-resilience.md) | Oscillator models are datasheet parameters, not a unit; receiver time only shows jumps > 5 s |
| Dismounted / indoor | pyshoe hallway set via [dismounted-foot-ins](../samples/dismounted-foot-ins/) `sh fetch_data.sh` (~120 MB, about 15 min over FTP) | `python3 run_hallway.py data/hallway --tables filter --jobs 8` (stdlib, ~3 min) | pyshoe's own code needs Python 3.11 + numpy < 1.24; the filter's 95 % radius covers the truth at 31 % of markers |
| Celestial | cedar-solve test frames, SkyView cutouts, DE421 via [celestial-star-tracker](../samples/celestial-star-tracker/) `python3 fetch_data.py` (~190 MB, ~5 min) | `.venv/bin/python plate_solve_eval.py` (~10 s) | cedar-solve from git tag v0.6.0 with `--no-deps` (PyPI 0.5.1 predates its NumPy 2 fix); SkyView sometimes answers "Too Many Processes" |

If the organisers provide data, start there instead and keep one shortlisted set as a
cross-check.

## 7. H+3 checkpoint

Go if all of these are true; otherwise switch to the fallback now, while it is cheap.

- [ ] Real input (SITL telemetry, recorded data or provided data) reaches the map through the
      template pipeline.
- [ ] The one metric is named in ADR-001 and `eval/` can compute it, even if the number is bad.
- [ ] Ground truth for that metric exists on disk.
- [ ] No unresolved hard-gate question from the organisers.
- [ ] Threat model v0 and risk register v0 are committed.
- [ ] Every person knows their H+3 to H+6 task (the playbook's
      [48h plan](hackathon-playbook.md#5-48h-execution-plan-template) takes over from here).
