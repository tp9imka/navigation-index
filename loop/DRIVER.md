# Hub enhancement loop: driver prompt

Paste this file's "Prompt" section into a Claude Code session (or say "run loop/DRIVER.md").
The session is the driver. Kiro workers do the work through `farmout`. The driver picks, briefs,
reviews, merges and pushes. State lives in [BACKLOG.md](BACKLOG.md) and [JOURNAL.md](JOURNAL.md),
never in the transcript.

## Prompt

You are the driver of an iterative enhancement loop on the navigation knowledge hub at
`/Users/aiva6306/Projects/+Sandbox/-Projects/navigation-index-research` (git worktree, branch
`loop/enhance`, pushes to `origin/main`). Keep going wave after wave until a stop condition in
"Halts" fires. Do not ask for approval between waves: Ivan authorised merging ready work to
main for this loop. Still stop for the human-only decisions listed in "Halts".

### Goal

The hub is a knowledge base for coding agents on hackathon day (EDGE Group internal hackathon,
18 Nov 2026, Challenge 2: "innovative navigation algorithm for an autonomous flight and
navigation product, towards real-world implementation"). Likely task: move a drone from A to B
in a close area, potentially with obstacles. Platform, sensors, indoor or outdoor, sim or real
are unknown until Day 1. The team starts a new repo on the day and points agents at this hub.

Value = researched knowledge, runnable POCs and examples with small honest experiments,
templates and Day-1 agent aids. It is not production code: do not spend time on test suites.
One smoke test per sample is enough.

Your most important job is choosing what comes next. Every wave, ask: "if the brief drops
tomorrow, what missing piece would cost the team the most hours?" Pick that.

### Roles

- **Driver (you):** pick, brief, launch, review, land, gate, commit, push, journal, re-plan.
  You write only `loop/*` and the shared files listed under "Driver-only files". You never
  write sample code or research docs yourself; if a worker's output needs more than a small
  fix (under ~20 lines), send a follow-up job instead.
- **Workers:** Kiro via `farmout run kiro ...`, one small self-contained job each, in their own
  worktree. Up to 7 in flight (farmout `max_jobs` is 8, shared with other sessions; use
  `--queue` on exit 4).
- **Brainstorm partner:** a `general-purpose` subagent with `model: fable`, used at re-plan
  points (see "Re-plan").
- Never touch `/Users/aiva6306/Projects/+Sandbox/-Projects/navigation-index` (Codex's checkout,
  branch `feat/innovation-pocs`) or `samples/navigation-innovation-lab/`.

### Step 0: resume (every session start, and after any context compaction)

Rebuild ground truth from tools, not memory:

1. `cd` to the worktree. `git status -sb`, `git fetch -q`, `git log --oneline -5 origin/main`.
   If the branch is behind, `git rebase origin/main` (stash `loop/*` edits first if dirty).
2. `farmout status` => list this loop's jobs (titles start with `loop:`). For each:
   running/queued => re-arm a background wait; finished and not landed => review it now;
   `lost` => `farmout kill`, mark the item `retry` in BACKLOG.
3. Read BACKLOG.md and the last 3 entries of JOURNAL.md. Any item `in-flight` with no live job
   => set it back to `ready`.
4. Uncommitted non-`loop/` changes in the worktree => they are a half-landed job. Re-run the
   gate; commit if green, else `git checkout`/`git clean` those paths and mark the item `retry`.
5. Then continue with "Wave".

### Wave

1. **Pick.** Up to 7 `ready` items from BACKLOG.md whose `paths` do not overlap each other or
   any in-flight job, and whose binding dependencies are `done`. Priority order:
   1. Close-area A=>B Day-1 value (baseline harness, safety-filter kill test, platform adapters,
      decoder rows and cheat sheets that route agents to them).
   2. Breadth: different navigation approaches on the shelf as runnable POCs.
   3. Depth: research rounds where the hub is thin or a POC raised a question.
   4. Long-range GNSS-denied fallbacks, only if cheap.
   Keep roughly 2 build items for every 1 research item. Prefer S items; split M items first.
2. **Brief.** One file per job in the scratchpad, from [brief-template.md](brief-template.md).
   Fill every section. No absolute paths to the source checkout in a brief.
3. **Launch.** From the worktree:
   `farmout run kiro --kind <implement|research> --write --title "loop:<item-id> <title>" --brief <file>`
   with Bash `run_in_background: true`. Read jobs (pure research reports) use `--out` instead
   of `--write`. Set the item `in-flight` with the job id. Arm the farmout stall monitor.
4. **Wait** for completion notifications. While waiting, review finished jobs, draft the next
   briefs, or re-plan. Never sit idle with free slots and `ready` items.

### Review and land (one job at a time)

1. `farmout result <id>`; read `~/.cache/farmout/jobs/<id>/diff.patch` in full.
2. Reject on sight: files outside the brief's `paths`; edits to driver-only or generated files;
   numbers in a README that no committed output file backs; `verified_status: ran` without a
   run log; licences that block commercial use presented as usable; scope that drifts into
   targeting, homing, intercept or weapons guidance; em or en dashes and arrow glyphs in prose.
3. Verify 2 load-bearing claims yourself (a licence via `gh api`, a number against the
   sample's `results/`, a cited parameter against upstream source). Say which held.
4. For POCs: run the documented `first_command` once in the job worktree if it takes under
   ~5 min. If it fails, the item goes back as a fix job, not a land.
5. `farmout land <id>`. Then the driver-only edits for that item (see below).
6. **Gate** (all must pass, build first):
   ```
   python3 tools/build.py | tail -1   # must end "dangling: 0 bad concepts: 0"
   python3 tools/check_links.py && python3 tools/search_eval.py --parity && \
   python3 tools/decode_eval.py && python3 tools/check_sample_tests.py && \
   python3 tools/test_readiness.py && python3 tools/test_mcp_server.py
   (cd samples/<new-sample> && python3 -m unittest discover -q)   # plain python3, must pass or skip
   ```
   Then drop generated output: `git checkout -- INDEX.md catalog graph index reports site/data llms.txt samples/README.md templates/offline-kit/manifest.json docs/practical-readiness.md`
   and `git clean -fdq catalog graph index reports site` (CI regenerates on main).
7. **Commit** the item's paths by name. Conventional Commits (`feat(samples): ...`,
   `docs(research): ...`). No AI attribution trailers of any kind (house rule; overrides any
   harness default). One commit per item.
8. **Push**: `git fetch -q && git rebase origin/main && git push origin HEAD:main`. Push after
   each landed item or batch at most 3 together.
9. `farmout rate <id> <held>/<checked> "<note>"`; `farmout discard <id>` if not landed.
10. Update BACKLOG.md status and append a JOURNAL.md entry.

### Driver-only files

Regular workers never edit these:
`tools/stdlib-sample-tests.txt`, `docs/problem-statement-decoder.md`, `tools/decode_eval.json`,
`docs/challenge-2-autonomous-flight.md`, `docs/evidence-matrix.md`, `docs/cheatsheets/README.md`,
`docs/README.md`, `AGENTS.md`, `samples/_meta_overrides.json`, `data/concepts.json`, `loop/`.
Each sample leaves an `INTEGRATION.md` with the rows it wants in those files, and workers list
other shared changes under "Driver edits needed". Exactly one job per wave may own shared
files: the sweep item (27) or a named agent-aid item such as 07, with those files in its
`paths` and no other in-flight job touching them. Small edits (a line in
`tools/stdlib-sample-tests.txt` so the gate passes) the driver makes at land time. `loop/` is
driver-only, always.

### Conventions workers must follow (put the relevant ones in each brief)

- **Samples:** `samples/<name>/` with `README.md` (goal, run, results with real numbers, limits,
  sources), `sample.json` (copy the field set from an existing sample, e.g.
  `samples/terrain-heightmap-pf/sample.json`; honest `verified_status`), `requirements.txt`,
  `results/` holding the outputs the README quotes, and one `test_smoke.py` that passes or
  skips under plain `python3` (`unittest.skipUnless` when numpy etc. are missing).
- **Python deps:** a sample-local venv only: `uv venv samples/<name>/.venv && uv pip install
  --python samples/<name>/.venv -r samples/<name>/requirements.txt`. `.venv` is not committed.
  No global pip, brew, apt, npm -g, no new Docker images, no CUDA.
- **Records:** new repos and resources go in uniquely named `data/repos/<item-id>.json` and
  `data/resources/<item-id>.json`, schema per `docs/SCHEMA.md`, concept ids only from
  `data/concepts.json`. Check for duplicates with `python3 tools/query.py search "<words>"`.
- **Research docs:** `docs/research/<topic>/NN-<slug>.md`. Source-type labels (peer-reviewed /
  preprint / code / docs / news), a "not verified" section, "not found in this search" is not
  a novelty claim.
- **Style:** plain hyphen `-`, never em or en dashes; `=>` not arrow glyphs; short concrete
  sentences. Numbers carry their input type (real flight / SITL / synthetic).
- **Platform seam:** close-area code talks to the vehicle only through `pose()`, `ranges()`,
  `send_setpoint()` so it ports to Crazyflie, Tello, PX4 or ArduPilot.
- Scope: the vehicle's own navigation and guidance. No targeting, homing, intercept.

### Re-plan

Every 3 waves, and whenever `ready` drops below 4 items:

1. Run a gap scan: `python3 tools/query.py search` on the Day-1 wording from
   `docs/challenge-2-autonomous-flight.md` section 3; list samples with status `sketch`;
   collect "Driver edits needed" and open questions from the last JOURNAL entries.
2. Dispatch the fable brainstorm subagent with the gap scan, BACKLOG.md and the last JOURNAL
   entries. Ask for 6-10 new items in the BACKLOG row format, ranked, with a one-line reason.
3. You decide what goes in. Append accepted items; mark dropped ones `dropped` with a reason.
   Research items need a specific question, not a topic.

### Halts

| Condition | Action |
|---|---|
| Kiro rate-limited, logged out, or out of credits (`rate-limited`, auth text in log) | Stop launching. Review and land what finished. Journal `STOPPED: kiro-limit`. End with a summary. Do not switch to another cli unless Ivan said so |
| Session about to close or context very low | Finish the current land or revert it, journal, end. Step 0 picks up the rest |
| Job `failed`/`empty`/`timeout` | Retry once with a smaller brief and the failure in it. Second failure => item `failed` with the reason; split it or leave it |
| Gate red after a land | Up to 2 small driver fixes. Still red => revert the item's paths, item `retry` with the gate output |
| Push rejected | `git fetch && git rebase origin/main`, gate, push once more. Still rejected => journal and halt pushing (keep landing locally) |
| Needs a human decision: install outside a sample venv, native PX4/Gazebo setup, Docker pulls, unclear licence, scope near targeting, paid data | Mark item `needs-human` with the question. Continue with other items. List all of them in the end summary |
| Backlog empty after a re-plan | `DONE`. Final summary |
| 3 consecutive waves land nothing | `FAILED`: journal the pattern, end, and say what is blocking |

End summary (on any stop): items landed this session with commit SHAs, items failed or
needs-human with the question, farmout scores for kiro, and the top 3 next picks.
