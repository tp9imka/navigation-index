"""Remote ID track table with plausibility checks.

Remote ID is a self-report: nothing in broadcast F3411 stops a transmitter from claiming
any ID or position. The flags below are cheap consistency checks a receiver can run on
its own; they raise suspicion, they do not prove spoofing. All thresholds are heuristics
picked for small UAS and should be tuned per site.
"""
import math
from dataclasses import dataclass, field

import odid

EARTH_R_M = 6371008.8

STALE_AFTER_S = 5.0          # F3411 Location rate is >= 1 Hz; 5 missed updates => stale
DROP_AFTER_S = 60.0
MAX_PLAUSIBLE_SPEED_MS = 100.0   # well above small-UAS performance, below airliners
JUMP_MARGIN_M = 50.0             # slack on top of claimed speed * dt and accuracy
SPEED_MISMATCH_MS = 20.0         # |claimed - implied| over a short window
SPEED_CHECK_MIN_DT_S = 0.5
SPEED_CHECK_MAX_DT_S = 10.0
OPERATOR_FAR_M = 2000.0          # EU open category / US Part 107 imply VLOS, far less than this
CLONE_DISTANCE_M = 500.0         # same ID heard at two places at once
CLONE_WINDOW_S = 3.0
TS_SKEW_S = 30.0                 # Location timestamp vs receiver clock (seconds after the hour)
SECONDS_PER_HOUR = 3600.0


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R_M * math.asin(min(1.0, math.sqrt(a)))


@dataclass
class Track:
    key: str
    mac: str = None
    uas_id: str = None
    first_seen: float = 0.0
    last_seen: float = 0.0
    last_fix_t: float = None
    info: dict = field(default_factory=dict)      # latest summarize() view
    history: list = field(default_factory=list)   # (t, lat, lon, mac)
    flags: dict = field(default_factory=dict)     # name => {"t", "detail"}
    msg_count: int = 0

    def stale(self, now):
        return now - self.last_seen > STALE_AFTER_S


class Tracker:
    def __init__(self):
        self.by_mac = {}     # transmitter address => accumulated UAS record (odid dict)
        self.mac_id = {}     # transmitter address => last UAS id it claimed
        self.tracks = {}     # track key => Track
        self.events = []     # (t, key, flag, detail) in arrival order

    @staticmethod
    def _uas_id(info):
        ids = info.get("ids", {})
        for kind in ("serial_number", "caa_registration_id", "utm_assigned_uuid", "specific_session_id"):
            if kind in ids:
                return f"{kind}:{ids[kind]}"
        return None

    def _flag(self, tr, t, name, detail):
        first = name not in tr.flags
        tr.flags[name] = {"t": t, "detail": detail}
        if first:
            self.events.append((t, tr.key, name, detail))

    def ingest(self, t, mac, payload):
        """Feed one received ODID message or pack. mac identifies the transmitter (BLE/Wi-Fi source)."""
        mac = mac or "unknown"
        uas = self.by_mac.setdefault(mac, odid.new_uas())
        if odid.decode_message(uas, payload) == odid.INVALID:
            return None
        info = odid.summarize(uas)
        uas_id = self._uas_id(info)
        key = uas_id or f"mac:{mac}"

        tr = self.tracks.get(key)
        if tr is None:
            orphan = self.tracks.pop(f"mac:{mac}", None)  # adopt the MAC-keyed track once the ID arrives
            tr = orphan or Track(key=key, first_seen=t)
            tr.key = key
            self.tracks[key] = tr
        prev_id = self.mac_id.get(mac)
        if uas_id and prev_id and prev_id != uas_id:
            self._flag(tr, t, "id_change", f"transmitter {mac} switched from {prev_id} to {uas_id}")
        if uas_id:
            self.mac_id[mac] = uas_id
        if tr.mac and tr.mac != mac and uas_id:
            self._check_clone(tr, t, mac, info)
        tr.mac, tr.uas_id, tr.last_seen = mac, uas_id, t
        tr.msg_count += 1

        lat, lon = info.get("lat"), info.get("lon")
        if lat is not None and (lat, lon) != (tr.info.get("lat"), tr.info.get("lon")):
            self._check_motion(tr, t, mac, info)
            tr.history.append((t, lat, lon, mac))
            tr.last_fix_t = t
        self._check_operator(tr, t, info)
        self._check_timestamp(tr, t, info)
        tr.info = info
        return tr

    def _check_motion(self, tr, t, mac, info):
        # compare against the same transmitter only; a cloned ID is caught by _check_clone
        prev = next((h for h in reversed(tr.history) if h[3] == mac), None)
        if prev is None:
            return
        t0, lat0, lon0, _ = prev
        dt = t - t0
        if dt <= 0:
            return
        d = haversine_m(lat0, lon0, info["lat"], info["lon"])
        implied = d / dt
        claimed = max(info.get("speed_h_ms") or 0.0, tr.info.get("speed_h_ms") or 0.0)
        acc = (info.get("h_acc_m") or 0.0) + (tr.info.get("h_acc_m") or 0.0)
        if implied > MAX_PLAUSIBLE_SPEED_MS:
            self._flag(tr, t, "impossible_speed", f"{implied:.0f} m/s implied over {dt:.1f} s")
        if d > claimed * dt + acc + JUMP_MARGIN_M:
            self._flag(tr, t, "location_jump", f"moved {d:.0f} m in {dt:.1f} s, claimed {claimed:.1f} m/s")
        elif SPEED_CHECK_MIN_DT_S <= dt <= SPEED_CHECK_MAX_DT_S and info.get("speed_h_ms") is not None \
                and abs(info["speed_h_ms"] - implied) > SPEED_MISMATCH_MS + acc / dt:
            self._flag(tr, t, "speed_mismatch",
                       f"claimed {info['speed_h_ms']:.1f} m/s, implied {implied:.1f} m/s")

    def _check_operator(self, tr, t, info):
        if None in (info.get("lat"), info.get("operator_lat")):
            return
        d = haversine_m(info["lat"], info["lon"], info["operator_lat"], info["operator_lon"])
        if d > OPERATOR_FAR_M:
            self._flag(tr, t, "operator_far", f"operator {d:.0f} m from UAS")

    def _check_clone(self, tr, t, mac, info):
        if tr.last_seen < t - CLONE_WINDOW_S or info.get("lat") is None or tr.info.get("lat") is None:
            return
        d = haversine_m(tr.info["lat"], tr.info["lon"], info["lat"], info["lon"])
        if d > CLONE_DISTANCE_M:
            self._flag(tr, t, "duplicate_id",
                       f"{tr.uas_id} heard from {tr.mac} and {mac} {d:.0f} m apart within {CLONE_WINDOW_S:.0f} s")

    def _check_timestamp(self, tr, t, info):
        ts = info.get("ts_after_hour_s")
        if ts is None:
            return
        rx = t % SECONDS_PER_HOUR
        skew = abs((ts - rx + SECONDS_PER_HOUR / 2) % SECONDS_PER_HOUR - SECONDS_PER_HOUR / 2)
        if skew > TS_SKEW_S:
            self._flag(tr, t, "timestamp_skew", f"location timestamp {skew:.0f} s from receiver clock")

    def sweep(self, now):
        """Return (live, stale) tracks and drop ones silent for longer than DROP_AFTER_S."""
        for key in [k for k, tr in self.tracks.items() if now - tr.last_seen > DROP_AFTER_S]:
            del self.tracks[key]
        live = [tr for tr in self.tracks.values() if not tr.stale(now)]
        stale = [tr for tr in self.tracks.values() if tr.stale(now)]
        return live, stale
