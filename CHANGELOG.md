# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Repo traffic on the Home page.** `tools/traffic.py` archives GitHub clone and view counts daily
  (`.github/workflows/traffic.yml`, repo secret `TRAFFIC_TOKEN`) into `site/data/traffic.json`,
  past GitHub's 14-day limit. Counting starts 2026-11-16, the day the repo went public. Clones
  include the repo's own CI and deploy builds; the 14-day unique count reads "not measured" until
  the whole window is after that date.

### Fixed

- **Arena mapper: a dropped beam no longer marks free space behind walls.** The unknown-map
  log-odds map traced a beam the sensor dropped as free out to max range. It now adds nothing
  (`SKIP_DROPPED_BEAMS = True`, upstream-findings section 22). The benchmark matrix, the depth
  camera matrix, the explore search benchmark, the Advisor data, the playground parity files, the
  scenario packs and the replays were regenerated. The 8 planners that build a map from the scan
  moved by -5.6 to +5.7 points of reach; the other 13 reproduced every run. The flight-repo arena
  adapter now passes the per-beam drop flags through.

## [0.1.0] - 2026-11-11

First public release. Counts are from `INDEX.md`, `samples/README.md` and
`samples/close-area-benchmark/results/matrix_0.json` at this release.

### Added

- **Catalog.** 923 open-source repos and 975 resources (409 papers, 77 datasets, 52 standards,
  162 docs, 76 blogs, 49 talks, 36 competitions, 33 reports and smaller kinds), tagged with 46
  concepts and linked in one graph. JSON records in `data/` are the source; `tools/build.py`
  generates `catalog/`, `INDEX.md`, `graph/`, `index/` and `site/data/`.
- **Guides and cards.** 89 guide pages in `docs/` and `templates/` (brief decoder, evidence
  matrix, primer, landscape notes, export control and ethics, template guides), plus integration
  cards, dataset cards, paper digests and cheat sheets under `docs/`.
- **Samples.** 63 samples, each with a README and a `sample.json` that says what ran, on which
  interpreter and on which data (`input`: synthetic, SITL, real or mixed). Status: 60 `ran`,
  3 `partial`.
- **The Arena** (browser, synthetic simulation scored on truth):
  - Solver: race every planner on a map you pick, draw or import, over sensor presets and seeds,
    ranked with 95 % Wilson intervals; Recommend writes the command to fly the pick.
  - Playground: draw an arena, pick a planner, sensor, VIO fault and safety filter, and run the
    hub's Python in the browser (Pyodide).
  - Results: measured results with verdict and input badges, replays and the sample gallery.
- **Benchmark.** `samples/close-area-benchmark`: 21 planners x 8 arena families x 2 sensor
  presets (`ideal`, `crazyflie`) x 20 layouts, 6,720 runs, synthetic.
- **For coding agents.** `llms.txt`, `AGENTS.md` and a stdlib MCP server (`tools/mcp_server.py`)
  with `search`, `decode`, `show`, `concept`, `neighbors` and `read`. `tools/query.py` is the
  same lookup as a CLI.
- **Templates.** `flight-repo` (planner + safety filter + estimator faults, `make first-flight`
  scores a flight in the arena), `drone-adapter` (PX4, ArduPilot, Crazyflie, Tello drivers,
  written from SDK docs, not run), `project-repo`, `demo-dashboard`, `offline-kit`,
  `presenting` and `competition-kit`.
- **Checks.** CI runs the build, link check, public-hygiene check, search and decoder evals,
  readiness contracts, browser tests and stdlib sample tests.
- **Licences.** Code Apache-2.0 (`LICENSE`), docs and data CC BY 4.0 (`LICENSE-docs`),
  third-party exceptions in `THIRD_PARTY.md`.

[Unreleased]: https://github.com/tp9imka/navigation-index/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tp9imka/navigation-index/releases/tag/v0.1.0
