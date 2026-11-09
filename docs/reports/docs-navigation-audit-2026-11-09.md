# Docs and navigation audit (loop-29, read-only)

Date 2026-11-09. Checkout at commit `9bd82eb`, clean tree before and after. Only this file was
written. No repo file was changed and `tools/build.py` was not run.

Method: a cold agent is assumed to have file access plus the CLI, or MCP access only. Every count
below comes from a command run in this checkout. The command is next to the number or in the
appendix. All inputs are the hub's own files (no vehicle, no SITL). Read-only tools that were run:
`tools/query.py`, `tools/mcp_server.py` (stdin JSON-RPC), `tools/check_links.py`,
`tools/decode_eval.py`, `tools/search_eval.py`.

## Key result

The decoder routes problem statements well and routes how-to questions badly.

- `python3 tools/decode_eval.py`: hit@1 1.00 on all 59 eval statements, including 8 of 8
  close-area statements.
- On the 12 Day-1 questions below, `decode` picks a correct row confidently for 6 of 12. For 4
  of those 6 (rows 31, 32, 33), the "start from" text says "sample pending:
  samples/close-area-arena". That sample exists and has status `ran`. So decode alone points to
  a runnable starter for 2 of 12 questions (the two long-range ones).
- The asset that answers "how do I send setpoints to PX4 / ArduPilot / Crazyflie"
  ([templates/drone-adapter/drivers/README.md](../../templates/drone-adapter/drivers/README.md)) has
  three problems. It is not a search record. It is named in none of AGENTS.md, llms.txt,
  docs/README.md, the Challenge 2 page or the decoder (0 mentions each, `grep -c`). The MCP
  `read` tool refuses its path.

## 1. Cold-start walkthroughs

A hop is one file opened or one tool call. "Answer" is the file that actually answers the
question. Decode results come from `python3 tools/query.py decode "<question>"`. Search results
are the top 5 or 6 hits of `python3 tools/query.py search "<keywords>" --limit 5`.

| # | Question | Path an agent takes | Hops | Dead ends | Answer |
|---|---|---|---|---|---|
| 1 | Drone A to B with obstacles on a Crazyflie | AGENTS.md => challenge-2 page (update box) => `decode` row 31 (score 22.2) => its search line => close-area-arena at rank 2 | 5 | Row 31 "start from" says no starter exists (stale). The Crazyflie driver in templates/drone-adapter is not found: `search "crazyflie"` returns 6 upstream records and no template. | [samples/close-area-arena/README.md](../../samples/close-area-arena/README.md) + [templates/drone-adapter/drivers/README.md](../../templates/drone-adapter/drivers/README.md) (Crazyflie row). The second file needs llms.txt => templates/README.md => drone-adapter => drivers (3 hops from llms.txt, by BFS over links). |
| 2 | How do I send velocity setpoints to PX4 / ArduPilot | `decode` => low confidence (rows 31 / 33, scores 3.2 / 2.1) => `search "velocity setpoint offboard PX4"` => upstream repos (ARK example, MAVSDK-Python, px4_ros_com) | 4-6 | `search "drone adapter send_setpoint"` and `search "drone-adapter"` return 0 template hits. MCP `read templates/drone-adapter/README.md` => "not readable". | [templates/drone-adapter/drivers/README.md](../../templates/drone-adapter/drivers/README.md) platform table (MAVSDK `set_velocity_ned`, GUIDED `SET_POSITION_TARGET_LOCAL_NED` masks 1479 / 3527, cflib, Tello). Unrun drivers, written from docs. |
| 3 | Which planner should I start with | `decode` => row 31 (9.1), but row 13 counter-UAS is second (6.3) => close-area README "Recommended direction" => 01 section 5 | 4 | `search "which planner"` returns TARE, OMPL, CMU env, FAR, EGO: research planners, none of them the hub's pick. close-area-arena ships only `straight`. The better `freest_beam` baseline lives inside `run_faults.py` and CONTRACT.md, and no index names it. | [docs/research/close-area-nav/01-planning-and-mapping.md](../../docs/research/close-area-nav/01-planning-and-mapping.md) section 5 + arena results |
| 4 | How do I score a run | `decode` => low confidence, rows 6 and 19 (timing, critical infrastructure): wrong family => `search "score run time to goal collisions scorer"` => close-area-arena rank 1 | 4 | MCP agent: CONTRACT.md "Scorer fields" is refused by `read`. Judge-side scoring sits in 02 section 3 and 06, and no scoring query finds 06 (`search "judging criteria score"` top 5 has no close-area doc). | [samples/close-area-arena/CONTRACT.md](../../samples/close-area-arena/CONTRACT.md) (scorer fields) + [06-task-phrasing-survey.md](../../docs/research/close-area-nav/06-task-phrasing-survey.md) (how events score) |
| 5 | What if VIO is lost indoors | `decode` => row 33 (17.2) => 03 sections 4-6 | 3 | Row 33 "start from" says no starter exists, but close-area-arena now has `estimator.py` + `faults.py` (jump, bias, dropout, overconfident) with results. Cheat sheets README maps "indoors" to the dismounted sheet. | [03-close-area-localization.md](../../docs/research/close-area-nav/03-close-area-localization.md) + [close-area-arena "Estimator and faults"](../../samples/close-area-arena/README.md#estimator-and-faults-ran-2026-11-09-synthetic) |
| 6 | What is our innovation story | `decode` => "no decoder row matched" => `search "innovation story headline"` => 07, 05, innovation-prior-art README, close-area README | 4-6 | Three pages give different headlines: challenge-2 section 5 (drag as a virtual velocity sensor for long range), close-area README (integrity-aware safety filter, narrowed by 07), innovation-prior-art README. Nothing says which one wins for which brief, except one sentence near the end of challenge-2 section 5. | [docs/research/close-area-nav/README.md](../../docs/research/close-area-nav/README.md) "Recommended direction" + "Narrowed after 07" |
| 7 | Goal is an AprilTag | `decode` => row 32 (16.4) => 03 section 3 | 3 | Row 32 "start from" says pending. Its search line returns AprilTag, apriltag_ros, 06, Clover, EGO-Swarm, and doc 03 is not in the top 5. | [03-close-area-localization.md](../../docs/research/close-area-nav/03-close-area-localization.md) section 3 |
| 8 | What can run on a Mac without CUDA | `decode` => low confidence (rows 10, 28: swarm, phone) => `search "Mac without CUDA"` => cuVSLAM, Genesis, LightGlue-ONNX, cuVSLAM paper, fast_gicp (all CUDA-centred) => `search "apple silicon cpu only"` => PX4 macOS docs, doc 02 | 5-7 | The readiness filter `--platform macos-arm64 --kind sample` returns 5 samples and `--compute cpu` returns 7. close-area-arena is in neither, although it ran on an M3 Max: 39 of 48 samples have `compute:unknown`. | Close-area README "License traps" line ("Only nvblox needs CUDA") + [02-sims-platforms-competitions.md](../../docs/research/close-area-nav/02-sims-platforms-competitions.md) (gz Harmonic native on Apple Silicon) |
| 9 | What licences block commercial use | `decode` => no row => `search "license commercial use non-commercial weights"` => model-weights-licenses rank 1 | 3 | Close-area licence traps (SUPER, IPC with no LICENSE file) sit only in the close-area README and doc 01, and `search "no license file read-only"` does not surface them. | [docs/model-weights-licenses.md](../../docs/model-weights-licenses.md) + challenge-2 section 6 + close-area README "License traps" |
| 10 | What did past competitions score | `decode` => no row => `search "past competitions scoring IMAV"` => IMAV 2026 rulebook, doc 06 | 3 | None for close area. A long-range brief needs [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md), which this query does not return. | [06-task-phrasing-survey.md](../../docs/research/close-area-nav/06-task-phrasing-survey.md) (IMAV 1.0 / 0.7 / 0.4 autonomy multipliers) + [02](../../docs/research/close-area-nav/02-sims-platforms-competitions.md) section 3 |
| 11 | Navigate a small drone 10 km without GNSS using the camera | `decode` => row 1 (23.0), start-from lists 9 samples => samples/README.md => e2e-visual-nav-vpair | 3 | None. Row 1 lists 9 samples with golden-demo first. The challenge-2 page lists e2e-visual-nav-vpair first, so the order differs. | [samples/e2e-visual-nav-vpair/README.md](../../samples/e2e-visual-nav-vpair/README.md) + [evidence-matrix.md](../../docs/evidence-matrix.md) |
| 12 | Fixed-wing 30 km with GPS jammed and spoofed | `decode` => row 27 (28.7) => golden-demo-fixedwing | 2-3 | None. | [samples/golden-demo-fixedwing/README.md](../../samples/golden-demo-fixedwing/README.md) + decoder gap note on rows 15/18/25/27 |

Tally:

- Decode confident and on the right row: 6 of 12 (Q1, Q3, Q5, Q7, Q11, Q12).
- Decode low confidence: 3 of 12 (Q2, Q4, Q8). Decode no row: 3 of 12 (Q6, Q9, Q10).
- Questions whose best hub file is unreachable through MCP `read`: 3 of 12 (Q1 and Q2 need
  templates/, Q4 needs CONTRACT.md).
- Long-range questions take 2-3 hops. Close-area questions take 3-7 hops and hit at least one
  stale "pending" statement each, except Q6, Q9 and Q10.

The decoder is built for problem statements. On Day 1 the agent will mostly ask how-to
questions, and for those nothing routes to a guide.

## 2. Structural findings

### 2.1 Orphan docs

The script walked 440 hand-written `.md` files plus llms.txt. It excluded catalog/, reports/,
index/, graph/, site/data, loop/, `.venv` and `results/`. It resolved every relative markdown
link and counted inbound links per target under docs/, templates/ and samples/ (435 targets).

- No inbound link from any hand-written file: 12. These are
  [docs/reports/backlog-additions.md](../../docs/reports/backlog-additions.md),
  [docs/reports/mcp-security-review.md](../../docs/reports/mcp-security-review.md),
  [docs/reports/search-ranking.md](../../docs/reports/search-ranking.md),
  [docs/superpowers/plans/2026-11-07-hackathon-readiness.md](../../docs/superpowers/plans/2026-11-07-hackathon-readiness.md),
  [templates/project-repo/CLAUDE.md](../../templates/project-repo/CLAUDE.md), and 7 generated `out/`
  summaries under samples/blind-flight-bench and samples/thermal-geolocalization (acceptable).
- No inbound link from any README, INDEX.md, llms.txt or AGENTS.md: 14 (the 12 above plus 2).
- `python3 tools/check_links.py`: 25853 relative links, 0 broken. Link hygiene is good. The
  problem is discoverability.
- docs/README.md links `reports/` as a directory. docs/reports/ has no README, so an agent gets a
  bare directory listing of 11 files.

Reachability by BFS over markdown links (shortest hop count):

| Target | from llms.txt | from docs/README.md | from README.md | from AGENTS.md |
|---|---|---|---|---|
| close-area-nav/README.md | 1 | 2 | 2 | unreachable |
| samples/close-area-arena/README.md | 1 | 2 | 2 | unreachable |
| templates/drone-adapter/README.md | 2 | 3 | 2 | unreachable |
| templates/drone-adapter/drivers/README.md | 3 | 4 | 3 | unreachable |
| templates/demo-script-close-area.md | 4 | 5 | 4 | unreachable |
| templates/pitch/close-area-story.md | 3 | 4 | 3 | unreachable |

AGENTS.md has 0 markdown links. It names paths in backticks, so the BFS reaches nothing from it.
An agent with file access copes. A link-following client or the site page view does not.

### 2.2 Duplicated or competing entry points

These pages each say, in their own words, "start here" for a problem statement (from
`grep -rniE "start here|read first|entry point"` plus reading):

1. AGENTS.md => docs/challenge-2-autonomous-flight.md first.
2. llms.txt => challenge-2 ("read first") and decoder ("start here") as two neighbouring
   entry points.
3. README.md "Four hops" => decoder first. It never names Challenge 2 or close-area
   (`grep -ci challenge README.md` = 0).
4. docs/hackathon-playbook.md line 25, "Start here when the statement drops".
5. docs/cheatsheets/README.md, "pick one in 30 seconds". It has no close-area row.
6. docs/day0-runbook.md, "the first three hours", with 0 close-area mentions.
7. docs/research/close-area-nav/README.md, which challenge-2's update box says to "start from".

Items 1, 2 and 7 agree. Items 3 to 6 predate the close-area update and route a close-area brief
elsewhere: cheat sheets send "indoors" to dismounted-indoor-tunnel, and day0 sends it to the
long-range rubric.

### 2.3 Stale pointers whose target now exists

From `grep -rnoiE "none yet|pending|not written yet|sample pending|does not exist in the hub yet|nothing in ..."`:

| File:line | Says | Fact now |
|---|---|---|
| docs/problem-statement-decoder.md rows 31, 32, 33 (lines 125-127), "Start from" | "No runnable ... starter in the hub (sample pending: samples/close-area-arena)" | close-area-arena exists, `verified_status: ran`, with an estimator-and-faults run. `decode` prints this text verbatim. |
| docs/problem-statement-decoder.md lines 196-197 (gaps) | "nothing in them was run. A matching sample is pending (samples/close-area-arena)" | Same as above. |
| docs/problem-statement-decoder.md row 31 risk | "Nothing in the close-area docs was run" | Still true of the docs, but the arena ran. Reword to "docs not run; arena baseline ran, synthetic". |
| docs/research/close-area-nav/README.md line 8 | "Nothing in these docs has been run." | Same. No link to the arena from the synthesis. |
| templates/pitch/close-area-story.md line 8 | "nothing in the close-area lane has been run" | The arena ran. `samples/close-area-safety-filter` (line 9) still does not exist (`ls`), so that pointer is accurate. |
| samples/close-area-arena/sample.json `verified` | "templates/drone-adapter was not present in this checkout" | It is present now. This is a historical record, so add a follow-up note rather than rewrite it. |
| samples/close-area-arena/INTEGRATION.md cheat-sheet line | "none yet: start at close-area-arena" | The proposed line was never applied to docs/cheatsheets/README.md. |
| site/README.md "Data" and "Verification" | "about 1.3 MB for 1287 nodes + 189 docs", "Starter kits view lists 16 samples" | site/data/index.json is now 2,581,596 bytes with 2023 nodes and 275 docs, and 48 samples carry a badge (counted with `json.load`). |

Accurate and not stale: challenge-2 line 57 "none yet" (no decoder row for propulsion exists),
and guidance-planning section 4 "proposed, not yet merged" (the decoder has 0 G-rows).

### 2.4 READMEs without a one-line "use this when"

19 index READMEs were checked (`docs/**/README.md`, `templates/**/README.md`, root,
samples/README.md). A regex looked for "use this when / start here when / read this first /
pick one" in the first 15 lines. 2 of 19 have it: docs/cheatsheets/README.md and
samples/README.md.

Most of the other 17 open with a purpose sentence. A trigger sentence that an agent can match
against its question is missing from: docs/README.md, docs/integration-cards/README.md (opens
with an HTML comment), docs/research/close-area-nav/README.md,
docs/research/innovation-prior-art/README.md, templates/README.md,
templates/drone-adapter/README.md, templates/drone-adapter/drivers/README.md, and templates/pitch/README.md.

### 2.5 Inconsistent table formats across index READMEs

First table header per index (`grep -m1 '^| '`):

| Index | Columns |
|---|---|
| docs/cheatsheets/README.md | The brief says... / Sheet / Decoder rows |
| templates/README.md | Template / What it is for / When in the 48h |
| templates/pitch/README.md | File / What it is for / When |
| docs/paper-digests/README.md | Digest / Use when |
| docs/landscape/README.md | File / Contents |
| docs/primer/README.md | # / Chapter / Read it if you are going to... |
| docs/research/close-area-nav/README.md | Doc / Lane / Bottom line |
| docs/research/innovation-prior-art/README.md | Doc / Idea / What exists / What may remain / Verdict |
| templates/drone-adapter/README.md | File / What it is |
| docs/README.md | bullet list, no table |

That makes 10 indexes with 9 different shapes. Three of them carry a "when" column. A shared
`| Page | Use it when | You get |` shape would let an agent scan any index the same way.

### 2.6 docs/research/ has no index page

`ls docs/research/README.md` => no such file. The two rounds (innovation-prior-art, then
close-area-nav, which "replaces the long-range frame as the default") are told apart only inside
close-area-nav/README.md line 3. docs/README.md does not mention research/ at all (0 matches).

### 2.7 Entry-point lists that miss the close-area material

Mentions of close-area / research/ / drone-adapter / close-area-arena per file (`grep -c`):

| File | close-area | research/ | drone-adapter | close-area-arena |
|---|---|---|---|---|
| AGENTS.md | 0 | 0 | 0 | 0 |
| llms.txt | 9 (all in the generated Guides list) | 13 | 0 | 1 (Samples list) |
| docs/README.md | 0 | 0 | 0 | 0 |
| README.md | 0 | 0 | 0 | 0 |
| docs/day0-runbook.md | 0 | 0 | 0 | 0 |
| docs/cheatsheets/README.md | 0 | 0 | 0 | 0 |
| templates/README.md | 0 | 0 | 1 | 0 |

The llms.txt "Entry points" list has 14 items and 0 close-area items. The challenge-2 page
section 4 "working set" (13 rows) has no close-area-arena and no drone-adapter. templates/README.md
lists neither [demo-script-close-area.md](../../templates/demo-script-close-area.md) nor
[pitch/close-area-story.md](../../templates/pitch/close-area-story.md).

### 2.8 Tooling gaps found on the way

- MCP `read` allowlist (tools/mcp_server.py `readable()`): `docs/**/*.md`, `catalog/**/*.md`,
  `samples/<name>/README.md` and 4 root files. These calls were refused when sent over stdin
  JSON-RPC: `templates/drone-adapter/README.md`, `templates/README.md` and
  `samples/close-area-arena/CONTRACT.md`.
- `row_keywords()` in tools/query.py drops "A" from "A=>B" (STOP has "a"). Row 31's search line
  therefore reads "Drone B through obstacles close area arena ...". The approach text prints
  "A with clearance cost" because the `*` of A* is stripped.
- `python3 tools/query.py -h` lists subcommands with no one-line help each.
- `search_eval.py`: BM25F on the 11 "problem" queries scores 0.626 against 0.777 on all 41. This
  agrees with the decoder-first advice in AGENTS.md.

## 3. Ranked fix list

Ranked by agent time saved on Day 1 for the close-area task. Size: S = under 1 hour, M = 1-3
hours. Almost every target file is on this job's never-edit list, so all of these are driver
edits.

| Rank | Change | Files | Why it saves time | Size |
|---|---|---|---|---|
| 1 | Replace "sample pending: samples/close-area-arena" in rows 31-33 "Start from" with `[close-area-arena]` (+ `[drone-adapter]` for 31 and 32; + the arena's estimator-and-faults section for 33). Update the gaps note (lines 196-197) the same way. | docs/problem-statement-decoder.md, tools/decode_eval.json (assert start_from contains close-area-arena) | `decode` is hop 2 for every agent. Today it says no starter exists for 4 of the 12 questions. | S |
| 2 | Widen MCP `read` to `templates/**/*.md` and `samples/<name>/*.md` (CONTRACT.md, INTEGRATION.md), with the same `..` and symlink checks. Add tests. | tools/mcp_server.py, tools/test_mcp_server.py | An MCP-only agent cannot reach the drivers table, frames.md or the scorer contract (Q1, Q2, Q4). | M |
| 3 | Index templates as `guide` nodes (at least drone-adapter README, drivers README, frames.md, demo-script-close-area, pitch/close-area-story) so `search` returns them. | tools/build.py (guide discovery) | `search "drone adapter send_setpoint"` returns 0 template hits today. Q2 ends on upstream repos instead of the hub's own drivers. | M |
| 4 | Add a 5-line "Close-area A=>B (likely Day-1 task)" block to AGENTS.md under "Given a problem statement": synthesis README, close-area-arena, drone-adapter + drivers, decoder rows 31-33, cheat sheet (rank 7). | AGENTS.md | AGENTS.md is the first file read and has 0 close-area mentions. | S |
| 5 | Add 3 items to the llms.txt "Entry points": close-area synthesis, close-area-arena, templates/drone-adapter/drivers. | tools/build.py (llms.txt writer) | Puts the Day-1 assets at hop 1 instead of 2-3. | S |
| 6 | Challenge-2 page: in section 3 row 1, open close-area-arena and drone-adapter first. In section 4, add a "close-area" sub-table (arena, drone-adapter, sitl-docker, relative-nav-benchmark OpenVINS indoor, vio-to-mavlink-bridge). Move the update box's "start from" into the section 4 lead. | docs/challenge-2-autonomous-flight.md | The Challenge 2 page is the agreed first page, and its working set is long-range only. | S |
| 7 | Cheat sheets: add a close-area row ("A to B", "obstacles", "arena", "indoor drone" => new sheet, rows 31-33). Write `close-area-a-to-b.md` in the existing sheet shape. Change the dismounted row to say "on foot", so that "indoors" + drone goes to row 33. | docs/cheatsheets/README.md, docs/cheatsheets/close-area-a-to-b.md (new) | Today "indoors" routes an indoor-drone brief to the dismounted sheet. | M |
| 8 | New docs/research/README.md: the two rounds, dates, "close-area-nav is the default; innovation-prior-art is the long-range fallback", and one table "brief family => headline idea => kill test => status". | docs/research/README.md (new) | Answers Q6 in one hop and removes the three-way headline ambiguity. | S |
| 9 | Make decode fall back to guides on how-to questions: when no row or low confidence, print 1-3 guide hits from `search` (for example licences => model-weights-licenses, competitions => doc 06, Mac => practical-readiness). | tools/query.py, tools/mcp_server.py (tool_decode `next`), tools/decode_eval.json | 6 of 12 Day-1 questions get low or no decode today. The agent then has to guess keywords. | M |
| 10 | docs/README.md: add a "Close-area A=>B" block under H+0 (research/README, arena, drone-adapter, demo-script-close-area, pitch/close-area-story). Link the 3 orphan docs/reports files. | docs/README.md | The docs map has 0 research/ mentions and leaves 3 reports orphaned. | S |
| 11 | Root README: one line above "Four hops": "EDGE Challenge 2 => docs/challenge-2-autonomous-flight.md; close-area task => docs/research/close-area-nav/". | README.md | Humans and agents that open README.md first get no hint of Challenge 2 today. | S |
| 12 | Remove "Nothing ... has been run" from the close-area synthesis line 8 and from close-area-story line 8. Link the arena's results instead, with the input type (synthetic). | docs/research/close-area-nav/README.md, templates/pitch/close-area-story.md | Stops agents from concluding there is no runnable baseline. | S |
| 13 | Fill `readiness` for close-area-arena (compute cpu, platform macos-arm64, setup measured). Then do the same for the other close-area-relevant samples among the 39 with compute unknown. | samples/close-area-arena/sample.json or samples/_meta_overrides.json | `--platform macos-arm64` returns 5 samples and misses the arena that ran on an M3 Max (Q8). | M |
| 14 | Name the `freest_beam` baseline in the arena README "Run" section and in the decoder row 31 approach ("start from freest_beam, not straight"). | samples/close-area-arena/README.md | Q3: the better baseline (86 % vs 26 % reach on truth, 50 synthetic layouts, from the arena README table) is hidden in run_faults.py. | S |
| 15 | day0-runbook: add a close-area branch (sim pick, adapter, arena kill test by H+3). The rubric should accept rows 31-33. | docs/day0-runbook.md | The H+0 to H+3 plan has 0 close-area mentions. | S |
| 16 | templates/README.md: add rows for demo-script-close-area.md and pitch/close-area-story.md, and a drivers/ line under drone-adapter. | templates/README.md | Removes 1-2 hops to the demo and pitch scaffolds. | S |
| 17 | Fix `row_keywords` so "A=>B" keeps "A to B" and "A*" survives. | tools/query.py | Row 31's search line is mangled today. | S |
| 18 | Point playbook line 25 "Start here when the statement drops" at the challenge-2 page for Challenge 2. | docs/hackathon-playbook.md | Brings the competing entry points down from 7 to 4 (same as rank 11 + rank 15). | S |
| 19 | Add a one-line "Use this when ..." to the 17 index READMEs that lack one (list in 2.4). | the 17 READMEs, split per package below | Agents pick an index by matching their question to a trigger line. | M |
| 20 | Standardise index tables on `| Page | Use it when | You get |`. | same as rank 19 | One scan pattern for 10 indexes. | M |
| 21 | Add docs/reports/README.md (one line per report, which are superseded). | docs/reports/README.md (new) | `reports/` currently links to a bare directory of 11 files. | S |
| 22 | site/README.md: refresh the "Data" size and counts. Mark the 2026-11-06 verification block as historical. | site/README.md | A reviewer reads "1287 nodes" while the UI holds 2023. | S |
| 23 | Add one-line help per subcommand in `query.py -h`. | tools/query.py | `-h` shows names only. | S |
| 24 | Add a follow-up note to the close-area-arena `verified` text: "drone-adapter now present; interface diff not yet done". | samples/close-area-arena/sample.json | Stops an agent from reading the stale "not present" as current. | S |
| 25 | In decoder row 1 "Start from", move e2e-visual-nav-vpair first, to match challenge-2 section 4. | docs/problem-statement-decoder.md | Q11: two orderings for the same need. | S |

### Work packages (disjoint file sets, can run in parallel)

| WP | Fixes | Files (only these) |
|---|---|---|
| A. Decoder | 1, 25 | docs/problem-statement-decoder.md, tools/decode_eval.json |
| B. Tooling | 2, 3, 5, 9, 17, 23 | tools/mcp_server.py, tools/test_mcp_server.py, tools/query.py, tools/build.py (then one build by the driver) |
| C. Agent entry points | 4, 10, 11, 21, and 19 + 20 for docs/README.md | AGENTS.md, README.md, docs/README.md, docs/reports/README.md (new) |
| D. Challenge 2 and cheat sheets | 6, 7, 15, 18 | docs/challenge-2-autonomous-flight.md, docs/cheatsheets/README.md, docs/cheatsheets/close-area-a-to-b.md (new), docs/day0-runbook.md, docs/hackathon-playbook.md |
| E. Research and close-area docs | 8, 12, and 19 + 20 for the research READMEs | docs/research/README.md (new), docs/research/close-area-nav/README.md, docs/research/innovation-prior-art/README.md |
| F. Templates | 16, 12 (pitch line), and 19 + 20 for template READMEs | templates/README.md, templates/pitch/README.md, templates/pitch/close-area-story.md, templates/drone-adapter/README.md, templates/drone-adapter/drivers/README.md, templates/demo-dashboard/README.md, templates/offline-kit/README.md, templates/project-repo/README.md |
| G. Arena sample metadata | 13, 14, 24 | samples/close-area-arena/README.md, samples/close-area-arena/sample.json (or samples/_meta_overrides.json, as a driver edit) |
| H. Site | 22 | site/README.md (site/app.js only if the showcase preset below is taken) |
| I. Remaining index READMEs | 19 + 20 | docs/integration-cards/README.md (generated by tools/card_index.py: edit the generator, which conflicts with WP-B only if both touch the same tool), docs/dataset-cards/README.md, docs/paper-digests/README.md, docs/landscape/README.md, docs/primer/README.md |

Order if run in series: A, C, B, D, E, F, G, H, I. A and C together are about 1.5 hours and fix
the two hop-1 failures (decode output and AGENTS.md).

## 4. Showcase notes (site/)

What already works for humans:

- A static UI with no build step. Search ranking matches the CLI (`search_eval.py --parity` is
  documented). Facets show live counts. The concept tree, the related panel and in-app markdown
  rendering are in place, and URL-hash state makes searches shareable.
- The Starter kits view (`#view=kits`) shows the `verified` text per sample, which is the hub's
  strongest honesty signal. 48 of 48 samples now carry a badge in site/data/index.json.
- Copy MCP and Copy CLI turn a UI search into an agent call. This shows "humans and agents use
  the same index".
- Constraint filters (compute, platform, setup, download) are tested by
  `node --test site/test_constraints.js` (per site/README.md; not re-run here).
- There are desktop and phone screenshots. The desktop one shows a generic "visual
  geolocalization" search.

What a reviewer would want to see first, and does not get today:

1. A Challenge 2 landing state. The UI opens on an empty search (`grep -ci "challenge\|close-area"`
   in app.js and index.html = 0). A header link "Challenge 2" pointing to the challenge-2 page,
   plus a preset `#q=close area A to B&kind=sample,guide`, would show the Day-1 path in one click.
2. The close-area arena result as a picture. `samples/close-area-arena/results/*_run0.png`
   exists (3 plots) but sits two clicks deep inside a sample README.
3. Evidence with input type. The evidence matrix is the hub's best artefact for judges and is
   one generic doc among 275 in the UI. A pinned "Evidence (real / SITL / synthetic)" link would
   show the rigour.
4. Fresh numbers in site/README.md (rank 22). They are the first thing a reviewer cross-checks.
5. A screenshot of the kits view or a close-area search, in place of the generic geolocalization
   search.

## Not verified

- No real cold agent was run. Paths are the ones an agent following AGENTS.md literally would
  take. Hop counts for Q2, Q6 and Q8 are ranges because the keyword choice varies.
- The site was not served or opened in a browser. Showcase notes come from site/README.md, one
  screenshot, `grep` and a `json.load` of site/data/index.json.
- `node --test site/test_constraints.js` was not run.
- The "use this when" count is a regex heuristic (2.4), checked by reading the first content
  line of each README.
- Driver code in templates/drone-adapter/drivers is unrun by its own README. This audit quotes
  its table and did not check it against the SDKs.

## Appendix: commands

```sh
python3 tools/query.py decode "<question>"                      # Q1-Q12
python3 tools/query.py search "<keywords>" --limit 5            # per walkthrough row
python3 tools/query.py search "" --platform macos-arm64 --kind sample --limit 60 | grep -c '^sample'   # 5
python3 tools/query.py search "" --compute cpu --kind sample --limit 60 | grep -c '^sample'           # 7
python3 tools/query.py search "" --kind sample --limit 80 | grep -o 'compute:[a-z-]*' | sort | uniq -c  # 39 unknown of 48
python3 tools/check_links.py                                    # 25853 links, 0 broken
python3 tools/decode_eval.py | tail -4                          # all n=59 hit@1 1.00; close-area n=8 1.00
python3 tools/search_eval.py | tail -3                          # problem n=11 0.626
printf '<initialize + tools/call read {"path":"templates/drone-adapter/README.md"}>' | python3 tools/mcp_server.py   # "not readable"
```

The orphan, BFS-reachability and use-when scripts were inline `python3 -` heredocs (re + os +
posixpath, stdlib only). They walk all `.md` files outside generated folders, resolve
`(relative)` links against the source file's folder, and map a directory link to its README.md.
