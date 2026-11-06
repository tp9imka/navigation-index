# MOOS-IvP - integration card
<!-- about: repo:moos-ivp/moos-ivp -->
One-line: MIT's marine autonomy stack - MOOSDB pub/sub plus the IvP Helm behaviour engine with waypoint, loiter, obstacle and COLREGs avoidance behaviours, a marine vehicle sim and a 2D viewer - runnable as a desktop sim in under an hour.

| | |
|---|---|
| Install | Source only: `git clone https://github.com/moos-ivp/moos-ivp && cd moos-ivp && ./build.sh` (or `./build-moos.sh && ./build-ivp.sh`), then add `moos-ivp/bin` to `PATH`. Ubuntu deps (README-GNULINUX.txt list): `g++ cmake xterm patch libfltk1.3-dev freeglut3-dev libpng-dev libjpeg-dev libxft-dev libxinerama-dev libtiff5-dev espeak`. Latest GitHub release v24.8.1. Docker: `docker/moos-ivp/Dockerfile` (ubuntu:24.04, `minrobot` stage, no GUI); CI pushes `ghcr.io/moos-ivp/moos-ivp/indev` (tags not checked). |
| Runs on | Linux, macOS, Windows (separate README-* files); Ubuntu is the main target. Headless builds `./build.sh --minrobot` (`-m`) or `--minrobotx` (`-mx`, required on Pi OS per `build.sh`). No GPU. |
| Inputs | MOOS variables posted to MOOSDB (TCP, `ServerPort` in the `.moos` file, 9000 in `s1_alpha`): own-ship `NAV_X`, `NAV_Y` (metres, local frame from `LatOrigin`/`LongOrigin`), `NAV_HEADING`, `NAV_SPEED`, `NAV_DEPTH`; contacts as `NODE_REPORT` strings; mission flags (`DEPLOY`, `RETURN`); behaviour files `.bhv`, process configs `.moos`. |
| Outputs | Helm decisions `DESIRED_HEADING`, `DESIRED_SPEED` (and `DESIRED_DEPTH` for UUVs), consumed by `pMarinePIDV22` => `DESIRED_RUDDER` / `DESIRED_THRUST`, or by your own vehicle interface. Logs as `.alog` (pLogger), viewable with `alogview`. |
| Key API / entry points | Launch `pAntler <mission>.moos [--MOOSTimeWarp=N]`; apps `MOOSDB`, `pHelmIvP`, `pMarineViewer`, `uSimMarineV22`/`V23`, `pMarinePIDV22`, `pNodeReporter`, `pContactMgrV20`, `pObstacleMgr`, `uFldCollisionDetect`, `pLogger`, `uMAC`, `uXMS`, `uPokeDB`. Behaviours: `BHV_Waypoint`, `BHV_ConstantSpeed`, `BHV_Loiter`, `BHV_AvdColregsV22` / `V26` (`ivp/src/lib_behaviors-colregs`). Scaffolding: `app_gen_moos_app` for a new `i*` interface app. C++ base class for apps is `AppCastingMOOSApp` / `CMOOSApp` (MOOS core). |
| Time to first result | Estimate: 30-60 min to build on Ubuntu and run `s1_alpha` in pMarineViewer; a day to write an interface app that feeds a real estimator. Assumes Ubuntu 22.04/24.04 with FLTK from apt. |
| License | GPLv3 and LGPLv3 mix, optional commercial licence (COPYING.md). Which modules are LGPL vs GPL is not stated in COPYING.md (not checked per file). GitHub metadata: NOASSERTION. |

## Minimal usage
Not run. From README-GNULINUX.txt and `ivp/missions/s1_alpha/launch.sh`.

```sh
sudo apt install g++ cmake xterm patch libfltk1.3-dev freeglut3-dev libpng-dev libjpeg-dev \
  libxft-dev libxinerama-dev libtiff5-dev espeak
git clone https://github.com/moos-ivp/moos-ivp && cd moos-ivp && ./build.sh
export PATH=$PWD/bin:$PATH
cd ivp/missions/s1_alpha && ./launch.sh 10    # numeric arg = time warp; starts pAntler + uMAC
# in pMarineViewer click DEPLOY; the vehicle follows BHV_Waypoint from alpha.bhv
```

COLREGs and obstacle examples: `ivp/missions/s1_alpha_obsavoid`, `m2_berta_obstacles`, `m10_jake` and the `ufld_*` multi-vehicle missions.

## Wiring it into a nav stack
- MOOS-IvP does not estimate pose: whatever posts `NAV_X/NAV_Y/NAV_HEADING/NAV_SPEED` is the nav source. In sim that is `uSimMarineV22`; on a vehicle it is your interface app. A GNSS-denied demo replaces it with a DR/visual/terrain estimator posting the same variables, and the helm, COLREGs behaviours and viewer stay unchanged.
- No MAVLink or ROS app in `ivp/src`. To drive an [ArduPilot](./ardupilot__ardupilot.md) boat (e.g. on [BlueOS](./bluerobotics__blueos.md)), write an `iArduPilot`-style app with `app_gen_moos_app` that maps `DESIRED_HEADING/SPEED` to guided-mode MAVLink and back-fills `NAV_*` from `GLOBAL_POSITION_INT` (lat/lon => local via MOOSGeodesy). [pymavlink](./ardupilot__pymavlink.md) plus pymoos is the quick prototype route (pymoos not indexed, not checked).
- Contacts: AIS ([pyais](../../catalog/repos/m0r13n__pyais.md), [AIS-catcher](../../catalog/repos/jvde-github__ais-catcher.md)) or a tracker (e.g. [VIMMJIPDA](../../catalog/repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md), [Stone Soup](./dstl__stone-soup.md)) converted to `NODE_REPORT` for `pContactMgrV20`.
- Chart display for operators: [OpenCPN](./opencpn__opencpn.md) fed with RMC from the same `NAV_*` values.
- Concepts: [maritime-nav](../../catalog/concepts/maritime-nav.md), [path-planning](../../catalog/concepts/path-planning.md), [obstacle-avoidance](../../catalog/concepts/obstacle-avoidance.md), [multi-agent](../../catalog/concepts/multi-agent.md). Catalog page: [catalog/repos/moos-ivp__moos-ivp.md](../../catalog/repos/moos-ivp__moos-ivp.md).

## Gotchas
- The one-line apt command in README-GNULINUX.txt (dated 2021, "tested on Ubuntu 18.04") names `libpng12-dev` and `libtiff4-dev`, which modern Ubuntu does not ship; use `libpng-dev` and `libtiff5-dev` (or `libtiff-dev`) as in the package list above it. FLTK is no longer vendored.
- Bundled MOOSGeodesy mis-converts UTM when the origin and the point are in different zones (#72, open). Keep `LatOrigin/LongOrigin` inside the operating area; do not span a zone boundary.
- `build-ivp.sh --clean` was broken (#5, closed); build failures on main reported in #28 (closed). Use the release tag if main fails.
- Docker `moos` user password issue (#88, closed). The GHCR image path is `indev`, i.e. development builds.
- Pi OS needs `--minrobotx`; `build.sh` stops otherwise.
- Time warp > 1 is sim-only; keep `--MOOSTimeWarp=1` with real hardware in the loop.
- Licensing: GPLv3 parts propagate to linked apps you distribute; LGPLv3 parts allow linking. Check headers of the libraries you link before shipping.

## Alternatives
- [colav-simulator](./ntnu-itk-autonomous-ship-lab__colav-simulator.md) - Python, Gymnasium env, ENC grounding hazards; prefer for COLAV algorithm research and RL rather than a deployable autonomy runtime.
- [moos-ivp-masters](../../catalog/repos/d2snc__moos-ivp-masters.md) - extension tree built on MOOS-IvP; look there for worked COLREGs extensions.
- [Nav2](./ros-navigation__navigation2.md) or [VRX](../../catalog/repos/osrf__vrx.md) - prefer when the team is ROS 2 native.

Sources: `gh api repos/moos-ivp/moos-ivp` (NOASSERTION, release v24.8.1 2025-11-16), README.md, COPYING.md, README-GNULINUX.txt, build.sh (flags, Pi OS check), docker/moos-ivp/Dockerfile, .github/workflows/docker.yaml (GHCR `indev`), ivp/src listing, ivp/src/lib_behaviors-colregs listing, ivp/missions listing, ivp/missions/s1_alpha/{launch.sh,alpha.moos,alpha.bhv}, issues #5, #28, #72, #88.
