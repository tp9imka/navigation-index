# Contributing

Navigation Index takes corrections, new records, new samples and new planners. Small PRs are
easiest to review: one record fix, one sample, one planner.

Before you start, read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and the scope line at the end of
this page.

## Run the hub locally

Everything below is stdlib Python 3. CI uses Python 3.12. No installs, no network.

```sh
git clone https://github.com/tp9imka/navigation-index.git
cd navigation-index
python3 tools/build.py                          # regenerate catalog/, INDEX.md, graph/, index/, site/data/
python3 -m http.server 8000                     # serve the repo root, then open http://localhost:8000/
python3 tools/query.py search "visual geolocalization satellite" --kind repo --fit high
python3 tools/query.py decode "fly a drone from A to B indoors without GPS"
```

The MCP server is `tools/mcp_server.py` (stdlib). Register it with your MCP client, for example
`claude mcp add navigation-index -- python3 "$PWD/tools/mcp_server.py"`. [AGENTS.md](AGENTS.md)
and [llms.txt](llms.txt) describe the tools.

`tools/enrich.py` is the one tool that needs network: it reads stars, licence and last push
through an authenticated `gh` CLI. You do not need it for a PR. Maintainers run it.

## The gate a PR must pass

CI runs [.github/workflows/check.yml](.github/workflows/check.yml) on every push and PR. The same
steps as local commands, from the repo root:

```sh
# 1. Build from the tree (must print "dangling: 0 bad concepts: 0")
python3 tools/build.py | tee build.log
python3 templates/offline-kit/build_manifest.py
python3 tools/card_index.py
grep -q "dangling: 0 bad concepts: 0" build.log && echo build OK

# 2. Relative links resolve (must print "broken: 0")
python3 tools/check_links.py

# 3. Public-release hygiene (must print 0 hits)
python3 tools/check_public.py
python3 -m unittest tools/test_check_public.py

# 4. Search, decoder, sample list, readiness, deploy smoke
python3 tools/search_eval.py --parity
python3 tools/decode_eval.py
python3 tools/check_sample_tests.py
python3 tools/test_readiness.py
python3 -m unittest tools/test_check_deploy.py

# 5. Browser tests (Node 20)
node --test site/test_constraints.js site/solver/test_sweep.mjs site/test_nav.mjs

# 6. Stdlib sample and template tests
python3 tools/test_mcp_server.py
make -C templates/project-repo test
(cd templates/demo-dashboard && python3 -m unittest -q)
(cd templates/offline-kit && python3 -m unittest -q)
while read -r d; do
  [ -z "$d" ] && continue
  (cd "samples/$d" && python3 -m unittest discover -q) || exit 1
done < tools/stdlib-sample-tests.txt
```

Step 1 rewrites generated files. You do not need to commit them: on `main`, CI rebuilds them
and commits the result. Never edit a generated file by hand (`catalog/`, `INDEX.md`, `llms.txt`,
`graph/graph.json`, `index/records.jsonl`, `reports/`, `site/data/`, `site/learn.html`, the
generated table in `samples/README.md`).

`tools/check_public.py` flags machine paths, internal tags and event wording. If it flags a
third-party fact (a real competition's rules, a paper author), add an entry to
[tools/public_allowlist.json](tools/public_allowlist.json) with a reason, and say why in the PR.

## Add or fix a record

Records are JSON. The schema is [docs/SCHEMA.md](docs/SCHEMA.md).

1. Pick the lane file that fits: `data/repos/<lane>.json` for a code repository,
   `data/resources/<lane>.json` for a paper, dataset, standard, talk, course or other resource.
   A new lane is a new file in the same folder.
2. Use an id in the schema's form: `repo:<owner>/<name>` from the canonical GitHub URL, or
   `res:<short-kebab-slug>`.
3. Use only concept ids that exist in [data/concepts.json](data/concepts.json). If nothing fits,
   add the concept there first, in the same PR.
4. Write the summary in your own words. Confirm the URL resolves. Do not type stars, licence or
   dates from memory: `tools/enrich.py` fills them.
5. Run `python3 tools/build.py`. It must print `dangling: 0 bad concepts: 0`. A dangling id
   means a `related` entry points at a record nobody indexed.

`reports/quality.md` (generated) lists "Referenced but not indexed": repos other records point at
that have no record yet. That list is a good first PR.

To report a wrong record without a PR, open a "Record correction" issue.

## Add a sample

Copy the layout of [samples/close-area-arena](samples/close-area-arena/README.md):

- `README.md`: goal, run commands, results, limits, sources. Paste the real output of the run
  you did, with the date, machine, interpreter and package versions in the section heading or
  next to it. Do not write output you did not see.
- `sample.json`: the fields in the [samples/README.md](samples/README.md) "Columns" section.
  - `verified`: free text. What ran, when, on which interpreter and on which data.
  - `verified_status`: `ran` (the main path ran and its output is in the README), `partial`
    (the main path ran, a shipped part did not) or `sketch` (nothing ran). Pick the honest one.
  - `input`: `synthetic`, `SITL` or `real` (or `mixed` when the key result reports both real
    and synthetic numbers). Name the dataset or simulator in the README.
  - `deps`, `first_command`, `group`, `shows`, `runtime`, `key_result`.
- `results/`: every number the README quotes, as JSON, CSV, Markdown or a log written by the
  run. A reader must be able to find each number in a file.
- `requirements.txt` when it needs third-party packages. Install them in a venv inside the
  sample folder, never in the global interpreter:
  `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- Tests that run under plain `python3 -m unittest` with no third-party packages (guard the
  imports, use `skipIf`). Stdlib-only samples go in `tools/stdlib-sample-tests.txt`.

Then add its measured numbers to [docs/evidence-matrix.md](docs/evidence-matrix.md) and a
"Start from" entry in [docs/problem-statement-decoder.md](docs/problem-statement-decoder.md).
When a new run supersedes a published number, update `key_result` and the matrix in the same
PR and label the old number as superseded.

Defects you find in upstream code go in [docs/upstream-findings.md](docs/upstream-findings.md),
with the file, the line and how you found it.

## Add a planner to the benchmark

The benchmark is [samples/close-area-benchmark](samples/close-area-benchmark/README.md): every
planner x 8 arena families x 2 sensor presets (`ideal`, `crazyflie`) x 20 layouts, seed 0. All of
it is synthetic. The planners are reference implementations, untuned. PRs are welcome.

1. Write the planner against the `Planner` interface in
   [samples/close-area-arena/CONTRACT.md](samples/close-area-arena/CONTRACT.md) ("Add a
   planner"). It reads only pose, scan, goal and the optional grid. It never calls `truth()`.
   Put it in its own sample folder with a README and `sample.json`, as above.
2. Register it in `PLANNERS`, `DEFAULT_PLANNERS` and `NEEDS` in
   [samples/close-area-benchmark/bench.py](samples/close-area-benchmark/bench.py).
3. Run the full matrix for your row and commit the JSON. Adding a row keeps the old rows as they
   are:

   ```sh
   cd samples/close-area-benchmark
   uv venv .venv && uv pip install --python .venv -r requirements.txt
   .venv/bin/python bench.py --add-to matrix_0 --planners <your_id> --recheck astar_unknown --workers 8
   .venv/bin/python bench.py --render matrix_0
   ```

   `--recheck` re-runs an existing row in the same pool and compares it run by run with the
   committed one (`results/matrix_0_recheck.*`). Commit `results/matrix_0.json`,
   `results/matrix_0.md`, the recheck files and the command's stdout in `results/`.
4. Update the tables in the benchmark README from `results/matrix_0.md`, and report your row as
   it came out. A planner that loses is a result.
5. To show it in the browser Arena, follow "How to add a planner" in
   [site/solver/README.md](site/solver/README.md).

Measured cost for scale: all 21 rows (6,720 flights) took 2963.7 s wall on 10 processes on
an Apple M3 Max (benchmark README, synthetic). Your machine will differ.

## Honesty rules

- Every number says what it ran on: synthetic, SITL or real. Arena results are synthetic
  simulation scored on truth. None is a flight result.
- A FAIL against the stated threshold is a valid result. Report it plainly, with its number. Do
  not tune until it passes and then report only the pass.
- Nothing unverified is written as verified. If you read the code but did not run it, say "read,
  not run". If one part ran and another did not, say which.
- One run is an example, not a statistic. Say how many seeds, layouts or flights stand behind a
  number.
- Quote numbers from a file in the repo or a cited source. Do not type counts from memory.

## Style

- Lab notebook, not landing page. Short declarative sentences.
- Plain hyphen `-` only. No em or en dashes.
- `=>` for arrows, not arrow glyphs.
- No marketing words. Say what the thing does and what it measured.
- Relative links must resolve from the file they are in (`python3 tools/check_links.py`).

## Licences of contributions

- Code is Apache-2.0 ([LICENSE](LICENSE)).
- Docs and data are CC BY 4.0 ([LICENSE-docs](LICENSE-docs) lists the paths).
- Third-party material keeps its own licence and is listed in [THIRD_PARTY.md](THIRD_PARTY.md).
  If you add some, add its row there.

Inbound = outbound: by opening a PR you agree that your contribution is licensed under the same
terms as the part of the repo it lands in. Do not submit material you have no right to license
that way.

## Scope

The hub covers the vehicle's own navigation: localization, PNT resilience, autonomy, situational
awareness, defensive EW and counter-UAS detection. No targeting, homing, intercept or weapons
guidance. PRs that add them are closed. Read
[docs/export-control-and-ethics.md](docs/export-control-and-ethics.md) before contributing code
that touches GNSS signal generation, RF transmission or defense end uses.
