# AGENTS.md

Guide for LLM coding agents (Claude Code, Cursor, Codex, Copilot...) using or extending this hub.

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
   python3 tools/query.py show res:afrl-magnav-challenge --json
   ```
   or register the MCP server: `claude mcp add navigation-index -- python3 /abs/path/tools/mcp_server.py`.
5. For working code start from `samples/` - each sample says honestly whether it was run
   or is a syntax-checked sketch.

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
- Never hand-edit generated files (`catalog/`, `INDEX.md`, `graph/graph.json`,
  `index/records.jsonl`, `reports/`).

## Scope and safety

In scope: navigation, localization, PNT resilience, autonomy, situational awareness,
defensive EW and counter-UAS detection. Out of scope: weapon terminal guidance,
targeting, offensive payloads. See `docs/export-control-and-ethics.md` before shipping
code that touches GNSS signal generation or defense end uses.
