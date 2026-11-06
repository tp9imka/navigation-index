# ROS MCP Server - integration card
<!-- about: repo:robotmcp/ros-mcp-server -->
One-line: MCP server that gives an LLM client (Claude Code, Codex CLI, Gemini CLI, Cursor...) discovery and pub/sub/service/action/param access to any ROS 1 or ROS 2 robot through rosbridge, with no changes to robot code; useful for an agent that inspects a nav stack ("is VIO publishing? what is the EKF covariance?") in a demo.

| | |
|---|---|
| Install | Client side: `claude mcp add ros-mcp -- uvx ros-mcp --transport=stdio` (PyPI package `ros-mcp`, v3.1.2 at time of writing, Python >= 3.10). Robot side: `sudo apt install ros-<distro>-rosbridge-server` and `ros2 launch rosbridge_server rosbridge_websocket_launch.xml`. |
| Runs on | Any host with Python 3.10+/uv for the server; robot needs ROS with rosbridge (ROS 2 Jazzy, Humble and others; ROS 1 too, per README). |
| Inputs | rosbridge WebSocket, default `127.0.0.1:9090` (`ros_mcp/main.py`); the LLM can call `connect_to_robot` to change IP/port. |
| Outputs | MCP tool results as JSON; images via `tools/images.py`. |
| Key API / entry points | Tools in `ros_mcp/tools/`: topics `get_topics`, `get_topic_type`, `get_topic_details`, `get_message_details`, `subscribe_once`, `subscribe_for_duration`, `publish_once`, `publish_for_durations`; services `get_services`, `get_service_type`, `get_service_details`, `call_service`; connection `connect_to_robot`, `ping_robots`; plus `actions.py`, `nodes.py`, `parameters.py`, `robot_config.py`. Resources `robot_specs`, `ros_metadata`. |
| Time to first result | Estimate: 15-20 min to list topics of a running ROS 2 sim from Claude Code. Assumes ROS 2 installed with rosbridge available. |
| License | Apache-2.0. |

## Minimal usage
From `docs/install/installation.md`. Not run.

```bash
# robot / sim machine
sudo apt install ros-${ROS_DISTRO}-rosbridge-server
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
# operator machine
claude mcp add ros-mcp -- uvx ros-mcp --transport=stdio
# prompt: "connect to the robot at 192.168.1.20 and tell me the rate and frame of /mavros/local_position/odom"
```

## Wiring it into a nav stack
- Read-mostly diagnostics over [MAVROS](./mavlink__mavros.md) topics (`/mavros/state`, `/mavros/local_position/odom`, `/mavros/gpsstatus/*`), PX4 `/fmu/out/*` ([px4_ros_com](./px4__px4_ros_com.md)), [Nav2](./ros-navigation__navigation2.md) and [robot_localization](./cra-ros-pkg__robot_localization.md) outputs.
- Simulators: Gazebo ([gz-sim](./gazebosim__gz-sim.md)) or Isaac Sim through their ROS bridges.
- Demos and tutorials: [demos-ros-mcp-server](../../catalog/repos/robotmcp__demos-ros-mcp-server.md).
- Catalog: [ros-mcp-server page](../../catalog/repos/robotmcp__ros-mcp-server.md).

## Gotchas
- `publish_once`, `call_service` and actions give the LLM full write access to anything rosbridge exposes, including MAVROS arming and setpoint topics. For flying vehicles add limits before anything flies (index note): run rosbridge with a topic/service allowlist or keep the agent on a read-only rosbridge instance.
- rosbridge on 9090 has no authentication by default; do not expose it beyond the lab network.
- High-rate topics (images, point clouds, 200 Hz IMU) through rosbridge JSON are slow; use `subscribe_once` or throttled topics.
- PX4 `/fmu/out/*` topics are best-effort QoS; check rosbridge subscribes with compatible QoS or you get no data.

## Alternatives
- [ROSA](./nasa-jpl__rosa.md): LangChain agent embedded in your own Python app rather than an MCP server.
- [wise-vision ros2_mcp](../../catalog/repos/wise-vision__ros2_mcp.md), [LCAS ros2_mcp](../../catalog/repos/lcas__ros2_mcp.md): ROS 2-native MCP servers without rosbridge.
- [MAVLinkMCP](./ion-g-ion__mavlinkmcp.md) when the robot is a MAVLink vehicle without ROS.

Sources: `README.md`, `docs/install/installation.md`, `pyproject.toml`, `ros_mcp/main.py`, `ros_mcp/tools/{topics,services,connection}.py` (function names), repo tree, releases API.
