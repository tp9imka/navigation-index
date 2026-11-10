# AGENTS.md

Guide for LLM coding agents (Claude Code, Cursor, Codex, Copilot...) using or extending this hub.

## Given a problem statement

For the EDGE internal hackathon, Challenge 2 "Autonomous Frontiers", read
[docs/challenge-2-autonomous-flight.md](docs/challenge-2-autonomous-flight.md) first (MCP: `read`
with `guide:challenge-2-autonomous-flight`). It narrows the hub to the rows, samples and guides
that fit an autonomous flight product and lists the rows to skip.

### Close-area A=>B (likely Day-1 task)

Use this block when the brief is "fly a drone from A to B in a close area, maybe with obstacles".

1. First 20 minutes: [docs/day1-close-area-intake.md](docs/day1-close-area-intake.md) - organiser
   questions in order, each answer => driver, sim, sample. Research behind it:
   [docs/research/close-area-nav/README.md](docs/research/close-area-nav/README.md).
2. Runnable baseline: [samples/close-area-arena](samples/close-area-arena/README.md) (status `ran`,
   synthetic inputs only). Starter loop for the team repo:
   [templates/flight-repo](templates/flight-repo/README.md): `make first-flight` flies it in the arena
   (planner + safety filter + estimator faults) and scores the log. `make first-flight-reloc` adds relocalization after a VIO jump; outside the hub use `make first-flight HUB=/path/to/hub`.
3. Send setpoints to a real platform: [templates/drone-adapter](templates/drone-adapter/README.md)
   and its [drivers table](templates/drone-adapter/drivers/README.md) (PX4, ArduPilot, Crazyflie,
   Tello; unrun, written from SDK docs).
4. Decoder rows 31 (obstacles), 32 (visual goal B) and 33 (indoor VIO loss) in
   [docs/problem-statement-decoder.md](docs/problem-statement-decoder.md); `decode` prints
   their runnable starters.
   Headline after the kill test: relocalization after VIO loss
   ([samples/close-area-relocalize](samples/close-area-relocalize/README.md)); every planner on
   every arena: [samples/close-area-benchmark](samples/close-area-benchmark/README.md); try it in
   the browser: [site/playground/](site/playground/index.html).
5. One-page summary: [docs/cheatsheets/close-area-a-to-b.md](docs/cheatsheets/close-area-a-to-b.md). Demo and
   pitch: [templates/demo-script-close-area.md](templates/demo-script-close-area.md),
   [templates/pitch/close-area-story.md](templates/pitch/close-area-story.md).
6. Day-1 tools, one entry command each (all synthetic; flow in the cheat sheet "Day-1 flow with the browser tools"):
   - Room => world JSON: `world_from_room.py rooms/hall_8x6.json` or `world_from_image.py <plan>.png --ref ...` in [close-area-arena](samples/close-area-arena/README.md#your-room-in-the-arena-ran-2026-11-10-synthetic).
   - Rank planners on that world: [site/solver/](site/solver/README.md) (Import world JSON, Your drone, Quick / Stress / Thorough, Pareto view, Recommend => `recommend.md`).
   - Fly the pick: `make first-flight PLANNER=bench:<id> WORLD=<file.json> ARM=<F0|F2>` in [flight-repo](templates/flight-repo/README.md#fly-what-the-solver-picks-benchid-in-a-world-file); F2 cannot pass gaps under ~1.4 m, use `ARM=F0` there.
   - Regression bar: `pack.py run packs/<name>.json` in [close-area-benchmark](samples/close-area-benchmark/README.md#scenario-packs).
   - People walking through: `run_predict.py --layouts 50 --seeds 0,1` in [close-area-moving-obstacles](samples/close-area-moving-obstacles/README.md) (VO gate PASS on held-out seed 1).
   - B is a marker at an unknown spot: `bench.py --layouts 20 --seed 0` in [close-area-explore](samples/close-area-explore/README.md) (frontier finds B in 43 % with B unknown; ask for a nominal B).
   - More planners: [thetastar](samples/close-area-planner-thetastar/README.md), [mppi](samples/close-area-planner-mppi/README.md), [hybrid-astar](samples/close-area-planner-hybrid-astar/README.md) (negative result); all are `bench:` ids.
   - Offline browser tools: `python3 tools/venue_kit.py prepare` then `verify` ([day-0 runbook](docs/day0-runbook.md#browser-tools-offline)).
   - How it was built: [docs/case-study](docs/case-study/README.md); live site: https://navigation-index.pages.dev/.

MCP-only clients: `read` serves `docs/**/*.md`, `templates/**/*.md` and `samples/<name>/*.md`
(README, CONTRACT, INTEGRATION), so every page above is reachable without file access.

Free-text search ranks a pasted problem statement poorly. Do this instead:

1. Run `python3 tools/query.py decode "<statement>"` (MCP: `decode`). It matches the statement
   against `docs/problem-statement-decoder.md` and returns 1-3 rows with approach, cards, samples
   to start from, risk and search keywords. Skim the doc to confirm the pick.
2. Open `samples/README.md` for the named samples: status (`ran` / `partial` / `sketch`),
   deps (`stdlib` / `venv` / `docker`), first command, key measured result. The same fields
   are in each `samples/<name>/sample.json` (`verified_status`, `deps`, `first_command`).
3. Quote numbers from `docs/evidence-matrix.md`, which marks real vs simulated inputs and
   labels superseded results (e.g. altpnt-integrity v1's 41.7 % availability, withdrawn by its
   v2). Never present a synthetic or SITL number as a field result.
4. Then search with the row's keywords (decode prints them), not the statement
   (`search "jammer localization sensor network TAK"` works; a paragraph of prose does not).
   This applies to `tools/query.py`, the MCP `search` tool and the site alike. An MCP client
   without file access can get the decoder's full text with the `read` tool
   (`guide:problem-statement-decoder`).

Install convention for samples: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
inside the sample folder, or the sample's Docker command. Never install into the global
interpreter. Deviations are listed in `samples/README.md`.
Run long commands (clone, venv install, first sample run) with stdin closed (`< /dev/null`) or in the background: in the Day-1 dry run a plain `git clone` hung past 120 s in an agent shell.

## Using the hub to answer a question

For resource constraints, read `docs/practical-readiness.md`. Search, concept and neighbors
accept `compute`, `hardware`, `offline`, `platform`, `validation`, `max_setup_minutes` and
`max_download_mb` (CLI: hyphens). An empty search lists only matching candidates. Unknown
values never satisfy a numeric budget or verified-offline filter. `readiness` is independent
of `verified_status`; cite its evidence and limitation. See `docs/starter-bundles.md` for
selective preparation and measured rehearsal receipts.

1. Start at `llms.txt` (map) and `INDEX.md` (concept tree + high-fit repos).
2. Pick a concept page in `catalog/concepts/` - it lists every repo, document, talk,
   dataset and sample tagged with that concept, high hackathon-fit first.
3. Open individual pages in `catalog/repos/` or `catalog/resources/` for summary,
   hackathon notes, GitHub metadata and graph links (related / referenced by).
4. For programmatic lookup use the CLI (stdlib Python, no installs):
   ```
   python3 tools/query.py search "uav satellite image matching" --kind repo --fit high
   python3 tools/query.py concept concept:terrain-nav
   python3 tools/query.py neighbors repo:px4/px4-autopilot --depth 2
   python3 tools/query.py show res:afrl-magnav-challenge-2020 --json
   python3 tools/query.py show sample:golden-demo
   ```
   or register the MCP server: `claude mcp add navigation-index -- python3 /abs/path/tools/mcp_server.py`.
   Tools: `search`, `decode`, `show`, `concept`, `neighbors`, `read` (MCP only: full markdown of a guide
   or sample README). A sample id `sample:<name>` maps to `samples/<name>/README.md`; a repo id `repo:owner/name` maps to
   `docs/integration-cards/owner__name.md` when a card exists, else `catalog/repos/owner__name.md`.
5. For working code start from `samples/README.md` - each sample says what ran, on which
   data, and what was only syntax-checked.
6. Deep dives that are not records: integration cards (`docs/integration-cards/`), dataset
   cards (`docs/dataset-cards/`), paper digests (`docs/paper-digests/`), landscape
   (`docs/landscape/`, incl. `blind-flight-teardown.md`), integrity and timing guides
   (`docs/integrity-monitoring.md`, `docs/timing-resilience.md`), weights licenses
   (`docs/model-weights-licenses.md`).

A second MCP server, `samples/llm-mission-agent/mav_mcp_server.py`, exposes vehicle tools
(state, nav health, takeoff, goto, mission, EKF source set) behind a geofence, altitude band,
mode allowlist, dry-run mode and command log. It was verified against SITL only; keep it there.

Do not clone indexed repos just to answer "what does X do" - the catalog has it. Clone
when you are going to build with it.

## Extending the hub

- Source of truth is JSON in `data/` (see `docs/SCHEMA.md`). Add records to the lane file
  that fits, or create `data/repos/<new-lane>.json`.
- Concept ids are a fixed vocabulary in `data/concepts.json`. Add a concept there first if
  nothing fits.
- Then run:
  ```
  python3 tools/enrich.py   # GitHub stars/license/last push via gh api (incremental)
  python3 tools/build.py    # regenerate catalog/, INDEX.md, graph/, index/, reports/
  ```
- Check `reports/quality.md`: "Referenced but not indexed" is the to-do list of repos
  other records point at but nobody indexed yet.
- A new sample needs `samples/<name>/sample.json` with `verified` (free text: what ran, when,
  on which interpreter and data), `verified_status` (`ran` | `partial` | `sketch`), `deps`
  (`stdlib` | `venv` | `docker`, for the first command), `first_command`, and the table fields
  `group`, `shows`, `input`, `runtime`, `key_result` (the `samples/README.md` table is
  generated from them); then its measured numbers in `docs/evidence-matrix.md` and a "Start
  from" entry in `docs/problem-statement-decoder.md`. When a newer run supersedes a published
  number, update `key_result` and the matrix in the same change and label the old number.
  Defects found in upstream code go in `docs/upstream-findings.md`; do not file them yourself. Tests must run under plain
  `python3 -m unittest` with no third-party packages (guard imports, `skipIf`).
- Never hand-edit generated files (`catalog/`, `INDEX.md`, `graph/graph.json`,
  `index/records.jsonl`, `reports/`).

## Scope and safety

In scope: navigation, localization, PNT resilience, autonomy, situational awareness,
defensive EW and counter-UAS detection. Out of scope: weapon terminal guidance,
targeting, offensive payloads. See `docs/export-control-and-ethics.md` before shipping
code that touches GNSS signal generation or defense end uses.
