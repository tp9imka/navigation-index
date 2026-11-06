#!/usr/bin/env python3
"""MCP server (stdio, JSON-RPC 2.0, stdlib only) over the navigation index.

Exposes tools search / show / concept / neighbors, reusing tools/query.py.
Needs index/records.jsonl and graph/graph.json: run `python3 tools/build.py` first.

  claude mcp add navigation-index -- python3 /abs/path/tools/mcp_server.py
"""
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import query  # noqa: E402

SERVER_NAME = "navigation-index"
SERVER_VERSION = "0.1.0"
SUPPORTED_PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
DEFAULT_LIMIT = 10
MAX_LIMIT = 100
MAX_DEPTH = 3
SUMMARY_CHARS = 300

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602

FILTERS = {
    "kind": {"type": "string", "description": "repo, concept, paper, doc, dataset, standard, talk, ..."},
    "fit": {"type": "string", "enum": ["high", "medium", "low"], "description": "hackathon fit"},
    "domain": {"type": "string", "description": "air, ground, maritime, underwater, space, dismounted, multi"},
    "limit": {"type": "integer", "minimum": 1, "maximum": MAX_LIMIT, "default": DEFAULT_LIMIT},
}

TOOLS = [
    {
        "name": "search",
        "description": "Ranked keyword search over repos, resources, concepts and samples of the "
                       "navigation/PNT hub. Returns ids, one-line summaries and URLs.",
        "inputSchema": {"type": "object", "required": ["query"], "properties": {
            "query": {"type": "string", "description": "space-separated keywords"},
            "concept": {"type": "string", "description": "restrict to a concept id, e.g. concept:vio"},
            **FILTERS}},
    },
    {
        "name": "show",
        "description": "Full record for one id (repo:owner/name, res:slug, concept:x, sample:x).",
        "inputSchema": {"type": "object", "required": ["id"],
                        "properties": {"id": {"type": "string"}}},
    },
    {
        "name": "concept",
        "description": "Everything tagged with a concept, high hackathon fit first. "
                       "Omit id to list all concept ids with record counts.",
        "inputSchema": {"type": "object", "properties": {
            "id": {"type": "string", "description": "concept id, e.g. concept:terrain-nav"}, **FILTERS}},
    },
    {
        "name": "neighbors",
        "description": "Graph walk from an id: related repos, resources, concepts and the edge "
                       "that links them (integrates_with, alternative_to, has_code, about, ...).",
        "inputSchema": {"type": "object", "required": ["id"], "properties": {
            "id": {"type": "string"},
            "depth": {"type": "integer", "minimum": 1, "maximum": MAX_DEPTH, "default": 1},
            **FILTERS}},
    },
]

_data = None


def data():
    global _data
    if _data is None:
        _data = query.load()
    return _data


def filters(args, concept=None):
    return SimpleNamespace(kind=args.get("kind"), fit=args.get("fit"),
                           domain=args.get("domain"), concept=concept or args.get("concept"))


def limit_of(args):
    return max(1, min(int(args.get("limit", DEFAULT_LIMIT)), MAX_LIMIT))


def brief(r, **extra):
    out = {"id": r["id"], "kind": r["kind"], "name": r.get("name") or r.get("title"),
           "summary": (r.get("summary") or "")[:SUMMARY_CHARS]}
    for key in ("url", "hackathon_fit", "page"):
        if r.get(key):
            out[key] = r[key]
    stars = (r.get("github") or {}).get("stargazers_count")
    if stars:
        out["stars"] = stars
    out.update(extra)
    return out


def tool_search(args):
    recs, _ = data()
    terms = [t for t in str(args["query"]).lower().split() if t]
    f = filters(args)
    hits = [(query.score(r, terms), r) for r in recs.values() if query.matches_filters(r, f)]
    hits = [h for h in hits if h[0] > 0]
    hits.sort(key=lambda h: (-h[0], -((h[1].get("github") or {}).get("stargazers_count") or 0)))
    return [brief(r, score=s) for s, r in hits[:limit_of(args)]]


def tool_show(args):
    recs, _ = data()
    if args["id"] not in recs:
        raise ToolError(f"not found: {args['id']}")
    return recs[args["id"]]


def tool_concept(args):
    recs, _ = data()
    cid = args.get("id")
    if not cid:
        counts = defaultdict(int)
        for r in recs.values():
            for c in r.get("concepts", []):
                counts[c] += 1
        return [{"id": c["id"], "name": c["name"], "count": counts[c["id"]]}
                for c in recs.values() if c["kind"] == "concept"]
    if cid not in recs:
        raise ToolError(f"unknown concept: {cid}")
    f = filters(args, concept=cid)
    res = [r for r in recs.values() if query.matches_filters(r, f)]
    res.sort(key=lambda r: ({"high": 0, "medium": 1, "low": 2}.get(r.get("hackathon_fit"), 3), r["kind"]))
    return [brief(r) for r in res[:limit_of(args)]]


def tool_neighbors(args):
    recs, adj = data()
    start = args["id"]
    if start not in recs and start not in adj:
        raise ToolError(f"not found: {start}")
    depth = max(1, min(int(args.get("depth", 1)), MAX_DEPTH))
    f = filters(args)
    seen, q, res = {start}, deque([(start, 0)]), []
    while q and len(res) < limit_of(args):
        node, d = q.popleft()
        if d >= depth:
            continue
        for nb, rel, direction in adj[node]:
            if nb in seen:
                continue
            seen.add(nb)
            if nb in recs and query.matches_filters(recs[nb], f):
                via = f"{node} -{rel}->" if direction == "out" else f"{node} <-{rel}-"
                res.append(brief(recs[nb], via=via, hop=d + 1))
            q.append((nb, d + 1))
    return res[:limit_of(args)]


HANDLERS = {"search": tool_search, "show": tool_show, "concept": tool_concept, "neighbors": tool_neighbors}


class ToolError(Exception):
    pass


class RpcError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def call_tool(params):
    name, args = params.get("name"), params.get("arguments") or {}
    if name not in HANDLERS:
        raise RpcError(INVALID_PARAMS, f"unknown tool: {name}")
    try:
        result = HANDLERS[name](args)
    except (ToolError, KeyError, ValueError, TypeError) as e:
        # tool-level failures go back as isError content so the model can recover
        return {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True}
    return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
            "isError": False}


def initialize(params):
    requested = params.get("protocolVersion")
    version = requested if requested in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
    return {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": "Navigation/PNT open-source hub. Start with concept (no id) or search, "
                            "then show for details and neighbors for related work."}


METHODS = {
    "initialize": initialize,
    "ping": lambda p: {},
    "tools/list": lambda p: {"tools": TOOLS},
    "tools/call": call_tool,
}


def handle(msg):
    """Return a response dict, or None for notifications."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return {"jsonrpc": "2.0", "id": msg.get("id") if isinstance(msg, dict) else None,
                "error": {"code": INVALID_REQUEST, "message": "invalid request"}}
    is_notification = "id" not in msg
    method = METHODS.get(msg["method"])
    if is_notification:
        return None
    if method is None:
        return {"jsonrpc": "2.0", "id": msg["id"],
                "error": {"code": METHOD_NOT_FOUND, "message": f"method not found: {msg['method']}"}}
    try:
        return {"jsonrpc": "2.0", "id": msg["id"], "result": method(msg.get("params") or {})}
    except RpcError as e:
        return {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": e.code, "message": str(e)}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": PARSE_ERROR, "message": str(e)}}
        else:
            reply = handle(msg)
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
