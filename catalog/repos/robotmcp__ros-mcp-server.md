# ROS MCP Server

`repo:robotmcp/ros-mcp-server` - <https://github.com/robotmcp/ros-mcp-server>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,514 | Python | Apache-2.0 | 2026-11-05 | False | active-research | high |

Model Context Protocol server that exposes ROS topics, services and parameters (via rosbridge) to LLM clients such as Claude or GPT, for ROS 1 and ROS 2.

**Why it matters:** Fastest way to let an LLM inspect and drive an existing robot without changing robot code.

**Hackathon notes:** Run rosbridge on the robot and point the MCP client config at the server; works with sim (Gazebo/Isaac). Add safety limits before anything flies.

## Deep dives

- [_index-flight-c2](../../docs/integration-cards/_index-flight-c2.md) (integration-cards)
- [robotmcp__ros-mcp-server](../../docs/integration-cards/robotmcp__ros-mcp-server.md) (integration-cards)

**Concepts:** [LLM agents for robotics and navigation](../../catalog/concepts/llm-agents-robotics.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `mcp`, `rosbridge`, `llm`, `ros2`

**Domains:** multi

## Related

- same_org: [ROS MCP Server demos](../../catalog/repos/robotmcp__demos-ros-mcp-server.md)
- alternative_to: [WiseVision ROS 2 MCP](../../catalog/repos/wise-vision__ros2_mcp.md)
- alternative_to: [ROSA (ROS Agent)](../../catalog/repos/nasa-jpl__rosa.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ROSA (ROS Agent)](../../catalog/repos/nasa-jpl__rosa.md) (alternative_to)
- [ROS MCP Server demos](../../catalog/repos/robotmcp__demos-ros-mcp-server.md) (extends)
- [WiseVision ROS 2 MCP](../../catalog/repos/wise-vision__ros2_mcp.md) (alternative_to)
- [Model Context Protocol specification](../../catalog/resources/mcp-specification.md) (explains)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
