# Sample: Querying the hub from LLM agents via MCP

`sample:llm-agent-usage` - code and walkthrough in [samples/llm-agent-usage](../../samples/llm-agent-usage/)

A stdlib-only MCP stdio server (tools/mcp_server.py) exposes search, show, concept and neighbors over the hub's index and graph so Claude Code, Cursor and other MCP clients can query it as tools. The README covers client registration, a navigation path for agents (llms.txt, INDEX.md, concept pages, records.jsonl) and prompt recipes.

**Verification:** tools/mcp_server.py ran with python3.14.7 stdlib on 2026-11-06 by piping demo_requests.jsonl into it (initialize, tools/list, tools/call for search/concept/neighbors/show, error paths); transcript shown in README. Client registration (Claude Code, Cursor, others) was not exercised.

**Concepts:** [LLM agents for robotics and navigation](../../catalog/concepts/llm-agents-robotics.md)

**Tags:** `mcp`, `json-rpc`, `claude-code`, `cursor`, `agents`, `stdlib`

## Referenced by

- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): samples_
