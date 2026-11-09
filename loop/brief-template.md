# Brief template for loop workers

Copy into the scratchpad, fill every section, launch with `farmout run kiro`. Keep each job to
about 30 minutes of work. If it needs more, split it.

```markdown
# Task
<item-id>: <one paragraph - what to produce and why it matters on hackathon day>

# Context
- Repo: navigation knowledge hub for an autonomous-flight hackathon (Python 3.12 tooling,
  JSON records in data/, generated catalog). Your cwd is a fresh checkout of it.
- Read first: AGENTS.md, <the 2-5 files this item builds on, with one line each on why>
- Prior result this builds on: <numbers or findings, with their source file>
- Likely task on the day: fly a drone from A to B in a close area with obstacles. Platform and
  sensors unknown. Close-area code talks to the vehicle only through pose(), ranges(),
  send_setpoint().

# Constraints
- Create or edit only these paths: <paths>. Nothing else.
- Never edit (unless listed in your paths above): tools/stdlib-sample-tests.txt,
  docs/problem-statement-decoder.md, tools/decode_eval.json, docs/evidence-matrix.md,
  docs/challenge-2-autonomous-flight.md, docs/README.md,
  docs/cheatsheets/README.md, AGENTS.md, samples/_meta_overrides.json, data/concepts.json,
  loop/, or generated files (INDEX.md, llms.txt, catalog/, graph/, index/, reports/, site/data).
  Do not run tools/build.py.
- A new sample also gets INTEGRATION.md: the decoder row, evidence-matrix line and cheat-sheet
  line it wants, as text. Other shared changes go under "Driver edits needed" in your final message.
- Python deps only in a sample-local venv: `uv venv <sample>/.venv` then
  `uv pip install --python <sample>/.venv -r <sample>/requirements.txt`. No global installs,
  brew, apt, Docker pulls or CUDA. If the task cannot be done without one, stop and say so.
- Records: data/repos/<item-id>.json and data/resources/<item-id>.json, schema per
  docs/SCHEMA.md, concept ids only from data/concepts.json, no duplicates
  (`python3 tools/query.py search "<words>"`).
- Samples: README.md (goal, run, results, limits, sources), sample.json (copy the field set
  from samples/terrain-heightmap-pf/sample.json, honest verified_status), requirements.txt,
  results/ with the outputs the README quotes, one test_smoke.py that passes or skips under
  plain python3. Do not write a test suite.
- Every number in prose comes from a file in results/ or a cited source, with its input type
  (real / SITL / synthetic). Nothing unverified is written as verified.
- Style: plain hyphen "-" only, never em or en dashes; "=>" not arrow glyphs; short sentences.
- Scope: the vehicle's own navigation. No targeting, homing or intercept.
- Do not commit, push, or change git config.

# Deliverable
<exact output: files and what each holds; the experiment and its pass/fail line if any>
Final message: one line per file changed; the key result with its number; what you did not
verify; "Driver edits needed:" list (or "none").
```
