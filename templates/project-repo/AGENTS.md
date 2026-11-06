# AGENTS.md

For coding agents (Claude Code, Cursor, Codex, Copilot) working in this repo during a 48h hackathon.

## Ground rules

- The demo path is sacred: `make test && make eval && make demo` must pass after every change you hand back.
- Keep the core stdlib-only (`src/navapp`). Optional deps go behind extras in `pyproject.toml`.
- Work through the interfaces in `src/navapp/interfaces.py` (PoseSource, NavFilter, IntegrityMonitor, Publisher).
  New sensor => new PoseSource. New estimator => new NavFilter. Do not reach across stages.
- Every number in README comes from `eval/metrics.py` output. Never type a metric by hand. If it cannot be
  measured, it reads `not measured`.
- Name thresholds and limits as constants. Few comments, only for non-obvious rationale.
- No secrets in the repo (`.env` is ignored; commit `.env.example`).

## Scope

Navigation, localization, PNT integrity, situational awareness, defensive EW detection. No targeting, no
terminal guidance, no offensive payloads. GNSS signal generation only to file or cable; never write code or
docs that radiate. Read the hub's `docs/export-control-and-ethics.md` before touching signal generation.

## Knowledge hub: navigation-index

Use it before searching the web or cloning repos.

- MCP (preferred): `claude mcp add navigation-index -- python3 /abs/path/navigation-index/tools/mcp_server.py`
  Tools: `search`, `show`, `concept`, `neighbors`.
- No MCP: read `/abs/path/navigation-index/llms.txt`, then
  `python3 /abs/path/navigation-index/tools/query.py search "<terms>" --fit high`.
- Before building a capability, check `docs/reference-stacks.md` (default, alternative, avoid) and
  `samples/` in the hub (each sample says whether it was run or is a sketch).

Typical lookups:

```
search "gnss spoofing detection" --kind repo --fit high
concept concept:gnss-interference
show repo:ardupilot/pymavlink
neighbors repo:snstac/pytak --depth 1
```

## Layout

| Path | What |
|---|---|
| `src/navapp/interfaces.py` | Typed boundaries; change with an ADR |
| `src/navapp/sim.py` | Synthetic clean / jam / spoof source |
| `src/navapp/filter.py` | Dead reckoning + absolute-fix filter (replace the maths, keep the interface) |
| `src/navapp/integrity.py` | Chi-square innovation monitor, NullMonitor baseline |
| `src/navapp/publishers.py` | CoT, MAVLink v1 STATUSTEXT, JSONL |
| `eval/metrics.py` | ATE, RPE, time to detect, false alarms, availability, misleading % |
| `tests/` | `python3 -m unittest discover -s tests` with `PYTHONPATH=src` |
