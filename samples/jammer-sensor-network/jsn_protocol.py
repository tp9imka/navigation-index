"""Node <=> aggregator message schema `jsn/1` (compact JSON, MQTT-shaped) and the
aggregator-side conversion of one observation into a jammer-power measurement.

Topics (MQTT): jsn/v1/<node>/meta  retained, sent on boot and on config change
               jsn/v1/<node>/obs   QoS 0, 1 Hz
The payload repeats the kind in `k`, so the same JSON works over HTTP POST or stdin.
"""
import json
import math
from dataclasses import dataclass

import jsn_model as M

SCHEMA_VERSION = 1
TOPIC_PREFIX = "jsn/v1"
KINDS = ("meta", "obs")
POS_SOURCES = ("survey", "gnss", "dr")

DETECT_DROP_DB = 1.0
AGC_DETECT_DB = 1.0
DROP_SIGMA_DB = 0.5            # median of ~9 SVs at 1 dB-Hz per-SV noise, rounded up
AGC_SIGMA_DB = 0.5
AGC_CAL_SIGMA_DB = 1.5         # per-node calibration uncertainty the aggregator assumes
MAX_MEAS_SIGMA_DB = 6.0
STRONGEST_SV_DBHZ = 48.0       # all SVs lost => drop beyond this - tracking threshold

META_FIELDS = {"v": int, "k": str, "id": str, "lat": float, "lon": float, "static": bool}
META_OPTIONAL = {"hw": str, "agc_ref": int, "agc_db_per_cnt": float, "q": float}
OBS_FIELDS = {"v": int, "k": str, "id": str, "seq": int, "t": float, "lat": float, "lon": float,
              "ps": float, "pf": str, "fix": int, "nsv": int, "agc": int, "jam": int, "jst": int}
OBS_NULLABLE = {"cn0": float, "dcn0": float}


def topic(msg):
    return f"{TOPIC_PREFIX}/{msg['id']}/{msg['k']}"


def make_meta(node_id, lat, lon, static, hw=None, agc_ref=None, agc_db_per_cnt=None):
    m = {"v": SCHEMA_VERSION, "k": "meta", "id": node_id, "lat": round(lat, 7), "lon": round(lon, 7),
         "static": bool(static)}
    if hw:
        m["hw"] = hw
    if agc_ref is not None:
        m["agc_ref"], m["agc_db_per_cnt"] = int(agc_ref), float(agc_db_per_cnt)
    return m


def make_obs(node_id, lat, lon, f):
    """f: the dict SimNode.observe returns (or the same fields from a real UBX reader)."""
    return {"v": SCHEMA_VERSION, "k": "obs", "id": node_id, "seq": f["seq"], "t": round(f["t"], 3),
            "lat": round(lat, 7), "lon": round(lon, 7), "ps": round(f["ps"], 1), "pf": f["pf"],
            "fix": f["fix"], "nsv": f["nsv"], "cn0": f["cn0"], "dcn0": f["dcn0"], "agc": f["agc"],
            "jam": f["jam"], "jst": f["jst"]}


def _check(msg, required, optional, nullable=None):
    for k, typ in required.items():
        if k not in msg:
            raise ValueError(f"missing field {k}")
        v = msg[k]
        if typ is float and isinstance(v, int) and not isinstance(v, bool):
            continue
        if not isinstance(v, typ) or (typ is int and isinstance(v, bool)):
            raise ValueError(f"field {k} must be {typ.__name__}")
    for k, typ in {**optional, **(nullable or {})}.items():
        v = msg.get(k)
        if v is None:
            continue
        if not (isinstance(v, typ) or (typ is float and isinstance(v, int) and not isinstance(v, bool))):
            raise ValueError(f"field {k} must be {typ.__name__}")


def validate(msg):
    if not isinstance(msg, dict):
        raise ValueError("message must be a JSON object")
    if msg.get("v") != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema version {msg.get('v')}")
    if msg.get("k") == "meta":
        _check(msg, META_FIELDS, META_OPTIONAL)
    elif msg.get("k") == "obs":
        _check(msg, OBS_FIELDS, {}, OBS_NULLABLE)
        if msg["pf"] not in POS_SOURCES:
            raise ValueError(f"pf must be one of {POS_SOURCES}")
        if not 0 <= msg["jst"] <= 3:
            raise ValueError("jst must be 0..3")
    else:
        raise ValueError(f"k must be one of {KINDS}")
    if not (-90 <= msg["lat"] <= 90 and -180 <= msg["lon"] <= 180):
        raise ValueError("lat/lon out of range")
    return msg


def parse_line(line):
    """One message from a line: plain JSON, or `topic JSON` as `mosquitto_sub -v` prints it."""
    line = line.strip()
    if not line:
        return None
    if not line.startswith("{"):
        tp, _, line = line.partition(" ")
        msg = validate(json.loads(line))
        if tp != topic(msg):
            raise ValueError(f"topic {tp} does not match payload {topic(msg)}")
        return msg
    return validate(json.loads(line))


@dataclass
class Meas:
    """Jammer power at one node. kind: 'val' (j_dbm +- sigma), 'upper' (J below j_dbm),
    'lower' (J above j_dbm)."""
    node: str
    t: float
    x: float
    y: float
    ps: float
    kind: str
    j_dbm: float
    sigma_db: float
    static: bool
    source: str


J_UPPER_CN0 = M.jammer_dbm_from_cn0_drop(DETECT_DROP_DB)
J_UPPER_AGC = M.jammer_dbm_from_agc_reduction(AGC_DETECT_DB)
J_LOWER_ALL_LOST = M.jammer_dbm_from_cn0_drop(STRONGEST_SV_DBHZ - M.TRACK_LOSS_CN0_DBHZ)


def _from_drop(drop, sigma, inv):
    j = inv(drop)
    s = min(M.d_power_d_drop(drop) * sigma, MAX_MEAS_SIGMA_DB)
    return j, s


def to_measurement(obs, meta, xy):
    """Convert an obs (plus its node's meta) into a Meas at local position xy."""
    ests = []
    if obs.get("dcn0") is not None and obs["nsv"] > 0 and obs["dcn0"] >= DETECT_DROP_DB:
        ests.append(_from_drop(obs["dcn0"], DROP_SIGMA_DB, M.jammer_dbm_from_cn0_drop) + ("cn0",))
    agc_ok = meta is not None and meta.get("agc_ref") is not None
    if agc_ok:
        red = (meta["agc_ref"] - obs["agc"]) * meta["agc_db_per_cnt"]
        if red >= AGC_DETECT_DB:
            sig = math.hypot(AGC_SIGMA_DB, AGC_CAL_SIGMA_DB)
            ests.append(_from_drop(red, sig, M.jammer_dbm_from_agc_reduction) + ("agc",))
    static = bool(meta and meta.get("static"))
    base = dict(node=obs["id"], t=obs["t"], x=xy[0], y=xy[1], ps=obs["ps"], static=static)
    if ests:
        w = [1 / s ** 2 for _, s, _ in ests]
        j = sum(wi * e[0] for wi, e in zip(w, ests)) / sum(w)
        return Meas(kind="val", j_dbm=j, sigma_db=math.sqrt(1 / sum(w)),
                    source="+".join(e[2] for e in ests), **base)
    if obs["nsv"] == 0:
        return Meas(kind="lower", j_dbm=J_LOWER_ALL_LOST, sigma_db=DROP_SIGMA_DB, source="all-lost", **base)
    upper = min(J_UPPER_CN0, J_UPPER_AGC) if agc_ok else J_UPPER_CN0
    return Meas(kind="upper", j_dbm=upper, sigma_db=DROP_SIGMA_DB, source="clear", **base)
