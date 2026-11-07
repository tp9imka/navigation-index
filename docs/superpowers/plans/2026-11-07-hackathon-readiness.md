# Hackathon readiness implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development to implement the independent tasks below. The user approved the review suggestions and authorized implementation and push on 2026-11-07.

**Goal:** Help a team choose and reproduce a suitable navigation stack with the hardware, time and connectivity available.

**Architecture:** Extend the existing stdlib Python builder, CLI and MCP server plus the static browser UI. Keep curated readiness in `data/readiness.json`, propagate it through generated records, and provide selective offline bundles with verifiable receipts. Expand the deterministic decoder and add recording/debugging catalog entries.

**Tech stack:** Python standard library, browser JavaScript/CSS, JSON and Markdown. No new application framework.

**Spec:** The five accepted suggestions in the repository review: constraint search; three offline bundles; broader decoder; consistent limitations/readiness; recording/debugging tools.

## Global constraints

- Never hand-edit generated catalog, indexes, graph, quality report or site data.
- Preserve unknown values; never turn missing evidence into a successful verification or an estimated measurement.
- Keep navigation work within the repository's existing scope; samples involving vehicles remain simulation/replay examples.
- Tests must run with stdlib Python; optional libraries may be guarded.
- Workers share one checkout. Each owns the files listed below, preserves others' changes, and leaves commits to the coordinator.
- Report observations to the coordinator; workers never write the shared observation log.

## Shared readiness contract

`data/readiness.json` maps record id to an object. Records and `show` expose that object as `readiness`; site nodes expose it as `rd`. Keys: `compute` (`cpu`, `gpu`, `optional-gpu`, `unknown`); `hardware` (`none`, `optional`, `required`, `unknown`); `offline` (`verified`, `cache-required`, `unknown`); `setup_minutes` (nonnegative number or null); `download_mb` (nonnegative number or null, dataset download only); `platforms` (list of tested OS/architecture labels); `validation` (`integrated`, `components`, `unverified`); `limitation` (one plain sentence); `evidence` (list of repo-relative source paths). Inline record readiness overrides curated values. Unknown defaults are explicit for samples.

Search options: `compute`, `hardware`, `offline`, `platform`, `max_setup_minutes`, `max_download_mb`, `validation`. CLI uses hyphens. Numeric ceilings exclude unknown values. Unset filters preserve existing results. Browser filters persist in the URL and copy to CLI/MCP.

## Review focus

Unknown readiness must not pass a numeric budget or a verified-offline filter. Saved browser links and copied CLI/MCP filters must agree. Offline receipts must reflect actual command exit status, not cache presence alone. New decoder cues must not break established air/timing briefs. Generated pages and human guidance must agree.

### Task 1: Readiness source and query interfaces (coordinator)

- [x] Add failing tests for defaults, overrides, validation and numeric/enum filtering.
- [x] Implement readiness loading, source validation and propagation in builder, catalog pages and site data.
- [x] Add CLI and MCP filters with tests for invalid input and missing evidence.
- [x] Curate evidence-backed metadata for the practical shortlist; document the schema.

### Task 2: Browser constraint search (UI worker)

Own `site/app.js`, `site/index.html`, `site/style.css`, `site/README.md`, and a focused JS verification script if needed. Consume `rd` above. Expose enum/platform/budget filters, readable readiness/limitations on results and starter kits, shareable URLs and matching CLI/MCP copy actions. Verify realistic fixtures, unknown handling and existing search parity.

### Task 3: Selective offline bundles (offline worker)

Own `templates/offline-kit/*` and `docs/starter-bundles.md`. Add three small selective bundle definitions for receiver-log replay, vehicle simulation and visual localization. Include prepare/verify/rehearse commands, explicit weights/cache requirements, measured receipts, fallback artifact instructions and a second-laptop checklist. Tests cover selection, missing/corrupt caches and failed rehearsal. Run a practical lightweight replay when feasible; heavy paths stay explicitly unverified until executed.

### Task 4: Decoder and consistency (decoder worker)

Own decoder-related code in `tools/query.py` (only the decoder section, coordinate with coordinator), `tools/decode_eval.json`, `tools/decode_eval.py`, `docs/problem-statement-decoder.md`, and related decoder guidance. Add pedestrian/phone indoor wayfinding, offline road routing, obstacle replanning briefs, prioritize explicit platforms, and repair stale UGV/timing gap statements. Add independent regression statements and preserve existing evaluation performance.

### Task 5: Recording/debugging lane and integration (coordinator)

- [x] Verify MCAP, Rosbags and Rerun using primary sources; add source records and integration cards with limitations and licensing checked from upstream.
- [x] Add a tiny deterministic shared recording/replay example and document what actually ran.
- [x] Link starter bundles and constraint search from README, runbook and agent instructions.
- [x] Regenerate all derived outputs, run existing CI checks and focused new tests, inspect final diff, obtain a fresh review and fix material findings. Commit and push follow this verified snapshot.

## Execution ledger

- Start: clean checkout at `d6a4a7a`, synchronized with origin/main. Working on `codex/hackathon-readiness-20261107` in the user-supplied folder.
- Ruling: use a branch in the supplied clean checkout; the user's request authorizes implementation and push, so no additional confirmation is needed.

- Verification: all 51 aggregate checks passed after final regeneration; decoder 51/51 real cases and 10/10 negative controls, browser constraint tests 10/10, bundle tests 15/15. Browser interactions confirmed CPU/hardware/download and verified-offline filters.
- Review: task reviews and final integration review completed; fixed short-brief rejection, unrelated photography matches, strict byte-budget rounding, fresh LightGlue dependency closure, and live budget input handling.
- Evidence limits: receiver replay ran on seven real logs with networking available; MCAP replay ran under network denial on one prepared Mac. Heavy SITL/vision and a second laptop were not rehearsed.
