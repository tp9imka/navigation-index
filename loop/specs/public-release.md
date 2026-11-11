# Spec: public release of Navigation Index

Status: approved by Ivan 2026-11-11 (decisions in section 1). Driver: Claude (review, gate, merge).
Workers: Kiro via farmout, at most 2 jobs at once, at most 4 worker processes each (loop/DRIVER.md CPU budget).
This file lives in loop/, which leaves the public tree in wave 5. Workers read it; they never edit it.

Inputs this spec is built from (verify before relying on any count, they were measured at HEAD 9642ecb):
- Positioning and community report (Fable, 2026-11-11), summarised in sections 2-4.
- Mention inventory (Fable, 2026-11-11), summarised in section 6 and the Touches column.
- Designs: Claude Design project "Navigation Index - public release"
  (https://claude.ai/design/p/4bf72617-9fb2-48d5-ba22-7b3a143c43e1, files Home, Results, Learn, Arena chrome,
  README hero). Durable copies: docs/design/public-release/*.png, tokens-and-components.css (the .dv-* rules
  are design-canvas chrome only, never ship them), arena-preview.js (the top-down preset renderer).

## 1. Decisions (Ivan, 2026-11-11)

| # | Decision |
|---|---|
| D1 | Name stays **Navigation Index**. The browser lab (Solver, Playground, Results) is branded **the Arena**. |
| D2 | Civil framing. Top level speaks "resilient PNT" and "airspace awareness". All content stays, including defense-context records, counter-UAS samples and the Ukrainian/Russian source lane (neutral title "Sources in Ukrainian and Russian"). The scope line (no targeting, no weapons guidance, no over-the-air transmission) and docs/export-control-and-ethics.md stay. |
| D3 | Git history is kept as is. No rewrite, no fresh repo. Old commits keep their old wording. |
| D4 | Visual direction: evolve the current look (site/showcase.css tokens, system fonts, light and dark). Home = the "2" design (arena hero + counters + tiles + one real result + agents box). |
| D5 | Licences: code Apache-2.0 (LICENSE), docs and data CC BY 4.0 (LICENSE-docs), exceptions in THIRD_PARTY.md. |
| D6 | Event material is reframed, not deleted, where it has community value (mapping in section 5). Event-only and internal material is removed. |
| D7 | `hackathon_fit` / `hackathon_notes` JSON keys keep their names for now. Every reader-facing label becomes "Quick-build fit" / "Build notes". A key rename with a shim is a later item. |
| D8 | Repo visibility is flipped by Ivan, not by this programme. Nothing here makes the repo public or posts anywhere. |

Out of scope: item 88c (regeneration, held for Ivan), launch posts, repo visibility, DOI minting.

## 2. Positioning (copy to use verbatim unless a wave says otherwise)

- Tagline: "Open navigation knowledge for drones and robots: a linked catalog, honest experiments, and a
  browser Arena that races 21 planners on your map."
- Home headline: "Draw a room. Race 21 planners. See who reaches B."
- GitHub About: "An open knowledge hub for navigation of small autonomous vehicles: 900+ open-source repos
  and 1000+ papers, datasets and standards linked in one graph, 60+ runnable samples that say what ran on
  which data, and a browser Arena that races 21 path planners on a map you draw. Every number is labelled
  synthetic, SITL or real. Readable by people and by coding agents (llms.txt, MCP server)."
- Topics: navigation, path-planning, obstacle-avoidance, drones, uav, px4, ardupilot, gnss, slam, robotics,
  pyodide, mcp-server.
- Honesty line: "Every number says what it ran on: synthetic, SITL or real. Arena results are synthetic
  simulation scored on truth. None is a flight result."
- Counts are never hand-typed in new prose: they come from INDEX.md (build.py) or
  samples/close-area-benchmark/results/matrix_0.json (planner count = 21 at 9642ecb). Where a static page
  needs a number, build.py writes it.

## 3. Audience and tone

Robotics students and early-career engineers, PX4/ArduPilot/Crazyflie developers, researchers comparing
planners, people working with coding agents. Lab notebook, not landing page. Short declarative sentences.
Plain hyphen only, `=>` for arrows. No "hackathon day", "judges", "organisers", "the team" (event sense),
"Day 1", "H+N" in reader-facing text except inside third-party facts (a real competition's name, a
teardown of someone else's hackathon repo).

## 4. Site design (wave 3 implements this)

Reference images: docs/design/public-release/. Tokens: keep site/showcase.css and site/style.css values;
add `--sitl` / `--sitl-bg` (light #6a3fb0 / #efe6fb, dark #c9a4ff / #2b2140) in both files and both dark
blocks.

Shared, every page (site/nav.js + site/nav.css own it):
- Top bar: brand mark + "Navigation Index"; nav groups **Arena** (Solver, Playground, Results) and
  **Index** (Search, Learn, Graph) with small mono group labels; GitHub link and theme toggle on the right;
  current page underlined with the accent. Phone: brand + Menu button (existing collapse behaviour).
- Input badges: `.badge.b-syn`, `.b-sitl`, `.b-real` (and `.b-pass`, `.b-fail`, `.b-neg` for verdicts), mono
  uppercase pill with a dot. One CSS definition in nav.css so every page has it.
- Footer: "Code Apache-2.0, docs and data CC BY 4.0", How to cite (CITATION.cff), Contribute
  (CONTRIBUTING.md), Scope and ethics (docs/export-control-and-ethics.md), How it was built
  (docs/how-it-was-built.md). nav.js injects it, like the nav.
- Arena pages (Solver, Playground, Results): a one-line honesty bar under the top bar, accent-bg, with the
  synthetic badge. Replaces today's per-page honesty paragraphs (keep their wording).

Pages:
- **Home** (index.html), design "2": kicker + headline + lead; buttons "Race planners on your map" (Solver)
  and "Search the index"; badge row + honesty sentence; right side an arena frame drawing glass_office_0
  from site/playground/presets with arena-preview.js logic and **replaying a committed Solver race** (new
  small JSON of per-planner paths captured from a real run, labelled synthetic, with its source command;
  if no paths can be captured honestly, show the static map and say "map preview", never invented
  paths). Counters strip (4, from build.py), four tiles (Solver, Playground, Results, Search and Learn),
  "One real result, verdict included" section (Solver Quick table from
  site/solver/results/quick_random_0.json + the kill-test card), agents box with the MCP one-liner,
  footer. Phone layout per design 2b.
- **Results** (site/results.html; site/showcase.html becomes a redirect stub to it): honesty bar, header
  "What we measured, and what failed.", filter chips (All, Pass, Fail, Negative, Benchmark), six cards
  (safety filter FAIL, relocalization narrowed, VO gate PASS, find B limit, Hybrid A* negative, benchmark).
  Every card: verdict badge, input badge, numbers with 95 % Wilson interval bars **computed from the
  committed JSON** (no illustrative bars), source link. Below: existing replays (tabs Kill test,
  Relocalization, Side by side) and sample gallery with input badges.
- **Learn** (site/learn.html, written by tools/build.py so counts stay true): primer chapters 1-9 in order,
  cheat sheets as chips with civil titles (section 5), preview card, card counts (integration, dataset,
  paper digests), guides row (Brief decoder, Quickstart: first flight, Competition playbook). Links open
  the existing doc page view (site/ search page view) or GitHub.
- **Solver / Playground**: bodies unchanged. Add honesty bar, page header (kicker "Arena / Solver",
  one-sentence job as h1, primary action on the right), and on the Solver a 4-step strip (Map, Sweep,
  Race, Result) that highlights the section in view. Phone: the strip becomes a segmented control.
- **Search** (site/index.html + site/app.js): labels only. "Hackathon fit" => "Quick-build fit",
  "Hackathon notes" => "Build notes"; samples show their input badge in result rows.
- **Graph**: only the shared nav and footer.

Checks for wave 3: node tests (site/test_nav.mjs updated for the groups and footer), phone width 390 with
no horizontal scroll on every page (existing measure scripts), tools/check_deploy.py page list updated
(results.html, learn.html, showcase redirect), screenshots of every page in both themes committed under
site/screenshots/ (replace the stale showcase-* ones).

## 5. Reframe and rename map (wave 2 implements this)

| Now | Becomes | Notes |
|---|---|---|
| docs/challenge-2-autonomous-flight.md | removed | its "words in the brief => rows" table moves into docs/problem-statement-decoder.md |
| docs/problem-statement-decoder.md | kept at the same path, titled "Brief decoder" | path kept: query.py DECODER_DOC, MCP, tests, decode_eval, 55 inbound links. Column "Pitch" => "One-line summary" with query.py decoder_rows + DECODE_FIELD_W updated together |
| docs/day1-quickstart.md | docs/quickstart-first-flight.md | |
| docs/day1-close-area-intake.md | docs/first-day-intake.md | "organisers" => "whoever set the task" |
| docs/day0-runbook.md | docs/first-three-hours.md | anchor #browser-tools-offline must survive (bundles.json, test_manifest.py) |
| docs/day1-dry-run.md + docs/day1-drill-2026-11.md + docs/drill-2026-11/ | docs/cold-start-drill.md + docs/cold-start-drill/ | one page; blockers table kept |
| docs/hackathon-playbook.md | docs/competition-playbook.md | "What judges reward" => "What reviewers look for"; strip defense-judge wording |
| docs/case-study/ | docs/how-it-was-built.md (+ docs/how-it-was-built/figures/) | method, kill tests, fact-check error rates; keep benchmark_heatmap.svg and kill_test_intervals.svg; drop commit_timeline.svg and every loop/ input of make_figures.py |
| docs/superpowers/, docs/hypotheses/research-agent-prompt.md | removed | internal |
| templates/pitch/ | templates/presenting/ | judge drills => hard-questions.md (merge the two) |
| templates/demo-script.md, demo-script-close-area.md | templates/presenting/live-demo-script.md (+ close-area variant) | |
| templates/team-roles-and-48h-plan.md, judging-self-assessment.md, submission-checklist.md, post-hackathon-retro.md, risk-register.md, threat-model.md, adr.md, pitch-deck-outline.md | templates/competition-kit/ (retro.md, self-assessment.md, ...) | wording: "event", "reviewers" |
| tools/venue_kit.py, tools/test_venue_kit.py | tools/offline_browser_kit.py + test | bundles.json, test_manifest.py, docs, .gitignore, zip name updated together |
| "Hackathon fit", "Hackathon notes" labels | "Quick-build fit", "Build notes" | build.py, query.py help, mcp_server.py schema text, card_index.py, site/app.js, docs/SCHEMA.md; keys unchanged (D7) |
| Cheat-sheet titles | civil titles | counter-uas-remote-id => "Airspace awareness: counter-UAS detection and Remote ID"; jammer-ew-map => "Jamming detection, localization and maps"; file names unchanged |
| README "defense lens", llms.txt header | civil framing (D2) | build.py llms template edited by hand (check_links does not read llms.txt) |
| data/repos close-area-planning.json:268, guidance-planning.json:36, data/resources/loop-13.json:75 | employer and "local judges" wording removed | facts kept |

Every rename updates all inbound links (grep the old basename across the tree, generated files excluded,
then rebuild), guide ids referenced by hand (AGENTS.md, mcp_server.py, tools/search_queries.json,
tools/test_mcp_server.py) and heading anchors referenced elsewhere (check_links strips `#`, so grep for
`old-file.md#`).

## 6. Hygiene rules (wave 1 builds the checker, every wave must pass it)

tools/check_public.py (stdlib) fails on any tracked, non-generated file matching:
- the employer: `\bEDGE\b` (case-sensitive), "EDGE Group", "Autonomous Frontiers", "Challenge 2" (event sense:
  any "challenge 2"/"challenge-2" outside third-party competition names, allow-list by path:line);
- `/Users/`, `/home/<name>/` machine paths (allow-list placeholders like site/test_nav.mjs `/Users/x/`);
- `loop-[0-9]+[a-z]?` wave tags outside loop/;
- tooling words "farmout", "Kiro", "Codex lane", "Ivan" (allow-list third-party authors in data/resources);
- event framing in reader-facing text: "hackathon day", "on the day", "Day 1", "Day-1", "day1", "organiser",
  "judges" (allow-list third-party facts by path:line, with a reason column).
Output: path:line:term, exit 1 on any hit; `--json`; allow-list in tools/public_allowlist.json with a reason
per entry. Unit test with fixtures. CI step in .github/workflows/check.yml and in the local gate.
Generated files (catalog/, INDEX.md, llms.txt, graph/, index/, reports/, site/data) are checked after a
rebuild, not allow-listed.

## 7. Waves

Binding order: W1 before W2 (W2 needs the checker); W3 runs in parallel with W1 (disjoint paths); W4 after W2
and W3; W5 last. Each wave is one or two Kiro jobs. Driver gate per wave: scratchpad gate.sh +
`python3 tools/check_public.py` (from W1 on; warn-only mode until W2 lands, strict after) + CI green after push.

| Wave | Job | Touches (do not overlap a parallel job) | Deliverable |
|---|---|---|---|
| W1 | legal + data + checker | LICENSE, LICENSE-docs, NOTICE, THIRD_PARTY.md, tools/check_public.py, tools/test_check_public.py, tools/public_allowlist.json, .github/workflows/check.yml (one step), samples/relative-nav-benchmark (GT files => fetch on demand), samples/two-source-integrity-vpair, samples/e2e-visual-nav-vpair, samples/osint-jamming-map/out/adsb-*.jsonl, the 11 result files with machine paths, samples/swarm-coop-real-uwb/miluv_io.py (MIT notice) | licences, removed redistributed data with fetch paths and READMEs updated, checker in warn mode listing every current hit, path scrub done |
| W3 | site (parallel with W1) | index.html, site/nav.js, site/nav.css, site/showcase.html (stub), site/results.html (new), site/learn.html (via tools/build.py write_learn), site/showcase.css, site/style.css, site/app.js (labels), site/solver/index.html + solver.css (frame only), site/playground/index.html + playground.css (frame only), site/test_nav.mjs, tools/check_deploy.py page list, site/screenshots/ | section 4 |
| W2 | docs sweep (two jobs, split by folder) | 2a: docs/ (renames, reframes, employer lines, loop-NN tags, civil framing), docs/SCHEMA.md, data/repos + data/resources prose fixes. 2b: templates/, samples/*/README.md + code comments, tools/ (build.py strings, query.py, mcp_server.py, card_index.py, tests, search_queries.json), AGENTS.md, README.md (minimal: links and framing only; full rewrite is W4), llms template | section 5 + checker strict and clean |
| W4 | README + community | README.md (rewrite per blueprint), AGENTS.md top, CONTRIBUTING.md, CODE_OF_CONDUCT.md (Contributor Covenant 2.1 full text), SECURITY.md, CITATION.cff, CHANGELOG.md, .github/ISSUE_TEMPLATE/*, .github/pull_request_template.md, tools/capture_hero.mjs + docs/design/hero.gif (headless Chrome frames => ffmpeg; ffmpeg is at /opt/homebrew/bin) | public README and community files; planner count from matrix_0; 25 samples' `input` filled |
| W5 | driver only | loop/ moved out of the tree to the private vault (Projects/navigation-index/loop), final checker run, rebuild, size report (results JSON over 1 MB listed; compression is a separate decision for Ivan) | clean tree |

README blueprint (W4): title, tagline, shields (CI, licence code, licence docs, live demo), hero GIF, three
links (Try the Solver, Draw your own room, Search the index), honesty quote, quickstart (stdlib only: clone,
`python3 -m http.server 8000`, a query.py search, the MCP one-liner), What is in here (five offers), The
Arena (model in one table: 2.5D point mass, 50 Hz double integrator, ray-cast range fan, sensor presets,
VIO faults; what it is not), The benchmark (heatmap figure, "reference implementations, untuned, PRs
welcome: a planner PR runs the full matrix and commits the JSON"), Catalog and deep dives, Samples
(verified_status / input contract), Templates (flight-repo first; drone drivers unrun), For coding agents,
Honest limits (bullets from the Fable report), How it was built (one paragraph, links the fact-check
reports and how-it-was-built.md), Contributing, Licence, How to cite. Not mentioned: loop/, farmout, Kiro,
Claude Code as build tooling, event days, the employer.

## 8. Acceptance (programme done)

- tools/check_public.py strict: 0 hits outside the allow-list; every allow-list entry has a reason.
- `grep -rnw EDGE --exclude-dir=.git .` returns nothing that names the employer.
- Gate green: build ("dangling: 0 bad concepts: 0"), check_links broken: 0, search_eval --parity,
  decode_eval, sample tests, readiness, MCP tests, offline-kit tests, node tests, check_public.
- CI green on main, deploy-smoke green, live site shows the new Home, Results, Learn on Cloudflare.
- LICENSE, LICENSE-docs, THIRD_PARTY.md present; no NC-licensed ground truth or raw ADS-B reports tracked.
- loop/ is not in the tree.
- Ivan reviews the live site and README before flipping visibility (D8).
