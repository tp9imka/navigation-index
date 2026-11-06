# TypeFly - integration card
<!-- about: repo:typefly/typefly -->
One-line: natural-language-to-robot-plan loop (OpenAI planner + YOLO scene description + validated skill program) that runs on a webcam with no hardware, then on a DJI Tello, Unitree Go2 or Petoi quadruped.

| | |
|---|---|
| Install | Not on PyPI (`typefly` returns 404). `git clone https://github.com/typefly/TypeFly.git && cd TypeFly && pip install -e .` then `cp .env.example .env` and set `OPENAI_API_KEY`. Optional vision service container: `make serving_build` (NVIDIA Container Toolkit recommended). No release tags; package version 0.1.0. |
| Runs on | Python >=3.10. Linux or macOS (README: macOS native path uses Apple MPS). CPU works, GPU recommended for the YOLO service. Needs Internet for the OpenAI API. Hardware options: none (`virtual`, webcam), DJI/Ryze Tello (via `djitellopy`), Unitree Go2 (needs ROS 2 plus `go2_ros2_sdk`), Petoi Bittle/Nybble/Cub with OpenCatESP32 firmware and an ESP32-CAM. |
| Inputs | Typed instruction in the web UI; camera frames (webcam via `cv2.VideoCapture`, Tello video, Go2 via ROS 2, Petoi MJPEG); `typefly/config/robot_info.json` selects `robot_type` (`virtual`, `tello`, `go2`, `petoi`). |
| Outputs | LLM JSON plan whose `plan` field is a small Python program over registered skills; executed motion commands (`move_forward(dist)`, `rotate_left(deg)`, ...); detections and replies streamed to the web UI. |
| Key API / entry points | CLIs from `pyproject.toml`: `typefly-run` (`typefly.launcher:main`, starts vision service then UI), `typefly-serving` (`typefly.serving.run:main`), `typefly-webui` (`typefly.webui:main`). Classes: `RobotWrapper` (abstract, `typefly/robot_wrapper.py`: `_move(dx, dy)`, `_rotate(deg)`, `start()`, `stop()`), platform wrappers in `typefly/platforms/` (`tello_wrapper.py`, `go2_wrapper.py`, `petoi_wrapper.py`, `virtual_robot_wrapper.py`), `LLMPlanner(robot, model_type=ModelType.GPT4O)`, `plan_execution.validate_plan(...)`. Ports: UI `127.0.0.1:50000`, vision gateway `EDGE_SERVICE_PORT` 50049, YOLO workers 50050. |
| Time to first result | Estimate: 20-30 min to "Find a bottle" working on a laptop webcam, assuming Python 3.10+, an OpenAI key with credit, and a fast download of torch and YOLO weights. Add 1-2 h for a Tello (second network adapter, Wi-Fi join). |
| License | Apache-2.0 (LICENSE.md). Depends on `ultralytics` (AGPL-3.0) and calls the OpenAI API (commercial terms, data leaves the machine). |

## Minimal usage

Not run. From the README quick start (webcam, no hardware):

```bash
git clone https://github.com/typefly/TypeFly.git && cd TypeFly
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env          # set OPENAI_API_KEY=sk-...
typefly-run                   # open http://localhost:50000
```

Type `Find a bottle, tell me its height and take a picture of it.` The `virtual` robot does not move; it only finds, measures and photographs.

For a Tello: set `{"robot_id": "tello1", "robot_type": "tello", "extra": {}}` in `typefly/config/robot_info.json`, join the Tello Wi-Fi on one adapter and keep Internet on another.

## Wiring it into a nav stack

- TypeFly has no localization or map: motion skills are relative (`move_forward(dist)`, `rotate_left(deg)`), executed open loop by the platform wrapper. To put it on a real autopilot, write a `RobotWrapper` subclass whose `_move` / `_rotate` send body-frame setpoints over MAVLink ([pymavlink](./ardupilot__pymavlink.md), [MAVSDK-Python](./mavlink__mavsdk-python.md)) or ROS 2 ([PX4 ROS 2 interface](./auterion__px4-ros2-interface-lib.md)), and let the autopilot's own estimator hold position.
- Perception swap: the YOLO service is a gRPC worker (`typefly/serving/yolo_service.py`, `typefly/proto/hyrch_serving.proto`); a Jetson-side detector ([jetson-inference](./dusty-nv__jetson-inference.md)) could answer the same proto.
- Compare with tool-calling agents: [ROSA](./nasa-jpl__rosa.md) and [MAVLink MCP](./ion-g-ion__mavlinkmcp.md) call tools step by step; TypeFly emits a whole plan program in one LLM call, then validates and runs it locally (the paper's latency argument, see `res:typefly-2023` in the index).

Catalog page: [catalog/repos/typefly__typefly.md](../../catalog/repos/typefly__typefly.md). Concepts: [llm-agents-robotics](../../catalog/concepts/llm-agents-robotics.md), [mission-planning](../../catalog/concepts/mission-planning.md).

## Gotchas

- Hard requirement on OpenAI: `llm_wrapper.py` only implements GPT models (`gpt-4`, `gpt-4o`, `gpt-5`); anything else raises `ValueError`. No local LLM path without code changes. Default planner model is GPT-4o.
- Only the Tello is a drone. It is an indoor toy quad with no GNSS; the "drone" story assumes that specific vehicle. Tello needs its own Wi-Fi plus a second adapter for Internet (README).
- AGPL via `ultralytics`: fine for a hackathon demo, a problem if you ship a closed product.
- README says the first run downloads `yolov8m.pt` (~50 MB); the code (`serving/yolo_service.py`) loads `yolo26s.pt`. Expect the README to lag the code.
- Plan safety: generated plans are parsed with `ast` and checked against a whitelist of skills, statement types and loop budgets (`plan_execution.py`) before `compile` - better than raw `exec`, but still LLM output driving motors. Keep a manual kill switch; `RobotWrapper.emergency_shutdown()` exists.
- `robot_info.json` is committed, so local edits conflict on `git pull` (README note).
- Older issues: webcolors incompatibility (#3), Docker build context error (#8); both closed.

## Alternatives

- [ROSA](./nasa-jpl__rosa.md) - LangChain agent over ROS; prefer when the robot already runs ROS and you want inspection plus control.
- [MAVLink MCP](./ion-g-ion__mavlinkmcp.md) - MCP tools for an ArduPilot/PX4 vehicle; prefer for real autopilots and SITL.
- [ROS MCP server](./robotmcp__ros-mcp-server.md) - generic ROS topic/service access from any MCP client.

Sources: `gh api repos/typefly/typefly` (Apache-2.0, pushed 2026-07-08), PyPI JSON (typefly 404), README.md, pyproject.toml, .env.example, LICENSE.md, typefly/llm_wrapper.py, typefly/llm_planner.py, typefly/llm_controller.py, typefly/robot_wrapper.py, typefly/plan_execution.py, typefly/serving/yolo_service.py, typefly/config/robot_info.example.json, issues #1, #2, #3, #4, #8; `gh api repos/ultralytics/ultralytics` (AGPL-3.0).
