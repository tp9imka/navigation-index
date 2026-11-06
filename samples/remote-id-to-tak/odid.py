"""Stdlib decoder for ASTM F3411 / ASD-STAN EN 4709-002 broadcast Remote ID (Open Drone ID).

Mirrors opendroneid-core-c (libopendroneid/opendroneid.c) decode semantics, including
its float32 arithmetic, string handling and pack validation, so results compare bit-exact
against the C library (see test_odid.py). Field names follow the C structs.
"""
import struct

MESSAGE_SIZE = 25
PACK_MAX_MESSAGES = 9
ID_SIZE = 20
STR_SIZE = 23
AUTH_MAX_PAGES = 16
BASIC_ID_MAX_MESSAGES = 2
AUTH_PAGE_ZERO_DATA_SIZE = 17
AUTH_PAGE_NONZERO_DATA_SIZE = 23

BASIC_ID, LOCATION, AUTH, SELF_ID, SYSTEM, OPERATOR_ID, PACKED = 0, 1, 2, 3, 4, 5, 0xF
INVALID = 0xFF

IDTYPE_NONE, IDTYPE_SERIAL, IDTYPE_CAA, IDTYPE_UTM_UUID, IDTYPE_SESSION = 0, 1, 2, 3, 4

# Wire scaling (opendroneid.c constants)
SPEED_DIV = (0.25, 0.75)
VSPEED_DIV = 0.5
LATLON_MULT = 10_000_000
ALT_DIV = 0.5
ALT_ADDER = 1000
AREA_RADIUS_MULT = 10
TS_TENTHS = 10
UINT8_MAX = 255

# Sentinels meaning "unknown"
INV_DIR = 361.0
INV_SPEED_H = 255.0
INV_SPEED_V = 63.0
INV_ALT = -1000.0
INV_TIMESTAMP = 0xFFFF

UA_TYPES = ["none", "aeroplane", "helicopter_or_multirotor", "gyroplane", "hybrid_lift",
            "ornithopter", "glider", "kite", "free_balloon", "captive_balloon", "airship",
            "free_fall_parachute", "rocket", "tethered_powered_aircraft", "ground_obstacle", "other"]
ID_TYPES = ["none", "serial_number", "caa_registration_id", "utm_assigned_uuid", "specific_session_id"]
STATUS = ["undeclared", "ground", "airborne", "emergency", "remote_id_system_failure"]
OPERATOR_LOCATION_TYPES = ["takeoff", "live_gnss", "fixed"]

# Enum => metres (core-c decodeHorizontalAccuracy etc). 7808 for 4 NM is what core-c
# returns (4 NM is 7408 m); kept so outputs match the reference.
HORIZ_ACC_M = [18520, 18520, 7808, 3704, 1852, 926, 555.6, 185.2, 92.6, 30, 10, 3, 1]
VERT_ACC_M = [150, 150, 45, 25, 10, 3, 1]
SPEED_ACC_MS = [10, 10, 3, 1, 0.3]


def f32(x: float) -> float:
    """Round a Python float to IEEE float32, as the C library stores it."""
    return struct.unpack("<f", struct.pack("<f", x))[0]


def horiz_accuracy_m(enum: int) -> float:
    return f32(HORIZ_ACC_M[enum]) if 0 <= enum < len(HORIZ_ACC_M) else 18520.0


def vert_accuracy_m(enum: int) -> float:
    return float(VERT_ACC_M[enum]) if 0 <= enum < len(VERT_ACC_M) else 150.0


def speed_accuracy_ms(enum: int) -> float:
    return f32(SPEED_ACC_MS[enum]) if 0 <= enum < len(SPEED_ACC_MS) else 10.0


def message_type(byte0: int) -> int:
    t = byte0 >> 4
    return t if t in (BASIC_ID, LOCATION, AUTH, SELF_ID, SYSTEM, OPERATOR_ID, PACKED) else INVALID


def _cstr(raw: bytes, size: int) -> bytes:
    """safe_dec_copyfill: copy up to the first NUL, at most size bytes, zero-pad to size."""
    s = raw[:size].split(b"\0", 1)[0]
    return s + b"\0" * (size - len(s))


def _alt(enc: int) -> float:
    return f32(enc * ALT_DIV - ALT_ADDER)


def decode_basic_id(m: bytes) -> dict:
    ua_type, id_type = m[1] & 0x0F, m[1] >> 4
    raw = m[2:2 + ID_SIZE]
    uasid = _cstr(raw, ID_SIZE) if id_type in (IDTYPE_SERIAL, IDTYPE_CAA) else raw
    return {"UAType": ua_type, "IDType": id_type, "UASID": uasid}


def decode_location(m: bytes) -> dict:
    flags = m[1]
    speed_mult, ew, height_type, status = flags & 1, (flags >> 1) & 1, (flags >> 2) & 1, flags >> 4
    direction, speed_h, speed_v = m[2], m[3], struct.unpack_from("<b", m, 4)[0]
    lat, lon, alt_baro, alt_geo, height = struct.unpack_from("<iiHHH", m, 5)
    ts = struct.unpack_from("<H", m, 21)[0]
    if speed_mult:
        sh = f32(speed_h * SPEED_DIV[1] + UINT8_MAX * SPEED_DIV[0])
    else:
        sh = f32(speed_h * SPEED_DIV[0])
    return {
        "Status": status,
        "Direction": float(direction + 180 if ew else direction),
        "SpeedHorizontal": sh,
        "SpeedVertical": f32(speed_v * VSPEED_DIV),
        "Latitude": lat / LATLON_MULT,
        "Longitude": lon / LATLON_MULT,
        "AltitudeBaro": _alt(alt_baro),
        "AltitudeGeo": _alt(alt_geo),
        "HeightType": height_type,
        "Height": _alt(height),
        "HorizAccuracy": m[19] & 0x0F,
        "VertAccuracy": m[19] >> 4,
        "BaroAccuracy": m[20] >> 4,
        "SpeedAccuracy": m[20] & 0x0F,
        "TSAccuracy": m[23] & 0x0F,
        "TimeStamp": float(INV_TIMESTAMP) if ts == INV_TIMESTAMP else f32(ts / TS_TENTHS),
    }


def decode_auth(m: bytes):
    page, auth_type = m[1] & 0x0F, m[1] >> 4
    if page > AUTH_MAX_PAGES - 1:
        return None
    out = {"DataPage": page, "AuthType": auth_type, "LastPageIndex": 0, "Length": 0, "Timestamp": 0}
    if page == 0:
        last, length = m[2], m[3]
        if last >= AUTH_MAX_PAGES:
            return None
        if AUTH_PAGE_ZERO_DATA_SIZE + last * AUTH_PAGE_NONZERO_DATA_SIZE < length:
            return None
        out.update(LastPageIndex=last, Length=length, Timestamp=struct.unpack_from("<I", m, 4)[0])
        data = m[8:8 + AUTH_PAGE_ZERO_DATA_SIZE]
    else:
        data = m[2:2 + AUTH_PAGE_NONZERO_DATA_SIZE]
    out["AuthData"] = data + b"\0" * (AUTH_PAGE_NONZERO_DATA_SIZE - len(data))
    return out


def decode_self_id(m: bytes) -> dict:
    return {"DescType": m[1], "Desc": _cstr(m[2:2 + STR_SIZE], STR_SIZE)}


def decode_system(m: bytes) -> dict:
    op_lat, op_lon, area_count = struct.unpack_from("<iiH", m, 2)
    radius = m[12]
    ceiling, floor = struct.unpack_from("<HH", m, 13)
    op_alt, ts = struct.unpack_from("<HI", m, 18)
    return {
        "OperatorLocationType": m[1] & 0x03,
        "ClassificationType": (m[1] >> 2) & 0x07,
        "OperatorLatitude": op_lat / LATLON_MULT,
        "OperatorLongitude": op_lon / LATLON_MULT,
        "AreaCount": area_count,
        "AreaRadius": radius * AREA_RADIUS_MULT,
        "AreaCeiling": _alt(ceiling),
        "AreaFloor": _alt(floor),
        "CategoryEU": m[17] >> 4,
        "ClassEU": m[17] & 0x0F,
        "OperatorAltitudeGeo": _alt(op_alt),
        "Timestamp": ts,
    }


def decode_operator_id(m: bytes) -> dict:
    return {"OperatorIdType": m[1], "OperatorId": _cstr(m[2:2 + ID_SIZE], ID_SIZE)}


def new_uas() -> dict:
    """Equivalent of odid_initUasData: holds only the messages decoded so far."""
    return {}


def _check_pack_content(msgs) -> bool:
    if not 0 < len(msgs) <= PACK_MAX_MESSAGES:
        return False
    counts = [0] * 6
    for m in msgs:
        t = message_type(m[0])
        if t > OPERATOR_ID:
            return False
        counts[t] += 1
    return (counts[BASIC_ID] <= BASIC_ID_MAX_MESSAGES and counts[LOCATION] <= 1
            and counts[AUTH] <= AUTH_MAX_PAGES and counts[SELF_ID] <= 1
            and counts[SYSTEM] <= 1 and counts[OPERATOR_ID] <= 1)


def decode_pack(uas: dict, buf: bytes) -> bool:
    if len(buf) < 3 or message_type(buf[0]) != PACKED or buf[1] != MESSAGE_SIZE:
        return False
    n = buf[2]
    if len(buf) < 3 + n * MESSAGE_SIZE:
        return False  # truncated; core-c's odid_message_process_pack also rejects this
    msgs = [buf[3 + i * MESSAGE_SIZE: 3 + (i + 1) * MESSAGE_SIZE] for i in range(n)]
    if not _check_pack_content(msgs):
        return False
    for m in msgs:
        decode_message(uas, m)
    return True


def decode_message(uas: dict, buf: bytes) -> int:
    """decodeOpenDroneID: decode one 25-byte message (or a pack) into uas. Returns the type or INVALID."""
    if len(buf) < MESSAGE_SIZE:
        return INVALID
    t = message_type(buf[0])
    m = bytes(buf[:MESSAGE_SIZE])
    if t == BASIC_ID:
        new = decode_basic_id(m)
        for i in range(BASIC_ID_MAX_MESSAGES):
            stored = uas.get(f"BasicID{i}", {}).get("IDType", IDTYPE_NONE)
            if stored in (IDTYPE_NONE, new["IDType"]):
                uas[f"BasicID{i}"] = new
                return BASIC_ID
    elif t == LOCATION:
        uas["Location"] = decode_location(m)
        return LOCATION
    elif t == AUTH:
        a = decode_auth(m)
        if a is not None:
            uas[f"Auth{a['DataPage']}"] = a
            return AUTH
    elif t == SELF_ID:
        uas["SelfID"] = decode_self_id(m)
        return SELF_ID
    elif t == SYSTEM:
        uas["System"] = decode_system(m)
        return SYSTEM
    elif t == OPERATOR_ID:
        uas["OperatorID"] = decode_operator_id(m)
        return OPERATOR_ID
    elif t == PACKED:
        if decode_pack(uas, bytes(buf)):
            return PACKED
    return INVALID


def decode(buf: bytes):
    """Decode a message or pack into a fresh UAS record. Returns (type, uas)."""
    uas = new_uas()
    return decode_message(uas, buf), uas


# --- transports -----------------------------------------------------------------------

ASTM_BLE_UUID = 0xFFFA
ODID_APP_CODE = 0x0D
ASD_STAN_OUI = bytes.fromhex("fa0bbc")
WIFI_ALLIANCE_OUI = bytes.fromhex("506f9a")
NAN_OUI_TYPE = 0x13
NAN_ODID_SERVICE_ID = bytes.fromhex("8869199d9209")
NAN_ATTR_SERVICE_DESCRIPTOR = 0x03


def from_ble_service_data(sd: bytes):
    """sd = BLE service data after the 16-bit UUID 0xFFFA: app code 0x0D, counter, message or pack."""
    if len(sd) < 2 + MESSAGE_SIZE or sd[0] != ODID_APP_CODE:
        return None
    return sd[1], sd[2:]


def from_beacon_vendor_ie(body: bytes):
    """body = vendor-specific IE payload (after id/len): OUI FA0BBC, type 0x0D, counter, pack."""
    if len(body) < 5 or body[:3] != ASD_STAN_OUI or body[3] != ODID_APP_CODE:
        return None
    return body[4], body[5:]


def from_nan_sda(attr: bytes):
    """attr = NAN Service Descriptor Attribute incl. 3-byte header. Returns (counter, pack)."""
    if len(attr) < 13 or attr[0] != NAN_ATTR_SERVICE_DESCRIPTOR or attr[3:9] != NAN_ODID_SERVICE_ID:
        return None
    si_len = attr[12]
    si = attr[13:13 + si_len]
    if len(si) != si_len or si_len < 1:
        return None
    return si[0], si[1:]


# --- human-friendly view --------------------------------------------------------------

def _txt(b: bytes) -> str:
    return b.split(b"\0", 1)[0].decode("ascii", "replace")


def summarize(uas: dict) -> dict:
    """Flatten a decoded UAS record into receiver-friendly fields (None = not present/unknown)."""
    out = {}
    ids = [uas[k] for k in ("BasicID0", "BasicID1") if k in uas]
    for b in ids:
        id_type = ID_TYPES[b["IDType"]] if b["IDType"] < len(ID_TYPES) else str(b["IDType"])
        val = _txt(b["UASID"]) if b["IDType"] in (IDTYPE_SERIAL, IDTYPE_CAA) else b["UASID"].hex()
        out.setdefault("ids", {})[id_type] = val
        out["ua_type"] = UA_TYPES[b["UAType"]]
    loc = uas.get("Location")
    if loc:
        known = not (loc["Latitude"] == 0 and loc["Longitude"] == 0)
        out.update(
            status=STATUS[loc["Status"]] if loc["Status"] < len(STATUS) else str(loc["Status"]),
            lat=loc["Latitude"] if known else None,
            lon=loc["Longitude"] if known else None,
            alt_geo_m=None if loc["AltitudeGeo"] == INV_ALT else loc["AltitudeGeo"],
            alt_baro_m=None if loc["AltitudeBaro"] == INV_ALT else loc["AltitudeBaro"],
            height_m=None if loc["Height"] == INV_ALT else loc["Height"],
            height_ref="ground" if loc["HeightType"] else "takeoff",
            course_deg=None if loc["Direction"] > 360 else loc["Direction"],
            speed_h_ms=None if loc["SpeedHorizontal"] == INV_SPEED_H else loc["SpeedHorizontal"],
            speed_v_ms=None if loc["SpeedVertical"] == INV_SPEED_V else loc["SpeedVertical"],
            h_acc_m=None if loc["HorizAccuracy"] == 0 else horiz_accuracy_m(loc["HorizAccuracy"]),
            v_acc_m=None if loc["VertAccuracy"] == 0 else vert_accuracy_m(loc["VertAccuracy"]),
            ts_after_hour_s=None if loc["TimeStamp"] == INV_TIMESTAMP else loc["TimeStamp"],
        )
    sysm = uas.get("System")
    if sysm:
        known = not (sysm["OperatorLatitude"] == 0 and sysm["OperatorLongitude"] == 0)
        out.update(
            operator_lat=sysm["OperatorLatitude"] if known else None,
            operator_lon=sysm["OperatorLongitude"] if known else None,
            operator_alt_geo_m=None if sysm["OperatorAltitudeGeo"] == INV_ALT else sysm["OperatorAltitudeGeo"],
            operator_location_type=(OPERATOR_LOCATION_TYPES[sysm["OperatorLocationType"]]
                                    if sysm["OperatorLocationType"] < 3 else str(sysm["OperatorLocationType"])),
            system_timestamp=sysm["Timestamp"],
        )
    if "OperatorID" in uas:
        out["operator_id"] = _txt(uas["OperatorID"]["OperatorId"])
    if "SelfID" in uas:
        out["self_id"] = _txt(uas["SelfID"]["Desc"])
    auth_pages = sorted(int(k[4:]) for k in uas if k.startswith("Auth"))
    if auth_pages:
        out["auth_pages"] = auth_pages
    return out
