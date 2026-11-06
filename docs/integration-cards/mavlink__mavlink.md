# MAVLink - integration card
<!-- about: repo:mavlink/mavlink -->
The message definitions (XML dialects) and the `mavgen` generator behind every PX4 / ArduPilot link: generate C, C++11 or other-language headers for `common.xml` or your own dialect, then send `GPS_INPUT`, `ODOMETRY` or `VISION_POSITION_ESTIMATE` to inject an alternative position source.

| | |
|---|---|
| Install | No release tags; track `master`. `git clone --recursive https://github.com/mavlink/mavlink.git && cd mavlink && python3 -m pip install -r pymavlink/requirements.txt` (README, Ubuntu 20.04/22.04/24.04). CMake install of the header-only lib: `cmake -Bbuild -H. -DCMAKE_INSTALL_PREFIX=install -DMAVLINK_DIALECT=common -DMAVLINK_VERSION=2.0 && cmake --build build --target install`. If you only need prebuilt C headers for `common`/`ardupilotmega`, the generated repo `mavlink/c_library_v2` exists (pushed 2026-11-06). Python users usually just `pip install pymavlink` (PyPI 2.4.50, which bundles generated dialects); see the [pymavlink card](./ardupilot__pymavlink.md). |
| Runs on | Generator: Python 3 on any OS. Generated C library: header-only, no allocation, builds for MCUs and hosts. No GPU. |
| Inputs | Dialect XML in `message_definitions/v1.0/`: `minimal.xml`, `standard.xml`, `common.xml`, `development.xml`, `all.xml`, `ardupilotmega.xml`, plus vendor dialects (`ASLUAV`, `AVSSUAS`, `csAirLink`, `cubepilot`, `icarous`, `loweheiser`, `marsh`, `paparazzi`, `stemstudios`, `storm32`, `uAvionix`). Your own dialect = an XML that `<include>`s `common.xml`. |
| Outputs | Generated headers (`generated/include/mavlink/v2.0/<dialect>/mavlink.h` with the README command; `include/mavlink/<dialect>/mavlink.h` from the CMake path, plus C++11 `.hpp` when `MAVLINK_ENABLE_CXX` is ON, default ON). Wire format MAVLink 1 or 2. |
| Key API / entry points | `python3 -m pymavlink.tools.mavgen --lang=C --wire-protocol=2.0 --output=<dir> <dialect.xml>` (README); `mavgenerate.py` (Tk GUI at repo root); CMake `find_package(MAVLink REQUIRED)` + `target_link_libraries(x PRIVATE MAVLink::mavlink)`; CMake vars `MAVLINK_DIALECT` (default `common`), `MAVLINK_VERSION` (default `2.0`). Generated C: `mavlink_msg_<name>_pack()`, `mavlink_msg_<name>_encode()`, `mavlink_msg_to_send_buffer()`, `mavlink_parse_char()`, `mavlink_msg_<name>_decode()`. Nav-relevant `common.xml` ids (checked in XML): `GPS_RAW_INT` 24, `GPS_STATUS` 25, `SET_GPS_GLOBAL_ORIGIN` 48, `VISION_POSITION_ESTIMATE` 102, `HIL_GPS` 113, `GPS2_RAW` 124, `ESTIMATOR_STATUS` 230, `GPS_INPUT` 232, `ODOMETRY` 331, `OPEN_DRONE_ID_BASIC_ID` 12900. `common.xml` defines 233 messages. |
| Time to first result | Estimate: 10 min to generate headers; 30-60 min to a C program that parses a SITL stream with `examples/c`. Assumes Python 3 and a compiler. |
| License | `COPYING`: generator is LGPL-3.0 (GitHub shows NOASSERTION), with an explicit exception: generated code embedded in your binary is MIT. So proprietary firmware linking generated headers is fine; modifying the generator itself is LGPL. |

## Minimal usage
Not run. From README.

```sh
git clone https://github.com/mavlink/mavlink.git --recursive && cd mavlink
python3 -m pip install -r pymavlink/requirements.txt
python3 -m pymavlink.tools.mavgen --lang=C --wire-protocol=2.0 \
  --output=generated/include/mavlink/v2.0 message_definitions/v1.0/common.xml
```

Custom dialect for a hackathon-specific message (e.g. a jamming-detector report), saved as `message_definitions/v1.0/mynav.xml`:

```xml
<mavlink>
  <include>common.xml</include>
  <dialect>NNN</dialect>
  <messages>
    <message id="NNNNN" name="MY_JAM_STATUS">
      <field type="uint64_t" name="time_usec" units="us">Timestamp</field>
      <field type="uint8_t" name="jam_level">0-255</field>
    </message>
  </messages>
</mavlink>
```

Pick dialect and message ids from the reserved ranges on mavlink.io (closed issue #2620 asks the site to clarify how to choose a `<dialect>` number). Then rebuild with `-DMAVLINK_DIALECT=mynav`.

## Wiring it into a nav stack
- Alt-nav => autopilot: send `GPS_INPUT` (fake-GNSS path; ArduPilot's MAVLink GPS type, `GPS_TYPE=14` per ArduPilot docs, not checked here) or `ODOMETRY` / `VISION_POSITION_ESTIMATE` (external vision path) from a companion computer. See [PX4](./px4__px4-autopilot.md), [ArduPilot](./ardupilot__ardupilot.md), [MAVROS](./mavlink__mavros.md), [vision_to_mavros](./thien94__vision_to_mavros.md).
- Routing: [mavlink-router](./mavlink-router__mavlink-router.md) or [MAVProxy](./ardupilot__mavproxy.md) fan one serial link out to GCS + companion.
- Higher level APIs that hide the messages: [MAVSDK](./mavlink__mavsdk.md), [pymavlink](./ardupilot__pymavlink.md), [rust-mavlink](../../catalog/repos/mavlink__rust-mavlink.md), [node-mavlink](../../catalog/repos/ardupilot__node-mavlink.md).
- Situational awareness: `OPEN_DRONE_ID_*` messages (12900+) carry Remote ID; see [ArduRemoteID](./ardupilot__arduremoteid.md).

## Gotchas
- Dialect drift: a custom message only works if every hop (autopilot, router, GCS, your script) was built with the same dialect; routers forward unknown ids but GCS and MAVSDK will drop or ignore them. Open issue #2506: some vendor dialect XMLs are unmaintained and not clearly marked.
- `development.xml` holds work-in-progress messages that can change; do not ship against it.
- `--recursive` matters: `pymavlink/` is a submodule pointing at `ardupilot/pymavlink`, and the README generation command imports it.
- `GPS_INPUT` vs `ODOMETRY` semantics differ per autopilot (ArduPilot vs PX4 EKF settings); the XML does not tell you which one your firmware consumes.
- MAVLink 2 message signing exists in the spec but was not checked in this pass; assume links are unauthenticated unless you configured signing on both ends.

## Alternatives
- [pymavlink](./ardupilot__pymavlink.md) - Python, prebuilt dialects, fastest for scripts and log parsing.
- [MAVSDK](./mavlink__mavsdk.md) - when you want `takeoff()` / telemetry streams instead of raw messages.
- [MAVROS](./mavlink__mavros.md) - when the rest of the stack is ROS.

Sources: `README.md`, `COPYING`, `.gitmodules`, `CMakeLists.txt`, `message_definitions/v1.0/` listing, `message_definitions/v1.0/common.xml` (message ids), `examples/` listing, issues #2506 #2620, PyPI JSON for `pymavlink`, GitHub metadata for `mavlink/c_library_v2` (github.com/mavlink/mavlink).
