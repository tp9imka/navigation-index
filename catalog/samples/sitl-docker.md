# Sample: Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file

`sample:sitl-docker` - code and walkthrough in [samples/sitl-docker](../../samples/sitl-docker/)

Dockerfiles and a compose file that run ArduCopter 4.6.3 SITL (with a simulated vicon for ExternalNav) and PX4 v1.17.0 SIH quadrotor without Gazebo or a GUI, plus a Python client image with pymavlink and mavsdk-grpc that shares the PX4 network namespace. Built and flown on linux/arm64 (Apple Silicon).

**Verification:** Built and ran on 2026-11-06 with Docker 29.5.2 on Apple Silicon (linux/arm64): both SITL images built, the ArduPilot, PX4 and VIO bridge samples flew against them, and docker compose (v5.7.0, run from the docker:29-cli image) brought both services up and a client container reached both. amd64 not tested.

## Practical readiness

| Compute | Hardware | Offline | Setup | Dataset download | Tested platforms | Validation |
|---|---|---|---|---|---|---|
| unknown | unknown | unknown | unknown | unknown | unknown | unverified |

**Main limitation:** Read the sample verification; readiness has not been curated.

**Concepts:** [Simulation and HIL/SITL](../../catalog/concepts/simulation.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md)

**Tags:** `docker`, `compose`, `sitl`, `sih`, `ardupilot`, `px4`, `headless`, `arm64`, `mavsdk`, `pymavlink`

## Related

- uses: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)
- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md)
- uses: [pymavlink](../../catalog/repos/ardupilot__pymavlink.md)

## Referenced by

- [Challenge 2 "Autonomous Frontiers": entry point](../../docs/challenge-2-autonomous-flight.md) (mentions)
- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)
- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Guidance and planning for a navigation entry](../../docs/guidance-planning.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Close-area A=>B: planning and mapping for a small multirotor](../../docs/research/close-area-nav/01-planning-and-mapping.md) (mentions)
- [03. Adapt aerodynamic navigation parameters only when the data make them identifiable](../../docs/research/innovation-prior-art/03-identifiability-gated-aero-adaptation.md) (mentions)
- [Wider innovation scan: ten algorithmic directions for a 48h navigation POC](../../docs/research/innovation-prior-art/04-wider-innovation-scan.md) (mentions)
- [Upstream findings](../../docs/upstream-findings.md) (mentions)
- [Fixed-wing golden demo: ArduPlane 4.6.3 SITL on a 27.6 km route, coherent GPS drag, golden-demo monitor, EKF3 switch to ExternalNav fed by measured day (VPAIR) and night (thermal) geoloc fix models vs airspeed dead reckoning only](../../catalog/samples/golden-demo-fixedwing.md) (uses)

_Indexed by lane(s): samples_
