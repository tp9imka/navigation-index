"""Inject synthetic GNSS-spoofing episodes into real AIS tracks (stdlib).

Only positions change. Reported SOG / COG / heading stay as the ship sent them: in public
crop-circle cases the reported speed and course stayed steady while positions circled, and
heading comes from the gyro, which GNSS spoofing does not touch.

kinds:
  offset        whole track shifted by a constant vector (Gelendzhik-airport style, 0.2-40 km)
  drift         offset grows linearly at 1-5 m/s (slow pull-off)
  circle        one vessel's positions replaced by a circle around its own start position
  circle_group  several neighbouring vessels all moved onto one shared circle (crop circle)
"""
import math
import random
from collections import namedtuple
from dataclasses import replace

from geo import destination, haversine_m

Episode = namedtuple("Episode", "mmsi kind start end param n_in lead_gap_s")

EPISODE_S = 1800.0
EDGE_S = 600.0
MIN_TRACK_S = EPISODE_S + 2 * EDGE_S
MIN_FIXES = 100
MIN_MEDIAN_SOG_KN = 5.0
OFFSET_RANGE_M = (200.0, 40_000.0)
DRIFT_RANGE_MS = (1.0, 5.0)
CIRCLE_R_RANGE_M = (200.0, 600.0)
GROUP_CIRCLE_R_RANGE_M = (300.0, 800.0)
GROUP_RADIUS_M = 30_000.0
GROUP_CENTER_OFFSET_M = (5_000.0, 25_000.0)
GROUP_TIME_TOL_S = 120.0
KN_TO_MS = 0.514444


def _coverage(track, s, e):
    """Fixes inside the window and the receive gap right before it (coverage holes are real)."""
    n = sum(1 for f in track.fixes if s <= f.t <= e)
    before = [f.t for f in track.fixes if f.t < s]
    return n, (s - before[-1]) if before else math.inf


def _median_sog(fixes):
    s = sorted(f.sog for f in fixes if f.sog is not None)
    return s[len(s) // 2] if s else 0.0


def eligible(tracks, exclude=()):
    out = []
    for t in tracks:
        fx = t.fixes
        if (t.mobile == "Class A" and t.mmsi not in exclude and len(fx) >= MIN_FIXES
                and fx[-1].t - fx[0].t >= MIN_TRACK_S and _median_sog(fx) >= MIN_MEDIAN_SOG_KN):
            out.append(t)
    return out


def _window(track, rng):
    t0, t1 = track.fixes[0].t + EDGE_S, track.fixes[-1].t - EDGE_S - EPISODE_S
    s = rng.uniform(t0, t1)
    return s, s + EPISODE_S


def _apply(track, start, end, fn):
    fixes = [fn(f) if start <= f.t <= end else f for f in track.fixes]
    return replace(track, fixes=fixes)


def _circle_fn(center, radius, sog_kn, start, phase):
    omega = max(sog_kn, 1.0) * KN_TO_MS / radius

    def fn(f):
        lat, lon = destination(center[0], center[1], math.degrees(phase + omega * (f.t - start)), radius)
        return f._replace(lat=lat, lon=lon)
    return fn


def _pos_at(track, t):
    return min(track.fixes, key=lambda f: abs(f.t - t))


def inject(tracks, n_offset=100, n_drift=50, n_circle=50, n_groups=12, group_size=5,
           seed=1, exclude=()):
    rng = random.Random(seed)
    pool = eligible(tracks, exclude)
    rng.shuffle(pool)
    used, episodes, new = set(), [], {}

    def take():
        while pool:
            t = pool.pop()
            if t.mmsi not in used:
                used.add(t.mmsi)
                return t
        return None

    for _ in range(n_offset):
        t = take()
        if not t:
            break
        s, e = _window(t, rng)
        mag = math.exp(rng.uniform(*map(math.log, OFFSET_RANGE_M)))
        brg = rng.uniform(0, 360)
        new[t.mmsi] = _apply(t, s, e, lambda f: f._replace(**dict(zip(("lat", "lon"),
                                                                   destination(f.lat, f.lon, brg, mag)))))
        episodes.append(Episode(t.mmsi, "offset", s, e, mag, *_coverage(t, s, e)))
    for _ in range(n_drift):
        t = take()
        if not t:
            break
        s, e = _window(t, rng)
        rate, brg = rng.uniform(*DRIFT_RANGE_MS), rng.uniform(0, 360)

        def fn(f, s=s, rate=rate, brg=brg):
            lat, lon = destination(f.lat, f.lon, brg, rate * (f.t - s))
            return f._replace(lat=lat, lon=lon)
        new[t.mmsi] = _apply(t, s, e, fn)
        episodes.append(Episode(t.mmsi, "drift", s, e, rate, *_coverage(t, s, e)))
    for _ in range(n_circle):
        t = take()
        if not t:
            break
        s, e = _window(t, rng)
        p = _pos_at(t, s)
        r = rng.uniform(*CIRCLE_R_RANGE_M)
        win = [f for f in t.fixes if s <= f.t <= e]
        new[t.mmsi] = _apply(t, s, e, _circle_fn((p.lat, p.lon), r, _median_sog(win), s,
                                                 rng.uniform(0, 2 * math.pi)))
        episodes.append(Episode(t.mmsi, "circle", s, e, r, *_coverage(t, s, e)))
    for _ in range(n_groups):
        seed_t = take()
        if not seed_t:
            break
        s, e = _window(seed_t, rng)
        p0 = _pos_at(seed_t, s)
        members = [seed_t]
        for t in pool:
            if len(members) >= group_size:
                break
            if t.mmsi in used or t.fixes[0].t > s - EDGE_S or t.fixes[-1].t < e + EDGE_S:
                continue
            q = _pos_at(t, s)
            if abs(q.t - s) <= GROUP_TIME_TOL_S and haversine_m(p0.lat, p0.lon, q.lat, q.lon) <= GROUP_RADIUS_M:
                members.append(t)
                used.add(t.mmsi)
        center = destination(p0.lat, p0.lon, rng.uniform(0, 360), rng.uniform(*GROUP_CENTER_OFFSET_M))
        r = rng.uniform(*GROUP_CIRCLE_R_RANGE_M)
        for t in members:
            win = [f for f in t.fixes if s <= f.t <= e]
            new[t.mmsi] = _apply(t, s, e, _circle_fn(center, r, _median_sog(win), s, rng.uniform(0, 2 * math.pi)))
            episodes.append(Episode(t.mmsi, "circle_group", s, e, len(members), *_coverage(t, s, e)))
    return [new.get(t.mmsi, t) for t in tracks], episodes
