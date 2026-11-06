# Using the hub from an LLM coding agent (MCP server + navigation recipes)

Goal: let Claude Code, Cursor or any MCP client query this hub as tools instead of
grepping markdown. `tools/mcp_server.py` is a stdlib-only MCP server over stdio (JSON-RPC
2.0, newline-delimited) that exposes the same logic as `tools/query.py`.

## Tools exposed

| Tool | Arguments | Returns |
|---|---|---|
| `search` | `query` (required), `kind`, `fit`, `domain`, `concept`, `limit` | ranked briefs: id, kind, name, summary, url, fit, catalog page, stars, score |
| `show` | `id` (required) | the full record (summary, why_it_matters, hackathon_notes, related, github meta) |
| `concept` | `id` (omit to list all concepts with counts), `kind`, `fit`, `domain`, `limit` | records tagged with the concept, high hackathon fit first |
| `neighbors` | `id` (required), `depth` (1-3), `kind`, `fit`, `domain`, `limit` | graph neighbours with the linking edge in `via` |

Unknown ids come back as a tool result with `isError: true`, so the model can retry.
Unknown JSON-RPC methods get error `-32601`; bad JSON gets `-32700`.

## Prerequisites

- `python3` 3.9+ (verified on 3.14.7). No third-party packages.
- Generated index files. From the repo root:

```sh
python3 tools/build.py      # writes index/records.jsonl and graph/graph.json
```

## Register the server

Use the absolute path of your checkout in place of `/abs/path`.

Claude Code:

```sh
claude mcp add navigation-index -- python3 /abs/path/tools/mcp_server.py
claude mcp list             # should show navigation-index
```

Cursor (`.cursor/mcp.json` in a project, or `~/.cursor/mcp.json` globally), Claude Desktop
(`claude_desktop_config.json`) and most other clients use the same `mcpServers` shape:

```json
{
  "mcpServers": {
    "navigation-index": {
      "command": "python3",
      "args": ["/abs/path/tools/mcp_server.py"]
    }
  }
}
```

VS Code (GitHub Copilot agent mode, `.vscode/mcp.json`):

```json
{"servers": {"navigation-index": {"type": "stdio", "command": "python3", "args": ["/abs/path/tools/mcp_server.py"]}}}
```

Codex CLI (`~/.codex/config.toml`):

```toml
[mcp_servers.navigation-index]
command = "python3"
args = ["/abs/path/tools/mcp_server.py"]
```

Only the raw stdio protocol was exercised for this sample (transcript below). None of the
client registrations above were run; they follow each client's documented config format
at the time of writing, so check the client docs if one does not load.

## Smoke test without any client

```sh
python3 tools/mcp_server.py < samples/llm-agent-usage/demo_requests.jsonl
```

Expected: 7 response lines (the `notifications/initialized` line gets no reply).

### Verified transcript

Ran on 2026-11-06 with python3.14.7 against the index built that day. Requests are the
lines of `demo_requests.jsonl`. In the responses below, `tools/list` schemas and the
`summary` strings are cut short for readability; everything else is verbatim. Ids and
ranking will change as the index grows.

```
>>> {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"pipe-test","version":"0"}}}
<<< {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18", "capabilities": {"tools": {"listChanged": false}}, "serverInfo": {"name": "navigation-index", "version": "0.1.0"}, "instructions": "Navigation/PNT open-source hub. Start with concept (no id) or search, then show for details and neighbors for related work."}}

>>> {"jsonrpc":"2.0","method":"notifications/initialized"}
    (no response - notification)

>>> {"jsonrpc":"2.0","id":2,"method":"tools/list"}
<<< {"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "search", "description": "Ranked keyword search over repos, resources, concepts and sa...", "inputSchema": "..."}, {"name": "show", ...}, {"name": "concept", ...}, {"name": "neighbors", ...}]}}

>>> {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search","arguments":{"query":"gnss-denied fixed-wing visual geolocalization","kind":"repo","limit":3}}}
<<< {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "[{\"id\": \"repo:yfs90/gnss-denied-uav-geolocalization\", \"kind\": \"repo\", \"name\": \"GNSS-Denied UAV Geolocalization (terrain-weighted)\", \"summary\": \"Code and demos for a UAV geolocalization system that combines image ma...\", \"url\": \"https://github.com/YFS90/GNSS-Denied-UAV-Geolocalization\", \"hackathon_fit\": \"medium\", \"page\": \"catalog/repos/yfs90__gnss-denied-uav-geolocalization.md\", \"stars\": 86, \"score\": 15}, {\"id\": \"repo:gaoxiang12/slambook-en\", ... \"score\": 7}, {\"id\": \"repo:i2nav-whu/ic-gvins\", ... \"score\": 7}]"}], "isError": false}}

>>> {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"concept","arguments":{"id":"concept:terrain-nav","fit":"high","limit":2}}}
<<< {"jsonrpc": "2.0", "id": 4, "result": {"content": [{"type": "text", "text": "[{\"id\": \"repo:alti3/python-tercom\", \"kind\": \"repo\", \"name\": \"python-tercom\", \"summary\": \"Python demo of TERCOM terrain contour matching: simulate a radar-altim...\", \"url\": \"https://github.com/alti3/python-tercom\", \"hackathon_fit\": \"high\", \"page\": \"catalog/repos/alti3__python-tercom.md\", \"stars\": 7}, {\"id\": \"repo:mzahana/tercom_nav\", \"kind\": \"repo\", \"name\": \"tercom_nav (TERCOM + ESKF)\", ... \"stars\": 85}]"}], "isError": false}}

>>> {"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"neighbors","arguments":{"id":"repo:snstac/pytak","limit":2}}}
<<< {"jsonrpc": "2.0", "id": 5, "result": {"content": [{"type": "text", "text": "[{\"id\": \"repo:opendroneid/receiver-android\", \"kind\": \"repo\", \"name\": \"OpenDroneID Android receiver\", ... \"stars\": 385, \"via\": \"repo:snstac/pytak <-integrates_with-\", \"hop\": 1}, {\"id\": \"repo:tak-product-center/atak-civ\", \"kind\": \"repo\", \"name\": \"ATAK-CIV (TAK Product Center)\", ... \"stars\": 297, \"via\": \"repo:snstac/pytak <-integrates_with-\", \"hop\": 1}]"}], "isError": false}}

>>> {"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"show","arguments":{"id":"repo:nope/nope"}}}
<<< {"jsonrpc": "2.0", "id": 6, "result": {"content": [{"type": "text", "text": "error: not found: repo:nope/nope"}], "isError": true}}

>>> {"jsonrpc":"2.0","id":7,"method":"bogus"}
<<< {"jsonrpc": "2.0", "id": 7, "error": {"code": -32601, "message": "method not found: bogus"}}
```

`show` on a real id (checked with `repo:dstl/stone-soup`) returns the full record JSON.

## How an agent should navigate the hub

Follow the cheapest path that answers the question, and only clone a repo when you are
about to build with it.

1. `llms.txt` - one-screen map of the hub for LLMs. If your checkout has no `llms.txt`
   yet, start at `AGENTS.md`.
2. `INDEX.md` - concept tree with counts and the high-fit repos. Pick 1-3 concepts.
3. `catalog/concepts/<concept>.md` - every repo, resource and sample for that concept,
   high hackathon fit first. Then `catalog/repos/<owner>__<name>.md` for hackathon notes
   and related links.
4. `index/records.jsonl` - one JSON record per line, for filtering in bulk
   (`grep '"hackathon_fit": "high"' index/records.jsonl`), or the MCP tools /
   `tools/query.py` which read the same file plus `graph/graph.json`.
5. `samples/` - working starting points. Each `sample.json` has a `verified` field; treat
   "unverified sketch" as untested code.

With the MCP server registered, the same flow is `concept` (no id) => `concept <id>` =>
`show <id>` => `neighbors <id>` for alternatives and integrations.

## Prompt recipes

Paste these into Claude Code / Cursor once the server is registered.

- "Use the navigation-index tools. Find a GNSS-denied localization stack for a fixed-wing
  UAV at 1 km AGL. Search for visual geolocalization and terrain-relative navigation,
  keep only `fit: high` or `medium`, then `show` the top 3 and compare camera
  requirements, compute needs and map data. Recommend one and say why."
- "List concepts with `concept` and no id. For `concept:magnetic-nav` give me the
  datasets and the repos with code, then `neighbors` of the best repo to find the dataset
  it was evaluated on."
- "We have a PX4 quad and a TAK server. Use `search` and `neighbors` from
  `repo:snstac/pytak` to find what we need to put the drone on ATAK, then open
  `samples/mavlink-to-tak-cot/README.md` and follow it."
- "For a 48 h build on GNSS jamming detection, use `concept concept:gnss-interference`
  with `kind: repo` and `fit: high`, and give me a setup-cost table from each record's
  `hackathon_notes`."
- "Before recommending any repo, `show` it and quote its `maturity` and `hackathon_notes`.
  Do not recommend repos whose maturity is `archived` unless nothing else fits."

## Extending it in a hackathon

- Add a tool: write a `tool_<name>(args)` function in `tools/mcp_server.py`, add it to
  `HANDLERS` and its schema to `TOOLS`.
- Point a team chat bot at the same server so non-coders can query the hub.
- Rebuild (`python3 tools/build.py`) after adding records; restart the MCP client so the
  server reloads (it caches the index on first call).

## Pitfalls

- Missing `index/records.jsonl` or `graph/graph.json` => the first tool call fails with
  an error result; run `python3 tools/build.py`.
- Never print to stdout from the server; stdout is the protocol channel.
- Use the absolute path in client configs; clients start servers from other directories.
- Search is keyword scoring, not semantic: use domain words the records use
  ("geolocalization", "tercom", "spoofing") and try synonyms if results are thin.
