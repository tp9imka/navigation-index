# Headless SITL in Docker (ArduPilot + PX4 SIH)

<!-- about: repo:ardupilot/ardupilot, repo:px4/px4-autopilot, repo:mavlink/mavsdk-python, repo:ardupilot/pymavlink -->

One `docker compose` command gives a hackathon team a flying simulated copter without
Gazebo, a GPU or a GUI. Used by `samples/ardupilot-ekf3-source-switch`,
`samples/px4-sitl-gps-denial` and `samples/vio-to-mavlink-bridge`.

| Service | Image | What runs | MAVLink |
|---|---|---|---|
| `ardupilot` | `nav-sitl-ardupilot:copter-4.6.3` | ArduCopter `Copter-4.6.3` SITL binary, quad model, simulated vicon on SERIAL5 | TCP 5760 (SERIAL0), 5762 (SERIAL1), 5763 (SERIAL2), published to the host |
| `px4` | `nav-sitl-px4:v1.17.0` | PX4 `v1.17.0`, `sihsim_quadx` (SIH: physics inside PX4) | UDP, localhost only inside the container (see below) |
| `client` | `nav-sitl-client:latest` | Python 3.12 + pymavlink 2.4.50 + mavsdk-grpc 4.0.5 + pyulog 1.3.0 | shares the `px4` network namespace |

## Run

```sh
cd samples/sitl-docker
docker compose up -d ardupilot px4            # first run builds both images
docker compose run --rm client python ardupilot-ekf3-source-switch/source_switch.py \
    --connect tcp:ardupilot:5762 --setup
docker compose run --rm client python ardupilot-ekf3-source-switch/source_switch.py \
    --connect tcp:ardupilot:5762
docker compose run --rm client python px4-sitl-gps-denial/gps_denial_mission.py \
    --deny-via sim-param
docker compose down
```

Note: the sample scripts themselves were run against containers started with the
equivalent plain `docker run` commands (`docker run -d --name px4 nav-sitl-px4:v1.17.0`,
then the client with `--network container:px4`); through `docker compose run` only a
connectivity probe was run (below).

The `client` service mounts `samples/` at `/samples` and starts there. ArduPilot is also
reachable from the host (`tcp:127.0.0.1:5762`), so the ArduPilot samples can run from a
host venv with `pip install pymavlink`.

## What was verified (2026-11-06, Docker 29.5.2, Apple Silicon, linux/arm64)

- Both images built from these Dockerfiles. Build times on this machine: ArduPilot
  ~8.5 min, PX4 ~26 min (most of it the recursive submodule clone). Image sizes:
  ArduPilot 1.85 GB, PX4 214 MB (multi-stage), client 558 MB.
- `docker compose config` and `up -d ardupilot px4` worked with Compose v5.7.0 (run from
  the `docker:29-cli` image, since this host has no compose plugin). A client container
  started with `docker compose run` got an ArduPilot heartbeat over `tcp:ardupilot:5762`
  and PX4 health `global_ok True home_ok True` over MAVSDK `udpin://0.0.0.0:14540`.
- The three samples above ran against these containers; their READMEs carry the output.
- amd64: not tested. Both Dockerfiles avoid arch-specific steps, so they should build, but
  that is not verified.

## Why it is built this way

- **ArduPilot**: the `arducopter` SITL binary is started directly (no `sim_vehicle.py`,
  no MAVProxy), with `--serial0 tcp:0` so it does not block waiting for a client and
  `--serial5 sim:vicon:` so the EKF3 ExternalNav sample has a pose source. Parameters
  persist in `/sitl/eeprom.bin` across the in-SITL reboot, but not across container
  re-creation.
- **PX4**: the official `px4io/px4-dev:v1.17.0` image works (multi-arch, built fine here)
  but is ~11 GB on disk because it carries the NuttX toolchains, and it filled the
  Docker VM disk during this session. The Dockerfile uses a plain `ubuntu:24.04` builder
  with `Tools/setup/requirements.txt` and copies only `bin/` and `etc/` into the runtime.
- **PX4 network**: the SITL startup prints `MAVLink only on localhost (set param
  MAV_{i}_BROADCAST = 1 to enable network)`. Rather than change PX4 parameters, the
  client joins the `px4` container's network namespace (`network_mode: service:px4`), so
  `udpin://0.0.0.0:14540` (MAVSDK) and `udpout:127.0.0.1:14580` (pymavlink) work as on a
  native install. To reach PX4 from the host instead, set `MAV_0_BROADCAST 1` / use
  `mavlink start -t <host-ip>` in the `pxh>` shell; not tested here.
- **Shell access to PX4**: `docker compose exec px4 sh -c 'cd /px4/rootfs &&
  /px4/bin/px4-param show EKF2_GPS_CTRL'`. Every `pxh>` command has a `px4-<cmd>` client
  in `/px4/bin` (`px4-listener`, `px4-param`, `px4-commander`).

## Pitfalls seen while verifying

- **Docker Desktop disk**: when the VM disk is full, ArduPilot refuses to arm with
  `Arm: Logging failed` (it cannot create its dataflash log). Check `docker system df`.
- **Docker Desktop memory**: the VM here had 7.7 GB shared with other containers; Julia
  in `samples/magnav-quickstart` was OOM-killed until `--heap-size-hint` was set.
- **Bind mounts from `/tmp` or `/private/tmp` on macOS are empty** inside containers
  unless that path is in Docker Desktop's file sharing list. Keep the checkout under your
  home directory, or `docker cp` files in.
- ArduPilot SITL takes ~20-30 s after boot before pre-arm checks pass (`AHRS: waiting for
  home`, `Gyros inconsistent` while the simulated IMUs settle). Scripts must retry arming.
