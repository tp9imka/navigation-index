# TypeFly

`repo:typefly/typefly` - <https://github.com/typefly/TypeFly>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 118 | Python | Apache-2.0 | 2026-07-08 | False | research-prototype | high |

LLM-based robot control framework: an OpenAI model turns a natural-language request plus a YOLO scene description into a short Python plan built from the robot's registered skills, which is then executed. Ships wrappers for a virtual webcam robot, DJI Tello, Unitree Go2 and Petoi.

**Why it matters:** Shows how to constrain LLM output into a small, verifiable command language for drones, cutting latency and risk.

**Hackathon notes:** `pip install -e .`, add an OpenAI key and run `typefly-run`; the default virtual robot uses a webcam, so no hardware is needed. A Tello needs both a Wi-Fi and an ethernet adapter. Swap in a MAVSDK-based robot wrapper to target PX4.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [typefly__typefly](../../docs/integration-cards/typefly__typefly.md) (integration-cards)

**Concepts:** [LLM agents for robotics and navigation](../../catalog/concepts/llm-agents-robotics.md), [Mission planning and routing](../../catalog/concepts/mission-planning.md)

**Tags:** `llm`, `tello`, `dsl`, `drone`

**Domains:** air

## Related

- alternative_to: [PromptCraft-Robotics](../../catalog/repos/microsoft__promptcraft-robotics.md)
- integrates_with: [TypeFly: Flying Drones with Large Language Model](../../catalog/resources/typefly-2023.md)

## Referenced by

- [TypeFly: Flying Drones with Large Language Model](../../catalog/resources/typefly-2023.md) (has_code)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
