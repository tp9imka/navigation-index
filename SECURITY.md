# Security policy

## Scope

This policy covers the code in this repository:

- `tools/` - the build, query, link-check and MCP server scripts.
- `site/` - the static pages (Search, Learn, Graph and the Arena: Solver, Playground, Results).
- `samples/` - the runnable samples, including `samples/llm-mission-agent/mav_mcp_server.py`.

The hub ships no hosted service. The live site at https://navigation-index.pages.dev/ is a
static copy of this repository. It has no accounts, no backend and no user data.

## How to report

Use GitHub private vulnerability reporting on
[tp9imka/navigation-index](https://github.com/tp9imka/navigation-index): Security tab =>
Report a vulnerability. Do not open a public issue for a security problem.

Include the file, the commit, what an attacker can do, and the steps or input that show it.

## What to expect

This is a volunteer project. Reports are handled on a best-effort basis. There is no SLA and no
bug bounty. We will reply in the private report, fix what is in scope, and credit you in the fix
if you want.

## Third-party repositories

The hub indexes third-party repositories, papers and datasets. It does not maintain them. A
vulnerability in an indexed repository (PX4, ArduPilot, a SLAM package, any other record in
`catalog/`) must be reported to that project upstream, through its own security policy. If a
catalog record links to something unsafe or malicious, report that here, as a record correction
or privately.
