# LLM agents for robotics and navigation

`concept:llm-agents-robotics`

Language models driving robots, mission planning, MCP servers for drones/ROS/GIS.

## Samples (1)

- [Querying the hub from LLM agents via MCP](../samples/llm-agent-usage.md) - A stdlib-only MCP stdio server (tools/mcp_server.py) exposes search, show, concept and neighbors over the hub's index and graph so Claude Code, Cursor and other MCP clients can query it as tools.

## Repositories (30)

- [jetson-containers](../repos/dusty-nv__jetson-containers.md) - fit: high - Build system and prebuilt containers for ML on Jetson (PyTorch, ROS, LLMs, VLMs) matched to JetPack versions.
- [ROSA (ROS Agent)](../repos/nasa-jpl__rosa.md) - fit: high - NASA JPL's LangChain-based AI agent that lets operators query and command ROS 1 and ROS 2 systems in natural language through a set of ROS introspection and control tools.
- [ROS MCP Server](../repos/robotmcp__ros-mcp-server.md) - fit: high - Model Context Protocol server that exposes ROS topics, services and parameters (via rosbridge) to LLM clients such as Claude or GPT, for ROS 1 and ROS 2.
- [GNM / ViNT / NoMaD](../repos/robodhruv__visualnav-transformer.md) - fit: high - Code and checkpoints for general visual navigation foundation models (GNM, ViNT, NoMaD) that drive robots from camera images toward image goals or explore, with ROS deployment code.
- [QGIS MCP](../repos/jjsantos01__qgis_mcp.md) - fit: high - MCP server plus QGIS plugin that lets an LLM create projects, load layers, run processing algorithms and execute PyQGIS code in QGIS Desktop.
- [GIS MCP Server](../repos/mahdin75__gis-mcp.md) - fit: high - MCP server giving LLMs geospatial operations through Shapely, PyProj, GeoPandas and Rasterio: geometry ops, CRS transforms, distances and raster analysis, without a desktop GIS.
- [TypeFly](../repos/typefly__typefly.md) - fit: high - Framework for LLM-based drone task planning that compiles natural-language requests into a compact robot language (MiniSpec) executed on a DJI Tello with vision services.
- [MAVLinkMCP](../repos/ion-g-ion__mavlinkmcp.md) - fit: high - MCP server bridging an LLM to a drone over MAVLink, exposing arming, takeoff, waypoint and telemetry tools via MAVSDK.
- [PromptCraft-Robotics](../repos/microsoft__promptcraft-robotics.md) - fit: medium - Microsoft's collection of prompts and an AirSim-based ChatGPT drone simulator accompanying the 'ChatGPT for Robotics' work.
- [InternNav](../repos/internrobotics__internnav.md) - fit: medium - Open platform for building and evaluating generalist navigation foundation models, covering VLN and related embodied navigation tasks with training and benchmarks.
- [ConceptGraphs](../repos/concept-graphs__concept-graphs.md) - fit: medium - Builds open-vocabulary 3D scene graphs from RGB-D by associating 2D foundation-model detections across views, then lets an LLM plan over the graph.
- [VLMaps](../repos/vlmaps__vlmaps.md) - fit: medium - Builds visual-language maps by fusing pretrained visual-language features into a 3D reconstruction, enabling open-vocabulary landmark navigation from natural language.
- [LLM-Geo (Autonomous GIS)](../repos/gladcolor__llm-geo.md) - fit: medium - Research prototype of an LLM-driven 'autonomous GIS' that turns a spatial question into a solution graph, generates code and executes the analysis to return maps and numbers.
- [qgis-mcp (nkarasiak)](../repos/nkarasiak__qgis-mcp.md) - fit: medium - Actively maintained MCP bridge connecting AI agents to QGIS Desktop, with a broader tool set than the original qgis_mcp.
- [AerialVLN](../repos/airvln__airvln.md) - fit: medium - Benchmark and simulator (AirSim/UE-based) for vision-and-language navigation by UAVs in city-scale environments, with baseline agents.
- [OpenFly](../repos/shailab-ipec__openfly-platform.md) - fit: medium - Platform for outdoor aerial vision-language navigation: multi-engine simulators (UE, GTA V, Google Earth, 3DGS), automated data collection toolchain, a large benchmark and a keyframe-aware VLN model.
- [GRID playground (AirGen)](../repos/genrobo__grid-playground.md) - fit: medium - Notebooks and examples for the GRID platform from Scaled Foundations, which pairs the AirSim-derived AirGen simulator with foundation-model perception and LLM-driven robot control.
- [CityNav](../repos/water-cookie__citynav.md) - fit: medium - Language-goal aerial navigation dataset over real-city 3D point clouds with geographic information, plus baselines that use map-based landmark grounding.
- [Co-NavGPT](../repos/ybgdgh__co-navgpt.md) - fit: medium - Multi-robot exploration and object search where an LLM assigns frontier goals to robots from a merged semantic map.
- [WiseVision ROS 2 MCP](../repos/wise-vision__ros2_mcp.md) - fit: medium - MCP server that lets AI agents discover and operate ROS 2 robots: topic echo/publish, services, actions and introspection, implemented natively in ROS 2 rather than through rosbridge.
- [SatNav](../repos/eku127__satnav.md) - fit: medium - Scalable benchmark and platform for long-horizon UAV vision-language navigation built from satellite imagery (NeurIPS 2026 Datasets track).
- [ROS MCP Server demos](../repos/robotmcp__demos-ros-mcp-server.md) - fit: medium - Demos and tutorials for connecting LLMs to robots via the ROS MCP server, including simulated mobile robots.
- [mavlink-mcp (ArduPilot)](../repos/deepakpopli__mavlink-mcp.md) - fit: medium - MCP server for flying ArduPilot vehicles from AI agents over MAVLink, covering missions, camera vision and SITL workflows.
- [ardupilot-mcp (safety-gated)](../repos/rmeadomavic__ardupilot-mcp.md) - fit: medium - SITL-first MCP server for talking to ArduPilot vehicles over MAVLink, with explicit safety gating of commands.
- [ROS-LLM](../repos/auromix__ros-llm.md) - fit: low - Framework for natural-language interaction with ROS robots, letting an LLM call robot functions and chain behaviors.
- [NaVid / Uni-NaVid](../repos/jzhzhang__navid-vln-ce.md) - fit: low - Evaluation code for NaVid and Uni-NaVid, video-based VLMs that plan the next navigation step from monocular RGB history in continuous VLN environments.
- [NavGPT](../repos/gengzezhou__navgpt.md) - fit: low - Purely LLM-based vision-and-language navigation agent that reasons explicitly over textual observations to choose actions (AAAI 2024).
- [LM-Nav](../repos/blazejosinski__lm_nav.md) - fit: low - Code for LM-Nav, which composes a language model, CLIP and a visual navigation model to follow natural-language route instructions without language-annotated robot data.
- [3DG-VLN](../repos/xuefanfu__3dg-vln.md) - fit: low - UAV vision-language navigation framework using 3D grounding for more precise goal localization (2026 research code).
- [LCAS ROS 2 MCP](../repos/lcas__ros2_mcp.md) - fit: low - ROS 2 MCP server from the Lincoln Centre for Autonomous Systems, exposing topics, services and actions to LLM agents.

## Documents, talks, courses, datasets (15)

- [A Multi-Robot Platform for Robotic Triage Combining Onboard Sensing and Foundation Models](../resources/arxiv-multi-robot-triage-platform.md) - paper - Technical report from a DARPA Triage Challenge team describing a multi-robot system and fine-tuned open vision-language models for injury identification.
- [AerialVLN: Vision-and-Language Navigation for UAVs](../resources/aerialvln-iccv-2023.md) - paper - ICCV 2023 paper introducing a city-scale UAV vision-and-language navigation task, simulator and baselines.
- [ChatGPT for Robotics: Design Principles and Model Abilities](../resources/microsoft-chatgpt-robotics-2023.md) - paper - Early study of prompting strategies and API design for using ChatGPT to generate robot and drone control code, with AirSim demos.
- [CityNav: A Large-Scale Dataset for Real-World Aerial Navigation](../resources/citynav-2024.md) - paper - Introduces a language-goal aerial navigation dataset built on real-city 3D data with geographic metadata, and baselines using map-based grounding.
- [ConceptGraphs: Open-Vocabulary 3D Scene Graphs for Perception and Planning](../resources/conceptgraphs-2023.md) - paper - Builds object-centric 3D scene graphs with open-vocabulary labels from RGB-D and uses an LLM to plan over them.
- [Enabling Novel Mission Operations and Interactions with ROSA: The Robot Operating System Agent](../resources/jpl-rosa-paper-2024.md) - paper - Describes ROSA, an LLM agent that lets operators inspect and command ROS systems in natural language through a curated tool set, and discusses safety and operational considerations.
- [LM-Nav: Robotic Navigation with Large Pre-Trained Models of Language, Vision, and Action](../resources/lm-nav-2022.md) - paper - Combines an LLM for landmark extraction, CLIP for grounding and a visual navigation model to follow long route instructions outdoors.
- [Model Context Protocol specification](../resources/mcp-specification.md) - standard - The specification for MCP, the protocol LLM clients use to call tools and read resources from servers; the basis of the ROS, MAVLink and QGIS MCP servers.
- [NaVid: Video-based VLM Plans the Next Step for Vision-and-Language Navigation](../resources/navid-vln-2024.md) - paper - Video-based VLM that plans navigation actions from monocular RGB history without maps, odometry or depth.
- [NoMaD: Goal Masked Diffusion Policies for Navigation and Exploration](../resources/nomad-diffusion-nav-2023.md) - paper - Single diffusion policy that handles both goal-directed navigation and undirected exploration by masking the goal.
- [NVIDIA Jetson AI Lab](../resources/nvidia-jetson-ai-lab.md) - doc - Tutorial hub for running generative AI, VLMs and robotics models on Jetson devices, built around jetson-containers.
- [OpenFly: A Comprehensive Platform for Aerial Vision-Language Navigation](../resources/openfly-aerial-vln-2025.md) - paper - Presents a multi-engine aerial VLN platform with automated data generation, a large outdoor benchmark and a keyframe-aware VLN model.
- [TypeFly: Flying Drones with Large Language Model](../resources/typefly-2023.md) - paper - Proposes a compact drone programming language for LLM output, cutting token count and latency while keeping plans checkable.
- [ViNT: A Foundation Model for Visual Navigation](../resources/vint-foundation-model-2023.md) - paper - Trains a transformer navigation policy across many robot datasets and shows it adapts to new robots and tasks with little data.
- [Visual Language Maps for Robot Navigation](../resources/vlmaps-2022.md) - paper - Fuses visual-language features into 3D maps so robots can localize landmarks named in open-vocabulary language and navigate to them.

