# Day-0 runbook: the first 3 hours

What a 4-5 person team does from the moment the problem statement drops until H+3, when a
walking skeleton should run end to end. It assumes the
[prep checklist](hackathon-playbook.md#6-pre-hackathon-prep-checklist) is done: datasets on
disk, SITL images built, the [project-repo template](../templates/project-repo/) green on
every laptop, the hub registered as an MCP server.

Companions: [problem-statement-decoder.md](problem-statement-decoder.md) (statement => approach),
[hackathon-playbook.md](hackathon-playbook.md) (ideas, differentiators, 48h plan),
[reference-stacks.md](reference-stacks.md) (what to build on, licenses),
[templates/](../templates/README.md) (fill-in files).

Times are a plan, not a measurement. If a block overruns by more than 10 minutes, the Lead
cuts scope, not the next block.

## Timeline

| Clock | Who | Do | Output |
|---|---|---|---|
| 0:00-0:10 | All | Read the statement twice, silently. Then the judging criteria, rules, provided data and hardware. Highlight nouns: platform, threat, deliverable, constraints. | Highlighted statement |
| 0:10-0:20 | Lead + Pitch | Fill the decode sheet ([section 1](#1-decode-the-statement)). Match it to 1-3 rows of the [decoder](problem-statement-decoder.md). | Decode sheet, 3 candidates |
| 0:10-0:20 | Nav, Platform, Viz | Run the MCP queries for the matching statement ([section 5](#5-find-components-fast-with-the-hub-via-mcp)); open the linked integration and dataset cards. | One stack per candidate |
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

## 2. Pick the idea: scoring rubric

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
| Skeleton by H+6 with what is on disk | x3 | New toolchain, nothing built, no data local | Template + a sample + a shortlisted dataset or a built SITL image |
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
record). Without MCP, `python3 tools/query.py <tool> ...` takes the same arguments.

Every result is an id. Turn it into a file: `repo:owner/name` => integration card
`docs/integration-cards/owner__name.md` if it exists, else `catalog/repos/owner__name.md`.
Datasets => [dataset cards](dataset-cards/README.md). Samples => `samples/<name>/`.

Tips: `concept` with `fit: high` beats free-text search; `neighbors` from one repo you trust
finds its alternatives and integrations; free-text search on common words ("spoofing
detection") returns noise from other domains, so add a concept or `kind` filter.

The calls below were piped into `tools/mcp_server.py` on 2026-11-06 against the index built
that day; the hits column is what came back (top 5). Rankings can shift when the index is rebuilt.

| # | Statement | MCP calls | Top hits on 2026-11-06 | Then open |
|---|---|---|---|---|
| 1 | Navigate a drone 10 km without GNSS | `concept {"id":"concept:visual-geolocalization","domain":"air","fit":"high"}`; `neighbors {"id":"repo:cvg/lightglue"}` | WildNav, visual_localization, UAVLocalization, AnyVisLoc benchmark, GeoAnchor; neighbors add AnyLoc, hloc | [LightGlue card](integration-cards/cvg__lightglue.md), [AnyLoc card](integration-cards/anyloc__anyloc.md), [UAV-VisLoc](dataset-cards/uav-visloc.md) |
| 2 | Detect and map GNSS jamming | `concept {"id":"concept:gnss-interference","fit":"high"}`; `search {"query":"ads-b integrity interference map"}` | ADSBCOT, readsb, KrakenSDR DoA, Fraunhofer Jammertest 2025, GNSS-SDR; search adds GPSJam, Inside GNSS ADS-B mapping, the interference-monitor sample | [readsb card](integration-cards/wiedehopf__readsb.md), [Jammertest](dataset-cards/jammertest-data.md), [gnss-interference-monitor](../samples/gnss-interference-monitor/) |
| 3 | Detect spoofing and keep navigating | `search {"query":"spoofing","kind":"sample"}`; `search {"query":"spoofing detection","kind":"repo"}` | Samples: gnss-ins-ekf-outage, gnss-interference-monitor. Repos: S7AM1NA dataset, fit-gps-spoof-fix, GPSSpy (plus C-UAS noise: RFUAV, a UAV detection benchmark) | [gnss_lib_py card](integration-cards/stanford-navlab__gnss_lib_py.md), [project-repo](../templates/project-repo/) |
| 4 | Resilient timing for a sensor network | `concept {"id":"concept:timing"}`; `search {"query":"holdover clock"}` | gpsd, galmon, KiwiSDR, GNSSTk; DARPA ROCkN, IGS products, gnss-ins-ekf-outage | [gpsd](../catalog/repos/gitlab.com__gpsd__gpsd.md), [pyubx2 card](integration-cards/semuconsulting__pyubx2.md) - thin coverage, see decoder row 6 |
| 5 | Maritime USV in a spoofed area | `concept {"id":"concept:maritime-nav","fit":"high"}`; `search {"query":"ais spoofing"}` | ArduPilot, BlueOS, OpenCPN, pyais, AIS-catcher; C4ADS report, pyais, spoofing reviews, TEXBAT | [Stone Soup card](integration-cards/dstl__stone-soup.md), [maritime sets](dataset-cards/maritime-datasets.md) |
| 6 | Soldier navigation indoors / underground | `concept {"id":"concept:indoor-pedestrian","fit":"high"}`; `search {"query":"foot-mounted inertial zupt"}` | Crazyflie firmware, IEZ, PyShoe; OpenShoe, IEZ, ZUPT-aided INS, MPU6050 ZUPT | [PyShoe](dataset-cards/pyshoe.md), [FilterPy card](integration-cards/rlabbe__filterpy.md) |
| 7 | Swarm relative localization | `search {"query":"uwb relative localization"}`; `concept {"id":"concept:multi-agent","fit":"high"}` | Li et al. swarm ranging paper, ETH swarm relative localization, uwb-localization, UTIL dataset; Crazyflie firmware and cflib, drone-mesh-mapper, MOOS-IvP, EGO-Swarm | [GTSAM card](integration-cards/borglab__gtsam.md), [MILUV](dataset-cards/miluv.md) |
| 8 | C2 picture under EW | `neighbors {"id":"repo:snstac/pytak"}`; `concept {"id":"concept:situational-awareness","fit":"high"}` | OpenDroneID receiver, ATAK-CIV, FreeTAKServer, OpenTAKServer; QGroundControl, ArduRemoteID, Open Drone ID core, Stone Soup | [PyTAK card](integration-cards/snstac__pytak.md), [OpenTAKServer card](integration-cards/brian7704__opentakserver.md), [mavlink-to-tak-cot](../samples/mavlink-to-tak-cot/) |
| 9 | Detect and track drones | `concept {"id":"concept:counter-uas","fit":"high"}`; `search {"query":"remote id receiver","fit":"high"}` | ArduRemoteID, Open Drone ID core, OpenDroneID receiver, Stone Soup, ADSBCOT; RID (ESP32), DragonSync | [OpenDroneID receiver card](integration-cards/opendroneid__receiver-android.md), [Remote ID captures](dataset-cards/remote-id-droneid-captures.md) |
| 10 | Fixed-wing terrain navigation | `concept {"id":"concept:terrain-nav","fit":"high"}`; `show {"id":"repo:mzahana/tercom_nav"}` | python-tercom, tercom_nav, elevation_mapping_cupy, Rasterio, elevation | [tercom_nav card](integration-cards/mzahana__tercom_nav.md), [terrain-relative-nav-pf](../samples/terrain-relative-nav-pf/) |

## 6. Which SITL or dataset to start

Start from what is already on disk. Sizes are from the [dataset cards](dataset-cards/README.md).
The [sitl-docker](../samples/sitl-docker/) compose file pins ArduCopter 4.6.3 and PX4 v1.17.0 SIH
(check its README for what was run).

| Problem class | Start with | First command / file | Version trap |
|---|---|---|---|
| UAS navigates through GNSS loss (ArduPilot) | ArduPilot SITL from sitl-docker + [ardupilot-ekf3-source-switch](../samples/ardupilot-ekf3-source-switch/) | `docker compose up -d ardupilot` | 4.6.x: `SIM_GPS_DISABLE 1`; 4.7 / master: `SIM_GPS1_ENABLE 0` ([card](integration-cards/ardupilot__ardupilot.md)) |
| UAS with VIO or map-matching into PX4 | PX4 SIH from sitl-docker + [px4-sitl-gps-denial](../samples/px4-sitl-gps-denial/) | `docker compose up -d px4`; GPS loss via MAVSDK failure injection as in the sample, or `failure gps off` in the PX4 shell (`SYS_FAILURE_EN=1` first) | SIH target and `EKF2_AGP*` params differ between v1.17.0 and `main` ([card](integration-cards/px4__px4-autopilot.md)); `pip install mavsdk-grpc` |
| Visual geolocalization | [UAV-VisLoc](dataset-cards/uav-visloc.md) site 03 (2.0 GB) | [visual-geolocalization-lightglue](../samples/visual-geolocalization-lightglue/) | LightGlue with ALIKED, not SuperPoint (NC weights) |
| VIO drift | [EuRoC](dataset-cards/euroc-mav.md) vicon_room1 (6.04 GB) or [UZH-FPV](dataset-cards/uzh-fpv.md) (0.84 GB) | [evo card](integration-cards/michaelgrupp__evo.md) for scoring | EuRoC host rate-limits; it must already be on disk |
| Receiver jamming / spoofing | [Jammertest](dataset-cards/jammertest-data.md) VAARA (1.57 GB), [TEXBAT](dataset-cards/texbat.md) subset (8.8 GB) | [gnss-interference-monitor](../samples/gnss-interference-monitor/) `scorer.py` | S7AM1NA public sample is not a labelled attack |
| Phone / raw GNSS | [GSDC](dataset-cards/gsdc.md) taroz zip (2.76 GB), [UrbanNav](dataset-cards/urbannav.md) | [gnss-rinex-processing](../samples/gnss-rinex-processing/) | gnss-lib-py needs Python below 3.15 |
| INS holdover | [KITTI](dataset-cards/kitti.md) raw drive (1.2 GB), [NCLT](dataset-cards/nclt.md) (0.24 GB) | [gnss-ins-ekf-outage](../samples/gnss-ins-ekf-outage/) | FilterPy 2.0.0 API change |
| Terrain navigation | Copernicus DEM tiles for the AOI | [terrain-relative-nav-pf](../samples/terrain-relative-nav-pf/) | elevation 2.0 breaks 1.x commands; vertical datums differ |
| Radio ranging / swarm | [UTIL](dataset-cards/util-uwb-tdoa.md) (1.86 GB), [MILUV](dataset-cards/miluv.md) (3.2 GB) | [GTSAM card](integration-cards/borglab__gtsam.md) | - |
| Maritime | [Pohang](dataset-cards/maritime-datasets.md) navigation.zip (about 20 MB) | [project-repo](../templates/project-repo/) with an NMEA source | - |
| C-UAS awareness | [Remote ID captures](dataset-cards/remote-id-droneid-captures.md), [DroneRF](dataset-cards/drone-rf-datasets.md) | [stone-soup-tracking](../samples/stone-soup-tracking/) (sketch) | Stone Soup needs Python 3.11+ |
| MagNav | [MagNav challenge data](dataset-cards/magnav-challenge-data.md) (1.87 GB) | [magnav-quickstart](../samples/magnav-quickstart/) (unverified sketch) | Julia first-run compile; AFRL data agreement |

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
