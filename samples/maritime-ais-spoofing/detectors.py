"""AIS track anomaly detectors for GNSS spoofing signatures (stdlib only).

Every detector reads a Track (one MMSI, fixes sorted by time) and returns Flag
records. aggregate() turns flags into per-vessel alerts.
"""
import math
from collections import Counter, defaultdict, namedtuple
from dataclasses import dataclass, field, replace

from geo import angle_diff_deg, bearing_deg, circumradius_m, haversine_m

KN_TO_MS = 0.514444

Fix = namedtuple("Fix", "t lat lon sog cog hdg")          # t: epoch s, sog: kn, cog/hdg: deg or None
Flag = namedtuple("Flag", "mmsi t lat lon kind detail")


@dataclass
class Track:
    mmsi: int
    fixes: list
    ship_type: str = "Undefined"
    length_m: float = None
    mobile: str = "Class A"
    name: str = ""


# Plausible top speed (kn) by DMA "Ship type"; DEFAULT_VMAX_KN for anything else.
VMAX_KN = {
    "Cargo": 30, "Tanker": 30, "Fishing": 25, "Tug": 25, "Towing": 20, "Towing long/wide": 15,
    "Dredging": 20, "Passenger": 45, "HSC": 60, "SAR": 60, "Law enforcement": 50,
    "Military": 50, "Pilot": 40, "Pleasure": 50, "Sailing": 30,
}
DEFAULT_VMAX_KN = 50
SHIP_MOBILES = ("Class A", "Class B")
MMSI_PLACEHOLDERS = {0, 1, 111111111, 123456789, 999999999, 987654321, 100000000}
MID_MIN, MID_MAX = 201, 775            # ITU maritime identification digits, ship stations

STRONG_KINDS = {"jump", "on_land", "cluster", "mmsi_shared"}


@dataclass
class Config:
    speed_margin: float = 1.3          # x VMAX before a speed is called impossible
    jump_min_m: float = 500.0          # teleport must also exceed this distance (GNSS noise floor)
    window_s: float = 60.0             # lookback for speed / SOG / COG consistency
    max_window_s: float = 600.0        # ignore lookbacks across gaps longer than this
    check_stride_s: float = 30.0       # evaluate consistency at most this often per track
    sog_abs_tol_kn: float = 3.0
    sog_rel_tol: float = 0.5
    cog_min_sog_kn: float = 3.0
    cog_min_dist_m: float = 200.0
    cog_tol_deg: float = 60.0
    turn_min_length_m: float = 100.0
    turn_spacing_m: float = 150.0
    turn_radius_lengths: float = 1.0   # radius below 1 ship length while underway is implausible
    turn_min_sog_kn: float = 5.0
    bin_s: float = 600.0
    bin_min_fixes: int = 5
    loiter_min_sog_kn: float = 5.0
    loiter_path_ratio: float = 1.5     # reported path length / (2 * spread radius); straight line ~1
    loiter_max_r_m: float = 2000.0
    cluster_r_m: float = 2000.0
    cluster_min_vessels: int = 3
    land_stride_s: float = 60.0
    land_min_sog_kn: float = 1.0       # moored vessels in harbours the 10m coastline misses are not flagged
    shared_min_jumps: int = 6
    stale_min_sog_kn: float = 1.0
    alert_gap_s: float = 600.0
    alert_min_weak: int = 3


def vmax_ms(track, cfg):
    return VMAX_KN.get(track.ship_type, DEFAULT_VMAX_KN) * KN_TO_MS * cfg.speed_margin


def _flag(track, f, kind, detail):
    return Flag(track.mmsi, f.t, f.lat, f.lon, kind, detail)


def detect_kinematic(track, cfg=Config()):
    """jump: single-step teleport; speed: implied speed over >= window_s above vessel-type max;
    sog_mismatch / cog_mismatch: derived motion vs the vessel's own reported SOG/COG."""
    fx, out = track.fixes, []
    vmax = vmax_ms(track, cfg)
    last_jump_t, j, last_check = -math.inf, 0, -math.inf
    for i in range(1, len(fx)):
        p, f = fx[i - 1], fx[i]
        dt = f.t - p.t
        if dt > 0:
            d = haversine_m(p.lat, p.lon, f.lat, f.lon)
            if d >= cfg.jump_min_m and d / dt > vmax:
                out.append(_flag(track, f, "jump", f"{d:.0f} m in {dt:.0f} s"))
                last_jump_t = f.t
                continue
        while j + 1 < i and fx[j + 1].t <= f.t - cfg.window_s:
            j += 1
        a = fx[j]
        dt = f.t - a.t
        if not (cfg.window_s <= dt <= cfg.max_window_s) or a.t < last_jump_t:
            continue
        if f.t - last_check < cfg.check_stride_s:
            continue
        last_check = f.t
        d = haversine_m(a.lat, a.lon, f.lat, f.lon)
        v = d / dt
        if v > vmax and d >= cfg.cog_min_dist_m:
            out.append(_flag(track, f, "speed", f"{v / KN_TO_MS:.1f} kn over {dt:.0f} s"))
            continue
        if a.sog is not None and f.sog is not None:
            sog = 0.5 * (a.sog + f.sog)
            vk = v / KN_TO_MS
            if abs(vk - sog) > max(cfg.sog_abs_tol_kn, cfg.sog_rel_tol * sog):
                out.append(_flag(track, f, "sog_mismatch", f"derived {vk:.1f} kn vs reported {sog:.1f} kn"))
            course = f.cog if f.cog is not None else f.hdg
            if course is not None and sog >= cfg.cog_min_sog_kn and d >= cfg.cog_min_dist_m:
                brg = bearing_deg(a.lat, a.lon, f.lat, f.lon)
                if angle_diff_deg(brg, course) > cfg.cog_tol_deg:
                    out.append(_flag(track, f, "cog_mismatch", f"track {brg:.0f} vs reported {course:.0f} deg"))
    return out


def detect_turn(track, cfg=Config()):
    """Turn radius from decimated positions below turn_radius_lengths x ship length while underway."""
    if not track.length_m or track.length_m < cfg.turn_min_length_m:
        return []
    pts, out = [], []
    limit = cfg.turn_radius_lengths * track.length_m
    for f in track.fixes:
        if pts:
            last = pts[-1]
            if f.t - last.t > cfg.max_window_s:
                pts = []
            elif haversine_m(last.lat, last.lon, f.lat, f.lon) < cfg.turn_spacing_m:
                continue
        pts.append(f)
        if len(pts) >= 3:
            a, b, c = pts[-3:]
            if (c.sog or 0) >= cfg.turn_min_sog_kn:
                r = circumradius_m((a.lat, a.lon), (b.lat, b.lon), (c.lat, c.lon))
                if r < limit:
                    out.append(_flag(track, c, "turn", f"radius {r:.0f} m < {limit:.0f} m"))
    return out


BinSummary = namedtuple("BinSummary", "mmsi bin lat lon r_max sog_med n t_last")


def bin_summaries(track, cfg=Config()):
    groups = defaultdict(list)
    for f in track.fixes:
        groups[int(f.t // cfg.bin_s)].append(f)
    out = []
    for b, fs in groups.items():
        if len(fs) < cfg.bin_min_fixes or fs[-1].t - fs[0].t < cfg.bin_s / 2:
            continue
        lat = sum(f.lat for f in fs) / len(fs)
        lon = sum(f.lon for f in fs) / len(fs)
        r = max(haversine_m(lat, lon, f.lat, f.lon) for f in fs)
        sogs = sorted(f.sog for f in fs if f.sog is not None)
        sog_med = sogs[len(sogs) // 2] if sogs else None
        out.append(BinSummary(track.mmsi, b, lat, lon, r, sog_med, len(fs), fs[-1].t))
    return out


def is_loiter_underway(s, span_s, cfg=Config()):
    """Reported speed says the vessel covered far more ground than its position spread allows."""
    if s.sog_med is None or s.sog_med < cfg.loiter_min_sog_kn or s.r_max > cfg.loiter_max_r_m:
        return False
    path = s.sog_med * KN_TO_MS * span_s
    return path > cfg.loiter_path_ratio * 2.0 * max(s.r_max, 25.0)


def detect_loiter_and_clusters(tracks, cfg=Config()):
    """loiter_underway per vessel/bin; cluster when >= cluster_min_vessels loiter within cluster_r_m."""
    out, by_bin = [], defaultdict(list)
    for tr in tracks:
        if tr.mobile not in SHIP_MOBILES:
            continue
        spans = defaultdict(lambda: [math.inf, -math.inf])
        for f in tr.fixes:
            sp = spans[int(f.t // cfg.bin_s)]
            sp[0], sp[1] = min(sp[0], f.t), max(sp[1], f.t)
        for s in bin_summaries(tr, cfg):
            span = spans[s.bin][1] - spans[s.bin][0]
            if is_loiter_underway(s, span, cfg):
                out.append(Flag(tr.mmsi, s.t_last, s.lat, s.lon, "loiter_underway",
                                f"spread {s.r_max:.0f} m at {s.sog_med:.1f} kn"))
                by_bin[s.bin].append(s)
    for b, ss in by_bin.items():
        parent = list(range(len(ss)))

        def find(k):
            while parent[k] != k:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k
        for x in range(len(ss)):
            for y in range(x + 1, len(ss)):
                if haversine_m(ss[x].lat, ss[x].lon, ss[y].lat, ss[y].lon) <= cfg.cluster_r_m:
                    parent[find(x)] = find(y)
        groups = defaultdict(list)
        for k in range(len(ss)):
            groups[find(k)].append(ss[k])
        for g in groups.values():
            if len({s.mmsi for s in g}) >= cfg.cluster_min_vessels:
                for s in g:
                    out.append(Flag(s.mmsi, s.t_last, s.lat, s.lon, "cluster",
                                    f"{len(g)} vessels circling within {cfg.cluster_r_m:.0f} m"))
    return out


def detect_on_land(track, land_mask, cfg=Config()):
    """land_mask: list[bool] parallel to track.fixes (precomputed, e.g. by land.py)."""
    out, last = [], -math.inf
    for f, on in zip(track.fixes, land_mask):
        if on and (f.sog or 0.0) >= cfg.land_min_sog_kn and f.t - last >= cfg.land_stride_s:
            out.append(_flag(track, f, "on_land", "position inside eroded land polygon"))
            last = f.t
    return out


def mmsi_anomalies(mmsi, mobile):
    """MMSIs arrive as integers, so leading zeros (coast stations 00MID..., groups 0MID...)
    are restored by zero-padding; only > 9 digits is a length error."""
    s, out = str(mmsi).zfill(9), []
    if mmsi in MMSI_PLACEHOLDERS or len(set(s)) == 1:
        out.append("mmsi_placeholder")
    if len(s) != 9:
        out.append("mmsi_length")
    elif mobile in SHIP_MOBILES:
        if s[0] not in "234567":
            out.append("mmsi_not_ship")
        elif not MID_MIN <= int(s[:3]) <= MID_MAX:
            out.append("mmsi_bad_mid")
    return out


def detect_mmsi(track, kin_flags, cfg=Config()):
    out = []
    f0 = track.fixes[0]
    for kind in mmsi_anomalies(track.mmsi, track.mobile):
        out.append(_flag(track, f0, kind, f"MMSI {track.mmsi} ({track.mobile})"))
    jumps = [f for f in kin_flags if f.kind == "jump"]
    if len(jumps) >= cfg.shared_min_jumps:
        out.append(Flag(track.mmsi, jumps[0].t, jumps[0].lat, jumps[0].lon, "mmsi_shared",
                        f"{len(jumps)} teleports: two transmitters on one MMSI or repeated spoofing"))
    return out


def drop_stale_repeats(track, cfg=Config()):
    """Drop a single exact repeat of the previous position while the vessel reports way on.
    In DMA data these are re-delivered old reports with a new receive time; kept, they read
    as a halt plus a catch-up teleport. A run of repeats (frozen position) is kept."""
    fx = track.fixes
    keep = [f for i, f in enumerate(fx)
            if not (0 < i < len(fx) - 1 and (f.sog or 0.0) >= cfg.stale_min_sog_kn
                    and (f.lat, f.lon) == (fx[i - 1].lat, fx[i - 1].lon)
                    and (fx[i + 1].lat, fx[i + 1].lon) != (f.lat, f.lon))]
    return replace(track, fixes=keep)


def run_all(tracks, land_masks=None, cfg=Config()):
    flags = []
    for tr in tracks:
        if not tr.fixes:
            continue
        if tr.mobile in SHIP_MOBILES:
            clean = drop_stale_repeats(tr, cfg)
            kin = detect_kinematic(clean, cfg)
            flags += kin
            flags += detect_turn(clean, cfg)
            if land_masks is not None and tr.mmsi in land_masks:
                flags += detect_on_land(tr, land_masks[tr.mmsi], cfg)
        else:
            kin = []
        flags += detect_mmsi(tr, kin, cfg)
    flags += detect_loiter_and_clusters(tracks, cfg)
    return flags


@dataclass
class Alert:
    mmsi: int
    start: float
    end: float
    kinds: Counter = field(default_factory=Counter)
    flags: list = field(default_factory=list)


MMSI_STATIC_KINDS = {"mmsi_placeholder", "mmsi_length", "mmsi_not_ship", "mmsi_bad_mid"}


def aggregate(flags, cfg=Config()):
    """Group flags per vessel with gaps <= alert_gap_s. An alert needs one strong flag or
    alert_min_weak weak ones. Static MMSI anomalies are reported separately."""
    per = defaultdict(list)
    for f in flags:
        if f.kind not in MMSI_STATIC_KINDS:
            per[f.mmsi].append(f)
    alerts = []
    for mmsi, fs in per.items():
        fs.sort(key=lambda f: f.t)
        cur = None
        for f in fs:
            if cur is None or f.t - cur.end > cfg.alert_gap_s:
                if cur:
                    alerts.append(cur)
                cur = Alert(mmsi, f.t, f.t)
            cur.end = f.t
            cur.kinds[f.kind] += 1
            cur.flags.append(f)
        alerts.append(cur)
    return [a for a in alerts
            if STRONG_KINDS & set(a.kinds) or sum(a.kinds.values()) >= cfg.alert_min_weak]
