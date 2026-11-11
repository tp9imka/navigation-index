# Docs map

Use this page when you need to know which page under `docs/` answers your question, or the order
to read them in. Each table has the same columns: page, when to open it, what you get.

Every `docs/` page listed here is also a `guide` node in the index, so
`python3 tools/query.py search "<keywords>"`, the MCP server and the web UI in `site/` return
them next to repos and samples. Pages under `templates/` and sample files other than a README
are not index records: open them by path. Search with keywords, not a pasted problem statement:
for a statement, read the [decoder](problem-statement-decoder.md) first and search with its
row's keywords.

## Before the task (days to weeks)

| Page | Use it when | You get |
|---|---|---|
| [practical-readiness.md](practical-readiness.md) | You must fit compute, hardware, platform, budget or offline limits | Selection by actual compute, hardware, platform, budget and offline evidence; generated shortlist and limitations |
| [starter-bundles.md](starter-bundles.md) | You want one thing prepared and rehearsed before the task starts | One small receiver, simulation or vision bundle, with a rehearsal on a second laptop offline |
| [primer/](primer/README.md) | You need the vocabulary | Nine chapters, one cluster of the hub each, with the EW failure modes |
| [learning-paths.md](learning-paths.md) | You have a fixed amount of study time | Three study tracks by available time, built from indexed courses, talks and books |
| [competition-playbook.md](competition-playbook.md) sections 1-2 and 6 | You want to know what reviewers look for and what to prepare | Problem space map, and a prep checklist: datasets on disk, SITL images, template green |
| [landscape/](landscape/README.md) | You need to know what is already sold or funded | Vendors, funders, and a real past brief with seven solutions ([blind-flight-teardown.md](landscape/blind-flight-teardown.md)) |
| [export-control-and-ethics.md](export-control-and-ethics.md) | Before you pick a project | Scope limits, not legal advice. Read once |

## When the problem statement arrives

| Page | Use it when | You get |
|---|---|---|
| [problem-statement-decoder.md](problem-statement-decoder.md) | You have any problem statement | Brief decoder: wording table => 1-3 decoder rows, each with approach, stack, data, starting sample, risk and a one-line summary; a [full-brief routing table](problem-statement-decoder.md#route-a-full-brief-to-rows-and-first-pages) => rows and first pages |
| [first-three-hours.md](first-three-hours.md) | The row is picked and the clock runs | The first three hours, until a walking skeleton runs |
| [../samples/README.md](../samples/README.md) | You need code that already ran | Every sample with status, deps, first command and key measured result (generated from each `sample.json`) |
| [cheatsheets/](cheatsheets/README.md) | You want one page per brief family | Demo, first 2 hours, 3 citable numbers with input type, traps |

### Close-area A=>B

Use these when the brief is "fly a drone from A to B in a close area, maybe with obstacles"
(decoder rows 31, 32 and 33).

| Page | Use it when | You get |
|---|---|---|
| [first-day-intake.md](first-day-intake.md) | First 20 minutes after the brief | Questions for whoever set the task, in order; each answer => adapter driver, sim, samples, docs |
| [quickstart-first-flight.md](quickstart-first-flight.md) | First hour after the intake | Ordered script: clone, room => world JSON, Solver, `make first-flight`, score, scenario pack, offline fallbacks; each step with command, cwd, last line, wall time, gotchas |
| [research/](research/README.md) | You need the innovation story or which research round applies | Brief family => headline idea => kill test => status, both rounds |
| [research/close-area-nav/](research/close-area-nav/README.md) | You need the plan and the reasons | Planner, sim, localization and innovation lanes, recommended direction, kill test, licence traps |
| [research/innovation-prior-art/](research/innovation-prior-art/README.md) | The brief is long-range GNSS-denied instead | The earlier research round, now the fallback frame |
| [../samples/close-area-arena/](../samples/close-area-arena/README.md) | You need a runnable A=>B baseline and scorer | 2.5D arena, straight, A* + ESDF and freest_beam planners, estimator faults (status `ran`, synthetic inputs) |
| [../templates/flight-repo/](../templates/flight-repo/README.md) | You start the team repo | 20 Hz loop skeleton: adapter => nav health => planner => safety filter (mock only) |
| [../templates/drone-adapter/](../templates/drone-adapter/README.md) and [drivers](../templates/drone-adapter/drivers/README.md) | You must send setpoints to PX4, ArduPilot, Crazyflie or Tello | `pose()`, `ranges()`, `send_setpoint()` seam and a platform table (drivers unrun, written from SDK docs) |
| [../templates/presenting/live-demo-script-close-area.md](../templates/presenting/live-demo-script-close-area.md) and [../templates/presenting/close-area-story.md](../templates/presenting/close-area-story.md) | Demo and talk | Live-demo steps with a VIO fault, and the 3-minute pitch scaffold |

## While building

| Page | Use it when | You get |
|---|---|---|
| [reference-stacks.md](reference-stacks.md) | You must pick a library per capability | One default and one alternative per capability, plus what to avoid and why |
| [integration-cards/](integration-cards/README.md) | You are about to install or wire a repo | One card per repo: install, wiring, gotchas, license. Generated index grouped by capability, with fit, license and last push |
| [dataset-cards/](dataset-cards/README.md) | You need data | Checked sizes, formats and licenses |
| [paper-digests/](paper-digests/README.md) | You build on a paper | What the paper claims and what the code does |
| [integrity-monitoring.md](integrity-monitoring.md) | You need protection levels or fault detection | Protection levels, solution separation, Stanford diagram |
| [timing-resilience.md](timing-resilience.md) | The brief is about time or sync | Holdover, time attacks, timing builds |
| [autopilot-gnss-fault-handling.md](autopilot-gnss-fault-handling.md) | You need to know what the autopilot does under GNSS spoofing or jamming | PX4 EKF2 and ArduPilot EKF3 behaviour, read from pinned source and checked in SITL; what an external monitor must add |
| [model-weights-licenses.md](model-weights-licenses.md) | You ship a learned matcher or place recognition | Code license vs weights license |
| [competition-playbook.md](competition-playbook.md) sections 3-5 | You need ideas or a 48 h plan | Project ideas, reference architectures, 48 h plan |

## Presenting and provenance

| Page | Use it when | You get |
|---|---|---|
| [how-it-was-built.md](how-it-was-built.md) | You need to know how the hub was built and checked | Method, the kill tests that narrowed both headline ideas, fact-check error rates, figures derived from committed files |
| [cold-start-drill.md](cold-start-drill.md) | You want to know how long the first-flight path takes from a fresh clone | Two timed runs by one agent, every blocker and its fix |
| [evidence-matrix.md](evidence-matrix.md) | You quote any number | Every measured number across samples, with input type (real / SITL / synthetic). Superseded results (altpnt v1, the interference scorer before its real-data rework) are labelled |

## Maintaining the hub

| Page | Use it when | You get |
|---|---|---|
| [SCHEMA.md](SCHEMA.md) | You add or edit records in `data/` | The data model. Sample fields (`verified_status`, `deps`, `first_command`, `key_result`, `input`, `group`, `runtime`) are described in [../samples/README.md](../samples/README.md) |
| [reports/](reports/README.md) | You want past reviews, audits and fact checks | One line per report and which ones are superseded, including the [navigation audit 2026-11-09](reports/docs-navigation-audit-2026-11-09.md), [MCP security review](reports/mcp-security-review.md), [search ranking](reports/search-ranking.md) and [backlog additions](reports/backlog-additions.md) |
| [upstream-findings.md](upstream-findings.md) | A sample found a bug in upstream code | Reproduction, evidence, suggested report text and channel; nothing filed yet |

The top-level `reports/` folder is different: `reports/quality.md` there is generated by
`tools/build.py`.
