# CLAUDE.md

@AGENTS.md

Claude Code specifics:

- Register the hub once per machine: `claude mcp add navigation-index -- python3 /abs/path/navigation-index/tools/mcp_server.py`.
- Run `make test` before reporting work as done; paste the tail of the output.
- Long commands (SITL, docker builds): run in the foreground with a timeout, not in the background.
