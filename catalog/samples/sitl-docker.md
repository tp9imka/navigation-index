# Sample: Headless SITL in Docker: ArduCopter and PX4 SIH with one compose file

`sample:sitl-docker` - code and walkthrough in [samples/sitl-docker](../../samples/sitl-docker/)

Dockerfiles and a compose file that run ArduCopter 4.6.3 SITL (with a simulated vicon for ExternalNav) and PX4 v1.17.0 SIH quadrotor without Gazebo or a GUI, plus a Python client image with pymavlink and mavsdk-grpc that shares the PX4 network namespace. Built and flown on linux/arm64 (Apple Silicon).

**Verification:** Built and ran on 2026-11-06 with Docker 29.5.2 on Apple Silicon (linux/arm64): both SITL images built, the ArduPilot, PX4 and VIO bridge samples flew against them, and docker compose (v5.7.0, run from the docker:29-cli image) brought both services up and a client container reached both. amd64 not tested.

**Concepts:** [Simulation and HIL/SITL](../concepts/simulation.md), [Autopilots and flight control](../concepts/autopilot.md), [MAVLink, ground control and C2 links](../concepts/mavlink-gcs.md)

**Tags:** `docker`, `compose`, `sitl`, `sih`, `ardupilot`, `px4`, `headless`, `arm64`, `mavsdk`, `pymavlink`

## Related

- uses: [ArduPilot](../repos/ardupilot__ardupilot.md)
- uses: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- uses: [MAVSDK-Python](../repos/mavlink__mavsdk-python.md)
- uses: [pymavlink](../repos/ardupilot__pymavlink.md)

_Indexed by lane(s): samples_
