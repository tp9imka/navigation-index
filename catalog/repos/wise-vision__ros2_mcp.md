# WiseVision ROS 2 MCP

`repo:wise-vision/ros2_mcp` - <https://github.com/wise-vision/ros2_mcp>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 98 | Python | MPL-2.0 | 2026-10-21 | False | active-research | medium |

MCP server that lets AI agents discover and operate ROS 2 robots: topic echo/publish, services, actions and introspection, implemented natively in ROS 2 rather than through rosbridge.

**Why it matters:** Native ROS 2 alternative for LLM control without a rosbridge hop.

**Hackathon notes:** Fastest path is the Docker image (wisevision/ros2_mcp:jazzy or :humble) as the MCP client's stdio command - ROS 2 does not need to be installed on the host. Start with ROS2_MCP_READONLY=1 so the agent can inspect but not publish.

**Concepts:** [LLM agents for robotics and navigation](../../catalog/concepts/llm-agents-robotics.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `mcp`, `ros2`, `agent`

**Domains:** multi

## Related

- alternative_to: [ROS MCP Server](../../catalog/repos/robotmcp__ros-mcp-server.md)
- alternative_to: [LCAS ROS 2 MCP](../../catalog/repos/lcas__ros2_mcp.md)

## Referenced by

- [LCAS ROS 2 MCP](../../catalog/repos/lcas__ros2_mcp.md) (alternative_to)
- [ROS MCP Server](../../catalog/repos/robotmcp__ros-mcp-server.md) (alternative_to)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
