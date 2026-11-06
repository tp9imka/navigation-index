# MAVProxy - integration card
<!-- about: repo:ardupilot/mavproxy -->
One-line: terminal MAVLink GCS and router in Python that `sim_vehicle.py` starts for you; its module system is the quickest place to bolt on a GNSS-anomaly alert, a fake-GPS injector or an ADS-B/Remote ID display.

| | |
|---|---|
| Install | `pip install MAVProxy` (latest release seen v1.8.75, 2026-09-24). Map/console modules need wxPython and OpenCV; on Ubuntu the ArduPilot prereq script installs them. |
| Runs on | Linux, macOS, Windows (README names maintainers for each). Pure Python plus optional GUI deps. |
| Inputs | `--master` connection (serial, `tcp:127.0.0.1:5760`, `udpin:...`), commands typed in the console or from `--cmd`, module-specific inputs (NMEA, NTRIP, Vicon/OptiTrack, ADS-B, ASTERIX, OpenDroneID). |
| Outputs | `--out` forwards (UDP/TCP) to other GCSes and scripts, `.tlog` logs, map/console GUIs, module outputs (KML, MQTT, REST). |
| Key API / entry points | `mavproxy.py --master=<conn> --out=udp:127.0.0.1:14551 [--console --map]`; console commands `param set/show`, `mode`, `arm throttle`, `module load <name>`; module base class `MAVProxy.modules.lib.mp_module.MPModule(mpstate, name, description)` with `mavlink_packet(self, m)`, `idle_task(self)`, `add_command(name, cb, desc)`, `unload(self)`. Relevant shipped modules (`MAVProxy/modules/`): `mavproxy_GPSInput.py`, `mavproxy_fakegps.py`, `mavproxy_nmeagps.py`, `mavproxy_ntrip.py`, `mavproxy_DGPS.py`, `mavproxy_vicon.py`, `mavproxy_optitrack`, `mavproxy_OpenDroneID.py`, `mavproxy_adsb.py`, `mavproxy_asterix.py`, `mavproxy_mqtt.py`, `mavproxy_restserver.py`, `mavproxy_cesium`, `mavproxy_example.py`. |
| Time to first result | Estimate: zero extra minutes if you run ArduPilot SITL (it is the default console); 30-60 min to write and load a custom module. |
| License | GPL-3.0-or-later. |

## Minimal usage
Custom module skeleton built on the `MPModule` methods above; copy `mavproxy_example.py` for the full pattern. Not run.

```python
# save as MAVProxy/modules/mavproxy_gpswatch.py, then: module load gpswatch
from MAVProxy.modules.lib import mp_module

class GPSWatch(mp_module.MPModule):
    def __init__(self, mpstate):
        super().__init__(mpstate, "gpswatch", "warn on GNSS degradation")
        self.last = None
    def mavlink_packet(self, m):
        if m.get_type() == "GPS_RAW_INT":
            if self.last is not None and m.satellites_visible + 5 < self.last:
                self.say("GPS satellites dropped to %u" % m.satellites_visible)
            self.last = m.satellites_visible

def init(mpstate):
    return GPSWatch(mpstate)
```

## Wiring it into a nav stack
- ArduPilot SITL: `sim_vehicle.py` runs MAVProxy with master TCP 5760 and `--out 127.0.0.1:14550` (instance 0), so [QGroundControl](./mavlink__qgroundcontrol.md), [MAVROS](./mavlink__mavros.md) or a [pymavlink](./ardupilot__pymavlink.md) script can attach on 14550. Add more with `output add 127.0.0.1:14560`.
- GNSS-denied tests: `GPSInput` module listens for JSON GPS on UDP port 25100 (change with `GPSInput.port`) and forwards as `GPS_INPUT` to [ArduPilot](./ardupilot__ardupilot.md) (`GPS1_TYPE=14`), handy for injecting a map-matching fix without writing MAVLink code. `vicon`/`optitrack` modules feed external-nav pose from motion capture.
- Detection side: `adsb` and `OpenDroneID` modules show traffic and Remote ID; for a common picture forward to TAK via [PyTAK](./snstac__pytak.md).
- Catalog: [MAVProxy page](../../catalog/repos/ardupilot__mavproxy.md).

## Gotchas
- GUI modules (map, console, graph) depend on wxPython; pip builds of wxPython on Linux are slow or fail. Open issues include #1711 (mission editor child process hangs after fork) and #1180 (pip install fails on `attrdict`, old). Use headless mode plus QGC if wx fights you.
- The `GPSInput` module expects a specific JSON field set; read the module source before sending.
- For multi-client routing on a companion computer, mavlink-router uses less CPU than MAVProxy.

## Alternatives
- [mavlink-router](./mavlink-router__mavlink-router.md) for routing only.
- [QGroundControl](./mavlink__qgroundcontrol.md) for a full GUI GCS.
- [MAVSDK-Python](./mavlink__mavsdk-python.md) for scripted control without a console.

Sources: `README.md`, `setup.py`, `MAVProxy/modules/` listing, `MAVProxy/modules/lib/mp_module.py` (class and method names), ArduPilot `Tools/autotest/sim_vehicle.py` (default ports), releases API, issue search.
