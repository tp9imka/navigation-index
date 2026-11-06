# ROSA - integration card
<!-- about: repo:nasa-jpl/rosa -->
One-line: NASA JPL's LangChain agent for ROS 1 and ROS 2 with built-in introspection tools (nodes, topics, services, params, logs) and an extension point for your own tools; embed it in a Python node to give operators a natural-language view of the nav stack.

| | |
|---|---|
| Install | `pip3 install jpl-rosa` (latest release seen v1.0.10, 2026-03-17). TurtleSim demo via Docker: `./demo.sh` in the repo (Wiki "Guide: TurtleSim Demo"). |
| Runs on | Python 3.9+, ROS Noetic or ROS 2 (README). LLM via LangChain: `ChatOpenAI`, `AzureChatOpenAI`, `ChatAnthropic`, `ChatOllama` (type union in `rosa.py`), so it can run against a local Ollama model offline. |
| Inputs | Natural-language queries; the live ROS graph through the built-in tools (ROS 2 tools shell out to the `ros2` CLI per `tools/ros2.py` function names). |
| Outputs | Text answers; side effects through tools (topic publish, service call, param set) if not blacklisted; streaming events via `astream`. |
| Key API / entry points | `from rosa import ROSA`; `ROSA(ros_version=1|2, llm=..., tools=None, tool_packages=None, prompts=None, blacklist=None, ...)`; `agent.invoke(query) -> str`; `agent.astream(query)`; `agent.clear_chat()`; `RobotSystemPrompts` for robot-specific prompts. Built-in ROS 2 tools (`src/rosa/tools/ros2.py`): `ros2_node_list`, `ros2_topic_list`, `ros2_topic_echo`, `ros2_topic_info`, `ros2_service_list`, `ros2_service_call`, `ros2_param_get`, `ros2_param_set`, `ros2_topic_pub`, `ros2_doctor`, `ros2_log_directories`. Example custom agent: `src/turtle_agent/scripts/turtle_agent.py`. |
| Time to first result | Estimate: 30 min to run `agent.invoke("list topics with publishers but no subscribers")` against a ROS 2 sim with an API key or local Ollama model. Docker TurtleSim demo longer on first image build. |
| License | Apache-2.0. |

## Minimal usage
From README, ROS 2 variant. Not run.

```python
from langchain_ollama import ChatOllama          # or ChatOpenAI / ChatAnthropic
from rosa import ROSA

llm = ChatOllama(model="llama3.1", temperature=0)
agent = ROSA(ros_version=2, llm=llm,
             blacklist=["/mavros/setpoint"])   # hides matching ROS names from the tools
print(agent.invoke("Is /mavros/vision_pose/pose publishing, at what rate, and who subscribes?"))
```
`blacklist` is injected into every tool call and filters ROS entity names (nodes, topics, services) returned or acted on (`tools/__init__.py` `inject_blacklist`, `ros2_node_list(..., blacklist)`); it does not remove tools. Write tools (`ros2_topic_pub`, `ros2_service_call`, `ros2_param_set`) stay available unless you build the agent without them.

## Wiring it into a nav stack
- Add custom LangChain `@tool` functions that read [MAVROS](./mavlink__mavros.md) or PX4 `/fmu/out/*` ([px4_ros_com](./px4__px4_ros_com.md)) status and summarise EKF/GPS health, then pass them via `tools=[...]`.
- Works alongside [Nav2](./ros-navigation__navigation2.md) and [robot_localization](./cra-ros-pkg__robot_localization.md) as a diagnostic assistant.
- Catalog: [ROSA page](../../catalog/repos/nasa-jpl__rosa.md); paper: [ROSA paper](../../catalog/resources/jpl-rosa-paper-2024.md).

## Gotchas
- Built on LangChain `AgentExecutor`; LangChain API churn can break installs. Pin the versions from a working `jpl-rosa` release.
- Write-capable tools are on by default and `blacklist` only hides ROS names; blacklist setpoint/command topics and services of a real vehicle and use a read-only prompt.
- Closed #63: install failure on Ubuntu 20.04 / Python 3.8 / Galactic; use Python 3.9+ and a current ROS 2 distro.
- Shelling out to `ros2` CLI per query is slow on a loaded companion computer.

## Alternatives
- [ros-mcp-server](./robotmcp__ros-mcp-server.md): MCP over rosbridge, use any MCP client instead of embedding an agent.
- [ROS-LLM](../../catalog/repos/auromix__ros-llm.md): framework for LLM function calling on ROS robots.

Sources: `README.md`, `setup.py`, `src/rosa/rosa.py` (constructor, methods, ChatModel union), `src/rosa/tools/__init__.py` (`inject_blacklist`), `src/rosa/tools/ros2.py` (tool names), repo tree, releases API, issue search (#63).
