"""Stdlib-only Cursor-on-Target (CoT) event builder for UAV position reports."""
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

FRIENDLY_UAV_TYPE = "a-f-A-M-F-Q"
HOW_MACHINE_GPS = "m-g"
UNKNOWN_ERROR_M = 9999999.0  # CoT convention for "error not known"
DEFAULT_STALE_S = 30
COT_TIME_FMT = "%Y-%m-%dT%H:%M:%S.%f"

# MAVLink GLOBAL_POSITION_INT scaling
DEG_E7 = 1e7
MM_PER_M = 1000.0
CM_PER_M = 100.0
CDEG_PER_DEG = 100.0
HDG_UNKNOWN = 65535


def cot_time(t: datetime) -> str:
    """ISO 8601 UTC with millisecond precision, e.g. 2026-11-06T12:00:00.000Z."""
    return t.astimezone(timezone.utc).strftime(COT_TIME_FMT)[:-3] + "Z"


def build_event(uid, lat, lon, hae, course=None, speed=None, callsign=None,
                ce=UNKNOWN_ERROR_M, le=UNKNOWN_ERROR_M, now=None,
                stale_s=DEFAULT_STALE_S, cot_type=FRIENDLY_UAV_TYPE) -> bytes:
    now = now or datetime.now(timezone.utc)
    event = ET.Element("event", {
        "version": "2.0",
        "type": cot_type,
        "uid": uid,
        "how": HOW_MACHINE_GPS,
        "time": cot_time(now),
        "start": cot_time(now),
        "stale": cot_time(now + timedelta(seconds=stale_s)),
    })
    ET.SubElement(event, "point", {
        "lat": f"{lat:.7f}", "lon": f"{lon:.7f}", "hae": f"{hae:.2f}",
        "ce": f"{ce:.1f}", "le": f"{le:.1f}",
    })
    detail = ET.SubElement(event, "detail")
    if callsign:
        ET.SubElement(detail, "contact", {"callsign": callsign})
    if course is not None and speed is not None:
        ET.SubElement(detail, "track", {"course": f"{course:.1f}", "speed": f"{speed:.2f}"})
    return ET.tostring(event, encoding="utf-8")


def from_global_position_int(msg, uid, callsign=None, geoid_separation_m=0.0, now=None) -> bytes:
    """msg: any object with GLOBAL_POSITION_INT fields (lat, lon, alt, vx, vy, hdg).

    MAVLink alt is AMSL; CoT hae is height above the WGS84 ellipsoid, so pass the
    local geoid separation (N) if you know it: hae = AMSL + N.
    """
    vx, vy = msg.vx / CM_PER_M, msg.vy / CM_PER_M  # north, east m/s
    speed = math.hypot(vx, vy)
    if msg.hdg != HDG_UNKNOWN:
        course = msg.hdg / CDEG_PER_DEG
    else:
        course = math.degrees(math.atan2(vy, vx)) % 360.0
    return build_event(
        uid=uid,
        lat=msg.lat / DEG_E7,
        lon=msg.lon / DEG_E7,
        hae=msg.alt / MM_PER_M + geoid_separation_m,
        course=course,
        speed=speed,
        callsign=callsign,
        now=now,
    )


if __name__ == "__main__":
    print(build_event("uav-demo-1", 51.5007, -0.1246, 120.0, course=90.0, speed=15.0,
                      callsign="DEMO-1").decode())
