# AGENTS.md

Guide for LLM coding agents (Claude Code, Cursor, Codex, Copilot...) using or extending this hub.

## Given a problem statement

Free-text search ranks a pasted problem statement poorly. Do this instead:

1. Read `docs/problem-statement-decoder.md`. Match the statement's wording to 1-3 rows; each
   row names an approach, integration cards, datasets, a sample to start from and the main risk.
2. Open `samples/README.md` for the named samples: status (`ran` / `partial` / `sketch`),
   deps (`stdlib` / `venv` / `docker`), first command, key measured result. The same fields
   are in each `samples/<name>/sample.json` (`verified_status`, `deps`, `first_command`).
3. Quote numbers from `docs/evidence-matrix.md`, which marks real vs simulated inputs and
   labels superseded results (e.g. altpnt-integrity v1's 41.7 % availability, withdrawn by its
   v2). Never present a synthetic or SITL number as a field result.
4. Then search with keywords taken from the decoder row, not the statement
   (`search "jammer localization sensor network TAK"` works; a paragraph of prose does not).
   This applies to `tools/query.py`, the MCP `search` tool and the site alike. An MCP client
   without file access can get the decoder's full text with the `read` tool
   (`guide:problem-statement-decoder`).

Install convention for samples: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
inside the sample folder, or the sample's Docker command. Never install into the global
interpreter. Deviations are listed in `samples/README.md`.

## Using the hub to answer a question

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
   Tools: `search`, `show`, `concept`, `neighbors`, `read` (MCP only: full markdown of a guide
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
