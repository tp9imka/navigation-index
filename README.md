# navigation-index

A research hub for navigation hackathons with a defense lens: PNT, GNSS-denied and
GNSS-contested navigation, sensor fusion, SLAM, autopilots, situational awareness.
It indexes open-source repos (not cloned - described, tagged and linked) and the technical
material around them: standards, papers, talks, courses, masterclasses, datasets, reports.
Everything is one knowledge graph, so a repo page shows the papers, courses and samples
that point at it, and the reverse.

Current counts are at the top of [INDEX.md](INDEX.md) and in [llms.txt](llms.txt).

## Where to start

| You want | Go to |
|---|---|
| Project ideas, judging angle, reference architectures | [docs/hackathon-playbook.md](docs/hackathon-playbook.md) |
| "Which library should I use for X" | [docs/reference-stacks.md](docs/reference-stacks.md) |
| Learn navigation fast | [docs/primer/](docs/primer/README.md), [docs/learning-paths.md](docs/learning-paths.md) |
| Browse everything by topic | [INDEX.md](INDEX.md) => `catalog/concepts/` |
| Working code | [samples/](samples/) |
| See the graph | [graph/index.html](graph/index.html) (serve the repo root, see below) |
| Use it from an LLM agent | [AGENTS.md](AGENTS.md), [llms.txt](llms.txt), [samples/llm-agent-usage](samples/llm-agent-usage/README.md) |
| Stay legal | [docs/export-control-and-ethics.md](docs/export-control-and-ethics.md) |

## Layout

```
data/            source of truth (JSON per research lane) - edit here
  concepts.json  fixed concept taxonomy
  repos/         repo records
  resources/     papers, standards, talks, courses, datasets, reports
  github_meta.json  stars / license / last push, fetched by tools/enrich.py
catalog/         generated page per repo, resource, concept, sample
graph/           graph.json + interactive viewer
index/           records.jsonl - one JSON line per node, for grep / RAG
samples/         usage samples; each states whether it was run or is a sketch
docs/            playbook, reference stacks, primer, schema, reports
tools/           enrich.py, build.py, query.py, mcp_server.py (stdlib only)
```

## Tools

All stdlib Python 3, no installs. `enrich.py` needs an authenticated `gh` CLI.

```
python3 tools/query.py search "visual geolocalization satellite" --kind repo --fit high
python3 tools/query.py concept concept:magnetic-nav
python3 tools/query.py neighbors repo:mit-ai-accelerator/magnav.jl --depth 2
python3 tools/enrich.py && python3 tools/build.py      # after editing data/
python3 -m http.server 8000   # then open http://localhost:8000/graph/
claude mcp add navigation-index -- python3 "$PWD/tools/mcp_server.py"
```

## How it was built and how much to trust it

Eleven parallel research lanes (autopilots, GNSS, INS/fusion, SLAM, GNSS-denied alt-nav,
planning/GIS/C2, simulation/datasets, maritime/underwater/swarm/C-UAS, standards,
learning material, defense context), plus a gap-fill lane for thin areas. Every
GitHub repo was confirmed to exist via the GitHub API. Stars, license and last push come
from the API, not from the researchers. A fact-check pass sampled records against READMEs
and arXiv: see [docs/reports/fact-check-2026-11-06.md](docs/reports/fact-check-2026-11-06.md)
for the measured error rate. Most records got only mechanical checks, so verify a repo's
README before you build on it. Samples marked "unverified sketch" were syntax-checked,
never run.

Snapshot date: 2026-11-06. [reports/quality.md](reports/quality.md) lists dangling
references, archived repos and merged duplicates.

## Scope

In: navigation, localization, PNT resilience, autonomy, situational awareness, defensive
EW and counter-UAS detection. Out: weapon terminal guidance, targeting, offensive payloads.
